import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from recorder.bililive.journal import JsonlJournal
from recorder.bililive.media import MediaProbeRetryableError
from recorder.bililive.models import (
    ClassifiedMedia,
    JournalReplay,
    MediaInfo,
)
from recorder.bililive.runner import BililivePublishRunner
from recorder.danmaku.bilibili.bililive_xml import BililiveCaptionArtifact
from recorder.publishing.youtube import PublishResult, PublishStatus


NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)
ROOM_ID = 1829181560


class RecordingJournal:
    def __init__(self, path, events=None):
        self.inner = JsonlJournal(path)
        self.path = self.inner.path
        self.events = events if events is not None else []

    def append(self, event, **fields):
        self.events.append(('journal', event))
        self.inner.append(event, **fields)

    def replay(self):
        return self.inner.replay()


class FakePublisher:
    def __init__(self, results, events=None):
        self.results = list(results)
        self.events = events if events is not None else []
        self.calls = []

    def publish_video(self, **kwargs):
        callback = kwargs.get('before_video_upload')
        if callback is not None and kwargs['checkpoint'].video_id is None:
            callback('Generated title', 'description-fingerprint')
        self.events.append(('publisher', 'publish_video'))
        self.calls.append(kwargs)
        return self.results.pop(0)


class FailIfCalledPublisher:
    def publish_video(self, **kwargs):
        raise AssertionError(f'publisher must not be called: {kwargs}')


class SimulatedProcessCrash(BaseException):
    pass


def publish_result(status=PublishStatus.COMPLETE, **overrides):
    values = {
        'status': status,
        'video_id': 'yt123',
        'video_uploaded': True,
        'caption_uploaded': False,
        'playlist_inserted': True,
        'youtube_processed': True,
        'description_fingerprint': 'description-fingerprint',
        'caption_status': 'not_requested',
    }
    values.update(overrides)
    return PublishResult(**values)


def ready_media(tmp_path, name='recording.flv', fingerprint='fp1', start=NOW):
    path = tmp_path / name
    if not path.exists():
        path.write_bytes(b'original-flv')
    stat_result = path.stat()
    return ClassifiedMedia(
        media=MediaInfo(
            path=path.resolve(),
            xml_path=path.with_suffix('.xml').resolve(),
            size=stat_result.st_size,
            mtime_ns=stat_result.st_mtime_ns,
            start_time=start,
            stream_title='Stream title',
            duration=3600.25,
            has_video=True,
            has_audio=True,
            fingerprint=fingerprint,
        ),
        status='ready',
        reason='ready',
    )


def append_ready(journal, classified, manifest_id='session-1'):
    media = classified.media
    journal.append(
        'file_ready',
        fingerprint=media.fingerprint,
        manifest_id=manifest_id,
        file=str(media.path),
        xml_file=str(media.xml_path),
        title=media.stream_title,
        start_time=media.start_time.isoformat(),
        duration=media.duration,
        caption_status='not_requested',
    )


def append_manifest(journal, manifest_id, classified, settled_at=NOW):
    media = classified.media
    snapshot = {str(media.path): (media.size, media.mtime_ns)}
    if media.xml_path.exists():
        xml_stat = media.xml_path.stat()
        snapshot[str(media.xml_path)] = (xml_stat.st_size, xml_stat.st_mtime_ns)
    journal.append(
        'session_manifest_ready',
        manifest_id=manifest_id,
        room_id=ROOM_ID,
        started_at=(settled_at - timedelta(hours=1)).isoformat(),
        settled_at=settled_at.isoformat(),
        flv_paths=(str(media.path),),
        snapshot=snapshot,
    )
    append_ready(journal, classified, manifest_id)


def append_unclassified_manifest(journal, manifest_id, classified, settled_at=NOW):
    media = classified.media
    journal.append(
        'session_manifest_ready',
        manifest_id=manifest_id,
        room_id=ROOM_ID,
        started_at=(settled_at - timedelta(hours=1)).isoformat(),
        settled_at=settled_at.isoformat(),
        flv_paths=(str(media.path),),
        snapshot={str(media.path): (media.size, media.mtime_ns)},
    )


def journal_events(path):
    return [json.loads(line)['event'] for line in path.read_text().splitlines()]


