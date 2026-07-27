import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from recorder.bililive.cleanup import StateAwareCleanup
from recorder.bililive.journal import JsonlJournal
from recorder.bililive.media import MediaProbeRetryableError
from recorder.bililive.models import (
    ClassifiedMedia,
    JournalFileState,
    JournalReplay,
    JournalSessionState,
    MediaInfo,
    RoomState,
    SessionState,
)
from recorder.bililive.monitor import BililiveSessionMonitor
from recorder.bililive.runner import BililivePublishRunner
from recorder.danmaku.bilibili.bililive_xml import BililiveCaptionArtifact
from recorder.publishing.youtube import (
    PublishResult,
    PublishStatus,
    YoutubePublishService,
)


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
        self.config = {'source': {str(ROOM_ID): {}}}

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


def test_runner_classification_persists_source_generation_identity(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
    )

    runner._append_classification(classified, 'session-1')

    state = journal.replay().files[classified.media.fingerprint]
    assert state.source_size == classified.media.size
    assert state.source_mtime_ns == classified.media.mtime_ns


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
    classified.media.xml_path.write_text(
        '<i><d p="1">late caption</d></i>', encoding='utf8'
    )
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


def test_runner_fsyncs_caption_source_identity_before_publisher(tmp_path):
    events = []
    journal = RecordingJournal(tmp_path / 'state.jsonl', events)
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i/>', encoding='utf8')
    append_ready(journal, classified)
    caption_path = tmp_path / 'caption.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    events.clear()
    publisher = FakePublisher([
        publish_result(caption_uploaded=True, caption_status='uploaded')
    ], events)
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    runner.publish_one(
        classified,
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=caption_path
        ),
    )

    assert events.index(('journal', 'caption_source_frozen')) < events.index(
        ('publisher', 'publish_video')
    )
    xml_stat = classified.media.xml_path.stat()
    state = journal.replay().files['fp1']
    assert state.caption_source_xml_size == xml_stat.st_size
    assert state.caption_source_xml_mtime_ns == xml_stat.st_mtime_ns


def test_caption_identity_checkpoint_failure_prevents_remote_and_cleanup(
    tmp_path,
):
    class FreezeFailJournal(RecordingJournal):
        def append(self, event, **fields):
            if event == 'caption_source_frozen':
                raise SimulatedProcessCrash()
            return super().append(event, **fields)

    journal = FreezeFailJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i/>', encoding='utf8')
    append_ready(journal, classified)
    caption_path = tmp_path / 'caption.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    with pytest.raises(SimulatedProcessCrash):
        runner.publish_one(
            classified,
            caption_provider=lambda *args: BililiveCaptionArtifact(
                path=caption_path
            ),
        )

    state = journal.replay().files['fp1']
    assert state.caption_source_xml_size is None
    assert state.caption_source_xml_mtime_ns is None
    cleanup = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    )
    result = cleanup.run([state], dry_run=True)
    assert classified.media.xml_path not in result.deleted
    assert classified.media.xml_path in result.protected


def test_late_xml_identity_controls_cleanup_after_caption_upload(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    assert str(classified.media.xml_path) not in (
        journal.replay().manifests[0].snapshot
    )
    classified.media.xml_path.write_text(
        '<i><d p="1">late caption</d></i>', encoding='utf8'
    )
    caption_path = tmp_path / 'caption.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    publisher = FakePublisher([
        publish_result(caption_uploaded=True, caption_status='uploaded')
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=caption_path
        ),
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    replay = journal.replay()
    assert replay.manifests[0].completed is True
    state = replay.files['fp1']
    xml_stat = classified.media.xml_path.stat()
    assert state.caption_source_xml_size == xml_stat.st_size
    assert state.caption_source_xml_mtime_ns == xml_stat.st_mtime_ns
    cleanup = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    )
    unchanged = cleanup.run(replay.files.values(), dry_run=True)
    assert classified.media.xml_path in unchanged.deleted

    classified.media.xml_path.write_text(
        '<i><d p="1">changed after upload</d></i>', encoding='utf8'
    )
    changed = cleanup.run(journal.replay().files.values(), dry_run=True)
    assert classified.media.xml_path not in changed.deleted
    assert classified.media.xml_path in changed.protected


