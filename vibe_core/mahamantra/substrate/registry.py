"""
SIKSASTAKAM REGISTRY - The Musical Memory (512 Slots)
=====================================================

"ceto-darpaṇa-mārjanaṁ bhava-mahā-dāvāgni-nirvāpaṇaṁ"
"Cleansing the mirror of the heart, extinguishing the forest fire of material existence."
— Siksastakam Verse 1

THE MEMORY MODEL:
-----------------
The Registry is the stored state of the Sankirtan Chamber.
It has exactly 512 slots, corresponding to the 9 bits of the Vamsi flute.

   VAMSI (9 bits) -> 2^9 = 512 Addresses

This acts like a musical instrument's fingerboard.
When the Orchestrator plays a Vamsi note (e.g., 0x1A4),
it activates that specific slot in memory.

If a Cell is already there -> RESONANCE (Merge).
If the slot is empty -> PRESENCE (Storage).
"""

from typing import List, Optional, Final

from vibe_core.mahamantra.protocols._seed_cell import SIKSASTAKAM_CACHE
from vibe_core.mahamantra.cell import MahaCellUnified


class SiksastakamRegistry:
    """
    Fixed-size 512-slot memory for Vamsi orchestration.
    
    The 'Mirror' (Darpana) reflecting the state of the system.
    Access is O(1) via Vamsi index.
    """
    
    __slots__ = ('_memory',)
    
    def __init__(self) -> None:
        """Initialize the empty mirror with 512 slots (None)."""
        # Pre-allocate fixed list. Fast and memory efficient.
        self._memory: List[Optional[MahaCellUnified]] = [None] * SIKSASTAKAM_CACHE
        
    @property
    def capacity(self) -> int:
        """The fixed capacity (512)."""
        return SIKSASTAKAM_CACHE
        
    def get(self, index: int) -> Optional[MahaCellUnified]:
        """
        Retrieve cell at Vamsi index.
        
        Args:
            index: Vamsi state (0-511)
            
        Returns:
            The cell at this memory location, or None.
            
        Raises:
            IndexError: If index is outside valid Vamsi range.
        """
        # Python list access is safe, but explicit check matches strict protocol behavior
        if not 0 <= index < SIKSASTAKAM_CACHE:
            raise IndexError(f"Vamsi index {index} out of bounds (0-{SIKSASTAKAM_CACHE-1})")
        return self._memory[index]
        
    def set(self, index: int, cell: Optional[MahaCellUnified]) -> None:
        """
        Place (or clear) cell at Vamsi index.
        
        Args:
            index: Vamsi state (0-511)
            cell: The MahaCellUnified to place (or None to clear)
        """
        if not 0 <= index < SIKSASTAKAM_CACHE:
            raise IndexError(f"Vamsi index {index} out of bounds (0-{SIKSASTAKAM_CACHE-1})")
        self._memory[index] = cell

    def clear(self) -> None:
        """
        Wipe the mirror clean (ceto-darpaṇa-mārjanaṁ).
        Resets all slots to None.
        """
        # List slicing is the fastest way to clear/fill in Python
        self._memory[:] = [None] * SIKSASTAKAM_CACHE
        
    def active_cells(self) -> List[MahaCellUnified]:
        """
        Return list of all currently active cells.
        
        Used for visualization and debugging.
        Complexity: O(N) where N=512.
        """
        return [cell for cell in self._memory if cell is not None]

    def __repr__(self) -> str:
        """String representation of registry state."""
        count = sum(1 for c in self._memory if c is not None)
        return f"<SiksastakamRegistry: {count}/{SIKSASTAKAM_CACHE} slots active>"
