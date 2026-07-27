from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from recorder.bililive.cleanup import (
    DISK_CLEANUP_THRESHOLD_PERCENT,
    StateAwareCleanup,
)
from recorder.bililive.journal import JsonlJournal
from recorder.bililive.models import (
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
    fingerprint='fp1',
    event='file_ready',
    manifest_id=None,
    youtube_processed=False,
    caption_uploaded=False,
    video_id=None,
):
    return JournalFileState(
        fingerprint=fingerprint,
        event=event,
        manifest_id=manifest_id,
        file=str(video),
        xml_file=str(xml) if xml is not None else None,
        youtube_processed=youtube_processed,
        caption_uploaded=caption_uploaded,
        video_id=video_id,
    )


def session(state=SessionState.WAITING, paths=()):
    active = state in {
        SessionState.SKIP_CURRENT_SESSION,
        SessionState.RECORDING,
        SessionState.SETTLING,
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


class Usage:
    def __init__(self, *values):
        self.values = list(values)
        self.calls = []

    def __call__(self, path):
        self.calls.append(Path(path))
        if len(self.values) > 1:
            return self.values.pop(0)
        return self.values[0]


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
    assert journal.events == [(
        'source_deleted',
        {
            'fingerprint': 'fp1',
            'path': str(video),
            'reason': 'disk usage at or above 85 percent',
        },
    )]


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
    state = replace(
        file_state(video, xml),
        caption_source_xml_size=xml_stat.st_size,
        caption_source_xml_mtime_ns=xml_stat.st_mtime_ns,
        **state_changes,
    )
    journal, cleanup = cleanup_for(tmp_path, [state], Usage(99))

    result = cleanup.run([state], dry_run=False)

    assert set(result.protected) == {video, xml}
    assert video.exists() and xml.exists()
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
        file_state(
            old_video,
            old_xml,
            fingerprint='baseline',
            event='baseline',
        ),
    ]
    journal, cleanup = cleanup_for(tmp_path, states, Usage(99, 99, 99, 84))

    result = cleanup.run(states, dry_run=False)

    assert result.deleted == (old_video, old_xml, new_video)
    assert [fields['fingerprint'] for _, fields in journal.events] == [
        'baseline', 'baseline', 'ignored'
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
    assert journal.events[0][1]['path'] == str(xml)


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
        file_state(first, fingerprint='first', event='baseline'),
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


def test_cleanup_stops_after_usage_falls_below_threshold(tmp_path):
    old = tmp_path / 'old.flv'
    newer = tmp_path / 'new.flv'
    old.write_bytes(b'old')
    newer.write_bytes(b'new')
    import os
    os.utime(old, ns=(1_700_000_000_000_000_000,) * 2)
    os.utime(newer, ns=(1_700_000_010_000_000_000,) * 2)
    states = [
        file_state(old, fingerprint='old', event='baseline'),
        file_state(newer, fingerprint='new', event='baseline'),
    ]
    _, cleanup = cleanup_for(tmp_path, states, Usage(90, 84))

    result = cleanup.run(states, dry_run=False)

    assert result.deleted == (old,)
    assert newer.exists()
    assert result.disk_usage_percent == 84


def test_flv_and_xml_deletion_remain_independent_after_unlink_error(
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
    original_unlink = Path.unlink

    def fail_video(path, *args, **kwargs):
        if path == video:
            raise PermissionError('busy')
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'unlink', fail_video)

    with pytest.raises(PermissionError, match='busy'):
        cleanup.run([state], dry_run=False)

    assert video.exists() and xml.exists()
    assert journal.events == []
