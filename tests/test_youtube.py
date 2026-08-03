import json
import runpy
import sys

import pytest

import recorder.destination.youtube as youtube_module
from recorder.destination.youtube import (
    CAPTION_UPLOAD_QUOTA_EXCEEDED,
    CAPTION_UPLOAD_SUCCESS,
    find_missing_caption_uploads,
    upload_missing_captions,
    upload_missing_captions_from_roots,
    Youtube,
)


class FakeYoutube:
    def __init__(self, upload_result=True, captions=None, list_captions_error=False):
        self.upload_result = upload_result
        self.captions = captions or []
        self.list_captions_error = list_captions_error
        self.add_caption_calls = []
        self.list_captions_calls = []

    def add_caption(self, video_id, caption_path, caption_name='via_recorder'):
        self.add_caption_calls.append((video_id, caption_path, caption_name))
        if isinstance(self.upload_result, list):
            return self.upload_result.pop(0)
        return self.upload_result

    def list_captions(self, video_id):
        self.list_captions_calls.append(video_id)
        if self.list_captions_error:
            raise RuntimeError('remote check failed')
        return self.captions


def test_atomic_pickle_dump_replaces_credentials_with_private_file(tmp_path):
    credentials = tmp_path / 'credentials.pkl'
    credentials.write_bytes(b'old')

    youtube_module._atomic_pickle_dump({'token': 'new'}, credentials)

    with credentials.open('rb') as token:
        assert youtube_module.pickle.load(token) == {'token': 'new'}
    assert credentials.stat().st_mode & 0o777 == 0o600
    assert list(tmp_path.glob('*.tmp')) == []


def test_atomic_pickle_dump_failure_preserves_existing_credentials(
    tmp_path, monkeypatch
):
    credentials = tmp_path / 'credentials.pkl'
    credentials.write_bytes(b'old')

    def fail_after_partial_write(value, token):
        del value
        token.write(b'partial')
        raise OSError('no space left on device')

    monkeypatch.setattr(youtube_module.pickle, 'dump', fail_after_partial_write)

    with pytest.raises(OSError, match='no space'):
        youtube_module._atomic_pickle_dump({'token': 'new'}, credentials)

    assert credentials.read_bytes() == b'old'
    assert list(tmp_path.glob('*.tmp')) == []


class ExplodingCaptionList:
    def execute(self):
        raise OSError('google list failed')


class ExplodingCaptionsApi:
    def list(self, part, videoId):
        return ExplodingCaptionList()


class ExplodingYoutubeApi:
    def captions(self):
        return ExplodingCaptionsApi()


class QuotaExceededHttpError(Exception):
    error_details = [{'reason': 'quotaExceeded'}]


class QuotaExceededCaptionInsert:
    def execute(self):
        raise QuotaExceededHttpError()


class QuotaExceededCaptionsApi:
    def insert(self, part, body, media_body):
        return QuotaExceededCaptionInsert()


class QuotaExceededYoutubeApi:
    def captions(self):
        return QuotaExceededCaptionsApi()


class FakeRequest:
    def __init__(self, response=None, exception=None):
        self.response = response
        self.exception = exception

    def execute(self):
        if self.exception:
            raise self.exception
        return self.response


class RecordingListEndpoint:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def list(self, **kwargs):
        self.calls.append(kwargs)
        return FakeRequest(response=self.responses.pop(0))


class QueryYoutubeApi:
    def __init__(self, channels=None, playlist_items=None, videos=None):
        self.channels_endpoint = RecordingListEndpoint(channels or [])
        self.playlist_items_endpoint = RecordingListEndpoint(playlist_items or [])
        self.videos_endpoint = RecordingListEndpoint(videos or [])

    def channels(self):
        return self.channels_endpoint

    def playlistItems(self):
        return self.playlist_items_endpoint

    def videos(self):
        return self.videos_endpoint


class FakeHttpError(Exception):
    def __init__(self, status, reason=None):
        super().__init__(f'HTTP {status}: {reason}')
        self.resp = type('Response', (), {'status': status})()
        self.content = b'fake error'
        self.error_details = [{'reason': reason}] if reason else []


