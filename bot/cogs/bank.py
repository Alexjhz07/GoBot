from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from utils.bank import fetch_balance
from utils.user import user_mention_to_id

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    @commands.cooldown(1, 1, BucketType.user)
    async def balance(self, ctx: Context):
        bal = await fetch_balance(ctx.author.id)
        await ctx.send(f'Current Balance: {bal}')

    @commands.command(brief='Shows the balance of the user', aliases=['give', 'feed'])
    @commands.cooldown(1, 5, BucketType.user)
    async def donate(self, ctx: Context, amount: str, target: str):
        target_id = user_mention_to_id(target)
        if target_id == ctx.author.id: return await ctx.send("Error: Cannot send funds to yourself")
        if target_id == 0: return await ctx.send("Error: This is an invalid target id")
        print(target_id)

async def setup(bot):
    await bot.add_cog(Bank(bot))