from dataclasses import dataclass
from typing import Generic, List, Optional, Protocol, TypeVar, runtime_checkable

from vibe_core.mahamantra.protocols._seed import WORDS

T_Handler = TypeVar("T_Handler", covariant=True)


@runtime_checkable
class MahaAttentionProtocol(Protocol, Generic[T_Handler]):
    """
    Protocol for MahaAttention: O(1) Intent Resolution.

    Replaces linear scans/vector search with O(1) Lotus lookup.
    """

    def memorize(self, intent: str, handler: T_Handler) -> int:
        """
        Register intent handler mapping.

        Args:
            intent: The intent string.
            handler: The handler to execute.

        Returns:
            Address hash.
        """
        ...

    def attend(self, query: str) -> "AttentionResult[T_Handler]":
        """Resolve query to handler in O(1)."""
        ...

    def attend_batch(self, queries: List[str]) -> List["AttentionResult[T_Handler]"]:
        """Resolve multiple queries."""
        ...

    def attend_fuzzy(self, query: str, radius: int = WORDS) -> List["AttentionResult[T_Handler]"]:
        """Fuzzy match within radius."""
        ...

    def stats(self) -> "AttentionStats":
        """Get mechanism statistics."""
        ...


@dataclass(frozen=True)
class AttentionResult(Generic[T_Handler]):
    """Result of attention query."""

    query: str
    address: int
    handler: Optional[T_Handler]
    found: bool
    ops_saved: int


@dataclass(frozen=True)
class AttentionStats:
    """Statistics for attention mechanism."""

    mechanism: str
    address_space: int
    registered_intents: int
    queries_resolved: int
    cache_hits: int
    estimated_ops_saved: int
