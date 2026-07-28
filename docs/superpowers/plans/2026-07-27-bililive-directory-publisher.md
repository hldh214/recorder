# Bililive Directory Publisher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `instance-1`-ready BililiveRecorder directory mode that waits for a complete session, filters short fragments, publishes original FLV files with XML-derived VTT captions, persists progress in JSONL, and cleans disk safely without changing legacy behavior.

**Architecture:** Extract a reusable `YoutubePublishService` above the existing low-level YouTube client. Add focused Bililive modules for XML captions, JSONL state, media inspection, session monitoring, publication orchestration, and cleanup; expose them through a thin util CLI. The 60-second observation loop stays responsive while exactly one publication worker sequentially probes and uploads journaled ready manifests. The direct mode never mutates source FLV/XML during publication, while the legacy adapter retains its move/validate/delete lifecycle.

**Tech Stack:** Python 3.10, pytest 7, stdlib dataclasses/enum/json/fcntl/XML, httpx, arrow, ffprobe, google-api-python-client, Fire CLI.

---

## File Map

Create these focused modules:

- `recorder/publishing/__init__.py`: public publication types and service exports.
- `recorder/publishing/youtube.py`: complete YouTube publication orchestration with resumable stage results.
- `recorder/danmaku/bilibili/bililive_xml.py`: streaming BililiveRecorder XML to VTT/highlight provider.
- `recorder/bililive/__init__.py`: Bililive package exports.
- `recorder/bililive/models.py`: immutable room, media, session, and publication state types.
- `recorder/bililive/journal.py`: append-only JSONL journal and single-process lock.
- `recorder/bililive/media.py`: low-priority ffprobe inspection, fingerprinting, and tail classification.
- `recorder/bililive/monitor.py`: first-run baseline and session settlement state machine.
- `recorder/bililive/runner.py`: publication/retry/ambiguity coordinator.
- `recorder/bililive/service.py`: responsive observation loop plus sole sequential publication worker.
- `recorder/bililive/cleanup.py`: state-aware 85-percent cleanup.
- `recorder/utils/bililive_directory_monitor.py`: Fire CLI and dependency wiring only.

Modify these existing files:

- `recorder/destination/youtube.py`: add remote-state query primitives used for idempotent retries.
- `recorder/app.py`: make the legacy upload worker call `YoutubePublishService` while keeping file lifecycle unchanged.
- `recorder/utils/README.md`: document the new mode and dry-run command.

Create tests by responsibility:

- `tests/test_youtube_publishing.py`
- `tests/test_bililive_xml.py`
- `tests/test_bililive_journal.py`
- `tests/test_bililive_media.py`
- `tests/test_bililive_monitor.py`
- `tests/test_bililive_runner.py`
- `tests/test_bililive_service.py`
- `tests/test_bililive_cleanup.py`
- `tests/test_bililive_directory_monitor.py`
- `tests/test_bililive_pipeline_integration.py`

Do not modify `config.sample.toml`: policy thresholds are module constants and runtime paths are CLI arguments.

### Task 1: Add Idempotent YouTube Query Primitives

**Files:**
- Modify: `recorder/destination/youtube.py:273-471`
- Modify: `tests/test_youtube.py`

- [ ] **Step 1: Write failing tests for caption, playlist, recent-upload, and bounded-upload behavior**

Append fakes and tests to `tests/test_youtube.py` that assert these public methods:

```python
def test_youtube_caption_exists_uses_language_and_name():
    youtube = Youtube.__new__(Youtube)
    youtube.list_captions = lambda video_id: [{
        'snippet': {'language': 'zh-Hans', 'name': 'via_recorder_vtt'}
    }]

    assert youtube.caption_exists('yt123', 'via_recorder_vtt') is True


def test_youtube_playlist_contains_filters_by_video_id():
    youtube = Youtube.__new__(Youtube)
    request = FakeExecutable({'items': [{'contentDetails': {'videoId': 'yt123'}}]})
    youtube.youtube = FakePlaylistYoutube(request)

    assert youtube.playlist_contains('yt123', 'playlist123') is True
    assert request.kwargs == {
        'part': 'contentDetails',
        'playlistId': 'playlist123',
        'videoId': 'yt123',
        'maxResults': 1,
    }


def test_youtube_list_recent_uploads_reads_authenticated_uploads_playlist():
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FakeRecentUploadsYoutube(
        channel_response={'items': [{
            'contentDetails': {'relatedPlaylists': {'uploads': 'uploads123'}}
        }]},
        playlist_response={'items': [{
            'snippet': {
                'title': 'recording title',
                'publishedAt': '2026-07-27T03:00:00Z',
                'resourceId': {'videoId': 'yt123'},
            },
            'contentDetails': {'videoId': 'yt123'},
        }]},
        videos_response={'items': [{
            'id': 'yt123',
            'contentDetails': {'duration': 'PT3H2M1.5S'},
        }]},
    )

    assert youtube.list_recent_uploads(50) == [{
        'video_id': 'yt123',
        'title': 'recording title',
        'published_at': '2026-07-27T03:00:00Z',
        'duration_seconds': 10921.5,
    }]


def test_youtube_get_processing_status_preserves_rejection_details():
    youtube = Youtube.__new__(Youtube)
    youtube.youtube = FakeVideosYoutube({'items': [{'status': {
        'uploadStatus': 'rejected',
        'rejectionReason': 'duplicate',
    }}]})

    assert youtube.get_processing_status('yt123') == {
        'upload_status': 'rejected',
        'failure_reason': None,
        'rejection_reason': 'duplicate',
    }


def test_youtube_upload_can_return_control_on_first_retryable_error():
    youtube = youtube_with_retryable_resumable_error()

    with pytest.raises(HttpError):
        youtube.upload(
            '/recording.flv',
            'title',
            'description',
            max_retryable_errors=0,
            raise_errors=True,
        )
```

Implement `FakeExecutable`, `FakePlaylistYoutube`, and `FakeRecentUploadsYoutube` in the test file with the exact chained methods used by the production client. Each fake records keyword arguments so tests verify API filters, not only return values. Add strict-error tests proving a non-quota 403 is re-raised while a `quotaExceeded` 403 still returns `False`, and that `update`, `check_processed`, `insert_into_playlist`, and `add_caption_result` re-raise API errors only when `raise_errors=True`.

- [ ] **Step 2: Run the focused tests and verify the missing-method failures**

Run:

```shell
pipenv run pytest tests/test_youtube.py -q
```

Expected: the query/status tests fail with missing-method/assertion failures and the upload test fails because `upload` does not accept `max_retryable_errors`; existing tests pass.

- [ ] **Step 3: Add the low-level query and strict-error controls**

Add these methods to `Youtube` after `list_captions`:

