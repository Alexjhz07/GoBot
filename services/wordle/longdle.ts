import * as fs from 'fs';
import axios from 'axios';

// The vocabulary of the game alongside allowed entry words
const VALID_WORDS_LIST: string[] = fs.readFileSync('./assets/longdle_game_words.txt', { encoding: 'utf-8', flag: 'r' }).split('\n')
const VALID_ENTRY_LIST: string[] = fs.readFileSync('./assets/longdle_entry_words.txt', { encoding: 'utf-8', flag: 'r' }).split('\n')
const VALID_CUSTOM_WORDS: string[] = fs.readFileSync('./assets/longdle_custom_words.txt', { encoding: 'utf-8', flag: 'r' }).split('\n')
const VALID_WORDS_DICT: any = {}
const VALID_ENTRY_DICT: any = {}
const VALID_CUSTOM_DICT: any = {}

VALID_WORDS_LIST.map((word) => VALID_WORDS_DICT[word] = true)
VALID_ENTRY_LIST.map((word) => VALID_ENTRY_DICT[word] = true)
VALID_CUSTOM_WORDS.map((word) => VALID_CUSTOM_DICT[word] = true)

// Max reward calculation: BASE * len(word)
// Divided by 2 for each incorrect guess
const BASE_MAX_REWARD: number = 80000

const MINIMUM_WORD_LENGTH = 5
const MAXIMUM_WORD_LENGTH = 15

const LETTER_BIT_MAP: any = {'A': 1, 'B': 2, 'C': 4, 'D': 8, 'E': 16, 'F': 32, 'G': 64, 'H': 128, 'I': 256, 'J': 512, 'K': 1024, 'L': 2048, 'M': 4096, 'N': 8192, 'O': 16384, 'P': 32768, 'Q': 65536, 'R': 131072, 'S': 262144, 'T': 524288, 'U': 1048576, 'V': 2097152, 'W': 4194304, 'X': 8388608, 'Y': 16777216, 'Z': 33554432}

// Class to generate a unique game for each player based on the date
class GameContext {
    public user_id: string
    public date_string: string
    public word: string
    public word_length: number
    public max_guesses: number
    public max_reward: number

