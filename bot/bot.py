from os import listdir, getenv
from discord import Message
from discord.ext.commands import Bot, DefaultHelpCommand, Context
from discord.ext.commands.errors import CommandError, CommandNotFound, CommandOnCooldown, MissingRequiredArgument, CommandInvokeError
from lib.exceptions import PostException
from utils.user import assert_user_exists

class GBot(Bot):
    def __init__(self, command_prefix, intents):
        super(GBot, self).__init__(command_prefix=command_prefix, intents=intents, help_command=DefaultHelpCommand())

    async def on_message(self, message: Message):
        if message.author.bot: return
        
        try:
            await assert_user_exists(message.author)
            await super().on_message(message)
        except PostException as e:
            print(f'Server-side Exception: {e}')
        except Exception as e:
            print(f'Exception: {e}')

    async def load_cogs(self):
        for filename in listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename}')
     
    async def on_command_error(self, ctx: Context, exception: Exception):
        if isinstance(exception, CommandNotFound):
            await ctx.reply(f'Unknown Command: {exception}')
        elif isinstance(exception, CommandOnCooldown):
            await ctx.reply(f'Command Cooldown: {exception}')
        elif isinstance(exception, MissingRequiredArgument):
            await ctx.reply(f'Missing Arguments: {exception}')
        elif isinstance(exception, CommandInvokeError):
            await ctx.reply(f'{exception.original}')
        elif isinstance(exception, PostException):
            print(f'Server-side Exception: {exception}')
        else:
            print(f'Exception: {exception}')

    async def start(self, TOKEN):
        await self.load_cogs()
        await super().start(TOKEN)