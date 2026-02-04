from typing import Protocol, runtime_checkable, Literal, Iterator, Optional
from vibe_core.mahamantra.protocols._seed import (HARE_COUNT, QUARTERS)
from dataclasses import dataclass

@runtime_checkable
class MahaComputeProtocol(Protocol):
    """
    Protocol for MahaCompute: Unified Compute Analysis.
    
    Responsible for analyzing hardware alignment and data structure efficiency.
    """
    
    def analyze(
        self, 
        entries: int, 
        bytes_per_entry: int = HARE_COUNT, 
        access_pattern: Literal["uniform", "prefix", "sequential"] = "uniform"
    ) -> "DataAnalysis":
        """Analyze data structure for memory hierarchy fit."""
        ...
        
    def create_unit(
        self, 
        name: str, 
        simd_lanes: int, 
        cache_kb: int, 
        memory_levels: int = QUARTERS
    ) -> "ComputeUnit":
        """Create and evaluate a compute unit definition."""
        ...

@dataclass(frozen=True)
class DataAnalysis:
    """Analysis of data structure efficiency."""
    entries: int
    bytes_per_entry: int
    total_bytes: int
    optimal_depth: int
    memory_tier: str
    cache_hit_rate: float
    access_pattern: str
    fits_in_cache: bool
    lotus_capacity: int
    
    @property
    def efficiency_score(self) -> float: ...
    @property
    def verdict(self) -> str: ...

@dataclass(frozen=True)
class ComputeUnit:
    """Analysis of a hardware compute unit."""
    name: str
    simd_lanes: int
    cache_kb: int
    memory_levels: int
    
    @property
    def alignment(self) -> float: ...
    @property
    def is_unified(self) -> bool: ...
