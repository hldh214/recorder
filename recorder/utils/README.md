## Utils

### huya_replay

Guess huya official replay url.

### df_check

Check the disk space.

### rclone_moveto

Move the files to the remote server.

### blrec(Deprecated)

A simple tool to record the live stream of Bilibili.
Credits to [blrec](https://github.com/acgnhiki/blrec) for the idea and some code.

### BililiveRecorder

A simple tool to record the live stream of Bilibili.
Credits to [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) for the idea and some code.

### BililiveRecorder directory publisher

BililiveRecorder must have `RecordDanmaku` enabled so every FLV can be paired
with its same-stem XML danmaku file.

```shell
# Dry run and initial baseline inspection
pipenv run python -m recorder.utils.bililive_directory_monitor run \
  /data/BililiveRecorder \
  --room-id=12345 \
  --api-url=http://127.0.0.1:2356 \
  --dry-run

# Supervisor command
pipenv run python -u -m recorder.utils.bililive_directory_monitor run \
  /data/BililiveRecorder \
  --room-id=12345 \
  --api-url=http://127.0.0.1:2356
```

The first active/current session is baseline-only; publication starts with the
next complete session after the directory has settled. By default publication
waits for the room to go offline. Set both `youtube.upload_while_live = true`
and a positive `youtube.upload_rate_mib_per_second` to publish a rotated FLV
while the room remains live. A native FLV is eligible once it is no longer the
newest file and has remained unchanged for 30 minutes. The same quiet period
applies to a closed HLS segment, even if it is the newest file. The rate applies
to YouTube video media uploads created from the `[youtube]` configuration; other network traffic is
not limited. Publication reads FLV/XML files in place and never moves them. The
JSONL state file under `var/bililive/<room-id>/state.jsonl` is durable
application state and must not be log-rotated. Keep the old cleanup cron enabled
until the new cleanup decisions have been reviewed in dry-run output; do not run
both cleanup paths after cutover.

### BililiveRecorder HLS fallback

The fallback monitors the BililiveRecorder room API and tries original-quality
HLS when the room is live and native FLV output stops growing. It collects
danmaku and hands closed FLVs and their matching XML files to the directory
publisher. Both the staging directory and room directory must be on the same
filesystem for the handoff to work.

Initialize the Git submodules and install `ffmpeg` and `ffprobe`. Use the
BililiveRecorder data root containing `config.json` and the room directory.
The fallback reads the Bilibili cookie from that local config file.

```shell
git submodule update --init --recursive
pipenv run python -u -m recorder.utils.bililive_hls \
  --root /path/to/BililiveRecorder \
  --room-id 12345 \
  --api-url http://127.0.0.1:2356 \
  --segment-seconds 25200
```

The optional `--segment-seconds` defaults to 10800 (3 hours). The example uses
25200 (7 hours). FFmpeg cuts on a keyframe, and an interrupted stream can
produce shorter segments. Use the [example systemd unit](../../deploy/bililive-hls.service.example)
for unattended operation. Adapt its paths and service user locally and set
`RECORDING_ROOT`, `ROOM_ID`, `ROOM_API_URL`, and `SEGMENT_SECONDS` in
`/etc/recorder/bililive-hls.env`.

### Fixed Mongo backfill queue

`bililive_mongo_backfill` is an operator-maintained recovery queue for selected
BililiveRecorder FLVs. Its file list is intentionally defined as module-level
constants. It reads each FLV in place, generates VTT captions and highlights
from MongoDB, and records every YouTube publication stage in a separate JSONL
journal. It never copies, moves, or deletes source recordings.

```shell
pipenv run python -u -m recorder.utils.bililive_mongo_backfill run
```

State is stored under
`var/bililive-mongo-backfill/<room-id>/state.jsonl`. Do not run more than one
copy; the process lock rejects overlapping workers.
