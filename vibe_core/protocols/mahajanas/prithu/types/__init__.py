"""
PRITHU Types - Position 4 (DHARMA Quarter, ASSERT_TRUTH)
========================================================

PRITHU - The Compiler of the Vedas.
Types for records, lineage, ledger, and compliance.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0xa3e52f02"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.prithu.types.errors import (
    ErrorCategory,
    ErrorCode,
    StructuredError,
    kernel_fault,
)

# Lazy imports to avoid circular dependencies
__all__ = [
    # errors.py
    "ErrorCategory",
    "ErrorCode",
    "StructuredError",
    "kernel_fault",
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
        from vibe_core.protocols.mahajanas.prithu.types.lineage import (
            LineageBlock,
            LineageChain,
            LineageEventType,
        )

        return {"LineageBlock": LineageBlock, "LineageChain": LineageChain, "LineageEventType": LineageEventType}[name]
    if name in ("InMemoryLedger", "SQLiteLedger", "ArchiveAttachment"):
        from vibe_core.protocols.mahajanas.prithu.types.ledger import (
            ArchiveAttachment,
            InMemoryLedger,
            SQLiteLedger,
        )

        return {"InMemoryLedger": InMemoryLedger, "SQLiteLedger": SQLiteLedger, "ArchiveAttachment": ArchiveAttachment}[
            name
        ]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