```python
def caption_exists(self, video_id, caption_name='via_recorder_vtt'):
    return _caption_exists(
        self.list_captions(video_id),
        self.DEFAULT_CAPTION_LANGUAGE,
        caption_name,
    )

def playlist_contains(self, video_id, playlist_id):
    response = self.youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        videoId=video_id,
        maxResults=1,
    ).execute()
    return bool(response.get('items'))

def list_recent_uploads(self, max_results=50):
    channels = self.youtube.channels().list(
        part='contentDetails',
        mine=True,
    ).execute()
    items = channels.get('items') or []
    if not items:
        return []

    uploads_id = items[0]['contentDetails']['relatedPlaylists']['uploads']
    response = self.youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=uploads_id,
        maxResults=max_results,
    ).execute()
    recent = [
        {
            'video_id': item['contentDetails']['videoId'],
            'title': item['snippet']['title'],
            'published_at': item['snippet']['publishedAt'],
        }
        for item in response.get('items', [])
    ]
    details = self.youtube.videos().list(
        part='contentDetails',
        id=','.join(item['video_id'] for item in recent),
        maxResults=50,
    ).execute() if recent else {'items': []}
    durations = {
        item['id']: _youtube_duration_seconds(item['contentDetails']['duration'])
        for item in details.get('items', [])
    }
    return [
        {**item, 'duration_seconds': durations.get(item['video_id'])}
        for item in recent
    ]
```

Add `get_processing_status(video_id, raise_errors=False)` using `videos.list(part='status', id=video_id)`. Return normalized `upload_status`, `failure_reason`, and `rejection_reason` keys; return a `missing` status for an empty `items` list. Add a private `_youtube_duration_seconds` parser for the ISO-8601 `PT#H#M#S` values returned by YouTube. Reject unsupported values instead of guessing. The recent-upload fake must assert both the playlist query and the batched `videos.list(part='contentDetails', id=...)` query.

Extend the existing `Youtube.upload` signature with keyword-only `max_retryable_errors=None, raise_errors=False`. Preserve the current unbounded behavior for existing direct callers when the retry limit is `None`; when a finite limit is supplied, re-raise the last retryable exception as soon as the count exceeds the limit. When `raise_errors=True`, parse the `HttpError` reason and re-raise non-quota 403 responses while retaining `False` for `quotaExceeded`/`dailyLimitExceeded`. `YoutubePublishService` will pass zero plus strict error mode so its caller, journal, and retry scheduler regain control immediately.

Add keyword-only `raise_errors=False` to `update`, `check_processed`, `get_processing_status`, `insert_into_playlist`, and `add_caption_result`. Existing callers retain their current boolean/result behavior. In strict mode, keep the caption quota sentinel but re-raise every other caught API/authentication exception for classification by the publication service.

The `playlistItems.list` call intentionally uses both `playlistId` and `videoId`; the current official API supports this filter and charges one quota unit.

- [ ] **Step 4: Run YouTube tests**

Run:

```shell
pipenv run pytest tests/test_youtube.py -q
```

Expected: all tests in `tests/test_youtube.py` pass.

- [ ] **Step 5: Commit the low-level primitives**

```shell
git add recorder/destination/youtube.py tests/test_youtube.py
git commit -m "feat: add YouTube publication state queries"
```

### Task 2: Extract the Complete YouTube Publication Service

**Files:**
- Create: `recorder/publishing/__init__.py`
- Create: `recorder/publishing/youtube.py`
- Create: `tests/test_youtube_publishing.py`

- [ ] **Step 1: Write failing tests for direct publication and source immutability**

Create `tests/test_youtube_publishing.py` with a `FakeYoutube` that records `upload`, caption, playlist, update, and processed-status calls. Cover these exact cases:

```python
def test_publish_video_completes_all_stages_without_mutating_source(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'original-flv')
    caption = tmp_path / 'recording.vtt'
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    before = (video.stat().st_ino, video.stat().st_size, video.stat().st_mtime_ns)
    youtube = FakeYoutube(upload_id='yt123', processed=True)
    service = YoutubePublishService(youtube, source_config())

    result = service.publish_video(
        video_path=video,
        source_type='bilibili',
        source_name='1829181560',
        start='2026-07-27 18:00:00',
        stream_title='stream title',
        caption=CaptionArtifact(caption, 'Highlights\n00:00 Start'),
    )

    after = (video.stat().st_ino, video.stat().st_size, video.stat().st_mtime_ns)
    assert result.video_id == 'yt123'
    assert result.video_uploaded is True
    assert result.caption_uploaded is True
    assert result.playlist_inserted is True
    assert result.youtube_processed is True
    assert before == after
    assert video.read_bytes() == b'original-flv'


def test_publish_video_resumes_from_video_id_without_reupload(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'original-flv')
    youtube = FakeYoutube(upload_id='unexpected', processed=False)
    service = YoutubePublishService(youtube, source_config())

    result = service.publish_video(
        video_path=video,
        source_type='bilibili',
        source_name='1829181560',
        start='2026-07-27 18:00:00',
        checkpoint=PublishCheckpoint(video_id='yt123', video_uploaded=True),
    )

    assert youtube.upload_calls == []
    assert result.video_id == 'yt123'


def test_publish_video_returns_caption_quota_without_losing_video_id(tmp_path):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'original-flv')
    caption = tmp_path / 'recording.vtt'
    caption.write_text('WEBVTT\n\n', encoding='utf8')
    youtube = FakeYoutube(
        upload_id='yt123',
        caption_result=CAPTION_UPLOAD_QUOTA_EXCEEDED,
        processed=False,
    )
    service = YoutubePublishService(youtube, source_config())

    result = service.publish_video(
        video_path=video,
        source_type='bilibili',
        source_name='1829181560',
        start='2026-07-27 18:00:00',
        caption=CaptionArtifact(caption, ''),
    )

    assert result.video_id == 'yt123'
    assert result.status is PublishStatus.QUOTA_EXCEEDED
    assert result.error_stage == 'caption'
```

Also test remote-existing caption and playlist states skip inserts, missing source configuration returns `FATAL` without invoking the upload checkpoint callback, an invalid caption artifact yields `caption_status='invalid'` while video upload proceeds, an existing `video_id` with newly available highlights updates the description without re-uploading the video, and YouTube `rejected`/`failed` processing states return `FATAL` with the remote reason. Record callback and fake-YouTube events to assert the callback completes immediately before `upload`. A simulated timeout after that callback must return `remote_outcome_unknown=True`; a callback failure and a quota 403 must leave it false.

- [ ] **Step 2: Run the new test module and verify import failure**

Run:

```shell
pipenv run pytest tests/test_youtube_publishing.py -q
```

Expected: collection fails because `recorder.publishing.youtube` does not exist.

- [ ] **Step 3: Define immutable request/result types and service exports**

