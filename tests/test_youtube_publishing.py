import hashlib
import json
import os
import socket

import googleapiclient.errors
import httplib2
import pytest

from recorder.destination.youtube import (
    CAPTION_UPLOAD_FAILED,
    CAPTION_UPLOAD_QUOTA_EXCEEDED,
    CAPTION_UPLOAD_SUCCESS,
)
from recorder.publishing.youtube import (
    CaptionArtifact,
    PublishCheckpoint,
    PublishStatus,
    YoutubePublishService,
)


class FakeHttpError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.resp = type('Response', (), {'status': status})()


class FakeAuthError(Exception):
    pass


class FakeYoutube:
    def __init__(
        self,
        *,
        upload_result='yt123',
        caption_exists=False,
        caption_result=CAPTION_UPLOAD_SUCCESS,
        playlist_contains=False,
        playlist_result=True,
        update_result=True,
        processing=None,
        events=None,
    ):
        self.upload_result = upload_result
        self.caption_exists_result = caption_exists
        self.caption_result = caption_result
        self.playlist_contains_result = playlist_contains
        self.playlist_result = playlist_result
        self.update_result = update_result
        self.processing = processing or {
            'upload_status': 'processed',
            'failure_reason': None,
            'rejection_reason': None,
        }
        self.events = events if events is not None else []
        self.upload_calls = []
        self.caption_exists_calls = []
        self.caption_calls = []
        self.playlist_contains_calls = []
        self.playlist_calls = []
        self.update_calls = []
        self.processing_calls = []

    @staticmethod
    def _resolve(value):
        if isinstance(value, BaseException):
            raise value
        return value

    def upload(self, path, title, description, **kwargs):
        self.events.append('upload')
        self.upload_calls.append((path, title, description, kwargs))
        return self._resolve(self.upload_result)

    def caption_exists(self, video_id, caption_name):
        self.caption_exists_calls.append((video_id, caption_name))
        return self._resolve(self.caption_exists_result)

    def add_caption_result(self, video_id, path, caption_name, **kwargs):
        self.caption_calls.append((video_id, path, caption_name, kwargs))
        return self._resolve(self.caption_result)

    def playlist_contains(self, video_id, playlist_id):
        self.playlist_contains_calls.append((video_id, playlist_id))
        return self._resolve(self.playlist_contains_result)

    def insert_into_playlist(self, video_id, playlist_id, **kwargs):
        self.playlist_calls.append((video_id, playlist_id, kwargs))
        return self._resolve(self.playlist_result)

    def update(self, video_id, title, description, **kwargs):
        self.update_calls.append((video_id, title, description, kwargs))
        return self._resolve(self.update_result)

    def get_processing_status(self, video_id, **kwargs):
        self.processing_calls.append((video_id, kwargs))
        return self._resolve(self.processing)


def source_config(*, playlist=True):
    source = {
        'title': 'Live {datetime}',
        'description': 'Base description',
    }
    if playlist:
        source['playlist_id'] = 'PL123'
    return {'source': {'1829181560': source}}


def description_fingerprint(description):
    return hashlib.sha256(description.encode('utf8')).hexdigest()


def create_http_error(reason, status=403):
    response = type('Response', (), {'status': status, 'reason': 'request failed'})()
    return googleapiclient.errors.HttpError(
        response,
        json.dumps({
            'error': {
                'message': reason,
                'errors': [{'reason': reason}],
            }
        }).encode('utf8'),
    )


def make_video(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'original-flv')
    return video


def test_non_path_video_source_is_fatal(tmp_path):
    youtube = FakeYoutube()

    result = YoutubePublishService(youtube, source_config()).publish_video(
        None, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'video'
    assert youtube.upload_calls == []


def test_publish_video_completes_all_stages_without_mutating_source(tmp_path):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    before = (
        video.stat().st_ino,
        video.stat().st_size,
        video.stat().st_mtime_ns,
        video.read_bytes(),
    )
    youtube = FakeYoutube()

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        stream_title='Stream title',
        caption=CaptionArtifact(caption_path, 'Highlights\n00:00 Start'),
    )

    after = (
        video.stat().st_ino,
        video.stat().st_size,
        video.stat().st_mtime_ns,
        video.read_bytes(),
    )
    description = 'Base description\n\nHighlights\n00:00 Start'
    assert result.status is PublishStatus.COMPLETE
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True
    assert result.caption_uploaded is True
    assert result.playlist_inserted is True
    assert result.youtube_processed is True
    assert result.caption_status == 'uploaded'
    assert result.description_fingerprint == description_fingerprint(description)
    assert youtube.upload_calls == [(
        str(video),
        'Live 2026-07-27 18:00:00: Stream title',
        description,
        {'max_retryable_errors': 0, 'raise_errors': True},
    )]
    assert youtube.caption_calls == [(
        'yt123', str(caption_path), 'via_recorder_vtt', {'raise_errors': True}
    )]
    assert youtube.playlist_calls == [('yt123', 'PL123', {'raise_errors': True})]
    assert youtube.processing_calls == [('yt123', {'raise_errors': True})]
    assert before == after
    assert not caption_path.exists()


