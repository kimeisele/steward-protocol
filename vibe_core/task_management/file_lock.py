"""File-based locking for concurrent access."""

import json
import os
import time
from pathlib import Path
from typing import Optional


class FileLock:
    """Simple file-based lock for preventing concurrent writes."""

    def __init__(self, lock_path: Path, timeout: float = 10.0):
        """
        Initialize file lock.

        Args:
            lock_path: Path to lock file
            timeout: Lock acquisition timeout in seconds
        """
        self.lock_path = Path(lock_path)
        self.timeout = timeout
        self.lock_data = {"pid": os.getpid(), "timestamp": time.time()}

    def acquire(self) -> bool:
        """
        Acquire the lock.

        Returns:
            True if lock acquired, False if timeout
        """
        start_time = time.time()

        while True:
            try:
                # Try to create lock file exclusively
                self.lock_path.touch(exist_ok=False)
                self.lock_path.write_text(json.dumps(self.lock_data))
                return True
            except FileExistsError:
                # Lock exists, check if it's stale
                elapsed = time.time() - start_time

                if elapsed > self.timeout:
                    # Lock is stale, force acquire
                    try:
                        self.lock_path.unlink()
                        self.lock_path.write_text(json.dumps(self.lock_data))
                        return True
                    except:
                        return False

                # Wait a bit and retry
                time.sleep(0.1)

    def release(self):
        """Release the lock."""
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except:
            pass

    def __enter__(self):
        """Context manager entry."""
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock within {self.timeout}s")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
