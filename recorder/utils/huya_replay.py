import os
import pathlib

import arrow
import click
import pandas as pd
import grequests

import recorder.source.huya
import recorder.ffmpeg
from recorder import TZ_INFO


@click.group()
def cli():
    pass


def get_replay_by_time_range(base_url, start, end):
    start_rage = pd.date_range(
        start=start[0], end=start[1], freq='1S'
    ).map(lambda each: each.strftime('%Y-%m-%d-%H:%M:%S')).tolist()
    end_rage = pd.date_range(
        start=end[0], end=end[1], freq='1S'
    ).map(lambda each: each.strftime('%Y-%m-%d-%H:%M:%S')).tolist()

    for each_end in end_rage:
        rs = (grequests.get(f'{base_url}{each_start}_{each_end}.m3u8') for each_start in start_rage)
        res = grequests.map(rs)
        for each_res in res:
            if each_res and each_res.status_code != 404:
                return each_res.url


@cli.command()
@click.option('--video_id', '-v', type=int, required=True)
def download_replay(video_id):
    video_url = recorder.source.huya.get_replay(video_id)
    video_url_parsed = pathlib.Path(video_url)
    start_time = ' '.join(video_url_parsed.stem.split('_')[0].rsplit('-', 1))
    end_time = ' '.join(video_url_parsed.stem.split('_')[1].rsplit('-', 1))
    end_time_timestamp = arrow.get(end_time).replace(tzinfo=TZ_INFO).int_timestamp
    filename = f'{start_time}.mp4'

    recorder.ffmpeg.record(video_url, filename, 0, 0)

    os.utime(filename, (end_time_timestamp, end_time_timestamp))


if __name__ == '__main__':
    cli()
    # download_replay('677885387')
    # print(get_replay_by_time_range(
    #     'http://v-replay.cdn.huya.com/record/huyalive/3200269-3200269-13745050693402624-6523994-10057-A-0-1/',
    #     ['2020-07-29-00:33:00', '2020-07-29-00:33:59'],
    #     ['2020-07-29-01:44:00', '2020-07-29-01:50:59']
    # ))
