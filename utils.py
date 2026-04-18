from __future__ import annotations

import threading
import logging

# marker: added to a queue signals end of input
SENTINEL = object()

logger = logging.getLogger(__name__)


class Counter:
    """Thread safe counter, starting at 0."""

    def __init__(self):
        self.global_value: int = 0
        self._lock = threading.Lock()
        self.local = threading.local()

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

    def get(self) -> int:
        with self._lock:
            self._flush_unsafe()
            return self.global_value

    def get_approx(self) -> int:
        return self.global_value + self.local.value
