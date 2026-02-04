from typing import Protocol, runtime_checkable, Tuple, List
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA)
from dataclasses import dataclass

@runtime_checkable
class MahaBioProtocol(Protocol):
    """
    Protocol for MahaBio: O(1) DNA k-mer Indexing.
    
    Matches 4-base DNA structure to 4-Quarter Mahamantra.
    """
    
    def index_kmer(self, kmer: str, position: int = -KSETRAJNA) -> bool:
        """Index a single k-mer."""
        ...
        
    def index_sequence(self, sequence: str) -> int:
        """Index all k-mers in sequence."""
        ...
        
    def count(self, kmer: str) -> int:
        """Get k-mer count O(1)."""
        ...
        
    def find(self, kmer: str) -> Tuple[int, ...]:
        """Find all positions of k-mer O(1)."""
        ...
        
    def query(self, kmer: str) -> "KmerResult":
        """Full query with count and positions."""
        ...
        
    def prefix_match(self, prefix: str) -> List["KmerResult"]:
        """Find matches by prefix."""
        ...
        
    def stats(self) -> "IndexStats":
        """Get index statistics."""
        ...

@dataclass(frozen=True)
class KmerResult:
    """Result of k-mer query."""
    kmer: str
    key: int
    count: int
    positions: Tuple[int, ...]

@dataclass(frozen=True)
class IndexStats:
    """Statistics for k-mer index."""
    k: int
    key_space: int
    unique_kmers: int
    total_indexed: int
    sequence_length: int
