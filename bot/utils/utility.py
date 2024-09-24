from utils.db import post
from lib.exceptions import InvalidLinkCodeException

async def fetch_stats(user_id: int):
    res = await post('db', 'query', {
        'queries': [
                'SELECT experience FROM user_experience where user_id = $1',
                "SELECT COUNT(*) AS stonk_count, COALESCE(SUM(transaction_amount), 0) AS stonk_sum FROM bank_transactions WHERE transaction_type = 'stonks' AND user_id = $1",
                "SELECT COUNT(*) AS flip_won_count, COALESCE(SUM(transaction_amount), 0) AS flip_won_sum FROM bank_transactions WHERE transaction_type = 'flip' AND user_id = $1 AND transaction_amount > 0",
                "SELECT COUNT(*) AS flip_lost_count, COALESCE(SUM(transaction_amount), 0) AS flip_lost_sum FROM bank_transactions WHERE transaction_type = 'flip' AND user_id = $1 AND transaction_amount < 0",
            ], 
        'arguments': [
                [user_id],
                [user_id],
                [user_id],
                [user_id],
            ]
    })

    acc = dict()

    for item in res['responses']:
        acc.update(item[0])

    return acc

async def link_account(code: str, user_id: int):
    res = await post('db', 'query', {
        'queries': ["SELECT t.email, t.created_at FROM (SELECT DISTINCT ON (email) email, code, user_id, created_at FROM user_linking_history WHERE created_at >= NOW() - INTERVAL '10 minutes' ORDER BY email, created_at desc, user_id) AS t WHERE t.user_id = -1 AND code = $1"], 
        'arguments': [[code]]
    })

    res = res['responses'][0]

    if len(res) == 0:
        raise InvalidLinkCodeException('The code entered is either invalid or expired\nPlease try again with a different code')
    if len(res) > 1:
        raise InvalidLinkCodeException('Duplicate codes have been found\nPlease regenerate your code and try again')
    
    email = res[0]['email']
    created_at = res[0]['created_at']

    res = await post('db', 'exec', {
        'queries': [
            "UPDATE user_linking_history SET user_id=$1 WHERE email=$2 AND code=$3 AND created_at=$4",
            "UPDATE user_authentication SET user_id=$1 WHERE email=$2"
        ], 
        'arguments': [
            [user_id, email, code, created_at],
            [user_id, email]
        ]
    })