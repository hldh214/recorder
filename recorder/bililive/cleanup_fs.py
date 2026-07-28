import os
import stat
from contextlib import contextmanager
from pathlib import Path


class UnsafeCleanupPathError(OSError):
    pass


def stat_identity(file_stat):
    return (
        file_stat.st_dev,
        file_stat.st_ino,
        file_stat.st_size,
        file_stat.st_mtime_ns,
    )


class RootDirectory:
    def __init__(self, root):
        self.path = Path(root)
        self.fd = None

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
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def _relative_parts(self, path):
        candidate = Path(os.path.abspath(os.path.normpath(path)))
        try:
            relative = candidate.relative_to(self.path)
        except ValueError as exception:
            raise UnsafeCleanupPathError(
                'cleanup path is outside root'
            ) from exception
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
            try:
                for part in parts[:-1]:
                    next_fd = os.open(part, flags, dir_fd=current_fd)
                    os.close(current_fd)
                    current_fd = next_fd
            except OSError as exception:
                raise UnsafeCleanupPathError(str(exception)) from exception
            yield current_fd, parts[-1]
        finally:
            os.close(current_fd)

    def unlink_source(self, path, expected_identity):
        try:
            with self.parent(path) as (parent_fd, name):
                try:
                    file_stat = os.stat(
                        name, dir_fd=parent_fd, follow_symlinks=False
                    )
                except FileNotFoundError:
                    return False
                if (
                    not stat.S_ISREG(file_stat.st_mode)
                    or file_stat.st_nlink != 1
                    or stat_identity(file_stat) != expected_identity
                ):
                    return False
                try:
                    os.unlink(name, dir_fd=parent_fd)
                except FileNotFoundError:
                    return False
                os.fsync(parent_fd)
                return True
        except UnsafeCleanupPathError:
            return False
