import asyncio
import csv
import json
import logging
import pathlib
import traceback
import urllib.parse
import re
import subprocess
import time

import arrow
import bson
import click
import jwt
import pymongo.errors
import tenacity
import websockets

import recorder.danmaku
from recorder import config
from recorder.danmaku import parse_datetime, get_info_from_path
from recorder.destination.youtube import Youtube
from recorder.danmaku.caption import Caption

WS_HOST = 'ws-apiext.huya.com'
NOTICE_MAP = {
    'getMessageNotice': '弹幕消息',
    'getVipEnterBannerNotice': '高级用户进场消息',
    'getSendItemNotice': '送礼消息',
    'getOnTVAwardNotice': '上电视中奖',
    'getOpenNobleNotice': '开通续费贵族',
    'getOpenGuardianNotice': '开通续费守护',
    'getUserMutedNotice': '房管禁言',
    'getShareLiveNotice': '分享直播间',
    'getExpressionEmoticonNotice': '大表情/发送梗相关通用消息',
}
NOTICE_DATA = list(NOTICE_MAP.keys())
DANMAKU_MSG_TYPE = 0  # 弹幕类型，0-常规弹幕，1-功能性弹幕(诸如部分投票/战队支持等相关弹幕)，2-上电视弹幕
DANMAKU_NOTICE = 'getMessageNotice'

# spam 弹幕正则过滤
CONTENT_FILTER_PATTERNS = (
    re.compile(r'^/{'),  # 过滤表情开头的弹幕(通常全是表情)
    re.compile(r'抢福袋，一元开超粉！'),  # 过滤抢福袋弹幕
)
# spam 账号 unionId 过滤
UNION_ID_FILTER_LIST = (
    'un8RvnUOwsr6J3xq8uAXTzmtxs00GClkrY',  # 668668 直播间的 [你猜]
)

MONGODB_DATABASE = 'recorder'
MONGODB_COLLECTION = 'huya_danmaku'

mongo_client = pymongo.MongoClient(config['app'].get('mongo_dsn'))
mongo_collection = mongo_client[MONGODB_DATABASE][MONGODB_COLLECTION]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def gather_sub(room_ids):
    return await asyncio.gather(*[
        subscribe(room_id, config['huya']['app_id'], config['huya']['app_secret'])
        for room_id in room_ids
    ])


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_random_exponential(multiplier=1, max=60),
    retry=tenacity.retry_if_exception_type((websockets.WebSocketException,)),
)
async def subscribe(room_id, app_id, app_secret):
    iat = arrow.now().int_timestamp
    exp = iat + 10 * 60

    params = urllib.parse.urlencode({
        'iat': iat,
        'exp': exp,
        'sToken': jwt.encode({'iat': iat, 'exp': exp, 'appId': app_id}, app_secret),
        'appId': app_id,
        'roomId': room_id,
        'do': 'comm',
    })

    subscribe_notice = json.dumps({'command': 'subscribeNotice', 'data': NOTICE_DATA, 'reqId': iat})

    # `ping_timeout=None` for not sending ping package and don't wait for pong response
    async for websocket in websockets.connect(f'wss://{WS_HOST}/index.html?{params}', ping_timeout=None):
        try:
            await websocket.send(subscribe_notice)
            await consumer_handler(websocket)
        except websockets.WebSocketException:
            logging.warning('WebSocketException excepted: ' + traceback.format_exc())
            raise


async def consumer_handler(websocket):
    async for message in websocket:
        logging.info(message)
        mongo_collection.insert_one(json.loads(message))