@pytest.mark.parametrize('alias_kind', ['direct', 'symlink', 'hardlink'])
def test_ready_caption_aliasing_source_is_fatal_without_source_mutation(tmp_path, alias_kind):
    video = make_video(tmp_path)
    if alias_kind == 'direct':
        caption_path = video
    else:
        caption_path = tmp_path / f'{alias_kind}.vtt'
        if alias_kind == 'symlink':
            caption_path.symlink_to(video)
        else:
            os.link(video, caption_path)
    before = (video.stat().st_ino, video.stat().st_size, video.read_bytes())
    callback_calls = []
    youtube = FakeYoutube()

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path),
        before_video_upload=lambda *args: callback_calls.append(args),
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'caption'
    assert callback_calls == []
    assert youtube.events == []
    assert youtube.upload_calls == []
    assert video.exists()
    assert (video.stat().st_ino, video.stat().st_size, video.read_bytes()) == before
    assert caption_path.exists()


def test_caption_identity_stat_error_is_retryable_before_remote_work(tmp_path, monkeypatch):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    original_samefile = type(caption_path).samefile

    def fail_caption_samefile(path, other_path):
        if path == caption_path:
            raise OSError('caption storage unavailable')
        return original_samefile(path, other_path)

    monkeypatch.setattr(type(caption_path), 'samefile', fail_caption_samefile)
    callback_calls = []
    youtube = FakeYoutube()

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path),
        before_video_upload=lambda *args: callback_calls.append(args),
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == 'caption'
    assert callback_calls == []
    assert youtube.events == []
    assert caption_path.exists()
    assert video.read_bytes() == b'original-flv'


def test_publish_video_resumes_from_video_checkpoint_without_reupload(tmp_path):
    video = make_video(tmp_path)
    fingerprint = description_fingerprint('Base description')
    youtube = FakeYoutube(processing={
        'upload_status': 'processing',
        'failure_reason': None,
        'rejection_reason': None,
    })

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        checkpoint=PublishCheckpoint(
            video_id='yt123',
            video_uploaded=True,
            description_fingerprint=fingerprint,
        ),
    )

    assert result.status is PublishStatus.PENDING
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True
    assert youtube.upload_calls == []
    assert youtube.update_calls == []


def test_video_id_normalizes_video_upload_stage_to_complete(tmp_path):
    video = make_video(tmp_path)
    fingerprint = description_fingerprint('Base description')
    youtube = FakeYoutube()

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        checkpoint=PublishCheckpoint(
            video_id='yt123',
            description_fingerprint=fingerprint,
        ),
    )

    assert result.status is PublishStatus.COMPLETE
    assert result.video_uploaded is True
    assert youtube.upload_calls == []


def test_publish_video_returns_caption_quota_without_losing_video_id(tmp_path):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    youtube = FakeYoutube(caption_result=CAPTION_UPLOAD_QUOTA_EXCEEDED)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path),
    )

    assert result.status is PublishStatus.QUOTA_EXCEEDED
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True
    assert result.caption_uploaded is False
    assert result.caption_status == CAPTION_UPLOAD_QUOTA_EXCEEDED
    assert result.error_stage == 'caption'
    assert result.remote_outcome_unknown is False
    assert caption_path.exists()


def test_existing_remote_caption_and_playlist_skip_mutations(tmp_path):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    fingerprint = description_fingerprint('Base description')
    youtube = FakeYoutube(caption_exists=True, playlist_contains=True)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path),
        checkpoint=PublishCheckpoint(
            video_id='yt123',
            video_uploaded=True,
            description_fingerprint=fingerprint,
        ),
    )

    assert result.status is PublishStatus.COMPLETE
    assert result.caption_uploaded is True
    assert result.playlist_inserted is True
    assert result.caption_status == 'existing'
    assert youtube.caption_calls == []
    assert youtube.playlist_calls == []
    assert not caption_path.exists()


