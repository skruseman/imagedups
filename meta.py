# Provides dataclasses for passing meta-data
# on directories, files and runs.

from __future__ import annotations

import dataclasses
import hashlib
import os
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
    path: str
    # parent: Optional[Dir]  # None for top dir
    dirs: list[Dir]
    files: list[File]
    num_files: int = 0
    files_found: bool = False  #

    file_hashes: list[str] = dataclasses.field(default_factory=list)
    local_hash: Optional[bytes] = None  # 8 for xxhash.xxh3_64

    # timestamp: float

@dataclass(frozen=False)
class File:
    id: str
    name: str
    run_id: str
    parent: Dir
    length: int = -1
    hash: str = ""
    hash_worker: str = ""
    hash_error: str = ""
    # timestamp: float
