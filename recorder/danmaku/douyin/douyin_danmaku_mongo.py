import logging
import pathlib
import time

import arrow
import bson
import click
import pymongo

import recorder
from recorder import config
from recorder.danmaku import parse_datetime, get_info_from_path, Caption
from recorder.destination.youtube import Youtube
from recorder.source.douyin import get_room_info

MONGODB_DATABASE = 'recorder'
MONGODB_COLLECTION = 'douyin_danmaku'

mongo_client = pymongo.MongoClient(config['app'].get('mongo_dsn'))
mongo_collection = mongo_client[MONGODB_DATABASE][MONGODB_COLLECTION]

METHOD_DANMAKU = 'WebcastChatMessage'
CHAT_BY = '0'  # 弹幕类型，0-常规弹幕，9-功能性弹幕(福袋弹幕)


def get_room_id_str(room_id):
    return get_room_info(room_id)['id_str']


def find_danmaku(room_id, start=None, end=None):
    where_clause = {
        'payload.common.roomId': get_room_id_str(room_id),
        'method': METHOD_DANMAKU,  # maybe we can remove it? since we have `chatBy` filter already
        'payload.chatBy': CHAT_BY,
        '_id': {}
    }

    if start:
        where_clause['_id']['$gt'] = bson.objectid.ObjectId.from_datetime(parse_datetime(start).datetime)
    if end:
        where_clause['_id']['$lt'] = bson.objectid.ObjectId.from_datetime(parse_datetime(end).datetime)

    if not where_clause['_id']:
        del where_clause['_id']

    if not mongo_collection.count_documents(where_clause):
        logging.critical(f'Mongo_collection empty, room_id: {room_id}, start: {start}, end: {end}')
        return False

    return mongo_collection.find(where_clause)


def prepare_iterator_for_caption(danmaku):
    return (
        {
            'generation_time': each['_id'].generation_time,
            'content': each['payload']['content'],
        }
        for each in danmaku
    )


def gen_caption_and_return_highlights(room_id, start, end, caption_output_path):
    danmaku = find_danmaku(room_id, start, end)

    if not danmaku:
        return False

    highlights = recorder.danmaku.generate_highlights(danmaku, start)

    danmaku.rewind()

    caption = Caption(prepare_iterator_for_caption(danmaku), parse_datetime(start))
    caption.to_vtt(caption_output_path)

    return highlights


def add_caption_and_highlights_for_video(caption_path, highlights, video_id, source_config, start):
    youtube = Youtube(config.get('youtube'))

    description = source_config.get('description', '') + '\n\n' + highlights
    title = source_config['title'].format(datetime=start)

    return youtube.add_caption(video_id, caption_path), youtube.update(video_id, title, description)


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


@cli.command()
@click.option('--room_id', '-r', type=int)
@click.option('--start', '-s', type=click.DateTime())
@click.option('--end', '-e', type=click.DateTime())
@click.option('--path', '-p', type=click.Path(exists=True))
@click.option('--video_id', '-v', type=str)
def generate_with_highlight(room_id, start, end, path, video_id):
    if not (path and video_id) and not (room_id and start and end):
        click.echo(click.get_current_context().get_help())
        return

    caption_path = f'./{room_id}.vtt'
    source_config = None
    if path and video_id:
        source_config, start, end = get_info_from_path(path)
        room_id = source_config['room_id']
        caption_path = f'{pathlib.Path(path).parent}/{video_id}_{start}_{end}.vtt'

    highlights = gen_caption_and_return_highlights(room_id, start, end, caption_path)

    if path and video_id:
        assert source_config is not None

        print(add_caption_and_highlights_for_video(caption_path, highlights, video_id, source_config, start))
    else:
        print(highlights)


if __name__ == '__main__':
    cli()