from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import MappingProxyType


class SessionState(str, Enum):
    BASELINING = 'baselining'
    SKIP_CURRENT_SESSION = 'skip_current_session'
    WAITING = 'waiting'
    RECORDING = 'recording'
    SETTLING = 'settling'
    READY = 'ready'
    PUBLISHING = 'publishing'


@dataclass(frozen=True)
class RoomState:
    recording: bool
    streaming: bool

    @property
    def active(self):
        return self.recording or self.streaming


@dataclass(frozen=True)
class MediaInfo:
    path: Path
    xml_path: Path
    size: int
    mtime_ns: int
    start_time: datetime
    stream_title: str | None
    duration: float | None
    has_video: bool
    has_audio: bool
    fingerprint: str
    probe_error: str | None = None


@dataclass(frozen=True)
class ClassifiedMedia:
    media: MediaInfo
    status: str
    reason: str
    is_tail: bool = False


@dataclass(frozen=True)
class JournalFileState:
    fingerprint: str
    event: str
    manifest_id: str | None = None
    file: str | None = None
    xml_file: str | None = None
    title: str | None = None
    stream_title: str | None = None
    start_time: str | None = None
    duration: float | None = None
    video_id: str | None = None
    caption_status: str | None = None
    reason: str | None = None
    video_upload_rejected: bool = False
    caption_uploaded: bool = False
    playlist_inserted: bool = False
    youtube_processed: bool = False
    description_updated: bool = False
    description_fingerprint: str | None = None
    upload_started_at: str | None = None
    retry_at: str | None = None
    attempt: int = 0
    stage: str | None = None
    status: str | None = None
    ambiguous: bool = False
    error_stage: str | None = None
    error_message: str | None = None
    deleted_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class JournalManifest:
    manifest_id: str
    room_id: int
    started_at: str
    settled_at: str
    flv_paths: tuple[str, ...]
    snapshot: Mapping[str, tuple[int, int]]
    completed: bool = False
    invalidated: bool = False
    invalidated_at: str | None = None
    invalidation_reason: str | None = None
    changed_paths: tuple[str, ...] = ()
    replacement_manifest_id: str | None = None

    def __post_init__(self):
        object.__setattr__(self, 'flv_paths', tuple(self.flv_paths))
        object.__setattr__(self, 'changed_paths', tuple(self.changed_paths))
        object.__setattr__(
            self,
            'snapshot',
            MappingProxyType({
                path: tuple(identity)
                for path, identity in self.snapshot.items()
            }),
        )


@dataclass(frozen=True)
class JournalSessionState:
    state: SessionState
    room_id: int | None
    session_id: str | None
    session_paths: tuple[str, ...]
    snapshot: Mapping[str, tuple[int, int]]
    quiet_since: str | None
    started_at: str | None

    def __post_init__(self):
        object.__setattr__(self, 'session_paths', tuple(self.session_paths))
        object.__setattr__(
            self, 'snapshot', MappingProxyType(dict(self.snapshot))
        )


@dataclass(frozen=True)
class JournalResettleRequest:
    source_manifest_id: str
    settled_at: str
    detected_at: str
    reason: str
    changed_paths: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, 'changed_paths', tuple(self.changed_paths))


@dataclass(frozen=True)
class JournalReplay:
    files: Mapping[str, JournalFileState]
    manifests: tuple[JournalManifest, ...]
    session: JournalSessionState
    initialized: bool
    pending_resettles: tuple[JournalResettleRequest, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'files', MappingProxyType(dict(self.files)))
        object.__setattr__(self, 'manifests', tuple(self.manifests))
        object.__setattr__(
            self, 'pending_resettles', tuple(self.pending_resettles)
        )
