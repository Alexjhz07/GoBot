from discord import Game
from discord.ext import commands

class Client(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Successfully Logged in as {self.bot.user}')
        await self.bot.change_presence(activity=Game(name="Cops & Robbers"))

async def setup(bot):
    await bot.add_cog(Client(bot))