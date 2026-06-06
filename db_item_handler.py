"""Item specific support for storage in the database."""

from __future__ import annotations

import logging
from typing import Iterable, Tuple, Generic, TypeVar
from abc import ABC, abstractmethod

from identifier import Id
import record_pb2
from meta import File, Dir, Run
from db_constants import SCHEMA_VERSION


logger = logging.getLogger(__name__)

T = TypeVar('T')


class ItemHandler(ABC, Generic[T]):
    """Abstract base class for type specific, stateless handlers for storage in the database."""

    @staticmethod
    @abstractmethod
    def mk_kv_pairs(item: T) -> Iterable[Tuple[bytes, bytes]]:
        """Returns key-value pairs for storage in the database"""
        pass


class DirHandler(ItemHandler[Dir]):
    """Provides Dir specific DB functionality."""

    @staticmethod
    def mk_kv_pairs(dir_: Dir) -> Iterable[Tuple[bytes, bytes]]:
        """Returns Dir specific key-value pairs for storage in the database."""

        # one pair for the Dir object itself
        key_for_dir = DirHandler.mk_dir_key(dir_.id)
        value_for_dir = DirHandler.mk_dir_rec(dir_)
        pairs = [(key_for_dir, value_for_dir)]

        # pairs for files hash and dirs hash (if not empty); the value is the empty bytestring
        key_for_files_hash = DirHandler.mk_dir_files_hash_key(dir_.id, dir_.files_hash, dir_.dirs_hash)
        if key_for_files_hash:
            pairs.append((key_for_files_hash, b''))
        key_for_dirs_hash = DirHandler.mk_dir_dirs_hash_key(dir_.id, dir_.dirs_hash, dir_.files_hash)
        if key_for_dirs_hash:
            pairs.append((key_for_dirs_hash, b''))

        return pairs

    @staticmethod
    def mk_dir_key(dir_id: Id) -> bytes:
        return b'd:' + dir_id.to_bytes()

    @staticmethod
    def mk_dir_rec(dir_: Dir) -> bytes:
        rec = record_pb2.DirRecord(
            schema_version=SCHEMA_VERSION,
            id=dir_.id.to_bytes(),
            path=str(dir_.path),
            date_time=dir_.timestamp,
            files_hash=dir_.files_hash,
            dirs_hash=dir_.dirs_hash,
        )
        if dir_.parent:
            rec.parent_id = dir_.parent.id.to_bytes()
        if dir_.file_ids:
            rec.file_ids.extend([id_.to_bytes() for id_ in dir_.file_ids])
        if dir_.dir_ids:
            rec.dir_ids.extend([id_.to_bytes() for id_ in dir_.dir_ids])
        if dir_.tags:
            rec.tags.extend(dir_.tags)
        return rec.SerializeToString()

    @staticmethod
    def mk_dir_dirs_hash_key(id_: Id, hash_1: str, hash_2: str) -> bytes:
        """Returns a bytestring to be used as key for a 'dirs hash' type of
        key-value pair."""
        return DirHandler._mk_dir_hash_key(id_, hash_1, hash_2, b'dhd')

    @staticmethod
    def mk_dir_files_hash_key(id_: Id, hash_1: str, hash_2: str) -> bytes:
        """Returns a bytestring to be used as key for a 'files hash' type of
        key-value pair."""
        return DirHandler._mk_dir_hash_key(id_, hash_1, hash_2, b'dhf')

    @staticmethod
    def _mk_dir_hash_key(id_: Id, hash_1: str, hash_2: str, prefix: bytes) -> bytes:
        """Returns a bytestring to be used as key for a Dir hash
        key-value pair.

        The key consists of a prefix, both hashes and the
        Dir id, separated by b\':\'. The Dir id serves to make keys unique.

        If the first hash is empty then return an empty bytes string.
        The second hash is allowed to be the empty string.
        """
        if not hash_1:
            return b''
        assert len(hash_1) == 16 and len(hash_2) in (0, 16)
        parts = [prefix, bytes.fromhex(hash_1), bytes.fromhex(hash_2), id_.to_bytes()]
        return b':'.join(parts)


class FileHandler(ItemHandler[File]):
    """Provides File specific DB functionality."""

    @staticmethod
    def mk_kv_pairs(file: File) -> Iterable[Tuple[bytes, bytes]]:
        """Returns File specific key-value pairs for storage in the database."""

        # one pair for the File object itself
        key_for_file = FileHandler.mk_file_key(file.id)
        value_for_file = FileHandler.mk_file_rec(file)

        # and a pair for the file hash, if not empty; the value is the empty bytestring
        key_for_hash = FileHandler.mk_file_hash_key(file.id, file.hash)

        return [
            (key_for_file, value_for_file),
            (key_for_hash, b'')
        ]

    @staticmethod
    def mk_file_key(file_id: Id) -> bytes:
        return b'f:' + file_id.to_bytes()

    @staticmethod
    def mk_file_rec(file: File) -> bytes:
        rec = record_pb2.FileRecord(
            schema_version=SCHEMA_VERSION,
            id=file.id.to_bytes(),
            name=file.name,
            date_time=file.creation_time,
            length=file.length,
            hash=file.hash,
        )
        if file.tags:
            rec.tags.extend(file.tags)
        return rec.SerializeToString()

    @staticmethod
    def mk_file_hash_key(id_: Id, hash_: str) -> bytes:
        """Returns a bytestring to be used as key for a 'file hash' type of
        key-value pair.

        The key consists of the key-value pair prefix, the file hash, and the
        file id, separated by b\':\'. The file id serves to make keys unique.
        """
        assert len(hash_) == 32
        return b':'.join([b'fh', bytes.fromhex(hash_), id_.to_bytes()])
