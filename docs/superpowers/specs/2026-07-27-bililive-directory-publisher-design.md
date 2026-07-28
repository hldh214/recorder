# Bililive Directory Publisher Mode

Date: 2026-07-27
Status: Draft for written review

## Context

The current Bilibili workflow receives BililiveRecorder webhooks, moves each
closed FLV into the upload tree, renames it with an MP4 suffix, generates
captions from MongoDB, uploads it to YouTube, moves it into a validation tree,
and eventually deletes it.

The new deployment will run recording, danmaku capture, and YouTube publishing
on `instance-1`. It must use BililiveRecorder's XML danmaku files, remove the
MongoDB dependency for this mode, wait until the whole live session has ended,
avoid uploading small non-tail fragments, and publish directly from the
original FLV path without copying, moving, renaming, or deleting it.

The legacy workflow remains supported.

## Goals

- Add a directory-monitoring publisher mode for BililiveRecorder output.
- Wait for the entire live session to end before publishing any of its files.
- Treat BililiveRecorder API state and directory quietness as mandatory
  settlement signals.
- Publish each accepted FLV independently. Do not merge recordings.
- Skip small non-tail fragments without creating many short YouTube videos.
- Parse BililiveRecorder XML into YouTube-compatible VTT captions and reuse
  the existing highlight-generation behavior.
- Extract complete YouTube publication into a reusable function that never
  manages source-file lifecycle.
- Preserve partial publication progress across process restarts without
  MongoDB or a database server.
- Replace the uncoordinated disk-cleanup cron job with state-aware cleanup.
- Retain the legacy directory scanner and its existing move/validate/delete
  lifecycle through a legacy adapter.

## Non-Goals

- Merging, concatenating, remuxing, or transcoding FLV fragments.
- Filling or concealing recording gaps.
- Replacing BililiveRecorder itself.
- Uploading gift, guard, SuperChat, or raw danmaku records as captions.
- Parallel media probing or parallel video uploading.
- Backfilling files that already exist when the new mode is first enabled.
- A web UI or multi-worker task queue.

## Fixed Policy Values

These values are module-level constants, not application configuration:

```python
POLL_INTERVAL_SECONDS = 60
QUIET_PERIOD_SECONDS = 30 * 60
MIN_NON_TAIL_SIZE_BYTES = 256 * 1024 * 1024
MIN_TAIL_DURATION_SECONDS = 60
FFPROBE_TIMEOUT_SECONDS = 120
DISK_CLEANUP_THRESHOLD_PERCENT = 85
RETRY_BASE_SECONDS = 5 * 60
RETRY_MAX_SECONDS = 6 * 60 * 60
SESSION_TIMEZONE = "Asia/Shanghai"
```

The recorder's configured cut duration is deliberately absent. Changing from
three-hour to four-hour cuts does not alter discovery, classification, or
publication behavior.

## Architecture

```text
BililiveRecorder working directory
              |
              v
BililiveDirectoryMonitor
  - observes room and directory state
  - settles complete sessions
  - validates and classifies files
  - owns retries and the JSONL journal
              |
              v
BililiveXmlCaptionProvider
  - streams same-stem XML
  - creates temporary VTT
  - creates highlight text
              |
              v
YoutubePublishService
  - uploads the original video path
  - uploads optional VTT
  - ensures playlist membership
  - returns resumable stage results
  - never mutates source FLV or XML
```

The legacy path becomes an adapter around the same publication service:

```text
LegacyUploadWorker -> YoutubePublishService -> legacy move/validate/delete
```

### Module Boundaries

- `recorder/destination/youtube.py` remains the low-level YouTube API client.
- `recorder/publishing/youtube.py` contains the publication request/result
  types and the reusable publication service.
- `recorder/danmaku/bilibili/bililive_xml.py` contains streaming XML parsing
  and adaptation to the existing caption/highlight code.
- `recorder/utils/bililive_directory_monitor.py` contains the new CLI,
  session monitor, journal replay, retry scheduler, and state-aware cleanup.
- `recorder/app.py` retains the legacy worker but delegates complete YouTube
  publication to the new service.

## Publication Service Contract

The public service accepts an existing source path and explicit publication
context. A representative interface is:

```python
result = publish_video(
    video_path=video_path,
    source_type="bilibili",
    source_name="1829181560",
    caption_provider=caption_provider,
    checkpoint=previous_result,
)
```

The service:

