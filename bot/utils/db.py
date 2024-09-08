from lib.exceptions import PostException
from aiohttp import ClientSession
from json import dumps, loads

ROUTES = {
    'db': 'http://localhost:3815/api/v1',
    'experience': 'http://localhost:3816/api/v1',
    'banking': 'http://localhost:3817/api/v1',
    'wordle': 'http://localhost:3915',
}

async def post(service: str, route: str, payload: dict):
    try:
        async with ClientSession(headers={"Content-Type": "application/json"}) as session:
            async with session.post(f'{ROUTES[service]}/{route}', data=dumps(payload)) as r:
                content = loads((await r.read()).decode('utf8') or '{}')
                if r.status == 200:
                    return content
                else:
                    raise PostException(f'{service} @ {route}: Return code {r.status}')
    except Exception as e:
        raise PostException(f'{service} @ {route}: {e}')