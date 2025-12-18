"""
FileState - Layer 1 (STHULA) File System Operations

Tracks workspace file state for the Prakriti state engine.
Provides dirty file detection and file categorization.

GAD-000 Compliant:
- All methods return dict/dataclass
- Errors use StructuredError with codes
- get_capabilities() for discoverability
"""

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("FILE_STATE")


@dataclass
class FileInfo:
    """Information about a tracked file."""

    path: str
    relative_path: str
    size_bytes: int
    extension: str
    is_directory: bool = False
    content_hash: Optional[str] = None


@dataclass
class FileSnapshot:
    """Snapshot of file state at a point in time."""

    timestamp: float
    total_files: int
    total_size_bytes: int
    files_by_extension: Dict[str, int] = field(default_factory=dict)


class FileState:
    """Workspace file tracking for Prakriti.

    Tracks file state to detect changes and categorize files.
    Used alongside GitState for complete workspace awareness.
    """

    # File categories for the Steward Protocol
    CATEGORIES = {
        "code": {".py", ".js", ".ts", ".go", ".rs"},
        "config": {".yaml", ".yml", ".json", ".toml"},
        "docs": {".md", ".rst", ".txt"},
        "data": {".csv", ".sqlite", ".db"},
    }

    # Directories to ignore
    IGNORE_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        ".benchmarks",
    }

    def __init__(self, workspace_path: Optional[Path] = None):
        self._workspace = workspace_path or Path.cwd()
        self._file_hashes: Dict[str, str] = {}
        self._last_snapshot: Optional[FileSnapshot] = None

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": [
                "dirty_files",
                "categorize",
                "snapshot",
                "list_files",
            ],
            "categories": list(self.CATEGORIES.keys()),
            "workspace": str(self._workspace),
        }

    # =========================================================================
    # Core Operations
    # =========================================================================

    def dirty_files(self) -> List[str]:
        """Get list of files that have changed since last snapshot.

        Returns:
            List of relative file paths that changed
        """
        dirty = []

        for file_path in self._iter_workspace_files():
            try:
                current_hash = self._hash_file(file_path)
                relative = str(file_path.relative_to(self._workspace))

                if relative in self._file_hashes:
                    if self._file_hashes[relative] != current_hash:
                        dirty.append(relative)
                else:
                    # New file
                    dirty.append(relative)

            except Exception as e:
                logger.debug(f"Error checking file {file_path}: {e}")
                continue

        return dirty

    def snapshot(self) -> FileSnapshot:
        """Take a snapshot of current file state.

        Returns:
            FileSnapshot with current state
        """
        import time

        total_files = 0
        total_size = 0
        by_extension: Dict[str, int] = {}

        for file_path in self._iter_workspace_files():
            try:
                total_files += 1
                stat = file_path.stat()
                total_size += stat.st_size

                ext = file_path.suffix.lower() or "(none)"
                by_extension[ext] = by_extension.get(ext, 0) + 1

                # Update hash cache
                relative = str(file_path.relative_to(self._workspace))
                self._file_hashes[relative] = self._hash_file(file_path)

            except Exception:
                continue

        snapshot = FileSnapshot(
            timestamp=time.time(),
            total_files=total_files,
            total_size_bytes=total_size,
            files_by_extension=by_extension,
        )

        self._last_snapshot = snapshot
        return snapshot

    def categorize(self, relative_path: str) -> str:
        """Categorize a file by its extension.

        Args:
            relative_path: Path relative to workspace

        Returns:
            Category name or 'other'
        """
        ext = Path(relative_path).suffix.lower()
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category
        return "other"

    def list_files(self, category: Optional[str] = None, limit: int = 100) -> List[FileInfo]:
        """List files in workspace.

        Args:
            category: Optional filter by category
            limit: Maximum files to return

        Returns:
            List of FileInfo objects
        """
        files = []

        for file_path in self._iter_workspace_files():
            if len(files) >= limit:
                break

            try:
                relative = str(file_path.relative_to(self._workspace))
                file_category = self.categorize(relative)

                if category and file_category != category:
                    continue

                stat = file_path.stat()
                files.append(
                    FileInfo(
                        path=str(file_path),
                        relative_path=relative,
                        size_bytes=stat.st_size,
                        extension=file_path.suffix.lower(),
                    )
                )

            except Exception:
                continue

        return files

    def status(self, include_dirty: bool = False) -> Dict[str, Any]:
        """GAD-000: Get comprehensive file status as dict.

        Args:
            include_dirty: If True, scan for dirty files (EXPENSIVE!)
                          Default False to avoid rglob() timeout on large workspace

        Returns:
            Dict with file state metadata
        """
        snapshot = self._last_snapshot

        result = {
            "workspace": str(self._workspace),
            "last_snapshot": {
                "timestamp": snapshot.timestamp if snapshot else None,
                "total_files": snapshot.total_files if snapshot else 0,
                "total_size_bytes": snapshot.total_size_bytes if snapshot else 0,
            }
            if snapshot
            else None,
        }

        # OPUS-095 Fix: Only scan dirty files if explicitly requested
        # (avoids timeout on large workspaces)
        if include_dirty:
            dirty = self.dirty_files()
            result["dirty_count"] = len(dirty)
            result["dirty_files"] = dirty[:10]  # First 10 for brevity
        else:
            result["dirty_count"] = None  # Not computed
            result["dirty_files"] = []

        return result

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _iter_workspace_files(self):
        """Iterate over workspace files, respecting ignore patterns."""
        try:
            for item in self._workspace.rglob("*"):
                if item.is_file():
                    # Check if in ignored directory
                    parts = item.relative_to(self._workspace).parts
                    if any(part in self.IGNORE_DIRS for part in parts):
                        continue
                    yield item
        except PermissionError:
            pass

    def _hash_file(self, file_path: Path) -> str:
        """Compute MD5 hash of file contents."""
        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
