import asyncio
import json
import time
import urllib.parse
import jwt
import websockets

app_id = ''
app_secret = ''
host = 'ws-apiext.huya.com'
iat = int(time.time())
exp = iat + 10 * 60
message_notice = 'getMessageNotice'
notice_data = [message_notice]
subscribe_notice = json.dumps({'command': 'subscribeNotice', 'data': notice_data, 'reqId': iat})


async def subscribe(room_id):
    params = urllib.parse.urlencode({
        'iat': iat,
        'exp': exp,
        'sToken': jwt.encode({'iat': iat, 'exp': exp, 'appId': app_id}, app_secret),
        'appId': app_id,
        'roomId': room_id,
        'do': 'comm',
    })

    # If the corresponding Pong frame isn’t received within ping_timeout seconds,
    # the connection is considered unusable and is closed with code 1011.
    # This ensures that the remote endpoint remains responsive.
    # Set ping_timeout to None to disable this behavior.
    # https://websockets.readthedocs.io/en/stable/api.html#websockets.protocol.WebSocketCommonProtocol
    async with websockets.connect('wss://{}/index.html?{}'.format(host, params), ping_timeout=None) as websocket:
        await websocket.send(subscribe_notice)
        await consumer_handler(websocket)


async def consumer_handler(websocket):
    async for message in websocket:
        try:
            message = json.loads(message)
            notice = message['notice']
        except (ValueError, KeyError):
            continue

        if notice != message_notice:
            print(message)
            continue

        print(message['data']['content'])


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(subscribe('11342412'))