class FailingUploadRequest:
    def __init__(self, exception):
        self.exception = exception
        self.calls = 0

    def next_chunk(self):
        self.calls += 1
        raise self.exception


class SequenceUploadRequest:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def next_chunk(self):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class UploadVideosEndpoint:
    def __init__(self, request):
        self.request = request

    def insert(self, **kwargs):
        return self.request


class UploadYoutubeApi:
    def __init__(self, request):
        self.videos_endpoint = UploadVideosEndpoint(request)

    def videos(self):
        return self.videos_endpoint


class FailingMutationEndpoint:
    def __init__(self, exception):
        self.exception = exception

    def update(self, **kwargs):
        return FakeRequest(exception=self.exception)

    def insert(self, **kwargs):
        return FakeRequest(exception=self.exception)

    def list(self, **kwargs):
        return FakeRequest(exception=self.exception)


class FailingMutationYoutubeApi:
    def __init__(self, exception):
        self.endpoint = FailingMutationEndpoint(exception)

    def videos(self):
        return self.endpoint

    def playlistItems(self):
        return self.endpoint

    def captions(self):
        return self.endpoint


class RecordingCaptionEndpoint:
    def __init__(self, response):
        self.response = response
        self.update_calls = []

    def update(self, **kwargs):
        self.update_calls.append(kwargs)
        return FakeRequest(response=self.response)


class RecordingCaptionYoutubeApi:
    def __init__(self, response):
        self.endpoint = RecordingCaptionEndpoint(response)

    def captions(self):
        return self.endpoint


def create_http_error(payload, status=403):
    response = type('Response', (), {'status': status, 'reason': 'Forbidden'})()
    return youtube_module.googleapiclient.errors.HttpError(
        response,
        json.dumps(payload).encode('utf8'),
    )


