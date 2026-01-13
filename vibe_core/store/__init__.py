"""Persistence layer for vibe-agency"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xf2f9abda"  # GenesisByte: parampara % 37 == 0

from .sqlite_store import SQLiteStore

# Alias for compatibility with test expectations
ArtifactStore = SQLiteStore

__all__ = ["SQLiteStore", "ArtifactStore"]
