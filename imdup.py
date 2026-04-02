import hashlib
import os
import pathlib
import queue
import threading
import time
import uuid
from typing import Optional

from meta import Dir, File, Run


RUN_ID = '42'
SENTINEL = object()


last_id: int = 0
last_hash: int = 0

start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin'

# dirs_by_path = dict()


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

def hash_file(from_queue: queue.Queue[File|object],
              to_queue: queue.Queue[File]):

    global last_hash

    worker_name = threading.current_thread().name

    while True:
        file = from_queue.get()
        try:
            if file is SENTINEL:
                return
            assert isinstance(file, File)

            try:
                file.hash_worker = worker_name

                last_hash += 1
                file.hash = f'hash_{('000' + str(last_hash))[-4:]}'
                # size, digest = hash_file(job.path, algorithm=algorithm, chunk_size=chunk_size)
            except Exception as exc:  # queue.Empty ?
                file.hash_error = f"{type(exc).__name__}: {exc}"

            to_queue.put(file)

        finally:
            from_queue.task_done()


def process_hashed_file(file: File, dirs_by_path: dict[str, Dir]):

    # file.hash is set

    if file.hash_error:
        return

    dir = file.parent
    # dir_path = dir.path
    # dir = dirs_by_path[dir_path]

    dir.file_hashes.append(file.hash)

    # update all dirs up: files_found := True
    pass

    # check if the parent dir is complete
    if len(dir.file_hashes) == len(dir.files):
        # calc fileS hash for the dir
        pass

        # check if all the subdirs (with files_found=True) een hash hebben;
        # zo ja, dan kun je de nested hash voor de dir berekenen en naar
        # boven doorgeven.
        pass


def process_hashed_files(hashed_files: queue.Queue[File], dirs_by_path: dict[str, Dir]):
    # global
    num_files_processed = 0
    try:
        while True:
            file = hashed_files.get()
            process_hashed_file(file, dirs_by_path)
            num_files_processed += 1
    except queue.Empty:
        print('Queue of hashed files is empty.')
    finally:
        print(f'Processed {num_files_processed} hashed files')


def handle_dir(path: str, subdirs: list[str], files: list[str],
               dirs_by_path: dict[str, Dir]):

    print(f'Handling dir {path}')

    dir = Dir(
        id=generate_id(),
        path=path,
        run_id=RUN_ID,
        num_files=len(files),
        files_found=bool(files),
        dirs = [],
        files = [],
    )

    dirs_by_path[path] = dir

    # dir['subdirs'] = sorted(subdirs)
    # dir['files'] = sorted(files)


    # file_hashes = []
    # for file in dir['files']:
    #     file_path = os.path.join(path, file)
    #     with open(file_path, 'rb') as f:
    #         file_hash = hashlib.md5(f.read()).hexdigest()
    #         file_hashes.append(file_hash)  # same order a file names
    #         # now store the file hash and file record

    for name in files:
        file = File(
            id=generate_id(),
            name=name,
            parent=dir,
            run_id=RUN_ID,
        )
        dir.files.append(file)

        # push the file obj for hashing
        pass


    # subdir_hashes = []
    # for subdir_name in dir['subdirs']:
    #     subdir_path = os.path.join(path, subdir_name)
    #     subdir = dirs_by_path[subdir_path]
    #     subdir_hashes.append(subdir['hash'])  # same order as subdir names

    for name in subdirs:
        path = str(pathlib.Path(path, name))
        subdir = dirs_by_path[path]
        subdir.parent = dir  # or just its ID?
        dir.dirs.append(subdir)

    # # calculate hash of concatenated file hashes
    # files_hash_input = ''.join(sorted(file_hashes))
    # files_hash = hashlib.md5(files_hash_input.encode()).hexdigest()

    # # concat the subdir hashes
    # subdirs_hash_input = ''.join(sorted(subdir_hashes))
    # subdirs_hash = hashlib.md5(subdirs_hash_input.encode()).hexdigest()

    # dir['hash'] = files_hash + '::' + subdirs_hash
    # return dir

def create_dir_info(path: str, dirs: list[str]):
    pass
    return None

def main() -> None:

    num_hash_workers = 2
    max_hash_queue_size = 5

    dirs_by_path: dict[str, Dir] = dict()


    # create files-to-hash queue
    fth_queue: queue.Queue[File|object] = queue.Queue(maxsize=max_hash_queue_size)

    # create files-hashed-queue
    fh_queue: queue.Queue[File] = queue.Queue()

    # create hash workers
    hash_workers = [
        threading.Thread(
            target=hash_file(),
            name=f"hash-worker-{i+1}",
            args=(fth_queue, fh_queue),
            daemon=False,
        )
        for i in range(num_hash_workers)
    ]

    # started = time.perf_counter()


    # create process-hashed-files worker
    pass


    # create storage queue
    storage_queue: queue.Queue[Dir] = queue.Queue()

    # create storage worker
    pass


    for fs_item in os.walk(start_dir, topdown=False):
        handle_dir(*fs_item, dirs_by_path)

    # walk the flattened dir tree where each dir can access values
    # (hashes) of its subdirs
    try:
        for dir_obj in a:
            pass

            # generate dir ID (if not already)
            # include the run ID

            # dir ID entry:
            # - key is dirid:
            # - record: run ID, dir name, file contents hash,
            #           dir path, contained file ID's,
            #           contained dir ID's

            # involve the dir name
            # involve the number of contained files?
            # involve ordered list of contained file names?
            # involve ordered list of contained dir names?
            # include into record the contained file ID's
            # include into record the contained dir ID's

            # create files contents hash:
            # - collect the file hashes
            # - concat these hashes in alphan order
            # - hash the resulting string

            # create files names hash:
            # - collect the file names
            # - concat these names in alphan order
            # - hash the resulting string

            # to be stored as: dir:<file contents hash>:<file names has>:<dir ID>

            # to create the dir hash, I need;
            #   - list of hashes of files it contains
            #   - list of hashes of dirs it contains
            # concat the hashes in normalized order (e.g. lexicogr)

    finally:
        # stop the workers
        for worker in hash_workers:
            fth_queue.put(SENTINEL)


if __name__ == "__main__":
    main()
