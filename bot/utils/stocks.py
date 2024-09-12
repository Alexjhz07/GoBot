from utils.db import post

async def stock_transaction(user_id: int, ticker_symbol: str, transaction_amount: int, transaction_stocks: int):
    await post('db', 'exec', {
        'queries': [
                'INSERT INTO stock_transactions (ticker_symbol, transaction_amount, transaction_stocks, user_id) VALUES ($1, $2, $3, $4)',
                'INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id) VALUES ($1, $2, $3)'
            ], 
        'arguments': [
                [ticker_symbol, transaction_amount, transaction_stocks, user_id],
                ['stock', transaction_amount, user_id]
            ]
    })

async def fetch_stocks(user_id: int, ticker_symbol: str):
    res = await post('db', 'query', {'queries': ['SELECT SUM(transaction_stocks) FROM stock_transactions WHERE ticker_symbol=$1 AND user_id=$2'], 'arguments': [[ticker_symbol, user_id]]})
    
    raw = res['responses'][0][0]['sum']
    if raw == '': raw = 0

    return int(raw)