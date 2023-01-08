import asyncio
import websockets


async def hello():
    async for message in websockets.connect(''):
        print(message)


asyncio.run(hello())
