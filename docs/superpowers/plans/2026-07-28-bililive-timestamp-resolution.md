# Bililive Timestamp Resolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve BililiveRecorder start times across ffprobe, XML, filename, and host timezone differences while always formatting YouTube title time in Asia/Shanghai.

**Architecture:** Add a focused timestamp module that parses and reconciles absolute candidates without consulting the process timezone. `inspect_media` reads the stable XML header and uses this resolver, while the runner independently normalizes persisted timestamps to Asia/Shanghai immediately before calling the YouTube publisher.

**Tech Stack:** Python 3.10, `datetime`/`zoneinfo`, `xml.etree.ElementTree`, ffprobe JSON, pytest

---

### Task 1: Add the Pure Timestamp Resolver

**Files:**
- Create: `recorder/bililive/timestamps.py`
- Create: `tests/test_bililive_timestamps.py`

- [ ] **Step 1: Write failing resolver tests**

Create tests that use no filesystem or subprocess:

```python
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from recorder.bililive.timestamps import (
    TIMESTAMP_CONFLICT_TOLERANCE_SECONDS,
    resolve_start_time,
)


SHANGHAI = ZoneInfo('Asia/Shanghai')


def test_real_metadata_instants_agree_and_return_shanghai_time():
    result = resolve_start_time(
        Path('2026-07-27 19:31:59.flv'),
        {'StartTime': '2026-07-27T11:31:59.154000Z'},
        '2026-07-27T20:31:59.1494083+09:00',
        0,
    )

    assert result.start_time == datetime(
        2026, 7, 27, 19, 31, 59, 154000, tzinfo=SHANGHAI
    )
    assert result.source == 'ffprobe'
    assert result.error is None


@pytest.mark.parametrize('delta', [5, 5.001])
def test_metadata_conflict_boundary(delta):
    result = resolve_start_time(
        Path('ignored.flv'),
        {'starttime': '2026-07-27T11:31:00Z'},
        f'2026-07-27T11:31:{delta:06.3f}Z',
        0,
    )

    if delta <= TIMESTAMP_CONFLICT_TOLERANCE_SECONDS:
        assert result.error is None
    else:
        assert 'conflicting start times' in result.error
        assert 'ffprobe=' in result.error
        assert 'xml=' in result.error


@pytest.mark.parametrize(
    ('filename', 'expected'),
    [
        ('2026-07-27 19:31:59.flv', (2026, 7, 27, 19, 31, 59)),
        ('2026-07-27T19-31-59.flv', (2026, 7, 27, 19, 31, 59)),
        ('2026-07-27_19-31-59.flv', (2026, 7, 27, 19, 31, 59)),
    ],
)
def test_filename_variants_are_explicitly_shanghai(filename, expected):
    result = resolve_start_time(Path(filename), {}, None, 0)

    assert result.start_time == datetime(*expected, tzinfo=SHANGHAI)
    assert result.source == 'filename'
    assert result.error is None


def test_ffprobe_only_and_xml_only_are_accepted():
    ffprobe = resolve_start_time(
        Path('unknown.flv'),
        {'STARTTIME': 'Mon, 27 Jul 2026 19:30:00 +0800'},
        None,
        0,
    )
    xml = resolve_start_time(
        Path('unknown.flv'), {}, '2026-07-27T20:30:00+09:00', 0
    )

    assert ffprobe.start_time.isoformat() == '2026-07-27T19:30:00+08:00'
    assert ffprobe.source == 'ffprobe'
    assert xml.start_time.isoformat() == '2026-07-27T19:30:00+08:00'
    assert xml.source == 'xml'


def test_naive_metadata_uses_shanghai_not_process_timezone(monkeypatch):
    monkeypatch.setenv('TZ', 'America/Los_Angeles')
    result = resolve_start_time(
        Path('unknown.flv'), {'StartTime': '2026-07-27T19:30:00'}, None, 0
    )

    assert result.start_time.isoformat() == '2026-07-27T19:30:00+08:00'


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('2026-01-15T08:00:00-05:00', '2026-01-15T21:00:00+08:00'),
        ('2026-07-15T08:00:00-04:00', '2026-07-15T20:00:00+08:00'),
    ],
)
def test_dst_season_offsets_normalize_by_absolute_instant(raw, expected):
    result = resolve_start_time(
        Path('unknown.flv'), {'StartTime': raw}, None, 0
    )

    assert result.start_time.isoformat() == expected


def test_no_valid_source_is_not_uploadable():
    result = resolve_start_time(Path('unknown.flv'), {}, None, 1_000_000_000)

    assert result.source == 'mtime_diagnostic'
    assert result.error == 'missing valid ffprobe, XML, and filename start time'
```

