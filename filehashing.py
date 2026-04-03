import hashlib
import os
import pathlib
import queue
import threading
import time
import uuid
from queue import ShutDown
from typing import Optional

from meta import File


last_hash: int = 0


def hash_file(path: pathlib.Path) -> str:
    global last_hash

    # file_hashes = []
    # for file in dir['files']:
    #     file_path = os.path.join(path, file)
    #     with open(file_path, 'rb') as f:
    #         file_hash = hashlib.md5(f.read()).hexdigest()
    #         file_hashes.append(file_hash)  # same order a file names
    #         # now store the file hash and file record

    # fake impl
    last_hash += 1
    return f'hash_{('000' + str(last_hash))[-4:]}'


def hash_files(from_queue: queue.Queue[File | object],
               to_queue: queue.Queue[File],
               sentinel: object):

    worker_name = threading.current_thread().name

    try:
        while True:
            try:
                file = from_queue.get(timeout=1)
            except queue.Empty:
                continue

            if file is sentinel:
                print(f'{worker_name} received sentinel', flush=True)
                from_queue.task_done()
                return
            assert isinstance(file, File)

            print(f'{worker_name} about to hash {file.id}:{file.path}', flush=True)
            file.hash_worker = worker_name
            file.hash = hash_file(file.path)

            # size, digest = hash_file(job.path, algorithm=algorithm, chunk_size=chunk_size)

            # except Exception as exc:  # queue.Empty ?
            #     file.hash_error = f"{type(exc).__name__}: {exc}"

            from_queue.task_done()
            # to_queue.put(file)

    except ShutDown:
        print(f'{worker_name} being shut down', flush=True)
        to_queue.put(
            sentinel,
            block=False,
        )

        # while from_queue.unfinished_tasks:
        #     print(f'Removing unfinished task from queue ({worker_name})')
        #     from_queue.task_done()

        return

    finally:
        print(f'{worker_name} finished', flush=True)
