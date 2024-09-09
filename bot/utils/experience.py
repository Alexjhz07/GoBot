from utils.db import post

async def add_experience(user_id: int, experience: int):
    await post('db', 'query', {'queries': ['UPDATE user_experience SET experience = experience + $1 WHERE user_id=$2'], 'arguments': [[experience, user_id]]})