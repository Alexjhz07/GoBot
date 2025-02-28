from discord import Embed, ButtonStyle
from discord.ui import View, Button
from utils.db import post
from random import randint
from utils.ansi import wrap_list, wrap_text, get_ansi_raw, get_ansi_block, ANSI_Style, ANSI_Color

LONGDLE_HEADER = get_ansi_raw(""" ____   ____   ____   ____   ____   ____   ____ 
||L || ||O || ||N || ||G || ||D || ||L || ||E ||
||__|| ||__|| ||__|| ||__|| ||__|| ||__|| ||__||
|/__\| |/__\| |/__\| |/__\| |/__\| |/__\| |/__\|
""", color=ANSI_Color.green)

LONDGLE_INTRO = f"""{get_ansi_raw("Welcome to Longdle, the expanded version of WORDLE! This game is only functional when viewed in full screen from a laptop or desktop. (Not mobile, sorry!)")}

{get_ansi_raw("How to Play", style=ANSI_Style.bold_underline, color=ANSI_Color.yellow)}

{get_ansi_raw("Use")} {get_ansi_raw(";longlength", color=ANSI_Color.pink)} {get_ansi_raw("or")} {get_ansi_raw(";ll", color=ANSI_Color.pink)} {get_ansi_raw("at the start of the day to obtain your word length of the day.")}

{get_ansi_raw("The length of the daily word can be anywhere from 5 to 15 characters long. This information will be provided to you every time, and you will recieve more guesses based on how long the word is. There are also higher potential rewards for words of a greater length!")}

{get_ansi_raw("Your guess must have a length between 5 and the length of the word of the day. For example, if your the word of the day is 10 characters long, your guess can be 5, 7 or or 10 characters long but not 11 or 4.")}

{get_ansi_raw("This game provides feedback to guide your guesses:")}
{get_ansi_raw("GREY", color=ANSI_Color.grey)} {get_ansi_raw("- the letter is not in the word.")}
{get_ansi_raw("BLUE", color=ANSI_Color.blue)} {get_ansi_raw("- the letter is in the word but is misplaced")}
{get_ansi_raw("GREEN", color=ANSI_Color.green)} {get_ansi_raw("- the letter is in the word and in the right place")}

{get_ansi_raw("Also, basic letter tracking is built into this game!")}
{get_ansi_raw("GREY", color=ANSI_Color.grey)} {get_ansi_raw("- the letter is not in the word.")}
{get_ansi_raw("WHITE")} {get_ansi_raw("- the letter might be in the word.")}

{get_ansi_raw("The tracking is, as stated, basic, so don't rely on it to eliminate all the letters under more complex assumptions. It just keeps track of which letters have been eliminated directly through your guesses.")}

{get_ansi_raw("Disclaimer", style=ANSI_Style.bold_underline, color=ANSI_Color.red)}

{get_ansi_raw("This game has many more words than the original game, and I do not have time to personally filter through everything. Some items that aren't traditionally in Wordle like the names of well-known companies, places, and people are included in this expansion.")}

{get_ansi_raw("If a word should be an acceptable input but isn't currently, please use")} {get_ansi_raw(";longadd word_goes_here", color=ANSI_Color.pink)} {get_ansi_raw("to add the word into the acceptable inputs list. You will be able to use that word in your guess, but please use this command appropriately.")}

{get_ansi_raw("If a word is not fit for the game, please DM me and I will remove it from the list. Examples include: company names that not everyone will know, places that people not everyone will know, or words that are generally inappropriate.")}

{get_ansi_raw('With all that being said, I hope you have fun playing this "expansion" of Wordle!', color=ANSI_Color.green)}
"""

LONGDLE_FOOTER = 'Reminder: Use ";longadd word_goes_here" if you want to add a word to the allowed inputs list. Please DM any word removal requests to me.'

ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def get_longdle_intro() -> str:
    embed = Embed(
        description=wrap_list([LONGDLE_HEADER, LONDGLE_INTRO]), 
        color=0xffffff
    )
    embed.set_footer(text=LONGDLE_FOOTER)
    return embed 

async def add_longdle_word(user_id: int, word: str) -> list:
    response = await post('wordle', 'longdle/custom', { "user_id": str(user_id), "word": word })
    if response['status'] == 'success':
        return _generate_custom_accepted(response)
    elif response['status'] == 'error':
        return _generate_custom_rejected(response)
    
async def get_longdle_length(user_id: int):
    response = await post('wordle', 'longdle/custom/length', { "user_id": str(user_id) })
    if response['win_flag']:
        return f"Your daily word length is `{response['length']}`\nYou have already won today"
    else:
        return f"Your daily word length is `{response['length']}`\nYou have {response['guess_remaining']} guesses remaining today"

async def get_longdle_response(user_id: int, guess: str) -> list:
    response = await post('wordle', 'longdle', { "user_id": str(user_id), "guess": guess })
    if response['status'] == 'miss':
        return _generate_miss(response)
    elif response['status'] == 'invalid-guess':
        return _generate_invalid_guess(response)
    elif response['status'] == 'out-of-tries':
        return _generate_out_of_tries(response)
    elif response['status'] == 'win':
        return _generate_win(response)
    elif response['status'] == 'already-won':
        return _generate_already_won(response)
    elif response['status'] == 'error':
        return _generate_error(response)

