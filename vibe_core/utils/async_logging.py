"""Async logging to prevent I/O blocking.

OPUS-304: Non-blocking log writes using QueueHandler.
Prevents I/O from blocking kernel pulse.

Usage:
    from vibe_core.utils.async_logging import setup_async_logging, shutdown_async_logging

    # At boot
    setup_async_logging()

    # At shutdown
    shutdown_async_logging()
"""

import logging
import os
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from queue import Queue

_log_queue = Queue()
_listener = None


def setup_async_logging():
    """Setup async logging with queue-based handler."""
    global _listener

    # Ensure log directory exists
    log_dir = Path(".vibe/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    handler = QueueHandler(_log_queue)
    root.addHandler(handler)

    log_file = log_dir / "system.log"
    file_handler = logging.FileHandler(str(log_file))
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    _listener = QueueListener(_log_queue, file_handler)
    _listener.start()


def shutdown_async_logging():
    """Shutdown async logging listener.

    OPUS-305: Prevent test timeouts by:
    1. Sending sentinel (None) to unblock listener thread
    2. Using stop() which processes remaining items
    """
    global _listener
    if _listener:
        # Send sentinel to unblock the listener's queue.get()
        # QueueListener checks for None as the stop signal
        _log_queue.put_nowait(None)

        # Stop listener (this will now complete without blocking)
        _listener.stop()
        _listener = None
