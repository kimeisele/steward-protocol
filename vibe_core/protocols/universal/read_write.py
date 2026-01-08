from typing import Optional, Protocol, runtime_checkable

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
    """

    def read(self, key: str, context: Optional[SovereignContext] = None) -> ReadResult:
        """
        Read value by key.
        Returns ENVELOPE (Value + Provenance).

        Raises:
            KeyNotFoundError: If key does not exist.
            AccessDeniedError: If context lacks permission.
        """
        ...

    def write(self, key: str, value: object, context: Optional[SovereignContext] = None) -> None:
        """
        Write value by key.
        Args:
            context: (Required) Who is writing?

        Raises:
            AccessDeniedError: If signature invalid or permission denied.
        """
        ...

    def exists(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        """Check if key exists."""
        ...
