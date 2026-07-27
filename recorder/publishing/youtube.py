import hashlib
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import httplib2

from recorder.destination.youtube import (
    CAPTION_UPLOAD_QUOTA_EXCEEDED,
    CAPTION_UPLOAD_SUCCESS,
    YOUTUBE_QUOTA_REASONS,
    _http_error_reasons,
)


YOUTUBE_RATE_LIMIT_REASONS = frozenset(('rateLimitExceeded', 'userRateLimitExceeded'))
RETRYABLE_HTTP_STATUSES = frozenset((408, 429, 500, 502, 503, 504))
RETRYABLE_HTTPLIB2_EXCEPTIONS = (
    httplib2.FailedToDecompressContent,
    httplib2.ServerNotFoundError,
)


class _CaptionSourceAliasError(ValueError):
    pass


class PublishStatus(str, Enum):
    COMPLETE = 'complete'
    PENDING = 'pending'
    RETRYABLE = 'retryable'
    QUOTA_EXCEEDED = 'quota_exceeded'
    FATAL = 'fatal'


@dataclass(frozen=True)
class CaptionArtifact:
    path: Path | None
    highlights: str = ''
    status: str = 'ready'
    temporary: bool = True


@dataclass(frozen=True)
class PublishCheckpoint:
    video_id: str | None = None
    video_upload_rejected: bool = False
    video_uploaded: bool = False
    caption_uploaded: bool = False
    playlist_inserted: bool = False
    youtube_processed: bool = False
    description_fingerprint: str | None = None


@dataclass(frozen=True)
class PublishResult:
    status: PublishStatus
    video_id: str | None = None
    video_uploaded: bool = False
    caption_uploaded: bool = False
    playlist_inserted: bool = False
    youtube_processed: bool = False
    description_fingerprint: str | None = None
    caption_status: str = 'not_requested'
    error_stage: str | None = None
    error_message: str | None = None
    remote_outcome_unknown: bool = False


def _http_status(exception):
    response = getattr(exception, 'resp', None)
    status = getattr(response, 'status', None)
    if status is None:
        status = getattr(exception, 'status_code', None)
    try:
        return int(status) if status is not None else None
    except (TypeError, ValueError):
        return None


def _classify_error(exception):
    reasons = _http_error_reasons(exception)
    if reasons & YOUTUBE_QUOTA_REASONS:
        return PublishStatus.QUOTA_EXCEEDED
    if reasons & YOUTUBE_RATE_LIMIT_REASONS:
        return PublishStatus.RETRYABLE

    status = _http_status(exception)
    if status in RETRYABLE_HTTP_STATUSES or (status is not None and status >= 500):
        return PublishStatus.RETRYABLE
    if isinstance(exception, (OSError,) + RETRYABLE_HTTPLIB2_EXCEPTIONS):
        return PublishStatus.RETRYABLE
    return PublishStatus.FATAL


def _upload_outcome_unknown(exception, status):
    if status is not PublishStatus.RETRYABLE:
        return False
    reasons = _http_error_reasons(exception)
    if reasons & YOUTUBE_RATE_LIMIT_REASONS:
        return False
    return _http_status(exception) != 429


def _validated_caption_path(video_path, caption_path):
    candidate = Path(caption_path)
    try:
        candidate_stat = candidate.stat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(candidate_stat.st_mode):
        return None
    if candidate.samefile(video_path):
        raise _CaptionSourceAliasError('Caption artifact aliases the source video')
    return candidate


def _unlink_temporary_caption(video_path, caption_path):
    try:
        caption_path.stat()
    except FileNotFoundError:
        return
    if caption_path.samefile(video_path):
        raise _CaptionSourceAliasError('Caption artifact aliases the source video')
    caption_path.unlink()


