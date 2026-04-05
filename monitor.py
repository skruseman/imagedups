from __future__ import annotations

import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)


def monitor_hash_queue(fth_queue: queue.Queue[File|object], stop_event: threading.Event):
    max_hash_queue_size: int = 0
    num_samples: int = 0

    while not stop_event.is_set():
        sz: int = fth_queue.qsize()
        max_hash_queue_size = max(max_hash_queue_size, sz)
        num_samples += 1
        time.sleep(0.42)

    logger.info('Max hash queue size %s (%s samples)' % (max_hash_queue_size, num_samples))
