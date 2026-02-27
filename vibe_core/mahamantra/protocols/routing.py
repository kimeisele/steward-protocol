from dataclasses import dataclass
from typing import Dict, Generic, Iterator, Optional, Protocol, Tuple, TypeVar, runtime_checkable

V = TypeVar("V", covariant=True)


@runtime_checkable
class MahaRoutingProtocol(Protocol, Generic[V]):
    """
    Protocol for MahaRouting (HolographicRouter).

    O(1) Key-Value Routing using Lotus Tree.
    """

    def insert(self, key: int, value: object) -> None:
        """Insert key-value pair."""
        ...

    def get(self, key: int) -> Optional[V]:
        """Lookup value for key."""
        ...

    def range_query(self, start: int, end: int) -> "RangeResult[V]":
        """Get entries in range."""
        ...

    def prefix_query(self, prefix: int, prefix_bits: int) -> "RangeResult[V]":
        """Get entries matching prefix."""
        ...

    def stats(self) -> Dict[str, object]:
        """Get router statistics."""
        ...

    def keys(self) -> Iterator[int]: ...

    def items(self) -> Iterator[Tuple[int, V]]: ...

    def __getitem__(self, key: int) -> V: ...

    def __setitem__(self, key: int, value: object) -> None: ...

    def __contains__(self, key: int) -> bool: ...

    def __len__(self) -> int: ...


@dataclass(frozen=True)
class RouteEntry(Generic[V]):
    """Single routing entry."""

    key: int
    value: V
    depth: int


@dataclass(frozen=True)
class RangeResult(Generic[V]):
    """Result of range query."""

    entries: Tuple[RouteEntry[V], ...]
    count: int
    levels_visited: int


from dataclasses import dataclass

from vibe_core.mahamantra.protocols.types import PhoneticClass


@runtime_checkable
class PhoneticRoutingProtocol(Protocol):
    """
    Protocol for Phonetic Routing (The True Algorithm).

    Maps Mahamantra positions -> RAMA Grid Coordinates -> Phonetic Classes.
    """

    def route_to_rama(self, position: int) -> int:
        """
        Route a Mahamantra position (1-16) to a RAMA Grid coordinate (0-48).
        Uses the Krishna Router (Prime 17).
        """
        ...

    def get_phoneme(self, rama_coord: int) -> str:
        """
        Get the string phoneme for a RAMA coordinate.
        """
        ...

    def get_phonetic_class(self, rama_coord: int) -> PhoneticClass:
        """
        Get the PhoneticClass (Verification Type) for a RAMA coordinate.
        """
        ...
