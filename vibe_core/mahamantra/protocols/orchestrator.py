from typing import Protocol, runtime_checkable, List, Tuple
from vibe_core.mahamantra.protocols._seed import (SEVEN)
from dataclasses import dataclass, field

@runtime_checkable
class MahaOrchestratorProtocol(Protocol):
    """
    Protocol for MahaOrchestrator: Rhythmic Compute Engine.
    
    7-beat timing cycle for algorithmic resonance.
    """
    
    def tick(self, seed: int) -> "TickResult":
        """Execute single beat (1/7)."""
        ...
        
    def round(self, seed: int) -> "RoundResult":
        """Execute full round (7 beats)."""
        ...
        
    def rounds(self, seed: int, count: int = SEVEN) -> List["RoundResult"]:
        """Execute multiple rounds."""
        ...
        
    def mala(self, seed: int) -> "MalaResult":
        """Execute complete mala (108 rounds)."""
        ...
        
    def reset(self) -> None:
        """Reset state."""
        ...
        
    @property
    def state(self) -> dict:
        """Get current state."""
        ...

@dataclass(frozen=True)
class TickResult:
    """Result of a single tick."""
    seed: int
    value: int
    beat: int
    round_num: int
    call_response: str
    resonance: float
    beat_delta: int = 0
    metrics: dict = field(default_factory=dict)

@dataclass(frozen=True)
class RoundResult:
    """Result of a complete round."""
    seed: int
    final_value: int
    ticks: Tuple[TickResult, ...]
    resonance: float
    metrics: dict = field(default_factory=dict)

@dataclass(frozen=True)
class MalaResult:
    """Result of a complete mala."""
    seed: int
    final_value: int
    total_ticks: int
    final_resonance: float
    attractor: int
    metrics: dict = field(default_factory=dict)
