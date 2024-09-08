from utils.db import post
from discord import Member

async def check_user_exists(user_id: int):
    res = await post('db', 'query', {'queries': ['SELECT COUNT(1) FROM user_information WHERE user_id=$1'], 'arguments': [[user_id]]})
    return res['responses'][0][0]['count'] == '1'

async def assert_user_exists(user: Member):
    user_exists = await check_user_exists(user.id)
    if (not user_exists):
        await post('db', 'exec', {'queries': ['INSERT INTO user_information (user_id, username, nickname, avatar_url) VALUES ($1, $2, $3, $4)'], 'arguments': [[user.id, user.name, user.nick, str(user.avatar)]]})

def user_mention_to_id(user_mention: str):
    try:
        return int(user_mention.replace("<", "").replace("@", "").replace(">", ""))
    except Exception as e:
        return 0