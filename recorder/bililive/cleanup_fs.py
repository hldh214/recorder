import ctypes
import os
import stat
from contextlib import contextmanager
from pathlib import Path


QUARANTINE_DIRECTORY = '.bililive-cleanup-quarantine'
_RENAME_NOREPLACE = 1
_LIBC = ctypes.CDLL(None, use_errno=True)
_RENAMEAT2 = getattr(_LIBC, 'renameat2', None)
if _RENAMEAT2 is not None:
    _RENAMEAT2.argtypes = (
        ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
        ctypes.c_uint,
    )
    _RENAMEAT2.restype = ctypes.c_int


class UnsafeCleanupPathError(OSError):
    pass


def stat_identity(file_stat):
    return (
        file_stat.st_dev,
        file_stat.st_ino,
        file_stat.st_size,
        file_stat.st_mtime_ns,
    )


def _rename_noreplace(source_fd, source_name, destination_fd, destination_name):
    if _RENAMEAT2 is None:
        raise UnsafeCleanupPathError('renameat2 is unavailable')
    result = _RENAMEAT2(
        source_fd,
        os.fsencode(source_name),
        destination_fd,
        os.fsencode(destination_name),
        _RENAME_NOREPLACE,
    )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(
            error_number,
            os.strerror(error_number),
            destination_name,
        )


