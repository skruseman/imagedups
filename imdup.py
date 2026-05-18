import os
import pathlib
import queue
import logging.config
import threading
import time
import logging

from queue import Queue
from typing import Optional

from scripts.regsetup import description

from identifier import Id
from meta import Run, Dir, File
from filehashing import hash_files
from monitor import monitor_queues
from dirhashing import collect_and_store
from utils import Counter, SENTINEL

# path to directory containing the LMDB database
LMDB_PATH = './imdup_lmdb'

# devel only
RUN_ID = '42'

# number of threads to use for performing file hashing
NUM_HASH_WORKERS = 4

# max number of entries in the 'files to be hashed' queue
# (to push back on the thread queing files)
MAX_HASH_QUEUE_SIZE = 12

# event used to control the monitoring thread
stop_event = threading.Event()

logger = logging.getLogger(__name__)

# for devel only: remember last used integer ID value per category (dir, file)
last_ids: dict[str, int] = {}

# object representing a single hashing run
the_run: Run

# path of directory to start the hashing run at
start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin'
# start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin\\2025\\bloemennoord met wenda'
# start_dir = 'E:\\MeerNoodMovesMarietta\\2020-04-13\\50 jaar M'


def collect_run_input():
    """Interactively collects input from the user."""
    pass

def generate_id(cat: str = '') -> str:
    # global last_ids
    last_id = last_ids.get(cat, 0)
    last_id += 1
    last_ids[cat] = last_id
    # return str(uuid.uuid4())
    num_len = 4
    return f'{cat + '-' if cat else ''}{('0'*4 + str(last_id))[-num_len:]}'

def mkid(last: int) -> str:
    """Returns a string that represents the hex
    value of a two-byte unsigned int value."""
    assert last >= 0
    ival = last + 1
    # assert ival < 256
    bval = ival.to_bytes(length=2)
    sval = bval.hex()
    return sval

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

    logger.info('Processing contents of directory: %s', start_dir)

    num_dirs_found = 0
    num_files_found = 0

    # register Dir objects by path to later link subdirs to them
    dirs_by_path: dict[pathlib.Path, Dir] = dict()

    # create queue for files to hash, and a counter
    fth_queue: queue.Queue[File|object] = queue.Queue(maxsize=MAX_HASH_QUEUE_SIZE)
    hashed_files_counter: Counter = Counter()  # thread-safe

    # create queue for hashed files, and counters
    fh_queue: queue.Queue[File|object] = queue.Queue()
    stored_files_counter: Counter = Counter()
    stored_dirs_counter: Counter = Counter()

    # create Run object;
    # with temporary ID value; final value will be set by db object;
    # but some fields should be set from here
    run = Run(
        id=Id(0),
        path=pathlib.Path(start_dir),
        description='test run for development',
        platform='plattevorm',
        start_time=time.time(),
    )

    # create hash workers
    hash_workers = [
        threading.Thread(
            target=hash_files,
            name=f"hashworker-{i+1}",
            args=(fth_queue, fh_queue, hashed_files_counter),
            daemon=False,
        )
        for i in range(NUM_HASH_WORKERS)
    ]
    for w in hash_workers:
        w.start()

    started = time.perf_counter()

    # create process-hashed-files worker
    # pass

    # create storage queue
    # storage_queue: queue.Queue[Dir] = queue.Queue()

    # create storage worker; not safe for multiple threads because...
    store_worker = threading.Thread(
        target=collect_and_store,
        name='store-worker',
        args=(fh_queue, run, LMDB_PATH, stored_dirs_counter, stored_files_counter),
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

    assert stored_dirs_counter.value() == num_dirs_found
    assert stored_files_counter.value() == num_files_found


if __name__ == "__main__":

    logging.config.fileConfig(fname='logging.conf', disable_existing_loggers=False)

    # to allow only logging from logger X:
    # console_handler = logging.getLogger().handlers[0]
    # console_handler.addFilter(logging.Filter("utils"))
    # Just one filter can be added!

    main()

    print('Fin!')