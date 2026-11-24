from recorder.utils.bililive_hls import Danmaku
from recorder.danmaku.bilibili.blivedm.blivedm import BaseHandler


def test_danmaku_only_dispatches_chat_and_heartbeat(monkeypatch):
    handled = []
    monkeypatch.setattr(BaseHandler, 'handle', lambda self, client, command: handled.append(command))
    handler = Danmaku(None)
    chat = {'cmd': 'DANMU_MSG:4:0:2:2:2:0'}
    heartbeat = {'cmd': '_HEARTBEAT'}
    handler.handle(None, chat)
    handler.handle(None, heartbeat)
    handler.handle(None, {'cmd': 'UNRECOGNIZED_EVENT', 'data': {'user': 'example'}})

    assert handled == [chat, heartbeat]
