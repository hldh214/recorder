import json
import logging
from types import SimpleNamespace

import pytest

import recorder

mongo_dsn = recorder.config['app'].get('mongo_dsn')
recorder.config['app']['mongo_dsn'] = None
import recorder.app as app
recorder.config['app']['mongo_dsn'] = mongo_dsn
from recorder.publishing import PublishResult, PublishStatus


class FakeYoutube:
    def __init__(self, upload_result='yt123'):
        self.upload_result = upload_result
        self.upload_calls = []
        self.caption_calls = []

    def upload(self, path, title, description, **kwargs):
        self.upload_calls.append((path, title, description, kwargs))
        return self.upload_result

    def caption_exists(self, video_id, caption_name):
        return False

    def add_caption_result(self, video_id, path, caption_name, **kwargs):
        self.caption_calls.append((video_id, path, caption_name, kwargs))
        return 'uploaded'

    def get_processing_status(self, video_id, **kwargs):
        return {
            'upload_status': 'processed',
            'failure_reason': None,
            'rejection_reason': None,
        }


def make_config(tmp_path, *, source_type='bilibili'):
    return {
        'app': {
            'video_path': str(tmp_path / 'videos'),
            'danmaku_path': str(tmp_path / 'captions'),
        },
        'source': {
            'alice': {
                'source_type': source_type,
                'room_id': 'room-1',
                'title': 'Live {datetime}',
                'description': 'Base description',
            },
        },
    }


def make_upload_video(tmp_path, content=b'original-video'):
    path = (
        tmp_path / 'videos' / 'upload' / 'bilibili' / 'alice'
        / '2026-07-27 18:00:00.mp4'
    )
    path.parent.mkdir(parents=True)
    path.write_bytes(content)
    return path


def metadata_path_for(video_path):
    return app.pathlib.Path(str(video_path).split('.')[0].replace('upload', 'record') + '.metadata')


def test_process_upload_file_adapts_bilibili_caption_and_moves_source(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    video_path = make_upload_video(tmp_path)
    metadata_path = metadata_path_for(video_path)
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps({'title': 'Stream title'}), encoding='utf8')
    generated_calls = []

    def generate(room_id, start, end, caption_path):
        generated_calls.append((room_id, start, end, caption_path))
        caption = app.pathlib.Path(caption_path)
        caption.write_text('WEBVTT\n\n', encoding='utf8')
        return 'Highlights\n00:00 Start'

    monkeypatch.setattr(
        app,
        'bilibili_danmaku_mongo',
        SimpleNamespace(gen_caption_and_return_highlights=generate),
    )
    monkeypatch.setattr(app.ffmpeg, 'calc_end_time', lambda *args: '2026-07-27 19:00:00')
    monkeypatch.setattr(app, 'video_name_sep', '__')
    youtube = FakeYoutube()

    result = app.process_upload_file(config, youtube, str(video_path))

    validate_path = (
        tmp_path / 'videos' / 'validate' / 'bilibili' / 'alice'
        / 'yt123__2026-07-27 18:00:00.mp4'
    )
    caption_path = (
        tmp_path / 'captions' / 'bilibili' / 'alice'
        / '2026-07-27 18:00:00.mp4.vtt'
    )
    assert result.status is PublishStatus.COMPLETE
    assert result.video_id == 'yt123'
    assert not video_path.exists()
    assert validate_path.read_bytes() == b'original-video'
    assert not metadata_path.exists()
    assert not caption_path.exists()
    assert generated_calls == [(
        'room-1',
        '2026-07-27 18:00:00',
        '2026-07-27 19:00:00',
        str(caption_path),
    )]
    assert youtube.upload_calls == [(
        str(video_path),
        'Live 2026-07-27 18:00:00: Stream title',
        'Base description\n\nHighlights\n00:00 Start',
        {'max_retryable_errors': 0, 'raise_errors': True},
    )]
    assert youtube.caption_calls == [(
        'yt123',
        str(caption_path),
        'via_recorder_vtt',
        {'raise_errors': True},
    )]


