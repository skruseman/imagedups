import hashlib
import xxhash
import os
import pathlib
import queue
import threading
import time
import uuid
from queue import ShutDown
from typing import Optional
from random import random
import logging

from utils import Counter
from meta import File


TIMEOUT_SECS = 0.25
TIMEOUT_SECS = 5

SLEEP_SECS = 0.5  # to fake hashing time

logger = logging.getLogger(__name__)

# hashed_files_counter = None

last_hash: int = 0  # not thread safe! the get and set are not atomic ops


def hash_file(path: pathlib.Path) -> str:

    # global last_hash

    #     with open(file_path, 'rb') as f:
    #         file_hash = hashlib.md5(f.read()).hexdigest()
    #         file_hashes.append(file_hash)  # same order a file names
    #         # now store the file hash and file record

    # fake impl
    # last_hash += 1
    # return f'hash_{('000' + str(last_hash))[-4:]}'

    # another fake impl but with proper hash format output
    to_hash = str(path).encode('utf-8')
    # hash = xxhash.xxh64(to_hash).hexdigest()
    hash = hashlib.sha256(to_hash).hexdigest()

    # variable sleep time
    time.sleep(SLEEP_SECS + random() * 0.5)

    return hash


def hash_files(from_queue: queue.Queue[File | object],
               to_queue: queue.Queue[File | object],
               sentinel: object,
               counter: Counter,
               ):

    worker_name = threading.current_thread().name

    try:
        while True:
            try:
                file = from_queue.get(timeout=TIMEOUT_SECS)
            except queue.Empty:
                counter.flush()
                continue

            if file is sentinel:
                logger.debug('Received sentinel')
                from_queue.task_done()
                break
            assert isinstance(file, File)

            if file.marks_empty_dir():
                logger.debug('Ignoring empty dir marker for dir: %s', file.parent.path_repr)
            else:
                file.hash_worker = worker_name
                file_path = file.parent.path / file.name
                logger.debug('About to hash file %s', file.id)
                file.hash = hash_file(file_path)

                counter.incr()
                if counter.get_approx() % 3 == 0:
                    counter.flush()

            # size, digest = hash_file(job.path, algorithm=algorithm, chunk_size=chunk_size)

            # except Exception as exc:  # queue.Empty ?
            #     file.hash_error = f"{type(exc).__name__}: {exc}"

            from_queue.task_done()
            to_queue.put(file)

    except ShutDown:
        logger.warning('Being shut down')
        to_queue.put(sentinel, block=False)  # should we really? isnt this main's resp?

        # while from_queue.unfinished_tasks:
        #     print(f'Removing unfinished task from queue ({worker_name})')
        #     from_queue.task_done()

    finally:
        counter.flush()
        logger.debug('Finished')
