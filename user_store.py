from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable, Iterator, Optional

import lmdb

import record_pb2

SCHEMA_VERSION = 1


def make_user_key(user_id: str) -> bytes:
    """
    Encode keys so they are stable and easy to scan.
    Prefixes are useful if you later store multiple entity types.
    """
    return f"user:{user_id}".encode("utf-8")


class UserStore:
    def __init__(
        self,
        path: str | Path,
        map_size: int = 256 * 1024 * 1024,  # 256 MB
        max_dbs: int = 1,
    ) -> None:
        self.env = lmdb.open(
            str(path),
            map_size=map_size,
            max_dbs=max_dbs,
            subdir=True,
            create=True,
            readonly=False,
            lock=True,
            sync=True,
            metasync=True,
            readahead=True,
            meminit=False,
        )

    def close(self) -> None:
        self.env.close()

    def put_user(
        self,
        user_id: str,
        name: str,
        email: str,
        tags: list[str] | None = None,
    ) -> None:
        msg = record_pb2.UserRecord()
        msg.schema_version = SCHEMA_VERSION
        msg.user_id = user_id
        msg.name = name
        msg.email = email
        if tags:
            msg.tags.extend(tags)
        msg.updated_unix_ts = int(time.time())

        key = make_user_key(user_id)
        value = msg.SerializeToString()

        with self.env.begin(write=True) as txn:
            txn.put(key, value)

    def get_user(self, user_id: str) -> Optional[record_pb2.UserRecord]:
        key = make_user_key(user_id)

        with self.env.begin(write=False) as txn:
            raw = txn.get(key)

        if raw is None:
            return None

        msg = record_pb2.UserRecord()
        msg.ParseFromString(raw)

        if msg.schema_version != SCHEMA_VERSION:
            # In a real application, you might migrate here.
            raise ValueError(
                f"Unsupported schema_version={msg.schema_version}, "
                f"expected {SCHEMA_VERSION}"
            )

        return msg

    def delete_user(self, user_id: str) -> bool:
        key = make_user_key(user_id)
        with self.env.begin(write=True) as txn:
            return txn.delete(key)

    def put_users_batch(
        self,
        rows: Iterable[tuple[str, str, str, list[str]]],
    ) -> None:
        """
        Batch writes are usually much faster than one transaction per record.
        """
        with self.env.begin(write=True) as txn:
            for user_id, name, email, tags in rows:
                msg = record_pb2.UserRecord()
                msg.schema_version = SCHEMA_VERSION
                msg.user_id = user_id
                msg.name = name
                msg.email = email
                msg.tags.extend(tags)
                msg.updated_unix_ts = int(time.time())

                txn.put(
                    make_user_key(user_id),
                    msg.SerializeToString(),
                )

    def iter_all_users(self) -> Iterator[record_pb2.UserRecord]:
        """
        Iterate in key order.
        """
        prefix = b"user:"
        with self.env.begin(write=False) as txn:
            with txn.cursor() as cursor:
                found = cursor.set_range(prefix)
                while found:
                    key = cursor.key()
                    if not key.startswith(prefix):
                        break

                    msg = record_pb2.UserRecord()
                    msg.ParseFromString(cursor.value())
                    yield msg

                    found = cursor.next()

    def count_users(self) -> int:
        count = 0
        for _ in self.iter_all_users():
            count += 1
        return count

    # def __repr__(self) -> str:
    #     return f"LmdbTestEnv(path={self.path!r})"
