import recorder.source.panda as panda


def test_get_stream():
    assert panda.get_stream('a_non_exist_room') is False
