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
        self._settling_paths = {}

    def run_pending_once(self, replay: JournalReplay) -> RunnerResult | None:
        manifests = tuple(
            manifest for manifest in replay.manifests
            if not manifest.completed and not manifest.invalidated
        )
        eligible_manifest_ids = set()
        deferred_result = None
        for manifest in manifests:
            changed_paths = self._manifest_changed_paths(manifest)
            if changed_paths:
                if deferred_result is None:
                    deferred_result = self._invalidate_changed_manifest(
                        manifest, changed_paths
                    )
                else:
                    self._invalidate_changed_manifest(
                        manifest, changed_paths
                    )
                continue
            classification_result = self._ensure_manifest_classified(
                manifest, replay
            )
            if classification_result is not None:
                if deferred_result is None:
                    deferred_result = classification_result
                continue
            eligible_manifest_ids.add(manifest.manifest_id)
            replay = self.journal.replay()

        state_index = self._file_state_index(replay)
        candidate = self._select_due_candidate(
            replay,
            eligible_manifest_ids=eligible_manifest_ids,
            state_index=state_index,
        )
        if candidate is None:
            completed = self._complete_finished_manifests(
                replay,
                eligible_manifest_ids=eligible_manifest_ids,
                state_index=state_index,
            )
            if completed:
                return RunnerResult('complete')
            return deferred_result

        classified, manifest, unresolved_upload = candidate
        fingerprint = classified.media.fingerprint
        expected_snapshot = dict(manifest.snapshot)
        xml_path = str(classified.media.xml_path)
        expected_snapshot.setdefault(xml_path, _identity(xml_path))
        self._expected_snapshots[fingerprint] = expected_snapshot
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
            settling_paths = self._settling_paths.get(fingerprint, ())
            if result.status == 'settling' and settling_paths:
                result = self._invalidate_changed_manifest(
                    manifest,
                    settling_paths,
                    reason=result.message,
                )
            else:
                post_remote_changes = self._snapshot_changed_paths(
                    self._expected_snapshots[fingerprint]
                )
                if post_remote_changes:
                    result = self._invalidate_changed_manifest(
                        manifest,
                        post_remote_changes,
                        reason=(
                            'frozen source identity changed after publication: '
                            + ', '.join(post_remote_changes)
                        ),
                    )
        finally:
            self._expected_snapshots.pop(fingerprint, None)
            self._manifest_rooms.pop(fingerprint, None)
            self._settling_paths.pop(fingerprint, None)

        completion_replay = self.journal.replay()
        self._complete_finished_manifests(
            completion_replay,
            eligible_manifest_ids=eligible_manifest_ids,
            state_index=self._file_state_index(completion_replay),
        )
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
        self._settling_paths.pop(fingerprint, None)
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
        caption_error_message = None
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
            caption_error_message = artifact.error_message
            if (
                state.caption_status != artifact.status
                or (
                    artifact.error_message is not None
                    and state.error_message != artifact.error_message
                )
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

        if (
            caption is not None
            and caption.status == 'ready'
            and caption.path is not None
        ):
            xml_path = str(media.xml_path)
            xml_identity = _identity(media.xml_path)
            expected_xml_identity = expected.get(xml_path)
            if (
                xml_identity is None
                or expected_xml_identity is None
                or tuple(xml_identity) != tuple(expected_xml_identity)
            ):
                self._settling_paths[fingerprint] = (xml_path,)
                return RunnerResult(
                    'settling', fingerprint,
                    message=f'frozen XML identity changed: {xml_path}',
                )
            durable_xml_identity = (
                state.caption_source_xml_size,
                state.caption_source_xml_mtime_ns,
            )
            durable_identity_complete = all(
                value is not None for value in durable_xml_identity
            )
            manifest_has_xml_identity = any(
                manifest.manifest_id == state.manifest_id
                and xml_path in manifest.snapshot
                for manifest in replay.manifests
            )
            if (
                durable_identity_complete
                and tuple(durable_xml_identity) != tuple(xml_identity)
            ) or (
                any(value is not None for value in durable_xml_identity)
                and not durable_identity_complete
            ) or (
                not durable_identity_complete
                and not manifest_has_xml_identity
                and (
                    state.caption_uploaded
                    or state.caption_refresh_required
                )
            ):
                self._settling_paths[fingerprint] = (xml_path,)
                return RunnerResult(
                    'settling', fingerprint,
                    message=f'durable XML identity changed: {xml_path}',
                )
            self.journal.append(
                'caption_source_frozen',
                fingerprint=fingerprint,
                xml_file=xml_path,
                caption_source_xml_size=xml_identity[0],
                caption_source_xml_mtime_ns=xml_identity[1],
            )

        state = self.journal.replay().files[fingerprint]
        checkpoint = PublishCheckpoint(
            video_id=state.video_id,
            video_upload_rejected=state.video_upload_rejected,
            video_uploaded=state.video_id is not None,
            caption_uploaded=state.caption_uploaded,
            caption_refresh_required=state.caption_refresh_required,
            caption_track_id=state.caption_track_id,
            playlist_inserted=state.playlist_inserted,
            youtube_processed=state.youtube_processed,
            description_updated=state.description_updated,
            description_fingerprint=state.description_fingerprint,
        )
        callback_ran = False
        checkpointed_stages = set()

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

        def on_stage_completed(stage, **fields):
            if stage == 'video_uploaded':
                self.journal.append(
                    'video_uploaded',
                    fingerprint=fingerprint,
                    video_id=fields['video_id'],
                )
            elif stage == 'description_updated':
                self.journal.append(
                    'description_updated',
                    fingerprint=fingerprint,
                    description_fingerprint=fields[
                        'description_fingerprint'
                    ],
                )
            elif stage == 'caption_uploaded':
                self.journal.append(
                    stage,
                    fingerprint=fingerprint,
                    caption_track_id=fields.get('caption_track_id'),
                )
            elif stage in {'playlist_inserted', 'youtube_processed'}:
                self.journal.append(stage, fingerprint=fingerprint)
            else:
                raise ValueError(f'unknown publication stage {stage!r}')
            checkpointed_stages.add(stage)

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
                on_stage_completed=on_stage_completed,
            )
        except Exception as exception:
            current = self.journal.replay().files[fingerprint]
            if callback_ran and current.video_id is None:
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
            classified,
            state,
            result,
            callback_ran,
            checkpointed_stages,
            caption_error_message,
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

    def _record_publish_result(
        self,
        classified,
        previous,
        result,
        callback_ran,
        checkpointed_stages,
        caption_error_message,
    ):
        fingerprint = classified.media.fingerprint
        current = self.journal.replay().files[fingerprint]
        if result.video_id is not None and current.video_id is None:
            self.journal.append(
                'video_uploaded', fingerprint=fingerprint, video_id=result.video_id
            )
            current = self.journal.replay().files[fingerprint]
        if (
            result.video_id is not None
            and result.description_fingerprint is not None
            and 'description_updated' not in checkpointed_stages
            and (
                not current.description_updated
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
        if result.caption_uploaded and (
            not current.caption_uploaded
            or current.caption_track_id != result.caption_track_id
        ):
            self.journal.append(
                'caption_uploaded',
                fingerprint=fingerprint,
                caption_track_id=result.caption_track_id,
            )
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
                return self._schedule_retry(
                    fingerprint,
                    current,
                    'caption',
                    PublishStatus.RETRYABLE.value,
                    caption_error_message
                    or current.error_message
                    or f'caption XML is {result.caption_status}',
                    quota=False,
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
        changed_paths = self._manifest_changed_paths(manifest)
        if changed_paths:
            return self._invalidate_changed_manifest(
                manifest, changed_paths
            )
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

    def _select_due_candidate(
        self, replay, eligible_manifest_ids=None, state_index=None
    ):
        candidates = []
        now = self._now()
        if state_index is None:
            state_index = self._file_state_index(replay)
        for manifest in replay.manifests:
            if manifest.completed or manifest.invalidated:
                continue
            if (
                eligible_manifest_ids is not None
                and manifest.manifest_id not in eligible_manifest_ids
            ):
                continue
            for path in manifest.flv_paths:
                state = state_index.get((manifest.manifest_id, path))
                if state is None or state.event in _IGNORED_STATUSES:
                    continue
                if state.event in ('fatal', 'ambiguous') or state.ambiguous:
                    continue
                if (
                    state.retry_at is not None
                    and _aware_datetime(state.retry_at) > now
                ):
                    continue
                if self._state_complete(state, manifest.room_id):
                    continue
                classified = self._classified_from_state(state, manifest)
                unresolved = (
                    state.event == 'upload_started'
                    and state.video_id is None
                    and not state.video_upload_rejected
                )
                candidates.append((
                    _aware_datetime(manifest.settled_at),
                    classified.media.start_time,
                    str(classified.media.path),
                    classified,
                    manifest,
                    unresolved,
                ))
        if not candidates:
            return None
        selected = min(candidates, key=lambda item: item[:3])
        return selected[3], selected[4], selected[5]

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
        playlist_required = self._playlist_requirement(room_id)
        if playlist_required is None:
            return False
        return bool(
            state.video_id
            and state.youtube_processed
            and caption_complete
            and (not playlist_required or state.playlist_inserted)
        )

    def _playlist_requirement(self, room_id):
        config = getattr(self.publisher, 'config', None)
        if not isinstance(config, Mapping):
            return None
        sources = config.get('source')
        if not isinstance(sources, Mapping):
            return None
        source = sources.get(str(room_id))
        if not isinstance(source, Mapping):
            return None
        playlist_id = source.get('playlist_id')
        if playlist_id is None or playlist_id == '':
            return False
        if not isinstance(playlist_id, str):
            return None
        return True

    def _complete_finished_manifests(
        self, replay, eligible_manifest_ids=None, state_index=None
    ):
        appended = False
        if state_index is None:
            state_index = self._file_state_index(replay)
        for manifest in replay.manifests:
            if manifest.completed or manifest.invalidated:
                continue
            if (
                eligible_manifest_ids is not None
                and manifest.manifest_id not in eligible_manifest_ids
            ):
                continue
            states = []
            for path in manifest.flv_paths:
                state = state_index.get((manifest.manifest_id, path))
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

    @staticmethod
    def _file_state_index(replay):
        index = {}
        for state in replay.files.values():
            if state.manifest_id is None or state.file is None:
                continue
            key = (state.manifest_id, state.file)
            existing = index.get(key)
            if existing is not None and existing.fingerprint != state.fingerprint:
                raise ValueError(
                    f'duplicate manifest/file binding {key!r} for '
                    f'fingerprints {existing.fingerprint!r} and '
                    f'{state.fingerprint!r}'
                )
            index[key] = state
        return index

    def _expected_for(self, classified):
        media = classified.media
        expected = self._expected_snapshots.get(media.fingerprint)
        if expected is not None:
            return dict(expected)
        dynamic = {str(media.path): (media.size, media.mtime_ns)}
        xml_identity = _identity(media.xml_path)
        if xml_identity is not None:
            dynamic[str(media.xml_path)] = xml_identity
        return dynamic

    def _manifest_changed_paths(self, manifest: JournalManifest):
        return tuple(
            path for path, expected in manifest.snapshot.items()
            if _identity(path) != tuple(expected)
        )

    def _invalidate_changed_manifest(
        self, manifest, changed_paths, reason=None
    ):
        message = reason or (
            'frozen manifest identity changed: ' + ', '.join(changed_paths)
        )
        self.journal.append(
            'session_manifest_changed',
            manifest_id=manifest.manifest_id,
            detected_at=self._now().isoformat(),
            reason=message,
            changed_paths=changed_paths,
        )
        return RunnerResult('resettle_pending', message=message)

    def _snapshot_mismatch(self, media, expected):
        changed_paths = self._snapshot_changed_paths(expected)
        if changed_paths:
            self._settling_paths[media.fingerprint] = changed_paths
            labels = ', '.join(
                f'{Path(path).suffix.upper().lstrip(".")} identity changed: {path}'
                for path in changed_paths
            )
            return f'frozen {labels}'
        return None

    @staticmethod
    def _snapshot_changed_paths(expected):
        return tuple(
            path for path, identity in expected.items()
            if _identity(path) != (
                tuple(identity) if identity is not None else None
            )
        )

    def _room_for(self, fingerprint):
        room = self._manifest_rooms.get(fingerprint, self.room_id)
        return '' if room is None else room

    def _now(self):
        return _aware_datetime(self.clock()).astimezone(timezone.utc)
