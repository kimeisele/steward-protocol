"""
READ/WRITE PROTOCOL - The Record/Akasha (Layer 1)
==================================================

HARDENED (Phase 27):
- NO ANONYMOUS ACCESS.
- Context is MANDATORY.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x48e836a6"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable
from .types import ReadResult, SovereignContext


@runtime_checkable
class ReadWriteProtocol(Protocol):
    """
    Atomic protocol for State/Config access (The Record/Akasha).

    GAD-000 COMPLIANCE:
    - Discoverability: Type-safe 'ReadResult' envelope.
    - Observability: Provenance tracking via 'ReadResult.writer'.
    - Parseability: Standardized exceptions (KeyNotFoundError).
    - Composability: Can pipe ReadResult into specialized logic.
    - Idempotency: Read is side-effect free; Write is idempotent.
    - Recoverability: Exceptions defined for graceful handling.

    HARDENED (Phase 27):
    - NO ANONYMOUS ACCESS.
    - Context is MANDATORY.
    """

    def read(self, key: str, context: SovereignContext) -> ReadResult:
        """
        Read value by key.
        Args:
            context: (Required) Who is reading?
        Raises:
            KeyNotFoundError: If key does not exist.
            AccessDeniedError: If context lacks permission.
        """
        ...

    def write(self, key: str, value: object, context: SovereignContext) -> None:
        """
        Write value by key.
        Args:
            context: (Required) Who is writing?
            value: (Required) The strict object (Metadata/Struct), not Any.
        Raises:
            AccessDeniedError: If signature invalid or permission denied.
        """
        ...

    def exists(self, key: str, context: SovereignContext) -> bool:
        """
        Check if key exists.
        Even checking existence requires permission (to prevent enumeration attacks).
        """
        ...
