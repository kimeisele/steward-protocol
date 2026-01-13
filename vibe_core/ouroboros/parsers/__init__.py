"""
Violation Source Parsers - VEDA-4 Compliant Discovery.

Each parser knows how to extract ViolationRecords from a specific file format.
Parsers are auto-discovered by ViolationParserLoader.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0xa87d5b3a"  # GenesisByte: parampara % 37 == 0

from vibe_core.ouroboros.parsers.base import ViolationSourceParser

__all__ = ["ViolationSourceParser"]