Create `recorder/publishing/youtube.py` with these public types:

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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
```

Export these names from `recorder/publishing/__init__.py`.

- [ ] **Step 4: Implement `YoutubePublishService.publish_video`**

Define `YoutubePublishService.CAPTION_NAME = 'via_recorder_vtt'`. Its constructor accepts `(youtube, config)`, stores both dependencies, and exposes this concrete method signature: `publish_video(self, video_path, source_type, source_name, start, stream_title=None, caption=None, checkpoint=None, before_video_upload=None)`.

Implement the method in this fixed order:

1. Convert `video_path` to `Path` and return `FATAL/error_stage='video'` if it is not a file.
2. Read `self.config['source'][source_name]`; return `FATAL/error_stage='config'` if absent.
3. Build title from `source['title'].format(datetime=start)` and append `: {stream_title}` when present.
4. Build description from `source.get('description', '')` and append caption highlights separated by two newlines. Compute a SHA-256 fingerprint of the exact UTF-8 description.
5. Start from `checkpoint or PublishCheckpoint()`.
6. If no checkpoint `video_id`, invoke `before_video_upload(title, description_fingerprint)` when supplied, then immediately call `youtube.upload(str(path), title, description, max_retryable_errors=0, raise_errors=True)` with no intervening work. A callback exception prevents the remote call and returns `RETRYABLE/error_stage='checkpoint'`. A false upload result is a conclusive quota rejection and becomes `QUOTA_EXCEEDED/error_stage='video'`. A timeout, connection loss, or retryable 5xx after the callback becomes `RETRYABLE/error_stage='video', remote_outcome_unknown=True`; the caller must reconcile rather than retry upload. A conclusive 4xx authentication/configuration response becomes `FATAL` with `remote_outcome_unknown=False`.
7. A successful fresh upload sets `description_fingerprint` to the desired fingerprint. When resuming an existing `video_id`, compare the stored and desired description fingerprints; if they differ because highlights became available, call `youtube.update(video_id, title, description, raise_errors=True)` and checkpoint the new fingerprint before caption/playlist work.
8. If a caption path exists and caption is not checkpoint-complete, call `caption_exists` before `add_caption_result(..., raise_errors=True)`. Map `CAPTION_UPLOAD_QUOTA_EXCEEDED` to quota and retryable transport/server failures to retryable while retaining `video_id`. Authentication failures remain fatal.
9. If `playlist_id` exists and is not checkpoint-complete, call `playlist_contains` before `insert_into_playlist(..., raise_errors=True)`.
10. Call `get_processing_status(video_id, raise_errors=True)`. Set `youtube_processed=True` only for `processed`; return `FATAL/error_stage='processing'` for `failed` or `rejected` with the supplied reason; treat `uploaded`, `processing`, and `missing` as pending rather than complete.
11. Delete only `caption.path` when `caption.temporary` and caption upload is confirmed. Never mutate `video_path`.
12. Return `COMPLETE` only when requested caption/description/playlist stages and YouTube processing are complete; otherwise return `PENDING` unless a more specific error status was produced.

Do not add sleeps or retry loops.

- [ ] **Step 5: Run publication-service tests**

Run:

```shell
pipenv run pytest tests/test_youtube_publishing.py tests/test_youtube.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit the publication service**

```shell
git add recorder/publishing tests/test_youtube_publishing.py
git commit -m "feat: extract reusable YouTube publication service"
```

### Task 3: Adapt the Legacy Worker Without Changing File Lifecycle

**Files:**
- Modify: `recorder/app.py:159-280`
- Create: `tests/test_app_upload.py`

- [ ] **Step 1: Write a failing single-iteration legacy upload test**

First extract one loop body into a callable `process_upload_file(config, youtube, video_path)` so it can be tested without an infinite thread. Write `tests/test_app_upload.py` with temporary `upload` and `validate` trees and monkeypatched caption generation. Assert:

```python
def test_legacy_process_upload_file_moves_after_service_upload(tmp_path, monkeypatch):
    video = tmp_path / 'videos' / 'upload' / 'bilibili' / '1829181560' / '2026-07-27 18:00:00.mp4'
    video.parent.mkdir(parents=True)
    video.write_bytes(b'legacy-video')
    youtube = FakeYoutube(upload_id='yt123', processed=False)
    config = legacy_config(tmp_path)

    result = process_upload_file(config, youtube, str(video))

    target = tmp_path / 'videos' / 'validate' / 'bilibili' / '1829181560' / 'yt123__2026-07-27 18:00:00.mp4'
    assert result.video_id == 'yt123'
    assert not video.exists()
    assert target.read_bytes() == b'legacy-video'
```

Add failure assertions that an upload without `video_id` remains in `upload`, and a successful temporary VTT is removed by the service. Add a metadata fixture and assert it is deleted only after `video_id` is returned, matching the existing lifecycle.

- [ ] **Step 2: Run the focused test and verify the missing callable**

Run:

```shell
pipenv run pytest tests/test_app_upload.py -q
```

Expected: collection fails because `process_upload_file` does not exist.

- [ ] **Step 3: Extract `process_upload_file` and delegate publication**

Move the body of the current `for video_path in videos` loop into `process_upload_file`. Preserve metadata lookup and all existing Mongo caption providers, but represent the generated caption as:

```python
caption = CaptionArtifact(
    path=pathlib.Path(vtt_caption_path) if os.path.exists(vtt_caption_path) else None,
    highlights=highlights,
    temporary=True,
)
```

Instantiate `YoutubePublishService(youtube, config)`, call `publish_video`, delete the legacy `.metadata` only after `result.video_id` exists, and perform `os.rename` into `validate` only in that same successful-video branch. Keep the current upload-thread sleeps and quota behavior in the legacy adapter, not in the service.

Replace the loop body with:

```python
for video_path in videos:
    result = process_upload_file(config, youtube, video_path)
    if result.status is PublishStatus.QUOTA_EXCEEDED:
        time.sleep(quota_exceeded_sleep)
```

Do not change `validate_thread` deletion behavior.

- [ ] **Step 4: Run legacy and publication tests**

Run:

```shell
pipenv run pytest tests/test_app_upload.py tests/test_youtube_publishing.py tests/test_youtube.py -q
```

Expected: all tests pass, including source move into `validate` for the legacy path.

- [ ] **Step 5: Commit the legacy adapter**

```shell
git add recorder/app.py tests/test_app_upload.py
git commit -m "refactor: route legacy uploads through publication service"
```

### Task 4: Parse BililiveRecorder XML into VTT and Highlights

**Files:**
- Create: `recorder/danmaku/bilibili/bililive_xml.py`
- Create: `tests/test_bililive_xml.py`

- [ ] **Step 1: Write failing parser/provider tests**

Create XML fixtures inline with `tmp_path`. Cover ordinary messages, ignored non-`d` elements, negative/out-of-duration timestamps, Unicode, malformed XML, and missing XML:

```python
def test_prepare_caption_streams_normal_danmaku(tmp_path):
    xml = tmp_path / 'recording.xml'
    xml.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<i>'
        '<d p="1.250,1,25,16777215,1780000000,0,100,0">first</d>'
        '<gift ts="2.0">ignored</gift>'
        '<d p="3.500,1,25,16777215,1780000001,0,101,0">second</d>'
        '<d p="99.0,1,25,16777215,1780000002,0,102,0">late</d>'
        '</i>',
        encoding='utf8',
    )
    output = tmp_path / 'recording.vtt'

    artifact = prepare_bililive_xml_caption(
        xml_path=xml,
        output_path=output,
        start='2026-07-27 18:00:00',
        duration=10.0,
    )

    content = output.read_text(encoding='utf8')
    assert artifact.status == 'ready'
    assert 'first' in content
    assert 'second' in content
    assert 'ignored' not in content
    assert 'late' not in content
    assert artifact.dropped_out_of_range == 1
```

Assert missing XML returns `CaptionArtifact(path=None, status='missing')`; malformed XML returns status `invalid`, does not leave a partial VTT, and includes an error message.

- [ ] **Step 2: Run XML tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_xml.py -q
```

Expected: collection fails because `bililive_xml` does not exist.

- [ ] **Step 3: Implement a streaming parser and provider**

Define an immutable provider result extending the publication artifact data:

```python
@dataclass(frozen=True)
class BililiveCaptionArtifact:
    path: Path | None
    highlights: str = ''
    status: str = 'ready'
    dropped_out_of_range: int = 0
    error_message: str | None = None
    temporary: bool = True
