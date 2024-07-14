from discord.ext.commands import Cog, command
import requests

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.route = bot.routes['banking']

    @command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    async def balance(self, ctx):
        r = requests.post(f'{self.route}/', {'queries': ['']})
        await ctx.send('Balance')

async def setup(bot):
    await bot.add_cog(Bank(bot))