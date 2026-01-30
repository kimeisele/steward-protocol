from typing import Protocol, runtime_checkable, TypeVar, Generic, Optional, List, Dict, Tuple, Any
from dataclasses import dataclass

S = TypeVar("S")  # State Type
M = TypeVar("M")  # Message/Signal Type

@runtime_checkable
class MahaCellProtocol(Protocol, Generic[S, M]):
    """
    Protocol for MahaCell: The Fundamental Unit of Life & Compute.
    
    A Cell is a Jiva (living entity) within the Kshetra (field).
    It maintains Homeostasis, processes Prana, and follows Samsara (cycles).
    
    Principles:
    1. Membrane (Kshetra-boundary): Strict filter (0.0-1.0 integrity).
    2. Nucleus (Bijam): Protected state (S).
    3. Mitochondria (Prana): Energy management.
    """
    
    @property
    def id(self) -> str:
        """Unique Cell ID (UUID)."""
        ...
        
    @property
    def state(self) -> S:
        """Current internal state (Observation)."""
        ...
        
    @property
    def membrane_integrity(self) -> float:
        """Health of the boundary (0.0 - 1.0)."""
        ...
        
    @property
    def prana(self) -> int:
        """Current energy level."""
        ...

    def conceive(self, dna: str, genesis_state: S) -> None:
        """Initialize the cell (Birth/Janma)."""
        ...
        
    def metabolize(self, energy: int) -> int:
        """Process energy (Karma). Returns new prana level."""
        ...
        
    def signal(self, message: M) -> Optional[M]:
        """Process an incoming signal (Sanga)."""
        ...
        
    def mitosis(self) -> "MahaCellProtocol[S, M]":
        """Divide into two cells (Reproduction)."""
        ...
        
    def apoptosis(self) -> None:
        """Self-destruct (Death/Mrityu)."""
        ...
        
    def homeostasis(self) -> bool:
        """Maintain balance/integrity. Returns is_alive."""
        ...
        
    def get_organelles(self) -> Dict[str, object]:
        """List internal components."""
        ...

@dataclass(frozen=True)
class CellState(Generic[S]):
    """Snapshot of a cell's state."""
    id: str
    cycle: int
    data: S
    integrity: float
    prana: int
    dna: str

@dataclass(frozen=True)
class MembraneSignal(Generic[M]):
    """A signal trying to cross the membrane."""
    source_id: str
    payload: M
    strength: float
    signature: str