class YoutubePublishService:
    CAPTION_NAME = 'via_recorder_vtt'

    def __init__(self, youtube, config):
        self.youtube = youtube
        self.config = config

    def publish_video(
        self,
        video_path,
        source_type,
        source_name,
        start,
        stream_title=None,
        caption=None,
        checkpoint=None,
        before_video_upload=None,
    ):
        del source_type
        checkpoint = checkpoint or PublishCheckpoint()
        video_id = checkpoint.video_id
        video_uploaded = checkpoint.video_uploaded or video_id is not None
        caption_uploaded = checkpoint.caption_uploaded
        playlist_inserted = checkpoint.playlist_inserted
        youtube_processed = checkpoint.youtube_processed
        fingerprint = checkpoint.description_fingerprint
        caption_status = 'not_requested'

        def result(
            status,
            *,
            error_stage=None,
            error_message=None,
            remote_outcome_unknown=False,
        ):
            return PublishResult(
                status=status,
                video_id=video_id,
                video_uploaded=video_uploaded,
                caption_uploaded=caption_uploaded,
                playlist_inserted=playlist_inserted,
                youtube_processed=youtube_processed,
                description_fingerprint=fingerprint,
                caption_status=caption_status,
                error_stage=error_stage,
                error_message=error_message,
                remote_outcome_unknown=remote_outcome_unknown,
            )

        def error_result(exception, stage):
            status = _classify_error(exception)
            return result(
                status,
                error_stage=stage,
                error_message=str(exception),
                remote_outcome_unknown=(
                    stage == 'video' and _upload_outcome_unknown(exception, status)
                ),
            )

        try:
            path = Path(video_path)
            source_is_file = path.is_file()
        except (TypeError, ValueError, OSError):
            path = None
            source_is_file = False

        if not source_is_file:
            return result(
                PublishStatus.FATAL,
                error_stage='video',
                error_message=f'Video source is not a file: {video_path!r}',
            )

        try:
            sources = self.config['source']
            if not isinstance(sources, Mapping):
                raise TypeError("config['source'] must be a mapping")
            source = sources[source_name]
            if not isinstance(source, Mapping):
                raise TypeError(f'Source configuration for {source_name!r} must be a mapping')
            title_template = source['title']
            if not isinstance(title_template, str):
                raise TypeError('Source title must be a string')
            description = source.get('description', '')
            if not isinstance(description, str):
                raise TypeError('Source description must be a string')
            playlist_id = source.get('playlist_id')
            if playlist_id is not None and not isinstance(playlist_id, str):
                raise TypeError('Source playlist_id must be a string')
            title = title_template.format(datetime=start)
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as exception:
            return result(
                PublishStatus.FATAL,
                error_stage='config',
                error_message=str(exception),
            )

        if stream_title:
            title += f': {stream_title}'

        if caption is not None and caption.highlights:
            description += f'\n\n{caption.highlights}'
        desired_fingerprint = hashlib.sha256(description.encode('utf8')).hexdigest()

        caption_path = None
        caption_required = False
        if caption is not None:
            caption_status = caption.status
            if caption.status == 'ready' and caption.path is not None:
                try:
                    caption_path = _validated_caption_path(path, caption.path)
                except _CaptionSourceAliasError as exception:
                    caption_status = 'invalid'
                    return result(
                        PublishStatus.FATAL,
                        error_stage='caption',
                        error_message=f'Cannot validate caption path {caption.path}: {exception}',
                    )
                except Exception as exception:
                    status = _classify_error(exception)
                    if status is PublishStatus.FATAL:
                        caption_status = 'invalid'
                    return result(
                        status,
                        error_stage='caption',
                        error_message=f'Cannot validate caption path {caption.path}: {exception}',
                    )
                if caption_path is None:
                    caption_status = 'missing'
                else:
                    caption_required = True

        if video_id is None:
            if before_video_upload is not None:
                try:
                    before_video_upload(title, desired_fingerprint)
                except Exception as exception:
                    return result(
                        PublishStatus.RETRYABLE,
                        error_stage='checkpoint',
                        error_message=str(exception),
                    )
            try:
                video_id = self.youtube.upload(
                    str(path),
                    title,
                    description,
                    max_retryable_errors=0,
                    raise_errors=True,
                )
            except Exception as exception:
                return error_result(exception, 'video')

            if not video_id:
                return result(
                    PublishStatus.QUOTA_EXCEEDED,
                    error_stage='video',
                    error_message='YouTube API quota exceeded',
                )
            video_uploaded = True
            fingerprint = desired_fingerprint
        elif fingerprint != desired_fingerprint:
            try:
                updated = self.youtube.update(
                    video_id,
                    title,
                    description,
                    raise_errors=True,
                )
            except Exception as exception:
                return error_result(exception, 'description')
            if not updated:
                return result(
                    PublishStatus.RETRYABLE,
                    error_stage='description',
                    error_message='YouTube description update was not confirmed',
                )
            fingerprint = desired_fingerprint

        if caption_required:
            if caption_uploaded:
                caption_status = CAPTION_UPLOAD_SUCCESS
            else:
                try:
                    exists = self.youtube.caption_exists(video_id, self.CAPTION_NAME)
                except Exception as exception:
                    return error_result(exception, 'caption')

                if exists:
                    caption_uploaded = True
                    caption_status = 'existing'
                else:
                    try:
                        caption_result = self.youtube.add_caption_result(
                            video_id,
                            str(caption_path),
                            self.CAPTION_NAME,
                            raise_errors=True,
                        )
                    except Exception as exception:
                        return error_result(exception, 'caption')

                    caption_status = caption_result
                    if caption_result == CAPTION_UPLOAD_QUOTA_EXCEEDED:
                        return result(
                            PublishStatus.QUOTA_EXCEEDED,
                            error_stage='caption',
                            error_message='YouTube API quota exceeded',
                        )
                    if caption_result != CAPTION_UPLOAD_SUCCESS and caption_result is not True:
                        return result(
                            PublishStatus.RETRYABLE,
                            error_stage='caption',
                            error_message='YouTube caption upload was not confirmed',
                        )
                    caption_uploaded = True
                    caption_status = CAPTION_UPLOAD_SUCCESS

            if caption.temporary:
                try:
                    _unlink_temporary_caption(path, caption_path)
                except _CaptionSourceAliasError as exception:
                    caption_status = 'invalid'
                    return result(
                        PublishStatus.FATAL,
                        error_stage='caption',
                        error_message=str(exception),
                    )
                except OSError as exception:
                    return result(
                        PublishStatus.RETRYABLE,
                        error_stage='caption',
                        error_message=str(exception),
                    )

        playlist_required = bool(playlist_id)
        if playlist_required and not playlist_inserted:
            try:
                exists = self.youtube.playlist_contains(video_id, playlist_id)
            except Exception as exception:
                return error_result(exception, 'playlist')

            if exists:
                playlist_inserted = True
            else:
                try:
                    inserted = self.youtube.insert_into_playlist(
                        video_id,
                        playlist_id,
                        raise_errors=True,
                    )
                except Exception as exception:
                    return error_result(exception, 'playlist')
                if not inserted:
                    return result(
                        PublishStatus.RETRYABLE,
                        error_stage='playlist',
                        error_message='YouTube playlist insertion was not confirmed',
                    )
                playlist_inserted = True

        if not youtube_processed:
            try:
                processing = self.youtube.get_processing_status(video_id, raise_errors=True)
            except Exception as exception:
                return error_result(exception, 'processing')

            if not isinstance(processing, Mapping):
                return result(
                    PublishStatus.RETRYABLE,
                    error_stage='processing',
                    error_message='YouTube processing status was not available',
                )
            upload_status = processing.get('upload_status')
            if upload_status == 'processed':
                youtube_processed = True
            elif upload_status in ('deleted', 'failed', 'rejected'):
                primary_reason = (
                    'rejection_reason' if upload_status == 'rejected' else 'failure_reason'
                )
                fallback_reason = (
                    'failure_reason' if upload_status == 'rejected' else 'rejection_reason'
                )
                reason = processing.get(primary_reason) or processing.get(fallback_reason) or upload_status
                return result(
                    PublishStatus.FATAL,
                    error_stage='processing',
                    error_message=f'YouTube processing {upload_status}: {reason}',
                )

        stages_complete = (
            video_uploaded
            and (not caption_required or caption_uploaded)
            and (not playlist_required or playlist_inserted)
            and youtube_processed
        )
        return result(PublishStatus.COMPLETE if stages_complete else PublishStatus.PENDING)