@pytest.mark.parametrize(
    'config',
    [
        {},
        {'source': None},
        {'source': {}},
        {'source': {'1829181560': None}},
        {'source': {'1829181560': {}}},
        {'source': {'1829181560': {'title': 42}}},
        {'source': {'1829181560': {'title': '{}'}}},
    ],
)
def test_missing_or_malformed_source_config_is_fatal_before_callback(tmp_path, config):
    video = make_video(tmp_path)
    youtube = FakeYoutube()
    callback_calls = []

    result = YoutubePublishService(youtube, config).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        before_video_upload=lambda *args: callback_calls.append(args),
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'config'
    assert callback_calls == []
    assert youtube.upload_calls == []


def test_invalid_caption_does_not_block_video_publication(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube()

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(path=None, status='invalid'),
    )

    assert result.status is PublishStatus.COMPLETE
    assert result.video_uploaded is True
    assert result.caption_uploaded is False
    assert result.caption_status == 'invalid'
    assert youtube.upload_calls
    assert youtube.caption_exists_calls == []
    assert youtube.caption_calls == []


def test_existing_video_gets_new_highlight_description_without_reupload(tmp_path):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    old_fingerprint = description_fingerprint('Base description')
    new_description = 'Base description\n\nNew highlights'
    youtube = FakeYoutube(caption_exists=True)

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path, highlights='New highlights'),
        checkpoint=PublishCheckpoint(
            video_id='yt123',
            video_uploaded=True,
            description_fingerprint=old_fingerprint,
        ),
    )

    assert result.status is PublishStatus.COMPLETE
    assert youtube.upload_calls == []
    assert youtube.update_calls == [(
        'yt123',
        'Live 2026-07-27 18:00:00',
        new_description,
        {'raise_errors': True},
    )]
    assert result.description_fingerprint == description_fingerprint(new_description)


@pytest.mark.parametrize(
    ('upload_status', 'failure_reason', 'rejection_reason', 'expected_reason'),
    [
        ('failed', 'processingFailed', None, 'processingFailed'),
        ('rejected', None, 'duplicate', 'duplicate'),
        ('rejected', 'processingFailed', 'duplicate', 'duplicate'),
    ],
)
def test_terminal_youtube_processing_failure_is_fatal(
    tmp_path, upload_status, failure_reason, rejection_reason, expected_reason
):
    video = make_video(tmp_path)
    youtube = FakeYoutube(processing={
        'upload_status': upload_status,
        'failure_reason': failure_reason,
        'rejection_reason': rejection_reason,
    })

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'processing'
    assert expected_reason in result.error_message
    assert result.youtube_processed is False


def test_deleted_youtube_video_is_terminal_processing_failure(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(processing={
        'upload_status': 'deleted',
        'failure_reason': 'userRequested',
        'rejection_reason': None,
    })

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'processing'
    assert 'deleted' in result.error_message
    assert 'userRequested' in result.error_message
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True


def test_checkpoint_callback_completes_immediately_before_upload(tmp_path):
    video = make_video(tmp_path)
    events = []
    callback_args = []
    youtube = FakeYoutube(events=events)

    def checkpoint_callback(title, fingerprint):
        callback_args.append((title, fingerprint))
        events.append('checkpoint')

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        before_video_upload=checkpoint_callback,
    )

    assert result.status is PublishStatus.COMPLETE
    assert events == ['checkpoint', 'upload']
    assert callback_args == [(
        'Live 2026-07-27 18:00:00',
        description_fingerprint('Base description'),
    )]


