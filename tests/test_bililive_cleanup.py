from dataclasses import replace
from datetime import datetime, timezone
import os
from pathlib import Path

import pytest

import recorder.bililive.cleanup_fs as cleanup_fs_module
from recorder.bililive.cleanup import (
    DISK_CLEANUP_THRESHOLD_PERCENT,
    StateAwareCleanup,
)
from recorder.bililive.cleanup_fs import RootDirectory, stat_identity
from recorder.bililive.journal import JsonlJournal
from recorder.bililive.journal import baseline_fingerprint, file_state_checkpoint
from recorder.bililive.models import (
    JournalDeleteIntent,
    JournalFileState,
    JournalManifest,
    JournalReplay,
    JournalResettleRequest,
    JournalSessionState,
    SessionState,
)


NOW = datetime(2026, 7, 27, tzinfo=timezone.utc).isoformat()


def file_state(
    video,
    xml=None,
    *,
    fingerprint=None,
    event='file_ready',
    manifest_id=None,
    youtube_processed=False,
    caption_uploaded=False,
    video_id=None,
    durable_identity=True,
):
    video_path = Path(video)
    file_stat = (
        video_path.stat()
        if durable_identity and video_path.is_file()
        else None
    )
    if fingerprint is None:
        fingerprint = (
            baseline_fingerprint(
                video_path, file_stat.st_size, file_stat.st_mtime_ns
            )
            if event == 'baseline' and file_stat is not None
            else 'fp1'
        )
    return JournalFileState(
        fingerprint=fingerprint,
        event=event,
        manifest_id=manifest_id,
        file=str(video),
        xml_file=str(xml) if xml is not None else None,
        youtube_processed=youtube_processed,
        caption_uploaded=caption_uploaded,
        video_id=video_id,
        source_size=file_stat.st_size if file_stat is not None else None,
        source_mtime_ns=(
            file_stat.st_mtime_ns if file_stat is not None else None
        ),
    )


def session(state=SessionState.WAITING, paths=()):
    active = state in {
        SessionState.SKIP_CURRENT_SESSION,
        SessionState.RECORDING,
        SessionState.SETTLING,
        SessionState.READY,
    }
    return JournalSessionState(
        state=state,
        room_id=1829181560,
        session_id='current-session' if active else None,
        session_paths=tuple(str(path) for path in paths),
        snapshot={},
        quiet_since=NOW if active else None,
        started_at=NOW if active else None,
    )


def manifest(
    manifest_id,
    videos,
    *,
    completed=False,
    invalidated=False,
    replacement_manifest_id=None,
):
    videos = tuple(str(path) for path in videos)
    snapshot = {}
    for path in videos:
        stat_result = Path(path).stat()
        snapshot[path] = (stat_result.st_size, stat_result.st_mtime_ns)
        xml_path = Path(path).with_suffix('.xml')
        if xml_path.exists():
            xml_stat = xml_path.stat()
            snapshot[str(xml_path)] = (xml_stat.st_size, xml_stat.st_mtime_ns)
    return JournalManifest(
        manifest_id=manifest_id,
        room_id=1829181560,
        started_at=NOW,
        settled_at=NOW,
        flv_paths=videos,
        snapshot=snapshot,
        completed=completed,
        invalidated=invalidated,
        invalidated_at=NOW if invalidated else None,
        invalidation_reason='source changed' if invalidated else None,
        changed_paths=videos[:1] if invalidated else (),
        replacement_manifest_id=replacement_manifest_id,
    )


def replay(states=(), *, current_session=None, manifests=(), pending=()):
    return JournalReplay(
        files={state.fingerprint: state for state in states},
        manifests=tuple(manifests),
        session=current_session or session(),
        initialized=True,
        pending_resettles=tuple(pending),
    )


class FakeJournal:
    def __init__(self, current_replay):
        self.current_replay = current_replay
        self.events = []

    def replay(self):
        return self.current_replay

    def append(self, event, **fields):
        self.events.append((event, fields))
        return self.current_replay.journal_version


class FailOnceEventJournal(FakeJournal):
    def __init__(self, current_replay, fail_event):
        super().__init__(current_replay)
        self.fail_event = fail_event
        self.failed = False

    def append(self, event, **fields):
        version = super().append(event, **fields)
        if event == self.fail_event and not self.failed:
            self.failed = True
            raise OSError(f'{event} fsync failed')
        return version


class Usage:
    def __init__(self, *values):
        self.values = list(values)
        self.calls = []

    def __call__(self, path):
        self.calls.append(Path(path))
        if len(self.values) > 1:
            return self.values.pop(0)
        return self.values[0]


class SimulatedCleanupCrash(BaseException):
    pass


def pending_intent(state, path, quarantine_path, *, source_deleted=False):
    file_stat = path.stat()
    return JournalDeleteIntent(
        fingerprint=state.fingerprint,
        original_path=str(path),
        quarantine_path=quarantine_path,
        dev=file_stat.st_dev,
        ino=file_stat.st_ino,
        size=file_stat.st_size,
        mtime_ns=file_stat.st_mtime_ns,
        reason='disk pressure',
        source_deleted=source_deleted,
        state_checkpoint=file_state_checkpoint(state),
    )


class CrashJournal(JsonlJournal):
    def __init__(self, path, *, before=None, after=None):
        super().__init__(path)
        self.before = before
        self.after = after

    def append(self, event, **fields):
        if event == self.before:
            raise SimulatedCleanupCrash(f'before {event}')
        version = super().append(event, **fields)
        if event == self.after:
            raise SimulatedCleanupCrash(f'after {event}')
        return version


class CountingJournal(JsonlJournal):
    def __init__(self, path):
        super().__init__(path)
        self.replay_calls = 0

    def replay(self):
        self.replay_calls += 1
        return super().replay()


class SessionRaceJournal(JsonlJournal):
    def __init__(self, path, video, identity):
        super().__init__(path)
        self.video = str(video)
        self.identity = identity
        self.injected = False

    def append(self, event, **fields):
        if event == 'source_delete_intent' and not self.injected:
            self.injected = True
            super().append(
                'session_state', room_id=1829181560, state='recording',
                session_id='racing-session', session_paths=(self.video,),
                snapshot={self.video: self.identity},
                quiet_since='2026-07-27T12:00:00+00:00',
                started_at='2026-07-27T08:00:00+00:00',
            )
        return super().append(event, **fields)


class PostTransactionRaceJournal(JsonlJournal):
    def __init__(self, path, video, identity):
        super().__init__(path)
        self.video = str(video)
        self.identity = identity
        self.injected = False

    def append(self, event, **fields):
        version = super().append(event, **fields)
        if event == 'quarantine_removed' and not self.injected:
            self.injected = True
            super().append(
                'session_state', room_id=1829181560, state='recording',
                session_id='post-transaction-race',
                session_paths=(self.video,),
                snapshot={self.video: self.identity},
                quiet_since='2026-07-27T12:00:00+00:00',
                started_at='2026-07-27T08:00:00+00:00',
            )
        return version


class DirectorySyncGuardJournal(JsonlJournal):
    def __init__(self, path, phase_event, directories_synced):
        super().__init__(path)
        self.phase_event = phase_event
        self.directories_synced = directories_synced

    def append(self, event, **fields):
        if event == self.phase_event and not self.directories_synced():
            raise AssertionError(
                f'{event} advanced before namespace directories were synced'
            )
        return super().append(event, **fields)


def baseline_journal(path, video):
    file_stat = video.stat()
    fingerprint = baseline_fingerprint(
        video, file_stat.st_size, file_stat.st_mtime_ns
    )
    journal = JsonlJournal(path)
    journal.append('baseline', fingerprint=fingerprint, file=str(video))
    return journal, fingerprint


def cleanup_for(tmp_path, states, usage, **replay_fields):
    journal = FakeJournal(replay(states, **replay_fields))
    cleanup = StateAwareCleanup(journal, tmp_path, usage)
    return journal, cleanup


def test_cleanup_deletes_processed_flv_but_retains_invalid_xml(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<broken>', encoding='utf8')
    state = file_state(
        video, xml, event='youtube_processed', youtube_processed=True,
        video_id='yt123',
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(86, 84))

    result = cleanup.run([state], dry_run=False)

    assert not video.exists()
    assert xml.exists()
    assert result.deleted == (video,)
    assert result.protected == (xml,)
    assert result.disk_usage_percent == 84
    assert result.exhausted is False
    assert [event for event, _ in journal.events] == [
        'source_delete_intent', 'source_deleted', 'quarantine_removed'
    ]
    assert journal.events[0][1]['original_path'] == str(video)
    assert journal.events[1][1]['path'] == str(video)


@pytest.mark.parametrize('event', [
    'file_ready', 'upload_started', 'video_uploaded', 'ambiguous', 'unknown'
])
def test_cleanup_never_deletes_protected_video(tmp_path, event):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    state = file_state(video, event=event)
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert result.protected == (video,)
    assert result.exhausted is True
    assert journal.events == []


@pytest.mark.parametrize('event', [
    'ready',
    'file_ready',
    'upload_started',
    'video_uploaded',
    'ambiguous',
    'fatal',
    'stage_retry_scheduled',
    'video_upload_rejected',
    'unknown',
])
def test_hard_lifecycle_protection_overrides_inconsistent_completion_flags(
    tmp_path, event
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = file_state(
        video,
        xml,
        event=event,
        youtube_processed=True,
        caption_uploaded=True,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert video.exists() and xml.exists()
    assert set(result.protected) == {video, xml}
    assert journal.events == []


def test_ambiguous_flag_overrides_apparently_completed_state(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = replace(
        file_state(
            video,
            xml,
            event='youtube_processed',
            youtube_processed=True,
            caption_uploaded=True,
            video_id='yt123',
        ),
        ambiguous=True,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()
    assert journal.events == []


def test_valid_journal_sequence_ending_ambiguous_protects_completed_flags(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file=str(video), xml_file=str(xml)
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append('caption_uploaded', fingerprint='fp1')
    journal.append('youtube_processed', fingerprint='fp1')
    journal.append(
        'ambiguous', fingerprint='fp1', stage='caption',
        message='remote outcome became uncertain',
    )
    state = journal.replay().files['fp1']
    assert state.youtube_processed is True
    assert state.caption_uploaded is True
    assert state.ambiguous is True

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    ).run([state], dry_run=False)

    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()


def append_processed_video(journal, video, xml):
    file_stat = video.stat()
    journal.append(
        'file_ready', fingerprint='fp1', file=str(video), xml_file=str(xml),
        source_size=file_stat.st_size,
        source_mtime_ns=file_stat.st_mtime_ns,
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append('youtube_processed', fingerprint='fp1')


@pytest.mark.parametrize(
    ('suffix_events', 'xml_eligible'),
    [
        ((), False),
        ((('description_updated', {
            'description_fingerprint': 'description-v2',
        }),), False),
        ((('caption_status', {
            'caption_status': 'not_requested',
        }),), False),
        ((('caption_source_frozen', {}),), False),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
        ), True),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('playlist_inserted', {}),
        ), True),
        ((
            ('playlist_inserted', {}),
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
        ), True),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('description_updated', {
                'description_fingerprint': 'caption-highlights',
            }),
        ), True),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('caption_status', {'caption_status': 'uploaded'}),
        ), True),
        ((('stage_retry_scheduled', {
            'stage': 'caption', 'status': 'retryable',
            'retry_at': '2026-07-28T12:05:00+00:00', 'attempt': 1,
            'error_message': 'caption API unavailable',
        }),), False),
        ((('fatal', {
            'stage': 'caption', 'message': 'caption rejected',
        }),), False),
        ((('stage_retry_scheduled', {
            'stage': 'playlist', 'status': 'retryable',
            'retry_at': '2026-07-28T12:05:00+00:00', 'attempt': 1,
            'error_message': 'playlist API unavailable',
        }),), False),
        ((('fatal', {
            'stage': 'processing', 'message': 'processing rejected',
        }),), False),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('stage_retry_scheduled', {
                'stage': 'playlist', 'status': 'retryable',
                'retry_at': '2026-07-28T12:05:00+00:00', 'attempt': 1,
                'error_message': 'playlist API unavailable',
            }),
        ), True),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('fatal', {
                'stage': 'processing', 'message': 'processing rejected',
            }),
        ), True),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('stage_retry_scheduled', {
                'stage': 'caption', 'status': 'retryable',
                'retry_at': '2026-07-28T12:05:00+00:00', 'attempt': 1,
                'error_message': 'caption refresh unavailable',
            }),
        ), False),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('fatal', {
                'stage': 'caption', 'message': 'caption refresh rejected',
            }),
        ), False),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('caption_source_frozen', {}),
        ), True),
        ((
            ('caption_source_frozen', {}),
            ('caption_uploaded', {}),
            ('caption_source_frozen', {}),
            ('caption_status', {'caption_status': 'existing'}),
        ), True),
    ],
)
def test_processed_flv_remains_eligible_after_legitimate_non_video_events(
    tmp_path, suffix_events, xml_eligible
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    append_processed_video(journal, video, xml)
    xml_stat = xml.stat()
    for event, fields in suffix_events:
        fields = dict(fields)
        if event == 'caption_source_frozen':
            fields.update(
                xml_file=str(xml),
                caption_source_xml_size=xml_stat.st_size,
                caption_source_xml_mtime_ns=xml_stat.st_mtime_ns,
            )
        journal.append(event, fingerprint='fp1', **fields)
    state = journal.replay().files['fp1']

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    ).run([state], dry_run=True)

    assert video in result.deleted
    assert (xml in result.deleted) is xml_eligible
    assert (xml in result.protected) is (not xml_eligible)
    assert result.exhausted is False


