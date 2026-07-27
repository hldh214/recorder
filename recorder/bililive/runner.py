import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import islice
from pathlib import Path

from recorder.bililive.media import (
    MediaProbeRetryableError,
    classify_session_files,
    inspect_media,
)
from recorder.bililive.models import (
    ClassifiedMedia,
    JournalManifest,
    JournalReplay,
    MediaInfo,
)
from recorder.danmaku.bilibili.bililive_xml import (
    prepare_bililive_xml_caption,
)
from recorder.publishing.youtube import (
    CaptionArtifact,
    PublishCheckpoint,
    PublishStatus,
)


RETRY_BASE_SECONDS = 5 * 60
RETRY_MAX_SECONDS = 6 * 60 * 60
AMBIGUOUS_TIME_SKEW_SECONDS = 5 * 60
AMBIGUOUS_DURATION_TOLERANCE_SECONDS = 1.0


_IGNORED_STATUSES = frozenset({
    'ignored_invalid',
    'ignored_tiny',
    'ignored_invalid_tail',
})


@dataclass(frozen=True)
class RunnerResult:
    status: str
    fingerprint: str | None = None
    retry_at: datetime | None = None
    message: str = ''


def _aware_datetime(value):
    if isinstance(value, datetime):
        instant = value
    elif isinstance(value, str):
        normalized = value[:-1] + '+00:00' if value.endswith(('Z', 'z')) else value
        instant = datetime.fromisoformat(normalized)
    else:
        raise TypeError('timestamp must be a datetime or ISO string')
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('timestamp must be timezone-aware')
    return instant


def _identity(path):
    try:
        stat_result = Path(path).stat()
    except OSError:
        return None
    return stat_result.st_size, stat_result.st_mtime_ns


