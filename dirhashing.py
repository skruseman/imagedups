from __future__ import annotations

from typing import Optional, Iterable
import logging
import queue
from collections import deque
import xxhash

from meta import File, Dir
from utils import Counter, SENTINEL


TIMEOUT_SECS = 0.5
TIMEOUT_SECS = 25

logger = logging.getLogger(__name__)


def collect_and_store(hashed_files: queue.Queue[File | object],
                      dirs_counter: Counter,
                      files_counter: Counter) -> None:
    """Processes entries from the queue and stores them in the database.


    """
    Storage(dirs_counter, files_counter).run(hashed_files)


class Storage:
    """Don't use this class externally; use `collect_and_store` instead.

    This class calculates dir hashes, and will store file and dir hashes to the database.
    """

    @staticmethod
    def calc_files_hash(file_hashes: list[str]) -> str:
        """Calculates a file group hash from individual file hashes.

        Individual file hashes are sha256: 256 bits = 32 bytes; represented as hex stings (32x2 long)
        For file group hashes we use xxhash: 64 bits = 8 bytes (hex strings 16 long)

        If the list of hashes is empty, return empty string.
        If there's only a single file hash was received, return its first 16 hexits.
        Otherwise, sort the input hashes, concatenate them, then hash and return the hex digest.
        """

        if not file_hashes:
            return ''

        assert len(file_hashes[0]) == 64  # sha256: 32 bytes = 64 hexits
        if len(file_hashes) == 1:
            return file_hashes[0][:16]  # return first 16 hexits of that single file's hash

        hasher = xxhash.xxh3_64()
        # normalize by sorting the hashes
        for hash_ in sorted(file_hashes):
            hasher.update(bytes.fromhex(hash_))
        return hasher.hexdigest()

    @staticmethod
    def calc_dirs_hash(dir_hashes: list[str]) -> str:
        """Calculates a dir group hash from individual dir hashes.

        For both dir hashes and dir group hashes we use xxhash: 64 bits = 8 bytes (hex strings 16 long)

        If the list of hashes is empty, return empty string.
        If only a single dir hash, return it.
        Otherwise, sort the input hashes, concatenate them, then hash and return the hex digest.

        An individual dir hash can be the empty string, indicating the dir contains no files and no
        (sub-)directories containing files. Such empty string hashes will not affect the returned hash
        value; unless all input hashes are empty, in which case an empty string hash is returned.
        """

        if not ''.join(dir_hashes):
            return ''

        if len(dir_hashes) == 1:
            assert len(dir_hashes[0]) == 16
            return dir_hashes[0]

        hasher = xxhash.xxh3_64()
        # normalize by sorting the hashes; empty hash strings do not affect the output hash value
        for hash_ in sorted(dir_hashes):
            hasher.update(bytes.fromhex(hash_))
        return hasher.hexdigest()

    @staticmethod
    def calc_all_hash(files_hash: str, dirs_hash: str) -> str:
        """Calculates a directory node's "all" (overall) hash.

        The "all" hash is what is passed to a directory's parent dir, representing both the
        files of the subject dir (its "files" hash) and its subdirectories' contents (
        its "dirs" hash).
        In the parent dir, this hash value is used to calculate the parent's "dirs" hash.

        To calculate:
        concatenate the files hash and the dirs hash, then xxhash and return the hexdigest.

        If the dir has no files, the files hash should be the empty string.
        The same goes for subdirectories and the dirs hash.
        If exactly one of the two hashes is not empty then return that value (no re-hashing a single hash).
        If both hashes are empty then return the empty string.
        """

        if not (files_hash or dirs_hash):  # both empty
            return ''
        if not (files_hash and dirs_hash):  # exactly one is empty
            assert len(files_hash) + len(dirs_hash) == 16
            return files_hash + dirs_hash  # i.e. the one that is not empty

        hasher = xxhash.xxh3_64()
        for hash_ in (files_hash, dirs_hash):
            assert len(hash_) == 16
            hasher.update(bytes.fromhex(hash_))
        return hasher.hexdigest()


    def __init__(self, dirs_counter: Counter, files_counter: Counter):
        """This class ...

        This class is not thread-safe because it operates on shared Dir objects
        which are not thread-safe. E.g. two threads handling sibling files from the same Dir;
        adding file/dir hashes and calculating group hashes would have to be made thread-safe.
        """

        self.dirs_counter = dirs_counter
        self.files_counter = files_counter

    def pop(self, hashed_files: queue.Queue[File | object], ) -> Iterable[File]:
        """Generator for popping File objects from the queue. Use locally only."""

        while True:
            try:
                file = hashed_files.get(timeout=TIMEOUT_SECS)
            except queue.Empty:
                logger.debug('Input queue empty; will retry pop')
                continue

            hashed_files.task_done()
            if file is SENTINEL:
                logger.info('Input queue exhausted')
                return
            assert isinstance(file, File)
            yield file

    def store_file(self, file: File):
        # create records for the file's hash and for the file itself

        self.files_counter.incr()
        logger.debug('Stored file %s (hash: %s)', file.id, file.hash[:8])


    def store_dir(self, dir_: Dir):
        # create records for the dir's hash and for the dir itself

        self.dirs_counter.incr()
        logger.debug('Stored dir %s (hash: %s | %s)', dir_.id, dir_.files_hash[:8], dir_.dirs_hash[:8])

    def update_dir(self, dir_: Dir):
        """Sets the overall hash value if possible, in which case this value is passed to the parent dir
        (as hash representing the dir).

        If passed a node representing an empty dir, the "files hash" and "dirs hash" are empty and so
        will be the "all hash".
        """

        files_done = len(dir_.file_hashes) == dir_.num_files
        # for dirs with only empty subdirs (including nested), the dirs hash will remain empty
        dirs_done = len(dir_.dir_hashes) == dir_.num_dirs

        if files_done and dirs_done:

            assert dir_.num_files == 0 or dir_.files_hash
            assert dir_.num_dirs == 0 or (dir_.dirs_hash or ''.join(dir_.dir_hashes) == '')

            # this dir is now complete
            self.store_dir(dir_)

            # propagate the dirs hash up
            if dir_.parent:  # i.e. not root dir
                all_hash = self.calc_all_hash(dir_.files_hash, dir_.dirs_hash)
                if not all_hash:
                    logger.debug('Empty overall hash for dir %s: %s', dir_.id, dir_.path_repr)
                self.update_dir_with_dir_hash(dir_.parent, all_hash)

        # if len(dir_.dir_hashes) == dir_.num_dirs:
        #     # ready to calc the dirs hash if needed ('' by default)
        #     if ''.join(dir_.dir_hashes) != '':  # at least one dir that is not empty
        #         if not dir_.dirs_hash:  # not yet set
        #             dir_.dirs_hash = calc_dirs_hash(dir_.dir_hashes)
        #
        #     if dir_.num_files == 0 or dir_.files_hash:
        #         # this dir is completed
        #         store_dir(dir_)
        #         # propagate up
        #         if dir_.parent:  # i.e. not root dir
        #             all_hash = calc_all_hash(dir_.files_hash, dir_.dirs_hash)
        #             if not all_hash:
        #                 logger.debug('Empty overall hash for dir %s: %s', dir_.id, dir_.path_repr)
        #             dir_.parent.dir_hashes.append(all_hash)
        #             update_dir(dir_.parent)

    def update_dir_with_dir_hash(self, dir_: Dir, dir_hash: str):
        assert len(dir_.dir_hashes) < dir_.num_dirs  # not all contained dirs yet processed
        dir_.dir_hashes.append(dir_hash)
        if len(dir_.dir_hashes) == dir_.num_dirs:
            # assert not dir_.dirs_hash or ''.join(dir_.dir_hashes) == ''
            dir_.dirs_hash = self.calc_dirs_hash(dir_.dir_hashes)
            self.update_dir(dir_)

    def update_dir_with_file_hash(self, dir_: Dir, file_hash: str):
        """Updates the dir's files hash if possible and if so, checks if the dir is complete."""

        assert len(dir_.file_hashes) < dir_.num_files  # not all contained files yet processed
        dir_.file_hashes.append(file_hash)
        if len(dir_.file_hashes) == dir_.num_files:
            dir_.files_hash = self.calc_files_hash(dir_.file_hashes)
            self.update_dir(dir_)

    def handle_file(self, file: File):
        """Process the file and update its containing dir(s) if possible."""

        self.store_file(file)
        self.update_dir_with_file_hash(file.parent, file.hash)

    def run(self, hashed_files: queue.Queue[File|object]) -> None:
        """Reads and processes items from the queue until it hits an end-of-input marker."""

        assert self.dirs_counter.value() == 0
        assert self.files_counter.value() == 0

        handled_files_counter = Counter()  # not access. from outside

        for file in self.pop(hashed_files):
            if not file.marks_empty_dir():
                self.handle_file(file)
                handled_files_counter.incr()
            else:
                # handle the empty dir the File obj links to
                self.update_dir(file.parent)

        num_files_processed = handled_files_counter.value()
        logger.info('Processed %d queued files', num_files_processed)

        num_dirs_stored = self.dirs_counter.value()
        num_files_stored = self.files_counter.value()
        logger.info('Stored %d files and %d directories',
                    num_files_stored, num_dirs_stored)
        assert num_files_stored == num_files_processed
