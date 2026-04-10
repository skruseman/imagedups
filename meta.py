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


@dataclass(frozen=False)
class Run:
    id: str  # r'0001' and up i.e. 4 bytes
    description: str
    specification: str
    start_time: float
    end_time: float
    duration: float
    status: str


@dataclass(frozen=False)
class Dir:
    # name: str
    id: str  # 36 , str(uuid.uuid4()) ; prepend with run id?
    run_id: str  # 36
    path: pathlib.Path
    path_repr: str

    num_files: int
    num_dirs: int
    file_ids: list[str]
    dir_ids: list[str]

    parent: Optional[Dir] = None  # None for top dir

    # files_found: bool = False  #
    dir_hashes: list[str] = dataclasses.field(default_factory=list)
    file_hashes: list[str] = dataclasses.field(default_factory=list)
    files_hash: str = ''  # 16 hexits for xxhash.xxh3_64
    dirs_hash: str = ''  # 16 hexits for xxhash.xxh3_64
    # the overall "all" hash to be passed to the parent dir
    all_hash: str = ''  # 16 hexits for xxhash.xxh3_64

    # timestamp: float


@dataclass(frozen=False)
class File:
    id: str
    name: str
    # path: pathlib.Path
    run_id: str
    parent: Dir
    length: int = -1
    hash: str = ""
    hash_worker: str = ""
    hash_error: str = ""
    # timestamp: float