@pytest.mark.parametrize(
    'suffix_events',
    [
        (),
        (('upload_started', {
            'title': 'title', 'duration': 60,
            'upload_started_at': '2026-07-28T12:00:00+00:00',
            'attempt': 0,
        }),),
        (('video_uploaded', {'video_id': 'yt123'}),),
        (('video_upload_rejected', {
            'stage': 'video', 'message': 'upload rejected',
        }),),
        (
            ('upload_started', {
                'title': 'title', 'duration': 60,
                'upload_started_at': '2026-07-28T12:00:00+00:00',
                'attempt': 0,
            }),
            ('ambiguous', {
                'stage': 'video', 'message': 'outcome unknown',
            }),
        ),
        (('stage_retry_scheduled', {
            'stage': 'video', 'status': 'retryable',
            'retry_at': '2026-07-28T12:05:00+00:00', 'attempt': 1,
            'error_message': 'upload unavailable',
        }),),
        (('fatal', {
            'stage': 'video', 'message': 'upload rejected',
        }),),
    ],
)
def test_real_video_stage_final_events_protect_flv_and_xml(
    tmp_path, suffix_events
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file=str(video), xml_file=str(xml)
    )
    for event, fields in suffix_events:
        journal.append(event, fingerprint='fp1', **fields)
    state = journal.replay().files['fp1']

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    ).run([state], dry_run=True)

    assert result.deleted == ()
    assert set(result.protected) == {video, xml}
    assert result.exhausted is True


@pytest.mark.parametrize(
    'event', ['ignored_invalid', 'ignored_tiny', 'ignored_invalid_tail']
)
def test_real_ignored_final_event_only_deletes_identity_bound_video(
    tmp_path, event
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    video_stat = video.stat()
    fields = {
        'fingerprint': 'fp1', 'file': str(video), 'xml_file': str(xml),
        'source_size': video_stat.st_size,
        'source_mtime_ns': video_stat.st_mtime_ns,
    }
    fields['reason'] = 'classification policy'
    journal.append(event, **fields)
    state = journal.replay().files['fp1']

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    ).run([state], dry_run=True)

    assert result.deleted == (video,)
    assert result.protected == (xml,)
    assert result.exhausted is False


def test_real_baseline_event_recomputes_each_source_identity(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    for path in (video, xml):
        path_stat = path.stat()
        journal.append(
            'baseline',
            fingerprint=baseline_fingerprint(
                path, path_stat.st_size, path_stat.st_mtime_ns
            ),
            file=str(path),
            source_size=path_stat.st_size,
            source_mtime_ns=path_stat.st_mtime_ns,
        )

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    ).run(journal.replay().files.values(), dry_run=True)

    assert set(result.deleted) == {video, xml}
    assert result.protected == ()
    assert result.exhausted is False


def test_real_baseline_flv_and_xml_each_keep_canonical_delete_owner(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    for path in (video, xml):
        path_stat = path.stat()
        journal.append(
            'baseline',
            fingerprint=baseline_fingerprint(
                path, path_stat.st_size, path_stat.st_mtime_ns
            ),
            file=str(path.parent / 'nested' / '..' / path.name),
        )
    (tmp_path / 'nested').mkdir()

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(99, 99, 84)
    ).run(journal.replay().files.values(), dry_run=False)

    assert result.deleted == (video, xml)
    assert not video.exists() and not xml.exists()
    assert journal.replay().pending_deletions == ()


