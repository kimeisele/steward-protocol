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

from typing import Final, ClassVar, Optional, TypeVar, Generic, List
import struct

from vibe_core.mahamantra.substrate.cell import MahaCellUnified
from vibe_core.mahamantra.protocols._seed import (
    MALA,
    WORDS,
    HALVES,
    NAVA,
)

SIKSASTAKAM_CACHE: Final[int] = HALVES ** NAVA  # 512


class SiksastakamRegistry:
    """
    Fixed-size 512-slot memory for Vamsi orchestration.
    
    The 'Mirror' (Darpana) reflecting the state of the system.
    Access is O(1) via Vamsi index.
    
    Uses Null Object Pattern (Branchless Sunya):
    - No 'None' in memory.
    - SiksastakamRegistry is always full of either Active or Null cells.
    """
    
    __slots__ = ('_memory',)
    
    def __init__(self) -> None:
        """Initialize the mirror with 512 Null Cells (Silence)."""
        # Pre-allocate fixed list with distinct Null objects
        self._memory: List[MahaCellUnified] = [
            MahaCellUnified.null() for _ in range(SIKSASTAKAM_CACHE)
        ]
        
    @property
    def capacity(self) -> int:
        """The fixed capacity (512)."""
        return SIKSASTAKAM_CACHE
        
    def get(self, index: int) -> MahaCellUnified:
        """
        Retrieve cell at Vamsi index.
        
        Args:
            index: Vamsi state (0-511)
            
        Returns:
            The cell at this memory location (Active or Null).
            Never returns None.
            
        Raises:
            IndexError: If index is outside valid Vamsi range.
        """
        if not 0 <= index < SIKSASTAKAM_CACHE:
            raise IndexError(f"Vamsi index {index} out of bounds (0-{SIKSASTAKAM_CACHE-1})")
        return self._memory[index]
        
    def set(self, index: int, cell: MahaCellUnified) -> None:
        """
        Place cell at Vamsi index.
        
        Args:
            index: Vamsi state (0-511)
            cell: The MahaCellUnified to place (Active or Null)
        """
        if not 0 <= index < SIKSASTAKAM_CACHE:
            raise IndexError(f"Vamsi index {index} out of bounds (0-{SIKSASTAKAM_CACHE-1})")
        self._memory[index] = cell

    def clear(self) -> None:
        """
        Wipe the mirror clean (ceto-darpaṇa-mārjanaṁ).
        Resets all slots to Null Cells.
        """
        self._memory[:] = [MahaCellUnified.null() for _ in range(SIKSASTAKAM_CACHE)]
        
    def active_cells(self) -> List[MahaCellUnified]:
        """
        Return list of all currently active cells.
        
        Used for visualization and debugging.
        Complexity: O(N) where N=512.
        """
        return [cell for cell in self._memory if cell.is_alive]

    def __repr__(self) -> str:
        """String representation of registry state."""
        count = sum(1 for c in self._memory if c.is_alive)
        return f"<SiksastakamRegistry: {count}/{SIKSASTAKAM_CACHE} slots active>"

    # =========================================================================
    # PERSISTENCE (ChamberState)
    # =========================================================================
    
    def to_bytes(self) -> bytes:
        """
        Serialize registry state (Active cells only).
        
        Format:
            [4 bytes: count (uint32)]
            Repeating 'count' times:
                [2 bytes: index (uint16)]
                [4 bytes: length (uint32)]
                [N bytes: cell data]
        """
        result = bytearray()
        
        # Filter active cells
        active_entries = [(i, c) for i, c in enumerate(self._memory) if c.is_alive]
        
        # 1. Count
        result.extend(struct.pack("<I", len(active_entries)))
        
        # 2. Entries
        for index, cell in active_entries:
            cell_bytes = cell.to_bytes()
            # Index (2 bytes) + Length (4 bytes)
            result.extend(struct.pack("<HI", index, len(cell_bytes)))
            result.extend(cell_bytes)
            
        return bytes(result)
    
    def from_bytes(self, data: bytes) -> None:
        """
        Restore registry state from bytes.
        
        Replaces current state.
        
        Args:
            data: Serialized registry data
        """
        # Reset to clean state
        self.clear()
        
        offset = 0
        if len(data) < 4:
            raise ValueError("Data too short check count")
            
        # 1. Count
        count = struct.unpack("<I", data[offset:offset+4])[0]
        offset += 4
        
        # 2. Entries
        for _ in range(count):
            if len(data) < offset + 6:
                raise ValueError("Data truncated reading entry header")
            
            index, length = struct.unpack("<HI", data[offset:offset+6])
            offset += 6
            
            if len(data) < offset + length:
                raise ValueError("Data truncated reading cell body")
            
            cell_data = data[offset:offset+length]
            cell, _ = MahaCellUnified.from_bytes(cell_data)
            
            # Place in registry
            if 0 <= index < SIKSASTAKAM_CACHE:
                self._memory[index] = cell
            
            offset += length
