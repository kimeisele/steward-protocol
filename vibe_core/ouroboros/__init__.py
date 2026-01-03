"""
OUROBOROS - The Self-Healing Loop

"The snake that eats its own tail"

This module implements the feedback loop that enables the system to:
1. SENSE: Detect violations from multiple sources (local, CI/CD, runtime)
2. REMEMBER: Persist violations in the Knowledge Graph
3. LEARN: Identify patterns and training gaps
4. HEAL: Apply remedies via Shuddhi
5. VERIFY: Confirm fixes worked

The Ouroboros loop is the immune system of the codebase.

VEDA-4 Architecture:
    - ViolationParserLoader: Discovers parser implementations (SHABDA → KARMA)
    - ViolationSourceLoader: Discovers violation source files
    - ViolationIngester: Ingests violations into Knowledge Graph

GAD-000 Compliance:
    - Discoverability: Loaders expose status() and list methods
    - Observability: All parsers and sources are queryable
    - Composability: Loaders work together seamlessly
"""

from .ingestion import ViolationIngester, ViolationRecord, ViolationSource
from .parser_loader import (
    ViolationParserLoader,
    discover_parsers,
    get_parser_for,
    get_parser_loader,
)
from .source_loader import (
    ViolationSourceFile,
    ViolationSourceLoader,
    discover_sources,
    get_source_loader,
)
from .sync import CISyncService

__all__ = [
    # Core
    "ViolationIngester",
    "ViolationRecord",
    "ViolationSource",
    "CISyncService",
    # Parser Discovery
    "ViolationParserLoader",
    "get_parser_loader",
    "discover_parsers",
    "get_parser_for",
    # Source Discovery
    "ViolationSourceLoader",
    "ViolationSourceFile",
    "get_source_loader",
    "discover_sources",
]
