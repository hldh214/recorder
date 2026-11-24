"""Record original-quality Bilibili HLS when the FLV recorder stalls."""

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import signal
import sqlite3
import time
from contextlib import closing
from http.cookies import SimpleCookie
from pathlib import Path
from xml.etree import ElementTree

import aiohttp

from recorder.bililive.journal import ProcessLock
from recorder.bililive.media import inspect_media
from recorder.danmaku.bilibili.blivedm.blivedm import BaseHandler, BLiveClient


LOG = logging.getLogger(__name__)
API = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
POLL = 5
STALL = 45
MIN_FREE = 5 * 1024 ** 3
CHAT_RETENTION = 7 * 86400
INVALID_XML = re.compile(r'[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]')


class Danmaku(BaseHandler):
    def __init__(self, db):
        self.db = db
        self.last_heartbeat = None

    def handle(self, client, command):
        # The upstream handler logs entire payloads for unrecognized events.
        if command.get('cmd', '').partition(':')[0] in ('DANMU_MSG', '_HEARTBEAT'):
            super().handle(client, command)

    def _on_heartbeat(self, client, message):
        self.last_heartbeat = time.monotonic()

    def _on_danmaku(self, client, message):
        if message.dm_type == 0 and message.msg_type == 0:
            timestamp = message.timestamp / 1000
            if abs(timestamp - time.time()) < 300:
                with self.db:
                    self.db.execute('INSERT INTO chat VALUES (?, ?)', (timestamp, message.msg))


async def finalize(source, target_dir, db):
    media = await asyncio.to_thread(inspect_media, source)
    if not (media.has_video and media.has_audio and media.duration and not media.probe_error):
        raise ValueError('recording failed media probe')
    start = media.start_time.timestamp()
    target = target_dir / source.name
    sidecar = target.with_suffix('.xml')
    staged_xml = source.with_suffix('.xml')
    if not staged_xml.exists():
        xml = ElementTree.Element('i')
        for timestamp, message in db.execute(
            'SELECT timestamp, message FROM chat WHERE timestamp >= ? AND timestamp < ? ORDER BY timestamp',
            (start, start + media.duration),
        ):
            ElementTree.SubElement(xml, 'd', p=f'{timestamp - start:.3f}').text = INVALID_XML.sub('', message)
        partial = staged_xml.with_suffix('.xml.partial')
        ElementTree.ElementTree(xml).write(partial, encoding='utf-8', xml_declaration=True)
        partial.replace(staged_xml)
    # Expose the XML first and use hard links to avoid overwriting a recording
    # on a name collision. A reboot between the links can resume safely.
    if not sidecar.exists():
        os.link(staged_xml, sidecar)
    elif not os.path.samefile(sidecar, staged_xml):
        raise FileExistsError(sidecar)
    if not target.exists():
        os.link(source, target)
    elif not os.path.samefile(source, target):
        raise FileExistsError(target)
    source.unlink()
    staged_xml.unlink()
    LOG.info('Handed off %s and its danmaku XML', target.name)


async def handoff(path, destination, db):
    try:
        await finalize(path, destination, db)
    except (OSError, ValueError, RuntimeError) as error:
        LOG.error('Retained %s for recovery (%s)', path.name, type(error).__name__)


async def capture(url, stage, destination, db, referer, title, segment_seconds, stop):
    run_id = time.time_ns()
    pattern = f'*-hls-{run_id}.flv'
    output = stage / f'%Y-%m-%d %H:%M:%S-hls-{run_id}.flv'
    process = await asyncio.create_subprocess_exec(
        'nice', '-n', '10', 'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error',
        '-rw_timeout', '10000000', '-user_agent', 'Mozilla/5.0',
        '-headers', f'Referer: {referer}\r\n', '-live_start_index', '-1',
        '-i', url, '-map', '0:v:0', '-map', '0:a:0', '-c', 'copy',
        '-metadata', f'title={title}', '-flush_packets', '1',
        '-f', 'segment', '-segment_format', 'flv', '-segment_time', str(segment_seconds),
        '-reset_timestamps', '1', '-strftime', '1', '-n', str(output),
        env={**os.environ, 'TZ': 'Asia/Shanghai'},
        stderr=asyncio.subprocess.DEVNULL,
    )
    last_write = None
    last_growth = time.monotonic()
    try:
        while process.returncode is None:
            if stop.is_set() or shutil.disk_usage(stage).free < MIN_FREE:
                LOG.warning('Closing HLS capture on shutdown or low disk space')
                break
            files = sorted(stage.glob(pattern))
            if files:
                current = files[-1]
                marker = (current.name, current.stat().st_size)
                if marker != last_write:
                    last_write, last_growth = marker, time.monotonic()
                for closed in files[:-1]:
                    await handoff(closed, destination, db)
            if time.monotonic() - last_growth >= STALL:
                LOG.error('HLS stopped writing')
                break
            try:
                await asyncio.wait_for(process.wait(), POLL)
            except asyncio.TimeoutError:
                pass
    finally:
        if process.returncode is None:
            try:
                process.send_signal(signal.SIGINT)
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(process.wait(), 10)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
    for closed in sorted(stage.glob(pattern)):
        await handoff(closed, destination, db)
    return process.returncode


async def get_json(session, url, **kwargs):
    async with session.get(url, **kwargs) as response:
        response.raise_for_status()
        return await response.json()