def test_runner_never_overwrites_changed_caption_identity_to_reuse_checkpoint(
    tmp_path,
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    xml_path = classified.media.xml_path
    xml_path.write_text('<i><d p="1">original</d></i>', encoding='utf8')
    append_ready(journal, classified)
    original = xml_path.stat()
    journal.append(
        'caption_source_frozen', fingerprint='fp1', xml_file=str(xml_path),
        caption_source_xml_size=original.st_size,
        caption_source_xml_mtime_ns=original.st_mtime_ns,
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append('caption_uploaded', fingerprint='fp1')
    xml_path.write_text(
        '<i><d p="1">changed after remote caption</d></i>', encoding='utf8'
    )
    caption_path = tmp_path / 'caption.vtt'
    caption_path.write_text('WEBVTT\n\n', encoding='utf8')
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
    )

    result = runner.publish_one(
        classified,
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=caption_path
        ),
    )

    assert result.status == 'settling'
    assert 'durable XML identity changed' in result.message
    state = journal.replay().files['fp1']
    assert state.caption_source_xml_size == original.st_size
    assert state.caption_source_xml_mtime_ns == original.st_mtime_ns


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


@pytest.mark.parametrize('source_config', [{}, {'playlist_id': ''}])
def test_run_pending_completes_manifest_only_after_requested_stages(
    tmp_path, source_config
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    publisher = FakePublisher([publish_result()])
    publisher.config = {'source': {str(ROOM_ID): source_config}}
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


def test_selection_and_completion_share_one_state_index_per_replay(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'description_updated',
        fingerprint='fp1',
        description_fingerprint='description-fingerprint',
    )
    journal.append('youtube_processed', fingerprint='fp1')

    class CountingRunner(BililivePublishRunner):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.index_calls = 0

        def _file_state_index(self, replay):
            self.index_calls += 1
            return super()._file_state_index(replay)

    runner = CountingRunner(
        journal=journal,
        publisher=FakePublisher([]),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    assert runner.index_calls == 1


def test_state_index_rejects_duplicate_manifest_file_bindings():
    replay = JournalReplay(
        files={
            'fp-first': JournalFileState(
                fingerprint='fp-first',
                event='file_ready',
                manifest_id='session-1',
                file='/recording/video.flv',
            ),
            'fp-second': JournalFileState(
                fingerprint='fp-second',
                event='file_ready',
                manifest_id='session-1',
                file='/recording/video.flv',
            ),
        },
        manifests=(),
        session=JournalSessionState(
            state=SessionState.WAITING,
            room_id=ROOM_ID,
            session_id=None,
            session_paths=(),
            snapshot={},
            quiet_since=None,
            started_at=None,
        ),
        initialized=True,
    )

    with pytest.raises(ValueError, match='duplicate manifest/file binding'):
        BililivePublishRunner._file_state_index(replay)


@pytest.mark.parametrize(
    'invalid_config',
    [
        None,
        {},
        {'source': []},
        {'source': {}},
        {'source': {str(ROOM_ID): []}},
    ],
    ids=[
        'missing-config',
        'missing-source',
        'bad-source',
        'missing-room',
        'bad-room',
    ],
)
def test_invalid_playlist_config_cannot_complete_processed_manifest(
    tmp_path, invalid_config
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    append_manifest(journal, 'session-1', classified)
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'description_updated',
        fingerprint='fp1',
        description_fingerprint='description-fingerprint',
    )
    journal.append('youtube_processed', fingerprint='fp1')

    class ConfigFatalPublisher:
        def __init__(self):
            self.config = invalid_config
            self.calls = 0

        def publish_video(self, **kwargs):
            self.calls += 1
            return publish_result(
                PublishStatus.FATAL,
                playlist_inserted=False,
                error_stage='config',
                error_message='invalid source configuration',
            )

    publisher = ConfigFatalPublisher()
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'fatal'
    assert publisher.calls == 1
    assert journal.replay().manifests[0].completed is False


@pytest.mark.parametrize(
    'mutation_stage', ['video_uploaded', 'youtube_processed']
)
def test_post_remote_source_change_preserves_checkpoints_and_resettles(
    tmp_path, mutation_stage
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i/>')
    append_manifest(journal, 'session-1', classified)

    class MutatingPublisher:
        config = {'source': {str(ROOM_ID): {}}}

        def __init__(self):
            self.calls = 0

        def publish_video(self, **kwargs):
            self.calls += 1
            kwargs['before_video_upload'](
                'Generated title', 'description-fingerprint'
            )
            callback = kwargs['on_stage_completed']
            for stage, fields in (
                ('video_uploaded', {'video_id': 'yt123'}),
                ('description_updated', {
                    'description_fingerprint': 'description-fingerprint'
                }),
                ('caption_uploaded', {}),
                ('playlist_inserted', {}),
                ('youtube_processed', {}),
            ):
                callback(stage, **fields)
                if stage == mutation_stage:
                    classified.media.path.write_bytes(b'changed-after-remote')
                    classified.media.xml_path.write_text('<i>changed</i>')
            return publish_result(
                caption_uploaded=True, caption_status='uploaded'
            )

    publisher = MutatingPublisher()
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW,
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'resettle_pending'
    replay = journal.replay()
    manifest = replay.manifests[0]
    state = replay.files['fp1']
    assert manifest.invalidated is True
    assert manifest.completed is False
    assert set(manifest.changed_paths) == {
        str(classified.media.path), str(classified.media.xml_path)
    }
    assert state.video_id == 'yt123'
    assert state.description_updated is True
    assert state.caption_uploaded is True
    assert state.playlist_inserted is True
    assert state.youtube_processed is True

    assert runner.run_pending_once(replay) is None
    assert publisher.calls == 1


def test_xml_only_replacement_reuses_video_and_backfills_caption(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    xml_path = classified.media.xml_path
    xml_path.write_text('<i/>')
    flv_identity = (
        classified.media.path.stat().st_size,
        classified.media.path.stat().st_mtime_ns,
    )
    old_xml_identity = (xml_path.stat().st_size, xml_path.stat().st_mtime_ns)
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=ROOM_ID,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={
            str(classified.media.path): flv_identity,
            str(xml_path): old_xml_identity,
        },
        quiet_since=None,
        started_at=None,
    )
    append_manifest(journal, 'old-session', classified, NOW)
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'description_updated',
        fingerprint='fp1',
        description_fingerprint='old-description',
    )
    journal.append(
        'caption_status', fingerprint='fp1', caption_status='uploaded'
    )
    journal.append(
        'caption_uploaded', fingerprint='fp1', caption_track_id='track-1'
    )
    journal.append('playlist_inserted', fingerprint='fp1')
    journal.append('youtube_processed', fingerprint='fp1')

    xml_path.write_text('<i><d p="1">new</d></i>')
    changed_xml_identity = (
        xml_path.stat().st_size,
        xml_path.stat().st_mtime_ns,
    )
    invalidator = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=5),
    )

    invalidated = invalidator.run_pending_once(journal.replay())
    assert invalidated.status == 'resettle_pending'

    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=ROOM_ID,
        id_factory=lambda: 'replacement-session',
    )
    current = {
        str(classified.media.path): flv_identity,
        str(xml_path): changed_xml_identity,
    }
    claimed = monitor.observe(
        NOW + timedelta(minutes=10), RoomState(False, False), current
    )
    ready = monitor.observe(
        NOW + timedelta(minutes=40), RoomState(False, False), current
    )
    assert claimed.state is SessionState.SETTLING
    assert ready.state is SessionState.READY

    caption_path = tmp_path / 'caption.vtt'
    caption_path.write_text('WEBVTT\n\n')
    publisher = FakePublisher([
        publish_result(
            caption_uploaded=True,
            caption_track_id='track-1',
            caption_status='uploaded',
            description_fingerprint='new-description',
        )
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=41),
        probe=lambda path: classified.media,
        classifier=lambda media: {'fp1': ClassifiedMedia(
            media=media[0], status='ready', reason='ready'
        )},
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=caption_path, status='ready'
        ),
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    assert len(publisher.calls) == 1
    checkpoint = publisher.calls[0]['checkpoint']
    assert checkpoint.video_id == 'yt123'
    assert checkpoint.caption_uploaded is False
    assert checkpoint.caption_refresh_required is True
    assert checkpoint.caption_track_id == 'track-1'
    assert checkpoint.playlist_inserted is True
    assert checkpoint.youtube_processed is True
    assert checkpoint.description_fingerprint == 'old-description'
    assert publisher.calls[0]['before_video_upload'] is None
    replay = journal.replay()
    state = replay.files['fp1']
    assert state.manifest_id == 'replacement-session'
    assert state.video_id == 'yt123'
    assert state.caption_uploaded is True
    assert state.caption_refresh_required is False
    assert state.caption_track_id == 'track-1'
    old, replacement = replay.manifests
    assert old.invalidated is True
    assert old.replacement_manifest_id == replacement.manifest_id
    assert replacement.completed is True


