import requests


def get_stream(room_id, **kwargs):
    try:
        res = requests.post('https://api.pandalive.co.kr/v1/live/play', data={
            'action': 'watch',
            'userId': room_id,
        }, cookies={
            'sessKey': kwargs['sess_key'],
        }).json()
    except requests.exceptions.RequestException:
        return False

    if 'PlayList' not in res:
        return False

    return res['PlayList']['hls'][0]['url']


if __name__ == '__main__':
    import time

    while True:
        print(get_stream('10535725', sess_key='018c6d30a09720dd7aba6a9113fa5227bc9c78e033eb1a2be5fec88af599e3c6'))
        time.sleep(5)
