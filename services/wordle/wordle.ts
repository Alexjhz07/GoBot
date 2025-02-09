import * as fs from 'fs';
import axios from 'axios';

// The vocabulary of the game alongside allowed entry words
const VALID_WORDS_LIST: string[] = fs.readFileSync('./assets/wordle_game_words.txt', { encoding: 'utf-8', flag: 'r' }).split('\n')
const VALID_ENTRY_LIST: string[] = fs.readFileSync('./assets/wordle_entry_words.txt', { encoding: 'utf-8', flag: 'r' }).split('\n')
const VALID_WORDS_DICT: any = {}
const VALID_ENTRY_DICT: any = {}

VALID_WORDS_LIST.map((word) => VALID_WORDS_DICT[word] = true)
VALID_ENTRY_LIST.map((word) => VALID_ENTRY_DICT[word] = true)

const WIN_REWARDS = [400000, 200000, 100000, 50000, 25000, 12500]

// Class to generate a unique game for each player based on the date
class GameContext {
    public user_id: string
    public date_string: string
    public word: string
    public word_list: string[]
    public word_length: number

    constructor(user_id: string) {
        this.user_id = user_id
        const today = new Date()
        this.date_string = today.toISOString().substring(0, 10)
        this.word = this.get_daily_word(this.date_string, this.user_id)
        this.word_list = this.word.split("")
        this.word_length = this.word.length
    }

    private get_daily_word(date_string: string, user_id: string): string {
        const seed = `${date_string}_${user_id}`
        // Harnessing the power of a seeded chaotic generator from here:
        // https://stackoverflow.com/questions/521295/seeding-the-random-number-generator-in-javascript
        let h1 = 1779033703, h2 = 3144134277,
            h3 = 1013904242, h4 = 2773480762;
        for (let i = 0, k; i < seed.length; i++) {
            k = seed.charCodeAt(i);
            h1 = h2 ^ Math.imul(h1 ^ k, 597399067);
            h2 = h3 ^ Math.imul(h2 ^ k, 2869860233);
            h3 = h4 ^ Math.imul(h3 ^ k, 951274213);
            h4 = h1 ^ Math.imul(h4 ^ k, 2716044179);
        }
        h1 = Math.imul(h3 ^ (h1 >>> 18), 597399067);
        h2 = Math.imul(h4 ^ (h2 >>> 22), 2869860233);
        h3 = Math.imul(h1 ^ (h3 >>> 17), 951274213);
        h4 = Math.imul(h2 ^ (h4 >>> 19), 2716044179);
        h1 ^= (h2 ^ h3 ^ h4), h2 ^= h1, h3 ^= h1, h4 ^= h1;
        return VALID_WORDS_LIST[(h1 >>> 0) % VALID_WORDS_LIST.length];
    }
}

// Class that handles the business logic of our Wordle game
export default class Wordle {
    private players: any = {}
    private loaded: boolean = false;
    private current_date_string: string

    constructor() {
        const today = new Date()
        this.current_date_string = today.toISOString().substring(0, 10)
    }

    public async make_guess(user_id: string, guess: string) {
        try {
            guess = String(guess).toUpperCase()
        } catch (e: any) {
            return {"status": "error", "message": `Type cast failed for user_id or guess: ${e.message}`}
        }

        const gc = new GameContext(user_id)
        
        if (gc.date_string != this.current_date_string) this.start_new_day(gc.date_string)

        if (!this.loaded) {
            try {
                await this.fetch_guess_counts(gc.date_string)
                this.loaded = true
            } catch (e: any) {
                return {"status": "error", "message": e.message}
            }
        }
        
        if (this.players[user_id]?.win_flag) return {"status": "already-won", "guess_count": this.players[user_id].guess_count, "reward": WIN_REWARDS[this.players[user_id].guess_count - 1], "answer": gc.word}
        if (this.players[user_id]?.guess_count >= 6) return {"status": "out-of-tries", "guess_count": this.players[user_id].guess_count, "answer": gc.word}

        if (!this.players[user_id]) this.players[user_id] = {"win_flag": 0, "guess_count": 0}
        if (!(VALID_ENTRY_DICT[guess] || VALID_WORDS_DICT[guess])) return {"status": "invalid-guess", "guess_count": this.players[user_id].guess_count};
        
        if (gc.word === guess) {
            const reward = WIN_REWARDS[this.players[user_id].guess_count]
            try {
                await axios.post("http://localhost:3815/api/v1/exec", {"queries": [
                    "INSERT INTO wordle_games (user_id, guess_word, date_string, win_flag) VALUES ($1, $2, $3, True)",
                    "INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id) VALUES ($1, $2, $3)"
                ], "arguments": [
                    [user_id, guess, gc.date_string],
                    ["wordle", reward, user_id]
                ]})
            } catch (e: any) {
                return {"status": "error", "message": `Correct guess but error communicating with db for reward: ${e.message}`}
            }
            this.players[user_id].win_flag = 1
            this.players[user_id].guess_count += 1
            return {"status": "win", "guess": gc.word_list, "matching": gc.word_length, "misplaced": 0, "guess_count": this.players[user_id].guess_count, "reward": reward, "result": ["matching", "matching", "matching", "matching", "matching"]}
        }

        try {
            await axios.post("http://localhost:3815/api/v1/exec", {"queries": [
                "INSERT INTO wordle_games (user_id, guess_word, date_string) VALUES ($1, $2, $3)"
            ], "arguments": [
                [user_id, guess, gc.date_string]
            ]})
        } catch (e: any) {
            return {"status": "error", "message": `error communicating with db: ${e.message}`}
        }
        this.players[user_id].guess_count += 1

        let tracker: any = {}
        for (let i = 0; i < gc.word_length; i++) !tracker[gc.word[i]] ? tracker[gc.word[i]] = 1 : tracker[gc.word[i]] += 1
        
        let guess_list = guess.split("") 
        let result = guess.split("")

        let matching = 0
        let misplaced = 0
        // Record Matching Characters
        for (let i = 0; i < gc.word_length; i++) {
            if (guess_list[i] === gc.word_list[i]) {
                result[i] = "matching"
                tracker[guess_list[i]] -= 1
                matching += 1
            } else {
                result[i] = "absent"
            }
        }
        // Record Misplaced Characters
        for (let i = 0; i < gc.word_length; i++) {
            if (guess_list[i] !== gc.word_list[i] && tracker[guess_list[i]] != undefined && tracker[guess_list[i]] > 0) {
                result[i] = "misplaced"
                misplaced += 1
                tracker[guess_list[i]] -= 1
            }
        } 

        return {"status": "miss", "guess": guess_list, "matching": matching, "misplaced": misplaced, "guess_count": this.players[user_id].guess_count, "result": result}
    }

    private start_new_day(new_date_string: string) {
        this.players = {}
        this.loaded = false
        this.current_date_string = new_date_string
    }

    private async fetch_guess_counts(date_string: string) {
        try {
            let res = await axios.post("http://localhost:3815/api/v1/query", {"queries": [
                "SELECT user_id, COUNT(date_string) FROM wordle_games WHERE date_string=$1 GROUP BY user_id",
                "SELECT user_id FROM wordle_games WHERE date_string=$1 AND win_flag=true GROUP BY user_id"
            ], "arguments": [
                [date_string],
                [date_string]
            ]})
            res.data.responses[0].map((i: any) => this.players[i.user_id] = {"win_flag": 0, "guess_count": Number(i.count)})
            res.data.responses[1].map((i: any) => this.players[i.user_id].win_flag = 1)
        } catch (e: any) {
            throw new Error(`error communicating with db: ${e.message}`)
        }
    }
}
