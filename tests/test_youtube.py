import runpy
import sys

from recorder.destination.youtube import (
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
        return self.upload_result

    def list_captions(self, video_id):
        self.list_captions_calls.append(video_id)
        if self.list_captions_error:
            raise RuntimeError('remote check failed')
        return self.captions


class ExplodingCaptionList:
    def execute(self):
        raise OSError('google list failed')


class ExplodingCaptionsApi:
    def list(self, part, videoId):
        return ExplodingCaptionList()


class ExplodingYoutubeApi:
    def captions(self):
        return ExplodingCaptionsApi()


def create_caption_and_validate_video(tmp_path):
    caption = tmp_path / 'captions' / 'bilibili' / '1829181560' / '2026-07-04 20-48-09.mp4.vtt'
    caption.parent.mkdir(parents=True)
    caption.write_text('WEBVTT\n\n', encoding='utf8')

    validate_video = tmp_path / 'videos' / 'validate' / 'bilibili' / '1829181560' / 'yt123__2026-07-04 20-48-09.mp4'
    validate_video.parent.mkdir(parents=True)
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


def test_youtube_module_help_does_not_initialize_client(monkeypatch):
    def fail_youtube_init(self, config):
        raise AssertionError('Youtube should not initialize while rendering CLI help')

    monkeypatch.setattr('recorder.destination.youtube.Youtube.__init__', fail_youtube_init)
    monkeypatch.setattr(sys, 'argv', ['youtube.py', '--help'])

    try:
        runpy.run_module('recorder.destination.youtube', run_name='__main__')
    except SystemExit as exception:
        assert exception.code == 0


def test_upload_missing_captions_dry_run_does_not_initialize_client(monkeypatch, tmp_path):
    create_caption_and_validate_video(tmp_path)

    def fail_youtube_init(config):
        raise AssertionError('Youtube should not initialize during dry-run')

    monkeypatch.setattr('recorder.destination.youtube.Youtube', fail_youtube_init)

    results = upload_missing_captions(
        dry_run=True,
        caption_root=str(tmp_path / 'captions'),
        video_root=str(tmp_path / 'videos'),
    )

    assert results[0]['status'] == 'dry_run'


def test_upload_missing_captions_uses_log_path_for_dry_run(monkeypatch, tmp_path):
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

    assert results[0]['video_id'] == 'yt123'
    assert results[0]['status'] == 'dry_run'


def test_upload_missing_captions_resolves_relative_roots_against_base_path(monkeypatch, tmp_path):
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

    assert results[0]['caption_path'] == str(caption)
    assert results[0]['video_id'] == 'yt123'
    assert results[0]['status'] == 'dry_run'
