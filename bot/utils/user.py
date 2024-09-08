from utils.db import post
from discord import Member

async def assert_user_exists(user: Member):
    res = await post('db', 'query', {'queries': ['SELECT COUNT(1) FROM user_information WHERE user_id=$1'], 'arguments': [[user.id]]})
    if res == None: return False
    if (res['responses'][0][0]['count'] == '0'):
        user_created = await post('db', 'exec', {'queries': ['INSERT INTO user_information (user_id, username, nickname, avatar_url) VALUES ($1, $2, $3, $4)'], 'arguments': [[user.id, user.name, user.nick, str(user.avatar)]]})
    return True