    constructor(user_id: string) {
        this.user_id = user_id
        const today = new Date()
        today.setUTCHours(today.getUTCHours() - 9);
        this.date_string = today.toISOString().substring(0, 10)
        this.word = this.get_daily_word(this.date_string, this.user_id)
        this.word_length = this.word.length
        this.max_guesses = this.word_length + 1
        this.max_reward = BASE_MAX_REWARD * (this.word_length)
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

class PlayerCache {
    public win_flag: boolean = false
    public guess_count: number = 0
    public previous_guesses: string[] = []
    public previous_results: string[][] = []
    public valid_letter_map: number = 67108863 // Bit map

    private invalidate_letter(letter: string) {
        if (LETTER_BIT_MAP[letter] & this.valid_letter_map) {
            this.valid_letter_map -= LETTER_BIT_MAP[letter]
        }
    }

    public invalidate_string(correct_string: string, guess_string: string) {
        for (const c of guess_string) {
            if (!correct_string.includes(c)) {
                this.invalidate_letter(c)
            }
        }
    }
}

// Class that handles the business logic of our Longdle game
export default class Longdle {
    private players: { [key: string]: PlayerCache } = {}
    private loaded: boolean = false;
    private current_date_string: string

    constructor() {
        const today = new Date()
        today.setUTCHours(today.getUTCHours() - 9);
        this.current_date_string = today.toISOString().substring(0, 10)
    }

    public async make_guess(user_id: string, guess: string) {
        try {
            guess = String(guess).toUpperCase()
        } catch (e: any) {
            return {"status": "error", "message": `Type cast failed for guess: ${e.message}`}
        }

        const gc = new GameContext(user_id)
        
        if (gc.date_string != this.current_date_string) this.start_new_day(gc.date_string)

        if (!this.loaded) {
            try {
                await this.reload_cache(gc.date_string)
                this.loaded = true
            } catch (e: any) {
                return {"status": "error", "message": e.message}
            }
        }

        var cache = this.players[user_id]
        
        if (cache?.win_flag) return {"status": "already-won", "date_string": this.current_date_string, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "reward": gc.max_reward / ( 2 ** (cache.guess_count - 1)), "answer": gc.word, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results}
        if (cache?.guess_count >= gc.max_guesses) return {"status": "out-of-tries", "date_string": this.current_date_string, "word_length": gc.word_length, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "answer": gc.word, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results}

        if (!cache) {
            this.players[user_id] = new PlayerCache()
            cache = this.players[user_id]
        }

        if (guess.length > gc.word_length) return {"status": "invalid-guess", "date_string": this.current_date_string, "message": `Guess was ${guess.length} letters but maximum length is ${gc.word_length}`, "word_length": gc.word_length, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results};
        if (guess.length < MINIMUM_WORD_LENGTH) return {"status": "invalid-guess", "date_string": this.current_date_string, "message": `Guess was ${guess.length} letters but minimum length is ${MINIMUM_WORD_LENGTH}`, "word_length": gc.word_length, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results};
        if (!(VALID_WORDS_DICT[guess] || VALID_ENTRY_DICT[guess] || VALID_CUSTOM_DICT[guess])) return {"status": "invalid-guess", "date_string": this.current_date_string, "message": "Invalid entry word (Not in accepted inputs)", "word_length": gc.word_length, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results};
        
        if (gc.word === guess) {
            const reward = Math.floor(gc.max_reward / ( 2 ** cache.guess_count))
            try {
                await axios.post("http://localhost:3815/api/v1/exec", {"queries": [
                    "INSERT INTO longdle_games (user_id, guess_word, daily_word, date_string, win_flag) VALUES ($1, $2, $3, $4, True)",
                    "INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id) VALUES ($1, $2, $3)"
                ], "arguments": [
                    [user_id, guess, gc.word, gc.date_string],
                    ["longdle", reward, user_id]
                ]})
            } catch (e: any) {
                return {"status": "error", "message": `Correct guess but error communicating with db for reward: ${e.message}`}
            }
            cache.win_flag = true
            cache.guess_count += 1
            cache.previous_guesses.push(guess)
            cache.previous_results.push(this.get_guess_result(gc.word, guess))
            return {"status": "win", "date_string": this.current_date_string, "word_length": gc.word_length, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "reward": reward, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results}
        }

        try {
            await axios.post("http://localhost:3815/api/v1/exec", {"queries": [
                "INSERT INTO longdle_games (user_id, guess_word, daily_word, date_string) VALUES ($1, $2, $3, $4)"
            ], "arguments": [
                [user_id, guess, gc.word, gc.date_string]
            ]})
        } catch (e: any) {
            return {"status": "error", "message": `error communicating with db: ${e.message}`}
        }
        cache.guess_count += 1

        const result = this.get_guess_result(gc.word, guess)

        cache.invalidate_string(gc.word, guess)
        cache.previous_guesses.push(guess)
        cache.previous_results.push(result)

        return {"status": "miss", "date_string": this.current_date_string, "answer": gc.word, "word_length": gc.word_length, "guess_count": cache.guess_count, "guess_remaining": gc.max_guesses - cache.guess_count, "alpha_bits": cache.valid_letter_map, "previous_guesses": cache.previous_guesses, "previous_results": cache.previous_results}
    }

    public async get_word_length(user_id: string) {
        const gc = new GameContext(user_id)

        if (gc.date_string != this.current_date_string) this.start_new_day(gc.date_string)

        if (!this.loaded) {
            try {
                await this.reload_cache(gc.date_string)
                this.loaded = true
            } catch (e: any) {
                return {"status": "error", "message": e.message}
            }
        }

        var cache = this.players[user_id]

        if (!cache) {
            this.players[user_id] = new PlayerCache()
            cache = this.players[user_id]
        }

        return {"date_string": this.current_date_string, "length": gc.word_length, "guess_remaining": gc.max_guesses - cache.guess_count, "win_flag": cache.win_flag}
    }

    public async add_custom_word(user_id: string, word: string) {
        try {
            word = String(word).toUpperCase()
        } catch (e: any) {
            return {"status": "error", "message": `Type cast failed for word: ${e.message}`}
        }

        if (VALID_WORDS_DICT[word] || VALID_ENTRY_DICT[word] || VALID_CUSTOM_DICT[word]) {
            return {"status": "error", "message": `${word} is already acceptable as an input`}
        }

        if (word.length > MAXIMUM_WORD_LENGTH || word.length < MINIMUM_WORD_LENGTH) {
            return {"status": "error", "message": `The word must be between ${MINIMUM_WORD_LENGTH} and ${MAXIMUM_WORD_LENGTH} characters long (inclusive)`}
        }

        if (!/^[a-zA-Z()]+$/.test(word)) {
            return {"status": "error", "message": "The word must only contain alphabetical characters"}
        }

        fs.appendFileSync('./assets/longdle_custom_words.txt', `${word}\n`)
        fs.appendFileSync('./assets/longdle_custom_logs.txt', `${user_id}~${word}\n`)
        VALID_CUSTOM_DICT[word] = true
        
        return {"status": "success", "message": `Successfully added ${word} to the accepted inputs list`}
    }

    private start_new_day(new_date_string: string) {
        this.loaded = false
        this.current_date_string = new_date_string
    }

    private get_guess_result(correct_string: string, guess_string: string) {
        let tracker: any = {}
        for (let i = 0; i < correct_string.length; i++) !tracker[correct_string[i]] ? tracker[correct_string[i]] = 1 : tracker[correct_string[i]] += 1
        
        let result = guess_string.split("")

        let matching = 0
        let misplaced = 0
        // Record Matching Characters
        for (let i = 0; i < correct_string.length && i < guess_string.length; i++) {
            if (guess_string.charAt(i) === correct_string.charAt(i)) {
                result[i] = "matching"
                tracker[guess_string.charAt(i)] -= 1
                matching += 1
            } else {
                result[i] = "absent"
            }
        }
        // Record Misplaced Characters
        for (let i = 0; i <  correct_string.length && i < guess_string.length; i++) {
            if (guess_string.charAt(i) !== correct_string.charAt(i) && tracker[guess_string.charAt(i)] != undefined && tracker[guess_string.charAt(i)] > 0) {
                result[i] = "misplaced"
                misplaced += 1
                tracker[guess_string.charAt(i)] -= 1
            }
        }

        return result
    }

    private async reload_cache(date_string: string) {
        try {
            this.players = {}

            let res = await axios.post("http://localhost:3815/api/v1/query", {"queries": [
                "SELECT user_id, guess_word, daily_word FROM longdle_games WHERE date_string=$1",
                "SELECT user_id FROM longdle_games WHERE date_string=$1 AND win_flag=true GROUP BY user_id"
            ], "arguments": [
                [date_string],
                [date_string]
            ]})

            for (const r of res.data.responses[0]) {
                const player_id = r.user_id
                if (!this.players[player_id]) {
                    this.players[player_id] = new PlayerCache()
                }

                const guess = r.guess_word
                const daily = r.daily_word
                const result = this.get_guess_result(daily, guess)

                this.players[player_id].previous_guesses.push(guess)
                this.players[player_id].previous_results.push(result)
                this.players[player_id].invalidate_string(daily, guess)
                
                this.players[player_id].guess_count += 1
            }

            res.data.responses[1].map((i: any) => this.players[i.user_id].win_flag = true)
        } catch (e: any) {
            throw new Error(`error communicating with db: ${e.message}`)
        }
    }
}