```

Implement `iter_bililive_danmaku(xml_path, start, duration, counters)` with `ElementTree.iterparse(events=('end',))`. For each `d` element:

1. Split `p`; require at least one field.
2. Parse field zero as float seconds.
3. Strip text and reject empty content.
4. Accept only `0 <= relative_seconds <= duration`.
5. Yield `{'content': text, 'generation_time': start_epoch + relative_seconds}`.
6. Clear each processed element to bound memory.

Implement `prepare_bililive_xml_caption` by parsing twice: call `Caption(iter_bililive_danmaku(xml_path, start, duration, caption_counters), parse_datetime(start)).to_vtt(partial_path)` and call `generate_highlights(iter_bililive_danmaku(xml_path, start, duration, highlight_counters), start)` with a second fresh counter map. Report only `caption_counters` in the artifact so the two passes do not double the dropped-message count. Import `Caption`, `parse_datetime`, and `generate_highlights` from `recorder.danmaku`. Write to `output_path.with_suffix(output_path.suffix + '.partial')`, then atomically replace the generated VTT only after both passes complete. On parse failure, unlink only the partial VTT and return `invalid`.

- [ ] **Step 4: Run XML and existing caption tests**

Run:

```shell
pipenv run pytest tests/test_bililive_xml.py tests/test_youtube_publishing.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit the XML provider**

```shell
git add recorder/danmaku/bilibili/bililive_xml.py tests/test_bililive_xml.py
git commit -m "feat: generate captions from BililiveRecorder XML"
```

### Task 5: Add the Crash-Safe JSONL Journal and Process Lock

**Files:**
- Create: `recorder/bililive/__init__.py`
- Create: `recorder/bililive/models.py`
- Create: `recorder/bililive/journal.py`
- Create: `tests/test_bililive_journal.py`

- [ ] **Step 1: Write failing journal replay and corruption tests**

Cover append/replay, `fsync`, truncated final line, corrupt middle line, and exclusive locking:

```python
def test_journal_replays_latest_file_state(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')

    replay = journal.replay()

    assert replay.files['fp1'].event == 'video_uploaded'
    assert replay.files['fp1'].video_id == 'yt123'


def test_journal_ignores_only_truncated_final_line(tmp_path):
    path = tmp_path / 'state.jsonl'
    path.write_bytes(
        b'{"event":"baseline","fingerprint":"fp1"}\n'
        b'{"event":"video_uploaded"'
    )

    replay = JsonlJournal(path).replay()

    assert replay.files['fp1'].event == 'baseline'


def test_journal_rejects_corrupt_middle_line(tmp_path):
    path = tmp_path / 'state.jsonl'
    path.write_text(
        '{"event":"baseline","fingerprint":"fp1"}\n'
        'not-json\n'
        '{"event":"baseline","fingerprint":"fp2"}\n',
        encoding='utf8',
    )

    with pytest.raises(JournalCorruptError, match='line 2'):
        JsonlJournal(path).replay()
```

Use monkeypatch on `os.fsync` to assert every append flushes durable state. Open a second `ProcessLock` for the same path and assert `AlreadyRunningError`. Append from two test threads and verify every produced line replays, proving one in-process mutex covers serialize/write/flush/fsync as a single critical section.

- [ ] **Step 2: Run journal tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_journal.py -q
```

Expected: collection fails because `recorder.bililive.journal` does not exist.

- [ ] **Step 3: Define shared state models**

In `models.py`, define:

```python
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
    caption_uploaded: bool = False
    playlist_inserted: bool = False
    youtube_processed: bool = False
    description_fingerprint: str | None = None
    upload_started_at: str | None = None
    retry_at: str | None = None
    attempt: int = 0


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
```

`snapshot` is the most recently journaled path-to-`(size, mtime_ns)` map; `session_paths` is the complete set discovered since this session entered `RECORDING`. Create `session_id` once at the active transition and retain it through settlement; use it as the eventual `manifest_id`.

- [ ] **Step 4: Implement append, replay, and `fcntl` locking**

`JsonlJournal.append(event, **fields)` must add UTC `recorded_at`, serialize with `ensure_ascii=False` and compact separators, append one newline, flush, and call `os.fsync`. Protect serialization through fsync with one `threading.Lock` because the observation loop and the sole publisher worker share the journal.

Baseline events do not run ffprobe. Give them a deterministic `baseline:` fingerprint made from resolved path, size, and `mtime_ns`; accepted/invalid media events use the richer media fingerprint from Task 6. Replay treats both as opaque identifiers and cleanup keys by the stored path.

`replay()` acquires the same in-process mutex as append, validates every complete line, reduces file events cumulatively by `fingerprint` without discarding prior completed-stage fields, folds observation events into the current `JournalSessionState`, and folds every `session_manifest_ready`/`session_manifest_completed` pair into the ordered manifest tuple. A new `upload_started` replaces attempt timestamps/title/duration and resets `video_upload_rejected=False`; `video_upload_rejected` sets it true; `video_uploaded` sets `video_id` and clears ambiguity. It may ignore an invalid final byte sequence only when that line has no terminating newline. A syntactically valid event missing required fields raises `JournalCorruptError` rather than producing an unknown cleanup state.

`ProcessLock` opens `<state-dir>/monitor.lock`, calls `fcntl.flock(fd, LOCK_EX | LOCK_NB)`, and releases it in `__exit__`.

- [ ] **Step 5: Run journal tests**

Run:

```shell
pipenv run pytest tests/test_bililive_journal.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit journal and shared models**

```shell
git add recorder/bililive tests/test_bililive_journal.py
git commit -m "feat: persist Bililive publication state in JSONL"
```

### Task 6: Inspect and Classify Media Without Cut-Length Assumptions

**Files:**
- Modify: `recorder/bililive/models.py`
- Create: `recorder/bililive/media.py`
- Create: `tests/test_bililive_media.py`

- [ ] **Step 1: Write failing media inspection and classification tests**

Use a fake subprocess runner returning ffprobe JSON; do not invoke production files. Cover metadata `StartTime`, filename fallback, audio/video requirements, timeout classification, fingerprints, mixed 3h/4h durations, and tail selection:

```python
def test_classify_files_ignores_small_non_tail_but_keeps_valid_tail(tmp_path):
    first = media_info(tmp_path / 'a.flv', size=255 * 1024 * 1024, start=1, duration=300)
    middle = media_info(tmp_path / 'b.flv', size=2 * 1024**3, start=2, duration=4 * 3600)
    tail = media_info(tmp_path / 'c.flv', size=10 * 1024 * 1024, start=3, duration=120)

    classified = classify_session_files([first, middle, tail])

    assert classified[first.fingerprint].status == 'ignored_tiny'
    assert classified[middle.fingerprint].status == 'ready'
    assert classified[tail.fingerprint].status == 'ready'
    assert classified[tail.fingerprint].is_tail is True


def test_classify_files_ignores_tail_shorter_than_sixty_seconds(tmp_path):
    tail = media_info(tmp_path / 'tail.flv', size=10 * 1024 * 1024, start=3, duration=59.9)

    classified = classify_session_files([tail])

    assert classified[tail.fingerprint].status == 'ignored_invalid_tail'
```

Add a test showing a trailing corrupt file is excluded before tail selection, so the last playable file remains tail.

