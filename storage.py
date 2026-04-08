from __future__ import annotations

import logging
import queue
# from enum import nonmember

import xxhash

from meta import File, Dir


# EMPTY_HASH = ''  # for empty dirs?


logger = logging.getLogger(__name__)


def store_file_record(file: File):
    # key: file:<run id>:<id>
    # value: full details
    pass


def store_file_hash(file: File):
    # sha256 file hash and file size as key
    #   filehash:<hash>:<size>
    # FileHashRecord as value, or empty string?  b''
    pass


def store_file(file: File):
    pass

    # create file records for its hash and for the file itself

    logger.debug('Stored file %s (hash: %s)', file.id, file.hash[:8])


def calc_files_hash(file_hashes: list[str]) -> str:
    """Calculate a single hash value from individual file hashes.

    File hashes are sha256: 256 bits = 32 bytes; represented as hex stings (32x2 long)
    For hashing (concatenated) file hashes we use xxhash: 64 bits = 8 bytes (hex strings 16 long)

    If the list of hashes is empty, return empty string.
    If there's only a single file hash, return its first 16 hexits.
    Otherwise, sort the hashes, concatenate, then hash and return the hex digest.
    """

    if not file_hashes:
        return ''

    assert len(file_hashes[0]) == 64  # sha256: 32 bytes = 64 hexits
    if len(file_hashes) == 1:
        return file_hashes[0][:16]  # simply use substr of the file hash

    hasher = xxhash.xxh3_64()
    # normalize by sorting the hashes
    for file_hash in sorted(file_hashes):
        hasher.update(bytes.fromhex(file_hash))
    return hasher.hexdigest()


def calc_dirs_hash(dir_hashes: list[str]) -> str:
    """Calculate a single hash value from individual dir hashes.

    For dir hashes we use xxhash: 64 bits = 8 bytes (hex strings 16 long)

    If the list of hashes is empty, return empty string.
    If there's only a single dir hash, return it.
    Otherwise, sort the hashes, concatenate, then hash and return the hex digest.

    A dir hash can be the empty string, indicating it contains no files and no
    (sub-)directories containing files.
    """

    return ''


def calc_all_hash(files_hash: str, dirs_hash: str) -> str:
    """Calculates a directory node's "all" hash.

    The "all" hash is what is passed to a directory's parent dir, representing the
    files of the subject dir (its "files" hash) and its subdirectories' contents (
    its "dirs" hash).
    In the parent dir, this hash value is used to calculate the parent's "dirs" hash.

    To calculate:
    concatenate the files hash and the dirs hash, then xxhash and return the hexdigest.

    If the dir has no files, the files hash should be the empty string.
    The same goes for subdirectories and the dirs hash.
    If exactly one of the two hashes is not empty then return that value (i.e. is don't re-hash).
    If both hashes are empty then simply return the empty string.
    """

    return ""


def update_dir(dir_: Dir):
    if len(dir_.file_hashes) == dir_.num_files:
        dir_.files_hash = calc_files_hash(dir_.file_hashes)
        if len(dir_.dir_hashes) == dir_.num_dirs:
            all_hash = calc_dirs_hash(dir_.dir_hashes)
            update_dir(dir_.parent, all_hash)


def add_file_hash_to_dir(dir_: Dir, file_hash: str):
    assert len(dir_.file_hashes) < dir_.num_files
    dir_.file_hashes.append(file_hash)
    update_dir(dir_)


def handle_file(file: File):
    store_file(file)  # for now no actual storage
    add_file_hash_to_dir(file.parent, file.hash)


def store(file_queue: queue.Queue[File|object],
          sentinel: object):

    num_files_processed: int = 0

    while True:
        try:
            file = file_queue.get(timeout=0.5)
        except queue.Empty:
            logger.debug('Queue empty; will retry get')
            continue

        if file is sentinel:
            logger.info('Received sentinel')
            file_queue.task_done()
            break

        assert isinstance(file, File)
        handle_file(file)
        file_queue.task_done()
        num_files_processed += 1

    logger.info('Processed %s files' % num_files_processed)
