import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from recorder.bililive.journal import JsonlJournal
from recorder.bililive.media import inspect_media
from recorder.bililive.models import ClassifiedMedia
from recorder.bililive.runner import BililivePublishRunner
from recorder.publishing.youtube import YoutubePublishService


ROOM_ID = 1829181560
NOW = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


class FakeYoutube:
    def __init__(self):
        self.upload_calls = []
        self.caption_calls = []

    def upload(self, path, title, description, **kwargs):
        self.upload_calls.append((path, title, description, kwargs))
        return 'video-1'

    def update(self, *args, **kwargs):
        return True

    def matching_caption_track_ids(self, video_id, caption_name):
        return ()

    def add_caption_track_result(self, video_id, path, caption_name, **kwargs):
        self.caption_calls.append((video_id, Path(path).read_text(), caption_name))
        return 'caption-1'

    def playlist_contains(self, video_id, playlist_id):
        return False

    def insert_into_playlist(self, video_id, playlist_id, **kwargs):
        return True

    def get_processing_status(self, video_id, **kwargs):
        return {
            'upload_status': 'processed',
            'failure_reason': None,
            'rejection_reason': None,
        }


def identity(path):
    stat_result = path.stat()
    return (
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
    )


@pytest.mark.skipif(
    shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None,
    reason='ffmpeg and ffprobe are required',
)
def test_real_probe_xml_and_fake_youtube_leave_source_identity_unchanged(tmp_path):
    video_path = tmp_path / '2026-07-28 19:00:00.flv'
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=320x180:r=1:d=1',
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-shortest', '-c:v', 'flv', '-c:a', 'aac',
        str(video_path),
    ], check=True, timeout=30)
    xml_path = video_path.with_suffix('.xml')
    xml_path.write_text(
        '<i><d p="0.1,1,25,16777215,0,0,0,0">first</d>'
        '<d p="0.7,1,25,16777215,0,0,0,0">second</d></i>',
        encoding='utf8',
    )
    before = {path: identity(path) for path in (video_path, xml_path)}

    media = inspect_media(video_path)
    classified = ClassifiedMedia(
        media=media, status='ready', reason='integration fixture', is_tail=True
    )
    journal = JsonlJournal(tmp_path / 'state' / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint=media.fingerprint, manifest_id=None,
        file=str(video_path.resolve()), xml_file=str(xml_path.resolve()),
        title=media.stream_title, stream_title=media.stream_title,
        start_time=media.start_time.isoformat(), duration=media.duration,
        source_size=media.size, source_mtime_ns=media.mtime_ns,
        caption_status='pending',
    )
    youtube = FakeYoutube()
    publisher = YoutubePublishService(youtube, {
        'source': {str(ROOM_ID): {
            'title': 'Live {datetime}',
            'description': 'Integration test',
        }},
    })
    runner = BililivePublishRunner(
        journal=journal, publisher=publisher, room_id=ROOM_ID,
        state_dir=tmp_path / 'state', clock=lambda: NOW,
    )

    result = runner.publish_one(classified)

    assert result.status == 'complete'
    assert len(youtube.upload_calls) == 1
    assert len(youtube.caption_calls) == 1
    assert 'first' in youtube.caption_calls[0][1]
    assert 'second' in youtube.caption_calls[0][1]
    assert {path: identity(path) for path in (video_path, xml_path)} == before
