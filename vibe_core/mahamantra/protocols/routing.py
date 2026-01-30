from typing import Protocol, runtime_checkable, TypeVar, Generic, Tuple, Optional, Iterator, Dict, Any

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
