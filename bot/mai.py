from os import getenv
from asyncio import run
from discord import Intents
from dotenv import load_dotenv
from bo import GBot

# LOAD ========================================================================

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("BOT_PREFIX")
INTENTS = Intents.all()

# RUN =========================================================================

bot = GBot(command_prefix=PREFIX, intents=INTENTS) # Our Bot Instance

async def main():
    await bot.start(TOKEN) # Note that this will block until the bot stops running
    print('Graceful exit completed')

run(main())