from __future__ import annotations

import os
import platform
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import win32api
import win32file
import pywintypes


@dataclass(frozen=True)
class WindowsFileTimes:
    creation_time: datetime
    access_time: datetime
    write_time: datetime
    change_time: datetime


class WindowsFileInfo:
    """
    Windows-focused file info wrapper with attribute access for:
    - path info
    - drive info
    - host OS info
    - standard Python stat timestamps
    - Windows-native NTFS timestamps, including change_time
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = Path(path).resolve()
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        self._stat = self.path.stat()
        self._native_times = self._read_native_file_times()

    # ---------- basic path ----------
    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def is_file(self) -> bool:
        return self.path.is_file()

    @property
    def is_dir(self) -> bool:
        return self.path.is_dir()

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def parent(self) -> Path:
        return self.path.parent

    @property
    def suffix(self) -> str:
        return self.path.suffix

    @property
    def size_bytes(self) -> int:
        return self._stat.st_size

    # ---------- drive ----------
    @property
    def drive(self) -> str:
        return self.path.drive

    @property
    def drive_id(self) -> str:
        """
        For normal local Windows paths this is typically like 'C:'.
        If you want the volume serial number instead, use volume_serial_number.
        """
        return self.path.drive

    @property
    def volume_path(self) -> str:
        drive = self.drive
        return f"{drive}\\"

    @property
    def volume_serial_number(self) -> Optional[int]:
        try:
            info = win32api.GetVolumeInformation(self.volume_path)
            return info[1]
        except Exception:
            return None

    @property
    def filesystem_name(self) -> Optional[str]:
        try:
            info = win32api.GetVolumeInformation(self.volume_path)
            return info[4]
        except Exception:
            return None

    # ---------- host OS ----------
    @property
    def os_name(self) -> str:
        return platform.system()

    @property
    def os_release(self) -> str:
        return platform.release()

    @property
    def os_version(self) -> str:
        return platform.version()

    @property
    def machine(self) -> str:
        return platform.machine()

    @property
    def hostname(self) -> str:
        return platform.node()

    # ---------- Python stat times ----------
    @staticmethod
    def _ts_to_local_datetime(ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()

    @property
    def atime(self) -> float:
        return self._stat.st_atime

    @property
    def mtime(self) -> float:
        return self._stat.st_mtime

    @property
    def ctime(self) -> float:
        # On Windows this is creation time
        return self._stat.st_ctime

    @property
    def atime_dt(self) -> datetime:
        return self._ts_to_local_datetime(self.atime)

    @property
    def mtime_dt(self) -> datetime:
        return self._ts_to_local_datetime(self.mtime)

    @property
    def ctime_dt(self) -> datetime:
        return self._ts_to_local_datetime(self.ctime)

    # ---------- Windows native file times ----------
    @staticmethod
    def _pywintime_to_local_datetime(value: pywintypes.TimeType) -> datetime:
        # pywin32 returns a pywintypes datetime-like object
        if isinstance(value, datetime):
            dt = value
        else:
            # fallback, usually not needed
            dt = datetime.fromtimestamp(float(value), tz=timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone()

    def _read_native_file_times(self) -> WindowsFileTimes:
        handle = win32file.CreateFile(
            str(self.path),
            0,  # no access needed just to query metadata
            win32file.FILE_SHARE_READ
            | win32file.FILE_SHARE_WRITE
            | win32file.FILE_SHARE_DELETE,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_FLAG_BACKUP_SEMANTICS if self.path.is_dir() else 0,
            None,
        )
        try:
            creation, access, write = win32file.GetFileTime(handle)
            info = win32file.GetFileInformationByHandleEx(
                handle,
                win32file.FileBasicInfo,
            )
        finally:
            handle.Close()

        # info format from pywin32 is a dict-like structure on current builds
        change_raw = info["ChangeTime"]

        return WindowsFileTimes(
            creation_time=self._pywintime_to_local_datetime(creation),
            access_time=self._pywintime_to_local_datetime(access),
            write_time=self._pywintime_to_local_datetime(write),
            change_time=self._pywintime_to_local_datetime(change_raw),
        )

    @property
    def creation_time(self) -> datetime:
        return self._native_times.creation_time

    @property
    def access_time(self) -> datetime:
        return self._native_times.access_time

    @property
    def write_time(self) -> datetime:
        return self._native_times.write_time

    @property
    def change_time(self) -> datetime:
        return self._native_times.change_time

    # ---------- derived ----------
    @property
    def modified_age_seconds(self) -> float:
        now = datetime.now().astimezone()
        return (now - self.write_time).total_seconds()

    @property
    def changed_age_seconds(self) -> float:
        now = datetime.now().astimezone()
        return (now - self.change_time).total_seconds()

    # ---------- summary ----------
    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "is_file": self.is_file,
            "is_dir": self.is_dir,
            "name": self.name,
            "parent": str(self.parent),
            "suffix": self.suffix,
            "size_bytes": self.size_bytes,
            "drive": self.drive,
            "drive_id": self.drive_id,
            "volume_path": self.volume_path,
            "volume_serial_number": self.volume_serial_number,
            "filesystem_name": self.filesystem_name,
            "os_name": self.os_name,
            "os_release": self.os_release,
            "os_version": self.os_version,
            "machine": self.machine,
            "hostname": self.hostname,
            "python_stat_ctime": self.ctime_dt,
            "python_stat_mtime": self.mtime_dt,
            "python_stat_atime": self.atime_dt,
            "creation_time": self.creation_time,
            "access_time": self.access_time,
            "write_time": self.write_time,
            "change_time": self.change_time,
            "modified_age_seconds": self.modified_age_seconds,
            "changed_age_seconds": self.changed_age_seconds,
        }