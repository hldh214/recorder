import logging
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import os
import json
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer

from tqdm import tqdm
import fire
from recorder import ffmpeg

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

PATTERN = re.compile(r"^blive_(\d+)_(\d{4}-\d{2}-\d{2})-(\d{6})\.(\w+)$")

# Resolve destination root from config.toml: app.video_path + /record/bilibili
from recorder import config as _app_config

_video_root = _app_config.get('app', {}).get('video_path')
if not _video_root:
    raise KeyError('app.video_path not set in config')
TARGET_ROOT = Path(_video_root) / "record" / "bilibili"
UPLOAD_ROOT = Path(_video_root) / "upload" / "bilibili"


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
    """Adjust the timestamp in the filename from the machine's local timezone to Beijing time (UTC+8).

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


def build_target_path(roomid: str, beijing_dt: datetime, tgt=TARGET_ROOT) -> Path:
    # Always use .mp4 extension as required
    filename = f"{beijing_dt.strftime('%Y-%m-%d %H:%M:%S')}.mp4"
    return tgt / roomid / filename


def copy_or_move(src: Path, dst: Path, upload=False):
    dst.parent.mkdir(parents=True, exist_ok=True)
    src_stat = src.stat()

    if upload:
        # move
        shutil.move(str(src), str(dst))
    else:
        # copy with mtime
        total = src_stat.st_size
        buf_size = 16 * 1024 * 1024  # 16MB buffers for high throughput

        desc = f"Copying {src.name}"
        with (open(src, 'rb') as f_src,
              open(dst, 'wb') as f_dst,
              tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, desc=desc) as pbar):
            while True:
                chunk = f_src.read(buf_size)
                if not chunk:
                    break
                f_dst.write(chunk)
                pbar.update(len(chunk))

        # Preserve mtime exactly (as per requirement)
        os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))


def read_room_title(xml_path: Path) -> str | None:
    """Read room_title from a blrec XML file. Returns None if not available.
    Expected structure:
    <i>
      <metadata>
        <room_title>...</room_title>
      </metadata>
    </i>
    """
    try:
        if not xml_path.exists():
            return None
        tree = ET.parse(xml_path)
        root = tree.getroot()
        meta = root.find('metadata')
        if meta is None:
            return None
        rt = meta.findtext('room_title')
        if rt is None:
            return None
        # Strip whitespace
        return rt.strip()
    except Exception:
        # Be permissive: on any parsing error, just skip metadata
        return None


def copy(input_path: str, upload=False) -> str:
    """
    Copy or move (if upload=True) a blrec output file into the project's record/bilibili folder.
    Returns the destination absolute path as a string.
    """
    input_path_p = Path(input_path)
    if not input_path_p.is_absolute():
        raise ValueError(f"path must be absolute: {input_path}")
    if not input_path_p.exists():
        raise FileNotFoundError(f"file not found: {input_path}")

    # ext not used for now, but may be useful later
    roomid, naive_dt, _ext = parse_filename(input_path_p.name)

    # Read room_title from the sibling XML if available
    xml_path = input_path_p.with_suffix('.xml')
    room_title = read_room_title(xml_path)

    beijing_dt = adjust_dt_for_local_tz(naive_dt)
    target_path_record = build_target_path(roomid, beijing_dt)
    target_path = target_path_record
    if upload:
        target_path = build_target_path(roomid, beijing_dt, UPLOAD_ROOT)

    copy_or_move(input_path_p, target_path, upload)

    # After copy, write a metadata file with only the title (if available)
    if room_title:
        try:
            metadata_path = target_path_record.with_suffix('.metadata')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({"title": room_title}, f, ensure_ascii=False)
        except Exception:
            # Best-effort only
            pass

    return str(target_path)


def _move_to_upload(copied_path: Path):
    roomid = copied_path.parent.name
    dst_dir = UPLOAD_ROOT / roomid
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_file = dst_dir / copied_path.name

    # Move video
    shutil.move(str(copied_path), str(dst_file))

    return dst_file


class _WebhookHandler(BaseHTTPRequestHandler):
    # Reference to the outer module's functions
    def _send(self, code=200, body: dict | str = "ok"):
        body_bytes = (json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else str(body)).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_POST(self):  # noqa: N802 (http.server naming)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(length) if length > 0 else b''
            data = json.loads(raw.decode('utf-8') or '{}')
        except Exception as e:
            return self._send(400, {"error": f"invalid json: {e}"})

        logging.info(f"blrec webhook: {data}")
        if data.get('type') != 'VideoPostprocessingCompletedEvent':
            return self._send(200, "ok")

        video_path = (data.get('data') or {}).get('path')
        if not video_path:
            return self._send(400, {"error": "missing data.path"})

        try:
            copied = Path(copy(str(video_path)))
        except Exception as e:
            return self._send(500, {"error": f"copy failed: {e}"})

        logging.info(f"blrec webhook: copied {video_path} -> {copied}")

        # Check validity via ffprobe
        try:
            if ffmpeg.valid(str(copied)):
                moved_to = _move_to_upload(copied)
                logging.info(f"blrec webhook: uploaded {copied} -> {moved_to}")
                return self._send(200, {"status": "uploaded", "path": str(moved_to)})
            else:
                return self._send(202, {"status": "invalid", "path": str(copied)})
        except Exception as e:
            return self._send(500, {"error": f"ffprobe/move error: {e}"})

    def log_message(self, _format: str, *args) -> None:  # silence default logging
        try:
            sys.stderr.write("blrec serve: " + (_format % args) + "\n")
        except Exception:
            pass


def serve(port: int = 10064):
    """Start a simple HTTP server to receive blrec webhooks (POST /)."""
    server = HTTPServer(("0.0.0.0", int(port)), _WebhookHandler)
    print(f"[blrec] webhook listening on http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main():
    class CLI:
        def copy(self, path: str) -> str:
            """Copy a blrec file to the record folder. Returns destination path."""
            return copy(path)

        def serve(self, port: int = 10064):
            """Run webhook HTTP server on given port (default 10064)."""
            serve(port)

    # Assume Fire is installed; no backward compatibility needed
    fire.Fire(CLI)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
