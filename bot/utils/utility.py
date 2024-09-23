from utils.db import post

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