- [ ] **Step 2: Run media tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_media.py -q
```

Expected: collection fails because `recorder.bililive.media` does not exist.

- [ ] **Step 3: Add immutable media models and constants**

Add to `models.py`:

```python
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
```

Define the policy values exactly in `media.py`:

```python
MIN_NON_TAIL_SIZE_BYTES = 256 * 1024 * 1024
MIN_TAIL_DURATION_SECONDS = 60
FFPROBE_TIMEOUT_SECONDS = 120
SESSION_TIMEZONE = 'Asia/Shanghai'
```

- [ ] **Step 4: Implement low-priority ffprobe inspection**

Build one command per file:

```python
args = [
    ffprobe_path,
    '-v', 'error',
    '-print_format', 'json',
    '-show_format',
    '-show_streams',
    str(path),
]
if sys.platform.startswith('linux') and shutil.which('ionice'):
    args = ['ionice', '-c3', 'nice', '-n', '10', *args]
```

Run with `subprocess.run(args, timeout=FFPROBE_TIMEOUT_SECONDS, check=True, capture_output=True)`. Parse both audio and video streams. Parse the `StartTime` format tag with `email.utils.parsedate_to_datetime`; fall back to the filename interpreted in `Asia/Shanghai`. Preserve a non-empty `format.tags.title` as `stream_title` for the existing title suffix behavior. Compute fingerprint as SHA-256 of the UTF-8 string `resolved_path\0size\0mtime_ns\0start_iso\0duration_token`; never hash media bytes. The duration token is exactly three decimal places for valid probes and the literal `invalid` for a stable invalid probe, making replay fingerprints stable across JSON float representations.

Raise `MediaProbeRetryableError` on timeout or process-launch/storage `OSError`. For a manifest-stable file, classify ffprobe `CalledProcessError`, invalid JSON, missing duration, or absence of both required audio and video streams as `ignored_invalid`, recording bounded stderr and the exact reason. Re-stat after probing so a concurrently changed file returns to settlement instead of being mislabeled invalid.

- [ ] **Step 5: Implement `classify_session_files`**

Mark `probe_error`, missing duration, or missing audio/video as `ignored_invalid` first. Sort the remaining playable files by `(start_time, path.name)`, mark the final playable entry as tail, and apply exactly:

```python
if not is_tail and media.size < MIN_NON_TAIL_SIZE_BYTES:
    status = 'ignored_tiny'
elif is_tail and media.duration < MIN_TAIL_DURATION_SECONDS:
    status = 'ignored_invalid_tail'
else:
    status = 'ready'
```

Return a fingerprint-keyed mapping and include measured values in every reason string.
`inspect_media` and `classify_session_files` accept no configured/expected cut duration; the mixed-duration test is the regression guard for changing BililiveRecorder from three-hour to four-hour segments.

- [ ] **Step 6: Run media and XML tests**

Run:

```shell
pipenv run pytest tests/test_bililive_media.py tests/test_bililive_xml.py -q
```

Expected: all tests pass without invoking a real large FLV.

- [ ] **Step 7: Commit media inspection**

```shell
git add recorder/bililive/models.py recorder/bililive/media.py tests/test_bililive_media.py
git commit -m "feat: classify settled Bililive recordings"
```

### Task 7: Implement First-Run Baseline and Session Settlement

**Files:**
- Create: `recorder/bililive/monitor.py`
- Create: `tests/test_bililive_monitor.py`

- [ ] **Step 1: Write failing pure state-machine tests**

Use an injected clock/`id_factory` and synthetic snapshots. Cover offline baseline, live startup skip, API unavailability, live-to-settling transition, quiet reset, and ready after 30 minutes:

```python
def test_first_start_while_live_skips_entire_current_session():
    machine = SessionMonitorState(initialized=False)

    first = machine.observe(
        now=at(18, 0),
        room=RoomState(recording=True, streaming=True),
        snapshot={'a.flv': (100, 1)},
    )
    during = machine.observe(
        now=at(21, 0),
        room=RoomState(recording=True, streaming=True),
        snapshot={'a.flv': (200, 2), 'b.flv': (100, 1)},
    )
    settled = machine.observe(
        now=at(22, 31),
        room=RoomState(recording=False, streaming=False),
        snapshot={'a.flv': (200, 2), 'b.flv': (100, 1)},
    )

    assert first.state is SessionState.SKIP_CURRENT_SESSION
    assert set(during.baseline_paths) == {'a.flv', 'b.flv'}
    assert settled.state is SessionState.WAITING
    assert settled.ready_paths == ()


def test_offline_session_requires_thirty_unchanged_minutes():
    machine = armed_machine()
    machine.observe(at(18, 0), RoomState(True, True), {'a.flv': (100, 1)})
    machine.observe(at(22, 0), RoomState(False, False), {'a.flv': (200, 2)})

    early = machine.observe(at(22, 29), RoomState(False, False), {'a.flv': (200, 2)})
    ready = machine.observe(at(22, 30), RoomState(False, False), {'a.flv': (200, 2)})

    assert early.state is SessionState.SETTLING
    assert ready.state is SessionState.READY
    assert ready.ready_paths == ('a.flv',)
```

An API-unavailable observation must return a wait action and never advance to `READY`.

- [ ] **Step 2: Run monitor tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_monitor.py -q
```

Expected: collection fails because `recorder.bililive.monitor` does not exist.

- [ ] **Step 3: Implement pure session monitoring**

Define:

```python
POLL_INTERVAL_SECONDS = 60
QUIET_PERIOD_SECONDS = 30 * 60


@dataclass(frozen=True)
class MonitorDecision:
    state: SessionState
    session_id: str | None = None
    baseline_paths: tuple[str, ...] = ()
    ready_paths: tuple[str, ...] = ()
    session_paths: tuple[str, ...] = ()
    snapshot: dict[str, tuple[int, int]] = field(default_factory=dict)
    quiet_since: datetime | None = None
    reason: str = ''
```

`SessionMonitorState.observe(now, room, snapshot)` must have no I/O. Snapshots contain only `.flv` and same-directory `.xml` paths. Compare full path-to-`(size, mtime_ns)` snapshots; any addition, removal, size change, or mtime change resets `quiet_since`. While `WAITING`, retain the latest known snapshot. On transition to `RECORDING`, create one stable `session_id`, seed session paths only from paths added or changed since that waiting snapshot, then accumulate later additions/changes. `ready_paths` contains only the accumulated FLV paths; XML paths participate in quiet detection but are paired later by stem. This excludes unrelated historical files without losing an FLV created between two API polls.

Provide `restore(replay)` so a Supervisor restart resumes `SKIP_CURRENT_SESSION`, `RECORDING`, or `SETTLING` with its stable session ID and accumulated paths. The caller appends a `session_state` event containing session ID, state, session paths, snapshot, `quiet_since`, and `started_at` whenever one of those values changes. An offline first run may append baseline file events immediately. A live first run stores baseline candidates only inside protected `SKIP_CURRENT_SESSION` state; append/fsync their baseline file events only after the room is offline and the full 30-minute quiet period completes. On normal `READY`, append and fsync a `session_manifest_ready` event with `manifest_id=session_id` and the frozen FLV paths before returning the observation state to `WAITING`; that journaled manifest, rather than an in-memory queue, is the publisher's source of truth. On restart in `SETTLING`, retain the session ID/paths but reset `quiet_since` on the first equal observation and wait a fresh full 30 minutes; downtime can never count as proven quiet time. Add tests for conservative restart, deferred live-baseline eligibility, multiple retained manifests, and manifest persistence before re-arming.

