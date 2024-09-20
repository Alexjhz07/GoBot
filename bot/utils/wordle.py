from discord import Embed, ButtonStyle
from discord.ui import View, Button
from utils.db import post

COLOUR_MAP = {
    "matching": ButtonStyle.success,
    "misplaced": ButtonStyle.blurple,
    "absent": ButtonStyle.gray
}

class WordleView(View):
    def __init__(self, resp):
        super().__init__()

        letters = resp['guess']
        results = resp['result']

        for i in range(len(letters)):
            self.add_item(Button(label=letters[i], style=COLOUR_MAP[results[i]], disabled=True))

async def get_wordle_response(user_id: int, guess: str) -> list:
    response = await post('wordle', 'game', { "user_id": user_id, "guess": guess })
    if response['status'] == 'miss':
        return generate_miss(response)
    elif response['status'] == 'invalid-guess':
        return generate_invalid_guess(response)
    elif response['status'] == 'out-of-tries':
        return generate_out_of_tries(response)
    elif response['status'] == 'win':
        return generate_win(response)
    elif response['status'] == 'already-won':
        return generate_already_won(response)
    elif response['status'] == 'error':
        return generate_error(response)
    
def generate_win(resp: any):
    embed = Embed(
        title="Winner Winner Chicken Dinner", 
        description=f"You completed the daily wordle in {resp['guess_count']} guesses and gained {resp['reward'] / 100} peanuts :tada:\nThanks for playing today, come back tomorrow for another puzzle!", 
        color=0xffd500
    )
    view = WordleView(resp)

    return [embed, view]

def generate_already_won(resp: any):
    embed = Embed(
        title="Already Won", 
        description=f"You completed the daily wordle in {resp['guess_count']} guesses and gained {resp['reward'] / 100} peanuts :tada:\nThanks for playing today, come back tomorrow for another puzzle!\nToday's word for you was ||`{resp['answer']}`||", 
        color=0xffd500
    )
    
    return [embed]

def generate_miss(resp: any):
    titles = [
        "A little far off",
        "One is more than none",
        "Getting warmer",
        "Now what could this be?",
        "On the tip of your tongue",
        "Well... this is awkward...",
    ]

    embed = Embed(
        title=titles[resp['matching'] + resp['misplaced']], 
        description=f"Nice try, but no cigar\nYou have {6 - resp['guess_count']} guesses remaining\n\nGrey = This letter is not in the word\nBlue = This letter is in the word but is in the wrong spot\nGreen = This letter is in the word and is in the right spot", 
        color=0x5539cc
    )
    embed.set_footer(text='Rewards are higher for winning with fewer guesses:\n4k, 2k, 1k, 500, 250, 125')

    view = WordleView(resp)

    return [embed, view]

def generate_out_of_tries(resp: any):
    embed = Embed(
        title="Out of tries", 
        description=f"Come back next tomorrow for more exciting puzzles!\nToday's word for you was ||`{resp['answer']}`||", 
        color=0xffffff
    )

    return [embed]

def generate_invalid_guess(resp: any):
    embed = Embed(
        title="Invalid Guess", 
        description=f"The word is 5 letters long and cannot be the name of a person or place\nYou have {6 - resp['guess_count']} attempts remaining, good luck! (This guess does not count)", 
        color=0xffffff
    )

    return [embed]

def generate_error(resp: any):
    embed = Embed(
        title="Error", 
        description=f"An error occurred, please contact Alex to fix the situation.\nMessage: {resp['message']}", 
        color=0xff0000
    )
    
    return [embed]