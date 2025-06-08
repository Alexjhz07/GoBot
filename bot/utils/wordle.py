from discord import Embed, File
from utils.db import post
from utils.image import generate_wordle_image
from random import randint

async def get_wordle_response(user_id: int, guess: str) -> list:
    response = await post('wordle', 'wordle', { "user_id": str(user_id), "guess": guess })

    if response['status'] == 'error':
        return _generate_error(response), None
    
    filename, filepath = generate_wordle_image(guesses=response['previous_guesses'], results=response['previous_results'], user_id=user_id)
    image = File(filepath, filename=filename)

    if response['status'] == 'miss':
        embed = _generate_miss(response)
    elif response['status'] == 'invalid-guess':
        embed = _generate_invalid_guess(response)
    elif response['status'] == 'out-of-tries':
        embed = _generate_out_of_tries(response)
    elif response['status'] == 'win':
        embed = _generate_win(response)
    elif response['status'] == 'already-won':
        embed = _generate_already_won(response)

    embed.set_image(url=f'attachment://{filename}')
    return embed, image

def _generate_win(resp: any):
    embed = Embed(
        title=_get_title(5, 0), 
        description=f"You completed the daily wordle in {resp['guess_count']} guesses and gained {resp['reward'] / 100} peanuts :tada:\nThanks for playing today, come back tomorrow for another puzzle!", 
        color=0xffd500
    )
    return embed

def _generate_already_won(resp: any):
    embed = Embed(
        title="Already Won", 
        description=f"You completed the daily wordle in {resp['guess_count']} guesses and gained {resp['reward'] / 100} peanuts :tada:\nThanks for playing today, come back tomorrow for another puzzle!\nToday's word for you was ||`{resp['answer']}`||", 
        color=0xffd500
    )
    return embed

def _generate_miss(resp: any):
    embed = Embed(
        title=_get_title(resp['matching'], resp['misplaced']), 
        description=f"Nice try, but not quite there.\nYou have {6 - resp['guess_count']} guesses remaining", 
        color=0x5539cc
    )
    embed.set_footer(text='Rewards are higher for winning with fewer guesses:\n4k, 2k, 1k, 500, 250, 125')
    return embed

def _generate_out_of_tries(resp: any):
    embed = Embed(
        title="Out of tries", 
        description=f"Come back next tomorrow for more exciting puzzles!\nToday's word for you was ||`{resp['answer']}`||", 
        color=0xffffff
    )
    return embed

def _generate_invalid_guess(resp: any):
    embed = Embed(
        title="Invalid Guess", 
        description=f"The word is 5 letters long and cannot be the name of a person or place\nYou have {6 - resp['guess_count']} attempts remaining, good luck! (This guess does not count)", 
        color=0xffffff
    )
    return embed

def _generate_error(resp: any):
    embed = Embed(
        title="Error", 
        description=f"An error occurred, please contact Alex to fix the situation.\nMessage: {resp['message']}", 
        color=0xff0000
    )
    return embed

def _get_title(matching_count: int, misplaced_count: int):
    titles = [
        [ # 0 Correct
            ["A little far off", "Quite the long shot", "Not Even Close!", "Back to the Drawing Board", "Overcooked", "An ally has been slain"], # 0 Misplaced
            ["One is more than none", "We're on the map!", "Enemy spotted", "That's one small step for man", "Just a Taste"], # 1 Misplaced
            ["Prepare for trouble", "Romeo and Juliet", "Salt and Pepper", "Right foot left shoe"], # 2 Misplaced
            ["Something's cooking", "3 letters in play", "Some assembly required", "On the right path"], # 3 Misplaced
            ["Chat is this real?", "So close yet so far", "Permutations permutation permutations..."], # 4 Misplaced
            ["How did we even get here...", "I'm not even sure what to say...", "This is rather impressive", "Dyslexia"] # 5 Misplaced
        ],
        [ # 1 Correct
            ["One giant leap for mankind", "One step closer", "A glimmer of hope", "On the right track", "An enemy has been slain"],
            ["One is in the mix", "Just a bit off", "A good start!"],
            ["Got the right idea", "Two letters in play", "Almost a breakthrough"],
            ["Fairly close!", "Nearing completion", "More than just a hint"],
            ["Eurek- what?", "Befuddled...", "What a twist!"]
        ],
        [ # 2 Correct
            ["Two steps forward", "Getting warmer", "Just about there", "Two letter conspiracy", "Double kill!"],
            ["Almost a trio", "A solid effort!", "Wingman"],
            ["Moves and countermoves...", "Solid attempt", "Someone's cooking..."],
            ["Welcome to the wild, no heroes and villains", "Just around the corner", "Triple inhibitors!"]
        ],
        [ # 3 Correct
            ["Now what could this be?", "Triple kill!", "On the tip of your tongue"],
            ["An inhibitor has been destroyed", "3 course meal plus dessert", "Final stretch"],
            ["Body swap", "Mirrored images", "Well... This is awkward"]
        ],
        [ # 4 Correct
            ["Chef???", "Double date", "Quadra kill!", "Michelin style dish"]
        ],
        [ # 5 Correct (Win)
            ["Penta Kill!", "Winner Winner Chicken Dinner", "Triumphant", "GGWP", "Another day, another W", "Sherlock Holmes"]
        ]
    ]
    return titles[matching_count][misplaced_count][randint(0, len(titles[matching_count][misplaced_count]) - 1)]