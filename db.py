from __future__ import annotations

import logging
import re
from collections import deque
from pathlib import Path
from typing import Optional

import lmdb
from google.protobuf.message import EncodeError, DecodeError

from identifier import Id
# from lmdb_experi import mk_run_key
# from enum import nonmember

from meta import File, Dir, Run
from utils import Counter, SENTINEL
import record_pb2

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
            *,
            readonly: bool = True,
            create: bool = False,
    ) -> Db:  # lmdb env

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

        try:
            env = lmdb.open(**kwargs)

        except lmdb.Error as exc:
            if re.match('.*cannot find the path specified.*', exc.args[0]):
                raise exc  # to be elab.
            else:
                logger.warning(exc, exc_info=True)
                raise exc

        db_name = path.name
        logger.info('Opened database %s: readonly=%s', db_name, readonly)
        return Db(env)

    def __init__(self, lmdb_env: lmdb.Environment):
        self.env = lmdb_env
        self.dirs_queue = deque()
        self.files_queue = deque()

    def max_run_id(self) -> int:
        prefix = b"r:"
        max_id = 0
        last_key = b''
        with self.env.begin() as txn:
            with txn.cursor() as cur:
                if cur.set_range(prefix):
                    for key, _ in cur:
                        if not key.startswith(prefix):
                            break
                        last_key = key

        if last_key:
            last_key_str = last_key.decode()
            last_id_str = last_key_str.split(':')[1]
            max_id = int.from_bytes(bytes.fromhex(last_id_str))

            # or:
            len_id = 2
            # last_id_bytes = bytes.fromhex(last_key[len(prefix):])
            last_id_bytes = bytes.fromhex(last_key[-len_id:])
            max_id = int.from_bytes(last_id_bytes)

        return max_id

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

    RUN_PREFIX = 'r'

    @staticmethod
    def mk_run_key(run_id: Id) -> bytes:
        return run_id.to_bytes()

    @staticmethod
    def mk_run_rec(run: Run) -> bytes:
        rec = record_pb2.RunRecord(
            schema_version=SCHEMA_VERSION,
            id=run.id.val,
            path=str(run.path),
            description=run.description,
            platform=run.platform,
            date_time=run.start_time,
            dur_secs=run.duration,
            status=run.status,
            num_dirs=run.num_dirs,
            num_files=run.num_files,
            extra=run.extra,
            error=run.error,
        )

        try:
            return rec.SerializeToString()
        except EncodeError as exc:
            pass  # do what now?
            raise exc

    def put_run(self, run: Run):
        key = self.mk_run_key(run.id)
        value = self.mk_run_rec(run)
        # print(key)
        # print(value)

        with self.env.begin(write=True) as txn:
            try:
                txn.put(key, value)
            except EncodeError as exc:
                # do what?
                raise exc
        logger.warning('Stored run %s', run.id)

    def get_run(self, run_id: Id) -> Run:
        """Do I actually want a Run obj returned?
        What use cases?
        Only for info to the user?
        Verify: num Files/Dirs vs what the Run obj tells?

        And what for getting Files and Dirs?
        """

        # read the encoded record
        with self.env.begin(write=False) as txn:
            try:
                value = txn.get(self.mk_run_key(run_id))
            except DecodeError as exc:
                # do what?
                raise exc

        if not value:
            raise RuntimeError(f'No run {run_id} found')
            # logger.warning('No run %s found', run_id)

        run_rec = record_pb2.RunRecord()
        try:
            run_rec.ParseFromString(value)
        except DecodeError as exc:
            pass  # do what?
            raise exc

        # verify schema version; what if different?
        if run_rec.schema_version != SCHEMA_VERSION:
            raise ValueError('Schema version mismatch')

        # compose Run obj from the decoded record
        run = Run(
            id=run_id,
            path=Path(run_rec.path),
            description=run_rec.description,
            platform=run_rec.platform,
            start_time=run_rec.date_time,
            end_time=run_rec.date_time,
            duration=run_rec.dur_secs,
            extra=dict(run_rec.extra),
            status=run_rec.status,
            num_dirs=run_rec.num_dirs,
            num_files=run_rec.num_files,
            error=run_rec.error,
        )
        return run

    def update_run(self, run: Run):
        # update the relevant Run record with the changed values;
        # for finishing a run
        #
        # since we use lmdb, an upate is simply a re-write.

        self.put_run(run)
