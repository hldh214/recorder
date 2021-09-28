import asyncio
import json
import traceback
import urllib.parse

import arrow
import bson
import jwt
import pymongo
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

mongo_collection = pymongo.MongoClient()['recorder']['huya_danmaku']


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
            traceback.print_exc()
            continue


async def consumer_handler(websocket):
    async for message in websocket:
        print(message)
        mongo_collection.insert_one(json.loads(message))


def find_by_time_range(room_id, start, end, notice='getMessageNotice'):
    dummy_start_id = bson.objectid.ObjectId.from_datetime(start)
    dummy_end_id = bson.objectid.ObjectId.from_datetime(end)

    return mongo_collection.find({
        'notice': notice,
        'data.roomId': int(room_id),
        '_id': {
            '$gt': dummy_start_id,
            '$lt': dummy_end_id,
        }
    })


class Caption:
    def __init__(self, iterator, output_path):
        self.iterator = iterator
        self.output_path = output_path

    def to_sbv(self):
        pass

    def to_srt(self):
        pass


def main(room_id, app_id, app_secret):
    # print(list(find_by_time_range(room_id, arrow.now().shift(minutes=-10), arrow.now())))
    asyncio.run(subscribe(room_id, app_id, app_secret))


if __name__ == '__main__':
    import sys
    import toml

    my_room_id = '11342412'
    if len(sys.argv) > 1:
        my_room_id = sys.argv[1]

    config = toml.load('../../config.toml')
    main(my_room_id, config['huya']['app_id'], config['huya']['app_secret'])
