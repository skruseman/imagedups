import os
import my_platform
from pathlib import Path
from datetime import datetime, timezone


class FileTimeInfo:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(path)

        self._stat = self.path.stat()

    # --- raw timestamps (float, seconds since epoch) ---
    @property
    def atime(self):
        return self._stat.st_atime

    @property
    def mtime(self):
        return self._stat.st_mtime

    @property
    def ctime(self):
        return self._stat.st_ctime  # creation time on Windows

    # --- datetime versions ---
    @staticmethod
    def _to_dt(ts):
        return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()

    @property
    def atime_dt(self):
        return self._to_dt(self.atime)

    @property
    def mtime_dt(self):
        return self._to_dt(self.mtime)

    @property
    def ctime_dt(self):
        return self._to_dt(self.ctime)

    # --- derived info ---
    @property
    def age_seconds(self):
        return (datetime.now(timezone.utc) - self._to_dt(self.mtime)).total_seconds()

    @property
    def is_recently_modified(self, seconds=3600):
        return self.age_seconds < seconds

    # --- file system resolution (useful on Windows) ---
    @property
    def timestamp_resolution_ns(self):
        # NTFS typically ~100ns, but Python rounds to system precision
        return os.statvfs(self.path).f_frsize if hasattr(os, "statvfs") else None

    # --- system info ---
    @property
    def system_info(self):
        return {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
        }

    # --- pretty summary ---
    def summary(self):
        return {
            "path": str(self.path),
            "created": self.ctime_dt,
            "modified": self.mtime_dt,
            "accessed": self.atime_dt,
            "age_seconds": self.age_seconds,
        }