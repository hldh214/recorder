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
next complete session after the room is offline and the directory has settled.
Publication reads FLV/XML files in place and never moves them. The JSONL state
file under `var/bililive/<room-id>/state.jsonl` is durable application state and
must not be log-rotated. Keep the old cleanup cron enabled until the new
cleanup decisions have been reviewed in dry-run output; do not run both cleanup
paths after cutover.
