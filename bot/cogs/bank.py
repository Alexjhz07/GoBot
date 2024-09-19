from lib.exceptions import BankTimerException
from random import randint
from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from utils.bank import fetch_balance, add_funds, transfer_funds, collect_timely_funds
from utils.user import user_mention_to_id, check_user_exists
from utils.caster import number_g

class Bank(Cog):
    @commands.command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    @commands.cooldown(1, 1, BucketType.user)
    async def balance(self, ctx: Context):
        bal = await fetch_balance(ctx.author.id)
        await ctx.reply(f'Current Balance: {bal} peanuts')

    @commands.command(brief='Shows the balance of the user', aliases=['give', 'feed'], ignore_extra=False)
    @commands.cooldown(1, 5, BucketType.user)
    async def donate(self, ctx: Context, amount: str, target: str):
        target_id = user_mention_to_id(target)
        if target_id == ctx.author.id: return await ctx.reply("Error: Cannot send funds to yourself")
        if target_id == 0: return await ctx.reply("Error: This is an invalid target id")

        amount = number_g(amount)
        
        bal = await fetch_balance(ctx.author.id)
        if bal < amount: return await ctx.reply(f'Error: Insufficient balance ({bal})')

        if not await check_user_exists(target_id): return await ctx.reply(f'Error: User with id {target_id} does not exist')

        await transfer_funds(ctx.author.id, amount, target_id)
        await ctx.reply(f'Successfully transferred {amount} peanuts')

    @commands.command(brief='Variable but frequent income', aliases=['s'])
    @commands.cooldown(1, 180, BucketType.user)
    async def stonks(self, ctx: Context):
        user_id = ctx.author.id
        peanuts = randint(100, 5000)
        jackpot = randint(1, 100)
        
        author_name = ctx.author.nick or ctx.author.name

        if jackpot == 42:
            await add_funds(user_id, 30000, 'jackpot')
            bal = await fetch_balance(user_id)
            await ctx.reply(f'***JACKPOT!***\n${author_name} just won the stonks jackpot!\n*30000* peanuts were added to their balance!\nThey now have {bal} peanuts in their account')
        
        await add_funds(user_id, peanuts, 'stonks')
        bal = await fetch_balance(user_id)

        if peanuts == 100:
            await ctx.reply(f"The stonks are not very high today...\n{author_name} just received {peanuts} peanut from the heavens.\nTheir pocket is now at {bal} peanuts.")
        elif peanuts < 1500:
            await ctx.reply(f"{author_name} just had {peanuts} more peanuts added to their pockets.\nTheir balance is now {bal} peanuts.")
        elif peanuts < 3500:
            await ctx.reply(f"A great day for stonks!\n{author_name} just received {peanuts} peanuts.\nTheir balance is now {bal} peanuts.")
        else:
            await ctx.reply(f"Big stonks!\n{author_name} just received {peanuts} peanuts.\nTheir balance is now {bal} peanuts.")

    @commands.command(brief='Daily income')
    @commands.cooldown(1, 30, BucketType.user)
    async def daily(self, ctx: Context):
        try:
            collected = await collect_timely_funds(ctx.author.id, 'daily')
            balance = await fetch_balance(ctx.author.id)
            await ctx.reply(f"Successfully collected {collected} peanuts from daily!\nYour now have {balance} peanuts in your wallet")
        except BankTimerException as e:
            await ctx.reply(e)

    @commands.command(brief='Weekly income')
    @commands.cooldown(1, 30, BucketType.user)
    async def weekly(self, ctx: Context):
        try:
            collected = await collect_timely_funds(ctx.author.id, 'weekly')
            balance = await fetch_balance(ctx.author.id)
            await ctx.reply(f"Successfully collected {collected} peanuts from weekly!\nYour now have {balance} peanuts in your wallet")
        except BankTimerException as e:
            await ctx.reply(e)

    @commands.command(brief='Monthly income')
    @commands.cooldown(1, 30, BucketType.user)
    async def monthly(self, ctx: Context):
        try:
            collected = await collect_timely_funds(ctx.author.id, 'monthly')
            balance = await fetch_balance(ctx.author.id)
            await ctx.reply(f"Successfully collected {collected} peanuts from monthly!\nYour now have {balance} peanuts in your wallet")
        except BankTimerException as e:
            await ctx.reply(e)

        

async def setup(bot):
    await bot.add_cog(Bank())