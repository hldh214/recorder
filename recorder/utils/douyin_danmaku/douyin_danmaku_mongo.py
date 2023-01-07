import time

import arrow
import bson
import click
import pymongo

from recorder import config

MONGODB_DATABASE = 'recorder'
MONGODB_COLLECTION = 'douyin_danmaku'

mongo_client = pymongo.MongoClient(config['app'].get('mongo_dsn'))
mongo_collection = mongo_client[MONGODB_DATABASE][MONGODB_COLLECTION]

METHOD_DANMAKU = 'WebcastChatMessage'
CHAT_BY = '0'  # 弹幕类型，0-常规弹幕，9-功能性弹幕(福袋弹幕)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--room_ids', '-r', default=[], multiple=True, type=int)
def watch(room_ids):
    start_id = bson.objectid.ObjectId.from_datetime(arrow.now().datetime)

    while True:
        where_clause = {
            'method': METHOD_DANMAKU,
            'payload.chatBy': CHAT_BY,
            '_id': {'$gt': start_id}
        }

        if room_ids:
            where_clause.update({'payload.common.roomId': {'$in': room_ids}})

        cursor = mongo_collection.find(where_clause)

        while cursor.alive:
            for doc in cursor:
                start_id = doc.get('_id')

                generation_time = arrow.get(doc.get('_id').generation_time) \
                    .to('Asia/Hong_Kong') \
                    .format('YYYY-MM-DD HH:mm:ss')
                payload = doc.get('payload')
                room_id = payload.get('common').get('roomId')
                sender_nick = payload.get('user').get('nickname')
                content = payload.get('content')
                print(f'{generation_time}: {room_id}: {sender_nick}: {content}')

        time.sleep(1)


if __name__ == '__main__':
    cli()
