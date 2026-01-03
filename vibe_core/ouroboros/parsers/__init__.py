"""
Violation Source Parsers - VEDA-4 Compliant Discovery.

Each parser knows how to extract ViolationRecords from a specific file format.
Parsers are auto-discovered by ViolationParserLoader.
"""

from vibe_core.ouroboros.parsers.base import ViolationSourceParser

__all__ = ["ViolationSourceParser"]
