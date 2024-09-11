from yfinance import Ticker
from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from discord import Embed
from utils.bank import fetch_balance, add_funds

class Stocks(Cog):
    # Unforunately, it seems like the default yf lib uses requests and is thus single threaded
    # Perhaps in the future, I can research for a way to make this multithreaded
    @commands.command(brief='Flip a coin for double the peanuts or nothing!', aliases=['q'], ignore_extra=False)
    @commands.cooldown(5, 1, BucketType.user)
    async def quote(self, ctx: Context, ticker_symbol: str):
        ticker_symbol = ticker_symbol.upper()

        stock = Ticker(ticker_symbol).info
        if stock.get('ask') == None: return await ctx.reply(f'Error: Stock with ticker symbol {ticker_symbol} not found')

        embed=Embed(title=ticker_symbol, url=stock.get('website', None), description=stock.get('longName'), color=0xffffff)
        embed.add_field(name="Current Price", value=stock.get('ask'), inline=True)
        embed.add_field(name="Day Low", value=stock.get('dayLow'), inline=True)
        embed.add_field(name="Day High", value=stock.get('dayHigh'), inline=True)
        embed.add_field(name="50 day average", value=stock.get('fiftyDayAverage'), inline=True)
        embed.add_field(name="Industry", value=stock.get('industry'), inline=True)
        embed.add_field(name="Market Cap", value=f"{stock.get('marketCap', ''):,}", inline=True)
        
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Stocks())