def create_caption_and_validate_video(tmp_path):
    caption = tmp_path / 'captions' / 'bilibili' / '1829181560' / '2026-07-04 20-48-09.mp4.vtt'
    caption.parent.mkdir(parents=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')

    validate_video = tmp_path / 'videos' / 'validate' / 'bilibili' / '1829181560' / 'yt123__2026-07-04 20-48-09.mp4'
    validate_video.parent.mkdir(parents=True)
    validate_video.write_bytes(b'')

    return caption, validate_video


def create_caption_and_validate_video_for_start(tmp_path, start, video_id):
    caption = tmp_path / 'captions' / 'bilibili' / '1829181560' / f'{start}.mp4.vtt'
    caption.parent.mkdir(parents=True, exist_ok=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')

    validate_video = tmp_path / 'videos' / 'validate' / 'bilibili' / '1829181560' / f'{video_id}__{start}.mp4'
    validate_video.parent.mkdir(parents=True, exist_ok=True)
    validate_video.write_bytes(b'')

    return caption, validate_video


def test_find_missing_caption_uploads_matches_validate_video(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)

    results = find_missing_caption_uploads(tmp_path / 'captions', tmp_path / 'videos')

    assert len(results) == 1
    assert results[0]['caption_path'] == str(caption)
    assert results[0]['video_id'] == 'yt123'
    assert results[0]['source_type'] == 'bilibili'
    assert results[0]['source_name'] == '1829181560'
    assert results[0]['video_filename'] == '2026-07-04 20-48-09.mp4'
    assert results[0]['status'] == 'pending'


def test_find_missing_caption_uploads_marks_unmatched_caption(tmp_path):
    caption = tmp_path / 'captions' / 'bilibili' / '1829181560' / '2026-07-04 20-48-09.mp4.vtt'
    caption.parent.mkdir(parents=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')

    results = find_missing_caption_uploads(tmp_path / 'captions', tmp_path / 'videos')

    assert len(results) == 1
    assert results[0]['caption_path'] == str(caption)
    assert results[0]['video_id'] is None
    assert results[0]['status'] == 'unmatched'


def test_find_missing_caption_uploads_filters_source_name_without_source_type(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)

    results = find_missing_caption_uploads(
        tmp_path / 'captions',
        tmp_path / 'videos',
        source_name='1829181560',
    )

    assert len(results) == 1
    assert results[0]['caption_path'] == str(caption)
    assert results[0]['video_id'] == 'yt123'
    assert results[0]['source_type'] == 'bilibili'
    assert results[0]['source_name'] == '1829181560'


def test_find_missing_caption_uploads_can_match_from_upload_log(tmp_path):
    caption = tmp_path / 'captions' / 'bilibili' / '1829181560' / '2026-07-04 20-48-09.mp4.vtt'
    caption.parent.mkdir(parents=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    log_path = tmp_path / 'recorder.log'
    log_path.write_text(
        '2026-07-09 02:00:00,000 INFO uploaded: '
        '/mnt/ssd-4t/data/videos/upload/bilibili/1829181560/2026-07-04 20-48-09.mp4 -> yt123\n',
        encoding='utf8',
    )

    results = find_missing_caption_uploads(tmp_path / 'captions', tmp_path / 'videos', log_path=log_path)

    assert len(results) == 1
    assert results[0]['caption_path'] == str(caption)
    assert results[0]['video_id'] == 'yt123'
    assert results[0]['status'] == 'pending'


def test_upload_missing_captions_dry_run_does_not_upload_or_delete(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube()

    results = upload_missing_captions_from_roots(
        youtube, tmp_path / 'captions', tmp_path / 'videos', dry_run=True
    )

    assert results[0]['status'] == 'dry_run'
    assert youtube.add_caption_calls == []
    assert caption.exists()


def test_upload_missing_captions_uploads_and_deletes_caption_on_success(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube(upload_result=True)

    results = upload_missing_captions_from_roots(
        youtube, tmp_path / 'captions', tmp_path / 'videos', dry_run=False
    )

    assert results[0]['status'] == 'uploaded'
    assert youtube.add_caption_calls == [('yt123', str(caption), 'via_recorder_vtt')]
    assert not caption.exists()


def test_upload_missing_captions_keeps_caption_on_failure(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube(upload_result=False)

    results = upload_missing_captions_from_roots(
        youtube, tmp_path / 'captions', tmp_path / 'videos', dry_run=False
    )

    assert results[0]['status'] == 'failed'
    assert youtube.add_caption_calls == [('yt123', str(caption), 'via_recorder_vtt')]
    assert caption.exists()


def test_upload_missing_captions_stops_after_quota_exceeded(tmp_path):
    first_caption, _ = create_caption_and_validate_video_for_start(tmp_path, '2026-07-04 20-48-09', 'yt123')
    second_caption, _ = create_caption_and_validate_video_for_start(tmp_path, '2026-07-04 20-51-08', 'yt456')
    youtube = FakeYoutube(upload_result=['quota_exceeded', True])

    results = upload_missing_captions_from_roots(
        youtube, tmp_path / 'captions', tmp_path / 'videos', dry_run=False
    )

    assert results[0]['status'] == 'quota_exceeded'
    assert results[1]['status'] == 'skipped_quota_exceeded'
    assert youtube.add_caption_calls == [('yt123', str(first_caption), 'via_recorder_vtt')]
    assert first_caption.exists()
    assert second_caption.exists()


def test_upload_missing_captions_skips_existing_remote_caption(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube(captions=[{
        'snippet': {
            'language': 'zh-Hans',
            'name': 'via_recorder_vtt',
        }
    }])

    results = upload_missing_captions_from_roots(
        youtube,
        tmp_path / 'captions',
        tmp_path / 'videos',
        dry_run=False,
        check_remote=True,
    )

    assert results[0]['status'] == 'skipped_remote_exists'
    assert youtube.list_captions_calls == ['yt123']
    assert youtube.add_caption_calls == []
    assert caption.exists()


def test_upload_missing_captions_dry_run_can_check_existing_remote_caption(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube(captions=[{
        'snippet': {
            'language': 'zh-Hans',
            'name': 'via_recorder_vtt',
        }
    }])

    results = upload_missing_captions_from_roots(
        youtube,
        tmp_path / 'captions',
        tmp_path / 'videos',
        dry_run=True,
        check_remote=True,
        delete_skipped=True,
    )

    assert results[0]['status'] == 'skipped_remote_exists'
    assert youtube.list_captions_calls == ['yt123']
    assert youtube.add_caption_calls == []
    assert caption.exists()


def test_upload_missing_captions_can_delete_skipped_remote_caption(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube(captions=[{
        'snippet': {
            'language': 'zh-Hans',
            'name': 'via_recorder_vtt',
        }
    }])

    results = upload_missing_captions_from_roots(
        youtube,
        tmp_path / 'captions',
        tmp_path / 'videos',
        dry_run=False,
        check_remote=True,
        delete_skipped=True,
    )

    assert results[0]['status'] == 'skipped_remote_exists'
    assert not caption.exists()


def test_upload_missing_captions_does_not_upload_when_remote_check_fails(tmp_path):
    caption, _ = create_caption_and_validate_video(tmp_path)
    youtube = FakeYoutube(list_captions_error=True)

    results = upload_missing_captions_from_roots(
        youtube,
        tmp_path / 'captions',
        tmp_path / 'videos',
        dry_run=False,
        check_remote=True,
    )

    assert results[0]['status'] == 'failed_remote_check'
    assert results[0]['message'] == 'remote check failed'
    assert youtube.add_caption_calls == []
    assert caption.exists()


def test_youtube_list_captions_propagates_remote_errors():
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = ExplodingYoutubeApi()

    try:
        youtube.list_captions('yt123')
    except OSError as exception:
        assert str(exception) == 'google list failed'
    else:
        raise AssertionError('list_captions should propagate remote errors')


def test_youtube_add_caption_result_returns_quota_exceeded_without_traceback(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.errors.HttpError', QuotaExceededHttpError)
    caption = tmp_path / 'caption.vtt'
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = QuotaExceededYoutubeApi()

    result = youtube.add_caption_result('yt123', str(caption), 'via_recorder_vtt')
    captured = capsys.readouterr()

    assert result == CAPTION_UPLOAD_QUOTA_EXCEEDED
    assert 'Traceback' not in captured.err
    assert 'quota_exceeded' in captured.err


def test_youtube_add_caption_returns_false_on_quota_exceeded_for_legacy_callers(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.errors.HttpError', QuotaExceededHttpError)
    caption = tmp_path / 'caption.vtt'
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = QuotaExceededYoutubeApi()

    result = youtube.add_caption('yt123', str(caption), 'via_recorder_vtt')
    captured = capsys.readouterr()

    assert result is False
    assert 'Traceback' not in captured.err
    assert 'quota_exceeded' in captured.err


def test_youtube_module_help_does_not_initialize_client(monkeypatch):
    def fail_youtube_init(self, config):
        raise AssertionError('Youtube should not initialize while rendering CLI help')

    monkeypatch.setattr('recorder.destination.youtube.Youtube.__init__', fail_youtube_init)
    monkeypatch.setattr(sys, 'argv', ['youtube.py', '--help'])

    try:
        runpy.run_module('recorder.destination.youtube', run_name='__main__')
    except SystemExit as exception:
        assert exception.code == 0


def test_upload_missing_captions_dry_run_does_not_initialize_client(monkeypatch, tmp_path, capsys):
    create_caption_and_validate_video(tmp_path)

    def fail_youtube_init(config):
        raise AssertionError('Youtube should not initialize during dry-run')

    monkeypatch.setattr('recorder.destination.youtube.Youtube', fail_youtube_init)

    results = upload_missing_captions(
        dry_run=True,
        caption_root=str(tmp_path / 'captions'),
        video_root=str(tmp_path / 'videos'),
    )
    captured = capsys.readouterr()

    assert results is None
    assert 'dry_run:' in captured.out
    assert '-> yt123' in captured.out
    assert 'summary: total=1, dry_run=1' in captured.out


def test_upload_missing_captions_uses_log_path_for_dry_run(monkeypatch, tmp_path, capsys):
    caption = tmp_path / 'captions' / 'bilibili' / '1829181560' / '2026-07-04 20-48-09.mp4.vtt'
    caption.parent.mkdir(parents=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    log_path = tmp_path / 'recorder.log'
    log_path.write_text(
        '2026-07-09 02:00:00,000 INFO uploaded: '
        '/mnt/ssd-4t/data/videos/upload/bilibili/1829181560/2026-07-04 20-48-09.mp4 -> yt123\n',
        encoding='utf8',
    )

    def fail_youtube_init(config):
        raise AssertionError('Youtube should not initialize during dry-run')

    monkeypatch.setattr('recorder.destination.youtube.Youtube', fail_youtube_init)

    results = upload_missing_captions(
        dry_run=True,
        caption_root=str(tmp_path / 'captions'),
        video_root=str(tmp_path / 'videos'),
        log_path=str(log_path),
    )
    captured = capsys.readouterr()

    assert results is None
    assert 'dry_run:' in captured.out
    assert '-> yt123' in captured.out


def test_upload_missing_captions_resolves_relative_roots_against_base_path(monkeypatch, tmp_path, capsys):
    caption_root = tmp_path / 'videos' / 'captions'
    video_root = tmp_path / 'videos'
    caption = caption_root / 'bilibili' / '1829181560' / '2026-07-04 20-48-09.mp4.vtt'
    caption.parent.mkdir(parents=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    validate_video = video_root / 'validate' / 'bilibili' / '1829181560' / 'yt123__2026-07-04 20-48-09.mp4'
    validate_video.parent.mkdir(parents=True)
    validate_video.write_bytes(b'')
    monkeypatch.chdir(tmp_path.parent)
    monkeypatch.setattr('recorder.destination.youtube.recorder.base_path', tmp_path)

    def fail_youtube_init(config):
        raise AssertionError('Youtube should not initialize during dry-run')

    monkeypatch.setattr('recorder.destination.youtube.Youtube', fail_youtube_init)

    results = upload_missing_captions(
        dry_run=True,
        caption_root='videos/captions',
        video_root='videos',
        log_path='recorder.log',
    )
    captured = capsys.readouterr()

    assert results is None
    assert str(caption) in captured.out
    assert '-> yt123' in captured.out
    assert 'summary: total=1, dry_run=1' in captured.out


def test_upload_missing_captions_command_returns_none(monkeypatch, tmp_path):
    create_caption_and_validate_video(tmp_path)

    def fail_youtube_init(config):
        raise AssertionError('Youtube should not initialize during dry-run')

    monkeypatch.setattr('recorder.destination.youtube.Youtube', fail_youtube_init)

    result = upload_missing_captions(
        dry_run=True,
        caption_root=str(tmp_path / 'captions'),
        video_root=str(tmp_path / 'videos'),
    )

    assert result is None


def test_youtube_caption_exists_matches_language_and_name():
    youtube = Youtube.__new__(Youtube)
    list_captions_calls = []

    def list_captions(video_id):
        list_captions_calls.append(video_id)
        return [
            {'snippet': {'language': 'en', 'name': 'via_recorder_vtt'}},
            {'snippet': {'language': 'zh-Hans', 'name': 'other'}},
            {'snippet': {'language': 'zh-Hans', 'name': 'via_recorder_vtt'}},
        ]

    youtube.list_captions = list_captions

    assert youtube.caption_exists('yt123') is True
    assert list_captions_calls == ['yt123']


def test_youtube_caption_exists_requires_both_language_and_name():
    youtube = Youtube.__new__(Youtube)
    youtube.list_captions = lambda video_id: [
        {'snippet': {'language': 'en', 'name': 'custom'}},
        {'snippet': {'language': 'zh-Hans', 'name': 'other'}},
    ]

    assert youtube.caption_exists('yt123', caption_name='custom') is False


def test_youtube_matching_caption_track_ids_returns_exact_named_tracks():
    youtube = Youtube.__new__(Youtube)
    youtube.list_captions = lambda video_id: [
        {'id': 'track-1', 'snippet': {
            'language': youtube.DEFAULT_CAPTION_LANGUAGE,
            'name': 'via_recorder_vtt',
        }},
        {'id': 'track-2', 'snippet': {
            'language': 'en', 'name': 'via_recorder_vtt',
        }},
    ]

    assert youtube.matching_caption_track_ids(
        'yt123', 'via_recorder_vtt'
    ) == ('track-1',)


def test_youtube_update_caption_result_updates_track_media_in_place(tmp_path):
    caption = tmp_path / 'caption.vtt'
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    api = RecordingCaptionYoutubeApi({'id': 'track-1'})
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    result = youtube.update_caption_result(
        'track-1', str(caption), raise_errors=True
    )

    assert result == CAPTION_UPLOAD_SUCCESS
    call = api.endpoint.update_calls[0]
    assert call['part'] == 'id'
    assert call['body'] == {'id': 'track-1'}
    assert call['media_body']._filename == str(caption)


def test_youtube_playlist_contains_queries_video_membership():
    api = QueryYoutubeApi(playlist_items=[{'items': [{'contentDetails': {'videoId': 'yt123'}}]}])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    assert youtube.playlist_contains('yt123', 'PL123') is True
    assert api.playlist_items_endpoint.calls == [{
        'part': 'contentDetails',
        'playlistId': 'PL123',
        'videoId': 'yt123',
        'maxResults': 1,
    }]


def test_youtube_playlist_contains_returns_false_for_no_items():
    api = QueryYoutubeApi(playlist_items=[{'items': []}])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    assert youtube.playlist_contains('yt123', 'PL123') is False


def test_youtube_list_recent_uploads_joins_batched_video_durations():
    api = QueryYoutubeApi(
        channels=[{'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UU123'}}}]}],
        playlist_items=[{'items': [
            {
                'snippet': {'title': 'First', 'publishedAt': '2026-07-27T01:00:00Z'},
                'contentDetails': {'videoId': 'yt1'},
            },
            {
                'snippet': {'title': 'Second', 'publishedAt': '2026-07-26T01:00:00Z'},
                'contentDetails': {'videoId': 'yt2'},
            },
        ]}],
        videos=[{'items': [
            {'id': 'yt2', 'contentDetails': {'duration': 'PT3H2M1.5S'}},
            {'id': 'yt1', 'contentDetails': {'duration': 'PT45S'}},
        ]}],
    )
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    assert youtube.list_recent_uploads(max_results=2) == [
        {
            'video_id': 'yt1',
            'title': 'First',
            'published_at': '2026-07-27T01:00:00Z',
            'duration_seconds': 45,
        },
        {
            'video_id': 'yt2',
            'title': 'Second',
            'published_at': '2026-07-26T01:00:00Z',
            'duration_seconds': 10921.5,
        },
    ]
    assert api.channels_endpoint.calls == [{'part': 'contentDetails', 'mine': True}]
    assert api.playlist_items_endpoint.calls == [{
        'part': 'snippet,contentDetails',
        'playlistId': 'UU123',
        'maxResults': 2,
    }]
    assert api.videos_endpoint.calls == [{
        'part': 'contentDetails',
        'id': 'yt1,yt2',
        'maxResults': 50,
    }]


@pytest.mark.parametrize(
    ('channels_response', 'playlist_response', 'expected_playlist_calls'),
    [
        ({'items': []}, None, []),
        ({'items': [{'contentDetails': {'relatedPlaylists': {}}}]}, None, []),
        (
            {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UU123'}}}]},
            {'items': []},
            [{'part': 'snippet,contentDetails', 'playlistId': 'UU123', 'maxResults': 50}],
        ),
    ],
)
def test_youtube_list_recent_uploads_returns_empty_without_video_query(
    channels_response, playlist_response, expected_playlist_calls
):
    api = QueryYoutubeApi(
        channels=[channels_response],
        playlist_items=[] if playlist_response is None else [playlist_response],
    )
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    assert youtube.list_recent_uploads() == []
    assert api.playlist_items_endpoint.calls == expected_playlist_calls
    assert api.videos_endpoint.calls == []


def test_youtube_get_processing_status_normalizes_status_fields():
    api = QueryYoutubeApi(videos=[{'items': [{
        'status': {
            'uploadStatus': 'rejected',
            'failureReason': 'processingFailed',
            'rejectionReason': 'duplicate',
        }
    }]}])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    assert youtube.get_processing_status('yt123') == {
        'upload_status': 'rejected',
        'failure_reason': 'processingFailed',
        'rejection_reason': 'duplicate',
    }
    assert api.videos_endpoint.calls == [{'part': 'status', 'id': 'yt123'}]


def test_youtube_get_processing_status_normalizes_missing_video():
    api = QueryYoutubeApi(videos=[{'items': []}])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = api

    assert youtube.get_processing_status('yt123') == {
        'upload_status': 'missing',
        'failure_reason': None,
        'rejection_reason': None,
    }


@pytest.mark.parametrize(
    ('duration', 'seconds'),
    [
        ('PT0S', 0),
        ('PT45S', 45),
        ('PT2M', 120),
        ('PT3H2M1.5S', 10921.5),
    ],
)
def test_youtube_duration_seconds_parses_supported_durations(duration, seconds):
    assert youtube_module._youtube_duration_seconds(duration) == seconds


@pytest.mark.parametrize('duration', ['P1D', 'PT', 'PT1Mgarbage', '1:30', None])
def test_youtube_duration_seconds_rejects_unsupported_values(duration):
    with pytest.raises(ValueError):
        youtube_module._youtube_duration_seconds(duration)


@pytest.mark.parametrize('exception', [IOError('disk failed'), FakeHttpError(500, 'backendError')])
def test_youtube_upload_can_bound_retryable_errors(monkeypatch, exception):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.errors.HttpError', FakeHttpError)
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.http.MediaFileUpload', lambda *args, **kwargs: object())
    request = FailingUploadRequest(exception)
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(request)

    with pytest.raises(type(exception)) as raised:
        youtube.upload(
            '/recording.flv',
            'title',
            'description',
            max_retryable_errors=0,
            raise_errors=True,
        )

    assert raised.value is exception
    assert request.calls == 1


def test_youtube_upload_strict_mode_reraises_non_quota_403(monkeypatch):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.errors.HttpError', FakeHttpError)
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.http.MediaFileUpload', lambda *args, **kwargs: object())
    exception = FakeHttpError(403, 'forbidden')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(FailingUploadRequest(exception))

    with pytest.raises(FakeHttpError) as raised:
        youtube.upload('/recording.flv', 'title', raise_errors=True)

    assert raised.value is exception


def test_youtube_upload_non_strict_mode_returns_false_for_non_quota_403(monkeypatch):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.errors.HttpError', FakeHttpError)
    monkeypatch.setattr(
        'recorder.destination.youtube.googleapiclient.http.MediaFileUpload',
        lambda *args, **kwargs: object(),
    )
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(FailingUploadRequest(FakeHttpError(403, 'forbidden')))

    assert youtube.upload('/recording.flv', 'title', raise_errors=False) is False


@pytest.mark.parametrize(
    'payload',
    [
        {
            'error': {
                'message': 'Denied',
                'errors': [
                    {'reason': 'forbidden'},
                    {'reason': 'quotaExceeded'},
                ],
            }
        },
        {
            'error': {
                'message': 'Denied',
                'details': {'reason': 'dailyLimitExceeded'},
            }
        },
        {
            'error': {
                'message': 'Denied',
                'details': 'quotaExceeded',
            }
        },
        {
            'error': {
                'message': 'Denied',
                'details': 'unstructured detail',
                'errors': [{'reason': 'dailyLimitExceeded'}],
            }
        },
    ],
)
def test_youtube_upload_strict_mode_finds_quota_reason_in_real_http_error_shapes(
    monkeypatch, payload
):
    monkeypatch.setattr(
        'recorder.destination.youtube.googleapiclient.http.MediaFileUpload',
        lambda *args, **kwargs: object(),
    )
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(FailingUploadRequest(create_http_error(payload)))

    assert youtube.upload('/recording.flv', 'title', raise_errors=True) is False


@pytest.mark.parametrize('reason', ['quotaExceeded', 'dailyLimitExceeded'])
def test_youtube_upload_strict_mode_returns_false_for_quota_403(monkeypatch, reason):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.errors.HttpError', FakeHttpError)
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.http.MediaFileUpload', lambda *args, **kwargs: object())
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(FailingUploadRequest(FakeHttpError(403, reason)))

    assert youtube.upload('/recording.flv', 'title', raise_errors=True) is False


def test_youtube_upload_allows_one_retryable_error_when_limit_is_one(monkeypatch):
    monkeypatch.setattr(
        'recorder.destination.youtube.googleapiclient.http.MediaFileUpload',
        lambda *args, **kwargs: object(),
    )
    request = SequenceUploadRequest([
        IOError('first failure'),
        (None, {'id': 'yt123'}),
    ])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(request)

    assert youtube.upload('/recording.flv', 'title', max_retryable_errors=1) == 'yt123'
    assert request.calls == 2


def test_youtube_upload_raises_second_retryable_error_when_limit_is_one(monkeypatch):
    monkeypatch.setattr(
        'recorder.destination.youtube.googleapiclient.http.MediaFileUpload',
        lambda *args, **kwargs: object(),
    )
    first_exception = IOError('first failure')
    second_exception = IOError('second failure')
    request = SequenceUploadRequest([first_exception, second_exception])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(request)

    with pytest.raises(IOError) as raised:
        youtube.upload('/recording.flv', 'title', max_retryable_errors=1)

    assert raised.value is second_exception
    assert request.calls == 2


def test_youtube_upload_default_retry_limit_remains_unbounded(monkeypatch):
    monkeypatch.setattr(
        'recorder.destination.youtube.googleapiclient.http.MediaFileUpload',
        lambda *args, **kwargs: object(),
    )
    request = SequenceUploadRequest([
        IOError('first failure'),
        (None, {'id': 'yt123'}),
    ])
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = UploadYoutubeApi(request)

    assert youtube.upload('/recording.flv', 'title') == 'yt123'
    assert request.calls == 2


def test_youtube_update_only_reraises_errors_in_strict_mode():
    exception = OSError('update failed')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FailingMutationYoutubeApi(exception)

    assert youtube.update('yt123', 'title', 'description') is False
    with pytest.raises(OSError) as raised:
        youtube.update('yt123', 'title', 'description', raise_errors=True)
    assert raised.value is exception


def test_youtube_check_processed_only_reraises_errors_in_strict_mode():
    exception = OSError('status failed')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FailingMutationYoutubeApi(exception)

    assert youtube.check_processed('yt123') is False
    with pytest.raises(OSError) as raised:
        youtube.check_processed('yt123', raise_errors=True)
    assert raised.value is exception


def test_youtube_get_processing_status_only_reraises_errors_in_strict_mode():
    exception = OSError('status failed')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FailingMutationYoutubeApi(exception)

    assert youtube.get_processing_status('yt123') is False
    with pytest.raises(OSError) as raised:
        youtube.get_processing_status('yt123', raise_errors=True)
    assert raised.value is exception


def test_youtube_insert_into_playlist_only_reraises_errors_in_strict_mode():
    exception = OSError('playlist failed')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FailingMutationYoutubeApi(exception)

    assert youtube.insert_into_playlist('yt123', 'PL123') is False
    with pytest.raises(OSError) as raised:
        youtube.insert_into_playlist('yt123', 'PL123', raise_errors=True)
    assert raised.value is exception


def test_youtube_add_caption_result_only_reraises_errors_in_strict_mode(monkeypatch):
    monkeypatch.setattr('recorder.destination.youtube.googleapiclient.http.MediaFileUpload', lambda *args, **kwargs: object())
    exception = OSError('caption failed')
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FailingMutationYoutubeApi(exception)

    assert youtube.add_caption_result('yt123', '/caption.vtt') == 'failed'
    with pytest.raises(OSError) as raised:
        youtube.add_caption_result('yt123', '/caption.vtt', raise_errors=True)
    assert raised.value is exception


@pytest.mark.parametrize('reason', ['quotaExceeded', 'dailyLimitExceeded'])
def test_youtube_add_caption_result_strict_mode_preserves_quota_sentinel(
    monkeypatch, capsys, reason
):
    monkeypatch.setattr(
        'recorder.destination.youtube.googleapiclient.http.MediaFileUpload',
        lambda *args, **kwargs: object(),
    )
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FailingMutationYoutubeApi(create_http_error({
        'error': {
            'message': 'Quota exhausted',
            'errors': [{'reason': reason}],
        }
    }))

    assert youtube.add_caption_result('yt123', '/caption.vtt', raise_errors=True) == CAPTION_UPLOAD_QUOTA_EXCEEDED
    assert 'quota_exceeded' in capsys.readouterr().err
