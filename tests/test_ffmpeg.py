import os

import recorder.ffmpeg as ffmpeg

SAMPLE_M3U8_URL = 'https://aldirect.hls.huya.com/backsrc/' \
                  '94525224-2460685313-10568562945082523648-2789274524-10057-A-0-1.m3u8'
OUTPUT_FILE = './test_video.mp4'
VIDEO_DURATION = 5


def test_record():
    # generate 5 seconds video for testing
    ffmpeg.record(SAMPLE_M3U8_URL, OUTPUT_FILE, ['-y', '-t', str(VIDEO_DURATION)])

    assert os.path.exists(OUTPUT_FILE)


def test_duration():
    assert ffmpeg.duration(OUTPUT_FILE) == VIDEO_DURATION


def test_valid():
    assert ffmpeg.valid(OUTPUT_FILE)
    os.unlink(OUTPUT_FILE)
