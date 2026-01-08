"""
STORE/RECALL PROTOCOL - Layer 2 (Memory/Smriti)

GAD-000 COMPLIANT:
- Discoverability: Clear CRUD-like interface
- Observability: get_memory_stats() ← RED-005 FIX
- Parseability: Returns structured MemoryValue objects
- Composability: Can pipe inference output to storage
- Idempotency: 'store' upserts, 'forget' is idempotent
- Recoverability: Persistence layer ensures data survival
"""

from dataclasses import dataclass
from typing import Iterator, Optional, Protocol, runtime_checkable

from .types import MemoryValue, SovereignContext


@dataclass
class MemoryStats:
    """GAD-000 Observability: Memory subsystem statistics."""

    total_keys: int
    total_bytes: int
    oldest_key_age_seconds: float
    newest_key_age_seconds: float
    hit_rate: float = 0.0  # Cache hit rate if applicable


@runtime_checkable
class StoreRecallProtocol(Protocol):
    """
    Atomic protocol for memory storage and retrieval (Mnemosyne/Smriti).

    GAD-000: Observability via get_memory_stats() + list_keys().
    """

    def store(
        self,
        key: str,
        value: MemoryValue,
        context: Optional[SovereignContext] = None,
    ) -> None:
        """
        Store value in memory.

        Args:
            key: Address/ID.
            value: Content + Metadata.
            context: (Required) Who is remembering this?
        """
        ...

    def recall(
        self,
        key: str,
        context: Optional[SovereignContext] = None,
    ) -> Optional[MemoryValue]:
        """
        Recall value from memory.

        Args:
            key: Address/ID.
            context: (Optional) Who is asking? (Access Control)
        """
        ...

    def forget(
        self,
        key: str,
        context: Optional[SovereignContext] = None,
    ) -> bool:
        """
        Forget (delete or tombstone) a value.

        Args:
            key: Address/ID.
            context: (Required) Who is authorizing the forgetting?
        """
        ...

    def get_memory_stats(self) -> MemoryStats:
        """
        GAD-000 Observability: Get memory subsystem statistics.

        Returns:
            MemoryStats with key count, size, ages, hit rate.
        """
        ...

    def list_keys(
        self,
        prefix: Optional[str] = None,
        context: Optional[SovereignContext] = None,
    ) -> Iterator[str]:
        """
        GAD-000 Observability + Discoverability: List all keys.

        Args:
            prefix: Optional filter by key prefix.
            context: Who is listing? (Access Control)

        Returns:
            Iterator of key strings (streaming for large datasets).
        """
        ...