- [ ] **Step 2: Run the tests and verify import failure**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_timestamps.py -q
```

Expected: collection fails because `recorder.bililive.timestamps` does not exist.

- [ ] **Step 3: Implement the resolver**

Create `timestamps.py` with these public contracts and exact policy:

```python
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SESSION_TIMEZONE = ZoneInfo('Asia/Shanghai')
TIMESTAMP_CONFLICT_TOLERANCE_SECONDS = 5
_FILENAME_TIMESTAMP = re.compile(
    r'^(\d{4}-\d{2}-\d{2})[ T_](\d{2})[:-](\d{2})[:-](\d{2})'
)


@dataclass(frozen=True)
class TimestampResolution:
    start_time: datetime
    source: str
    error: str | None = None


def normalized_tags(tags):
    return {
        str(name).casefold(): value
        for name, value in tags.items()
        if isinstance(name, str)
    }


def _parse_metadata_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    normalized = raw[:-1] + '+00:00' if raw.endswith(('Z', 'z')) else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=SESSION_TIMEZONE)
    return parsed


def _filename_time(path):
    match = _FILENAME_TIMESTAMP.match(path.stem)
    if match is None:
        return None
    try:
        parsed = datetime.strptime(
            f'{match.group(1)} {match.group(2)}:{match.group(3)}:{match.group(4)}',
            '%Y-%m-%d %H:%M:%S',
        )
    except ValueError:
        return None
    return parsed.replace(tzinfo=SESSION_TIMEZONE)


def _shanghai(value):
    return value.astimezone(SESSION_TIMEZONE)


def resolve_start_time(path, tags, xml_start_time, mtime_ns):
    tags = normalized_tags(tags)
    ffprobe = _parse_metadata_time(tags.get('starttime'))
    xml = _parse_metadata_time(xml_start_time)
    if ffprobe is not None and xml is not None:
        difference = abs(
            (ffprobe.astimezone(timezone.utc) - xml.astimezone(timezone.utc))
            .total_seconds()
        )
        if difference > TIMESTAMP_CONFLICT_TOLERANCE_SECONDS:
            return TimestampResolution(
                _shanghai(ffprobe),
                'conflict',
                'conflicting start times: '
                f'ffprobe={ffprobe.isoformat()}, xml={xml.isoformat()}, '
                f'difference_seconds={difference:.6f}',
            )
        return TimestampResolution(_shanghai(ffprobe), 'ffprobe')
    if ffprobe is not None:
        return TimestampResolution(_shanghai(ffprobe), 'ffprobe')
    if xml is not None:
        return TimestampResolution(_shanghai(xml), 'xml')
    filename = _filename_time(Path(path))
    if filename is not None:
        return TimestampResolution(filename, 'filename')
    diagnostic = datetime.fromtimestamp(
        mtime_ns / 1_000_000_000, SESSION_TIMEZONE
    )
    return TimestampResolution(
        diagnostic,
        'mtime_diagnostic',
        'missing valid ffprobe, XML, and filename start time',
    )
```

- [ ] **Step 4: Run resolver tests**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_timestamps.py -q
```

Expected: all resolver tests pass.

- [ ] **Step 5: Commit the pure resolver**

```shell
git add recorder/bililive/timestamps.py tests/test_bililive_timestamps.py
git commit -m "feat: resolve Bililive recording timestamps"
```

### Task 2: Read Stable XML Header Metadata

**Files:**
- Modify: `recorder/bililive/timestamps.py`
- Modify: `tests/test_bililive_timestamps.py`

- [ ] **Step 1: Write failing XML-header tests**

Add tests for a namespaced or plain record-info element, missing XML, malformed
header, and an identity change:

