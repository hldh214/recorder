# Bililive Timestamp Resolution Design

## Goal

Resolve every settled BililiveRecorder segment to one reliable absolute start
time despite differences between recorder, host, XML, and filename timezones.
The resolved value must align captions and highlights, while the wall-clock time
used in YouTube titles must always be Asia/Shanghai (UTC+8).

## Evidence

The real segment `2026-07-27 19:31:59.flv` contains these equivalent values:

- ffprobe `StartTime`: `2026-07-27T11:31:59.154000Z`
- XML `BililiveRecorderRecordInfo.start_time`:
  `2026-07-27T20:31:59.1494083+09:00`
- filename interpreted in Asia/Shanghai: `2026-07-27T19:31:59+08:00`

The first two differ by less than one second after UTC normalization. ffprobe's
format-level `start_time=0.018` is a media timeline offset, not a wall-clock
recording time, and must never be used as the absolute start time.

## Time Sources

`inspect_media` will delegate start-time selection to a focused resolver. It
will collect candidates from:

1. The ffprobe format tag named `StartTime`, matched case-insensitively.
2. The same-stem XML element `BililiveRecorderRecordInfo` and its `start_time`
   attribute, matched by local XML tag name.
3. A timestamp at the beginning of the FLV filename.
4. File mtime for diagnostics only.

Aware ISO-8601 and RFC-style metadata values are accepted. A legacy naive
`StartTime` is interpreted in Asia/Shanghai; the operating system timezone is
never consulted. Filename parsing accepts `YYYY-MM-DD` followed by a space,
`T`, or underscore, and accepts either colons or hyphens between time fields.
Filename timestamps are always interpreted in Asia/Shanghai.

## Resolution Policy

All reliable metadata candidates are converted to UTC before comparison.

- When ffprobe and XML candidates both exist, their absolute difference must
  be no more than five seconds. The ffprobe candidate is selected when they
  agree. A larger difference is a stable invalid-media error and prevents
  upload.
- When only ffprobe or only XML is valid, that source is selected. A filename
  disagreement is diagnostic only because filenames have no embedded timezone.
- When neither reliable metadata source is valid, a valid filename timestamp
  is selected as the compatibility fallback.
- When no valid source exists, mtime may be displayed in the error message but
  must not become an uploadable start time.

The selected instant is always returned as an aware Asia/Shanghai datetime.
This makes `BililivePublishRunner` pass an explicit UTC+8 wall-clock value to
the YouTube title template regardless of the recorder or deployment timezone.
Caption and highlight generation continue to use the same instant as an epoch,
so timezone representation changes cannot shift their relative timeline.

## XML Safety

Only the XML header is read until `BililiveRecorderRecordInfo` is found; the
timestamp resolver does not scan all danmaku records. XML identity is checked
before and after this read using size and nanosecond mtime. A changed XML is a
retryable condition, allowing the settled-session monitor to observe it again.

A missing XML timestamp or malformed XML header does not invalidate an
otherwise valid ffprobe timestamp. Caption preparation remains responsible for
reporting missing or invalid full XML content.

## Metadata Compatibility

ffprobe format tags are exposed through a case-insensitive lookup. Stream title
selection prefers `StreamTitle`, then `Title`, so current real BililiveRecorder
files and older lowercase test fixtures are supported without depending on tag
casing.

## Diagnostics

A timestamp conflict error records both normalized candidate values, their
original sources, and the absolute difference. Missing-source errors record
which candidates were absent or invalid. Successful resolution may log the
selected source at debug level, but does not add mutable state to the JSONL
journal schema.

## Tests

Unit tests cover:

- equivalent `Z`, `+09:00`, and `+08:00` instants;
- agreement at and conflict beyond the five-second boundary;
- ffprobe-only, XML-only, filename-only, and no-valid-source paths;
- naive legacy metadata interpreted explicitly in Asia/Shanghai;
- filename separator variants;
- case-insensitive `StartTime`, `StreamTitle`, and `Title` tags;
- an XML identity change during header parsing;
- process timezone changes that do not alter the resolved result;
- offsets from daylight-saving regions normalized correctly;
- the real observed metadata combination resolving to
  `2026-07-27T19:31:59.154000+08:00` for YouTube title formatting.

Existing media classification, runner, XML caption, integration, and source
identity tests remain required. No test may batch-probe production recordings;
real-media verification remains limited to one settled segment at a time.