class RootDirectory:
    def __init__(self, root):
        self.path = Path(root)
        self.fd = None
        self.quarantine_fd = None

    def __enter__(self):
        flags = (
            os.O_RDONLY
            | getattr(os, 'O_DIRECTORY', 0)
            | getattr(os, 'O_NOFOLLOW', 0)
        )
        root_stat = os.stat(self.path, follow_symlinks=False)
        root_fd = os.open(self.path, flags)
        opened_stat = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_stat.st_mode)
            or not stat.S_ISDIR(opened_stat.st_mode)
            or (root_stat.st_dev, root_stat.st_ino)
            != (opened_stat.st_dev, opened_stat.st_ino)
        ):
            os.close(root_fd)
            raise UnsafeCleanupPathError('cleanup root identity changed')
        self.fd = root_fd
        return self

    def __exit__(self, exception_type, exception, traceback):
        if self.quarantine_fd is not None:
            os.close(self.quarantine_fd)
            self.quarantine_fd = None
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def _relative_parts(self, path):
        candidate = Path(os.path.abspath(os.path.normpath(path)))
        try:
            relative = candidate.relative_to(self.path)
        except ValueError as exception:
            raise UnsafeCleanupPathError('cleanup path is outside root') from exception
        if not relative.parts:
            raise UnsafeCleanupPathError('cleanup path cannot be root')
        if any(part in ('', '.', '..') for part in relative.parts):
            raise UnsafeCleanupPathError('cleanup path is not normalized')
        return relative.parts

    @contextmanager
    def parent(self, path):
        parts = self._relative_parts(path)
        current_fd = os.dup(self.fd)
        flags = (
            os.O_RDONLY
            | getattr(os, 'O_DIRECTORY', 0)
            | getattr(os, 'O_NOFOLLOW', 0)
        )
        try:
            for part in parts[:-1]:
                next_fd = os.open(part, flags, dir_fd=current_fd)
                os.close(current_fd)
                current_fd = next_fd
            yield current_fd, parts[-1]
        except FileNotFoundError:
            raise
        except OSError as exception:
            raise UnsafeCleanupPathError(str(exception)) from exception
        finally:
            os.close(current_fd)

    def lstat(self, path):
        try:
            with self.parent(path) as (parent_fd, name):
                return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None

    def _open_quarantine(self, create):
        if self.quarantine_fd is not None:
            return self.quarantine_fd
        if create:
            try:
                os.mkdir(QUARANTINE_DIRECTORY, mode=0o700, dir_fd=self.fd)
                os.fsync(self.fd)
            except FileExistsError:
                pass
        flags = (
            os.O_RDONLY
            | getattr(os, 'O_DIRECTORY', 0)
            | getattr(os, 'O_NOFOLLOW', 0)
        )
        try:
            quarantine_fd = os.open(
                QUARANTINE_DIRECTORY, flags, dir_fd=self.fd
            )
        except FileNotFoundError:
            if not create:
                return None
            raise
        quarantine_stat = os.fstat(quarantine_fd)
        if (
            not stat.S_ISDIR(quarantine_stat.st_mode)
            or stat.S_IMODE(quarantine_stat.st_mode) != 0o700
            or quarantine_stat.st_dev != os.fstat(self.fd).st_dev
            or quarantine_stat.st_uid != os.geteuid()
        ):
            os.close(quarantine_fd)
            raise UnsafeCleanupPathError('unsafe cleanup quarantine directory')
        self.quarantine_fd = quarantine_fd
        return quarantine_fd

    def ensure_quarantine(self):
        return self._open_quarantine(create=True)

    @staticmethod
    def _validate_source_stat(file_stat, expected):
        if (
            not stat.S_ISREG(file_stat.st_mode)
            or file_stat.st_nlink != 1
            or stat_identity(file_stat) != expected
        ):
            raise UnsafeCleanupPathError('cleanup source identity changed')

    def quarantine_stat(self, quarantine_path, create=True):
        parts = Path(quarantine_path).parts
        if len(parts) != 2 or parts[0] != QUARANTINE_DIRECTORY:
            raise UnsafeCleanupPathError('invalid quarantine path')
        quarantine_fd = self._open_quarantine(create=create)
        if quarantine_fd is None:
            return None
        try:
            return os.stat(
                parts[1], dir_fd=quarantine_fd, follow_symlinks=False
            )
        except FileNotFoundError:
            return None

    def sync_intent_directories(self, original_path, recovery_path=None):
        quarantine_fd = self.ensure_quarantine()
        synced = set()

        def sync_parent(path):
            with self.parent(path) as (parent_fd, _):
                parent_stat = os.fstat(parent_fd)
                identity = (parent_stat.st_dev, parent_stat.st_ino)
                if identity not in synced:
                    os.fsync(parent_fd)
                    synced.add(identity)

        sync_parent(original_path)
        if recovery_path is not None:
            sync_parent(recovery_path)
        os.fsync(quarantine_fd)

    def rename_to_quarantine(self, original_path, quarantine_path, expected):
        quarantine_parts = Path(quarantine_path).parts
        if (
            len(quarantine_parts) != 2
            or quarantine_parts[0] != QUARANTINE_DIRECTORY
        ):
            raise UnsafeCleanupPathError('invalid quarantine path')
        quarantine_fd = self.ensure_quarantine()
        with self.parent(original_path) as (source_fd, source_name):
            source_stat = os.stat(
                source_name, dir_fd=source_fd, follow_symlinks=False
            )
            self._validate_source_stat(source_stat, expected)
            _rename_noreplace(
                source_fd,
                source_name,
                quarantine_fd,
                quarantine_parts[1],
            )
            os.fsync(source_fd)
            os.fsync(quarantine_fd)
        quarantined_stat = os.stat(
            quarantine_parts[1],
            dir_fd=quarantine_fd,
            follow_symlinks=False,
        )
        self._validate_source_stat(quarantined_stat, expected)

    def unlink_quarantine(self, quarantine_path, expected):
        parts = Path(quarantine_path).parts
        if len(parts) != 2 or parts[0] != QUARANTINE_DIRECTORY:
            raise UnsafeCleanupPathError('invalid quarantine path')
        quarantine_fd = self.ensure_quarantine()
        quarantined_stat = os.stat(
            parts[1], dir_fd=quarantine_fd, follow_symlinks=False
        )
        self._validate_source_stat(quarantined_stat, expected)
        os.unlink(parts[1], dir_fd=quarantine_fd)
        os.fsync(quarantine_fd)

    def move_quarantine_to_original(self, quarantine_path, original_path):
        quarantine_fd = self.ensure_quarantine()
        quarantine_name = Path(quarantine_path).name
        with self.parent(original_path) as (parent_fd, original_name):
            _rename_noreplace(
                quarantine_fd, quarantine_name, parent_fd, original_name
            )
            os.fsync(quarantine_fd)
            os.fsync(parent_fd)

    def move_quarantine_to_recovery(
        self, quarantine_path, original_path, recovery_name
    ):
        quarantine_fd = self.ensure_quarantine()
        quarantine_name = Path(quarantine_path).name
        with self.parent(original_path) as (parent_fd, _):
            _rename_noreplace(
                quarantine_fd, quarantine_name, parent_fd, recovery_name
            )
            os.fsync(quarantine_fd)
            os.fsync(parent_fd)
