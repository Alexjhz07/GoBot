import os
from discord import Message
from discord.ext.commands import Bot, MinimalHelpCommand

import aiohttp
import json

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
            async with aiohttp.ClientSession(headers={"Content-Type": "application/json"}) as session:
                async with session.post(f'{self.routes[service]}/{route}', data=json.dumps(payload)) as r:
                    if r.status == 200:
                        return json.loads((await r.read()).decode('utf8'))
                    else:
                        print(json.loads((await r.read()).decode('utf8')))
                        return None
        except Exception as e:
            print(f"[Error] (Request) {service} @ {route}: {e}", flush=True)
                
    async def verify_user(self, user_id: int):
        res = await self.post('db', 'query', {'queries': ['SELECT COUNT(1) FROM user_information WHERE user_id=$1'], 'arguments': [[user_id]]})
        if res == None: return None
        return res['responses'][0][0]['count'] == '1'
        

class GBot(Bot):
    def __init__(self, command_prefix, intents):
        self.locked_users = {}
        self.req = RequestHandler()
        super(GBot, self).__init__(command_prefix=command_prefix, intents=intents, help_command=MinimalHelpCommand(no_category='Commands'))

    async def on_message(self, message: Message):
        await self.confirm_user(message.author.id)
        await super().on_message(message)

    async def confirm_user(self, user_id: int):
        ...

    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename}')

    async def start(self, TOKEN):
        await self.load_cogs()
        await super().start(TOKEN)