```python
from recorder.bililive.timestamps import (
    TimestampReadRetryableError,
    read_xml_start_time,
)


@pytest.mark.parametrize(
    'record_info',
    [
        '<BililiveRecorderRecordInfo',
        '<x:BililiveRecorderRecordInfo xmlns:x="urn:bililive"',
    ],
)
def test_reads_record_info_without_parsing_danmaku_tail(tmp_path, record_info):
    xml = tmp_path / 'recording.xml'
    xml.write_text(
        f'<i>{record_info} '
        'start_time="2026-07-27T20:31:59.1494083+09:00"/>'
        '<d p="bad">unterminated',
        encoding='utf8',
    )

    assert read_xml_start_time(xml) == (
        '2026-07-27T20:31:59.1494083+09:00'
    )


def test_missing_or_malformed_xml_header_returns_none(tmp_path):
    assert read_xml_start_time(tmp_path / 'missing.xml') is None
    malformed = tmp_path / 'malformed.xml'
    malformed.write_text('<i><broken', encoding='utf8')
    assert read_xml_start_time(malformed) is None


def test_xml_identity_change_is_retryable(tmp_path):
    xml = tmp_path / 'recording.xml'
    xml.write_text(
        '<i><BililiveRecorderRecordInfo start_time="2026-07-27T00:00:00Z"/></i>',
        encoding='utf8',
    )
    real_stat = Path.stat
    calls = 0

    def changing_stat(path):
        nonlocal calls
        result = real_stat(path)
        calls += 1
        if calls == 2:
            return type('ChangedStat', (), {
                'st_size': result.st_size + 1,
                'st_mtime_ns': result.st_mtime_ns,
            })()
        return result

    with pytest.raises(TimestampReadRetryableError, match='changed'):
        read_xml_start_time(xml, statter=changing_stat)
```

- [ ] **Step 2: Run the XML tests and verify failure**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_timestamps.py -q
```

Expected: fail because `read_xml_start_time` and
`TimestampReadRetryableError` do not exist.

- [ ] **Step 3: Implement bounded XML-header reading**

Add `ElementTree.iterparse` with `events=('start',)`, stop immediately when the
local tag name is `BililiveRecorderRecordInfo`, and compare `(st_size,
st_mtime_ns)` before and after. Missing files and a parse error before record
info return `None`; other `OSError` values and identity changes raise
`TimestampReadRetryableError`. Add `from xml.etree import ElementTree`; `Path`
already exists from Task 1. The function is:

```python
class TimestampReadRetryableError(RuntimeError):
    pass


def read_xml_start_time(
    xml_path,
    statter=lambda path: path.stat(),
    parser=ElementTree.iterparse,
):
    xml_path = Path(xml_path)
    try:
        before = statter(xml_path)
    except FileNotFoundError:
        return None
    except OSError as exception:
        raise TimestampReadRetryableError(
            f'could not stat XML timestamp source {xml_path}: {exception}'
        ) from exception

    raw_start = None
    try:
        for _, element in parser(xml_path, events=('start',)):
            if element.tag.rsplit('}', 1)[-1] == 'BililiveRecorderRecordInfo':
                value = element.get('start_time')
                raw_start = value if isinstance(value, str) and value.strip() else None
                break
    except ElementTree.ParseError:
        raw_start = None
    except OSError as exception:
        raise TimestampReadRetryableError(
            f'could not read XML timestamp source {xml_path}: {exception}'
        ) from exception

    try:
        after = statter(xml_path)
    except OSError as exception:
        raise TimestampReadRetryableError(
            f'could not re-stat XML timestamp source {xml_path}: {exception}'
        ) from exception
    if (before.st_size, before.st_mtime_ns) != (
        after.st_size, after.st_mtime_ns
    ):
        raise TimestampReadRetryableError(
            f'XML timestamp source changed during read: {xml_path}'
        )
    return raw_start
```

The implementation must not iterate after finding the record-info start tag
and must not read `<d>`, `<sc>`, `<gift>`, or `<guard>` records.

- [ ] **Step 4: Run resolver/XML tests**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_timestamps.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit XML metadata reading**

```shell
git add recorder/bililive/timestamps.py tests/test_bililive_timestamps.py
git commit -m "feat: read stable Bililive XML timestamps"
```

### Task 3: Integrate Resolution Into Media Inspection

**Files:**
- Modify: `recorder/bililive/media.py`
- Modify: `tests/test_bililive_media.py`
- Test: `tests/test_bililive_timestamps.py`

- [ ] **Step 1: Write failing media integration tests**

Add tests proving real tag casing/title behavior, XML agreement, conflict
rejection, XML-only fallback, and retry conversion:

```python
def test_inspect_media_reconciles_real_ffprobe_and_xml_metadata(tmp_path):
    path = tmp_path / 'wrong-name.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T20:31:59.1494083+09:00"/></i>',
        encoding='utf8',
    )
    result = _probe_result(tags={
        'StartTime': '2026-07-27T11:31:59.154000Z',
        'Title': 'fallback title',
        'StreamTitle': '56冠神抽',
    })

    inspected = inspect_media(path, runner=lambda *args, **kwargs: result)

    assert inspected.start_time.isoformat() == (
        '2026-07-27T19:31:59.154000+08:00'
    )
    assert inspected.stream_title == '56冠神抽'
    assert inspected.probe_error is None


