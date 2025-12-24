"""Async logging to prevent I/O blocking."""
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import os

_log_queue = Queue()
_listener = None

def setup_async_logging():
    global _listener
    
    # Ensure log directory exists
    log_dir = Path(".vibe/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    root = logging.getLogger()
    handler = QueueHandler(_log_queue)
    root.addHandler(handler)

    log_file = log_dir / "system.log"
    file_handler = logging.FileHandler(str(log_file))
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    
    _listener = QueueListener(_log_queue, file_handler)
    _listener.start()

def shutdown_async_logging():
    if _listener:
        _listener.stop()

# Support for Path in this context
from pathlib import Path