def test_process_upload_file_without_video_id_preserves_upload_artifacts(tmp_path, monkeypatch, caplog):
    config = make_config(tmp_path)
    video_path = make_upload_video(tmp_path)
    metadata_path = metadata_path_for(video_path)
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps({'title': 'Stream title'}), encoding='utf8')
    caption_path = (
        tmp_path / 'captions' / 'bilibili' / 'alice'
        / '2026-07-27 18:00:00.mp4.vtt'
    )
    caption_path.parent.mkdir(parents=True)
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    monkeypatch.setattr(app, 'bilibili_danmaku_mongo', None)
    monkeypatch.setattr(app.ffmpeg, 'calc_end_time', lambda *args: '2026-07-27 19:00:00')
    monkeypatch.setattr(app.ffmpeg, 'get_bilibili_title', lambda path: None)
    caplog.set_level(logging.WARNING, logger='recorder')

    result = app.process_upload_file(config, FakeYoutube(upload_result=None), str(video_path))

    assert result.status is PublishStatus.QUOTA_EXCEEDED
    assert result.video_id is None
    assert video_path.read_bytes() == b'original-video'
    assert metadata_path.exists()
    assert caption_path.exists()
    assert not (tmp_path / 'videos' / 'validate').exists()
    assert (
        'YouTube publication failed (quota_exceeded) at video: '
        'YouTube API quota exceeded'
    ) in caplog.messages


@pytest.mark.parametrize('status', [PublishStatus.RETRYABLE, PublishStatus.FATAL])
def test_process_upload_file_logs_failed_result_without_mutating_artifacts(
    tmp_path,
    monkeypatch,
    caplog,
    status,
):
    config = make_config(tmp_path)
    video_path = make_upload_video(tmp_path)
    metadata_path = metadata_path_for(video_path)
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps({'title': 'Stream title'}), encoding='utf8')
    publish_result = PublishResult(
        status,
        error_stage='video',
        error_message='connection lost',
    )
    publisher = SimpleNamespace(publish_video=lambda *args, **kwargs: publish_result)
    monkeypatch.setattr(app, 'YoutubePublishService', lambda *args: publisher)
    monkeypatch.setattr(app, 'bilibili_danmaku_mongo', None)
    monkeypatch.setattr(app.ffmpeg, 'calc_end_time', lambda *args: '2026-07-27 19:00:00')
    caplog.set_level(logging.WARNING, logger='recorder')

    result = app.process_upload_file(config, object(), str(video_path))

    assert result is publish_result
    assert (
        f'YouTube publication failed ({status.value}) at video: connection lost'
        in caplog.messages
    )
    assert video_path.read_bytes() == b'original-video'
    assert metadata_path.exists()
    assert not (tmp_path / 'videos' / 'validate').exists()


@pytest.mark.parametrize(
    ('status', 'stage', 'message'),
    [
        (PublishStatus.RETRYABLE, 'caption', 'caption transport failed'),
        (PublishStatus.QUOTA_EXCEEDED, 'caption', 'caption quota exceeded'),
        (PublishStatus.FATAL, 'playlist', 'playlist rejected'),
    ],
)
def test_process_upload_file_logs_post_upload_failure_and_preserves_move_lifecycle(
    tmp_path,
    monkeypatch,
    caplog,
    status,
    stage,
    message,
):
    config = make_config(tmp_path)
    video_path = make_upload_video(tmp_path)
    metadata_path = metadata_path_for(video_path)
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps({'title': 'Stream title'}), encoding='utf8')
    publish_result = PublishResult(
        status,
        video_id='yt123',
        video_uploaded=True,
        error_stage=stage,
        error_message=message,
    )
    publisher = SimpleNamespace(publish_video=lambda *args, **kwargs: publish_result)
    monkeypatch.setattr(app, 'YoutubePublishService', lambda *args: publisher)
    monkeypatch.setattr(app, 'bilibili_danmaku_mongo', None)
    monkeypatch.setattr(app.ffmpeg, 'calc_end_time', lambda *args: '2026-07-27 19:00:00')
    monkeypatch.setattr(app, 'video_name_sep', '__')
    caplog.set_level(logging.INFO, logger='recorder')

    result = app.process_upload_file(config, object(), str(video_path))

    validate_path = (
        tmp_path / 'videos' / 'validate' / 'bilibili' / 'alice'
        / 'yt123__2026-07-27 18:00:00.mp4'
    )
    assert result is publish_result
    assert (
        f'YouTube publication failed ({status.value}) at {stage}: {message}'
        in caplog.messages
    )
    assert validate_path.read_bytes() == b'original-video'
    assert not metadata_path.exists()