def test_inspect_media_rejects_ffprobe_xml_timestamp_conflict(tmp_path):
    path = tmp_path / '2026-07-27 19:31:59.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T20:32:10+09:00"/></i>',
        encoding='utf8',
    )

    inspected = inspect_media(
        path,
        runner=lambda *args, **kwargs: _probe_result(
            tags={'StartTime': '2026-07-27T11:31:59Z'}
        ),
    )

    assert 'conflicting start times' in inspected.probe_error
    assert classify_session_files([inspected])[inspected.fingerprint].status == (
        'ignored_invalid'
    )


def test_inspect_media_uses_xml_when_ffprobe_start_tag_is_missing(tmp_path):
    path = tmp_path / 'unknown.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T20:31:59+09:00"/></i>',
        encoding='utf8',
    )

    inspected = inspect_media(
        path, runner=lambda *args, **kwargs: _probe_result(tags={})
    )

    assert inspected.start_time.isoformat() == '2026-07-27T19:31:59+08:00'
    assert inspected.probe_error is None
```

Use an injected `xml_start_reader` that raises
`TimestampReadRetryableError('changed')` and assert `inspect_media` raises
`MediaProbeRetryableError('changed')` rather than classifying the file:

```python
from recorder.bililive.timestamps import TimestampReadRetryableError


def test_inspect_media_retries_when_xml_changes(tmp_path):
    path = tmp_path / '2026-07-27 19:31:59.flv'
    path.write_bytes(b'video')

    def changed_xml(xml_path):
        raise TimestampReadRetryableError(f'changed: {xml_path}')

    with pytest.raises(MediaProbeRetryableError, match='changed'):
        inspect_media(
            path,
            runner=lambda *args, **kwargs: _probe_result(),
            xml_start_reader=changed_xml,
        )
```

- [ ] **Step 2: Run media tests and verify failures**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_media.py -q
```

Expected: new reconciliation, title, conflict, and retry tests fail.

- [ ] **Step 3: Replace the old local start-time helpers**

In `media.py`:

1. Remove `_FILENAME_TIMESTAMP`, `_filename_start_time`, and `_start_time`.
2. Import `normalized_tags`, `read_xml_start_time`, `resolve_start_time`, and
   `TimestampReadRetryableError`.
3. Add `xml_start_reader=read_xml_start_time` to `inspect_media`.
4. After ffprobe payload validation, call `xml_start_reader(path.with_suffix('.xml'))`.
5. Convert `TimestampReadRetryableError` to `MediaProbeRetryableError` with the
   source path in the message.
6. Call `resolve_start_time(path, tags, xml_raw_start, before.st_mtime_ns)` and
   combine `resolution.error` into `probe_error` before duration/stream checks.
7. Use `normalized_tags(tags)` for case-insensitive lookup; select a nonempty
   `streamtitle` first and `title` second.

The existing fingerprint continues to include the resolved Asia/Shanghai
`start_time`. Do not add fields to `MediaInfo` or the JSONL journal.

- [ ] **Step 4: Run media and timestamp tests**

Run:

```shell
.venv/bin/python -m pytest \
  tests/test_bililive_timestamps.py \
  tests/test_bililive_media.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit media integration**

```shell
git add recorder/bililive/media.py tests/test_bililive_media.py
git commit -m "feat: reconcile Bililive media timestamps"
```

### Task 4: Guarantee UTC+8 YouTube Title Time

**Files:**
- Modify: `recorder/bililive/runner.py`
- Modify: `tests/test_bililive_runner.py`

- [ ] **Step 1: Write a failing runner contract test**

Use the existing `ready_media`, `RecordingJournal`, `FakePublisher`, and
`publish_result` helpers:

```python
from zoneinfo import ZoneInfo