def find_danmaku(room_id, start=None, end=None):
    where_clause = {
        'notice': DANMAKU_NOTICE,
        'data.msgType': DANMAKU_MSG_TYPE,
        'data.roomId': int(room_id),
        'data.unionId': {
            '$nin': UNION_ID_FILTER_LIST
        },
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


def is_spam(content):
    for pattern in CONTENT_FILTER_PATTERNS:
        if pattern.match(content) is not None:
            return True

    return False


def prepare_iterator_for_caption(danmaku):
    return (
        {
            'generation_time': each['_id'].generation_time,
            'content': each['data']['content'],
        }
        for each in danmaku
        if not is_spam(each['data']['content'])
    )


def generate_highlights_from_video(path, video_id):
    source_config, start, end = get_info_from_path(path)
    highlights = generate_highlights(source_config['room_id'], start, end)

    if not highlights:
        logging.critical(f'Generate highlights failed, path: {path}, video_id: {video_id}')
        return False

    youtube = Youtube(config.get('youtube'))

    description = source_config.get('description', '') + '\n\n' + highlights
    title = source_config['title'].format(datetime=start)

    return youtube.update(video_id, title, description)


def generate(room_id, output_path, start, end):
    danmaku = find_danmaku(room_id, start, end)

    if not danmaku:
        return False

    caption = Caption(prepare_iterator_for_caption(danmaku), parse_datetime(start))
    caption.to_vtt(output_path)

    return True


def generate_from_video(path, video_id):
    source_config, start, end = get_info_from_path(path)
    output_path = f'{pathlib.Path(path).parent}/{video_id}_{start}_{end}.vtt'

    if not generate(source_config['room_id'], output_path, start, end):
        logging.critical(f'Generate failed, path: {path}, video_id: {video_id}')
        return False

    youtube = Youtube(config.get('youtube'))

    return youtube.add_caption(video_id, output_path)


def generate_highlights(room_id, start, end):
    danmaku = find_danmaku(room_id, start, end)

    if not danmaku:
        return False

    return recorder.danmaku.generate_highlights(danmaku, start)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--room_ids', '-r', default=[], multiple=True, type=int)
def sub(room_ids):
    if not room_ids:
        room_ids = [
            each['room_id'] for each in config['source'].values()
            if each.get('danmaku_enabled') is True and each.get('source_type') == 'huya'
        ]

    asyncio.run(gather_sub(room_ids))


@cli.command()
@click.option('--room_id', '-r', type=int)
@click.option('--start', '-s', type=click.DateTime())
@click.option('--end', '-e', type=click.DateTime())
@click.option('--path', '-p', type=click.Path(exists=True))
@click.option('--video_id', '-v', type=str)
def gen(room_id, start, end, path, video_id):
    if room_id and start and end:
        return generate(room_id, f'./{room_id}.vtt', start, end)

    if path and video_id:
        return generate_from_video(path, video_id)

    click.echo(click.get_current_context().get_help())


@cli.command()
@click.option('--room_ids', '-r', default=[], multiple=True, type=int)
def watch(room_ids):
    start_id = bson.objectid.ObjectId.from_datetime(arrow.now().datetime)

    while True:
        where_clause = {
            'notice': DANMAKU_NOTICE,
            'data.msgType': DANMAKU_MSG_TYPE,
            '_id': {'$gt': start_id}
        }

        if room_ids:
            where_clause.update({'data.roomId': {'$in': room_ids}})

        cursor = mongo_collection.find(where_clause)

        while cursor.alive:
            for doc in cursor:
                start_id = doc.get('_id')

                generation_time = arrow.get(doc.get('_id').generation_time) \
                    .to('Asia/Hong_Kong') \
                    .format('YYYY-MM-DD HH:mm:ss')
                data = doc.get('data')
                room_id = data.get('roomId')
                sender_nick = data.get('sendNick')
                sender_level = data.get('senderLevel')
                badge_name = data.get('badgeName')
                content = data.get('content')
                print(f'{generation_time}: {room_id}: [({sender_level}){badge_name}]{sender_nick}: {content}')

        time.sleep(1)


@cli.command()
@click.option('--start', '-s', type=click.DateTime(), required=True)
@click.option('--end', '-e', type=click.DateTime(), required=True)
def backup(start, end):
    start = parse_datetime(start)
    end = parse_datetime(end)

    dummy_start_id = bson.objectid.ObjectId.from_datetime(start.datetime)
    dummy_end_id = bson.objectid.ObjectId.from_datetime(end.datetime)

    query = json.dumps({'_id': {'$gte': {'$oid': str(dummy_start_id)}, '$lt': {'$oid': str(dummy_end_id)}}})

    cmd = [
        'mongodump', '-d', MONGODB_DATABASE, '-c', MONGODB_COLLECTION, '-q', query, '--gzip',
        '-o', f'./mongodump_{start.format("YYYYMMDDHHmmss")}_{end.format("YYYYMMDDHHmmss")}'
    ]

    dump_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with dump_process.stdout as stdout:
        for line in stdout:
            print(line.decode().strip())

    return dump_process.wait()


@cli.command()
@click.option('--room_id', '-r', type=int, required=True)
@click.option('--path', '-p', type=click.Path(), required=True)
def generate_csv_for_analyze(room_id, path):
    danmaku = find_danmaku(room_id)

    with open(path, 'w', encoding='utf8') as fp:
        writer = csv.writer(fp)
        writer.writerow(['_id', 'ts', 'sendNick', 'badgeName', 'fansLevel', 'content'])

        for each in danmaku:
            ts = int(arrow.get(each['_id'].generation_time).timestamp())
            writer.writerow([
                each['_id'], ts, each['data']['sendNick'], each['data']['badgeName'], each['data']['fansLevel'],
                each['data']['content']
            ])


@cli.command()
@click.option('--room_id', '-r', type=int, required=True)
@click.option('--start', '-s', type=click.DateTime(), required=True)
@click.option('--end', '-e', type=click.DateTime(), required=True)
def generate_highlights_command(room_id, start, end):
    print(generate_highlights(room_id, start, end))


@cli.command()
@click.option('--room_id', '-r', type=int)
@click.option('--start', '-s', type=click.DateTime())
@click.option('--end', '-e', type=click.DateTime())
@click.option('--path', '-p', type=click.Path(exists=True))
@click.option('--video_id', '-v', type=str)
def generate_with_highlight(room_id, start, end, path, video_id):
    if room_id and start and end:
        print(generate(room_id, f'./{room_id}.vtt', start, end))
        print(generate_highlights(room_id, start, end))
        return

    if path and video_id:
        print(generate_from_video(path, video_id))
        print(generate_highlights_from_video(path, video_id))
        return

    click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
    cli()
