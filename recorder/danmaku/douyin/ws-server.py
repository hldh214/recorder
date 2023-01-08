import asyncio
import json
import logging

import pymongo
import websockets

from recorder import config

MONGODB_DATABASE = 'recorder'
MONGODB_COLLECTION = 'douyin_danmaku'

mongo_client = pymongo.MongoClient(config['app'].get('mongo_dsn'))
mongo_collection = mongo_client[MONGODB_DATABASE][MONGODB_COLLECTION]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def consumer_handler(websocket):
    async for message in websocket:
        logging.info(message)
        msg_decoded = json.loads(message)
        mongo_collection.insert_one(msg_decoded)
        # if msg_decoded['method'] == 'WebcastChatMessage':
        #     print(msg_decoded['payload']['content'])


async def main():
    async with websockets.serve(consumer_handler, "localhost", 18964):
        await asyncio.Future()  # run forever


asyncio.run(main())