class BililivePublishRunner:
    def __init__(
        self,
        journal,
        publisher,
        room_id=None,
        state_dir=None,
        clock=None,
        recent_uploads=None,
        probe=inspect_media,
        classifier=classify_session_files,
        caption_provider=prepare_bililive_xml_caption,
    ):
        self.journal = journal
        self.publisher = publisher
        self.room_id = room_id
        journal_path = getattr(journal, 'path', None)
        default_state = Path(journal_path).parent if journal_path is not None else Path('.')
        self.state_dir = Path(state_dir) if state_dir is not None else default_state
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.probe = probe
        self.classifier = classifier
        self.caption_provider = caption_provider
        if recent_uploads is None:
            youtube = getattr(publisher, 'youtube', None)
            list_recent = getattr(youtube, 'list_recent_uploads', None)
            self.recent_uploads = (
                (lambda: list_recent(max_results=50))
                if list_recent is not None else (lambda: [])
            )
        else:
            self.recent_uploads = recent_uploads
        self._expected_snapshots = {}
        self._manifest_rooms = {}

    def run_pending_once(self, replay: JournalReplay) -> RunnerResult | None:
        manifests = tuple(
            manifest for manifest in replay.manifests if not manifest.completed
        )
        for manifest in manifests:
            mismatch = self._manifest_mismatch(manifest)
            if mismatch is not None:
                return RunnerResult('settling', message=mismatch)

        for manifest in manifests:
            classification_result = self._ensure_manifest_classified(
                manifest, replay
            )
            if classification_result is not None:
                return classification_result
            replay = self.journal.replay()

        candidate = self._select_due_candidate(replay)
        if candidate is None:
            completed = self._complete_finished_manifests(replay)
            return RunnerResult('complete') if completed else None

        classified, manifest, unresolved_upload = candidate
        fingerprint = classified.media.fingerprint
        self._expected_snapshots[fingerprint] = dict(manifest.snapshot)
        self._manifest_rooms[fingerprint] = manifest.room_id
        try:
            if unresolved_upload:
                result = self.recover_ambiguous(
                    classified, caption_provider=self.caption_provider
                )
            else:
                result = self.publish_one(
                    classified, caption_provider=self.caption_provider
                )
        finally:
            self._expected_snapshots.pop(fingerprint, None)
            self._manifest_rooms.pop(fingerprint, None)

        self._complete_finished_manifests(self.journal.replay())
        return result

    def publish_session(self, classified_media):
        results = []
        if isinstance(classified_media, Mapping):
            classified_media = classified_media.values()
        ordered = sorted(
            classified_media,
            key=lambda item: (item.media.start_time, item.media.path.name),
        )
        for classified in ordered:
            results.append(self.publish_one(
                classified, caption_provider=self.caption_provider
            ))
        return tuple(results)

    def publish_one(
        self,
        classified: ClassifiedMedia,
        caption_provider=prepare_bililive_xml_caption,
    ) -> RunnerResult:
        media = classified.media
        fingerprint = media.fingerprint
        if classified.status in _IGNORED_STATUSES:
            self._append_classification(classified, manifest_id=None)
            return RunnerResult(classified.status, fingerprint, message=classified.reason)
        if classified.status != 'ready':
            raise ValueError(f'unknown media classification {classified.status!r}')

        replay = self.journal.replay()
        state = replay.files.get(fingerprint)
        if state is None:
            self._append_classification(classified, manifest_id=None)
            state = self.journal.replay().files[fingerprint]
        if state.ambiguous or state.event == 'ambiguous':
            return RunnerResult('ambiguous', fingerprint, message=state.error_message or '')
        if state.event == 'fatal':
            return RunnerResult('fatal', fingerprint, message=state.error_message or '')
        if (
            state.event == 'upload_started'
            and state.video_id is None
            and not state.video_upload_rejected
        ):
            return self.recover_ambiguous(
                classified, caption_provider=caption_provider
            )

        expected = self._expected_for(classified)
        mismatch = self._snapshot_mismatch(media, expected)
        if mismatch is not None:
            return RunnerResult('settling', fingerprint, message=mismatch)

        caption = None
        if caption_provider is None:
            if state.caption_status != 'not_requested':
                self.journal.append(
                    'caption_status',
                    fingerprint=fingerprint,
                    caption_status='not_requested',
                )
        else:
            output_path = self.state_dir / 'captions' / f'{fingerprint}.vtt'
            artifact = caption_provider(
                media.xml_path,
                output_path,
                media.start_time,
                media.duration,
            )
            caption = CaptionArtifact(
                path=artifact.path,
                highlights=artifact.highlights,
                status=artifact.status,
                temporary=artifact.temporary,
            )
            if (
                state.caption_status != artifact.status
                or artifact.error_message
            ):
                self.journal.append(
                    'caption_status',
                    fingerprint=fingerprint,
                    caption_status=artifact.status,
                    error_message=artifact.error_message,
                )

        mismatch = self._snapshot_mismatch(media, expected)
        if mismatch is not None:
            return RunnerResult('settling', fingerprint, message=mismatch)

        state = self.journal.replay().files[fingerprint]
        checkpoint = PublishCheckpoint(
            video_id=state.video_id,
            video_upload_rejected=state.video_upload_rejected,
            video_uploaded=state.video_id is not None,
            caption_uploaded=state.caption_uploaded,
            playlist_inserted=state.playlist_inserted,
            youtube_processed=state.youtube_processed,
            description_fingerprint=state.description_fingerprint,
        )
        callback_ran = False

        def before_video_upload(title, description_fingerprint):
            nonlocal callback_ran
            self.journal.append(
                'upload_started',
                fingerprint=fingerprint,
                file=str(media.path),
                xml_file=str(media.xml_path),
                title=title,
                duration=media.duration,
                description_fingerprint=description_fingerprint,
                upload_started_at=self._now().isoformat(),
                attempt=state.attempt,
            )
            callback_ran = True

        before_upload = before_video_upload if state.video_id is None else None
        try:
            result = self.publisher.publish_video(
                video_path=media.path,
                source_type='bilibili',
                source_name=str(self._room_for(fingerprint)),
                start=media.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                stream_title=media.stream_title,
                caption=caption,
                checkpoint=checkpoint,
                before_video_upload=before_upload,
            )
        except Exception as exception:
            if callback_ran:
                self.journal.append(
                    'ambiguous',
                    fingerprint=fingerprint,
                    stage='video',
                    message=str(exception),
                )
                return RunnerResult('ambiguous', fingerprint, message=str(exception))
            return self._schedule_retry(
                fingerprint, state, 'publisher', PublishStatus.RETRYABLE.value,
                str(exception), quota=False,
            )

        return self._record_publish_result(
            classified, state, result, callback_ran
        )

    def recover_ambiguous(
        self,
        classified: ClassifiedMedia,
        caption_provider=prepare_bililive_xml_caption,
    ) -> RunnerResult:
        fingerprint = classified.media.fingerprint
        state = self.journal.replay().files.get(fingerprint)
        if (
            state is None
            or state.event != 'upload_started'
            or state.video_id is not None
            or state.video_upload_rejected
        ):
            return RunnerResult(
                'ambiguous', fingerprint,
                message='no unresolved upload_started checkpoint to recover',
            )

        now = self._now()
        try:
            upload_started_at = _aware_datetime(state.upload_started_at)
            uploads = self.recent_uploads()
        except Exception as exception:
            self.journal.append(
                'ambiguous', fingerprint=fingerprint, stage='video',
                message=f'could not reconcile recent uploads: {exception}',
            )
            return RunnerResult('ambiguous', fingerprint, message=str(exception))

        lower = upload_started_at - timedelta(
            seconds=AMBIGUOUS_TIME_SKEW_SECONDS
        )
        upper = now + timedelta(seconds=AMBIGUOUS_TIME_SKEW_SECONDS)
        matches = []
        for upload in islice(uploads, 50):
            try:
                duration = upload.get('duration_seconds')
                if (
                    isinstance(duration, bool)
                    or not isinstance(duration, (int, float))
                    or not math.isfinite(duration)
                    or state.duration is None
                    or abs(duration - state.duration)
                    > AMBIGUOUS_DURATION_TOLERANCE_SECONDS
                ):
                    continue
                published_at = _aware_datetime(upload.get('published_at'))
                if upload.get('title') != state.title:
                    continue
                if not lower <= published_at <= upper:
                    continue
                video_id = upload.get('video_id')
                if not isinstance(video_id, str) or not video_id:
                    continue
            except (AttributeError, TypeError, ValueError):
                continue
            matches.append(video_id)

        if len(matches) != 1:
            message = f'recent upload reconciliation found {len(matches)} matches'
            self.journal.append(
                'ambiguous', fingerprint=fingerprint, stage='video', message=message
            )
            return RunnerResult('ambiguous', fingerprint, message=message)

        self.journal.append(
            'video_uploaded', fingerprint=fingerprint, video_id=matches[0]
        )
        return self.publish_one(
            classified, caption_provider=caption_provider
        )

    def _record_publish_result(self, classified, previous, result, callback_ran):
        fingerprint = classified.media.fingerprint
        current = previous
        if result.video_id is not None and current.video_id is None:
            self.journal.append(
                'video_uploaded', fingerprint=fingerprint, video_id=result.video_id
            )
            current = self.journal.replay().files[fingerprint]
        if (
            result.video_id is not None
            and result.description_fingerprint is not None
            and (
                previous.video_id is None
                or current.description_fingerprint
                != result.description_fingerprint
            )
        ):
            self.journal.append(
                'description_updated',
                fingerprint=fingerprint,
                description_fingerprint=result.description_fingerprint,
            )
            current = self.journal.replay().files[fingerprint]
        if result.caption_uploaded and not current.caption_uploaded:
            self.journal.append('caption_uploaded', fingerprint=fingerprint)
            current = self.journal.replay().files[fingerprint]
        if result.playlist_inserted and not current.playlist_inserted:
            self.journal.append('playlist_inserted', fingerprint=fingerprint)
            current = self.journal.replay().files[fingerprint]
        if result.youtube_processed and not current.youtube_processed:
            self.journal.append('youtube_processed', fingerprint=fingerprint)
            current = self.journal.replay().files[fingerprint]
        if result.caption_status and current.caption_status != result.caption_status:
            self.journal.append(
                'caption_status', fingerprint=fingerprint,
                caption_status=result.caption_status,
                error_message=(
                    result.error_message if result.error_stage == 'caption' else None
                ),
            )
            current = self.journal.replay().files[fingerprint]

        if (
            result.video_id is None
            and result.remote_outcome_unknown
        ):
            self.journal.append(
                'ambiguous', fingerprint=fingerprint,
                stage=result.error_stage or 'video',
                message=result.error_message or 'remote upload outcome is unknown',
            )
            return RunnerResult(
                'ambiguous', fingerprint, message=result.error_message or ''
            )

        if (
            callback_ran
            and result.video_id is None
            and not result.remote_outcome_unknown
        ):
            self.journal.append(
                'video_upload_rejected',
                fingerprint=fingerprint,
                stage=result.error_stage,
                message=result.error_message,
            )
            current = self.journal.replay().files[fingerprint]

        status = result.status
        if status is PublishStatus.COMPLETE:
            if result.caption_status in ('missing', 'invalid'):
                return RunnerResult(
                    'caption_pending', fingerprint,
                    message=result.error_message or result.caption_status,
                )
            return RunnerResult('complete', fingerprint)
        if status in (PublishStatus.RETRYABLE, PublishStatus.QUOTA_EXCEEDED):
            return self._schedule_retry(
                fingerprint,
                current,
                result.error_stage or 'video',
                status.value,
                result.error_message or '',
                quota=status is PublishStatus.QUOTA_EXCEEDED,
            )
        if status is PublishStatus.PENDING:
            return self._schedule_retry(
                fingerprint,
                current,
                result.error_stage or 'processing',
                status.value,
                result.error_message or 'YouTube processing is pending',
                quota=False,
            )

        event = 'ambiguous' if getattr(status, 'value', status) == 'ambiguous' else 'fatal'
        self.journal.append(
            event,
            fingerprint=fingerprint,
            stage=result.error_stage or 'publication',
            message=result.error_message or str(status),
        )
        return RunnerResult(event, fingerprint, message=result.error_message or '')

    def _schedule_retry(self, fingerprint, state, stage, status, message, quota):
        continuing_stage = state.stage == stage or (
            stage == 'video'
            and state.video_id is None
            and state.upload_started_at is not None
        )
        attempt = state.attempt + 1 if continuing_stage else 1
        delay = (
            RETRY_MAX_SECONDS
            if quota else min(
                RETRY_BASE_SECONDS * (2 ** max(0, attempt - 1)),
                RETRY_MAX_SECONDS,
            )
        )
        retry_at = self._now() + timedelta(seconds=delay)
        self.journal.append(
            'stage_retry_scheduled',
            fingerprint=fingerprint,
            stage=stage,
            status=status,
            retry_at=retry_at.isoformat(),
            attempt=attempt,
            error_stage=stage,
            error_message=message,
        )
        return RunnerResult('retry_scheduled', fingerprint, retry_at, message)

    def _ensure_manifest_classified(self, manifest, replay):
        states_by_path = {
            state.file: state
            for state in replay.files.values()
            if state.manifest_id == manifest.manifest_id
        }
        if all(path in states_by_path for path in manifest.flv_paths):
            return None
        try:
            inspected = tuple(self.probe(path) for path in manifest.flv_paths)
        except MediaProbeRetryableError as exception:
            return RunnerResult('retryable', message=str(exception))
        classified = self.classifier(inspected)
        mismatch = self._manifest_mismatch(manifest)
        if mismatch is not None:
            return RunnerResult('settling', message=mismatch)
        for path in manifest.flv_paths:
            if path in states_by_path:
                continue
            media = next(item for item in inspected if str(item.path) == path)
            self._append_classification(
                classified[media.fingerprint], manifest.manifest_id
            )
        return None

    def _append_classification(self, classified, manifest_id):
        media = classified.media
        fields = {
            'fingerprint': media.fingerprint,
            'manifest_id': manifest_id,
            'file': str(media.path),
            'xml_file': str(media.xml_path),
            'title': media.stream_title,
            'stream_title': media.stream_title,
            'start_time': media.start_time.isoformat(),
            'duration': media.duration,
            'caption_status': (
                'pending' if classified.status == 'ready' else 'not_requested'
            ),
        }
        if classified.status == 'ready':
            self.journal.append('file_ready', **fields)
        else:
            self.journal.append(
                classified.status,
                **fields,
                reason=classified.reason,
                error_stage='probe' if media.probe_error else 'classification',
                error_message=media.probe_error,
            )

    def _select_due_candidate(self, replay):
        candidates = []
        for manifest in replay.manifests:
            if manifest.completed:
                continue
            for path in manifest.flv_paths:
                state = next((
                    item for item in replay.files.values()
                    if item.manifest_id == manifest.manifest_id and item.file == path
                ), None)
                if state is None or state.event in _IGNORED_STATUSES:
                    continue
                if state.event in ('fatal', 'ambiguous') or state.ambiguous:
                    continue
                if state.retry_at is not None and _aware_datetime(state.retry_at) > self._now():
                    continue
                if self._state_complete(state, manifest.room_id):
                    continue
                classified = self._classified_from_state(state, manifest)
                unresolved = (
                    state.event == 'upload_started'
                    and state.video_id is None
                    and not state.video_upload_rejected
                )
                priority = 0 if state.video_id is None else 1
                candidates.append((
                    priority,
                    classified.media.start_time,
                    _aware_datetime(manifest.settled_at),
                    str(classified.media.path),
                    classified,
                    manifest,
                    unresolved,
                ))
        if not candidates:
            return None
        selected = min(candidates, key=lambda item: item[:4])
        return selected[4], selected[5], selected[6]

    def _classified_from_state(self, state, manifest):
        size, mtime_ns = manifest.snapshot[state.file]
        start_time = _aware_datetime(state.start_time)
        path = Path(state.file)
        return ClassifiedMedia(
            media=MediaInfo(
                path=path,
                xml_path=Path(state.xml_file or path.with_suffix('.xml')),
                size=size,
                mtime_ns=mtime_ns,
                start_time=start_time,
                stream_title=state.stream_title,
                duration=state.duration,
                has_video=True,
                has_audio=True,
                fingerprint=state.fingerprint,
            ),
            status='ready',
            reason='replayed ready manifest',
        )

    def _state_complete(self, state, room_id):
        if state.event in _IGNORED_STATUSES:
            return True
        caption_complete = (
            state.caption_uploaded
            or state.caption_status == 'not_requested'
        )
        return bool(
            state.video_id
            and state.youtube_processed
            and caption_complete
            and (not self._playlist_required(room_id) or state.playlist_inserted)
        )

    def _playlist_required(self, room_id):
        config = getattr(self.publisher, 'config', None)
        try:
            return bool(config['source'][str(room_id)].get('playlist_id'))
        except (AttributeError, KeyError, TypeError):
            return False

    def _complete_finished_manifests(self, replay):
        appended = False
        for manifest in replay.manifests:
            if manifest.completed:
                continue
            states = []
            for path in manifest.flv_paths:
                state = next((
                    item for item in replay.files.values()
                    if item.manifest_id == manifest.manifest_id and item.file == path
                ), None)
                states.append(state)
            if states and all(
                state is not None and self._state_complete(state, manifest.room_id)
                for state in states
            ):
                self.journal.append(
                    'session_manifest_completed', manifest_id=manifest.manifest_id
                )
                appended = True
        return appended

    def _expected_for(self, classified):
        media = classified.media
        expected = self._expected_snapshots.get(media.fingerprint)
        if expected is not None:
            expected = dict(expected)
            xml_path = str(media.xml_path)
            if xml_path not in expected:
                xml_identity = _identity(media.xml_path)
                if xml_identity is not None:
                    expected[xml_path] = xml_identity
            return expected
        dynamic = {str(media.path): (media.size, media.mtime_ns)}
        xml_identity = _identity(media.xml_path)
        if xml_identity is not None:
            dynamic[str(media.xml_path)] = xml_identity
        return dynamic

    def _manifest_mismatch(self, manifest: JournalManifest):
        for path, expected in manifest.snapshot.items():
            if _identity(path) != tuple(expected):
                return f'frozen manifest path changed: {path}'
        return None

    def _snapshot_mismatch(self, media, expected):
        flv_path = str(media.path)
        if _identity(flv_path) != tuple(expected[flv_path]):
            return f'frozen FLV identity changed: {flv_path}'
        xml_path = str(media.xml_path)
        if xml_path in expected and _identity(xml_path) != tuple(expected[xml_path]):
            return f'frozen XML identity changed: {xml_path}'
        return None

    def _room_for(self, fingerprint):
        room = self._manifest_rooms.get(fingerprint, self.room_id)
        return '' if room is None else room

    def _now(self):
        return _aware_datetime(self.clock()).astimezone(timezone.utc)
