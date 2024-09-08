from utils.db import post

async def fetch_balance(user_id: int):
    res = await post('db', 'query', {'queries': ['SELECT SUM(transaction_amount) FROM bank_transactions WHERE user_id=$1'], 'arguments': [[user_id]]})
    if res == None: return None
    
    raw = res['responses'][0][0]['sum']
    if raw == '': raw = 0

    return int(raw)