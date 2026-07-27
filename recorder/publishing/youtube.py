import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from recorder.destination.youtube import (
    CAPTION_UPLOAD_QUOTA_EXCEEDED,
    CAPTION_UPLOAD_SUCCESS,
)


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


def _is_retryable_error(exception):
    status = _http_status(exception)
    if status is not None:
        return status >= 500 or status in (408, 429)
    return isinstance(exception, OSError)


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
        video_uploaded = checkpoint.video_uploaded
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
                candidate = Path(caption.path)
                if candidate.is_file():
                    caption_path = candidate
                    caption_required = True
                else:
                    caption_status = 'missing'

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
                if _is_retryable_error(exception):
                    return result(
                        PublishStatus.RETRYABLE,
                        error_stage='video',
                        error_message=str(exception),
                        remote_outcome_unknown=True,
                    )
                return result(
                    PublishStatus.FATAL,
                    error_stage='video',
                    error_message=str(exception),
                )

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
                status = PublishStatus.RETRYABLE if _is_retryable_error(exception) else PublishStatus.FATAL
                return result(status, error_stage='description', error_message=str(exception))
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
                    status = (
                        PublishStatus.RETRYABLE
                        if _is_retryable_error(exception)
                        else PublishStatus.FATAL
                    )
                    return result(status, error_stage='caption', error_message=str(exception))

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
                        status = (
                            PublishStatus.RETRYABLE
                            if _is_retryable_error(exception)
                            else PublishStatus.FATAL
                        )
                        return result(status, error_stage='caption', error_message=str(exception))

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

            if caption.temporary and caption_path.exists():
                try:
                    caption_path.unlink()
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
                status = PublishStatus.RETRYABLE if _is_retryable_error(exception) else PublishStatus.FATAL
                return result(status, error_stage='playlist', error_message=str(exception))

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
                    status = (
                        PublishStatus.RETRYABLE
                        if _is_retryable_error(exception)
                        else PublishStatus.FATAL
                    )
                    return result(status, error_stage='playlist', error_message=str(exception))
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
                status = PublishStatus.RETRYABLE if _is_retryable_error(exception) else PublishStatus.FATAL
                return result(status, error_stage='processing', error_message=str(exception))

            if not isinstance(processing, Mapping):
                return result(
                    PublishStatus.RETRYABLE,
                    error_stage='processing',
                    error_message='YouTube processing status was not available',
                )
            upload_status = processing.get('upload_status')
            if upload_status == 'processed':
                youtube_processed = True
            elif upload_status in ('failed', 'rejected'):
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
