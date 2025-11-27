"""Persistence layer for vibe-agency"""

from .sqlite_store import SQLiteStore

# Alias for compatibility with test expectations
ArtifactStore = SQLiteStore

__all__ = ["SQLiteStore", "ArtifactStore"]
