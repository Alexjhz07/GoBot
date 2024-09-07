from discord.ext.commands import Cog, Context, Bot
from discord.ext import commands

import os
OWNER = int(os.getenv('BOT_OWNER'))

class Admin(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    async def is_admin(self, ctx: Context):
        if (ctx.author.id != OWNER):
            await ctx.send('Insufficient Permissions')
            return False
        return True

    @commands.command(brief='Reload all cogs', aliases=['restart', 'rel'])
    async def reload(self, ctx: Context):
        if (not await self.is_admin(ctx)): return
        
        cogs = []
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cogs.append(filename[:-3])
                await self.bot.reload_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename}')
        
        await ctx.send(f'Cogs Reloaded: [{", ".join(cogs)}]')

    @commands.command(brief='Shutdown system gracefully')
    async def shutdown(self, ctx: Context):
        await ctx.send("Going to sleep")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))