"""
VIBE_CORE UTILS - Shared Utilities

Low-level utilities that provide guarantees:
- atomic_io: Crash-safe file operations
"""

from .atomic_io import atomic_write_json, atomic_write_text

__all__ = ["atomic_write_json", "atomic_write_text"]
