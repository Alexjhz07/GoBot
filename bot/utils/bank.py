from lib.exceptions import BankTimerException
from utils.db import post
from utils.caster import str_time_until
from uuid import uuid4

async def fetch_balance(user_id: int):
    res = await post('db', 'query', {'queries': ['SELECT SUM(transaction_amount) FROM bank_transactions WHERE user_id=$1'], 'arguments': [[user_id]]})
    
    raw = res['responses'][0][0]['sum']
    if raw == '': raw = 0

    return int(raw)

async def add_funds(user_id: int, amount: int, type: str):
    await post('db', 'exec', {
        'queries': ['INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id) VALUES ($1, $2, $3)'], 
        'arguments': [[type, amount, user_id]]
    })

async def transfer_funds(origin_id: int, amount: int, target_id: int):
    group_uuid = str(uuid4())

    await post('db', 'exec', {
        'queries': [
                'INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)',
                'INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)'
            ], 
        'arguments': [
                ['transfer', -amount, origin_id, group_uuid],
                ['transfer', amount, target_id, group_uuid]
            ]
    })

async def timer_status(user_id: int, timer: str):
    result = await post('db', 'query', {
        'queries': [f'SELECT NOW() > {timer} AS status, {timer} AS next FROM bank_timer WHERE user_id=$1'], 
        'arguments': [[user_id]]
    })
    result = result['responses'][0][0]
    return result['status'] == 'true', result['next']

async def collect_timely_funds(user_id: int, timer: str):
    timer_finished, next_date = await timer_status(user_id, timer)
    if not timer_finished: raise BankTimerException(f'Your next {timer} is in {str_time_until(next_date)}')

    REWARDS = {'daily': 6000, 'weekly': 18000, 'monthly': 80000}
    INTERVALS = {'daily': '1 day', 'weekly': '1 week', 'monthly': '1 month'}

    await post('db', 'exec', {
        'queries': [
            'INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id) VALUES ($1, $2, $3)',
            f"UPDATE bank_timer set {timer} = NOW() + interval '{INTERVALS[timer]}' where user_id = $1"
        ], 
        'arguments': [
            [timer, REWARDS[timer], user_id],
            [user_id]
        ]
    })

    return REWARDS[timer]
    