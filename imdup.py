import hashlib
import os
import pathlib
import queue
import threading
import time
import uuid
from typing import Optional

from meta import Dir, File, Run

from filehashing import hash_files
from dirhashing import process_hashed_files  # hash_dirs?

RUN_ID = '42'
SENTINEL = object()

num_hash_workers = 4
max_hash_queue_size = 10

last_id: int = 0

start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin'
start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin\\2025\\bloemennoord met wenda'


# generate run ID as yyyyMMdd:hhmmssuuu of start (wall) time

# run record: date and time, OS spec, FS spec, user comment
#             run duration,
#             total num files hashes, total num dir hashes,
#             errors encountered?
#             root dir ID?

def generate_id() -> str:
    global last_id
    last_id += 1
    # return str(uuid.uuid4())
    return f'id_{('000' + str(last_id))[-4:]}'


def handle_dir(path: str, subdirs: list[str], files: list[str],
               dirs_by_path: dict[pathlib.Path, Dir], fth_queue: queue.Queue[File|object]) -> int:
    """Processes a directory found by os.walk."""

    print(f'Handling dir {path}', flush=True)

    num_files_pushed = 0

    _dir = Dir(
        id=generate_id(),
        run_id=RUN_ID,
        path=pathlib.Path(path),
        num_files=len(files),
        num_dirs=len(subdirs),
        file_ids= [],
        dir_ids = [],

        # files_found=bool(files),
        # dir_hashes = [],
        # file_hashes = [],
    )

    dirs_by_path[_dir.path] = _dir

    # dir['subdirs'] = sorted(subdirs)

    for name in subdirs:
        # link the corresponding dir obj (which should be registered by now)
        # to the current dir (its parent)
        subdir = dirs_by_path[pathlib.Path(path, name)]
        subdir.parent = _dir

        _dir.dir_ids.append(subdir.id)  # do i need these?

    for name in files:
        file = File(
            id=generate_id(),
            name=name,
            parent=_dir,
            path=pathlib.Path(path, name),
            run_id=RUN_ID,
        )
        _dir.file_ids.append(file.id)

        # push the file obj for hashing
        while True:
            try:
                fth_queue.put(file)
                num_files_pushed += 1
                break
            except queue.Full:
                print(f'Queue of files to hash is full; will retry', flush=True)
                time.sleep(1)
                continue
            except Exception as e:
                print(f'Error pushing file {file.id}:{name}: {e}', flush=True)
                raise e

    return num_files_pushed


def main() -> None:

    num_dirs_processed = 0
    num_files_pushed_for_hashing = 0


    # dir objects will be registered by path
    # in order to (later) link them to their parent dir obj
    dirs_by_path: dict[pathlib.Path, Dir] = dict()

    # create queue for files to be hash
    fth_queue: queue.Queue[File|object] = queue.Queue(maxsize=max_hash_queue_size)

    # create queue for hashed files
    fh_queue: queue.Queue[File] = queue.Queue()

    # create hash workers
    hash_workers = [
        threading.Thread(
            target=hash_files,
            name=f"hash-worker-{i+1}",
            args=(fth_queue, fh_queue, SENTINEL),
            daemon=False,
        )
        for i in range(num_hash_workers)
    ]

    for w in hash_workers:
        w.start()

    # started = time.perf_counter()

    # create process-hashed-files worker
    pass

    # create storage queue
    # storage_queue: queue.Queue[Dir] = queue.Queue()

    # create storage worker
    pass


    # walk the flattened dir tree where each dir can access values
    # (hashes) of its subdirs
    try:
        for fs_item in os.walk(start_dir, topdown=False):
            root, dirs, files = fs_item
            num_files_pushed_for_hashing += handle_dir(root, dirs, files, dirs_by_path, fth_queue)
            num_dirs_processed += 1

    finally:
        # make the workers finish their work
        for _ in hash_workers:
            fth_queue.put(SENTINEL)
        print('Sentinel(s) sent to queue of files to hash', flush=True)

        # wait for the queue to be empty
        fth_queue.join()
        print('Queue of files to hash is empty', flush=True)

        # wait for the workers to finish
        for worker in hash_workers:
            worker.join()
        print('All hash workers finished', flush=True)

        pass

    pass

if __name__ == "__main__":
    main()
