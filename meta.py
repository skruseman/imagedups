# Provides dataclasses for passing meta-data
# on directories, files and runs.

from __future__ import annotations

import dataclasses
import hashlib
import os
import pathlib
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable

from identifier import Id

@dataclass(frozen=False)
class Run:
    id: Id
    path: str
    description: str
    specification: str
    start_time: float
    end_time: float
    duration: float
    extra: dict[str, str] = dataclasses.field(default_factory=dict)
    status: str = 'init'
    num_dirs: int = -1
    num_files: int = -1
    error: Optional[str] = None


@dataclass(frozen=False)
class Dir:
    id: Id
    name: str
    rel_path: pathlib.Path
    run: Run
    path_repr: str

    num_files: int = -1
    num_dirs: int = -1
    file_ids: list[str] = dataclasses.field(default_factory=list)
    dir_ids: list[str] = dataclasses.field(default_factory=list)

    parent: Optional[Dir] = None  # None for top dir

    file_hashes: list[str] = dataclasses.field(default_factory=list)
    dir_hashes: list[str] = dataclasses.field(default_factory=list)
    files_hash: str = ''  # 16 hexits for xxhash.xxh3_64
    dirs_hash: str = ''  # 16 hexits for xxhash.xxh3_64

    # the overall "all" hash to be passed to the parent dir
    # all_hash: str = ''  # 16 hexits for xxhash.xxh3_64

    # timestamp: float


@dataclass(frozen=False)
class File:
    id: Id
    name: str
    rel_path: pathlib.Path
    run: Run
    dir: Dir
    length: int = -1
    hash: str = ""
    hash_duration: float = -1
    hash_worker: Optional[str] = None
    hash_error: Optional[str] = None
    creation_time: Optional[float] = None
    last_mod_time: Optional[float] = None
    # age_secs: Optional[float] = None

    IS_EMPTY_DIR_MARKER = 'File instance to mark an empty directory'

    @staticmethod
    def make_empty_dir_marker(dir_: Dir) -> File:
        """Return a File instance pointing to the specified directory,
        indicating that the directory is empty."""

        return File(id=File.IS_EMPTY_DIR_MARKER, name='', run_id='', parent=dir_, length=0)

    def marks_empty_dir(self) -> bool:
        return self.id == self.IS_EMPTY_DIR_MARKER