def test_replacement_reconciles_unresolved_upload_without_reupload(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    classified.media.xml_path.write_text('<i/>')

    def identity(path):
        stat_result = path.stat()
        return stat_result.st_size, stat_result.st_mtime_ns

    snapshot = {
        str(classified.media.path): identity(classified.media.path),
        str(classified.media.xml_path): identity(classified.media.xml_path),
    }
    journal.append('initialized')
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='old-session', room_id=ROOM_ID,
        started_at=(NOW - timedelta(hours=1)).isoformat(),
        settled_at=NOW.isoformat(),
        flv_paths=(str(classified.media.path),), snapshot=snapshot,
    )
    append_ready(journal, classified, 'old-session')
    journal.append(
        'upload_started', fingerprint='fp1', file=str(classified.media.path),
        xml_file=str(classified.media.xml_path), title='Generated title',
        duration=classified.media.duration,
        description_fingerprint='description-fingerprint',
        upload_started_at=(NOW + timedelta(minutes=1)).isoformat(), attempt=1,
    )
    classified.media.xml_path.write_text('<i><d>changed</d></i>')
    replacement_snapshot = dict(snapshot)
    replacement_snapshot[str(classified.media.xml_path)] = identity(
        classified.media.xml_path
    )
    journal.append(
        'session_manifest_changed', manifest_id='old-session',
        detected_at=(NOW + timedelta(minutes=5)).isoformat(),
        reason='XML changed', changed_paths=(str(classified.media.xml_path),),
    )
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=replacement_snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_resettle_started', source_manifest_id='old-session',
        replacement_manifest_id='replacement-session', room_id=ROOM_ID,
        state='settling', session_paths=tuple(replacement_snapshot),
        snapshot=replacement_snapshot,
        quiet_since=(NOW + timedelta(minutes=10)).isoformat(),
        started_at=(NOW - timedelta(hours=1)).isoformat(),
    )
    journal.append(
        'session_manifest_ready', manifest_id='replacement-session',
        room_id=ROOM_ID,
        started_at=(NOW - timedelta(hours=1)).isoformat(),
        settled_at=(NOW + timedelta(minutes=40)).isoformat(),
        flv_paths=(str(classified.media.path),), snapshot=replacement_snapshot,
    )
    publisher = FakePublisher([publish_result(video_id='yt-reconciled')])
    recent_calls = []
    runner = BililivePublishRunner(
        journal=journal, publisher=publisher, room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=41),
        recent_uploads=lambda: recent_calls.append(True) or [{
            'video_id': 'yt-reconciled', 'title': 'Generated title',
            'published_at': (NOW + timedelta(minutes=2)).isoformat(),
            'duration_seconds': classified.media.duration,
        }],
        probe=lambda path: classified.media,
        classifier=lambda media: {'fp1': ClassifiedMedia(
            media=media[0], status='ready', reason='ready'
        )},
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    assert recent_calls == [True]
    assert len(publisher.calls) == 1
    assert publisher.calls[0]['checkpoint'].video_id == 'yt-reconciled'
    assert publisher.calls[0]['checkpoint'].caption_refresh_required is False
    assert publisher.calls[0]['before_video_upload'] is None
    assert journal_events(journal.path).count('upload_started') == 1
    assert journal.replay().files['fp1'].video_id == 'yt-reconciled'


