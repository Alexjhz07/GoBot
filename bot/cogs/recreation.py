from random import randint
from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from utils.bank import fetch_balance, add_funds

class Recreation(Cog):
    @commands.command(brief='Flip a coin for double the peanuts or nothing!', aliases=['flip'], ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def bet(self, ctx: Context, amount: str, prediction: str):
        try:
            prediction = prediction[0].lower()
            amount = int(amount)
        except Exception as e:
            return await ctx.reply('Error: Amount is invalid')
        
        if amount <= 0: return await ctx.reply('Error: Amount must be greater than 0')
        if prediction not in ['h', 't']: return await ctx.reply('Error: Valid bets are `h`, `t`, or any word that starts with those letters')
        bal = await fetch_balance(ctx.author.id)
        if bal < amount: await ctx.reply(f'Error: Insufficent balance: {bal}')

        # I know that this could just be a 50/50 random implementation.
        # However, some things feel different even if they are the same
        
        result = 'heads' if randint(0,3) % 2 == 1 else 'tails'
        prediction = 'heads' if prediction == 'h' else 'tails'
        if prediction == result:
            await add_funds(ctx.author.id, amount, 'flip')
            await ctx.reply(f'Success! You bet `{prediction}` and the coin landed `{result}` up.\nYou just gained {amount} peanuts, your pockets now contain {bal + amount} peanuts.')
        else:
            await add_funds(ctx.author.id, -amount, 'flip')
            await ctx.reply(f'Bad luck... You bet `{prediction}` and the coin landed `{result}` up.\nYou just lost {amount} peanuts, your pockets now contain {bal - amount} peanuts.')


async def setup(bot):
    await bot.add_cog(Recreation())