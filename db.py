from __future__ import annotations

import logging
import re
import lmdb
from pathlib import Path
from typing import cast, Iterable
from google.protobuf.message import EncodeError, DecodeError
from lmdb import Transaction

from db_constants import SCHEMA_VERSION
from db_item_handler import DirHandler, FileHandler
from db_item_handler import ItemHandler
from identifier import Id
import record_pb2
from meta import File, Dir, Run
from utils import Counter


# lmdb max nr of kv-pairs
MAP_SIZE = 2**32  # 4G

TIMEOUT_SECS = 0.5
TIMEOUT_SECS = 25

logger = logging.getLogger(__name__)

num_dirs_stored: Counter
num_files_stored: Counter


class Db:
    """
    Serves as a proxy for storing our objects in an lmdb database.


    lmdb errors:

    MapFullError: mdb_put: MDB_MAP_FULL: Environment mapsize limit reached
    Error: The environment 'test-db' is already open in this process.
    ReadonlyError: Cannot start write transaction with read-only environment.
    Error: The environment 'test-db' is already open in this process.

    Error: Attempt to operate on closed/deleted/dropped object.
    - for invalid Env obj
    -
    """

    @staticmethod
    def open(
            path: Path = Path('.'),  # path to dir with data and lock file; can be relative?
            *,
            readonly: bool = True,
            create: bool = False,
    ) -> Db:
        """Sets up an LMDB environment for accessing the specified database,
        wraps it in a Db object serving as a proxy for storing our objects,
        and returns that Db object.
        """

        kwargs = dict(
            path=str(path),
            map_size=MAP_SIZE,
            max_dbs=0,
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
                raise  # to be elab.
            else:
                logger.warning(exc, exc_info=True)
                raise

        db_name = path.name
        logger.info('Opened database %s: readonly=%s', db_name, readonly)
        return Db(env)

    def __init__(self, lmdb_env: lmdb.Environment):
        self.env = lmdb_env

        # item handlers (stateless)
        self.dir_handler = DirHandler()
        self.file_handler = FileHandler()

    def max_run_id(self) -> int:
        """Returns the highest int value occurring in the database, representing a Run identifier.

        Uses the lmdb feature that keys are always in alphabetical order,
        and our design decision that Run id's are encoded to fixed byte length.
        """
        prefix = b'r:'
        last_key = b''
        with self.env.begin(write=False) as txn, txn.cursor() as cur:
            if cur.set_range(prefix):
                while cur.key().startswith(prefix):
                    last_key = cur.key()
                    cur.next()
                if last_key:
                    return int.from_bytes(last_key[len(prefix):])
            return 0


    def add_run(self, run: Run):
        """Add the Run object to the DB.

        Raises KeyError if key already exists.
        """
        assert run.id.val > 0, 'Run id must not be zero'
        self._add_run(run)
        logger.info('Added run %s', run.id)

    def _add_run(self, run: Run):
        key = self.mk_run_key(run.id)
        value = self.mk_run_rec(run)
        self._add_kv_pair(key, value)

    @staticmethod
    def mk_run_key(run_id: Id) -> bytes:
        return b'r:' + run_id.to_bytes()

    @staticmethod
    def mk_run_rec(run: Run) -> bytes:
        rec = record_pb2.RunRecord(
            schema_version=SCHEMA_VERSION,
            id=run.id.val,
            uuid=run.uuid.bytes,
            path=str(run.path),
            description=run.description,
            platform=run.platform,
            start_time=run.start_time,
            dur_secs=run.duration,
            status=run.status,
            root_id=cast(Dir, run.root_dir).id.to_bytes(),
            num_dirs=run.num_dirs,
            num_files=run.num_files,
            extra=run.extra,
            error=run.error,
        )
        if run.tags:
            rec.tags.extend(run.tags)

        try:
            return rec.SerializeToString()
        except EncodeError as exc:
            pass  # do what now?
            raise exc


    def add_dir(self, dir_: Dir):
        self.add_dirs([dir_])

    def add_dirs(self, dirs: Iterable[Dir]):
        self._add_items(dirs, self.dir_handler)

    def add_file(self, file: File):
        self.add_files([file])

    def add_files(self, files: Iterable[File]):
        self._add_items(files, self.file_handler)

    def add_item(self, item: Dir|File):
        self.add_items([item])

    def add_items(self, items: Iterable[Dir|File]):
        self._add_items(items)

    def _add_items(self, items: Iterable[Dir | File], handler: DirHandler | FileHandler | None = None):
        """Adds key-value pairs for the specified items to the database using the handler.
        If no handler is specified then the correct handler (for the item) type is looked up.
        Each key should not yet exist in the database or a KeyError is raised.
        """
        with self.env.begin(write=True) as txn:
            for item in items:
                handler_ = handler or self._get_handler(item)
                handler_ = cast(ItemHandler[Dir | File], handler_)
                try:
                    self._add_kv_pairs(item, handler_, txn)
                except:
                    # transaction aborts implicitly
                    logger.exception('Failed to add item: %s\n'
                                     'Transaction aborts: %s', item.id, txn.stat())
                    raise
        item_ids = '; '.join(str(item.id) for item in items)
        logger.debug('Items added: %s', item_ids)

    @staticmethod
    def _add_kv_pairs(item: Dir | File, handler: ItemHandler[Dir|File], txn: Transaction):
        for key, value in handler.mk_kv_pairs(item):
            # assert key
            if not txn.put(key, value, overwrite=False):
                logger.fatal('Failed to add key %s', key)
                raise KeyError(f'{key} already exists')
            logger.debug('Added key %s', key)

    def _get_handler(self, item: Dir | File) -> DirHandler | FileHandler:
        """Here's the only location where we differentiate between Dir and File."""
        if isinstance(item, Dir):
            return self.dir_handler
        if isinstance(item, File):
            return self.file_handler
        raise TypeError(f"Unsupported item type: {type(item).__name__}")


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
            start_time=run_rec.start_time,
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
        # since we use lmdb, an update is simply a re-write.

        self._add_run(run)