1. Reads source configuration for title, description, and playlist settings.
2. Reads video metadata and duration without altering the file.
3. Requests caption/highlight artifacts from the supplied provider.
4. Uploads the video unless the checkpoint already contains a `video_id`.
5. Uploads the VTT if available.
6. Ensures playlist membership.
7. Returns the outcome of every stage.

A partial result retains enough information to resume safely:

```python
PublishResult(
    video_id="abc123",
    video_uploaded=True,
    youtube_processed=False,
    caption_uploaded=False,
    playlist_inserted=True,
    retryable=True,
    error_stage="caption",
)
```

When `video_id` is present, the service never uploads the video again. Caption
and playlist retries first query remote state so that already-completed work is
not duplicated. The service does not contain long sleeps; callers schedule
retries.

The service must not call `copy`, `move`, `rename`, or `unlink` for the source
video or its XML file. It passes the original FLV path directly to the YouTube
media uploader. Temporary VTT cleanup is allowed because it is a generated
artifact, not a source file.

## Monitor CLI

The intended Supervisor command is equivalent to:

```shell
python -m recorder.utils.bililive_directory_monitor \
  /data/BililiveRecorder \
  --room-id 1829181560 \
  --api-url http://100.87.152.23:2356
```

The source directory, room ID, API URL, and optional state-directory override
are runtime arguments. Stable behavioral policy remains in module constants.

Only one monitor instance may own a room. A process lock in the state directory
enforces this before any journal or publication work begins.

## First-Run Baseline

The first run never uploads files that already exist.

- If the room is offline, every existing file is journaled as `BASELINED`, and
  the monitor arms itself for the next live session.
- If the room is live, the monitor enters `SKIP_CURRENT_SESSION`. Existing
  files and every file created before that session settles are baseline-only.
- After the skipped session is offline and quiet for 30 minutes, the monitor
  arms itself for the next session.

This prevents a deployment made during a live stream from uploading only the
second half of that stream.

## Session State Machine

```text
WAITING
  -> BililiveRecorder reports streaming or recording
RECORDING
  -> BililiveRecorder reports neither streaming nor recording
SETTLING
  -> no new file and no FLV/XML size or mtime change for 30 minutes
READY
  -> freeze the session manifest and publish files sequentially
COMPLETE
  -> return to WAITING
```

The BililiveRecorder API is mandatory. If it is unavailable, malformed, or
times out, the monitor waits and publishes nothing. Directory quietness alone
cannot settle a session because a configured segment may remain open for three,
four, or more hours.

Before each upload starts, the monitor rechecks the manifest entry's size and
mtime. Any change invalidates the frozen manifest and returns the session to
`SETTLING`.

## File Discovery and Classification

After settlement, media checks run sequentially and at low CPU/I/O priority.
No command scans or decodes a batch of large files concurrently.

For each FLV, the monitor records:

- absolute path, byte size, and nanosecond mtime;
- BililiveRecorder `StartTime` metadata when available;
- filename timestamp as a fallback ordering signal;
- ffprobe duration and stream metadata;
- presence of at least one valid video stream and one valid audio stream;
- same-stem XML path and its stability state.

Unprobeable files and files without both audio and video are
`IGNORED_INVALID`. A probe timeout is retryable rather than immediately
invalid, because storage pressure or load can delay probing.

The chronologically last playable FLV is the tail. Classification is then:

- Non-tail and smaller than 256 MiB: `IGNORED_TINY`.
- Tail shorter than 60 seconds: `IGNORED_INVALID_TAIL`.
- Otherwise: `READY`.

The tail exception prevents a normal short stream ending from being discarded.
Trailing corrupt files do not steal tail status from the last playable file.
Every ignored decision includes the measured values and reason in both the
structured journal and human-readable log.

Each accepted file is published independently. There is no gap detection,
concatenation, remuxing, or transcoding in this mode.

## BililiveRecorder XML Captions

BililiveRecorder must have `RecordDanmaku` enabled. The provider pairs an FLV
with a same-directory, same-stem XML file and parses it with
`xml.etree.ElementTree.iterparse` to keep memory bounded.

Only ordinary `<d>` entries are converted. The first comma-separated value in
the `p` attribute is the message's relative media time in seconds. The parser:

- preserves Unicode message text;
- ignores gift, guard, SuperChat, and raw JSON entries;
- ignores empty messages;
- rejects negative timestamps;
- excludes messages beyond the measured media duration and logs their count;
- adapts relative timestamps to the existing `Caption` and highlight APIs.