def test_consecutive_xml_replacements_update_latest_caption_after_replay(
    tmp_path,
):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path)
    xml_path = classified.media.xml_path
    xml_path.write_text('<i/>')

    def identity(path):
        stat_result = path.stat()
        return stat_result.st_size, stat_result.st_mtime_ns

    video = str(classified.media.path)
    xml = str(xml_path)
    started_at = (NOW - timedelta(hours=1)).isoformat()
    snapshots = [{
        video: identity(classified.media.path),
        xml: identity(xml_path),
    }]
    journal.append('initialized')
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=snapshots[0], quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='manifest-1', room_id=ROOM_ID,
        started_at=started_at, settled_at=NOW.isoformat(),
        flv_paths=(video,), snapshot=snapshots[0],
    )
    append_ready(journal, classified, 'manifest-1')
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append('caption_uploaded', fingerprint='fp1')
    journal.append('youtube_processed', fingerprint='fp1')

    xml_path.write_text('<i><d>middle</d></i>')
    snapshots.append({
        video: identity(classified.media.path), xml: identity(xml_path),
    })
    journal.append(
        'session_manifest_changed', manifest_id='manifest-1',
        detected_at=(NOW + timedelta(minutes=5)).isoformat(),
        reason='middle XML', changed_paths=(xml,),
    )
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=snapshots[1], quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_resettle_started', source_manifest_id='manifest-1',
        replacement_manifest_id='manifest-2', room_id=ROOM_ID,
        state='settling', session_paths=(video, xml), snapshot=snapshots[1],
        quiet_since=(NOW + timedelta(minutes=10)).isoformat(),
        started_at=started_at,
    )
    journal.append(
        'session_manifest_ready', manifest_id='manifest-2', room_id=ROOM_ID,
        started_at=started_at,
        settled_at=(NOW + timedelta(minutes=40)).isoformat(),
        flv_paths=(video,), snapshot=snapshots[1],
    )
    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='manifest-2',
        file=video, xml_file=xml, start_time=classified.media.start_time.isoformat(),
        duration=classified.media.duration, caption_status='pending',
    )
    after_restart = JsonlJournal(journal.path).replay().files['fp1']
    assert after_restart.caption_refresh_required is True
    assert after_restart.caption_track_id is None

    xml_path.write_text('<i><d>latest</d></i>')
    snapshots.append({
        video: identity(classified.media.path), xml: identity(xml_path),
    })
    journal.append(
        'session_manifest_changed', manifest_id='manifest-2',
        detected_at=(NOW + timedelta(minutes=45)).isoformat(),
        reason='latest XML', changed_paths=(xml,),
    )
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=snapshots[2], quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_resettle_started', source_manifest_id='manifest-2',
        replacement_manifest_id='manifest-3', room_id=ROOM_ID,
        state='settling', session_paths=(video, xml), snapshot=snapshots[2],
        quiet_since=(NOW + timedelta(minutes=50)).isoformat(),
        started_at=started_at,
    )
    journal.append(
        'session_manifest_ready', manifest_id='manifest-3', room_id=ROOM_ID,
        started_at=started_at,
        settled_at=(NOW + timedelta(minutes=80)).isoformat(),
        flv_paths=(video,), snapshot=snapshots[2],
    )

    caption_path = tmp_path / 'latest.vtt'
    caption_path.write_text('WEBVTT\n\nlatest caption\n')

    class TrackAwareYoutube:
        def __init__(self):
            self.caption_updates = []

        def matching_caption_track_ids(self, video_id, caption_name):
            return ('track-1',)

        def update_caption_result(self, track_id, path, **kwargs):
            self.caption_updates.append((track_id, Path(path).read_text()))
            return 'uploaded'

        def update(self, *args, **kwargs):
            return True

    youtube = TrackAwareYoutube()
    publisher = YoutubePublishService(youtube, {
        'source': {str(ROOM_ID): {
            'title': 'Live {datetime}', 'description': 'Base',
        }},
    })
    runner = BililivePublishRunner(
        journal=journal, publisher=publisher, room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=81),
        probe=lambda path: classified.media,
        classifier=lambda media: {'fp1': ClassifiedMedia(
            media=media[0], status='ready', reason='ready'
        )},
        caption_provider=lambda *args: BililiveCaptionArtifact(
            path=caption_path, status='ready', temporary=False
        ),
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    assert youtube.caption_updates == [(
        'track-1', 'WEBVTT\n\nlatest caption\n'
    )]
    final = JsonlJournal(journal.path).replay().files['fp1']
    assert final.caption_refresh_required is False
    assert final.caption_uploaded is True
    assert final.caption_track_id == 'track-1'