def test_process_upload_file_logs_completed_caption_and_playlist_stages(tmp_path, monkeypatch, caplog):
    config = make_config(tmp_path)
    config['source']['alice']['playlist_id'] = 'PL123'
    video_path = make_upload_video(tmp_path)
    publish_result = PublishResult(
        PublishStatus.COMPLETE,
        video_id='yt123',
        video_uploaded=True,
        caption_uploaded=True,
        playlist_inserted=True,
        youtube_processed=True,
    )
    publisher = SimpleNamespace(publish_video=lambda *args, **kwargs: publish_result)
    monkeypatch.setattr(app, 'YoutubePublishService', lambda *args: publisher)
    monkeypatch.setattr(app, 'bilibili_danmaku_mongo', None)
    monkeypatch.setattr(app.ffmpeg, 'calc_end_time', lambda *args: '2026-07-27 19:00:00')
    caplog.set_level(logging.INFO, logger='recorder')

    app.process_upload_file(config, object(), str(video_path))

    assert any('caption publication complete' in message for message in caplog.messages)
    assert any('playlist publication complete' in message for message in caplog.messages)


def test_process_upload_file_uses_bilibili_tag_title_fallback(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    video_path = make_upload_video(tmp_path)
    monkeypatch.setattr(app, 'bilibili_danmaku_mongo', None)
    monkeypatch.setattr(app.ffmpeg, 'calc_end_time', lambda *args: '2026-07-27 19:00:00')
    monkeypatch.setattr(app.ffmpeg, 'get_bilibili_title', lambda path: 'Tagged title')
    youtube = FakeYoutube()

    app.process_upload_file(config, youtube, str(video_path))

    assert youtube.upload_calls[0][1] == 'Live 2026-07-27 18:00:00: Tagged title'


@pytest.mark.parametrize(
    ('result', 'expected_sleeps', 'quota_warning'),
    [
        pytest.param(
            PublishResult(PublishStatus.QUOTA_EXCEEDED, error_stage='video'),
            [99, 5],
            True,
            id='video-quota-without-id',
        ),
        pytest.param(
            PublishResult(
                PublishStatus.QUOTA_EXCEEDED,
                video_id='yt123',
                video_uploaded=True,
                error_stage='caption',
            ),
            [5],
            False,
            id='caption-quota-with-id',
        ),
        pytest.param(
            PublishResult(
                PublishStatus.QUOTA_EXCEEDED,
                video_id='yt123',
                video_uploaded=True,
                error_stage='processing',
            ),
            [5],
            False,
            id='processing-quota-with-id',
        ),
        pytest.param(
            PublishResult(PublishStatus.RETRYABLE, error_stage='video'),
            [5, 5],
            False,
            id='retryable-video-without-id',
        ),
    ],
)
def test_upload_thread_applies_stage_specific_sleep(
    monkeypatch,
    caplog,
    result,
    expected_sleeps,
    quota_warning,
):
    sleeps = []
    process_calls = []
    monkeypatch.setattr(app.glob, 'glob', lambda pattern: ['/tmp/video.mp4'])

    def process(*args):
        process_calls.append(args)
        return result

    monkeypatch.setattr(app, 'process_upload_file', process)

    def sleep(seconds):
        sleeps.append(seconds)
        if len(sleeps) == len(expected_sleeps):
            raise RuntimeError('stop loop')

    monkeypatch.setattr(app.time, 'sleep', sleep)
    caplog.set_level(logging.WARNING, logger='recorder')

    with pytest.raises(RuntimeError, match='stop loop'):
        app.upload_thread({'app': {'video_path': '/tmp'}}, object(), interval=5, quota_exceeded_sleep=99)

    assert len(process_calls) == 1
    assert sleeps == expected_sleeps
    assert any('quota exceeded, sleep 99 secs' in message for message in caplog.messages) is quota_warning
