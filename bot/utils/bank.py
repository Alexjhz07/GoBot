from utils.db import post
from uuid import uuid4

async def fetch_balance(user_id: int):
    res = await post('db', 'query', {'queries': ['SELECT SUM(transaction_amount) FROM bank_transactions WHERE user_id=$1'], 'arguments': [[user_id]]})
    
    raw = res['responses'][0][0]['sum']
    if raw == '': raw = 0

    return int(raw)

async def send_money(origin_id: int, amount: int, target_id: int):
    group_uuid = str(uuid4())

    await post('db', 'query', {
        'queries': [
                'INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)',
                'INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)'
            ], 
        'arguments': [
                ['transfer', -amount, origin_id, group_uuid],
                ['transfer', amount, target_id, group_uuid]
            ]
    })