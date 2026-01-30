from typing import Protocol, runtime_checkable, Any, Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Forward reference for simplicity if needed, but we can define Enums here or assume they are imported.
# For strictness, I will define the necessary Enums or use placeholders if they are cross-module.
# Reading the adapter, `Quarter` and `Sampradaya` are from `substrate.mahajana`.
# I will type hint assuming they are available or use valid substitutes.
# To be safe and self-contained in protocol (or assume imports), I will use 'object' for external enums 
# or strictly import them if I knew the path was safe from circular deps. 
# Protocol files should ideally be independent. I'll stick to 'Any' for external Enums if I can't import, 
# BUT the user banned 'Any'. 
# Solution: I will defining the Protocol to accept the specific Enum types if I can import them, 
# or define local Protocol-compatible Enums if possible.
# Better: Import the Enums. They are in `vibe_core.mahamantra.substrate.mahajana`.

from vibe_core.mahamantra.substrate.mahajana import Quarter, Sampradaya

@runtime_checkable
class MahaPipelineProtocol(Protocol):
    """
    Protocol for MahaPipeline: The 4-Phase Architecture.
    
    Order: GENESIS -> DHARMA -> KARMA -> MOKSHA.
    """
    
    def genesis(self, value: object) -> "GenesisResult":
        """Phase 1: Determine intent."""
        ...
        
    def dharma(self, value: int) -> "DharmaResult":
        """Phase 2: Transform."""
        ...
        
    def karma(self, value: int, payload: Optional[object] = None) -> "KarmaResult":
        """Phase 3: Route/Action."""
        ...
        
    def moksha(self, value: int) -> "MokshaResult":
        """Phase 4: Complete/Release."""
        ...
        
    def execute(self, value: object) -> "PipelineResult":
        """Execute full pipeline."""
        ...
        
    def reset(self) -> None:
        """Reset state."""
        ...
        
    def get_phase_spec(self, quarter: Quarter) -> "PhaseSpec":
        """Get specification for a phase."""
        ...

    def describe(self) -> Dict[str, object]:
        """Describe pipeline structure."""
        ...

@dataclass(frozen=True)
class PhaseSpec:
    """Specification for a pipeline phase."""
    quarter: Quarter
    sampradaya: Sampradaya
    sounds: str
    positions: Tuple[int, ...]
    function: str
    adapter_name: str

@dataclass(frozen=True)
class GenesisResult:
    """Result of Genesis phase."""
    input_value: object
    hash_value: int
    lens_scores: Tuple[int, ...]
    quarter: Quarter

@dataclass(frozen=True)
class DharmaResult:
    """Result of Dharma phase."""
    input_value: int
    output_value: int
    attractor: int
    steps: int
    quarter: Quarter

@dataclass(frozen=True)
class KarmaResult:
    """Result of Karma phase."""
    key: int
    value: object
    routed: bool
    quarter: Quarter

@dataclass(frozen=True)
class MokshaResult:
    """Result of Moksha phase."""
    input_value: int
    beat: int
    round_num: int
    resonance: float
    quarter: Quarter

@dataclass(frozen=True)
class PipelineResult:
    """Complete pipeline result."""
    genesis: GenesisResult
    dharma: DharmaResult
    karma: KarmaResult
    moksha: MokshaResult
    final_value: int
    total_resonance: float
