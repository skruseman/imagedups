from __future__ import annotations

import logging
import queue
import threading
import time

from meta import File


logger = logging.getLogger(__name__)

SLEEP_SECS = 0.25


def monitor_queues(fth_queue: queue.Queue[File | object],
                   fh_queue: queue.Queue[File | object],
                   stop_event: threading.Event):
    max_hash_queue_size: int = 0
    max_hashed_files_queue_size: int = 0
    num_samples: int = 0

    while not stop_event.is_set():
        sz: int = fth_queue.qsize()
        max_hash_queue_size = max(max_hash_queue_size, sz)
        sz = fh_queue.qsize()
        max_hashed_files_queue_size = max(max_hashed_files_queue_size, sz)
        num_samples += 1
        time.sleep(SLEEP_SECS)

    logger.info('Max hash queue size %s (%s samples)' % (max_hash_queue_size, num_samples))
    logger.info('Max hashed files queue size %s (%s samples)' % (max_hashed_files_queue_size, num_samples))