- [ ] **Step 4: Run monitor and journal tests**

Run:

```shell
pipenv run pytest tests/test_bililive_monitor.py tests/test_bililive_journal.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit the session state machine**

```shell
git add recorder/bililive/monitor.py tests/test_bililive_monitor.py
git commit -m "feat: settle complete Bililive sessions"
```

### Task 8: Coordinate Publication, Resume Partial Work, and Fail Closed

**Files:**
- Create: `recorder/bililive/runner.py`
- Create: `tests/test_bililive_runner.py`

- [ ] **Step 1: Write failing coordinator tests**

Use fake journal, probe, publisher, clock, and YouTube client. Cover strict sequential publication, replay of journaled ready manifests, `upload_started` journaling before API call, resume from `video_uploaded`, ambiguous crash state, caption backfill, and source immutability:

```python
def test_runner_journals_upload_started_before_calling_youtube(tmp_path):
    events = []
    journal = FakeJournal(events)
    publisher = FakePublisher(events, result=successful_result('yt123'))
    runner = BililivePublishRunner(journal=journal, publisher=publisher)

    runner.publish_one(ready_media(tmp_path), caption_provider=None)

    assert events[:2] == [
        ('journal', 'upload_started'),
        ('publisher', 'publish_video'),
    ]


def test_runner_resumes_caption_without_reupload(tmp_path):
    journal = journal_with_video_uploaded('fp1', 'yt123')
    publisher = FakePublisher(result=successful_result('yt123'))
    runner = BililivePublishRunner(journal=journal, publisher=publisher)

    runner.publish_one(ready_media(tmp_path, fingerprint='fp1'), caption_provider=None)

    checkpoint = publisher.calls[0].checkpoint
    assert checkpoint.video_id == 'yt123'
    assert checkpoint.video_uploaded is True


def test_runner_marks_unresolved_upload_started_as_ambiguous(tmp_path):
    journal = journal_with_upload_started('fp1')
    runner = BililivePublishRunner(
        journal=journal,
        publisher=FailIfCalledPublisher(),
        recent_uploads=lambda: [],
    )

    result = runner.recover_ambiguous(ready_media(tmp_path, fingerprint='fp1'))

    assert result.status == 'ambiguous'
    assert journal.last_event == 'ambiguous'
```

Add a unique recent-upload match test using title, publication time window, and stored source duration; multiple matches, a missing remote duration, or a duration difference greater than one second remain ambiguous. Add a caption-backfill test proving a later valid XML causes description update plus caption upload without video re-upload. Add a test where the publisher returns `remote_outcome_unknown=True` after `upload_started`; assert the runner appends `ambiguous` and never schedules video upload retry. Add two manifests where the older one is waiting on a future caption retry and assert `run_pending_once` selects the later manifest's due video.

- [ ] **Step 2: Run runner tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_runner.py -q
```

Expected: collection fails because `recorder.bililive.runner` does not exist.

- [ ] **Step 3: Implement the sequential coordinator**

Define the coordinator result and entry points:

```python
RETRY_BASE_SECONDS = 5 * 60
RETRY_MAX_SECONDS = 6 * 60 * 60
AMBIGUOUS_TIME_SKEW_SECONDS = 5 * 60
AMBIGUOUS_DURATION_TOLERANCE_SECONDS = 1.0


@dataclass(frozen=True)
class RunnerResult:
    status: str
    fingerprint: str | None = None
    retry_at: datetime | None = None
    message: str = ''
```

The exact entry-point signatures are `run_pending_once(self, replay: JournalReplay) -> RunnerResult | None` and `publish_one(self, classified: ClassifiedMedia, caption_provider=prepare_bililive_xml_caption) -> RunnerResult`. Passing `caption_provider=None` skips artifact preparation in unit tests and records `not_requested`; production always uses the default XML provider. `run_pending_once` scans manifests by `settled_at`, selects the oldest currently due file across them, and calls `publish_one` at most once; an older manifest waiting on caption/retry time must not starve a later ready video. `publish_session(classified_media)` loops through a newly classified manifest by repeatedly applying the same one-file logic. These methods must:

1. Append ignore events immediately for ignored classifications.
2. Iterate ready files sorted by start time; never create an executor or additional worker. The CLI owns exactly one long-lived publication thread around this runner.
3. Re-stat every FLV/XML before work; return the session to settling if size/mtime changed.
4. Generate the XML caption artifact in the state directory.
5. Convert `BililiveCaptionArtifact` explicitly into the publication-layer `CaptionArtifact`; do not make either package import the runner to achieve duck typing.
6. Build a `before_video_upload(title, description_fingerprint)` closure that appends/fsyncs `upload_started` with fingerprint, source paths, generated title, source duration, description fingerprint, and `upload_started_at`. Pass it to the service so the event occurs after local validation but immediately before the first video API call.
7. Build `PublishCheckpoint`, including `description_fingerprint`, from replayed events.
8. Call `YoutubePublishService.publish_video` with the original FLV path, `source_type='bilibili'`, `source_name=str(room_id)`, formatted start time, and the probed stream title.
9. Append `video_uploaded` immediately when `video_id` first appears, then append `description_updated`, `caption_uploaded`, `playlist_inserted`, and `youtube_processed` separately as each stage completes.
10. If a video-stage result has no `video_id` and `remote_outcome_unknown=True`, append `ambiguous` immediately and never schedule upload retry. When the callback ran but the service reports a conclusive quota/authentication/permanent-HTTP rejection, append/fsync `video_upload_rejected` before any retry/fatal event so replay knows no accepted upload is outstanding. Persist other `RETRYABLE`, conclusive `QUOTA_EXCEEDED`, and processing-`PENDING` outcomes as `stage_retry_scheduled` with stage, status, incremented attempt, and UTC `retry_at`. Use exponential backoff from five minutes to six hours; quota begins at the six-hour cap. Continue to the next ready file rather than sleeping. Persist `FATAL` and `AMBIGUOUS` without automatic retry while continuing unrelated files.
11. Treat missing/invalid XML as a retained caption stage. On a later poll, retry XML preparation; when it becomes valid, pass a checkpoint with the existing `video_id` and old description fingerprint so the service updates highlights and uploads captions without video re-upload.
12. Never call `copy`, `move`, `rename`, or `unlink` on source FLV/XML.
13. Upload every `ready` FLV independently. Never concatenate, remux, transcode, probe fragment boundaries, or attempt gap repair.
14. Append `session_manifest_completed` only when every manifest file is ignored or has all requested video/caption/playlist/processing stages complete. Missing/invalid XML keeps only its caption backfill stage pending and does not block due work from later manifests.

Implement `recover_ambiguous` only for replayed `upload_started` states lacking both `video_id` and `video_upload_rejected`. Load up to 50 recent uploads and match a unique candidate on exact generated title, publication time between five minutes before `upload_started_at` and five minutes after recovery time, and remote duration within one second of the stored ffprobe duration. Define both tolerances as file-level constants. If zero or multiple candidates remain, append `ambiguous` and do not call video upload. A unique match is journaled as `video_uploaded` before normal stage resumption.

- [ ] **Step 4: Run runner, publisher, XML, and journal tests**

Run:

