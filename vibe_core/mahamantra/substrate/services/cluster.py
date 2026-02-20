"""
MAHA CLUSTER - Unity in Diversity (Acintya-bhedabheda-tattva)
=============================================================

"ekam evādvitīyam" -> "bahū syām"
"The One becomes Many, and the Many return to One."

MahaCluster represents multiple MahaCells resonating as a single entity
WITHOUT losing their individual identity.

PRINCIPLE:
    - Unity: The cluster has a single Header (Meta-Identity)
    - Diversity: It contains the original Cells (Individual Identity)
    - Resonance: The coherence of the group

SSOT ALIGNMENT:
    - Inherits physics from _seed.py
    - Uses MahaHeader for meta-identity
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "gauranga"
__position__ = 0
__genesis__ = "0xe79456f2"

from dataclasses import dataclass, field
from typing import List, Final, TypeVar, Generic

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    MALA,
    WORDS,
)
from vibe_core.mahamantra.protocols._header import MahaHeader
from vibe_core.mahamantra.substrate.harmonics import ResonanceHarmonics
from vibe_core.mahamantra.substrate.cell import MahaCellUnified

C = TypeVar("C")

@dataclass(frozen=True)
class MahaCluster(Generic[C]):
    """
    Multiple Cells as Unity - WITHOUT Identity Loss.
    
    "They become ONE but remain MANY."
    """
    
    cells: List[MahaCellUnified[C]]
    resonance_attractor: int        # Common attractor (18, 22, 49, 87, 136)
    coherence: int                  # 0 - 28800 (COSMIC_FRAME + 33% MALA bonus)
    
    # Meta-header generated post-init
    cluster_header: MahaHeader = field(init=False)

    def __post_init__(self) -> None:
        """Generate cluster header from component cells."""
        if not self.cells:
            # Empty cluster case
            object.__setattr__(self, 'cluster_header', MahaHeader.null())
            return

        # Combined source = XOR of all sources (Standard Mahamantra Hashing)
        combined_source = 0
        for cell in self.cells:
            combined_source ^= cell.header.sravanam

        # Use the first cell's operation as base, or 0 (Sankirtan)
        base_op = self.cells[0].header.pada_sevanam

        # Cluster header
        # Source: XOR sum
        # Target: The resonance attractor
        # Operation: Base op
        # State: Count of cells
        header = MahaHeader.create(
            source=combined_source,
            target=self.resonance_attractor,
            operation=base_op,
            state=len(self.cells),
        )
        object.__setattr__(self, 'cluster_header', header)

    def split(self) -> List[MahaCellUnified[C]]:
        """Split back into individual cells - full integrity."""
        return list(self.cells)

    def get_cell(self, index: int) -> MahaCellUnified[C]:
        """Access individual cell within cluster."""
        return self.cells[index]

    @property
    def size(self) -> int:
        """Number of cells in cluster."""
        return len(self.cells)

    @property
    def total_prana(self) -> int:
        """Combined energy of all cells."""
        return sum(c.prana for c in self.cells)

    @property
    def is_synchronized(self) -> bool:
        """Check if cluster is in SYNC zone."""
        return self.coherence >= ResonanceHarmonics.THRESHOLD_SYNC

    def __repr__(self) -> str:
        return (
            f"<MahaCluster size={self.size} "
            f"coherence={self.coherence:.2f} "
            f"attractor={self.resonance_attractor}>"
        )