def test_ignored_fragment_reclassification_does_not_block_ready_peer(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    ignored_ready = ready_media(tmp_path, 'ignored.flv', 'fp-ignored')
    peer = ready_media(tmp_path, 'peer.flv', 'fp-peer')
    ignored_ready.media.xml_path.write_text('<i/>')
    peer.media.xml_path.write_text('<i/>')

    def identity(path):
        stat_result = path.stat()
        return stat_result.st_size, stat_result.st_mtime_ns

    old_snapshot = {
        str(item): identity(item)
        for item in (
            ignored_ready.media.path, ignored_ready.media.xml_path,
            peer.media.path, peer.media.xml_path,
        )
    }
    journal.append('initialized')
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=old_snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='old-session', room_id=ROOM_ID,
        started_at=(NOW - timedelta(hours=1)).isoformat(),
        settled_at=NOW.isoformat(),
        flv_paths=(str(ignored_ready.media.path), str(peer.media.path)),
        snapshot=old_snapshot,
    )
    journal.append(
        'ignored_tiny', fingerprint='fp-ignored', manifest_id='old-session',
        file=str(ignored_ready.media.path),
        xml_file=str(ignored_ready.media.xml_path),
        start_time=ignored_ready.media.start_time.isoformat(),
        duration=ignored_ready.media.duration, reason='tiny',
    )
    append_ready(journal, peer, 'old-session')
    journal.append('video_uploaded', fingerprint='fp-peer', video_id='yt-peer')
    journal.append('youtube_processed', fingerprint='fp-peer')

    ignored_ready.media.xml_path.write_text('<i><d>changed</d></i>')
    replacement_snapshot = dict(old_snapshot)
    replacement_snapshot[str(ignored_ready.media.xml_path)] = identity(
        ignored_ready.media.xml_path
    )
    journal.append(
        'session_manifest_changed', manifest_id='old-session',
        detected_at=(NOW + timedelta(minutes=5)).isoformat(),
        reason='ignored XML changed',
        changed_paths=(str(ignored_ready.media.xml_path),),
    )
    journal.append(
        'session_state', room_id=ROOM_ID, state='waiting', session_id=None,
        session_paths=(), snapshot=replacement_snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_resettle_started', source_manifest_id='old-session',
        replacement_manifest_id='replacement-session', room_id=ROOM_ID,
        state='settling', session_paths=tuple(replacement_snapshot),
        snapshot=replacement_snapshot,
        quiet_since=(NOW + timedelta(minutes=10)).isoformat(),
        started_at=(NOW - timedelta(hours=1)).isoformat(),
    )
    journal.append(
        'session_manifest_ready', manifest_id='replacement-session',
        room_id=ROOM_ID,
        started_at=(NOW - timedelta(hours=1)).isoformat(),
        settled_at=(NOW + timedelta(minutes=40)).isoformat(),
        flv_paths=(str(ignored_ready.media.path), str(peer.media.path)),
        snapshot=replacement_snapshot,
    )
    reclassified_ready = ClassifiedMedia(
        media=ignored_ready.media, status='ready', reason='now ready'
    )
    media_by_path = {
        str(ignored_ready.media.path): ignored_ready.media,
        str(peer.media.path): peer.media,
    }
    publisher = FakePublisher([publish_result(video_id='yt-ignored')])
    runner = BililivePublishRunner(
        journal=journal, publisher=publisher, room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=41),
        probe=lambda path: media_by_path[str(path)],
        classifier=lambda media: {
            'fp-ignored': reclassified_ready,
            'fp-peer': ClassifiedMedia(
                media=peer.media, status='ready', reason='ready'
            ),
        },
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    replay = journal.replay()
    assert replay.files['fp-ignored'].event == 'youtube_processed'
    assert replay.files['fp-ignored'].manifest_id == 'replacement-session'
    assert replay.files['fp-ignored'].video_id == 'yt-ignored'
    assert publisher.calls[0]['checkpoint'].caption_refresh_required is False
    assert replay.files['fp-peer'].video_id == 'yt-peer'
    assert replay.files['fp-peer'].manifest_id == 'replacement-session'
    assert replay.manifests[-1].completed is True
    assert len(publisher.calls) == 1


