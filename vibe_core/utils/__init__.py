"""
VIBE_CORE UTILS - Shared Utilities

Low-level utilities that provide guarantees:
- atomic_io: Crash-safe file operations (read + write)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xb68baebd"  # GenesisByte: parampara % 37 == 0

from .atomic_io import (
    atomic_write_json,
    atomic_write_text,
    atomic_write_yaml,
    safe_read_yaml,
)

__all__ = [
    "atomic_write_json",
    "atomic_write_text",
    "atomic_write_yaml",
    "safe_read_yaml",
]
