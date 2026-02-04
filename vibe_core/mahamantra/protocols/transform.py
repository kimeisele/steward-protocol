from typing import Protocol, runtime_checkable, List, Tuple, Dict, Optional
from vibe_core.mahamantra.protocols._seed import (MAHA_QUANTUM)
from dataclasses import dataclass, field

@runtime_checkable
class MahaTransformProtocol(Protocol):
    """
    Protocol for MahaTransform: Deterministic 16-Step Transformation.
    """
    
    def compute(self, seed: int) -> "TransformResult":
        """Apply 16-step transformation."""
        ...
        
    def find_attractor(self, seed: int, max_iterations: int = MAHA_QUANTUM) -> "AttractorResult":
        """Iterate until stable state reached."""
        ...
        
    def compute_batch(self, seeds: List[int]) -> "BatchResult":
        """Transform multiple seeds."""
        ...
        
    def analyze_distribution(self, sample_size: int = 1000) -> Dict[str, object]:
        """Analyze output distribution."""
        ...

@dataclass(frozen=True)
class TransformResult:
    """Result of a single transformation."""
    seed: int
    value: int
    mod_space: int
    iterations: int
    metrics: Dict[str, object] = field(default_factory=dict)

@dataclass(frozen=True)
class AttractorResult:
    """Result of attractor discovery."""
    seed: int
    stable_value: int
    cycles_to_converge: int
    is_fixed_point: bool
    trajectory: Tuple[int, ...]

@dataclass(frozen=True)
class BatchResult:
    """Result of batch transformation."""
    results: Tuple[TransformResult, ...]
    unique_outputs: int
    entropy: float
