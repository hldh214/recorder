from recorder.source.tars.core import tarscore
from recorder.source.utils import GetLivingInfoReq, WebSocketCommand, EWebSocketCommandType

import array
import websockets
import asyncio

get_living_info_req = GetLivingInfoReq()

get_living_info_req.lSubSid = 1678113423

tup = tarscore.TarsUniPacket()
tup.servant = 'liveui'
tup.func = 'getLivingInfo'
tup.requestid = -1
tup.put(GetLivingInfoReq, 'tReq', get_living_info_req)

ws_command = WebSocketCommand()
ws_command.iCmdType = EWebSocketCommandType.EWSCmd_WupReq
ws_command.vData = tup.encode()
output_stream = tarscore.TarsOutputStream()
ws_command.writeTo(output_stream)

py_res = [each for each in output_stream.getBuffer()]
js_res = [0, 3, 29, 0, 0, 109, 0, 0, 0, 109, 16, 3, 44, 60, 64, 255, 86, 6, 108, 105, 118, 101, 117, 105, 102, 13, 103,
          101, 116, 76, 105, 118, 105, 110, 103, 73, 110, 102, 111, 125, 0, 0, 67, 8, 0, 1, 6, 4, 116, 82, 101, 113, 29,
          0, 0, 54, 10, 10, 12, 22, 0, 38, 0, 54, 26, 119, 101, 98, 104, 53, 38, 50, 48, 48, 50, 50, 57, 49, 53, 49, 53,
          38, 119, 101, 98, 115, 111, 99, 107, 101, 116, 70, 0, 92, 102, 0, 11, 28, 34, 100, 5, 250, 143, 60, 70, 0, 86,
          0, 108, 11, 140, 152, 12, 168, 12, 35, 0, 0, 0, 0, 0, 0, 0, 0, 54, 9, 117, 110, 100, 101, 102, 105, 110, 101,
          100]

print(py_res)
print(js_res)
print(array.array('B', py_res).tobytes())
print(array.array('B', js_res).tobytes())


async def main():
    async with websockets.connect('wss://wsapi.huya.com') as websocket:
        await websocket.send(array.array('B', py_res).tobytes())
        res = await websocket.recv()
        print(res)
        ios = tarscore.TarsInputStream(res)
        ws_command = WebSocketCommand()
        ws_command.readFrom(ios)

        tup = tarscore.TarsUniPacket()
        print(ws_command.vData)


asyncio.run(main())