def test_runner_journals_upload_started_before_calling_youtube(tmp_path):
    events = []
    journal = RecordingJournal(tmp_path / 'state.jsonl', events)
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    events.clear()
    publisher = FakePublisher([publish_result()], events)
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.status == 'complete'
    assert events[:2] == [
        ('journal', 'upload_started'),
        ('publisher', 'publish_video'),
    ]
    replayed = journal.replay().files['fp1']
    assert replayed.title == 'Generated title'
    assert replayed.upload_started_at == NOW.isoformat()
    assert replayed.duration == 3600.25


def test_runner_resumes_caption_without_reupload(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Generated title',
        duration=3600.25,
        description_fingerprint='old-description',
        upload_started_at=(NOW - timedelta(minutes=3)).isoformat(),
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    publisher = FakePublisher([publish_result()])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )
    upload_started_count = journal.events.count(('journal', 'upload_started'))

    runner.publish_one(classified, caption_provider=None)

    checkpoint = publisher.calls[0]['checkpoint']
    assert checkpoint.video_id == 'yt123'
    assert checkpoint.video_uploaded is True
    assert checkpoint.description_fingerprint == 'old-description'
    assert journal.events.count(('journal', 'upload_started')) == upload_started_count


@pytest.mark.parametrize(
    ('completed_stages', 'expected_caption'),
    [
        (('video_uploaded',), False),
        (
            ('video_uploaded', 'description_updated', 'caption_uploaded'),
            True,
        ),
    ],
)
def test_crash_between_remote_stages_keeps_video_checkpoint_and_never_reuploads(
    tmp_path, completed_stages, expected_caption
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)

    class CrashingPublisher:
        def publish_video(self, **kwargs):
            kwargs['before_video_upload'](
                'Generated title', 'description-fingerprint'
            )
            callback = kwargs['on_stage_completed']
            for stage in completed_stages:
                fields = {}
                if stage == 'video_uploaded':
                    fields['video_id'] = 'yt123'
                elif stage == 'description_updated':
                    fields['description_fingerprint'] = (
                        'description-fingerprint'
                    )
                callback(stage, **fields)
            raise SimulatedProcessCrash()

    first_runner = BililivePublishRunner(
        journal=journal,
        publisher=CrashingPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    with pytest.raises(SimulatedProcessCrash):
        first_runner.publish_one(classified, caption_provider=None)

    after_crash = journal.replay().files['fp1']
    assert after_crash.video_id == 'yt123'
    assert after_crash.description_updated is (
        'description_updated' in completed_stages
    )
    assert after_crash.caption_uploaded is expected_caption

    resumed_publisher = FakePublisher([publish_result()])
    resumed_runner = BililivePublishRunner(
        journal=journal,
        publisher=resumed_publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )
    resumed_runner.publish_one(classified, caption_provider=None)

    assert resumed_publisher.calls[0]['checkpoint'].video_id == 'yt123'
    assert resumed_publisher.calls[0]['before_video_upload'] is None
    assert journal_events(journal.path).count('upload_started') == 1
    assert journal.replay().files['fp1'].description_updated is True


def test_exception_after_video_checkpoint_is_retryable_not_ambiguous(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)

    class FailAfterVideoCheckpoint:
        def publish_video(self, **kwargs):
            kwargs['before_video_upload'](
                'Generated title', 'description-fingerprint'
            )
            kwargs['on_stage_completed'](
                'video_uploaded', video_id='yt123'
            )
            raise RuntimeError('caption stage crashed')

    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailAfterVideoCheckpoint(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.status == 'retry_scheduled'
    state = journal.replay().files['fp1']
    assert state.video_id == 'yt123'
    assert state.ambiguous is False
    assert state.stage == 'publisher'


def test_unknown_remote_upload_is_ambiguous_without_retry(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    publisher = FakePublisher([
        publish_result(
            PublishStatus.RETRYABLE,
            video_id=None,
            video_uploaded=False,
            playlist_inserted=False,
            youtube_processed=False,
            error_stage='video',
            error_message='connection lost',
            remote_outcome_unknown=True,
        )
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.status == 'ambiguous'
    events = journal_events(journal.path)
    assert events[-2:] == ['upload_started', 'ambiguous']
    assert 'stage_retry_scheduled' not in events


def test_recover_ambiguous_marks_no_match_without_upload(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Generated title',
        duration=3600.25,
        description_fingerprint='old-description',
        upload_started_at=(NOW - timedelta(minutes=2)).isoformat(),
    )
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        recent_uploads=lambda: [],
    )

    result = runner.recover_ambiguous(classified)

    assert result.status == 'ambiguous'
    assert journal.replay().files['fp1'].ambiguous is True


def test_recover_ambiguous_unique_match_resumes_without_video_reupload(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Generated title',
        duration=3600.25,
        description_fingerprint='old-description',
        upload_started_at=(NOW - timedelta(minutes=2)).isoformat(),
    )
    publisher = FakePublisher([publish_result()])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        recent_uploads=lambda: [{
            'video_id': 'yt123',
            'title': 'Generated title',
            'published_at': (NOW - timedelta(minutes=1)).isoformat(),
            'duration_seconds': 3600.5,
        }],
    )

    result = runner.recover_ambiguous(classified, caption_provider=None)

    assert result.status == 'complete'
    assert publisher.calls[0]['checkpoint'].video_id == 'yt123'
    assert publisher.calls[0]['before_video_upload'] is None
    assert journal_events(journal.path).count('video_uploaded') == 1


@pytest.mark.parametrize(
    'uploads',
    [
        [
            {
                'video_id': 'yt1',
                'title': 'Generated title',
                'published_at': NOW.isoformat(),
                'duration_seconds': 3600.25,
            },
            {
                'video_id': 'yt2',
                'title': 'Generated title',
                'published_at': NOW.isoformat(),
                'duration_seconds': 3600.25,
            },
        ],
        [{
            'video_id': 'yt1',
            'title': 'Generated title',
            'published_at': NOW.isoformat(),
            'duration_seconds': None,
        }],
        [{
            'video_id': 'yt1',
            'title': 'Generated title',
            'published_at': NOW.isoformat(),
            'duration_seconds': 3601.251,
        }],
    ],
)
def test_recover_ambiguous_requires_one_precise_match(tmp_path, uploads):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Generated title',
        duration=3600.25,
        upload_started_at=(NOW - timedelta(minutes=2)).isoformat(),
    )
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        recent_uploads=lambda: uploads,
    )

    result = runner.recover_ambiguous(classified)

    assert result.status == 'ambiguous'
    assert journal.replay().files['fp1'].video_id is None


def test_recover_ambiguous_consumes_at_most_fifty_recent_uploads(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Generated title',
        duration=3600.25,
        upload_started_at=(NOW - timedelta(minutes=2)).isoformat(),
    )

    def uploads():
        for index in range(50):
            yield {
                'video_id': f'other-{index}',
                'title': 'different title',
                'published_at': NOW.isoformat(),
                'duration_seconds': 3600.25,
            }
        raise AssertionError('runner consumed more than 50 recent uploads')

    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        recent_uploads=uploads,
    )

    result = runner.recover_ambiguous(classified)

    assert result.status == 'ambiguous'


