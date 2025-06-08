from random import randint
from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from utils.bank import fetch_balance, add_funds
from utils.wordle import get_wordle_response
from utils.longdle import get_longdle_response, get_longdle_intro, get_longdle_length, add_longdle_word

class Recreation(Cog):
    @commands.command(brief='Flip a coin for double the peanuts or nothing!', aliases=['flip'], ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def bet(self, ctx: Context, amount: str, prediction: str):
        try:
            prediction = prediction[0].lower()
            amount = int(amount) * 100
        except Exception as e:
            return await ctx.reply('Error: Amount is invalid')
        
        if amount <= 0: return await ctx.reply('Error: Amount must be greater than 0')
        if prediction not in ['h', 't']: return await ctx.reply('Error: Valid bets are `h`, `t`, or any word that starts with those letters')
        bal = await fetch_balance(ctx.author.id)
        if bal < amount: await ctx.reply(f'Error: Insufficent balance: {bal / 100}')

        # I know that this could just be a 50/50 random implementation.
        # However, some things feel different even if they are the same
        
        result = 'heads' if randint(0,3) % 2 == 1 else 'tails'
        prediction = 'heads' if prediction == 'h' else 'tails'
        if prediction == result:
            await add_funds(ctx.author.id, amount, 'flip')
            await ctx.reply(f'Success! You bet `{prediction}` and the coin landed `{result}` up.\nYou gained {amount / 100} peanuts, your pockets now contain {(bal + amount) / 100} peanuts.')
        else:
            await add_funds(ctx.author.id, -amount, 'flip')
            await ctx.reply(f'Bad luck... You bet `{prediction}` and the coin landed `{result}` up.\nYou lost {amount / 100} peanuts, your pockets now contain {(bal - amount) / 100} peanuts.')

    @commands.command(brief='A pleasant game of wordle', aliases=['w'], ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def wordle(self, ctx: Context, guess: str):
        embed, file = await get_wordle_response(ctx.author.id, guess)
        await ctx.reply(embed=embed, file=file)

    @commands.command(brief='An intense game of longdle', aliases=['l', 'long'], ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def longdle(self, ctx: Context, guess: str = None):
        if guess == None:
            return await ctx.reply(embed=get_longdle_intro())
        await ctx.reply(embed=await get_longdle_response(ctx.author.id, guess))

    @commands.command(brief='Tells you the length of your word', aliases=['ll'], ignore_extra=True)
    @commands.cooldown(1, 1, BucketType.user)
    async def longlength(self, ctx: Context):
        await ctx.reply(await get_longdle_length(ctx.author.id))
        

    @commands.command(brief='Add a word to the accepted Longdle words for input', ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def longadd(self, ctx: Context, word: str):
        await ctx.reply(embed=await add_longdle_word(ctx.author.id, word))

async def setup(bot):
    await bot.add_cog(Recreation())