```shell
pipenv run pytest \
  tests/test_bililive_runner.py \
  tests/test_youtube_publishing.py \
  tests/test_bililive_xml.py \
  tests/test_bililive_journal.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit publication coordination**

```shell
git add recorder/bililive/runner.py tests/test_bililive_runner.py
git commit -m "feat: resume Bililive publication stages safely"
```

### Task 9: Replace Blind Disk Cleanup with State-Aware Cleanup

**Files:**
- Create: `recorder/bililive/cleanup.py`
- Create: `tests/test_bililive_cleanup.py`

- [ ] **Step 1: Write failing eligibility and deletion tests**

Cover every approved state and independent FLV/XML eligibility:

```python
def test_cleanup_deletes_processed_flv_but_retains_invalid_xml(tmp_path):
    video = tmp_path / 'recording.flv'
    xml = tmp_path / 'recording.xml'
    video.write_bytes(b'video')
    xml.write_text('<broken>', encoding='utf8')
    state = file_state(
        video=video,
        xml=xml,
        youtube_processed=True,
        caption_status='invalid',
    )
    cleanup = StateAwareCleanup(
        journal=FakeJournal(),
        root=tmp_path,
        disk_usage=lambda path: 86,
    )

    cleanup.run([state], dry_run=False)

    assert not video.exists()
    assert xml.exists()


@pytest.mark.parametrize('event', [
    'ready', 'upload_started', 'video_uploaded', 'ambiguous', 'unknown'
])
def test_cleanup_never_deletes_protected_video(tmp_path, event):
    video = tmp_path / 'recording.flv'
    video.write_bytes(b'video')

    StateAwareCleanup(FakeJournal(), tmp_path, lambda path: 99).run(
        [file_state(video=video, event=event)],
        dry_run=False,
    )

    assert video.exists()
```

Also assert baseline/ignored files are eligible oldest-first, a baseline path currently present in `SKIP_CURRENT_SESSION` is protected, caption-uploaded XML is eligible, dry-run returns planned decisions without journal writes or unlinking, an above-threshold disk with no eligible paths returns `exhausted=True` without deletion, and symlinks/paths resolving outside `root` are always protected.

- [ ] **Step 2: Run cleanup tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_cleanup.py -q
```

Expected: collection fails because `recorder.bililive.cleanup` does not exist.

- [ ] **Step 3: Implement cleanup eligibility and execution**

Define:

```python
DISK_CLEANUP_THRESHOLD_PERCENT = 85


@dataclass(frozen=True)
class CleanupResult:
    deleted: tuple[Path, ...]
    protected: tuple[Path, ...]
    disk_usage_percent: int
    exhausted: bool
```

`StateAwareCleanup(journal, root, disk_usage=filesystem_usage_percent, clock_ns=time.time_ns).run(states, dry_run)` must return immediately below 85 percent. Above threshold, consider only paths whose own mtime is at least six hours old, sort eligible paths by mtime, and delete one at a time, recomputing root disk usage after each delete. Append `source_deleted` with path, fingerprint, and reason after successful unlink. In dry-run, calculate and return the same ordered candidates but do not unlink or append any journal event.

Eligibility rules are exact:

- FLV: ignored, or `youtube_processed=True` with a durable `video_id`.
- XML: paired ignored, or `caption_uploaded=True` with no pending caption refresh.
- Baseline-only files are always protected because this service does not own their lifecycle.
- Any ambiguous, unknown, currently recording, ready, uploading, or remotely unprocessed video: protected.
- Any missing path, non-regular file, symlink, or path whose resolved parent is outside the resolved recorder root: protected regardless of journal fields.

Before applying file-level eligibility, build the protected path set from the replayed current session whenever it is `SKIP_CURRENT_SESSION`, `RECORDING`, or `SETTLING`. Membership in that set overrides an older ignored event for the same path. Revalidate the candidate through an open recorder-root directory fd immediately before a direct unlink; require the same device, inode, size, and mtime, and never follow symlinks or move the source to quarantine.

When no eligible path remains above threshold, return `exhausted=True` and log at critical level.

- [ ] **Step 4: Run cleanup and journal tests**

Run:

```shell
pipenv run pytest tests/test_bililive_cleanup.py tests/test_bililive_journal.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit state-aware cleanup**

```shell
git add recorder/bililive/cleanup.py tests/test_bililive_cleanup.py
git commit -m "feat: clean Bililive sources from publication state"
```

### Task 10: Wire the CLI, Dry Run, Documentation, and Final Verification

**Files:**
- Create: `recorder/bililive/service.py`
- Create: `recorder/utils/bililive_directory_monitor.py`
- Create: `tests/test_bililive_service.py`
- Create: `tests/test_bililive_directory_monitor.py`
- Create: `tests/test_bililive_pipeline_integration.py`
- Modify: `recorder/utils/README.md`

- [ ] **Step 1: Write failing CLI wiring tests**

Test that help and dry-run never initialize YouTube credentials, an API failure causes a wait-only `--once` iteration without publication, `--once` executes one observation, source/state paths are resolved, and a corrupt middle journal line returns a nonzero startup result before YouTube or cleanup initialization:

```python
def test_dry_run_does_not_initialize_youtube(monkeypatch, tmp_path):
    def fail_youtube_init(config):
        raise AssertionError('YouTube client must not initialize in dry-run')

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube',
        fail_youtube_init,
    )

    result = run_monitor(
        root=str(tmp_path),
        room_id=1829181560,
        api_url='http://127.0.0.1:2356',
        state_dir=str(tmp_path / 'state'),
        dry_run=True,
        once=True,
        room_state_provider=lambda: RoomState(False, False),
    )

    assert result == 0
