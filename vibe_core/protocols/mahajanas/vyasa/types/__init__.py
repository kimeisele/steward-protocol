"""
VYASA Types - Position 13 (MOKSHA Quarter, COMPILE_RECORD)
==========================================================

VYASA - The Compiler of the Vedas.
Types for records, lineage, ledger, and compliance.
"""

from vibe_core.protocols.mahajanas.vyasa.types.errors import (
    ErrorCategory,
    ErrorCode,
    StructuredError,
)

# Lazy imports to avoid circular dependencies
__all__ = [
    # errors.py
    "ErrorCategory",
    "ErrorCode",
    "StructuredError",
    # lineage.py
    "LineageBlock",
    "LineageChain",
    "LineageEventType",
    # ledger.py
    "InMemoryLedger",
    "SQLiteLedger",
    "ArchiveAttachment",
]


def __getattr__(name: str):
    """Lazy import for lineage and ledger to avoid circular dependencies."""
    if name in ("LineageBlock", "LineageChain", "LineageEventType"):
        from vibe_core.protocols.mahajanas.vyasa.types.lineage import (
            LineageBlock,
            LineageChain,
            LineageEventType,
        )
        return {"LineageBlock": LineageBlock, "LineageChain": LineageChain, "LineageEventType": LineageEventType}[name]
    if name in ("InMemoryLedger", "SQLiteLedger", "ArchiveAttachment"):
        from vibe_core.protocols.mahajanas.vyasa.types.ledger import (
            InMemoryLedger,
            SQLiteLedger,
            ArchiveAttachment,
        )
        return {"InMemoryLedger": InMemoryLedger, "SQLiteLedger": SQLiteLedger, "ArchiveAttachment": ArchiveAttachment}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
