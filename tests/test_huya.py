import recorder.source.huya as huya


def test_get_stream():
    assert huya.get_stream('a_non_exist_room') is False
