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
  --room-id=1829181560 \
  --api-url=http://100.87.152.23:2356 \
  --dry-run

# Supervisor command
pipenv run python -u -m recorder.utils.bililive_directory_monitor run \
  /data/BililiveRecorder \
  --room-id=1829181560 \
  --api-url=http://100.87.152.23:2356
```

The first active/current session is baseline-only; publication starts with the
next complete session after the directory has settled. By default publication
waits for the room to go offline. Set both `youtube.upload_while_live = true`
and a positive `youtube.upload_rate_mib_per_second` to publish older, settled
sessions while a new session is live. The rate applies to YouTube video media
uploads created from the `[youtube]` configuration; other network traffic is
not limited. Publication reads FLV/XML files in place and never moves them. The
JSONL state file under `var/bililive/<room-id>/state.jsonl` is durable
application state and must not be log-rotated. Keep the old cleanup cron enabled
until the new cleanup decisions have been reviewed in dry-run output; do not run
both cleanup paths after cutover.

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
