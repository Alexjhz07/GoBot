from os import listdir
from discord import Message, User, Member
from discord.ext.commands import Bot, MinimalHelpCommand

from aiohttp import ClientSession
from json import dumps, loads
class RequestHandler():
    def __init__(self):
        self.routes = {
            'db': 'http://localhost:3815/api/v1',
            'experience': 'http://localhost:3816/api/v1',
            'banking': 'http://localhost:3817/api/v1',
            'wordle': 'http://localhost:3915',
        }

    async def post(self, service: str, route: str, payload: dict):
        try:
            async with ClientSession(headers={"Content-Type": "application/json"}) as session:
                async with session.post(f'{self.routes[service]}/{route}', data=dumps(payload)) as r:
                    content = loads((await r.read()).decode('utf8') or '{}')
                    content['return_code'] = r.status
                    if r.status == 200:
                        return content
                    else:
                        return None
        except Exception as e:
            print(f"[Error] (Request) {service} @ {route}: {e}", flush=True)
            return None
                
    async def assert_user_exists(self, user: Member):
        res = await self.post('db', 'query', {'queries': ['SELECT COUNT(1) FROM user_information WHERE user_id=$1'], 'arguments': [[user.id]]})
        if res == None: return False
        if (res['responses'][0][0]['count'] == '0'):
            user_created = await self.post('db', 'exec', {'queries': ['INSERT INTO user_information (user_id, username, nickname, avatar_url) VALUES ($1, $2, $3, $4)'], 'arguments': [[user.id, user.name, user.nick, str(user.avatar)]]})
            return user_created['return_code'] == 200
        else:
            return True
        
class GBot(Bot):
    def __init__(self, command_prefix, intents):
        self.locked_users = {}
        self.req = RequestHandler()
        super(GBot, self).__init__(command_prefix=command_prefix, intents=intents, help_command=MinimalHelpCommand(no_category='Commands'))

    async def on_message(self, message: Message):
        if message.author.bot: return
        
        if (not await self.req.assert_user_exists(message.author)):
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