def test_run_pending_returns_to_settling_before_probe_when_manifest_changes(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    classified.media.path.write_bytes(b'changed-after-settlement')
    probe_calls = []
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        probe=lambda path: probe_calls.append(path),
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'resettle_pending'
    assert probe_calls == []
    replay = journal.replay()
    assert replay.manifests[0].completed is False
    assert replay.manifests[0].invalidated is True
    assert replay.manifests[0].replacement_manifest_id is None
    assert len(replay.pending_resettles) == 1

    second = runner.run_pending_once(replay)

    assert second is None
    assert journal_events(journal.path).count('session_manifest_changed') == 1


def test_changed_manifest_does_not_block_unrelated_due_manifest(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    changed = ready_media(
        tmp_path, 'changed.flv', 'changed', NOW - timedelta(hours=2)
    )
    due = ready_media(tmp_path, 'due.flv', 'due', NOW - timedelta(hours=1))
    append_manifest(
        journal, 'changed-session', changed, NOW - timedelta(hours=1)
    )
    append_manifest(journal, 'due-session', due, NOW)
    changed.media.path.write_bytes(b'changed-after-freeze')
    publisher = FakePublisher([publish_result(video_id='yt-due')])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.fingerprint == 'due'
    assert publisher.calls[0]['video_path'] == due.media.path
    replay = journal.replay()
    assert replay.manifests[0].invalidated is True
    assert [
        item.source_manifest_id for item in replay.pending_resettles
    ] == ['changed-session']


def test_probe_retryable_manifest_does_not_block_unrelated_due_manifest(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    deferred = ready_media(
        tmp_path, 'deferred.flv', 'deferred', NOW - timedelta(hours=2)
    )
    due = ready_media(tmp_path, 'due.flv', 'due', NOW - timedelta(hours=1))
    append_unclassified_manifest(
        journal, 'deferred-session', deferred, NOW - timedelta(hours=1)
    )
    append_manifest(journal, 'due-session', due, NOW)

    def probe(path):
        if str(path) == str(deferred.media.path):
            raise MediaProbeRetryableError('storage busy')
        raise AssertionError(f'unexpected probe: {path}')

    publisher = FakePublisher([publish_result(video_id='yt-due')])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        probe=probe,
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.fingerprint == 'due'
    assert publisher.calls[0]['video_path'] == due.media.path


def test_run_pending_retries_only_declared_probe_failures(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_unclassified_manifest(journal, 'session-1', classified)
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        probe=lambda path: (_ for _ in ()).throw(
            MediaProbeRetryableError('storage busy')
        ),
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'retryable'
    assert result.message == 'storage busy'


def test_run_pending_does_not_hide_classifier_contract_errors(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_unclassified_manifest(journal, 'session-1', classified)
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        probe=lambda path: classified.media,
        classifier=lambda media: (_ for _ in ()).throw(
            ValueError('invalid classifier result')
        ),
    )

    with pytest.raises(ValueError, match='invalid classifier result'):
        runner.run_pending_once(journal.replay())


def test_run_pending_does_not_let_future_caption_retry_starve_later_video(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    old = ready_media(tmp_path, 'old.flv', 'old', NOW - timedelta(hours=2))
    new = ready_media(tmp_path, 'new.flv', 'new', NOW - timedelta(hours=1))
    append_manifest(journal, 'old-session', old, NOW - timedelta(hours=1))
    journal.append('video_uploaded', fingerprint='old', video_id='yt-old')
    journal.append(
        'caption_status', fingerprint='old', caption_status='missing'
    )
    journal.append(
        'stage_retry_scheduled',
        fingerprint='old',
        stage='caption',
        status='retryable',
        retry_at=(NOW + timedelta(hours=1)).isoformat(),
        attempt=1,
    )
    append_manifest(journal, 'new-session', new, NOW)
    publisher = FakePublisher([
        publish_result(video_id='yt-new', caption_status='not_requested')
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.fingerprint == 'new'
    assert publisher.calls[0]['video_path'] == new.media.path


def test_due_candidates_are_ordered_by_manifest_settlement_before_stage(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    old = ready_media(tmp_path, 'old.flv', 'old', NOW - timedelta(hours=2))
    new = ready_media(tmp_path, 'new.flv', 'new', NOW - timedelta(hours=3))
    append_manifest(journal, 'old-session', old, NOW - timedelta(hours=1))
    journal.append('video_uploaded', fingerprint='old', video_id='yt-old')
    journal.append(
        'caption_status', fingerprint='old', caption_status='missing'
    )
    journal.append(
        'stage_retry_scheduled',
        fingerprint='old',
        stage='caption',
        status='retryable',
        retry_at=(NOW - timedelta(seconds=1)).isoformat(),
        attempt=1,
    )
    append_manifest(journal, 'new-session', new, NOW)
    publisher = FakePublisher([publish_result(video_id='yt-old')])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.fingerprint == 'old'
    assert publisher.calls[0]['video_path'] == old.media.path


def test_publish_session_accepts_classifier_mapping_and_runs_strictly_in_order(
    tmp_path,
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    later = ready_media(tmp_path, 'later.flv', 'later', NOW)
    earlier = ready_media(
        tmp_path, 'earlier.flv', 'earlier', NOW - timedelta(hours=1)
    )
    publisher = FakePublisher([
        publish_result(video_id='yt-earlier'),
        publish_result(video_id='yt-later'),
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=None,
    )

    results = runner.publish_session({
        later.media.fingerprint: later,
        earlier.media.fingerprint: earlier,
    })

    assert [call['video_path'] for call in publisher.calls] == [
        earlier.media.path, later.media.path
    ]
    assert [result.fingerprint for result in results] == ['earlier', 'later']


def test_publish_one_never_mutates_source_flv_or_xml(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i><d p="1">hello</d></i>')
    append_ready(journal, classified)
    before = {
        path: (path.stat().st_ino, path.stat().st_size, path.stat().st_mtime_ns, path.read_bytes())
        for path in (classified.media.path, classified.media.xml_path)
    }
    publisher = FakePublisher([
        publish_result(caption_uploaded=True, caption_status='uploaded')
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    runner.publish_one(classified, caption_provider=lambda *args: BililiveCaptionArtifact(
        path=None, status='missing'
    ))

    after = {
        path: (path.stat().st_ino, path.stat().st_size, path.stat().st_mtime_ns, path.read_bytes())
        for path in (classified.media.path, classified.media.xml_path)
    }
    assert after == before


def test_later_valid_xml_backfills_caption_without_reupload(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    publisher = FakePublisher([
        publish_result(caption_status='missing'),
        publish_result(
            caption_uploaded=True,
            caption_status='uploaded',
            description_fingerprint='with-highlights',
        ),
    ])
    current_time = [NOW]
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: current_time[0],
    )

    first = runner.publish_one(
        classified,
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=None, status='missing'
        ),
    )
    current_time[0] = NOW + timedelta(minutes=5, seconds=1)
    caption_path = tmp_path / 'state' / 'generated.vtt'
    caption_path.parent.mkdir(parents=True, exist_ok=True)
    caption_path.write_text('WEBVTT\n\n')
    second = runner.publish_one(
        classified,
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=caption_path,
            highlights='Highlights\n00:00 Start',
        ),
    )

    assert first.status == 'retry_scheduled'
    assert first.retry_at == NOW + timedelta(minutes=5)
    assert second.status == 'complete'
    assert publisher.calls[1]['checkpoint'].video_id == 'yt123'
    assert publisher.calls[1]['checkpoint'].description_fingerprint == (
        'description-fingerprint'
    )
    assert publisher.calls[1]['before_video_upload'] is None
    assert journal_events(journal.path).count('upload_started') == 1
    state = journal.replay().files['fp1']
    assert state.caption_uploaded is True
    assert state.description_fingerprint == 'with-highlights'


@pytest.mark.parametrize(
    ('status', 'expected_delay'),
    [
        (PublishStatus.RETRYABLE, 5 * 60),
        (PublishStatus.QUOTA_EXCEEDED, 6 * 60 * 60),
    ],
)
def test_conclusive_video_failure_records_rejection_before_retry(
    tmp_path, status, expected_delay
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    publisher = FakePublisher([
        publish_result(
            status,
            video_id=None,
            video_uploaded=False,
            playlist_inserted=False,
            youtube_processed=False,
            error_stage='video',
            error_message='not accepted',
            remote_outcome_unknown=False,
        )
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.status == 'retry_scheduled'
    assert result.retry_at == NOW + timedelta(seconds=expected_delay)
    assert journal_events(journal.path)[-3:] == [
        'upload_started',
        'video_upload_rejected',
        'stage_retry_scheduled',
    ]


def test_conclusive_fatal_video_failure_records_rejection_before_fatal(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    publisher = FakePublisher([
        publish_result(
            PublishStatus.FATAL,
            video_id=None,
            video_uploaded=False,
            playlist_inserted=False,
            youtube_processed=False,
            error_stage='video',
            error_message='invalid credentials',
        )
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.status == 'fatal'
    assert journal_events(journal.path)[-3:] == [
        'upload_started', 'video_upload_rejected', 'fatal'
    ]


def test_retry_backoff_uses_persisted_attempt_and_caps_at_six_hours(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'stage_retry_scheduled',
        fingerprint='fp1',
        stage='video',
        status='retryable',
        retry_at=(NOW - timedelta(seconds=1)).isoformat(),
        attempt=8,
    )
    publisher = FakePublisher([
        publish_result(
            PublishStatus.RETRYABLE,
            video_id=None,
            video_uploaded=False,
            playlist_inserted=False,
            youtube_processed=False,
            error_stage='video',
            error_message='journal temporarily unavailable',
        )
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.retry_at == NOW + timedelta(hours=6)
    assert journal.replay().files['fp1'].attempt == 9


def test_replayed_rejected_upload_retains_original_stream_title(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    first_publisher = FakePublisher([
        publish_result(
            PublishStatus.RETRYABLE,
            video_id=None,
            video_uploaded=False,
            playlist_inserted=False,
            youtube_processed=False,
            error_stage='video',
            error_message='rate limited before acceptance',
        )
    ])
    first_runner = BililivePublishRunner(
        journal=journal,
        publisher=first_publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )
    first_runner.publish_one(classified, caption_provider=None)

    retry_time = NOW + timedelta(minutes=5, seconds=1)
    second_publisher = FakePublisher([publish_result()])
    second_runner = BililivePublishRunner(
        journal=journal,
        publisher=second_publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: retry_time,
    )

    second_runner.run_pending_once(journal.replay())

    assert second_publisher.calls[0]['stream_title'] == 'Stream title'


def test_retry_attempt_resets_when_publication_advances_to_processing(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Generated title',
        duration=3600.25,
        upload_started_at=(NOW - timedelta(minutes=1)).isoformat(),
        attempt=8,
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    publisher = FakePublisher([
        publish_result(
            PublishStatus.PENDING,
            youtube_processed=False,
            error_stage=None,
            error_message=None,
        )
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.retry_at == NOW + timedelta(minutes=5)
    state = journal.replay().files['fp1']
    assert state.stage == 'processing'
    assert state.attempt == 1


def test_source_change_during_caption_generation_prevents_api_call(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i/>')
    append_ready(journal, classified)

    def mutate_source(xml_path, output_path, start, duration):
        classified.media.path.write_bytes(b'mutated-during-caption')
        return BililiveCaptionArtifact(path=None, status='missing')

    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(classified, caption_provider=mutate_source)

    assert result.status == 'settling'
    assert 'FLV identity changed' in result.message
    assert 'upload_started' not in journal_events(journal.path)


def test_frozen_xml_change_prevents_caption_or_api_work(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i/>')
    append_manifest(journal, 'session-1', classified)
    classified.media.xml_path.write_text('<i><d p="1">new</d></i>')
    caption_calls = []
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'resettle_pending'
    assert caption_calls == []
    assert journal.replay().manifests[0].changed_paths == (
        str(classified.media.xml_path),
    )


def test_new_backfill_xml_must_remain_stable_during_caption_generation(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    classified.media.xml_path.write_text('<i/>')

    def mutate_new_xml(xml_path, output_path, start, duration):
        xml_path.write_text('<i><d p="1">changed</d></i>')
        return BililiveCaptionArtifact(path=None, status='missing')

    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=mutate_new_xml,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'resettle_pending'
    assert 'XML identity changed' in result.message
    assert journal.replay().manifests[0].changed_paths == (
        str(classified.media.xml_path),
    )


def test_success_journals_each_completed_remote_stage_separately(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    publisher = FakePublisher([
        publish_result(caption_uploaded=True, caption_status='uploaded')
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    runner.publish_one(classified, caption_provider=None)

    events = journal_events(journal.path)
    remote_stages = [event for event in events if event in {
        'upload_started',
        'video_uploaded',
        'description_updated',
        'caption_uploaded',
        'playlist_inserted',
        'youtube_processed',
    }]
    assert remote_stages == [
        'upload_started',
        'video_uploaded',
        'description_updated',
        'caption_uploaded',
        'playlist_inserted',
        'youtube_processed',
    ]


def test_run_pending_completes_manifest_only_after_requested_stages(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    publisher = FakePublisher([publish_result()])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    assert journal.replay().manifests[0].completed is True
    assert journal_events(journal.path)[-1] == 'session_manifest_completed'


def test_missing_caption_keeps_manifest_open_without_blocking_video_stages(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    publisher = FakePublisher([publish_result(caption_status='missing')])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'retry_scheduled'
    assert result.retry_at == NOW + timedelta(minutes=5)
    state = journal.replay().files['fp1']
    assert state.video_id == 'yt123'
    assert state.youtube_processed is True
    assert state.stage == 'caption'
    assert journal.replay().manifests[0].completed is False


def test_repeated_invalid_xml_retry_does_not_spam_caption_status(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_ready(journal, classified)
    publisher = FakePublisher([
        publish_result(caption_status='invalid'),
        publish_result(caption_status='invalid'),
    ])
    current_time = [NOW]
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: current_time[0],
    )

    invalid_caption = lambda *args: BililiveCaptionArtifact(
        path=None, status='invalid', error_message='malformed XML'
    )
    first = runner.publish_one(classified, caption_provider=invalid_caption)
    current_time[0] = first.retry_at + timedelta(seconds=1)
    runner.publish_one(classified, caption_provider=invalid_caption)

    assert journal_events(journal.path).count('caption_status') == 1
    state = journal.replay().files['fp1']
    assert state.stage == 'caption'
    assert state.attempt == 2
    assert state.error_message == 'malformed XML'


def test_run_pending_accepts_public_immutable_replay_type_annotation():
    assert BililivePublishRunner.run_pending_once.__annotations__['replay'] is JournalReplay
