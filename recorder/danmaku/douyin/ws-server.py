import asyncio
import json
import logging

import websockets

from recorder import mongo_collection_douyin_danmaku as mongo_collection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def consumer_handler(websocket):
    async for message in websocket:
        msg_decoded = json.loads(message)
        mongo_collection.insert_one(msg_decoded)
        if msg_decoded['method'] == 'WebcastChatMessage':
            logging.info(msg_decoded['payload']['content'])


async def main():
    async with websockets.serve(consumer_handler, "localhost", 18964):
        await asyncio.Future()  # run forever


asyncio.run(main())