The provider writes a temporary VTT in the monitor state directory. Successful
caption upload removes the temporary VTT. A restart can regenerate it from XML.

Missing or malformed XML does not block video publication. It produces
`CAPTION_MISSING` or `CAPTION_INVALID`, retains diagnostic information, and
allows later caption backfill against the saved `video_id`. If valid XML later
appears, the service uploads the VTT and updates the video description with the
generated highlights.

## JSONL State Journal

Persistent state is required because source files no longer move between
directories to represent lifecycle. The implementation uses an append-only,
machine-readable JSONL journal rather than SQLite.

Representative events are:

```json
{"event":"baseline","file":"/data/BililiveRecorder/1829181560/a.flv"}
{"event":"session_started","room_id":1829181560}
{"event":"file_ready","fingerprint":"...","file":"..."}
{"event":"upload_started","fingerprint":"..."}
{"event":"video_uploaded","fingerprint":"...","video_id":"abc123"}
{"event":"caption_uploaded","fingerprint":"...","video_id":"abc123"}
{"event":"playlist_inserted","fingerprint":"...","video_id":"abc123"}
{"event":"youtube_processed","fingerprint":"...","video_id":"abc123"}
{"event":"source_deleted","fingerprint":"...","file":"..."}
```

Each event is written as one line, flushed, and `fsync`ed before the next
external stage begins. At startup, the monitor replays the journal to derive
the latest per-file and per-session state.

The last line may be ignored if a crash left it syntactically incomplete. Any
corrupt line before the final line is a fail-closed condition: the monitor logs
the offset and performs no automatic upload until the journal is repaired.
The journal is not a conventional log and must never be rotated.

The file fingerprint contains:

```text
absolute path + size + mtime_ns + metadata StartTime + media duration
```

It deliberately avoids hashing multi-gigabyte recordings.

### Ambiguous Uploads

No local storage format can atomically commit with YouTube. A process may stop
after YouTube accepts a video but before the returned `video_id` is persisted.

The monitor writes `upload_started` before calling YouTube. If replay finds
`upload_started` without `video_uploaded`, the file becomes `AMBIGUOUS` and is
not automatically uploaded again. Reconciliation checks recent channel uploads
using title, start time, duration, and upload time. If a unique match cannot be
established, the monitor requires manual resolution and continues processing
other non-ambiguous files.

## Retry and Error Handling

Publication outcomes are classified as:

- `RETRYABLE`: transient network or service failure;
- `QUOTA_EXCEEDED`: retry after the quota window/backoff;
- `FATAL`: invalid credentials, rejected media, or permanent configuration
  failure;
- `AMBIGUOUS`: remote acceptance cannot be determined safely.

Retries use exponential backoff from five minutes to six hours and are
scheduled by the monitor. One caption quota failure does not block publication
of another ready video. Video files themselves are still uploaded sequentially.

Video, caption, playlist, and YouTube-processing status are independent. A
video that already has a `video_id` never returns to the video-upload stage.

## Resource Safety

- At most one ffprobe or ffmpeg-family process may run at once.
- Media probes run with low CPU and best-effort I/O priority on Linux.
- Every probe has a timeout and retry classification.
- The monitor never full-decodes a large source file.
- At most one video upload runs at once.
- API or SSH/filesystem failure is treated as unavailable input, never as a
  completed session.
- No merge trial or boundary test exists in this version.

## State-Aware Disk Cleanup

The existing hourly cleanup script must be disabled after the new cleanup has
been verified. The new cleanup runs under the monitor's single-instance lock,
only after the room API reliably reports both recording and streaming as false
and the completed session has passed the normal directory-settling checks. It
never runs while a live session is active or while room state is unavailable.

Cleanup starts at 85 percent disk use, considers only files whose own mtime is
at least six hours old, deletes oldest-first, and stops as soon as usage drops
below 85 percent. The age gate is intentionally shorter than a multi-day
retention policy because a 100 GB recorder disk may hold only about two full
evening sessions.

FLV deletion eligibility is independent from XML deletion eligibility:

- A normal FLV is deletable only after its YouTube video is confirmed processed.
- A deliberately ignored small or invalid FLV is deletable because it has a
  terminal local decision and will never be uploaded.
- A baseline-only FLV is never automatically deleted. It predates ownership by
  this service and requires an explicit later decision.
