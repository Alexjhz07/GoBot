import os
import asyncio
import discord

from discord.ext.commands import Bot, MinimalHelpCommand
from dotenv import load_dotenv

# LOAD ========================================================================

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PREFIX = os.getenv("BOT_PREFIX")

intents = discord.Intents.all()
bot = Bot(command_prefix=PREFIX, intents=intents)

# RUN =========================================================================

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename}')

async def main():
    bot.locked_users = {}
    bot.routes = {
        'experience': 'http://localhost:3816/api/v1',
        'banking': 'http://localhost:3817/api/v1',
    }
    bot.help_command = MinimalHelpCommand(no_category='Commands')
    await load()
    await bot.start(TOKEN) # Note that this will block until the bot stops running
    print('Graceful exit completed')

asyncio.run(main())