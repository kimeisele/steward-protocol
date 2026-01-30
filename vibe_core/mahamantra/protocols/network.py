from typing import Protocol, runtime_checkable, List, Optional, Tuple
from dataclasses import dataclass

@runtime_checkable
class MahaNetworkProtocol(Protocol):
    """
    Protocol for MahaNetwork: O(1) IP Routing.
    
    Uses 8-level Lotus Tree for O(1) Longest Prefix Match.
    """
    
    def insert(self, prefix: str, prefix_len: int, next_hop: str) -> None:
        """Insert a route."""
        ...
        
    def insert_cidr(self, cidr: str, next_hop: str) -> None:
        """Insert route using CIDR notation."""
        ...
        
    def lookup(self, ip: str) -> Optional[str]:
        """Find longest prefix match O(1)."""
        ...
        
    def lookup_int(self, ip_int: int) -> Optional[str]:
        """Fast lookup by integer."""
        ...
        
    def query(self, ip: str) -> "RouteResult":
        """Full query with metadata."""
        ...
        
    def insert_batch(self, routes: List[Tuple[str, int, str]]) -> int:
        """Batch insert."""
        ...
        
    def lookup_batch(self, ips: List[str]) -> List[Optional[str]]:
        """Batch lookup."""
        ...
        
    def stats(self) -> "RouterStats":
        """Get router statistics."""
        ...

@dataclass(frozen=True)
class RouteResult:
    """Result of a route lookup."""
    ip: str
    ip_int: int
    next_hop: Optional[str]
    matched_prefix: Optional[str]
    matched_prefix_len: int
    ops: int

@dataclass(frozen=True)
class RouterStats:
    """Statistics for the router."""
    routes: int
    levels: int
    bits_per_level: int
    max_capacity: str
