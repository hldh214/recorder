import recorder.source.bilibili as bilibili


def test_get_stream():
    assert bilibili.get_stream('a_non_exist_room') is False
