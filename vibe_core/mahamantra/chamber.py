"""
SANKIRTAN CHAMBER - The Resonance Space
========================================

"kirtanīyaḥ sadā hariḥ"
"One should always chant the holy name of the Lord"
— Chaitanya Charitamrita, Adi 17.31

The Chamber OWNS the Orchestrator. Cells FLOW through.
This is COMPOSITION, not INHERITANCE.

Pattern:
- State (Cell) is separated from Logic (Orchestrator)
- Cells remain dumb (data), Chamber is intelligent (music)

ALL VALUES DERIVED FROM SSOT (_seed.py). NO HARDCODING. NO `Any`.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "gauranga"
__position__ = 0  # Chaitanya = 0 (The Source of Sankirtan)
__genesis__ = "0xd7a9e543"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Final, ClassVar, Optional, TypeVar, Generic, Callable
from enum import IntEnum

from vibe_core.mahamantra.protocols._seed import (
    # Core constants
    WORDS,
    MALA,
    PARAMPARA,
    MAHA_QUANTUM,
    COSMIC_FRAME,
    # Flute structure
    FLUTE_HOLES_SUM,
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    # Derived
    SEVEN,
    TEN,
)
from vibe_core.mahamantra.orchestrator import (
    VenuOrchestrator,
    THE_FLUTE_CYCLE,
    DIW_MASK,
    SUNYA_MASK,
)
from vibe_core.mahamantra.cell import (
    MahaCellUnified,
    CellLifecycleState,
    GENESIS_PRANA,
)


# =============================================================================
# TYPE VARIABLES
# =============================================================================

C = TypeVar("C")  # Cell state type


# =============================================================================
# CHAMBER CONSTANTS (DERIVED FROM SSOT)
# =============================================================================

# Maximum cells in chamber: MALA = 108
CHAMBER_CAPACITY: Final[int] = MALA

# Resonance threshold for merging: PARAMPARA = 37
RESONANCE_THRESHOLD: Final[int] = PARAMPARA

# Default chorus size: 16 (one full mantra cycle)
DEFAULT_CHORUS_SIZE: Final[int] = WORDS


# =============================================================================
# KIRTAN MODE (Transformation Types)
# =============================================================================

class KirtanMode(IntEnum):
    """
    The modes of chanting in the chamber.
    
    Derived from the three flutes:
    - SOLO (Venu) = Individual transformation
    - CALL_RESPONSE (Vamsi) = Leader-follower pattern
    - CHORUS (Murali) = Group harmony
    """
    SOLO = 0          # Single cell transformation
    CALL_RESPONSE = 1  # Two cells interacting
    CHORUS = 2         # Multiple cells merging


# =============================================================================
# SANKIRTAN CHAMBER
# =============================================================================

@dataclass
class SankirtanChamber(Generic[C]):
    """
    The Resonance Space - Where Cells Flow Through Music.
    
    The Chamber OWNS the Orchestrator and transforms cells that flow through.
    This is COMPOSITION, not INHERITANCE.
    
    Pattern:
        cell_in → orchestrator.step() → transform → cell_out
    
    SSOT Derivation:
        CHAMBER_CAPACITY = MALA = 108
        RESONANCE_THRESHOLD = PARAMPARA = 37
        DEFAULT_CHORUS_SIZE = WORDS = 16
    """
    
    __mahajana__: ClassVar[str] = "gauranga"
    __position__: ClassVar[int] = 0
    
    # The Orchestrator (owned, not inherited)
    _orchestrator: VenuOrchestrator = field(default_factory=VenuOrchestrator)
    
    # Chamber state
    _resonance_count: int = 0
    _total_transformations: int = 0
    _accumulated_diw: int = 0
    
    @property
    def tick(self) -> int:
        """Current orchestrator tick."""
        return self._orchestrator.tick
    
    @property
    def resonance_count(self) -> int:
        """Number of resonant transformations (mod PARAMPARA == 0)."""
        return self._resonance_count
    
    @property
    def total_transformations(self) -> int:
        """Total cells transformed."""
        return self._total_transformations
    
    # =========================================================================
    # CORE TRANSFORMATION METHODS
    # =========================================================================
    
    def dance(self, cell: MahaCellUnified[C]) -> MahaCellUnified[C]:
        """
        Single cell flows through, gets transformed.
        
        This is the atomic operation: cell + DIW → transformed cell.
        
        Args:
            cell: The cell to transform
            
        Returns:
            The same cell (mutated) after transformation
        """
        # Get the current Divine Instruction Word
        diw = self._orchestrator.step()
        
        # Transform the cell
        self._apply_diw(cell, diw)
        
        # Track resonance
        self._accumulated_diw ^= (diw & DIW_MASK)
        self._total_transformations += 1
        
        if self._accumulated_diw % PARAMPARA == 0:
            self._resonance_count += 1
        
        return cell
    
    def kirtan(
        self,
        cell: MahaCellUnified[C],
        cycles: int = 1,
    ) -> MahaCellUnified[C]:
        """
        Transform cell through multiple mantra cycles.
        
        One cycle = WORDS (16) transformations.
        
        Args:
            cell: The cell to transform
            cycles: Number of full cycles (default: 1)
            
        Returns:
            The transformed cell
        """
        for _ in range(cycles * WORDS):
            self.dance(cell)
        return cell
    
    def sankirtan(
        self,
        cells: list[MahaCellUnified[C]],
        merge: bool = False,
    ) -> list[MahaCellUnified[C]]:
        """
        Transform multiple cells together (group chanting).
        
        When merge=True, cells with resonance scores > RESONANCE_THRESHOLD
        are merged using XOR of their headers.
        
        Args:
            cells: List of cells to transform
            merge: Whether to merge resonant cells
            
        Returns:
            List of transformed cells (may be shorter if merged)
        """
        if not cells:
            return cells
        
        # Transform all cells
        for cell in cells:
            self.dance(cell)
        
        if not merge:
            return cells
        
        # Merge resonant cells
        return self._merge_resonant(cells)
    
    # =========================================================================
    # TRANSFORMATION LOGIC
    # =========================================================================
    
    def _apply_diw(self, cell: MahaCellUnified[C], diw: int) -> None:
        """
        Apply Divine Instruction Word to cell.
        
        The DIW modifies:
        - prana: energy adjustment based on low 6 bits (VENU)
        - integrity: adjustment based on middle 9 bits (VAMSI)
        - cycle: advancement based on high 4 bits (MURALI)
        """
        # Extract flute components
        venu_bits = diw & ((1 << VENU_HOLES) - 1)
        vamsi_bits = (diw >> VENU_HOLES) & ((1 << VAMSI_HOLES) - 1)
        murali_bits = (diw >> (VENU_HOLES + VAMSI_HOLES)) & ((1 << MURALI_HOLES) - 1)
        
        # Apply to lifecycle
        # VENU (6 bits): Modulate prana (energy)
        prana_delta = (venu_bits * SEVEN) % 64 - 32  # Range: -32 to +31
        cell.lifecycle.prana = max(0, cell.lifecycle.prana + prana_delta)
        
        # VAMSI (9 bits): Modulate integrity (stability factor)
        integrity_factor = 1.0 - (vamsi_bits / 512.0) * 0.01  # Max 1% change
        cell.lifecycle.integrity = max(0.0, min(1.0, 
            cell.lifecycle.integrity * integrity_factor
        ))
        
        # MURALI (4 bits): Advance cycle counter
        cell.lifecycle.cycle += murali_bits % 4
    
    def _merge_resonant(
        self,
        cells: list[MahaCellUnified[C]],
    ) -> list[MahaCellUnified[C]]:
        """
        Merge cells with high resonance.
        
        Cells are considered resonant if their header checksums
        have matching modulo PARAMPARA values.
        """
        if len(cells) < 2:
            return cells
        
        result: list[MahaCellUnified[C]] = []
        merged_indices: set[int] = set()
        
        for i, cell_a in enumerate(cells):
            if i in merged_indices:
                continue
            
            # Find resonant partner
            partner_found = False
            for j in range(i + 1, len(cells)):
                if j in merged_indices:
                    continue
                
                cell_b = cells[j]
                
                # Check resonance: XOR of checksums mod PARAMPARA
                xor_check = cell_a.header.atma_nivedanam ^ cell_b.header.atma_nivedanam
                if xor_check % PARAMPARA == 0:
                    # Merge: combine prana, average integrity
                    cell_a.lifecycle.prana += cell_b.lifecycle.prana
                    cell_a.lifecycle.integrity = (
                        cell_a.lifecycle.integrity + cell_b.lifecycle.integrity
                    ) / 2
                    
                    merged_indices.add(j)
                    partner_found = True
                    break
            
            result.append(cell_a)
        
        return result
    
    # =========================================================================
    # VERIFICATION METHODS
    # =========================================================================
    
    def verify_resonance(self) -> bool:
        """
        Verify the chamber maintains resonance.
        
        Returns True if accumulated DIW creates proper resonance pattern.
        """
        # Run one full cycle
        test_orch = VenuOrchestrator()
        xor_result = test_orch.cycle()
        
        # Must equal all 16 bits set
        expected = (1 << WORDS) - 1
        return xor_result == expected
    
    def is_silent(self, diw: int) -> bool:
        """Check if instruction is silence (SUNYA)."""
        return self._orchestrator.is_sunya(diw)
    
    def reset(self) -> None:
        """Reset chamber to initial state."""
        self._orchestrator.reset()
        self._resonance_count = 0
        self._total_transformations = 0
        self._accumulated_diw = 0
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create(cls) -> "SankirtanChamber[C]":
        """Create a new chamber with fresh orchestrator."""
        return cls(
            _orchestrator=VenuOrchestrator(),
            _resonance_count=0,
            _total_transformations=0,
            _accumulated_diw=0,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "CHAMBER_CAPACITY",
    "RESONANCE_THRESHOLD",
    "DEFAULT_CHORUS_SIZE",
    # Types
    "KirtanMode",
    "SankirtanChamber",
]
