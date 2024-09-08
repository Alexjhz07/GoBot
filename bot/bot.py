from os import listdir
from discord import Message
from discord.ext.commands import Bot, MinimalHelpCommand
from utils.user import assert_user_exists

class GBot(Bot):
    def __init__(self, command_prefix, intents):
        self.locked_users = {}
        super(GBot, self).__init__(command_prefix=command_prefix, intents=intents, help_command=MinimalHelpCommand(no_category='Commands'))

    async def on_message(self, message: Message):
        if message.author.bot: return
        
        if (not await assert_user_exists(message.author)):
            return await message.channel.send("[Error] (Bot) Error during user validation")
        await super().on_message(message)

    async def load_cogs(self):
        for filename in listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename}')

    async def start(self, TOKEN):
        await self.load_cogs()
        await super().start(TOKEN)