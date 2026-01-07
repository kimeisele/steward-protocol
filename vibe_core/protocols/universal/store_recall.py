from typing import Optional, Protocol, runtime_checkable

from .types import MemoryValue, SovereignContext


@runtime_checkable
class StoreRecallProtocol(Protocol):
    """
    Atomic protocol for memory storage and retrieval (Mnemosyne/Smriti).

    GAD-000 COMPLIANCE:
    - Discoverability: Clear CRUD-like interface.
    - Observability: Operations can be inspected via memory dumps.
    - Parseability: Returns structured MemoryValue objects.
    - Composability: Can pipe inference output to storage.
    - Idempotency: 'store' upserts, 'forget' is idempotent.
    - Recoverability: Persistence layer ensures data survival.
    """

    def store(self, key: str, value: MemoryValue, context: Optional[SovereignContext] = None) -> None:
        """
        Store value in memory.
        Args:
            key: Address/ID.
            value: Content + Metadata.
            context: (Required) Who is remembering this?
        """
        ...

    def recall(self, key: str, context: Optional[SovereignContext] = None) -> Optional[MemoryValue]:
        """
        Recall value from memory.
        Args:
            key: Address/ID.
            context: (Optional) Who is asking? (Access Control)
        """
        ...

    def forget(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        """
        Forget (delete or tombstone) a value.
        Args:
            key: Address/ID.
            context: (Required) Who is authorizing the forgetting?
        """
        ...
