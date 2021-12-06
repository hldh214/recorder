import asyncio
import json
import logging
import traceback
import urllib.parse
import os
import pathlib
import re
import subprocess
import time

import arrow
import bson
import cachetools
import click
import jwt
import pymongo.errors
import toml
import websockets

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

CAPTION_MINIMAL_INTERVAL = 0.1  # 两条字幕之间间隔不小于 0.1 秒, 为了字幕播放性能
CONTENT_TTL = 4  # 弹幕展示时间 (秒)
CONTENT_MAXSIZE = 6  # 最多一次显示多少条弹幕
DANMAKU_DELAY = 2  # 时间轴快进 (秒) for 直播延迟

# spam 弹幕正则过滤
CONTENT_FILTER_PATTERNS = (
    re.compile(r'^/{'),  # 过滤表情开头的弹幕(通常全是表情)
)
# spam 账号 unionId 过滤
UNION_ID_FILTER_LIST = (
    'un8RvnUOwsr6J3xq8uAXTzmtxs00GClkrY',  # 668668 直播间的 [你猜]
)

VTT_TIME_FORMAT = 'HH:mm:ss.SSS'
VTT_HEADERS = '''\
WEBVTT
Kind: captions
Language: zh-Hans

'''

TZ_INFO = 'Asia/Shanghai'
MONGODB_DATABASE = 'recorder'
MONGODB_COLLECTION = 'huya_danmaku'

mongo_client = pymongo.MongoClient()
mongo_collection = mongo_client[MONGODB_DATABASE][MONGODB_COLLECTION]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def gather_sub(room_ids, config):
    return await asyncio.gather(*[
        subscribe(room_id, config['huya']['app_id'], config['huya']['app_secret'])
        for room_id in room_ids
    ])


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
            continue


async def consumer_handler(websocket):
    async for message in websocket:
        logging.info(message)
        mongo_collection.insert_one(json.loads(message))


def find_danmaku_by_time_range(room_id, start, end):
    dummy_start_id = bson.objectid.ObjectId.from_datetime(start)
    dummy_end_id = bson.objectid.ObjectId.from_datetime(end)

    where_clause = {
        'notice': DANMAKU_NOTICE,
        'data.msgType': DANMAKU_MSG_TYPE,
        'data.roomId': int(room_id),
        'data.unionId': {
            '$nin': UNION_ID_FILTER_LIST
        },
        '_id': {
            '$gt': dummy_start_id,
            '$lt': dummy_end_id,
        }
    }

    if not mongo_collection.count_documents(where_clause):
        logging.critical(f'Mongo_collection empty, room_id: {room_id}, start: {start}, end: {end}')
        return False

    return mongo_collection.find(where_clause)


def is_spam(content):
    for pattern in CONTENT_FILTER_PATTERNS:
        if pattern.match(content) is not None:
            return True

    return False


class Timer:
    """
    custom timer for `TTLCache`
    """

    def __init__(self, ts):
        self.ts = ts

    def timer(self):
        return self.ts


class Caption:
    def __init__(self, iterator, started_at):
        self.iterator = iterator
        self.started_at = started_at

    def to_vtt(self, output_path):
        last_modified_at = self.started_at
        timer = Timer(self.started_at.timestamp())
        ttl_cache = cachetools.TTLCache(maxsize=CONTENT_MAXSIZE, ttl=CONTENT_TTL, timer=timer.timer)
        last_context = {'start': None, 'end': None, 'contents': []}

        with open(output_path, 'w', encoding='utf8') as fp:
            fp.write(VTT_HEADERS)

            for each in self.iterator:
                content = each['data']['content']

                if is_spam(content):
                    continue

                current_time = arrow.get(each['_id'].generation_time)
                start_seconds = current_time.timestamp() - self.started_at.timestamp()
                start = arrow.get(start_seconds)

                timer.ts = current_time.timestamp()
                cache_key = f'{start.format(VTT_TIME_FORMAT)}\n{content}'
                ttl_cache[cache_key] = content
                content_list = list(ttl_cache.values())  # 获取当前字幕需要展示的所有弹幕

                if not last_context['contents']:
                    # 第一次循环
                    last_context['start'] = start
                    last_context['contents'] = content_list
                    continue

                caption_interval = current_time - last_modified_at
                if caption_interval.seconds < CAPTION_MINIMAL_INTERVAL:
                    # 控制两条字幕之间间隔时间
                    last_context['contents'] = content_list
                    continue

                last_start = last_context['start']
                last_end = start

                line = f'{last_start.format(VTT_TIME_FORMAT)} --> {last_end.format(VTT_TIME_FORMAT)}\n'

                for each_content in last_context['contents']:
                    line += f'{each_content}\n'

                line += '\n'
                fp.write(line)

                last_context['start'] = start
                last_context['contents'] = content_list
                last_modified_at = current_time


def generate(room_id, output_path, start, end):
    start = arrow.get(start).replace(tzinfo=TZ_INFO).shift(seconds=DANMAKU_DELAY)
    end = arrow.get(end).replace(tzinfo=TZ_INFO).shift(seconds=DANMAKU_DELAY)

    danmaku = find_danmaku_by_time_range(
        room_id, arrow.get(start), arrow.get(end)
    )

    if not danmaku:
        return False

    caption = Caption(danmaku, arrow.get(start))
    caption.to_vtt(output_path)

    return True


@click.group()
def cli():
    pass


@cli.command()
@click.option('--room_ids', '-r', default=[], multiple=True, type=int)
def sub(room_ids):
    config = toml.load(os.path.join(
        pathlib.Path(os.path.abspath(__file__)).parent.parent.parent, 'config.toml'
    ))

    if not room_ids:
        room_ids = [each['room_id'] for each in config['source'].values() if each['enabled']]

    asyncio.run(gather_sub(room_ids, config))


@cli.command()
@click.option('--room_id', '-r', required=True, type=int)
@click.option('--start', '-s', type=click.DateTime(), required=True)
@click.option('--end', '-e', type=click.DateTime(), required=True)
def gen(room_id, start, end):
    generate(room_id, f'./{room_id}.vtt', start, end)


@cli.command()
@click.option('--room_ids', '-r', default=[], multiple=True, type=int)
def watch(room_ids):
    start_id = bson.objectid.ObjectId.from_datetime(arrow.now())

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
    start = arrow.get(start).replace(tzinfo=TZ_INFO)
    end = arrow.get(end).replace(tzinfo=TZ_INFO)

    dummy_start_id = bson.objectid.ObjectId.from_datetime(arrow.get(start))
    dummy_end_id = bson.objectid.ObjectId.from_datetime(arrow.get(end))

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


if __name__ == '__main__':
    cli()
