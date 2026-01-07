from typing import Optional, Protocol, runtime_checkable

from .types import MemoryValue


@runtime_checkable
class StoreRecallProtocol(Protocol):
    """
    Atomic protocol for memory storage and retrieval.
    Abstracts different memory backends (vector, graph, key-value).
    """

    def store(self, key: str, value: MemoryValue) -> None:
        """Store value in memory."""
        ...

    def recall(self, key: str) -> Optional[MemoryValue]:
        """Recall value from memory."""
        ...

    def forget(self, key: str) -> bool:
        """
        Forget (delete or tombstone) a value.
        Returns True if successful/found, False otherwise.
        """
        ...
