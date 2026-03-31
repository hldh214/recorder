import logging
import sys
import shutil
import time
from pathlib import Path
from datetime import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import fire

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Minimum file size (in bytes) for a recording to be considered valid for processing.
# NOTE: This threshold was intentionally lowered from 64 MB to 32 MB to allow
# shorter, but still complete, recordings to be picked up while still filtering
# out tiny/partial files that BililiveRecorder can create during interruptions.
MIN_FILE_SIZE = 32 * 1024 * 1024  # 32 MB

# Resolve destination root from config.toml: app.video_path + /upload/bilibili
from recorder import config as _app_config

_video_root = _app_config.get("app", {}).get("video_path")
if not _video_root:
    raise KeyError("app.video_path not set in config")
UPLOAD_ROOT = Path(_video_root) / "upload" / "bilibili"


def parse_rel_path(rel_path: str):
    """
    Parse BililiveRecorder RelativePath to extract room_id and start datetime.

    Expected RelativePath format: "{roomId}/{yyyy-MM-dd HH:mm:ss}.flv"
    e.g. "23058/2021-05-14 17:52:50.flv"

    The datetime in the filename is already GMT+8, no timezone conversion needed.

    Returns (room_id: str, start_dt: datetime)
    """
    p = Path(rel_path)
    room_id = p.parent.name
    if not room_id:
        raise ValueError(f"Cannot extract room_id from RelativePath: {rel_path}")

    stem = p.stem  # e.g. "2021-05-14 17:52:50"
    try:
        start_dt = datetime.strptime(stem, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(
            f"Cannot parse datetime from filename: {p.name}. "
            f"Expected format: YYYY-MM-DD HH:MM:SS.ext"
        )

    return room_id, start_dt


def build_upload_path(room_id: str, start_dt: datetime) -> Path:
    """Build the upload destination path. Always uses .mp4 extension."""
    filename = f"{start_dt.strftime('%Y-%m-%d %H:%M:%S')}.mp4"
    return UPLOAD_ROOT / room_id / filename


def _wait_file_stable(path: Path, interval: float = 2.0, checks: int = 3) -> bool:
    """
    Wait until a file's size stabilises (not being written to).
    Returns True if file exists and is stable, False otherwise.
    """
    if not path.exists():
        return False
    prev_size = -1
    stable_count = 0
    for _ in range(checks * 3):  # max iterations to avoid infinite loop
        try:
            cur_size = path.stat().st_size
        except OSError:
            return False
        if cur_size == prev_size:
            stable_count += 1
            if stable_count >= checks:
                return True
        else:
            stable_count = 0
        prev_size = cur_size
        time.sleep(interval)
    return False


def process_file(
    abs_path: Path, rec_dir: Path, execute: bool = True
) -> tuple[str, Path | None]:
    """
    Validate, parse, and (optionally) move a single recording file to the upload directory.

    Args:
        abs_path: Absolute path to the recording file.
        rec_dir: BililiveRecorder working directory (used to compute RelativePath).
        execute: If True, actually move the file. If False, dry-run only.

    Returns:
        (status: str, dst: Path | None)
        status is one of: "moved", "dry-run", "skipped:...", "error:..."
    """
    if not abs_path.exists():
        return f"error: file not found: {abs_path}", None

    # Check file size
    try:
        file_size = abs_path.stat().st_size
        if file_size < MIN_FILE_SIZE:
            return f"skipped: file too small ({file_size} bytes)", None
    except OSError as e:
        return f"error: stat failed: {e}", None

    # File stability check
    if not _wait_file_stable(abs_path):
        return f"error: file not stable: {abs_path}", None

    # Parse room_id and datetime from relative path
    try:
        rel_path = str(abs_path.relative_to(rec_dir))
    except ValueError:
        return f"error: {abs_path} is not under {rec_dir}", None

    try:
        room_id, start_dt = parse_rel_path(rel_path)
    except ValueError as e:
        return f"error: {e}", None

    dst = build_upload_path(room_id, start_dt)

    if not execute:
        return "dry-run", dst

    # Move
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(abs_path), str(dst))
    except Exception as e:
        return f"error: move failed: {e}", None

    return "moved", dst


# ---------------------------------------------------------------------------
# Webhook server
# ---------------------------------------------------------------------------


