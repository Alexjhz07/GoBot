from yfinance import Ticker
from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from discord import Embed
from utils.bank import fetch_balance
from utils.stocks import stock_transaction, fetch_stocks
from utils.caster import number_g
from lib.exceptions import StockNotFoundException

class Stock():
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol.upper()
        stock = Ticker(ticker_symbol).info
        if stock.get('ask') == None: raise StockNotFoundException(f'Stock with ticker symbol `{self.ticker_symbol}` not found')
        self.website = stock.get('website')
        self.longName = stock.get('longName')
        self.price = int(stock.get('ask') * 100)
        self.dayLow = int(stock.get('dayLow') * 100)
        self.dayHigh = int(stock.get('dayHigh') * 100)
        self.fiftyDayAverage = int(stock.get('fiftyDayAverage') * 100)
        self.industry = stock.get('industry')
        self.marketCap = stock.get('marketCap')

    def get_embed(self):
        embed=Embed(title=self.ticker_symbol, url=self.website, description=self.longName, color=0xffffff)
        embed.add_field(name="Current Price (₱)", value=self.price, inline=True)
        embed.add_field(name="Day Low (₱)", value=self.dayLow, inline=True)
        embed.add_field(name="Day High (₱)", value=self.dayHigh, inline=True)
        embed.add_field(name="50 day average (₱)", value=self.fiftyDayAverage, inline=True)
        embed.add_field(name="Industry", value=self.industry, inline=True)
        embed.add_field(name="Market Cap ($)", value=f"{self.marketCap:,}", inline=True)
        embed.set_footer(text="\ufeff\nNote that 1 USD = 100 peanuts. All values except Market Cap are displayed in peanuts")
        return embed

class Stocks(Cog):
    # Unfortunately, it seems like the default yf lib uses requests and is thus single threaded
    # Perhaps in the future, I can research for a way to make this multithreaded
    @commands.command(brief='Quotes a stock. Argument: symbol', aliases=['q'], ignore_extra=False)
    @commands.cooldown(5, 1, BucketType.user)
    async def quote(self, ctx: Context, ticker_symbol: str):
        stock = Stock(ticker_symbol)
        await ctx.reply(embed=stock.get_embed())

    @commands.command(brief='Invest your peanuts! Arguments in order: amount, symbol', aliases=['invest'], ignore_extra=False)
    @commands.cooldown(1, 5, BucketType.user)
    async def buy(self, ctx: Context, amount: str, ticker_symbol: str):
        amount = number_g(amount)
        stock = Stock(ticker_symbol)
        bal = await fetch_balance(ctx.author.id)
        price = (stock.price * amount)

        if bal < price: return await ctx.reply(f'Error: Insufficient balance ({bal}) Required: ({stock.price * amount})')

        await stock_transaction(ctx.author.id, stock.ticker_symbol, -price, amount)
        await ctx.reply(f'Successfully purchased {amount} `{stock.ticker_symbol}` stocks for {price} peanuts\nYour balance is now at {bal - price} peanuts')

    @commands.command(brief='Relish in your earnings! Arguments in order: amount, symbol', aliases=['liquidate'], ignore_extra=False)
    @commands.cooldown(1, 5, BucketType.user)
    async def sell(self, ctx: Context, amount: str, ticker_symbol: str):
        amount = number_g(amount)
        stock = Stock(ticker_symbol)
        bal = await fetch_balance(ctx.author.id)
        gains = (stock.price * amount)
        available = await fetch_stocks(ctx.author.id, stock.ticker_symbol)

        if available < amount: return await ctx.reply(f'Error: Insufficient stocks to sell ({available}) Wanted: ({amount})')

        await stock_transaction(ctx.author.id, stock.ticker_symbol, gains, -amount)
        await ctx.reply(f'Successfully sold {amount} `{stock.ticker_symbol}` stocks for {gains} peanuts\nYour balance is now at {bal + gains} peanuts')


async def setup(bot):
    await bot.add_cog(Stocks())