@pytest.mark.parametrize(
    'start',
    [
        datetime(2026, 7, 27, 20, 31, 59, tzinfo=ZoneInfo('Asia/Tokyo')),
        datetime(2026, 7, 27, 11, 31, 59, tzinfo=timezone.utc),
    ],
)
def test_runner_formats_youtube_start_in_shanghai(tmp_path, start):
    journal = RecordingJournal(tmp_path / 'state.jsonl')
    classified = ready_media(tmp_path, start=start)
    append_ready(journal, classified)
    publisher = FakePublisher([publish_result()])
    runner = BililivePublishRunner(
        journal=journal,
        publisher=publisher,
        room_id=ROOM_ID,
        state_dir=tmp_path / 'state',
    )

    result = runner.publish_one(classified, caption_provider=None)

    assert result.status == 'complete'
    assert publisher.calls[0]['start'] == '2026-07-27 19:31:59'
```

- [ ] **Step 2: Run the runner tests and verify timezone failures**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_runner.py -q
```

Expected: the new assertions receive `20:31:59` or `11:31:59` rather than the
required `19:31:59`.

- [ ] **Step 3: Normalize immediately before publication**

In `runner.py`, add an explicit `ZoneInfo('Asia/Shanghai')` constant and helper:

```python
YOUTUBE_TIMEZONE = ZoneInfo('Asia/Shanghai')


def _youtube_wall_time(value):
    instant = _aware_datetime(value)
    return instant.astimezone(YOUTUBE_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
```

Replace the direct `media.start_time.strftime` publisher argument with
`_youtube_wall_time(media.start_time)`. Do not use `datetime.now()`, `TZ`, or
the host's local timezone.

- [ ] **Step 4: Run runner and publishing tests**

Run:

```shell
.venv/bin/python -m pytest \
  tests/test_bililive_runner.py \
  tests/test_youtube_publishing.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit the YouTube formatting contract**

```shell
git add recorder/bililive/runner.py tests/test_bililive_runner.py
git commit -m "fix: format Bililive YouTube times in UTC+8"
```

### Task 5: Final Regression and Real-Metadata Verification

**Files:**
- Test: `tests/test_bililive_timestamps.py`
- Test: `tests/test_bililive_media.py`
- Test: `tests/test_bililive_runner.py`
- Test: `tests/test_bililive_pipeline_integration.py`

- [ ] **Step 1: Run all Bililive and YouTube-focused tests**

```shell
.venv/bin/python -m pytest \
  tests/test_youtube.py \
  tests/test_youtube_publishing.py \
  tests/test_bililive_xml.py \
  tests/test_bililive_journal.py \
  tests/test_bililive_media.py \
  tests/test_bililive_timestamps.py \
  tests/test_bililive_monitor.py \
  tests/test_bililive_runner.py \
  tests/test_bililive_service.py \
  tests/test_bililive_cleanup.py \
  tests/test_bililive_directory_monitor.py \
  tests/test_bililive_pipeline_integration.py -q
```

Expected: zero failures.

- [ ] **Step 2: Run static and source-mutation checks**

```shell
.venv/bin/python -m compileall -q recorder tests
git diff --check
rg -n "datetime\.now\(\)\.astimezone|astimezone\(\)" \
  recorder/bililive/timestamps.py \
  recorder/bililive/media.py \
  recorder/bililive/runner.py
```

Expected: compilation and diff checks pass. The timezone search must not find
timestamp-resolution or YouTube-title logic that depends on the current clock
or local process timezone.

- [ ] **Step 3: Run the full repository suite**

```shell
.venv/bin/python -m pytest -q
```

Expected: the Bililive-focused tests pass. If the known Huya live-network tests
or Panda missing-config test fail, record their exact names and do not describe
the complete repository suite as passing.

- [ ] **Step 4: Perform one read-only real-metadata check**

Run `inspect_media` against only one already-settled segment and print its
resolved ISO timestamp and title. Do not generate media, modify the FLV/XML, or
probe multiple production files:

```shell
.venv/bin/python -c "from recorder.bililive.media import inspect_media; m=inspect_media('/mnt/oracle-tokyo-01/data/BililiveRecorder/1829181560/2026-07-27 19:31:59.flv'); print(f'start_time={m.start_time.isoformat()}'); print(f'stream_title={m.stream_title}'); print(f'probe_error={m.probe_error}')"
```

For the observed sample, expect:

```text
start_time=2026-07-27T19:31:59.154000+08:00
stream_title=56冠神抽
probe_error=None
```

- [ ] **Step 5: Commit any test-only corrections**

Only when the preceding verification required a test correction:

```shell
git add tests/test_bililive_timestamps.py tests/test_bililive_media.py \
  tests/test_bililive_runner.py tests/test_bililive_pipeline_integration.py
git commit -m "test: verify Bililive timestamp compatibility"
```