class _WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for BililiveRecorder Webhook v2."""

    rec_dir: Path = Path(".")
    processed_events: set = set()

    def _send(self, code=200, body: dict | str = "ok"):
        body_bytes = (
            json.dumps(body, ensure_ascii=False)
            if isinstance(body, dict)
            else str(body)
        ).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_POST(self):  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b""
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception as e:
            return self._send(400, {"error": f"invalid json: {e}"})

        event_type = data.get("EventType", "")
        event_id = data.get("EventId", "")
        event_data = data.get("EventData") or {}

        logging.info(
            f"BililiveRecorder webhook: EventType={event_type} EventId={event_id}"
        )

        # Deduplicate retried events
        if event_id and event_id in self.__class__.processed_events:
            logging.info(
                f"BililiveRecorder webhook: skipping duplicate EventId={event_id}"
            )
            return self._send(200, {"skipped": "duplicate event"})

        # We only care about FileClosed events.
        # FileClosed means the recorder has finished writing and closed the file handle,
        # so it is safe to move the file at this point.
        # SessionEnded does NOT contain file path info and may arrive BEFORE FileClosed
        # due to async event ordering, so it is not suitable for triggering file moves.
        if event_type != "FileClosed":
            return self._send(200, "ok")

        rel_path = event_data.get("RelativePath", "")
        if not rel_path:
            return self._send(400, {"error": "missing EventData.RelativePath"})

        abs_path = self.__class__.rec_dir / rel_path
        logging.info(f"BililiveRecorder webhook: FileClosed -> {abs_path}")

        status, dst = process_file(abs_path, self.__class__.rec_dir, execute=True)

        if status.startswith("error:"):
            logging.warning(f"BililiveRecorder webhook: {status}")
            return self._send(500, {"error": status})

        if status.startswith("skipped:"):
            logging.info(f"BililiveRecorder webhook: {status}")
            return self._send(200, {"skipped": status})

        # Mark event as processed only on success
        if event_id:
            self.__class__.processed_events.add(event_id)

        logging.info(f"BililiveRecorder webhook: moved {abs_path} -> {dst}")
        return self._send(200, {"moved": str(dst)})

    def log_message(self, _format: str, *args) -> None:
        try:
            sys.stderr.write("BililiveRecorder serve: " + (_format % args) + "\n")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


def serve(rec_dir: str, port: int = 10065):
    """
    Start webhook server for BililiveRecorder.

    Args:
        rec_dir: The BililiveRecorder working/output directory where recordings are stored.
                 RelativePath from webhook events will be resolved relative to this directory.
        port: HTTP port to listen on (default 10065).
    """
    rec_path = Path(rec_dir)
    if not rec_path.is_dir():
        raise ValueError(f"rec_dir is not a directory: {rec_dir}")

    _WebhookHandler.rec_dir = rec_path
    _WebhookHandler.processed_events = set()

    server = HTTPServer(("0.0.0.0", int(port)), _WebhookHandler)
    print(f"[BililiveRecorder] webhook listening on http://0.0.0.0:{port}")
    print(f"[BililiveRecorder] rec_dir={rec_path}")
    print(f"[BililiveRecorder] upload_root={UPLOAD_ROOT}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def batch_move(rec_dir: str, execute: bool = False):
    """
    Scan rec_dir for recording files and move them to the upload directory.

    Scans all {roomId}/{datetime}.flv files under rec_dir that are >= MIN_FILE_SIZE.
    Default mode is dry-run; pass --execute to actually move files.

    Args:
        rec_dir: BililiveRecorder working directory.
        execute: If True, actually move files. Default is dry-run.
    """
    rec_path = Path(rec_dir)
    if not rec_path.is_dir():
        raise ValueError(f"rec_dir is not a directory: {rec_dir}")

    # Scan: rec_dir/{roomId}/{datetime}.flv
    candidates = sorted(rec_path.glob("*/*.flv"))

    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"[batch_move] mode={mode}, rec_dir={rec_path}")
    print(f"[batch_move] upload_root={UPLOAD_ROOT}")
    print(f"[batch_move] found {len(candidates)} .flv file(s)")

    moved_count = 0
    for src in candidates:
        status, dst = process_file(src, rec_path, execute=execute)
        label = "MOVE" if execute else "WOULD MOVE"

        if status in ("moved", "dry-run"):
            print(f"  [{label}] {src} -> {dst}")
            moved_count += 1
        else:
            print(f"  [SKIP] {src} ({status})")

    print(
        f"[batch_move] {moved_count} file(s) {'moved' if execute else 'would be moved'}"
    )
    if not execute and moved_count > 0:
        print("[batch_move] dry-run complete. Pass --execute to perform moves.")


def main():
    class CLI:
        def serve(self, rec_dir: str, port: int = 10065):
            """Run BililiveRecorder webhook HTTP server.

            Args:
                rec_dir: BililiveRecorder working directory (where recordings are saved).
                port: HTTP port (default 10065).
            """
            serve(rec_dir, port)

        def batch_move(self, rec_dir: str, execute: bool = False):
            """Scan and move recording files to upload directory. Dry-run by default.

            Args:
                rec_dir: BililiveRecorder working directory.
                execute: Pass --execute to actually move files.
            """
            batch_move(rec_dir, execute=execute)

    fire.Fire(CLI)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