def _render_previous_guesses(response: any):
    previous_guesses = response['previous_guesses']
    previous_results = response['previous_results']
    render_list = []
    
    for i in range(len(previous_guesses)):
        guess = previous_guesses[i]
        guess_render = []
        for j in range(len(guess)):
            res = previous_results[i][j]
            if res == 'absent':
                guess_render.append(get_ansi_raw(guess[j], style=ANSI_Style.bold, color=ANSI_Color.grey))
            elif res == 'misplaced':
                guess_render.append(get_ansi_raw(guess[j], style=ANSI_Style.bold, color=ANSI_Color.blue))
            elif res == 'matching':
                guess_render.append(get_ansi_raw(guess[j], style=ANSI_Style.bold, color=ANSI_Color.green))
            else:
                guess_render.append(get_ansi_raw(guess[j], style=ANSI_Style.bold, color=ANSI_Color.red))
        render_list.append(' '.join(guess_render))
    
    return '\n'.join(render_list)

def _render_alphabet(response: any):
    alpha_bits = response['alpha_bits']
    render_list = []
    for i in range(len(ALPHABET)):
        if alpha_bits & (1 << i):
            render_list.append(get_ansi_raw(ALPHABET[i], style=ANSI_Style.bold, color=ANSI_Color.white))
        else:
            render_list.append(get_ansi_raw(ALPHABET[i], style=ANSI_Style.normal, color=ANSI_Color.grey))
    return ' '.join(render_list)

def _render_game_raw(response: any):
    previous_guesses = _render_previous_guesses(response)
    alphabet = _render_alphabet(response)

    if previous_guesses:
        return f'{previous_guesses}\n\n{alphabet}'
    else:
        return alphabet

def _generate_win(response: any):
    title=get_ansi_raw("Winner", style=ANSI_Style.bold_underline, color=ANSI_Color.yellow)
    body_main=get_ansi_raw(f"You completed the daily longdle in {response['guess_count']} guesses and gained {response['reward'] / 100} peanuts 🎉 Thanks for playing today, come back tomorrow for another puzzle!")
    embed = Embed(
        description=wrap_list([title, body_main, _render_game_raw(response)]),
        color=0xffd500
    )
    embed.set_footer(text=f"Game: {response['date_string']} (Resets 4am EST)")
    return embed

def _generate_already_won(response: any):
    title=get_ansi_raw("Already Won", style=ANSI_Style.bold_underline, color=ANSI_Color.yellow)
    body_main=get_ansi_raw(f"You already completed the daily longdle in {response['guess_count']} guesses and gained {response['reward'] / 100} peanuts 🎉 Thanks for playing today, come back tomorrow for another puzzle!\n\nToday's word for you was {response['answer']}")
    embed = Embed(
        description=wrap_list([title, body_main, _render_game_raw(response)]), 
        color=0xffd500
    )
    embed.set_footer(text=f"Game: {response['date_string']} (Resets 4am EST)")
    return embed

def _generate_miss(response: any):
    title = get_ansi_raw('Miss', style=ANSI_Style.bold_underline, color=ANSI_Color.blue)
    body_main=get_ansi_raw(f"Today's word is {response['word_length']} letters long. In Longdle, this can be the name of a well-known entity, i.e. the name of a company, person, or other entity.\n\nReminder that your guess can be 6 - {response['word_length']} characters long. You have {response['guess_remaining']} guesses remaining today.")
    
    if response['guess_remaining'] == 0:
        embed = Embed(
            description=wrap_list([title, _render_game_raw(response)]) + f"\nOut of Tries! Today's word was: ||{response['answer']}||", 
            color=0x5539cc
        )
    else:
        embed = Embed(
            description=wrap_list([title, body_main, _render_game_raw(response)]), 
            color=0x5539cc
        )
    embed.set_footer(text=f"Game: {response['date_string']} (Resets 4am EST)")

    return embed

def _generate_out_of_tries(response: any):
    title=get_ansi_raw("Out of Tries", style=ANSI_Style.bold_underline, color=ANSI_Color.white)
    embed = Embed(
        description=wrap_list([title, _render_game_raw(response)]) + f"\nCome back next tomorrow for more exciting puzzles!\nToday's word for you was ||`{response['answer']}`||", 
        color=0xffffff
    )
    embed.set_footer(text=f"Game: {response['date_string']} (Resets 4am EST)")

    return embed

def _generate_invalid_guess(response: any):
    title = get_ansi_raw('Invalid Guess', style=ANSI_Style.bold_underline, color=ANSI_Color.white)
    body_main=get_ansi_raw(f"Message: {response['message']}\n\nToday's word is {response['word_length']} letters long. In Longdle, this can be the name of a well-known entity, i.e. the name of a company, person, or other entity.\n\nReminder that your guess can be 6 - {response['word_length']} characters long. You have {response['guess_remaining']} guesses remaining today.")
    
    embed = Embed(
        description=wrap_list([title, body_main, _render_game_raw(response)]), 
        color=0xffffff
    )
    embed.set_footer(text=f"Game: {response['date_string']} (Resets 4am EST)")

    return embed

def _generate_error(response: any):
    embed = Embed(
        title="Error", 
        description=f"An error occurred, please contact Alex to fix the situation.\nMessage: {response['message']}", 
        color=0xff0000
    )
    
    return embed

def _generate_custom_rejected(response: any):
    title = get_ansi_raw('Rejected', style=ANSI_Style.bold_underline, color=ANSI_Color.white)
    body_main=get_ansi_raw(response['message'])
    
    embed = Embed(
        description=wrap_list([title, body_main]), 
        color=0xffffff
    )

    return embed

def _generate_custom_accepted(response: any):
    title = get_ansi_raw('Success', style=ANSI_Style.bold_underline, color=ANSI_Color.green)
    body_main=get_ansi_raw(response['message'])
    
    embed = Embed(
        description=wrap_list([title, body_main]), 
        color=0xffffff
    )

    return embed
