from __future__ import annotations

import logging
import queue

from meta import File


logger = logging.getLogger(__name__)


def store(file_queue: queue.Queue[File|object], sentinel: object):
    num_files_processed: int = 0

    while True:
        try:
            file = file_queue.get(timeout=1)
        except queue.Empty:
            continue

        if file is sentinel:
            logger.info('Received sentinel')
            file_queue.task_done()
            break

        assert isinstance(file, File)

        # for now no actual storage
        file_queue.task_done()
        num_files_processed += 1
        logger.debug('File %s has hash %s' % (file.id, file.hash[:8]))

    logger.info('Processed %s files' % num_files_processed)

