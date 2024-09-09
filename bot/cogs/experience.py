from random import randint
from time import time
from discord import Message
from discord.ext.commands import Cog
from utils.experience import add_experience

class Experience(Cog):
    def __init__(self):
        self.timers = {}

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot: return
        if self.timers.get(message.author.id, 0) > time(): return

        exp = randint(1, 50)
        next_time = time() + randint(0, 180) + 120
        
        await add_experience(message.author.id, exp)
        self.timers[message.author.id] = next_time


async def setup(bot):
    await bot.add_cog(Experience())