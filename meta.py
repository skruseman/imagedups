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
from uuid import UUID, uuid4

from identifier import Id

@dataclass(frozen=False)
class Run:
    id: Id
    path: pathlib.Path
    description: str
    platform: str
    start_time: float
    end_time: float = 1.23
    duration: float = 2.45
    root_dir: Optional[Dir] = None  # to be set after instantiation
    uuid: UUID = uuid4()
    extra: dict[str, str] = dataclasses.field(default_factory=dict)
    status: str = 'init'
    num_dirs: int = -1
    num_files: int = -1
    error: Optional[str] = None
    tags: list[str] = dataclasses.field(default_factory=list)


@dataclass(frozen=False)
class Dir:
    run: Run
    id: Id
    path: pathlib.Path  # redundancy but speeds up comparing file locations
    path_repr: str  # keep? what use?
    timestamp: float

    parent: Optional[Dir] = None  # None for root dir

    file_ids: list[Id] = dataclasses.field(default_factory=list)
    dir_ids: list[Id] = dataclasses.field(default_factory=list)

    file_hashes: list[str] = dataclasses.field(default_factory=list)
    dir_hashes: list[str] = dataclasses.field(default_factory=list)
    files_hash: str = ''  # 16 hexits for xxhash.xxh3_64
    dirs_hash: str = ''  # 16 hexits for xxhash.xxh3_64

    # the overall "all" hash to be passed to the parent dir
    all_hash: str = ''  # 16 hexits; only store for debugging?

    tags: list[str] = dataclasses.field(default_factory=list)


@dataclass(frozen=False)
class File:
    run: Run
    dir: Dir
    id: Id
    name: str
    length: int = -1

    creation_time: Optional[float] = None
    last_mod_time: Optional[float] = None
    # age_secs: Optional[float] = None

    hash: str = ""
    hash_worker: Optional[str] = None
    hash_duration: float = -1
    hash_error: Optional[str] = None

    tags: list[str] = dataclasses.field(default_factory=list)

    IS_EMPTY_DIR_MARKER = 'File instance to mark an empty directory'

    @staticmethod
    def make_empty_dir_marker(dir_: Dir) -> File:
        """Return a File instance pointing to the specified directory,
        indicating that the directory is empty."""

        return File(id=File.IS_EMPTY_DIR_MARKER, name='', run_id='', parent=dir_, length=0)

    def marks_empty_dir(self) -> bool:
        return self.id == self.IS_EMPTY_DIR_MARKER