def test_multi_segment_replacement_reuses_only_unchanged_video(tmp_path):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    a_old = ready_media(
        tmp_path, 'a.flv', 'fp-a-old', NOW - timedelta(minutes=2)
    )
    b = ready_media(tmp_path, 'b.flv', 'fp-b', NOW - timedelta(minutes=1))
    a_old.media.xml_path.write_text('<i/>')
    b.media.xml_path.write_text('<i/>')

    def identity(path):
        stat_result = path.stat()
        return stat_result.st_size, stat_result.st_mtime_ns

    old_snapshot = {
        str(a_old.media.path): identity(a_old.media.path),
        str(a_old.media.xml_path): identity(a_old.media.xml_path),
        str(b.media.path): identity(b.media.path),
        str(b.media.xml_path): identity(b.media.xml_path),
    }
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=ROOM_ID,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot=old_snapshot,
        quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='old-session',
        room_id=ROOM_ID,
        started_at=(NOW - timedelta(hours=1)).isoformat(),
        settled_at=NOW.isoformat(),
        flv_paths=(str(a_old.media.path), str(b.media.path)),
        snapshot=old_snapshot,
    )
    for classified, video_id in ((a_old, 'yt-a-old'), (b, 'yt-b-old')):
        append_ready(journal, classified, 'old-session')
        fingerprint = classified.media.fingerprint
        journal.append(
            'video_uploaded', fingerprint=fingerprint, video_id=video_id
        )
        journal.append(
            'description_updated',
            fingerprint=fingerprint,
            description_fingerprint=f'description-{fingerprint}',
        )
        journal.append(
            'caption_status',
            fingerprint=fingerprint,
            caption_status='uploaded',
        )
        journal.append('caption_uploaded', fingerprint=fingerprint)
        journal.append('playlist_inserted', fingerprint=fingerprint)
        journal.append('youtube_processed', fingerprint=fingerprint)

    a_old.media.path.write_bytes(b'A changed and requires a new upload')
    a_new = ready_media(
        tmp_path, 'a.flv', 'fp-a-new', a_old.media.start_time
    )
    invalidator = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=5),
    )
    assert invalidator.run_pending_once(
        journal.replay()
    ).status == 'resettle_pending'

    current = {
        str(a_new.media.path): identity(a_new.media.path),
        str(a_new.media.xml_path): identity(a_new.media.xml_path),
        str(b.media.path): identity(b.media.path),
        str(b.media.xml_path): identity(b.media.xml_path),
    }
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=ROOM_ID,
        id_factory=lambda: 'replacement-session',
    )
    monitor.observe(
        NOW + timedelta(minutes=10), RoomState(False, False), current
    )
    assert monitor.observe(
        NOW + timedelta(minutes=40), RoomState(False, False), current
    ).state is SessionState.READY

    media_by_path = {
        str(a_new.media.path): a_new.media,
        str(b.media.path): b.media,
    }
    publisher = FakePublisher([
        publish_result(video_id='yt-a-new', caption_status='not_requested')
    ])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
        clock=lambda: NOW + timedelta(minutes=41),
        probe=lambda path: media_by_path[str(path)],
        classifier=lambda media: {
            item.fingerprint: ClassifiedMedia(
                media=item, status='ready', reason='ready'
            )
            for item in media
        },
        caption_provider=None,
    )

    result = runner.run_pending_once(journal.replay())

    assert result.status == 'complete'
    assert len(publisher.calls) == 1
    assert publisher.calls[0]['video_path'] == a_new.media.path
    assert publisher.calls[0]['checkpoint'].video_id is None
    replay = journal.replay()
    assert replay.files['fp-a-old'].manifest_id == 'old-session'
    assert replay.files['fp-a-old'].video_id == 'yt-a-old'
    assert replay.files['fp-a-new'].manifest_id == 'replacement-session'
    assert replay.files['fp-a-new'].video_id == 'yt-a-new'
    assert replay.files['fp-b'].manifest_id == 'replacement-session'
    assert replay.files['fp-b'].video_id == 'yt-b-old'
    assert replay.files['fp-b'].description_fingerprint == 'description-fp-b'
    assert replay.files['fp-b'].caption_uploaded is True
    assert replay.files['fp-b'].caption_refresh_required is False
    assert replay.files['fp-b'].playlist_inserted is True
    assert replay.files['fp-b'].youtube_processed is True
    assert replay.manifests[-1].completed is True


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
