from discord.ext.commands import Cog, Context, command
from discord.ext import commands
from discord import Message

class Test(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(brief='Testt', aliases=['tt', 't'])
    async def test(self, ctx: Context):
        await ctx.send('Test1')
        import asyncio
        await asyncio.sleep(10)
        await ctx.send('Test2')

async def setup(bot):
    await bot.add_cog(Test(bot))