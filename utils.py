from __future__ import annotations

import logging
import threading

# marker: add to a queue to signal end of input
SENTINEL = object()

logger = logging.getLogger(__name__)


class Counter:
    """Thread-safe counter, starting at 0."""

    def __init__(self):
        self.global_value: int = 0
        self._lock = threading.Lock()  # protect global value
        self.local = threading.local()  # thread-local value

    def incr(self, n = 1) -> None:
        """Cache thread-local updates, to be flushed with self.flush()"""
        if not hasattr(self.local, 'value'):
            self.local.value = 0
        self.local.value += n

    def _flush_unsafe(self) -> None:
        """Assumes lock is held; use locally only."""
        if hasattr(self.local, 'value'):
            self.global_value += self.local.value
        self.local.value = 0

    def flush(self) -> None:
        with self._lock:
            self._flush_unsafe()

    def value(self) -> int:
        # Does not include local changes of other threads
        with self._lock:
            self._flush_unsafe()
            return self.global_value

    def get_approx(self) -> int:
        return self.global_value + self.local.value
