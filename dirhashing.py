import hashlib
import os
import pathlib
import queue
import threading
import time
import uuid
from typing import Optional
import logging

from utils import Counter

logger = logging.getLogger(__name__)

from meta import Dir, File, Run


# stored_files_counter = None
# stored_dirs_counter = None


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


def process_hashed_files(hashed_files: queue.Queue[File],
                         dirs_by_path: dict[str, Dir],
                         # files_counter: Counter,
                         # dirs_counter: Counter,
                         ):

    # global stored_files_counter
    # global stored_dirs_counter
    #
    # stored_files_counter = files_counter
    # stored_dirs_counter = dirs_counter

    # to create the dir hash, I need;
    #   - list of hashes of files it contains
    #   - list of hashes of dirs it contains
    # concat the hashes in normalized order (e.g. lexicogr)

    # # calculate hash of concatenated file hashes
    # files_hash_input = ''.join(sorted(file_hashes))
    # files_hash = hashlib.md5(files_hash_input.encode()).hexdigest()

    # # concat the subdir hashes
    # subdirs_hash_input = ''.join(sorted(subdir_hashes))
    # subdirs_hash = hashlib.md5(subdirs_hash_input.encode()).hexdigest()

    # dir['hash'] = files_hash + '::' + subdirs_hash

    num_files_processed = 0
    try:
        while True:
            file = hashed_files.get()
            process_hashed_file(file, dirs_by_path)
            num_files_processed += 1
    except queue.Empty:
        logger.warning('Queue of hashed files is empty')
    finally:
        logger.info('Processed %s hashed files', num_files_processed)