async def play_info(session, room, referer):
    result = await get_json(session, API, headers={'Referer': referer}, params={
        'room_id': room, 'protocol': '0,1', 'format': '0,1,2', 'codec': '0,1',
        'qn': 10000, 'platform': 'web', 'ptype': 8,
    })
    if result['code'] != 0:
        raise ValueError(f'Bilibili play API code {result["code"]}')
    return result['data']


def original_urls(data):
    play = (data.get('playurl_info') or {}).get('playurl') or {}
    return [
        endpoint['host'] + codec['base_url'] + endpoint['extra']
        for stream in play.get('stream', []) if stream['protocol_name'] == 'http_hls'
        for fmt in stream['format'] if fmt['format_name'] == 'fmp4'
        for codec in fmt['codec'] if codec['codec_name'] == 'avc' and codec['current_qn'] == 10000
        for endpoint in codec['url_info']
    ]


async def run(args, stage, destination, db):
    stop = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_running_loop().add_signal_handler(sig, stop.set)
    cookie = SimpleCookie()
    config = json.loads((args.root / 'config.json').read_text())
    cookie.load(config['global']['Cookie']['Value'])
    jar = aiohttp.CookieJar()
    # Share login with the Bilibili web danmaku APIs, including api.bilibili.com.
    for value in cookie.values():
        value['domain'] = 'bilibili.com'
        value['path'] = '/'
    jar.update_cookies(cookie)
    referer = f'https://live.bilibili.com/{args.room_id}'
    async with aiohttp.ClientSession(cookie_jar=jar, timeout=aiohttp.ClientTimeout(total=8),
                                     headers={'User-Agent': 'Mozilla/5.0'}) as session:
        handler = Danmaku(db)
        chat = BLiveClient(args.room_id, session=session)
        chat.set_handler(handler)
        chat.start()
        try:
            await record_loop(args, stage, destination, db, stop, session, handler, referer)
        finally:
            await chat.stop_and_close()


async def record_loop(args, stage, destination, db, stop, session, chat, referer):
    latch = stage / 'takeover'
    endpoint_index = 0
    absent_since = time.monotonic()
    last_warning = float('-inf')
    last_maintenance = float('-inf')
    room_url = f'{args.api_url.rstrip("/")}/api/room/{args.room_id}'
    while not stop.is_set():
        now = time.monotonic()
        if now - last_maintenance > 60:
            for path in sorted(stage.glob('*.flv')):
                await handoff(path, destination, db)
            with db:
                oldest = min((p.stat().st_mtime for p in stage.glob('*.flv')), default=time.time())
                db.execute('DELETE FROM chat WHERE timestamp < ?', (min(oldest - args.segment_seconds, time.time() - CHAT_RETENTION),))
            last_maintenance = now
        try:
            # The LAN API uses a different host, so the Bilibili cookie jar
            # does not send credentials there.
            room = await get_json(session, room_url)
            if not room['streaming']:
                latch.unlink(missing_ok=True)
                absent_since = now
            else:
                newest = max((p.stat().st_mtime for p in destination.glob('*.flv')
                              if '-hls-' not in p.name), default=0)
                if room['recording'] and time.time() - newest < STALL and not latch.exists():
                    absent_since = now
                elif now - absent_since >= STALL or latch.exists():
                    if shutil.disk_usage(stage).free < MIN_FREE:
                        raise ValueError('low disk space')
                    info = await play_info(session, args.room_id, referer)
                    urls = original_urls(info)
                    if info.get('live_status') != 1 or not urls:
                        raise ValueError('original HLS unavailable')
                    if chat.last_heartbeat is None or now - chat.last_heartbeat > 90:
                        LOG.warning('Danmaku heartbeat unavailable at start of HLS segment')
                    latch.touch()
                    LOG.info('Starting HLS recording for %s', args.room_id)
                    result = await capture(
                        urls[endpoint_index % len(urls)], stage, destination, db,
                        referer, room.get('title') or '', args.segment_seconds, stop,
                    )
                    if result:
                        endpoint_index += 1
                        LOG.warning('HLS recorder exited with code %s', result)
        except (aiohttp.ClientError, OSError, ValueError, KeyError, RuntimeError, asyncio.TimeoutError) as error:
            if now - last_warning >= 60:
                # HTTP exceptions can contain signed media URLs.
                reason = str(error) if type(error) is ValueError else type(error).__name__
                LOG.error('HLS recording pending: %s', reason)
                last_warning = now
        try:
            await asyncio.wait_for(stop.wait(), POLL)
        except asyncio.TimeoutError:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--room-id', required=True, type=int)
    parser.add_argument('--api-url', required=True)
    parser.add_argument('--segment-seconds', type=int, default=10800)
    args = parser.parse_args()
    if args.segment_seconds <= 0:
        parser.error('--segment-seconds must be positive')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s %(message)s')
    destination = args.root / str(args.room_id)
    if not destination.is_dir():
        parser.error('room directory does not exist')
    stage = args.root / f'.hls-{args.room_id}'
    stage.mkdir(mode=0o700, exist_ok=True)
    with ProcessLock(stage), closing(sqlite3.connect(stage / 'danmaku.sqlite3')) as db:
        db.execute('CREATE TABLE IF NOT EXISTS chat (timestamp REAL, message TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS chat_time ON chat(timestamp)')
        asyncio.run(run(args, stage, destination, db))


if __name__ == '__main__':
    main()