def test_checkpoint_callback_failure_prevents_upload(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube()

    def fail_callback(title, fingerprint):
        raise OSError('journal fsync failed')

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        before_video_upload=fail_callback,
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == 'checkpoint'
    assert result.remote_outcome_unknown is False
    assert 'journal fsync failed' in result.error_message
    assert youtube.upload_calls == []


@pytest.mark.parametrize(
    'exception',
    [
        socket.timeout('timed out'),
        ConnectionError('connection lost'),
        FakeHttpError(503, 'backend unavailable'),
    ],
)
def test_retryable_upload_failure_after_callback_has_unknown_remote_outcome(
    tmp_path, exception
):
    video = make_video(tmp_path)
    events = []
    youtube = FakeYoutube(upload_result=exception, events=events)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        before_video_upload=lambda *args: events.append('checkpoint'),
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == 'video'
    assert result.remote_outcome_unknown is True
    assert result.video_id is None
    assert events == ['checkpoint', 'upload']
    assert len(youtube.upload_calls) == 1


def test_conclusive_upload_quota_has_known_remote_outcome(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(upload_result=False)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.QUOTA_EXCEEDED
    assert result.error_stage == 'video'
    assert result.remote_outcome_unknown is False


def test_conclusive_upload_auth_error_is_fatal_with_known_remote_outcome(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(upload_result=FakeHttpError(401, 'invalid credentials'))

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'video'
    assert result.remote_outcome_unknown is False
    assert 'invalid credentials' in result.error_message


def test_statusless_auth_error_is_fatal_with_known_remote_outcome(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(upload_result=FakeAuthError('token refresh denied'))

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'video'
    assert result.remote_outcome_unknown is False
    assert 'token refresh denied' in result.error_message


def test_statusless_httplib2_transport_failure_is_retryable(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(upload_result=httplib2.ServerNotFoundError('youtube.test'))

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == 'video'
    assert result.remote_outcome_unknown is True


def test_statusless_httplib2_configuration_failure_is_fatal(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(
        upload_result=httplib2.ProxiesUnavailableError('proxy support unavailable')
    )

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.FATAL
    assert result.error_stage == 'video'
    assert result.remote_outcome_unknown is False


def test_quota_during_caption_remote_read_is_quota_exceeded(tmp_path):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    youtube = FakeYoutube(caption_exists=create_http_error('quotaExceeded'))

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path),
    )

    assert result.status is PublishStatus.QUOTA_EXCEEDED
    assert result.error_stage == 'caption'
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True
    assert caption_path.exists()


@pytest.mark.parametrize(
    ('failure_stage', 'expected_stage'),
    [
        ('update', 'description'),
        ('caption', 'caption'),
        ('playlist', 'playlist'),
        ('processing', 'processing'),
    ],
)
@pytest.mark.parametrize('reason', ['rateLimitExceeded', 'userRateLimitExceeded'])
def test_rate_limit_errors_are_retryable_at_each_remote_stage(
    tmp_path, failure_stage, expected_stage, reason
):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    error = create_http_error(reason)
    kwargs = {}
    checkpoint = None
    caption = None
    if failure_stage == 'update':
        kwargs['update_result'] = error
        checkpoint = PublishCheckpoint(video_id='yt123', video_uploaded=True)
    elif failure_stage == 'caption':
        kwargs['caption_result'] = error
        caption = CaptionArtifact(caption_path)
    elif failure_stage == 'playlist':
        kwargs['playlist_contains'] = error
    else:
        kwargs['processing'] = error
    youtube = FakeYoutube(**kwargs)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=caption,
        checkpoint=checkpoint,
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == expected_stage
    assert result.video_id == 'yt123'


def test_quota_during_processing_read_is_quota_exceeded(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(processing=create_http_error('dailyLimitExceeded'))

    result = YoutubePublishService(youtube, source_config(playlist=False)).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.QUOTA_EXCEEDED
    assert result.error_stage == 'processing'
    assert result.video_id == 'yt123'


def test_temporary_caption_is_preserved_until_upload_is_confirmed(tmp_path):
    video = make_video(tmp_path)
    caption_path = tmp_path / 'recording.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    youtube = FakeYoutube(caption_result=CAPTION_UPLOAD_FAILED)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video,
        'bilibili',
        '1829181560',
        '2026-07-27 18:00:00',
        caption=CaptionArtifact(caption_path),
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == 'caption'
    assert caption_path.exists()
    assert video.exists()
    assert video.read_bytes() == b'original-flv'


def test_playlist_insert_failure_is_retryable_and_retains_completed_video(tmp_path):
    video = make_video(tmp_path)
    youtube = FakeYoutube(playlist_result=False)

    result = YoutubePublishService(youtube, source_config()).publish_video(
        video, 'bilibili', '1829181560', '2026-07-27 18:00:00'
    )

    assert result.status is PublishStatus.RETRYABLE
    assert result.error_stage == 'playlist'
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True
    assert result.playlist_inserted is False
