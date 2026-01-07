from typing import Any, Optional, Protocol, runtime_checkable

from .types import SovereignContext


@runtime_checkable
class ReadWriteProtocol(Protocol):
    """
    Atomic protocol for read/write operations (The Field/Ksetra).

    GAD-000 COMPLIANCE:
    - Discoverability: Methods have clear types and docstrings.
    - Observability: Operations interact with observable state.
    - Parseability: Returns Typed objects or raises defined exceptions.
    - Composability: Atomic verbs chainable via orchestration.
    - Idempotency: 'read' and 'exists' are idempotent. 'write' should be.
    - Recoverability: State can be rebuilt from Ledger.
    """

    def read(self, key: str, context: Optional[SovereignContext] = None) -> Any:
        """
        Read value by key.
        Args:
            key: The address to read from.
            context: (Optional) Identity of the reader.
        """
        ...

    def write(self, key: str, value: Any, context: Optional[SovereignContext] = None) -> None:
        """
        Write value by key.
        Args:
            key: The address to write to.
            value: The data to store.
            context: (Required for Anti-Mayavad) Identity of the writer.
        """
        ...

    def exists(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        """
        Check if key exists.
        Args:
            key: The address to check.
            context: (Optional) Identity of the checker.
        """
        ...
