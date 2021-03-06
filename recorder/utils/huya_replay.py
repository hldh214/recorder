import pandas as pd
import grequests


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


print(get_replay_by_time_range(
    'http://v-replay.cdn.huya.com/record/huyalive/3200269-3200269-13745050693402624-6523994-10057-A-0-1/',
    ['2020-07-29-00:33:00', '2020-07-29-00:33:59'],
    ['2020-07-29-01:44:00', '2020-07-29-01:50:59']
))
