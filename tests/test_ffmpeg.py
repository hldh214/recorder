import os

import recorder.ffmpeg as ffmpeg

SAMPLE_M3U8_URL = 'http://aldirect.flv.huya.com/backsrc/' \
                  '29106097-2689279974-11550369538117730304-2777027112-10057-A-0-1.flv'
OUTPUT_FILE = './test_video.flv'
VIDEO_DURATION = 5


def test_record():
    # generate 5 seconds video for testing
    ffmpeg.record(SAMPLE_M3U8_URL, OUTPUT_FILE, VIDEO_DURATION, ['-y'])

    assert os.path.exists(OUTPUT_FILE)


def test_duration():
    assert ffmpeg.duration(OUTPUT_FILE) == VIDEO_DURATION


def test_valid():
    assert ffmpeg.valid(OUTPUT_FILE)
    os.unlink(OUTPUT_FILE)