- An XML paired with a published FLV is deletable only after its caption has
  been confirmed uploaded. A missing XML requires no cleanup action.
- An XML paired with a deliberately ignored FLV is deletable with the ignored
  source once that XML independently passes the six-hour age gate.
- Missing or malformed XML does not retain the large FLV after YouTube
  processing. The small XML and journal metadata remain available for later
  repair and backfill.
- Playlist failure does not retain the FLV because playlist retry needs only
  the `video_id`.
- `READY`, `UPLOADING_VIDEO`, unprocessed uploaded videos, `AMBIGUOUS`, and
  unknown files are never deleted.

Immediately before deletion, the service revalidates that the path is a regular
file inside the configured recorder root, still has the size and mtime recorded
in the journal, and still has the device and inode observed when it became a
deletion candidate. Any mismatch protects the path. With cleanup restricted to
a settled offline directory, deletion uses a direct unlink rather than a
recoverable quarantine transaction. A crash after unlink but before the
completion event is safe: replay sees an absent source that was already in a
terminal publication/ignore state and performs no upload or second deletion.

Every successful deletion is journaled with the path and reason. If disk use is
above the threshold but no eligible file exists, cleanup deletes nothing and
emits a high-severity operational error.

## Legacy Compatibility

The legacy worker continues to discover MP4 paths under its upload tree and
continues to own its move-to-validate and delete-after-validation behavior.
Only publication orchestration is extracted into `YoutubePublishService`.

Legacy Mongo caption generation remains available to the legacy adapter. The
new directory monitor uses only the BililiveRecorder XML provider. Disabling
MongoDB on `instance-1` does not remove legacy code or alter other deployments.

## Testing

Unit tests cover:

- offline and live first-run baselines;
- all session-state transitions and API-unavailable behavior;
- quiet-period reset on new or changed FLV/XML files;
- 256 MiB non-tail filtering and the 60-second tail rule;
- three-hour, four-hour, mixed-length, and single-file sessions;
- sequential probe scheduling and timeout behavior;
- XML parsing, Unicode, timestamp clipping, missing XML, and malformed XML;
- JSONL replay, final-line truncation, mid-file corruption, and process locking;
- partial publication resume without a second video upload;
- caption and playlist remote-state checks;
- `AMBIGUOUS` crash recovery;
- cleanup eligibility for FLV and XML independently;
- source FLV/XML path, size, mtime, and inode remaining unchanged during direct
  publication;
- unchanged legacy move/validate/delete behavior.

Integration tests use only a tiny generated or checked-in FLV/XML fixture,
mock YouTube APIs, and no large production recording. They validate metadata
reading, VTT timing, publication stage order, retry resume, and the prohibition
on source-file mutations.

## Deployment

1. Install the updated project and dependencies on `instance-1`.
2. Verify BililiveRecorder `RecordDanmaku` is enabled and a new session emits
   same-stem XML files.
3. Configure the existing YouTube/source settings for room `1829181560`.
4. Run the monitor in dry-run mode to validate API access, paths, baseline,
   media probing, XML parsing, and cleanup decisions.
5. Start the new monitor under Supervisor and confirm that its JSONL baseline
   is durable across one controlled restart.
6. Keep legacy recorder and Mongo danmaku tasks disabled on `instance-1`.
7. Enable state-aware cleanup, inspect its dry-run output, and only then disable
   the old hourly cleanup cron entry.
8. After the first new live session, manually verify video title, description,
   VTT, playlist membership, YouTube processing state, journal replay, and disk
   cleanup eligibility.

Rollback stops the new Supervisor task and re-enables the previous cleanup or
legacy tasks. Because direct publication does not move source files, rollback
does not require restoring a source-directory layout.

## Acceptance Criteria

- Existing files are not uploaded on first enablement.
- A session is never processed while BililiveRecorder reports it active.
- A session is never processed before 30 minutes of directory stability.
- Cut-length changes do not require code or configuration changes.
- Small non-tail fragments do not appear as individual YouTube uploads.
- Accepted FLVs are uploaded from their original paths without source mutation.
- BililiveRecorder XML produces VTT and highlight text without MongoDB.
- Video publication continues when XML is missing or invalid.
- Restart after `video_uploaded` cannot upload the same video again.
- Ambiguous remote outcomes fail closed instead of blindly retrying.
- Cleanup cannot delete an active, unprocessed, ambiguous, or unknown file.
- Legacy publication behavior remains covered by regression tests.
