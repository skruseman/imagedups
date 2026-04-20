from __future__ import annotations

import logging
from collections import deque
from pathlib import Path
from typing import Optional

import lmdb

# from enum import nonmember

from meta import File, Dir, Run
from utils import Counter, SENTINEL
# from record_pb2 import FileRecord, FileHashRecord, DirRecord, DirHashRecord, RunRecord

SCHEMA_VERSION = 1
MAP_SIZE = 2**32
MAX_DBS = 0

TIMEOUT_SECS = 0.5
TIMEOUT_SECS = 25

logger = logging.getLogger(__name__)


num_dirs_stored: Counter
num_files_stored: Counter


class Db:

    """
    lmdb errors:

    MapFullError: mdb_put: MDB_MAP_FULL: Environment mapsize limit reached
    Error: The environment 'test-db' is already open in this process.
    ReadonlyError: Cannot start write transaction with read-only environment.
    Error: The environment 'test-db' is already open in this process.

    Error: Attempt to operate on closed/deleted/dropped object.
    - for invalid Env obj
    -
    """

    # @staticmethod
    # def create(path: str|Path, map_size: int, max_dbs: int) -> Db:
    #     env = lmdb.open(
    #         str(path),
    #         map_size=MAP_SIZE,
    #         max_dbs=max_dbs,
    #         subdir=True,
    #         create=True,
    #         readonly=False,
    #         lock=True,
    #         sync=True,
    #         metasync=True,
    #         readahead=True,
    #         meminit=False,
    #     )
    #     return Db(env)

    @staticmethod
    def open(
            path: Path = Path('.'),  # path to dir with data and lock file; can be relative?
            readonly: bool = True,
            *,
            create: bool = False,
    ) -> Db:

        kwargs = dict(
            path=str(path),
            map_size=MAP_SIZE,
            max_dbs=MAX_DBS,
            subdir=True,
            create=create,
            readonly=readonly,
            lock=True,
            sync=True,
            metasync=True,
            readahead=True,
            meminit=False,

        )

        # attempt to open;
        #   if not create and missing: get confirmation to create and retry
        #   if exists (regardless of create) then display some info from the db like
        #     last three runs with description; get confirmation to continue

        # on open: log info on readonly, create, etc

        env = lmdb.open(**kwargs)

        return Db(env)

    def __init__(self, lmdb_env: lmdb.Environment):
        self.env = lmdb_env
        self.dirs_queue = deque()
        self.files_queue = deque()
        pass

    def store_file(self, file: File):
        self.files_queue.append(file)
        if len(self.files_queue) > 3:
            self.put_files_batch()

    def put_files_batch(self):
        for file in self.files_queue.pop():
            self.put_file(file)

    def put_file(self, file: File):
        # create file rec
        # create file hash rec
        # store both records
        # update counter(s)
        pass


    # def make_run_key(self, run_id: str) -> bytes:
    #     pass

    # def store_run_record(self, run: Run):
    #     # key: ?
    #     # value: ?
    #     self.create_run_record(run)
    #     pass


    def store_file_record(self, file: File):
        # key: file:<run id>:<id>
        # value: full details
        pass


    def store_file_hash(self, file: File):
        # sha256 file hash and file size as key
        #   filehash:<hash>:<size>
        # FileHashRecord as value, or empty string?  b''
        pass


    # def store_file(self, file: File):
    #     # create records for the file's hash and for the file itself
    #
    #     global num_files_stored
    #     num_files_stored.incr()
    #     logger.debug('Stored file %s (hash: %s)', file.id, file.hash[:8])


    def store_dir(self, dir_: Dir):
        # create records for the dir's hash and for the dir itself

        global num_dirs_stored
        num_dirs_stored.incr()
        logger.debug('Stored dir %s (hash: %s | %s)', dir_.id, dir_.files_hash[:8], dir_.dirs_hash[:8])


    def store_run(self, run: Run):
        #

        logger.debug('Stored run %s', run.id)


    def update_run(self, run: Run):
        # update the relevant Run record with the changed values; for finishing a run

        logger.debug('Updated run %s', run.id)
