from discord.ext.commands import Cog, Context
from discord.ext import commands
from utils.bank import fetch_balance

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx: Context):
        bal = await fetch_balance(ctx.author.id)
        await ctx.send(f'Current Balance: {bal}')

async def setup(bot):
    await bot.add_cog(Bank(bot))