```

Use injected dependencies rather than opening real network connections in tests. In `tests/test_bililive_service.py`, block the fake publisher on a `threading.Event`, perform two observation iterations while it remains blocked, and assert both API snapshots are journaled. Also assert one worker never starts a second publication concurrently and `stop()` joins a cooperative worker cleanly; a second test keeps it blocked and asserts shutdown returns after the injected join timeout. Gate tests must prove `cleanup.run` and the next `run_pending_once` are both blocked when the API is unavailable, `recording=True`, `streaming=True`, or the monitor is `RECORDING`/`SETTLING`. An available `RoomState(False, False)` decision in `READY` or `WAITING` opens the gate and wakes exactly one pending worker iteration; a later active observation closes it before another cleanup or upload begins.

- [ ] **Step 2: Run CLI tests and verify import failure**

Run:

```shell
pipenv run pytest tests/test_bililive_directory_monitor.py -q
```

Expected: collection fails because the service and util modules do not exist.

- [ ] **Step 3: Implement `run_monitor` and Fire entry point**

Use the callable signature `run_monitor(root, room_id, api_url, state_dir=None, dry_run=False, once=False, room_state_provider=None)`.

Implementation requirements:

1. Resolve and validate `<root>/<room_id>`.
2. Default state directory to `<recorder.base_path>/var/bililive/<room_id>`.
3. Acquire `ProcessLock` before replay or cleanup.
4. Use `httpx.Client(timeout=5)` against `<api_url>/api/room/<room_id>` when no provider is injected.
5. Require boolean `recording` and `streaming`; malformed or unavailable API state produces a wait-only iteration.
6. In dry-run, replay/baseline/probe/XML decisions are printed, plus cleanup decisions only when the settled-offline gate is open; no YouTube client, journal append, source unlink, or remote mutation occurs.
7. In normal mode, create `Youtube`, `YoutubePublishService`, journal, runner, monitor state, and cleanup once, then poll every 60 seconds. Append the monitor's full `session_state` payload whenever it changes; append first-run `baseline` file events before arming the next session, but only after a live startup's skipped session has settled as specified in Task 7.
8. `once=True` runs one observation and returns an integer exit code without sleep.
9. Expose `run_monitor` through `fire.Fire({'run': run_monitor})` only under `if __name__ == '__main__'`.

Implement `BililiveDirectoryService` in `service.py`. Its main thread owns API observations, directory snapshots, the pure monitor state machine, and a thread-safe publication gate. The exact gate predicate is:

```python
cleanup_allowed = (
    room is not None
    and not room.active
    and decision.state in {SessionState.READY, SessionState.WAITING}
)
```

Unavailable/malformed input, active room state, or `RECORDING`/`SETTLING` closes it immediately. Its one daemon publication thread waits on a `threading.Event`, replays the JSONL journal, and performs state-aware cleanup before pending publication only while this gate is open. The worker rechecks the same gate before cleanup and after every item. Do not cancel an already-running runner/YouTube call when the gate closes, because an interrupted upload would create ambiguity, but do not begin cleanup or the next file until it reopens. A frozen manifest is fsynced before signaling the worker. The event is merely a wakeup optimization: startup and timeout wakeups always replay the journal, so a crash between append and signal cannot lose work. `stop()` sets a stop event, wakes the worker, and joins for the file-level `WORKER_JOIN_TIMEOUT_SECONDS = 30`; if an upload remains blocked, log a warning and let Supervisor terminate the daemon process, whose pre-upload checkpoint will force reconciliation on restart. No ffprobe/ffmpeg-family process or video upload may exist outside this sole worker.

- [ ] **Step 4: Document commands and operational cutover**

Add to `recorder/utils/README.md`:

```shell
# Dry run and initial baseline inspection
pipenv run python -m recorder.utils.bililive_directory_monitor run \
  /data/BililiveRecorder \
  --room-id=1829181560 \
  --api-url=http://100.87.152.23:2356 \
  --dry-run

# Supervisor command
pipenv run python -u -m recorder.utils.bililive_directory_monitor run \
  /data/BililiveRecorder \
  --room-id=1829181560 \
  --api-url=http://100.87.152.23:2356
```

Document that BililiveRecorder `RecordDanmaku` must be enabled, the first active/current session is baseline-only, source FLV/XML are not moved by publication, the JSONL state file must never be log-rotated, and the old cleanup cron must remain enabled until the new cleanup dry run is reviewed.

- [ ] **Step 5: Run all focused new tests**

Before the focused run, add one integration test guarded by `pytest.mark.skipif` when `ffmpeg` or `ffprobe` is absent. Generate a one-second FLV with one video stream and one silent audio stream into `tmp_path`, write a same-stem XML with two ordinary messages, run the real sequential probe and XML provider, publish through `FakeYoutube`, and assert the source FLV/XML inode, size, and mtime remain unchanged. The command fixture is exactly:

```python
subprocess.run([
    'ffmpeg', '-v', 'error', '-y',
    '-f', 'lavfi', '-i', 'color=c=black:s=320x180:r=1:d=1',
    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
    '-shortest', '-c:v', 'flv', '-c:a', 'aac',
    str(video_path),
], check=True, timeout=30)
```

This is the only test that invokes real ffmpeg-family binaries; it creates no production-sized media and runs one process at a time.

Run:

```shell
pipenv run pytest \
  tests/test_youtube.py \
  tests/test_youtube_publishing.py \
  tests/test_app_upload.py \
  tests/test_bililive_xml.py \
  tests/test_bililive_journal.py \
  tests/test_bililive_media.py \
  tests/test_bililive_monitor.py \
  tests/test_bililive_runner.py \
  tests/test_bililive_service.py \
  tests/test_bililive_cleanup.py \
  tests/test_bililive_directory_monitor.py \
  tests/test_bililive_pipeline_integration.py -q
```

Expected: all focused tests pass with zero failures.

- [ ] **Step 6: Run the full repository suite**

Run:

```shell
pipenv run pytest -q
```

Expected: zero failures. If the existing live-network tests fail because their external stream is unavailable, rerun all non-network modules, report the exact network-only failure, and do not claim the full suite passed.

- [ ] **Step 7: Run static and mutation checks**

Run:

```shell
python -m compileall -q recorder tests
git diff --check
rg -n "shutil\.move|os\.rename|Path\([^)]*\)\.rename" \
  recorder/publishing \
  recorder/bililive/runner.py \
  recorder/bililive/service.py \
  recorder/bililive/monitor.py \
  recorder/bililive/media.py \
  recorder/utils/bililive_directory_monitor.py
```

Expected: compilation and diff checks exit zero; the source-mutation search returns no matches in publication paths. Cleanup is excluded because it is the only direct-mode module authorized to unlink state-eligible source files.

- [ ] **Step 8: Commit CLI and documentation**

```shell
git add recorder/bililive/service.py recorder/utils/bililive_directory_monitor.py recorder/utils/README.md tests/test_bililive_service.py tests/test_bililive_directory_monitor.py tests/test_bililive_pipeline_integration.py
git commit -m "feat: add Bililive directory publisher mode"
```

- [ ] **Step 9: Perform read-only deployment preflight on `instance-1`**

Run only after all local tests pass:

```shell
ssh instance-1 'supervisorctl status'
ssh instance-1 'df -h /data/BililiveRecorder'
ssh instance-1 'jq ".global.RecordDanmaku" /data/BililiveRecorder/config.json'
ssh instance-1 'curl -fsS http://100.87.152.23:2356/api/room/1829181560'
```

Expected: BililiveRecorder is running, disk has working headroom, `RecordDanmaku.Value` is true, and the room API returns booleans for `recording` and `streaming`. These commands are read-only.

- [ ] **Step 10: Deploy with an explicit operational checkpoint**

Do not change Supervisor or cron without explicit approval in the execution session. After approval:

1. Deploy the tested commit to `instance-1`.
2. Run the documented dry-run and inspect baseline/classification/cleanup output.
3. After the dry-run is approved, disable the old hourly `/root/auto_clean_disk.sh` cron and immediately add/start the new Supervisor program, whose normal worker includes state-aware cleanup.
4. Restart it once and verify JSONL replay preserves the baseline.
5. Observe one complete live session and verify video, VTT, playlist, journal, source immutability, and cleanup eligibility.
6. Keep the old cron definition available but disabled until the new mode has completed that first-session verification, so rollback can restore it explicitly.

Record the exact deployed commit and Supervisor status in the handoff.

## Reference Documentation

- YouTube supports direct FLV uploads: https://support.google.com/youtube/troubleshooter/2888402
- `playlistItems.list` supports `playlistId` plus optional `videoId`: https://developers.google.com/youtube/v3/docs/playlistItems/list
- The authenticated channel exposes its uploads playlist through `contentDetails.relatedPlaylists.uploads`: https://developers.google.com/youtube/v3/docs/channels
- BililiveRecorder XML format: https://rec.danmuji.org/user/danmaku/
- BililiveRecorder settings including `RecordDanmaku`: https://rec.danmuji.org/reference/settings/
