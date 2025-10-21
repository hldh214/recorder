import re
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import os


PATTERN = re.compile(r"^blive_(\d+)_(\d{4}-\d{2}-\d{2})-(\d{6})\.(\w+)$")

# Resolve destination root from config.toml: app.video_path + /record/bilibili
try:
    from recorder import config as _app_config
    _video_root = _app_config.get('app', {}).get('video_path')
    if not _video_root:
        raise KeyError('app.video_path not set in config')
    TARGET_ROOT = Path(_video_root) / "record" / "bilibili"
except Exception:
    # Fallback to previous default for robustness
    TARGET_ROOT = Path("/mnt/ssd-4t/data/videos") / "record" / "bilibili"


def parse_filename(name: str):
    """
    Parse filename like: blive_{roomid}_{YYYY-MM-DD}-{HHMMSS}.{ext}
    Returns (roomid: str, naive_dt: datetime, ext: str)
    The naive_dt represents the timestamp encoded in the filename (East-9 time).
    """
    m = PATTERN.match(name)
    if not m:
        raise ValueError(
            f"Invalid filename format: {name}. Expected blive_{{roomid}}_YYYY-MM-DD-HHMMSS.ext"
        )
    roomid, date_part, time_part, ext = m.groups()
    # time_part is HHMMSS
    hh = int(time_part[0:2])
    mm = int(time_part[2:4])
    ss = int(time_part[4:6])
    naive_dt = datetime.strptime(f"{date_part} {hh:02d}:{mm:02d}:{ss:02d}", "%Y-%m-%d %H:%M:%S")
    return roomid, naive_dt, ext


def adjust_dt_for_local_tz(dt: datetime) -> datetime:
    """Adjust the timestamp in filename from the machine's local timezone to Beijing time (UTC+8).

    General rule:
    - Detect current machine local UTC offset (including half-hour zones).
    - Compute delta = UTC+8 offset − local offset.
    - Return dt shifted by delta, preserving minutes/seconds and handling date rollovers.
    """
    try:
        offset = datetime.now().astimezone().utcoffset()
        local_seconds = int(offset.total_seconds()) if offset is not None else 0
    except Exception:
        # If detection fails, assume local is UTC (0)
        local_seconds = 0

    target_seconds = 8 * 3600  # Beijing time UTC+8
    delta_seconds = target_seconds - local_seconds
    return dt + timedelta(seconds=delta_seconds)


def build_target_path(roomid: str, beijing_dt: datetime) -> Path:
    # Always use .mp4 extension as required
    filename = f"{beijing_dt.strftime('%Y-%m-%d %H:%M:%S')}.mp4"
    return TARGET_ROOT / roomid / filename


def copy_with_mtime(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Use copy2 to preserve metadata including mtime
    shutil.copy2(src, dst)
    # Ensure mtime equals source exactly (double-ensure)
    src_stat = src.stat()
    os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print("Usage: python -m recorder.utils.blrec <absolute_path_to_file>")
        return 2

    input_path = Path(argv[0])
    if not input_path.is_absolute():
        print(f"Error: path must be absolute: {input_path}")
        return 2
    if not input_path.exists():
        print(f"Error: file not found: {input_path}")
        return 2

    try:
        roomid, naive_dt, _ext = parse_filename(input_path.name)
    except Exception as e:
        print(f"Error: {e}")
        return 2

    beijing_dt = adjust_dt_for_local_tz(naive_dt)
    target_path = build_target_path(roomid, beijing_dt)

    try:
        copy_with_mtime(input_path, target_path)
    except Exception as e:
        print(f"Copy failed: {e}")
        return 1

    print(str(target_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
