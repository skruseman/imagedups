import hashlib
import os
import pathlib
import queue
import logging
import logging.config
import threading
import time
import uuid
from logging import exception
from queue import Queue
from typing import Optional

import logging

from meta import Dir, File, Run
from filehashing import hash_files
from monitor import monitor_queues
from storage import store
from dirhashing import process_hashed_files  # hash_dirs?
from utils import Counter

RUN_ID = '42'
SENTINEL = object()


logger = logging.getLogger(__name__)
stop_event = threading.Event()

num_hash_workers = 4
max_hash_queue_size = 12

last_ids: dict[str, int] = {}

start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin'
# start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin\\2025\\bloemennoord met wenda'
start_dir_len = len(start_dir)

# generate run ID as yyyyMMdd:hhmmssuuu of start (wall) time

# run record: date and time, OS spec, FS spec, user comment
#             run duration,
#             total num files hashes, total num dir hashes,
#             errors encountered?
#             root dir ID?

def generate_id(cat: str = '') -> str:
    # global last_ids
    last_id = last_ids.get(cat, 0)
    last_id += 1
    last_ids[cat] = last_id
    # return str(uuid.uuid4())
    num_len = 4
    return f'{cat + '-' if cat else ''}{('0'*4 + str(last_id))[-num_len:]}'


def queue_file_for_hashing(name: str, dir_: Dir, fth_queue: Queue[File | object]):
    file = File(
        id=generate_id('file'),
        name=name,
        parent=dir_,
        # path = pathlib.Path(path, name),
        run_id=RUN_ID,
    )
    logger.debug('Assigned ID %s to: %s', file.id, dir_.path_repr + name)
    dir_.file_ids.append(file.id)

    # push the file obj for hashing
    while True:
        try:
            fth_queue.put(file)  # we handle timeout ourselves for logging purposes
            break
        except queue.Full:
            logger.debug('Queue of files to hash is full; will retry')
            time.sleep(1)
            continue
        except Exception as e:
            logger.exception('Error pushing file %s:%s: %s', file.id, name, e)
            raise e


def handle_dir(path: str, subdirs: list[str], files: list[str],
               dirs_by_path: dict[pathlib.Path, Dir], fth_queue: queue.Queue[File|object]) -> int:
    """Processes a directory found by os.walk."""

    num_files_pushed = 0

    path_obj = pathlib.Path(path)
    parent_dir = dirs_by_path.get(pathlib.Path(path).parent, None)
    path_repr = '.' + os.path.sep + (str(path_obj.relative_to(start_dir)) + os.path.sep if parent_dir else '')

    dir_ = Dir(
        id = generate_id('dir'),
        run_id = RUN_ID,
        path = path_obj,
        num_files = len(files),
        num_dirs = len(subdirs),
        file_ids= [],
        dir_ids = [],
        parent = parent_dir,
        path_repr= path_repr,

        # files_found=bool(files),
        # dir_hashes = [],
        # file_hashes = [],
    )
    logger.debug('Assigned ID %s to:  %s', dir_.id, dir_.path_repr)

    if dir_.num_dirs > 0:
        # enable subdirs to look up this Dir instance by path
        dirs_by_path[dir_.path] = dir_

    elif dir_.num_files == 0:
        # push a dummy File instance that marks this directory is empty;
        # no file hashing to be done, yet we later need to process and store the dir.
        logger.info('Empty directories are NOT ignored and are stored as well: %s', dir_.path_repr)
        fth_queue.put(File.make_empty_dir_marker(dir_))
        return 0

    # dir['subdirs'] = sorted(subdirs)

    # for name in subdirs:
        # link the corresponding dir obj (which should be registered by now)
        # to the current dir (its parent)
        # subdir = dirs_by_path[pathlib.Path(path, name)]
        # subdir.parent = _dir

        # dirs_by_path[pathlib.Path(path)] = _dir

        # _dir.dir_ids.append(subdir.id)  # do i need these?

    for name in files:
        queue_file_for_hashing(name, dir_, fth_queue)
        num_files_pushed += 1

    return num_files_pushed


def main() -> None:

    logger.info('Inspecting contents of directory: %s', start_dir)

    num_dirs_found = 0
    num_files_found = 0

    # dir objects are registered by path
    # in order to (later) link subdirs to them
    dirs_by_path: dict[pathlib.Path, Dir] = dict()

    # create queue for files to be hash, and a counter
    fth_queue: queue.Queue[File|object] = queue.Queue(maxsize=max_hash_queue_size)
    hashed_files_counter: Counter = Counter()

    # create queue for hashed files, and counters
    fh_queue: queue.Queue[File|object] = queue.Queue()
    stored_files_counter: Counter = Counter()
    stored_dirs_counter: Counter = Counter()

    # create hash workers
    hash_workers = [
        threading.Thread(
            target=hash_files,
            name=f"hash-workr-{i+1}",
            args=(fth_queue, fh_queue, SENTINEL, hashed_files_counter),
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
    store_worker = threading.Thread(
        target=store,
        name='store-worker',
        args=(fh_queue, SENTINEL, stored_dirs_counter, stored_files_counter),
        daemon=False,
    )
    store_worker.start()

    # start monitor thread
    monitor = threading.Thread(
        target=monitor_queues,
        name='monitor',
        args=(fth_queue, fh_queue, stop_event),
        daemon=False,
    )
    monitor.start()

    # walk the flattened dir tree where each dir can access values
    # (hashes) of its subdirs
    try:
        for fs_item in os.walk(start_dir, topdown=True):
            root, dirs, files = fs_item
            num_files_found += handle_dir(root, dirs, files, dirs_by_path, fth_queue)
            num_dirs_found += 1

        logger.info('Detected %s files in %s directories', num_files_found, num_dirs_found)

    finally:
        # make the workers finish
        for _ in hash_workers:
            fth_queue.put(SENTINEL)

        logger.debug('Sentinel(s) sent to queue of files to hash')

        # wait for the hash queue to be empty
        fth_queue.join()
        logger.debug('Queue of files to hash is empty')

        # wait for the hash workers to finish
        for worker in hash_workers:
            worker.join()
        logger.info('All hash workers finished')

        # make the store worker finish
        fh_queue.put(SENTINEL)
        logger.info('Sentinel pushed to queue of hashed files')

        # wait for the store queue to be empty
        fh_queue.join()
        logger.info('Queue of hashed files is empty')

        # wait for the store worker to finish
        store_worker.join()
        logger.info('Store worker finished')

        # make the monitor thread finish
        stop_event.set()
        monitor.join()
        logger.info('Monitor thread finished')

    assert stored_dirs_counter.get() == num_dirs_found
    assert stored_files_counter.get() == num_files_found


if __name__ == "__main__":

    logging.config.fileConfig(fname='logging.conf', disable_existing_loggers=False)

    main()

    print('Fin!')