from discord.ext.commands import Cog, command

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    async def balance(self, ctx):
        await ctx.send('Balance')

async def setup(bot):
    await bot.add_cog(Bank(bot))