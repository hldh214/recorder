import re
import random
import json
from typing import Optional, Dict, Any

import httpx

from recorder import logger
from recorder.ffmpeg import USER_AGENTS

REQUEST_TIMEOUT = 5
ROOM_ID_REGEX = re.compile(r'"room_id"\s*:\s*(\d+)')


def _http_get(url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None):
    try:
        res = httpx.get(
            url,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        return res
    except httpx.HTTPError as e:
        logger.debug(f'bilibili http error: {e} url={url} params={params}')
        return None


def resolve_room_id(room: str) -> Optional[int]:
    """
    Resolve a possibly non-numeric bilibili room identifier to a numeric room_id by parsing the room page.
    Accepts numeric ids, short ids, or custom slugs.
    """
    if isinstance(room, int) or (isinstance(room, str) and room.isdigit()):
        try:
            return int(room)
        except ValueError:
            pass

    headers = {
        'user-agent': random.choice(USER_AGENTS),
        'referer': 'https://live.bilibili.com/',
    }
    res = _http_get(f'https://live.bilibili.com/{room}', headers=headers)
    if not res or res.status_code >= 400:
        return None

    m = ROOM_ID_REGEX.search(res.text)
    if not m:
        return None

    try:
        return int(m.group(1))
    except (ValueError, IndexError):
        return None


def _pick_url_from_playinfo(data: dict) -> Dict[str, Optional[str]]:
    """
    Parse xlive getRoomPlayInfo v2 response and construct playable urls.
    Returns dict with possible 'flv_url' and/or 'hls_url'.
    """
    result = {'flv_url': None, 'hls_url': None}

    try:
        playurl = data['data']['playurl_info']['playurl']
    except (KeyError, TypeError):
        return result

    streams = playurl.get('stream') or []

    def build_urls(codec_entry):
        base_url = codec_entry.get('base_url') or ''
        _urls = []
        for ui in codec_entry.get('url_info') or []:
            host = ui.get('host') or ''
            extra = ui.get('extra') or ''
            if host and base_url:
                _urls.append(f'{host}{base_url}{extra}')
        return _urls

    for s in streams:
        for f in s.get('format') or []:
            format_name = f.get('format_name', '').lower()
            for c in f.get('codec') or []:
                urls = build_urls(c)
                if not urls:
                    continue
                # prefer first url
                if format_name == 'flv' and not result['flv_url']:
                    # ensure .flv
                    for u in urls:
                        if '.flv' in u:
                            result['flv_url'] = u
                            break
                    if not result['flv_url']:
                        result['flv_url'] = urls[0]
                if format_name in ('ts', 'm3u8', 'hls') and not result['hls_url']:
                    for u in urls:
                        if u.endswith('.m3u8') or 'm3u8' in u:
                            result['hls_url'] = u
                            break
                    if not result['hls_url']:
                        result['hls_url'] = urls[0]

    return result


def _fallback_playurl_api(room_id: int) -> Dict[str, Optional[str]]:
    """Fallback older API returning durl with direct URLs."""
    headers = {
        'user-agent': random.choice(USER_AGENTS),
        'referer': 'https://live.bilibili.com/',
    }
    res = _http_get(
        'https://api.live.bilibili.com/room/v1/Room/playUrl',
        params={
            'cid': room_id,
            'qn': 10000,
            'platform': 'h5',
            'https_url_req': 1,
            'ptype': 8,
        },
        headers=headers,
    )
    if not res:
        return {'flv_url': None, 'hls_url': None}

    try:
        j = res.json()
    except ValueError:
        return {'flv_url': None, 'hls_url': None}

    durl = (j.get('data') or {}).get('durl') or []
    if not durl:
        return {'flv_url': None, 'hls_url': None}

    url = durl[0].get('url')
    if not url:
        return {'flv_url': None, 'hls_url': None}

    if '.flv' in url:
        return {'flv_url': url, 'hls_url': None}
    if 'm3u8' in url:
        return {'flv_url': None, 'hls_url': url}
    return {'flv_url': url, 'hls_url': None}


def get_stream(room_id, **_):
    """
    Return a dict containing flv_url or hls_url if the room is live, otherwise False.
    """
    rid = resolve_room_id(str(room_id))
    if not rid:
        return False

    headers = {
        'user-agent': random.choice(USER_AGENTS),
        'referer': f'https://live.bilibili.com/{rid}',
    }

    # v2 play info
    res = _http_get(
        'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo',
        params={
            'room_id': rid,
            'protocol': '0,1',  # http_stream, http_hls
            'format': '0,1,2',  # flv, ts, fmp4
            'codec': '0,1',  # avc, hevc
            'qn': 10000,  # best quality
            'platform': 'web',
            'ptype': 8,
        },
        headers=headers,
    )

    play = {'flv_url': None, 'hls_url': None}
    live_status = None

    if res:
        try:
            j = res.json()
            live_status = (j.get('data') or {}).get('live_status')
            play = _pick_url_from_playinfo(j)
        except ValueError:
            logger.debug('bilibili getRoomPlayInfo returned non-JSON')

    if not play.get('flv_url') and not play.get('hls_url'):
        # fallback API
        fallback_play = _fallback_playurl_api(rid)
        play['flv_url'] = play['flv_url'] or fallback_play.get('flv_url')
        play['hls_url'] = play['hls_url'] or fallback_play.get('hls_url')

    if not play.get('flv_url') and not play.get('hls_url'):
        return False

    # Optionally include title via another API
    title = None
    try:
        info_res = _http_get(
            'https://api.live.bilibili.com/room/v1/Room/get_info',
            params={'room_id': rid},
            headers=headers,
        )
        if info_res:
            info_json = info_res.json()
            data = info_json.get('data') or {}
            title = data.get('title')
            if live_status is None:
                live_status = data.get('live_status')
    except Exception:
        pass

    if live_status is not None and int(live_status) != 1:
        # not live
        return False

    result = {}
    if play.get('flv_url'):
        result['flv_url'] = play['flv_url']
    if play.get('hls_url'):
        result['hls_url'] = play['hls_url']
    if title:
        result['title'] = title

    # Ensure the debug log is ASCII-safe for Windows consoles (e.g., cp932) by escaping non-ASCII
    try:
        safe_result = json.dumps(result, ensure_ascii=True)
    except Exception:
        safe_result = str(result)
    logger.debug(f'bilibili.get_stream[{room_id}->{rid}]: {safe_result}')
    return result


if __name__ == '__main__':
    import time

    while True:
        print(get_stream('5269'))  # replace with a real room id to test
        time.sleep(5)
