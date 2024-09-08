from discord.ext.commands import Cog
from discord.ext import commands

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx):
        print("hi")

async def setup(bot):
    await bot.add_cog(Bank(bot))