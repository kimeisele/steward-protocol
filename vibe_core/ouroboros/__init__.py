"""
OUROBOROS - The Self-Healing Loop

"The snake that eats its own tail"

This module implements the COMPLETE feedback loop:
1. SENSE: Detect violations from multiple sources (local, CI/CD, runtime)
2. VERIFY: Validate claims against current code (SATYA layer)
3. REMEMBER: Persist VERIFIED violations in the Knowledge Graph
4. HEAL: Apply remedies via Shuddhi
5. LEARN: Identify patterns and training gaps

The Ouroboros loop is the immune system of the codebase.

VEDA-4 Architecture:
    - ViolationParserLoader: Discovers parser implementations (SHABDA → KARMA)
    - ViolationSourceLoader: Discovers violation source files
    - SatyaValidator: Verifies claims against current code (Smriti → Shruti)
    - ViolationIngester: Ingests violations into Knowledge Graph

SATYA (Truth) Layer:
    - Distinguishes Smriti (memory/reports) from Shruti (truth/code)
    - Discards Maya (illusion/false positives) before ingestion
    - Tracks verification status: unverified | verified | stale | maya

GAD-000 Compliance:
    - Discoverability: Loaders expose status() and list methods
    - Observability: All parsers, sources, and verification are queryable
    - Composability: Loaders and validators work together seamlessly
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
from .verification import (
    SatyaValidator,
    VerificationResult,
    VerificationStatus,
    VerifiedViolation,
    ViolationOrigin,
    filter_maya,
    verify_violations,
)

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
    # SATYA Verification
    "SatyaValidator",
    "VerificationStatus",
    "VerificationResult",
    "VerifiedViolation",
    "ViolationOrigin",
    "verify_violations",
    "filter_maya",
]
