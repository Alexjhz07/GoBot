import * as fs from 'fs';
import axios from 'axios';
import { log } from 'console';

export default class Wordle {
    private word_list: string[] = []
    private game_words: any = {}
    private entry_words: any = {}
    private players: any = {}
    private date_string: string = "1";
    private current_word: string = "APPLE";
    private current_word_list: string[] = ["A", "P", "P", "L", "E"];
    private loaded: boolean = false;

    constructor(game_words_file='valid_wordle_game_words.txt', entry_words_file='valid_wordle_entry_words.txt') {
        this.word_list = fs.readFileSync(game_words_file, { encoding: 'utf-8', flag: 'r' }).split('\n')
        this.word_list.map((word) => this.game_words[word] = true)
        fs.readFileSync(entry_words_file, { encoding: 'utf-8', flag: 'r' }).split('\n').map((word) => this.entry_words[word] = true)
        this.start_new_day()
    }

    public async make_guess(user_id: number, guess: string) {
        if (!this.loaded) {
            try {
                await this.persist_game()
                await this.fetch_guess_counts()
            } catch (e: any) {
                return {"status": "error", "message": e.message}
            }
        }

        guess = String(guess).toUpperCase()
        if (this.players[user_id]?.win_flag) return {"status": "already-won", "guess_count": this.players[user_id].guess_count}
        if (this.players[user_id]?.guess_count >= 6) return {"status": "out-of-tries", "guess_count": this.players[user_id].guess_count}

        if (!this.players[user_id]) this.players[user_id] = {"win_flag": 0, "guess_count": 0}
        if (!(this.entry_words[guess] || this.game_words[guess])) return {"status": "invalid-guess"};

        try {
            await axios.post("http://localhost:3815/api/v1/exec", {"queries": [
                "INSERT INTO wordle_games (user_id, guess_word, seed) VALUES ($1, $2, $3)"
            ], "arguments": [
                [user_id, guess, this.date_string]
            ]})
        } catch (e: any) {
            return {"status": "error", "message": `error communicating with db: ${e.message}`}
        }

        this.players[user_id].guess_count += 1
        if (this.current_word === guess) {
            this.players[user_id].win_flag = 1
            return {"status": "win", "guess_count": this.players[user_id].guess_count, "guess": guess}
        }

        let tracker: any = {}
        for (let i = 0; i < this.current_word.length; i++) !tracker[this.current_word[i]] ? tracker[this.current_word[i]] = 1 : tracker[this.current_word[i]] += 1
        
        let guess_list = guess.split("") 
        let result = guess.split("")

        let matching = 0
        let misplaced = 0
        // 1 Record Matching Characters
        for (let i = 0; i < this.current_word.length; i++) {
            if (guess_list[i] === this.current_word_list[i]) {
                result[i] = "#"
                tracker[guess_list[i]] -= 1
                matching += 1
            } else {
                result[i] = "."
            }
        }
        // 2 Record Misplaced Characters
        for (let i = 0; i < this.current_word.length; i++) {
            if (guess_list[i] !== this.current_word_list[i] && tracker[guess_list[i]] != undefined && tracker[guess_list[i]] > 0) {
                result[i] = "?"
                misplaced += 1
                tracker[guess_list[i]] -= 1
            }
        } 

        return {"status": "miss", "guess": guess_list, "matching": matching, "misplaced": misplaced, "guess_count": this.players[user_id].guess_count, "result": result}
    }

    private start_new_day() {
        this.players = {}
        const today = new Date()
        this.date_string = today.toISOString().substring(0, 10)
        this.current_word = this.get_daily_word()
        this.current_word_list = this.current_word.split("")
        this.loaded = false
    }

    private get_daily_word(): string {
        let h1 = 1779033703, h2 = 3144134277,
            h3 = 1013904242, h4 = 2773480762;
        for (let i = 0, k; i < this.date_string.length; i++) {
            k = this.date_string.charCodeAt(i);
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
        return this.word_list[(h1 >>> 0) % this.word_list.length];
    }

    async persist_game() {
        try {
            await axios.post("http://localhost:3815/api/v1/exec", {"queries": [
                "INSERT INTO wordle_history (seed, word) VALUES ($1, $2) ON CONFLICT DO NOTHING"
            ], "arguments": [
                [this.date_string, this.current_word]
            ]})
        } catch (e: any) {
            throw new Error(`error communicating with db: ${e.message}`)
        }
    }

    async fetch_guess_counts() {
        try {
            let res = await axios.post("http://localhost:3815/api/v1/query", {"queries": [
                "SELECT user_id, COUNT(seed) FROM wordle_games WHERE seed=$1 GROUP BY user_id",
                "SELECT user_id FROM wordle_games WHERE seed=$1 AND win_flag=true GROUP BY user_id"
            ], "arguments": [
                [this.date_string],
                [this.date_string]
            ]})
            res.data.responses[0].map((i: any) => this.players[Number(i.user_id)] = {"win_flag": 0, "guess_count": Number(i.count)})
            res.data.responses[1].map((i: any) => this.players[Number(i.user_id)].win_flag = 1)
        } catch (e: any) {
            throw new Error(`error communicating with db: ${e.message}`)
        }
    }
}
