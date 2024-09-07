from discord.ext.commands import Cog, command
import aiohttp

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    async def balance(self, ctx):
        # r = await aiohttp (f'{self.route}/', {'queries': ['']})
        # await ctx.send('Balance')
        print("hi")

async def setup(bot):
    await bot.add_cog(Bank(bot))