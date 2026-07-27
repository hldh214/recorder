from dataclasses import dataclass
from enum import Enum


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
class JournalFileState:
    fingerprint: str
    event: str
    manifest_id: str | None = None
    file: str | None = None
    xml_file: str | None = None
    title: str | None = None
    start_time: str | None = None
    duration: float | None = None
    video_id: str | None = None
    caption_status: str | None = None
    video_upload_rejected: bool = False
    caption_uploaded: bool = False
    playlist_inserted: bool = False
    youtube_processed: bool = False
    description_fingerprint: str | None = None
    upload_started_at: str | None = None
    retry_at: str | None = None
    attempt: int = 0
    stage: str | None = None
    status: str | None = None
    ambiguous: bool = False
    error_stage: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class JournalManifest:
    manifest_id: str
    room_id: int
    started_at: str
    settled_at: str
    flv_paths: tuple[str, ...]
    completed: bool = False


@dataclass(frozen=True)
class JournalSessionState:
    state: SessionState
    session_id: str | None
    session_paths: tuple[str, ...]
    snapshot: dict[str, tuple[int, int]]
    quiet_since: str | None
    started_at: str | None


@dataclass(frozen=True)
class JournalReplay:
    files: dict[str, JournalFileState]
    manifests: tuple[JournalManifest, ...]
    session: JournalSessionState
    initialized: bool