@pytest.mark.parametrize(
    'state_changes',
    [
        {
            'event': 'youtube_processed',
            'youtube_processed': True,
            'caption_uploaded': True,
            'video_id': None,
        },
        {
            'event': 'youtube_processed',
            'youtube_processed': False,
            'caption_uploaded': True,
            'video_id': 'yt123',
        },
        {
            'event': 'caption_uploaded',
            'youtube_processed': False,
            'caption_uploaded': False,
            'video_id': 'yt123',
        },
        {
            'event': 'stage_retry_scheduled',
            'youtube_processed': True,
            'video_id': 'yt123',
            'stage': 'caption',
            'status': None,
            'retry_at': None,
        },
        {
            'event': 'description_updated',
            'youtube_processed': True,
            'video_id': 'yt123',
            'description_updated': True,
            'description_fingerprint': None,
        },
        {
            'event': 'caption_source_frozen',
            'youtube_processed': True,
            'video_id': 'yt123',
            'caption_source_xml_size': None,
            'caption_source_xml_mtime_ns': None,
        },
    ],
)
def test_raw_inconsistent_completion_state_is_fully_protected(
    tmp_path, state_changes
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    xml_stat = xml.stat()
    replacements = {
        'caption_source_xml_size': xml_stat.st_size,
        'caption_source_xml_mtime_ns': xml_stat.st_mtime_ns,
    }
    replacements.update(state_changes)
    state = replace(
        file_state(video, xml),
        **replacements,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()
    assert journal.events == []


@pytest.mark.parametrize(
    ('field', 'bad_value'),
    [
        ('event', None),
        ('event', 1),
        ('event', True),
        ('event', ''),
        ('event', []),
        ('fingerprint', None),
        ('fingerprint', 1),
        ('fingerprint', True),
        ('fingerprint', ''),
        ('file', None),
        ('file', 1),
        ('file', True),
        ('file', ''),
        ('xml_file', 1),
        ('xml_file', True),
        ('xml_file', ''),
        ('manifest_id', 1),
        ('manifest_id', True),
        ('manifest_id', ''),
        *[
            (field, bad_value)
            for field in (
                'youtube_processed',
                'caption_uploaded',
                'caption_refresh_required',
                'ambiguous',
                'playlist_inserted',
                'description_updated',
                'video_upload_rejected',
            )
            for bad_value in (None, 0, 1, 'invalid-boolean')
        ],
        ('video_id', None),
        ('video_id', 1),
        ('video_id', True),
        ('video_id', ''),
        ('deleted_paths', []),
        ('deleted_paths', (1,)),
    ],
)
def test_corrupt_cleanup_state_shape_protects_paired_sources(
    tmp_path, field, bad_value
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    xml_stat = xml.stat()
    state = replace(
        file_state(
            video,
            xml,
            event='youtube_processed',
            youtube_processed=True,
            caption_uploaded=True,
            video_id='yt123',
        ),
        caption_source_xml_size=xml_stat.st_size,
        caption_source_xml_mtime_ns=xml_stat.st_mtime_ns,
        **{field: bad_value},
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()
    assert journal.events == []


@pytest.mark.parametrize(
    ('field', 'bad_value'),
    [
        ('stage', None),
        ('stage', 1),
        ('stage', ''),
        ('status', None),
        ('status', 1),
        ('status', ''),
        ('retry_at', None),
        ('retry_at', 1),
        ('retry_at', ''),
        ('retry_at', 'not-a-timestamp'),
        ('retry_at', '2026-07-28T12:05:00'),
        ('attempt', True),
        ('attempt', -1),
    ],
)
def test_corrupt_retry_shape_protects_paired_sources(
    tmp_path, field, bad_value
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = file_state(
        video,
        xml,
        event='stage_retry_scheduled',
        youtube_processed=True,
        video_id='yt123',
    )
    retry_fields = {
        'stage': 'caption',
        'status': 'retryable',
        'retry_at': '2026-07-28T12:05:00+00:00',
        'attempt': 1,
    }
    retry_fields[field] = bad_value
    state = replace(state, **retry_fields)
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {video, xml}
    assert journal.events == []


def test_cleanup_deletes_baseline_and_ignored_paths_oldest_first(tmp_path):
    old_video = tmp_path / 'old.flv'
    old_xml = tmp_path / 'old.xml'
    new_video = tmp_path / 'new.flv'
    old_video.write_bytes(b'old')
    old_xml.write_text('<i/>', encoding='utf8')
    new_video.write_bytes(b'new')
    old_ns = 1_700_000_000_000_000_000
    new_ns = old_ns + 10_000_000_000
    for path in (old_video, old_xml):
        path.touch()
        path.chmod(0o600)
        import os
        os.utime(path, ns=(old_ns, old_ns))
    import os
    os.utime(new_video, ns=(new_ns, new_ns))
    states = [
        file_state(
            new_video,
            fingerprint='ignored',
            event='ignored_tiny',
        ),
        file_state(old_video, event='baseline'),
        file_state(old_xml, event='baseline'),
    ]
    journal, cleanup = cleanup_for(tmp_path, states, Usage(99, 99, 99, 84))

    result = cleanup.run(states, dry_run=False)

    assert result.deleted == (old_video, old_xml, new_video)
    deleted_events = [
        fields for event, fields in journal.events
        if event == 'source_deleted'
    ]
    assert [fields['path'] for fields in deleted_events] == [
        str(old_video), str(old_xml), str(new_video)
    ]


def test_cleanup_deletes_caption_uploaded_xml_independently(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    xml_stat = xml.stat()
    state = replace(
        file_state(
            video, xml, event='caption_uploaded', caption_uploaded=True,
            video_id='yt123',
        ),
        caption_source_xml_size=xml_stat.st_size,
        caption_source_xml_mtime_ns=xml_stat.st_mtime_ns,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(90, 84))

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert not xml.exists()
    assert result.deleted == (xml,)
    assert result.protected == (video,)
    assert [event for event, _ in journal.events] == [
        'source_delete_intent', 'source_deleted', 'quarantine_removed'
    ]
    assert journal.events[1][1]['path'] == str(xml)


def test_published_caption_without_durable_xml_identity_is_protected(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = file_state(
        video,
        xml,
        event='caption_uploaded',
        caption_uploaded=True,
        video_id='yt123',
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert xml.exists()
    assert set(result.protected) == {video, xml}
    assert journal.events == []


def test_published_caption_uses_durable_identity_when_manifest_lacks_xml(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    xml_stat = xml.stat()
    state = replace(
        file_state(
            video,
            xml,
            event='caption_uploaded',
            caption_uploaded=True,
            video_id='yt123',
        ),
        caption_source_xml_size=xml_stat.st_size,
        caption_source_xml_mtime_ns=xml_stat.st_mtime_ns,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99, 84))

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert not xml.exists()
    assert result.deleted == (xml,)


def test_changed_durable_caption_source_identity_is_protected(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    original = xml.stat()
    state = replace(
        file_state(
            video,
            xml,
            event='caption_uploaded',
            caption_uploaded=True,
            video_id='yt123',
        ),
        caption_source_xml_size=original.st_size,
        caption_source_xml_mtime_ns=original.st_mtime_ns,
    )
    xml.write_text('<i><d p="1">changed</d></i>', encoding='utf8')
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert xml.exists()
    assert set(result.protected) == {video, xml}
    assert journal.events == []


@pytest.mark.parametrize('active_state', [
    SessionState.SKIP_CURRENT_SESSION,
    SessionState.RECORDING,
    SessionState.SETTLING,
    SessionState.READY,
])
def test_current_session_overrides_older_baseline(active_state, tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    state = file_state(video, event='baseline')
    journal, cleanup = cleanup_for(
        tmp_path,
        [state],
        Usage(99),
        current_session=session(active_state, (video,)),
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert set(result.protected) == {video, video.with_suffix('.xml')}
    assert result.exhausted is True
    assert journal.events == []


def test_dry_run_plans_candidates_without_unlinking_or_journaling(tmp_path):
    first = tmp_path / 'first.flv'
    second = tmp_path / 'second.flv'
    first.write_bytes(b'first')
    second.write_bytes(b'second')
    import os
    os.utime(first, ns=(1_700_000_000_000_000_000,) * 2)
    os.utime(second, ns=(1_700_000_010_000_000_000,) * 2)
    states = [
        file_state(first, event='baseline'),
        file_state(second, fingerprint='second', event='ignored_tiny'),
    ]
    usage = Usage(90)
    journal, cleanup = cleanup_for(tmp_path, states, usage)

    result = cleanup.run(states, dry_run=True)

    assert result.deleted == (first, second)
    assert first.exists() and second.exists()
    assert journal.events == []
    assert len(usage.calls) == 1
    assert result.disk_usage_percent == 90
    assert result.exhausted is False


def test_cleanup_below_threshold_returns_without_inspecting_paths(tmp_path):
    missing = tmp_path / 'missing.flv'
    state = file_state(missing, event='baseline')
    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(DISK_CLEANUP_THRESHOLD_PERCENT - 1)
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert result.protected == ()
    assert result.exhausted is False
    assert journal.events == []


def test_cleanup_above_threshold_without_eligible_paths_is_exhausted(
    tmp_path, caplog
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    state = file_state(video)
    _, cleanup = cleanup_for(tmp_path, [state], Usage(90))

    result = cleanup.run([state], dry_run=False)

    assert result.exhausted is True
    assert 'no eligible Bililive source paths remain' in caplog.text


def test_cleanup_protects_missing_nonregular_symlink_and_outside_paths(tmp_path):
    missing = tmp_path / 'missing.flv'
    directory = tmp_path / 'directory.flv'
    directory.mkdir()
    target = tmp_path / 'target.flv'
    target.write_bytes(b'target')
    symlink = tmp_path / 'symlink.flv'
    symlink.symlink_to(target)
    outside = tmp_path.parent / f'{tmp_path.name}-outside.flv'
    outside.write_bytes(b'outside')
    states = [
        file_state(missing, fingerprint='missing', event='baseline'),
        file_state(directory, fingerprint='directory', event='baseline'),
        file_state(symlink, fingerprint='symlink', event='baseline'),
        file_state(outside, fingerprint='outside', event='baseline'),
    ]
    journal, cleanup = cleanup_for(tmp_path, states, Usage(99))

    result = cleanup.run(states, dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {missing, directory, symlink, outside}
    assert target.exists() and outside.exists()
    assert journal.events == []


def test_new_ready_state_for_same_path_overrides_old_processed_state(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'changed video')
    states = [
        file_state(
            video,
            fingerprint='old',
            event='youtube_processed',
            youtube_processed=True,
            video_id='yt-old',
        ),
        file_state(video, fingerprint='new', event='file_ready'),
    ]
    journal, cleanup = cleanup_for(tmp_path, states, Usage(99))

    result = cleanup.run(states, dry_run=False)

    assert video.exists()
    assert result.protected == (video,)
    assert journal.events == []


def test_cleanup_uses_replay_state_instead_of_stale_supplied_state(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    replay_state = file_state(video, event='file_ready')
    stale_state = replace(
        replay_state,
        event='youtube_processed',
        youtube_processed=True,
        video_id='yt-stale',
    )
    journal, cleanup = cleanup_for(tmp_path, [replay_state], Usage(99))

    result = cleanup.run([stale_state], dry_run=False)

    assert result.deleted == ()
    assert result.protected == (video,)
    assert video.exists()
    assert journal.events == []


def test_conflicting_processed_fingerprints_cannot_authorize_same_path(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    states = [
        file_state(
            video, fingerprint='first', event='youtube_processed',
            youtube_processed=True, video_id='yt-first',
        ),
        file_state(
            video, fingerprint='second', event='youtube_processed',
            youtube_processed=True, video_id='yt-second',
        ),
    ]
    journal, cleanup = cleanup_for(tmp_path, states, Usage(99))

    result = cleanup.run(states, dry_run=False)

    assert result.deleted == ()
    assert result.protected == (video,)
    assert video.exists()
    assert journal.events == []


def test_changed_baseline_generation_is_protected(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'original')
    original = video.stat()
    state = file_state(
        video,
        fingerprint=baseline_fingerprint(
            video, original.st_size, original.st_mtime_ns
        ),
        event='baseline',
    )
    video.write_bytes(b'changed generation')
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert result.protected == (video,)
    assert video.exists()
    assert journal.events == []


@pytest.mark.parametrize('event', ['ignored_tiny', 'youtube_processed'])
def test_manifestless_nonbaseline_without_durable_identity_is_protected(
    tmp_path, event
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    state = file_state(
        video,
        event=event,
        youtube_processed=event == 'youtube_processed',
        video_id='yt123' if event == 'youtube_processed' else None,
        durable_identity=False,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert result.protected == (video,)
    assert video.exists()
    assert journal.events == []


@pytest.mark.parametrize('event', ['ignored_tiny', 'youtube_processed'])
def test_manifestless_nonbaseline_with_durable_identity_is_eligible(
    tmp_path, event
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    file_stat = video.stat()
    state = replace(
        file_state(
            video,
            event=event,
            youtube_processed=event == 'youtube_processed',
            video_id='yt123' if event == 'youtube_processed' else None,
        ),
        source_size=file_stat.st_size,
        source_mtime_ns=file_stat.st_mtime_ns,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99, 84))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == (video,)
    assert not video.exists()


def test_changed_frozen_source_is_protected_before_runner_invalidates_manifest(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'original')
    frozen = manifest('session-1', (video,))
    state = file_state(
        video,
        fingerprint='old',
        event='youtube_processed',
        manifest_id='session-1',
        youtube_processed=True,
        video_id='yt-old',
    )
    video.write_bytes(b'changed source')
    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), manifests=(frozen,)
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.protected == (video,)
    assert journal.events == []


def test_real_journal_missing_manifest_protects_paired_sources(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    xml_stat = xml.stat()
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='missing-manifest',
        file=str(video), xml_file=str(xml),
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'caption_source_frozen', fingerprint='fp1', xml_file=str(xml),
        caption_source_xml_size=xml_stat.st_size,
        caption_source_xml_mtime_ns=xml_stat.st_mtime_ns,
    )
    journal.append('caption_uploaded', fingerprint='fp1')
    journal.append('youtube_processed', fingerprint='fp1')
    state = journal.replay().files['fp1']

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=lambda path: 99
    ).run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()


def test_duplicate_manifest_id_protects_paired_sources(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    first = manifest('duplicate', (video,))
    second = manifest('duplicate', (video,))
    state = file_state(
        video, xml, event='youtube_processed', manifest_id='duplicate',
        youtube_processed=True, caption_uploaded=True, video_id='yt123',
    )
    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), manifests=(first, second)
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()
    assert journal.events == []


def test_mismatched_xml_binding_protects_claimed_and_derived_pairs(tmp_path):
    video = tmp_path / 'recording.flv'
    expected_xml = tmp_path / 'recording.xml'
    unrelated_video = tmp_path / 'unrelated.flv'
    unrelated_xml = tmp_path / 'unrelated.xml'
    video.write_bytes(b'video')
    expected_xml.write_text('<i>expected</i>', encoding='utf8')
    unrelated_video.write_bytes(b'unrelated video')
    unrelated_xml.write_text('<i>unrelated</i>', encoding='utf8')
    unrelated_stat = unrelated_xml.stat()
    state = replace(
        file_state(
            video, unrelated_xml, event='youtube_processed',
            youtube_processed=True, caption_uploaded=True, video_id='yt123',
        ),
        caption_source_xml_size=unrelated_stat.st_size,
        caption_source_xml_mtime_ns=unrelated_stat.st_mtime_ns,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {
        video, expected_xml, unrelated_video, unrelated_xml,
    }
    assert all(path.exists() for path in result.protected)
    assert journal.events == []


def test_manifest_snapshot_with_unpaired_xml_protects_bound_sources(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    unrelated_xml = tmp_path / 'unrelated.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    unrelated_xml.write_text('<i>unrelated</i>', encoding='utf8')
    frozen = manifest('session-1', (video,))
    malicious_snapshot = dict(frozen.snapshot)
    unrelated_stat = unrelated_xml.stat()
    malicious_snapshot[str(unrelated_xml)] = (
        unrelated_stat.st_size, unrelated_stat.st_mtime_ns,
    )
    frozen = replace(frozen, snapshot=malicious_snapshot)
    state = file_state(
        video, xml, event='youtube_processed', manifest_id='session-1',
        youtube_processed=True, caption_uploaded=True, video_id='yt123',
    )
    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), manifests=(frozen,)
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {
        video, xml, unrelated_xml, unrelated_xml.with_suffix('.flv')
    }
    assert video.exists() and xml.exists() and unrelated_xml.exists()
    assert journal.events == []


@pytest.mark.parametrize(
    'corruption',
    [
        'non_boolean_manifest_flag',
        'replacement_room_mismatch',
        'missing_replacement',
        'replacement_cycle',
        'missing_pending_source',
        'duplicate_pending_source',
        'invalid_manifest_id',
        'invalid_manifest_timestamp',
        'pending_noninvalid_source',
        'invalid_session_room',
        'unsupported_session_state',
        'stale_idle_session',
        'incomplete_active_session',
    ],
)
def test_corrupt_control_graph_globally_protects_sources(
    tmp_path, corruption
):
    video = tmp_path / 'eligible.flv'
    controlled = tmp_path / 'controlled.flv'
    video.write_bytes(b'eligible')
    controlled.write_bytes(b'controlled')
    state = file_state(video, event='baseline')
    old = manifest(
        'old', (controlled,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    replacement = manifest('replacement', (controlled,), completed=True)
    manifests = (old, replacement)
    pending = ()
    current_session = session()

    if corruption == 'non_boolean_manifest_flag':
        manifests = (replace(replacement, completed=1),)
    elif corruption == 'replacement_room_mismatch':
        manifests = (old, replace(replacement, room_id=123))
    elif corruption == 'missing_replacement':
        manifests = (old,)
    elif corruption == 'replacement_cycle':
        manifests = (
            old,
            replace(
                replacement, completed=False, invalidated=True,
                invalidated_at=NOW, invalidation_reason='changed again',
                changed_paths=(str(controlled),),
                replacement_manifest_id='old',
            ),
        )
    elif corruption == 'missing_pending_source':
        manifests = (replacement,)
        pending = (JournalResettleRequest(
            source_manifest_id='missing', settled_at=NOW,
            detected_at=NOW, reason='source changed',
            changed_paths=(str(controlled),),
        ),)
    elif corruption == 'duplicate_pending_source':
        unclaimed = replace(old, replacement_manifest_id=None)
        request = JournalResettleRequest(
            source_manifest_id='old', settled_at=NOW,
            detected_at=NOW, reason='source changed',
            changed_paths=(str(controlled),),
        )
        manifests = (unclaimed,)
        pending = (request, request)
    elif corruption == 'invalid_manifest_id':
        manifests = (replace(replacement, manifest_id=''),)
    elif corruption == 'invalid_manifest_timestamp':
        manifests = (replace(replacement, settled_at='not-a-timestamp'),)
    elif corruption == 'pending_noninvalid_source':
        manifests = (replace(replacement, completed=False),)
        pending = (JournalResettleRequest(
            source_manifest_id='replacement', settled_at=NOW,
            detected_at=NOW, reason='source changed',
            changed_paths=(str(controlled),),
        ),)
    elif corruption == 'invalid_session_room':
        manifests = ()
        current_session = replace(session(), room_id=True)
    elif corruption == 'unsupported_session_state':
        manifests = ()
        current_session = replace(
            session(), state=SessionState.PUBLISHING
        )
    elif corruption == 'stale_idle_session':
        manifests = ()
        current_session = replace(
            session(), session_id='stale', session_paths=(str(video),),
            quiet_since=NOW, started_at=NOW,
        )
    elif corruption == 'incomplete_active_session':
        manifests = ()
        current_session = replace(
            session(SessionState.RECORDING, (video,)), session_id=None
        )

    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), manifests=manifests,
        pending=pending, current_session=current_session,
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert video in result.protected
    assert result.deleted == ()
    assert journal.events == []


def test_corrupt_control_graph_blocks_pending_reconciliation_below_threshold(
    tmp_path,
):
    video = tmp_path / 'pending.flv'
    video.write_bytes(b'pending')
    state = file_state(video, event='baseline')
    file_stat = video.stat()
    intent = JournalDeleteIntent(
        fingerprint=state.fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=file_stat.st_dev,
        ino=file_stat.st_ino,
        size=file_stat.st_size,
        mtime_ns=file_stat.st_mtime_ns,
        reason='disk pressure',
    )
    current_replay = replay(
        (state,), current_session=replace(session(), room_id=True)
    )
    current_replay = replace(
        current_replay, pending_deletions=(intent,)
    )
    journal = FakeJournal(current_replay)
    cleanup = StateAwareCleanup(journal, tmp_path, disk_usage=Usage(1))

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected
    assert journal.events == []


def test_raw_caption_retry_after_xml_delete_intent_rolls_back_and_aborts(
    tmp_path,
):
    video = tmp_path / 'published.flv'
    xml = tmp_path / 'published.xml'
    video.write_bytes(b'video')
    xml.write_bytes(b'<i/>')
    authorized = file_state(
        video, xml, event='caption_uploaded', video_id='yt1',
        youtube_processed=True, caption_uploaded=True,
    )
    quarantine_name = '.bililive-cleanup-quarantine/pending-xml'
    intent = pending_intent(authorized, xml, quarantine_name)
    quarantine = tmp_path / quarantine_name
    quarantine.parent.mkdir(mode=0o700)
    xml.rename(quarantine)
    injected = replace(
        authorized, event='stage_retry_scheduled', stage='caption',
        status='retryable', retry_at=NOW, attempt=1,
    )
    current_replay = replace(
        replay((injected,)), pending_deletions=(intent,), journal_version=41,
    )
    journal = FakeJournal(current_replay)

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((injected,), dry_run=False)

    assert xml.read_bytes() == b'<i/>'
    assert not quarantine.exists()
    assert result.deleted == ()
    assert [event for event, _ in journal.events] == ['source_delete_aborted']
    assert journal.events[0][1]['expected_journal_version'] == 41


@pytest.mark.parametrize(
    'updates',
    [
        {'event': 'upload_started', 'upload_started_at': NOW, 'attempt': 1},
        {
            'event': 'description_updated', 'description_updated': True,
            'description_fingerprint': 'changed-after-intent',
        },
        {
            'event': 'stage_retry_scheduled', 'stage': 'video',
            'status': 'retryable', 'retry_at': NOW, 'attempt': 1,
        },
    ],
)
def test_raw_video_file_event_after_delete_intent_aborts(
    tmp_path, updates,
):
    video = tmp_path / 'published.flv'
    video.write_bytes(b'video')
    authorized = file_state(
        video, event='youtube_processed', video_id='yt1',
        youtube_processed=True,
    )
    quarantine_name = '.bililive-cleanup-quarantine/pending-video'
    intent = pending_intent(authorized, video, quarantine_name)
    quarantine = tmp_path / quarantine_name
    quarantine.parent.mkdir(mode=0o700)
    video.rename(quarantine)
    injected = replace(authorized, **updates)
    current_replay = replace(
        replay((injected,)), pending_deletions=(intent,), journal_version=43,
    )
    journal = FakeJournal(current_replay)

    StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((injected,), dry_run=False)

    assert video.read_bytes() == b'video'
    assert not quarantine.exists()
    assert [event for event, _ in journal.events] == ['source_delete_aborted']
    assert journal.events[0][1]['expected_journal_version'] == 43


def test_raw_lifecycle_change_after_tombstone_keeps_quarantine_pending(
    tmp_path,
):
    video = tmp_path / 'published.flv'
    video.write_bytes(b'video')
    authorized = file_state(
        video, event='youtube_processed', video_id='yt1',
        youtube_processed=True,
    )
    quarantine_name = '.bililive-cleanup-quarantine/pending-video'
    intent = pending_intent(
        authorized, video, quarantine_name, source_deleted=True
    )
    quarantine = tmp_path / quarantine_name
    quarantine.parent.mkdir(mode=0o700)
    video.rename(quarantine)
    injected = replace(
        authorized, event='stage_retry_scheduled', stage='video',
        status='retryable', retry_at=NOW, attempt=1,
        deleted_paths=(str(video),),
    )
    current_replay = replace(
        replay((injected,)), pending_deletions=(intent,), journal_version=47,
    )
    journal = FakeJournal(current_replay)

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((injected,), dry_run=False)

    assert quarantine.read_bytes() == b'video'
    assert not video.exists()
    assert journal.events == []
    assert quarantine in result.protected


def test_pending_reconciliation_requires_unique_replay_path_owner(tmp_path):
    video = tmp_path / 'pending.flv'
    video.write_bytes(b'pending')
    owner = file_state(video, event='baseline')
    conflicting = file_state(
        video, fingerprint='other-generation', event='ignored_tiny'
    )
    file_stat = video.stat()
    intent = JournalDeleteIntent(
        fingerprint=owner.fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=file_stat.st_dev,
        ino=file_stat.st_ino,
        size=file_stat.st_size,
        mtime_ns=file_stat.st_mtime_ns,
        reason='disk pressure',
    )
    current_replay = replace(
        replay((owner, conflicting)), pending_deletions=(intent,)
    )
    journal = FakeJournal(current_replay)
    cleanup = StateAwareCleanup(journal, tmp_path, disk_usage=Usage(1))

    result = cleanup.run([owner], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected
    assert journal.events == []


def test_pending_reconciliation_rejects_lexical_alias_owner(tmp_path):
    directory = tmp_path / 'nested'
    directory.mkdir()
    video = tmp_path / 'pending.flv'
    video.write_bytes(b'pending')
    owner = file_state(video, event='baseline')
    conflicting = file_state(
        directory / '..' / video.name,
        fingerprint='other-generation',
        event='ignored_tiny',
    )
    file_stat = video.stat()
    intent = JournalDeleteIntent(
        fingerprint=owner.fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=file_stat.st_dev,
        ino=file_stat.st_ino,
        size=file_stat.st_size,
        mtime_ns=file_stat.st_mtime_ns,
        reason='disk pressure',
    )
    current_replay = replace(
        replay((owner, conflicting)), pending_deletions=(intent,)
    )
    journal = FakeJournal(current_replay)
    cleanup = StateAwareCleanup(journal, tmp_path, disk_usage=Usage(1))

    result = cleanup.run([owner], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected
    assert journal.events == []


def test_deleted_path_alias_protects_canonical_recreated_path(tmp_path):
    nested = tmp_path / 'nested'
    nested.mkdir()
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    state = replace(
        file_state(video, event='baseline'),
        deleted_paths=(str(nested / '..' / video.name),),
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert journal.events == []


def test_pending_phase_must_match_source_deleted_tombstone(tmp_path):
    video = tmp_path / 'pending.flv'
    video.write_bytes(b'pending')
    owner = file_state(video, event='baseline')
    file_stat = video.stat()
    owner = replace(owner, deleted_paths=(str(video),))
    intent = JournalDeleteIntent(
        fingerprint=owner.fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=file_stat.st_dev,
        ino=file_stat.st_ino,
        size=file_stat.st_size,
        mtime_ns=file_stat.st_mtime_ns,
        reason='disk pressure',
        source_deleted=False,
    )
    current_replay = replace(
        replay((owner,)), pending_deletions=(intent,)
    )
    journal = FakeJournal(current_replay)
    cleanup = StateAwareCleanup(journal, tmp_path, disk_usage=Usage(1))

    result = cleanup.run([owner], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected
    assert journal.events == []


def test_raw_tombstoned_owner_releases_recreated_path_with_pending_quarantine(
    tmp_path,
):
    nested = tmp_path / 'nested'
    nested.mkdir()
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'new generation')
    old = replace(
        file_state(
            nested / '..' / video.name,
            fingerprint='old', event='baseline', durable_identity=False,
        ),
        deleted_paths=(str(video),),
    )
    new = file_state(video, event='baseline')
    old_intent = JournalDeleteIntent(
        fingerprint='old', original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/old',
        dev=10, ino=20, size=30, mtime_ns=40,
        reason='disk pressure', source_deleted=True,
    )
    current_replay = replace(
        replay((old, new)), pending_deletions=(old_intent,)
    )

    assert StateAwareCleanup._control_graph_valid(current_replay)


def test_raw_tombstone_does_not_hide_conflicting_active_aliases(tmp_path):
    nested = tmp_path / 'nested'
    nested.mkdir()
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'new generation')
    old = replace(
        file_state(
            video, fingerprint='old', event='baseline',
            durable_identity=False,
        ),
        deleted_paths=(str(video),),
    )
    new = file_state(video, fingerprint='new', event='baseline')
    conflicting = file_state(
        nested / '..' / video.name,
        fingerprint='conflicting', event='baseline',
    )
    old_intent = JournalDeleteIntent(
        fingerprint='old', original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/old',
        dev=10, ino=20, size=30, mtime_ns=40,
        reason='disk pressure', source_deleted=True,
    )
    current_replay = replace(
        replay((old, new, conflicting)),
        pending_deletions=(old_intent,),
    )

    assert not StateAwareCleanup._control_graph_valid(current_replay)


def test_pending_old_quarantine_reconciles_after_source_path_is_recreated(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old generation')
    journal, old_fingerprint = baseline_journal(
        tmp_path / 'state.jsonl', video
    )
    old_stat = video.stat()
    journal.append(
        'source_delete_intent', fingerprint=old_fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/old',
        dev=old_stat.st_dev, ino=old_stat.st_ino, size=old_stat.st_size,
        mtime_ns=old_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    quarantine_directory = tmp_path / '.bililive-cleanup-quarantine'
    quarantine_directory.mkdir(mode=0o700)
    quarantine = quarantine_directory / 'old'
    video.rename(quarantine)
    journal.append(
        'source_deleted', fingerprint=old_fingerprint, path=str(video),
        reason='disk pressure',
    )
    video.write_bytes(b'new generation')
    new_stat = video.stat()
    new_fingerprint = baseline_fingerprint(
        video, new_stat.st_size, new_stat.st_mtime_ns
    )
    journal.append(
        'baseline', fingerprint=new_fingerprint, file=str(video),
        source_size=new_stat.st_size, source_mtime_ns=new_stat.st_mtime_ns,
    )
    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((), dry_run=False)

    assert video.read_bytes() == b'new generation'
    assert not quarantine.exists()
    assert result.protected == (video,)
    assert journal.replay().pending_deletions == ()
    assert result.deleted == ()


def test_mismatched_old_quarantine_protects_quarantine_and_recreated_path(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'new generation')
    quarantine_directory = tmp_path / '.bililive-cleanup-quarantine'
    quarantine_directory.mkdir(mode=0o700)
    quarantine = quarantine_directory / 'old'
    quarantine.write_bytes(b'unrelated quarantine entry')
    old = replace(
        file_state(
            video, fingerprint='old', event='baseline',
            durable_identity=False,
        ),
        deleted_paths=(str(video),),
    )
    new = file_state(video, event='baseline')
    old_intent = JournalDeleteIntent(
        fingerprint='old', original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/old',
        dev=10, ino=20, size=30, mtime_ns=40,
        reason='disk pressure', source_deleted=True,
    )
    current_replay = replace(
        replay((old, new)), pending_deletions=(old_intent,)
    )
    journal = FakeJournal(current_replay)

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(99, 84)
    ).run((), dry_run=False)

    assert result.deleted == ()
    assert quarantine in result.protected
    assert video in result.protected
    assert video.read_bytes() == b'new generation'
    assert quarantine.read_bytes() == b'unrelated quarantine entry'


def test_quarantine_rename_never_replaces_existing_entry(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    file_stat = video.stat()
    quarantine = tmp_path / '.bililive-cleanup-quarantine'
    quarantine.mkdir(mode=0o700)
    occupied = quarantine / 'occupied'
    occupied.write_bytes(b'unjournaled')

    with RootDirectory(tmp_path) as root_directory:
        with pytest.raises(OSError):
            root_directory.rename_to_quarantine(
                video,
                '.bililive-cleanup-quarantine/occupied',
                stat_identity(file_stat),
            )

    assert video.read_bytes() == b'video'
    assert occupied.read_bytes() == b'unjournaled'


def test_quarantine_directory_must_belong_to_effective_user(
    tmp_path, monkeypatch
):
    quarantine = tmp_path / '.bililive-cleanup-quarantine'
    quarantine.mkdir(mode=0o700)
    actual_uid = quarantine.stat().st_uid
    monkeypatch.setattr(
        cleanup_fs_module.os, 'geteuid', lambda: actual_uid + 1
    )

    with RootDirectory(tmp_path) as root_directory:
        with pytest.raises(OSError, match='unsafe cleanup quarantine'):
            root_directory.ensure_quarantine()


def test_manifest_bound_baseline_still_requires_exact_baseline_fingerprint(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    frozen = manifest('session-1', (video,))
    state = file_state(
        video, fingerprint='stale-baseline', event='baseline',
        manifest_id='session-1',
    )
    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), manifests=(frozen,)
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected
    assert journal.events == []


def test_lexically_equivalent_file_and_xml_binding_remains_eligible(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    nested = tmp_path / 'nested'
    nested.mkdir()
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = replace(
        file_state(video, xml, event='baseline'),
        file=str(nested / '..' / video.name),
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99, 99, 84))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == (video,)
    assert result.protected == (xml,)
    assert [event for event, _ in journal.events] == [
        'source_delete_intent', 'source_deleted', 'quarantine_removed',
    ]
    assert journal.events[1][1]['path'] == str(video)


def test_xml_binding_does_not_follow_symlinked_parent(tmp_path):
    actual = tmp_path / 'actual'
    actual.mkdir()
    alias = tmp_path / 'alias'
    alias.symlink_to(actual, target_is_directory=True)
    video = actual / 'recording.flv'
    xml = actual / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = file_state(
        alias / video.name,
        xml,
        event='youtube_processed',
        youtube_processed=True,
        caption_uploaded=True,
        video_id='yt123',
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert set(result.protected) == {
        alias / video.name,
        alias / xml.name,
        video,
        xml,
    }
    assert video.exists() and xml.exists()
    assert journal.events == []


@pytest.mark.parametrize('claimed', [False, True])
def test_invalidated_resettle_protects_old_processed_paths(tmp_path, claimed):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'changed video')
    xml.write_text('<i>changed</i>', encoding='utf8')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement' if claimed else None,
    )
    pending = () if claimed else (JournalResettleRequest(
        source_manifest_id='old',
        settled_at=NOW,
        detected_at=NOW,
        reason='source changed',
        changed_paths=(str(video),),
    ),)
    current = (
        session(SessionState.SETTLING, (video, xml)) if claimed else session()
    )
    state = file_state(
        video,
        xml,
        fingerprint='old-fingerprint',
        event='youtube_processed',
        manifest_id='old',
        youtube_processed=True,
        caption_uploaded=True,
        video_id='yt-old',
    )
    journal, cleanup = cleanup_for(
        tmp_path,
        [state],
        Usage(99),
        manifests=(old,),
        pending=pending,
        current_session=current,
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists() and xml.exists()
    assert set(result.protected) == {video, xml}
    assert journal.events == []


def test_uncompleted_replacement_protects_old_and_replacement_paths(tmp_path):
    old_video = tmp_path / 'old.flv'
    replacement_video = tmp_path / 'replacement.flv'
    for path in (old_video, replacement_video):
        path.write_bytes(b'video')
        path.with_suffix('.xml').write_text('<i/>', encoding='utf8')
    old = manifest(
        'old', (old_video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    replacement_manifest = manifest('replacement', (replacement_video,))
    states = [
        file_state(
            old_video,
            old_video.with_suffix('.xml'),
            fingerprint='old',
            event='youtube_processed',
            manifest_id='old',
            youtube_processed=True,
            caption_uploaded=True,
            video_id='yt-old',
        ),
        file_state(
            replacement_video,
            replacement_video.with_suffix('.xml'),
            fingerprint='replacement',
            event='youtube_processed',
            manifest_id='replacement',
            youtube_processed=True,
            caption_uploaded=True,
            video_id='yt-replacement',
        ),
    ]
    journal, cleanup = cleanup_for(
        tmp_path,
        states,
        Usage(99),
        manifests=(old, replacement_manifest),
    )

    result = cleanup.run(states, dry_run=False)

    assert set(result.protected) == {
        old_video,
        old_video.with_suffix('.xml'),
        replacement_video,
        replacement_video.with_suffix('.xml'),
    }
    assert all(path.exists() for path in result.protected)
    assert journal.events == []


def test_completed_replacement_releases_chain_for_normal_eligibility(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )
    state = file_state(
        video,
        xml,
        fingerprint='replacement',
        event='youtube_processed',
        manifest_id='replacement',
        youtube_processed=True,
        caption_uploaded=True,
        video_id='yt-replacement',
    )
    _, cleanup = cleanup_for(
        tmp_path,
        [state],
        Usage(99, 99, 84),
        manifests=(old, replacement_manifest),
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == (video, xml)
    assert result.exhausted is False


def test_completed_replacement_allows_declared_flv_identity_change(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old generation')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    video.write_bytes(b'new generation with different bytes')
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )
    state = file_state(
        video,
        fingerprint='replacement-generation',
        event='youtube_processed',
        manifest_id='replacement',
        youtube_processed=True,
        video_id='yt-replacement',
    )
    journal, cleanup = cleanup_for(
        tmp_path,
        [state],
        Usage(99, 84),
        manifests=(old, replacement_manifest),
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == (video,)
    assert not video.exists()
    assert journal.events[1][0] == 'source_deleted'


def test_completed_replacement_rejects_undeclared_flv_identity_change(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old generation')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    old = replace(
        old, changed_paths=(str(video.with_suffix('.xml')),)
    )
    video.write_bytes(b'new generation with different bytes')
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )
    state = file_state(
        video,
        fingerprint='replacement-generation',
        event='youtube_processed',
        manifest_id='replacement',
        youtube_processed=True,
        video_id='yt-replacement',
    )
    journal, cleanup = cleanup_for(
        tmp_path,
        [state],
        Usage(99),
        manifests=(old, replacement_manifest),
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected
    assert journal.events == []


@pytest.mark.parametrize('flv_change', ['added', 'removed'])
def test_completed_replacement_rejects_declared_flv_set_change(
    tmp_path, flv_change
):
    video = tmp_path / 'recording.flv'
    changed = tmp_path / 'changed.flv'
    video.write_bytes(b'old generation')
    changed.write_bytes(b'changed generation')
    source_videos = (
        (video,) if flv_change == 'added' else (video, changed)
    )
    replacement_videos = (
        (video, changed) if flv_change == 'added' else (video,)
    )
    old = manifest(
        'old', source_videos, invalidated=True,
        replacement_manifest_id='replacement',
    )
    old = replace(old, changed_paths=(str(changed),))
    replacement_manifest = manifest(
        'replacement', replacement_videos, completed=True
    )

    assert not StateAwareCleanup._replacement_continuity_valid(
        old, replacement_manifest
    )


@pytest.mark.parametrize('xml_change', ['added', 'removed'])
def test_completed_replacement_allows_declared_paired_xml_key_change(
    tmp_path, xml_change
):
    video = tmp_path / 'recording.flv'
    xml = video.with_suffix('.xml')
    video.write_bytes(b'video')
    if xml_change == 'removed':
        xml.write_text('<i/>', encoding='utf8')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    old = replace(old, changed_paths=(str(xml),))
    if xml_change == 'added':
        xml.write_text('<i/>', encoding='utf8')
    else:
        xml.unlink()
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )

    assert StateAwareCleanup._replacement_continuity_valid(
        old, replacement_manifest
    )


def test_completed_replacement_pairs_xml_with_uppercase_flv_extension(
    tmp_path,
):
    video = tmp_path / 'recording.FLV'
    xml = video.with_suffix('.xml')
    video.write_bytes(b'video')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    old = replace(old, changed_paths=(str(xml),))
    xml.write_text('<i/>', encoding='utf8')
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )

    assert StateAwareCleanup._replacement_continuity_valid(
        old, replacement_manifest
    )


@pytest.mark.parametrize('xml_change', ['added', 'removed'])
def test_completed_replacement_rejects_undeclared_xml_key_change(
    tmp_path, xml_change
):
    video = tmp_path / 'recording.flv'
    xml = video.with_suffix('.xml')
    video.write_bytes(b'video')
    if xml_change == 'removed':
        xml.write_text('<i/>', encoding='utf8')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    if xml_change == 'added':
        xml.write_text('<i/>', encoding='utf8')
    else:
        xml.unlink()
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )
    old = replace(old, changed_paths=(str(video),))

    assert not StateAwareCleanup._replacement_continuity_valid(
        old, replacement_manifest
    )


def test_completed_replacement_rejects_declared_unpaired_xml_addition(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    unpaired_xml = tmp_path / 'other.xml'
    video.write_bytes(b'video')
    old = manifest(
        'old', (video,), invalidated=True,
        replacement_manifest_id='replacement',
    )
    old = replace(old, changed_paths=(str(unpaired_xml),))
    unpaired_xml.write_text('<i/>', encoding='utf8')
    replacement_manifest = manifest(
        'replacement', (video,), completed=True
    )
    unpaired_stat = unpaired_xml.stat()
    replacement_manifest = replace(
        replacement_manifest,
        snapshot={
            **replacement_manifest.snapshot,
            str(unpaired_xml): (
                unpaired_stat.st_size, unpaired_stat.st_mtime_ns
            ),
        },
    )

    assert not StateAwareCleanup._replacement_continuity_valid(
        old, replacement_manifest
    )


def _append_real_xml_key_replacement(journal, video, xml, xml_change):
    video_stat = video.stat()
    source_snapshot = {
        str(video): (video_stat.st_size, video_stat.st_mtime_ns)
    }
    source_has_xml = xml_change == 'removed'
    if source_has_xml:
        xml_stat = xml.stat()
        source_snapshot[str(xml)] = (
            xml_stat.st_size, xml_stat.st_mtime_ns
        )
    journal.append('initialized')
    journal.append(
        'session_state', room_id=1829181560, state='waiting',
        session_id=None, session_paths=(), snapshot=source_snapshot,
        quiet_since=None, started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='old', room_id=1829181560,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=(str(video),), snapshot=source_snapshot,
    )
    journal.append(
        'file_ready', fingerprint='fp', manifest_id='old', file=str(video),
        xml_file=str(xml) if source_has_xml else None,
    )
    journal.append('video_uploaded', fingerprint='fp', video_id='yt')
    if source_has_xml:
        journal.append('caption_uploaded', fingerprint='fp')
    journal.append('youtube_processed', fingerprint='fp')

    if xml_change == 'added':
        xml.write_text('<i/>', encoding='utf8')
    else:
        xml.unlink()
    target_snapshot = {
        str(video): (video_stat.st_size, video_stat.st_mtime_ns)
    }
    if xml_change == 'added':
        xml_stat = xml.stat()
        target_snapshot[str(xml)] = (
            xml_stat.st_size, xml_stat.st_mtime_ns
        )
    journal.append(
        'session_manifest_changed', manifest_id='old',
        detected_at='2026-07-27T12:05:00+00:00', reason='XML changed',
        changed_paths=(str(xml),),
    )
    journal.append(
        'session_resettle_started', source_manifest_id='old',
        replacement_manifest_id='replacement', room_id=1829181560,
        state='settling', session_paths=tuple(target_snapshot),
        snapshot=target_snapshot,
        quiet_since='2026-07-27T12:10:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    journal.append(
        'session_manifest_ready', manifest_id='replacement',
        room_id=1829181560,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:40:00+00:00',
        flv_paths=(str(video),), snapshot=target_snapshot,
    )
    journal.append(
        'file_ready', fingerprint='fp', manifest_id='replacement',
        file=str(video),
        xml_file=str(xml) if xml_change == 'added' else None,
    )
    if xml_change == 'added':
        journal.append('caption_uploaded', fingerprint='fp')
    journal.append('session_manifest_completed', manifest_id='replacement')
    journal.append(
        'session_state', room_id=1829181560, state='waiting',
        session_id=None, session_paths=(), snapshot=target_snapshot,
        quiet_since=None, started_at=None,
    )


@pytest.mark.parametrize('xml_change', ['added', 'removed'])
def test_real_journal_declared_xml_key_change_eventually_cleans(
    tmp_path, xml_change
):
    video = tmp_path / 'recording.flv'
    xml = video.with_suffix('.xml')
    video.write_bytes(b'video')
    if xml_change == 'removed':
        xml.write_text('<i/>', encoding='utf8')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    _append_real_xml_key_replacement(journal, video, xml, xml_change)
    usage = Usage(99, 99, 84) if xml_change == 'added' else Usage(99, 84)

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=usage
    ).run((), dry_run=False)

    expected = {video, xml} if xml_change == 'added' else {video}
    assert set(result.deleted) == expected
    assert all(not path.exists() for path in expected)
    assert result.exhausted is False


def test_cleanup_stops_after_usage_falls_below_threshold(tmp_path):
    old = tmp_path / 'old.flv'
    newer = tmp_path / 'new.flv'
    old.write_bytes(b'old')
    newer.write_bytes(b'new')
    import os
    os.utime(old, ns=(1_700_000_000_000_000_000,) * 2)
    os.utime(newer, ns=(1_700_000_010_000_000_000,) * 2)
    states = [
        file_state(old, event='baseline'),
        file_state(newer, event='baseline'),
    ]
    _, cleanup = cleanup_for(tmp_path, states, Usage(90, 84))

    result = cleanup.run(states, dry_run=False)

    assert result.deleted == (old,)
    assert newer.exists()
    assert result.disk_usage_percent == 84


def test_intent_cas_stops_session_state_race_before_rename(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    video_stat = video.stat()
    fingerprint = baseline_fingerprint(
        video, video_stat.st_size, video_stat.st_mtime_ns
    )
    journal = SessionRaceJournal(
        tmp_path / 'state.jsonl', video,
        (video_stat.st_size, video_stat.st_mtime_ns),
    )
    journal.append(
        'baseline', fingerprint=fingerprint, file=str(video),
        source_size=video_stat.st_size,
        source_mtime_ns=video_stat.st_mtime_ns,
    )

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(99, 99)
    ).run((), dry_run=False)

    replay = journal.replay()
    assert video.exists()
    assert replay.pending_deletions == ()
    assert replay.session.state is SessionState.RECORDING
    assert result.deleted == ()
    assert result.disk_usage_percent == 99


def test_cleanup_does_not_authorize_next_candidate_after_own_transaction(
    tmp_path,
):
    older = tmp_path / 'older.flv'
    newer = tmp_path / 'newer.flv'
    older.write_bytes(b'older')
    newer.write_bytes(b'newer')
    import os
    os.utime(older, ns=(1_700_000_000_000_000_000,) * 2)
    os.utime(newer, ns=(1_700_000_010_000_000_000,) * 2)
    newer_stat = newer.stat()
    journal = PostTransactionRaceJournal(
        tmp_path / 'state.jsonl', newer,
        (newer_stat.st_size, newer_stat.st_mtime_ns),
    )
    for video in (older, newer):
        video_stat = video.stat()
        journal.append(
            'baseline', fingerprint=baseline_fingerprint(
                video, video_stat.st_size, video_stat.st_mtime_ns
            ), file=str(video), source_size=video_stat.st_size,
            source_mtime_ns=video_stat.st_mtime_ns,
        )

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(99, 99)
    ).run((), dry_run=False)

    assert result.deleted == (older,)
    assert not older.exists()
    assert newer.exists()
    assert journal.replay().session.state is SessionState.RECORDING


def test_changed_source_aborts_old_intent_then_new_generation_can_claim(
    tmp_path,
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old')
    journal, old_fingerprint = baseline_journal(
        tmp_path / 'state.jsonl', video
    )
    old_stat = video.stat()
    journal.append(
        'source_delete_intent', fingerprint=old_fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/old',
        dev=old_stat.st_dev, ino=old_stat.st_ino, size=old_stat.st_size,
        mtime_ns=old_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    video.write_bytes(b'new generation')

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((), dry_run=False)

    replay = journal.replay()
    assert result.deleted == ()
    assert replay.pending_deletions == ()
    assert replay.files[old_fingerprint].deleted_paths == (str(video),)
    assert len(replay.deletion_aborts) == 1
    new_stat = video.stat()
    new_fingerprint = baseline_fingerprint(
        video, new_stat.st_size, new_stat.st_mtime_ns
    )
    journal.append(
        'baseline', fingerprint=new_fingerprint, file=str(video),
        source_size=new_stat.st_size, source_mtime_ns=new_stat.st_mtime_ns,
    )
    journal.append(
        'source_delete_intent', fingerprint=new_fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/new',
        dev=new_stat.st_dev, ino=new_stat.st_ino, size=new_stat.st_size,
        mtime_ns=new_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )


@pytest.mark.parametrize('original_occupied', [False, True])
def test_mismatched_quarantine_rolls_back_or_preserves_recovery(
    tmp_path, original_occupied
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old')
    journal, fingerprint = baseline_journal(tmp_path / 'state.jsonl', video)
    old_stat = video.stat()
    quarantine_dir = tmp_path / '.bililive-cleanup-quarantine'
    quarantine_dir.mkdir(mode=0o700)
    quarantine = quarantine_dir / 'mismatch'
    journal.append(
        'source_delete_intent', fingerprint=fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/mismatch',
        dev=old_stat.st_dev, ino=old_stat.st_ino, size=old_stat.st_size,
        mtime_ns=old_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    video.rename(quarantine)
    quarantine.write_bytes(b'mismatched bytes')
    if original_occupied:
        video.write_bytes(b'new generation')

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((), dry_run=False)

    replay = journal.replay()
    abort = replay.deletion_aborts[-1]
    assert result.deleted == ()
    assert replay.pending_deletions == ()
    assert not quarantine.exists()
    if original_occupied:
        assert video.read_bytes() == b'new generation'
        recovery = Path(abort.recovery_path)
        assert recovery.parent == video.parent
        assert recovery.suffix == '.bin'
        assert recovery.read_bytes() == b'mismatched bytes'
    else:
        assert abort.recovery_path is None
        assert video.read_bytes() == b'mismatched bytes'


def test_recovery_move_is_discovered_after_abort_append_crash(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old')
    journal, fingerprint = baseline_journal(tmp_path / 'state.jsonl', video)
    old_stat = video.stat()
    quarantine_dir = tmp_path / '.bililive-cleanup-quarantine'
    quarantine_dir.mkdir(mode=0o700)
    quarantine = quarantine_dir / 'mismatch'
    journal.append(
        'source_delete_intent', fingerprint=fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/mismatch',
        dev=old_stat.st_dev, ino=old_stat.st_ino, size=old_stat.st_size,
        mtime_ns=old_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    video.rename(quarantine)
    quarantine.write_bytes(b'mismatched bytes')
    video.write_bytes(b'new generation')

    crashing = CrashJournal(
        journal.path, before='source_delete_aborted'
    )
    with pytest.raises(SimulatedCleanupCrash):
        StateAwareCleanup(
            crashing, tmp_path, disk_usage=Usage(1)
        ).run((), dry_run=False)

    assert video.read_bytes() == b'new generation'
    assert not quarantine.exists()
    recovery_files = tuple(tmp_path.glob('*.bililive-recovery-*.bin'))
    assert len(recovery_files) == 1
    assert recovery_files[0].read_bytes() == b'mismatched bytes'

    StateAwareCleanup(
        JsonlJournal(journal.path), tmp_path, disk_usage=Usage(1)
    ).run((), dry_run=False)

    replay = journal.replay()
    assert replay.pending_deletions == ()
    assert replay.deletion_aborts[-1].recovery_path == str(recovery_files[0])
    assert recovery_files[0].read_bytes() == b'mismatched bytes'


@pytest.mark.parametrize(
    'pending_case',
    [
        'pre-rename-exact',
        'changed-original',
        'correct-quarantine',
        'mismatched-quarantine-rollback',
        'mismatched-quarantine-recovery',
        'source-deleted-new-original',
        'quarantine-missing',
        'recovery-present',
    ],
)
def test_pending_dry_run_matches_live_decision_without_mutation(
    tmp_path, monkeypatch, pending_case
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old')
    journal, fingerprint = baseline_journal(tmp_path / 'state.jsonl', video)
    old_stat = video.stat()
    quarantine_dir = tmp_path / '.bililive-cleanup-quarantine'
    quarantine = quarantine_dir / 'pending'
    journal.append(
        'source_delete_intent', fingerprint=fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=old_stat.st_dev, ino=old_stat.st_ino, size=old_stat.st_size,
        mtime_ns=old_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    intent = journal.replay().pending_deletions[0]
    recovery = StateAwareCleanup._intent_recovery_path(intent)

    if pending_case in {
        'correct-quarantine',
        'mismatched-quarantine-rollback',
        'mismatched-quarantine-recovery',
        'source-deleted-new-original',
        'recovery-present',
    }:
        quarantine_dir.mkdir(mode=0o700)
        video.rename(quarantine)
    if pending_case in {
        'mismatched-quarantine-rollback',
        'mismatched-quarantine-recovery',
        'recovery-present',
    }:
        quarantine.write_bytes(b'mismatched bytes')
    if pending_case in {
        'changed-original',
        'mismatched-quarantine-recovery',
        'source-deleted-new-original',
        'recovery-present',
    }:
        video.write_bytes(b'new generation')
    if pending_case == 'source-deleted-new-original':
        journal.append(
            'source_deleted', fingerprint=fingerprint, path=str(video),
            reason='disk pressure',
        )
    if pending_case == 'quarantine-missing':
        video.unlink()
    if pending_case == 'recovery-present':
        quarantine.rename(recovery)

    expected_deleted = (
        (video,)
        if pending_case in {'pre-rename-exact', 'correct-quarantine'}
        else ()
    )
    expected_protected = {
        'pre-rename-exact': (),
        'changed-original': (video,),
        'correct-quarantine': (),
        'mismatched-quarantine-rollback': (video,),
        'mismatched-quarantine-recovery': (video, recovery),
        'source-deleted-new-original': (video,),
        'quarantine-missing': (),
        'recovery-present': (video, recovery),
    }[pending_case]

    def tree_snapshot():
        return tuple(
            (
                str(path.relative_to(tmp_path)), path.is_dir(),
                None if path.is_dir() else path.read_bytes(),
            )
            for path in sorted(tmp_path.rglob('*'))
        )

    before = tree_snapshot()

    def forbidden(*args, **kwargs):
        raise AssertionError('dry-run attempted a filesystem or journal write')

    with monkeypatch.context() as dry_patch:
        dry_patch.setattr(journal, 'append', forbidden)
        dry_patch.setattr(cleanup_fs_module.os, 'fsync', forbidden)
        for method in (
            'sync_intent_directories', 'rename_to_quarantine',
            'unlink_quarantine', 'move_quarantine_to_original',
            'move_quarantine_to_recovery',
        ):
            dry_patch.setattr(RootDirectory, method, forbidden)
        dry_result = StateAwareCleanup(
            journal, tmp_path, disk_usage=Usage(1)
        ).run((), dry_run=True)

    assert tree_snapshot() == before
    assert dry_result.deleted == expected_deleted
    assert dry_result.protected == tuple(sorted(expected_protected))

    live_result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(1)
    ).run((), dry_run=False)

    assert live_result.deleted == expected_deleted
    assert live_result.protected == tuple(sorted(expected_protected))


@pytest.mark.parametrize(
    'pending_phase',
    [
        'pre-rename-exact',
        'abort-changed',
        'source-deleted',
        'quarantine-removed',
    ],
)
def test_pending_reconciliation_propagates_version_to_ordinary_candidates(
    tmp_path, pending_phase
):
    pending = tmp_path / 'pending.flv'
    ordinary_old = tmp_path / 'ordinary-old.flv'
    ordinary_new = tmp_path / 'ordinary-new.flv'
    pending.write_bytes(b'pending old')
    ordinary_old.write_bytes(b'ordinary old')
    ordinary_new.write_bytes(b'ordinary new')
    os.utime(ordinary_old, ns=(1_700_000_000_000_000_000,) * 2)
    os.utime(ordinary_new, ns=(1_700_000_010_000_000_000,) * 2)
    journal, fingerprint = baseline_journal(
        tmp_path / 'state.jsonl', pending
    )
    pending_stat = pending.stat()
    for path in (ordinary_old, ordinary_new):
        file_stat = path.stat()
        journal.append(
            'baseline', fingerprint=baseline_fingerprint(
                path, file_stat.st_size, file_stat.st_mtime_ns
            ), file=str(path), source_size=file_stat.st_size,
            source_mtime_ns=file_stat.st_mtime_ns,
        )
    quarantine_dir = tmp_path / '.bililive-cleanup-quarantine'
    quarantine = quarantine_dir / 'pending'
    journal.append(
        'source_delete_intent', fingerprint=fingerprint,
        original_path=str(pending),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=pending_stat.st_dev, ino=pending_stat.st_ino,
        size=pending_stat.st_size, mtime_ns=pending_stat.st_mtime_ns,
        reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    if pending_phase == 'abort-changed':
        pending.write_bytes(b'pending new generation')
    elif pending_phase in {'source-deleted', 'quarantine-removed'}:
        quarantine_dir.mkdir(mode=0o700)
        pending.rename(quarantine)
        journal.append(
            'source_deleted', fingerprint=fingerprint, path=str(pending),
            reason='disk pressure',
        )
        if pending_phase == 'quarantine-removed':
            quarantine.unlink()

    dry_result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(99)
    ).run((), dry_run=True)
    live_result = StateAwareCleanup(
        journal, tmp_path, disk_usage=Usage(99, 99, 84)
    ).run((), dry_run=False)

    expected_deleted = {
        'pre-rename-exact': (pending, ordinary_old, ordinary_new),
        'abort-changed': (ordinary_old, ordinary_new),
        'source-deleted': (ordinary_old, ordinary_new),
        'quarantine-removed': (ordinary_old, ordinary_new),
    }[pending_phase]
    expected_protected = (
        (pending,) if pending_phase == 'abort-changed' else ()
    )
    assert dry_result.deleted == expected_deleted
    assert live_result.deleted == expected_deleted
    assert dry_result.protected == expected_protected
    assert live_result.protected == expected_protected
    assert live_result.disk_usage_percent == 84
    assert not ordinary_old.exists() and not ordinary_new.exists()


@pytest.mark.parametrize(
    ('fault_operation', 'phase_event'),
    [
        ('rename_to_quarantine', 'source_deleted'),
        ('unlink_quarantine', 'quarantine_removed'),
        ('move_quarantine_to_recovery', 'source_delete_aborted'),
    ],
)
def test_reconciliation_resyncs_mutated_directories_before_phase_append(
    tmp_path, monkeypatch, fault_operation, phase_event
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'old')
    journal, fingerprint = baseline_journal(tmp_path / 'state.jsonl', video)
    old_stat = video.stat()
    quarantine_dir = tmp_path / '.bililive-cleanup-quarantine'
    quarantine_dir.mkdir(mode=0o700)
    quarantine = quarantine_dir / 'pending'
    journal.append(
        'source_delete_intent', fingerprint=fingerprint,
        original_path=str(video),
        quarantine_path='.bililive-cleanup-quarantine/pending',
        dev=old_stat.st_dev, ino=old_stat.st_ino, size=old_stat.st_size,
        mtime_ns=old_stat.st_mtime_ns, reason='disk pressure',
        expected_journal_version=journal.replay().journal_version,
    )
    if fault_operation == 'move_quarantine_to_recovery':
        video.rename(quarantine)
        quarantine.write_bytes(b'mismatched bytes')
        video.write_bytes(b'new generation')

    original_operation = getattr(RootDirectory, fault_operation)

    def mutate_then_report_fsync_failure(root_directory, *args, **kwargs):
        original_operation(root_directory, *args, **kwargs)
        raise OSError(f'{fault_operation} fsync failed')

    with monkeypatch.context() as fault_patch:
        fault_patch.setattr(
            RootDirectory, fault_operation,
            mutate_then_report_fsync_failure,
        )
        StateAwareCleanup(
            journal, tmp_path, disk_usage=Usage(1)
        ).run((), dry_run=False)

    assert len(journal.replay().pending_deletions) == 1
    synced_directory_inodes = set()
    source_parent_inode = tmp_path.stat().st_ino
    quarantine_inode = quarantine_dir.stat().st_ino
    real_fsync = cleanup_fs_module.os.fsync

    def track_directory_fsync(file_descriptor):
        file_stat = os.fstat(file_descriptor)
        if file_stat.st_ino in (source_parent_inode, quarantine_inode):
            synced_directory_inodes.add(file_stat.st_ino)
        return real_fsync(file_descriptor)

    def required_directories_synced():
        return synced_directory_inodes == {
            source_parent_inode, quarantine_inode,
        }

    with monkeypatch.context() as retry_patch:
        retry_patch.setattr(
            cleanup_fs_module.os, 'fsync', track_directory_fsync
        )
        guarded = DirectorySyncGuardJournal(
            journal.path, phase_event, required_directories_synced
        )
        StateAwareCleanup(
            guarded, tmp_path, disk_usage=Usage(1)
        ).run((), dry_run=False)

    assert guarded.replay().pending_deletions == ()


@pytest.mark.parametrize(
    ('fault', 'fail_event', 'fsync_call'),
    [
        ('intent-append', 'source_delete_intent', None),
        ('rename-fsync', None, 2),
        ('source-deleted-append', 'source_deleted', None),
        ('unlink-fsync', None, 4),
    ],
)
def test_transaction_error_stops_before_next_candidate_and_rechecks_usage(
    tmp_path, monkeypatch, fault, fail_event, fsync_call
):
    older = tmp_path / 'older.flv'
    newer = tmp_path / 'newer.flv'
    older.write_bytes(b'older')
    newer.write_bytes(b'newer')
    import os
    os.utime(older, ns=(1_700_000_000_000_000_000,) * 2)
    os.utime(newer, ns=(1_700_000_010_000_000_000,) * 2)
    states = (
        file_state(older, event='baseline'),
        file_state(newer, event='baseline'),
    )
    current_replay = replay(states)
    journal = (
        FailOnceEventJournal(current_replay, fail_event)
        if fail_event is not None else FakeJournal(current_replay)
    )
    if fsync_call is not None:
        real_fsync = cleanup_fs_module.os.fsync
        calls = 0

        def fail_selected_fsync(file_descriptor):
            nonlocal calls
            calls += 1
            if calls == fsync_call:
                raise OSError(f'{fault} failed')
            return real_fsync(file_descriptor)

        monkeypatch.setattr(
            cleanup_fs_module.os, 'fsync', fail_selected_fsync
        )
    usage = Usage(99, 84)
    cleanup = StateAwareCleanup(journal, tmp_path, disk_usage=usage)

    result = cleanup.run(states, dry_run=False)

    assert newer.exists()
    assert len(usage.calls) == 2
    assert result.disk_usage_percent == 84
    if fault in {'intent-append', 'rename-fsync'}:
        assert older.exists()
    else:
        assert not older.exists()


def test_pending_reconciliation_error_stops_and_rechecks_usage(
    tmp_path, monkeypatch
):
    older = tmp_path / 'older.flv'
    newer = tmp_path / 'newer.flv'
    older.write_bytes(b'older')
    newer.write_bytes(b'newer')
    states = (
        file_state(older, event='baseline'),
        file_state(newer, event='baseline'),
    )
    intents = []
    for index, (state, path) in enumerate(zip(states, (older, newer)), 1):
        file_stat = path.stat()
        intents.append(JournalDeleteIntent(
            fingerprint=state.fingerprint,
            original_path=str(path),
            quarantine_path=(
                f'.bililive-cleanup-quarantine/pending-{index}'
            ),
            dev=file_stat.st_dev,
            ino=file_stat.st_ino,
            size=file_stat.st_size,
            mtime_ns=file_stat.st_mtime_ns,
            reason='disk pressure',
        ))
    current_replay = replace(
        replay(states), pending_deletions=tuple(intents)
    )
    journal = FakeJournal(current_replay)
    real_fsync = cleanup_fs_module.os.fsync
    calls = 0

    def fail_first_rename_fsync(file_descriptor):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('rename fsync failed')
        return real_fsync(file_descriptor)

    monkeypatch.setattr(
        cleanup_fs_module.os, 'fsync', fail_first_rename_fsync
    )
    usage = Usage(84)

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=usage
    ).run(states, dry_run=False)

    assert not older.exists()
    assert newer.exists()
    assert len(usage.calls) == 1
    assert result.disk_usage_percent == 84


def test_pending_unsafe_filesystem_error_stops_before_next_intent(
    tmp_path, monkeypatch
):
    older = tmp_path / 'older.flv'
    newer = tmp_path / 'newer.flv'
    older.write_bytes(b'older')
    newer.write_bytes(b'newer')
    states = (
        file_state(older, event='baseline'),
        file_state(newer, event='baseline'),
    )
    intents = []
    for index, (state, path) in enumerate(zip(states, (older, newer)), 1):
        file_stat = path.stat()
        intents.append(JournalDeleteIntent(
            fingerprint=state.fingerprint,
            original_path=str(path),
            quarantine_path=(
                f'.bililive-cleanup-quarantine/pending-{index}'
            ),
            dev=file_stat.st_dev,
            ino=file_stat.st_ino,
            size=file_stat.st_size,
            mtime_ns=file_stat.st_mtime_ns,
            reason='disk pressure',
        ))
    current_replay = replace(
        replay(states), pending_deletions=tuple(intents)
    )
    journal = FakeJournal(current_replay)
    real_lstat = RootDirectory.lstat
    calls = 0

    def fail_first_lstat(root_directory, path):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise cleanup_fs_module.UnsafeCleanupPathError(
                'wrapped filesystem error'
            )
        return real_lstat(root_directory, path)

    monkeypatch.setattr(RootDirectory, 'lstat', fail_first_lstat)
    usage = Usage(84)

    result = StateAwareCleanup(
        journal, tmp_path, disk_usage=usage
    ).run(states, dry_run=False)

    assert older.exists() and newer.exists()
    assert len(usage.calls) == 1
    assert result.disk_usage_percent == 84


def test_cleanup_never_uses_path_unlink(
    tmp_path, monkeypatch
):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<i/>', encoding='utf8')
    state = file_state(
        video,
        xml,
        event='youtube_processed',
        youtube_processed=True,
        caption_uploaded=True,
        video_id='yt123',
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))
    monkeypatch.setattr(
        Path,
        'unlink',
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError('Path.unlink must not be used')
        ),
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == (video,)
    assert not video.exists() and xml.exists()


def test_cleanup_never_removes_multiply_linked_source(tmp_path):
    video = tmp_path / 'recording.flv'
    other_link = tmp_path / 'other-link.flv'
    video.write_bytes(b'video')
    other_link.hardlink_to(video)
    file_stat = video.stat()
    state = file_state(
        video,
        fingerprint=baseline_fingerprint(
            video, file_stat.st_size, file_stat.st_mtime_ns
        ),
        event='baseline',
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert result.protected == (video,)
    assert video.exists() and other_link.exists()
    assert journal.events == []


def test_parent_symlink_swap_after_identity_check_cannot_escape_root(
    tmp_path, monkeypatch
):
    source_parent = tmp_path / 'source'
    source_parent.mkdir()
    moved_parent = tmp_path / 'moved-source'
    outside_parent = tmp_path.parent / f'{tmp_path.name}-outside'
    outside_parent.mkdir()
    video = source_parent / 'recording.flv'
    outside_video = outside_parent / video.name
    video.write_bytes(b'inside')
    outside_video.write_bytes(b'outside')
    file_stat = video.stat()
    state = file_state(
        video,
        fingerprint=baseline_fingerprint(
            video, file_stat.st_size, file_stat.st_mtime_ns
        ),
        event='baseline',
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))
    original_identity = cleanup._stat_identity
    identity_calls = 0

    def swap_after_final_identity(stat_result):
        nonlocal identity_calls
        identity = original_identity(stat_result)
        identity_calls += 1
        if identity_calls == 2:
            source_parent.rename(moved_parent)
            source_parent.symlink_to(outside_parent, target_is_directory=True)
        return identity

    monkeypatch.setattr(cleanup, '_stat_identity', swap_after_final_identity)

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == ()
    assert video in result.protected
    assert outside_video.read_bytes() == b'outside'
    assert (moved_parent / video.name).read_bytes() == b'inside'
    assert [event for event, _ in journal.events] == [
        'source_delete_intent'
    ]


@pytest.mark.parametrize(
    ('before_event', 'after_event', 'expected_phase'),
    [
        (None, 'source_delete_intent', 'intent'),
        ('source_deleted', None, 'renamed'),
        (None, 'source_deleted', 'deleted-recorded'),
        ('quarantine_removed', None, 'quarantine-unlinked'),
    ],
)
def test_cleanup_reconciles_every_quarantine_crash_window_below_threshold(
    tmp_path, before_event, after_event, expected_phase
):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')
    journal_path = tmp_path / 'state.jsonl'
    _, fingerprint = baseline_journal(journal_path, video)
    crashing = CrashJournal(
        journal_path, before=before_event, after=after_event
    )

    with pytest.raises(SimulatedCleanupCrash):
        StateAwareCleanup(
            crashing, tmp_path, disk_usage=lambda path: 99
        ).run(crashing.replay().files.values(), dry_run=False)

    replay = JsonlJournal(journal_path).replay()
    assert len(replay.pending_deletions) == 1
    intent = replay.pending_deletions[0]
    quarantine = tmp_path / intent.quarantine_path
    if expected_phase == 'intent':
        assert video.exists() and not quarantine.exists()
        assert intent.source_deleted is False
    elif expected_phase == 'renamed':
        assert not video.exists() and quarantine.exists()
        assert intent.source_deleted is False
    elif expected_phase == 'deleted-recorded':
        assert not video.exists() and quarantine.exists()
        assert intent.source_deleted is True
    else:
        assert not video.exists() and not quarantine.exists()
        assert intent.source_deleted is True

    before_dry_journal = journal_path.read_bytes()
    before_dry_video = video.exists()
    before_dry_quarantine = quarantine.exists()
    dry_result = StateAwareCleanup(
        JsonlJournal(journal_path), tmp_path, disk_usage=lambda path: 1
    ).run((), dry_run=True)

    expected_dry_deleted = (
        (video,) if expected_phase in {'intent', 'renamed'} else ()
    )
    assert dry_result.deleted == expected_dry_deleted
    assert journal_path.read_bytes() == before_dry_journal
    assert video.exists() is before_dry_video
    assert quarantine.exists() is before_dry_quarantine

    recovery_journal = CountingJournal(journal_path)
    recovered = StateAwareCleanup(
        recovery_journal, tmp_path, disk_usage=lambda path: 1
    ).run((), dry_run=False)

    replay = JsonlJournal(journal_path).replay()
    assert replay.pending_deletions == ()
    assert replay.files[fingerprint].deleted_paths == (str(video),)
    assert not video.exists() and not quarantine.exists()
    assert recovery_journal.replay_calls >= 3
    assert recovered.disk_usage_percent == 1
