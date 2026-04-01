# Provides dataclasses for passing meta-data
# on directories, files and runs.

from __future__ import annotations

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
    name: str
    id: str  # 36 , str(uuid.uuid4()) ; prepend with run id?
    run_id: str  # 36
    path: str
    parent: Optional[Dir]  # None for top dir
    dirs: list[Dir]
    files: list[str]
    local_hash: bytes  # 8 for xxhash.xxh3_64
    timestamp: float
    files_found: bool = False  #

@dataclass(frozen=False)
class File:
    name: str
    id: str
    run_id: str
    parent: Dir
    lenght: int
    hash: bytes
    timestamp: float
