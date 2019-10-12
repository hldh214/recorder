import recorder.source.huya as huya


def test_is_live():
    assert huya.is_live('a_non_exist_room') is False


def test_parse_m3u8():
    assert huya.parse_m3u8('a_non_exist_room') is False
