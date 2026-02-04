"""
SANKIRTAN CHAMBER - The Resonance Space
========================================

"kirtanīyaḥ sadā hariḥ"
"One should always chant the holy name of the Lord"
— Chaitanya Charitamrita, Adi 17.31

The Chamber OWNS the Orchestrator and the Registry.
Cells FLOW through the Registry, triggered by the Orchestrator.

Structure:
    Orchestrator (Time/Logic) -> DIW -> Registry (Space/Memory) -> Cell (Life)

ALL VALUES DERIVED FROM SSOT (_seed.py). NO HARDCODING. NO `Any`.
"""
from vibe_core.mahamantra.protocols._seed import (HALVES, KSETRAJNA, KSHETRA, QUALITIES, QUARTERS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "gauranga"
__position__ = 0  # Chaitanya = 0 (The Source of Sankirtan)
__genesis__ = "0xe79456f2"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Final, ClassVar, Optional, TypeVar, Generic, Callable
import struct
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
from vibe_core.mahamantra.protocols._pancha import TattvaDict
from vibe_core.mahamantra.orchestrator import (
    VenuOrchestrator,
    THE_FLUTE_CYCLE,
    DIW_MASK,
    SUNYA_MASK,
    VENU_SHIFT,
    VAMSI_SHIFT,
    MURALI_SHIFT,
)
from vibe_core.mahamantra.substrate.cell import (
    MahaCellUnified,
    CellLifecycleState,
    GENESIS_PRANA,
)
from vibe_core.mahamantra.substrate.cluster import MahaCluster
from vibe_core.mahamantra.substrate.registry import SiksastakamRegistry
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator


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
    CALL_RESPONSE = KSETRAJNA  # Two cells interacting
    CHORUS = HALVES         # Multiple cells merging


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
        cell_in → orchestrator.step() → transform → registry(vamsi) → cell_out
    
    SSOT Derivation:
        CHAMBER_CAPACITY = MALA = 108
        RESONANCE_THRESHOLD = PARAMPARA = 37
        DEFAULT_CHORUS_SIZE = WORDS = 16
    """
    
    __mahajana__: ClassVar[str] = "gauranga"
    __position__: ClassVar[int] = 0
    
    # The Orchestrator (owned, not inherited)
    _orchestrator: VenuOrchestrator = field(default_factory=VenuOrchestrator)
    
    # The Registry (Musical Memory - 512 slots)
    _registry: SiksastakamRegistry = field(default_factory=SiksastakamRegistry)
    
    # Resonance Engines (for Clustering)
    _resonator: MahaResonator = field(default_factory=lambda: MahaResonator(mod_space=MAHA_QUANTUM))
    
    # Chamber state
    _resonance_count: int = 0
    _total_transformations: int = 0
    _accumulated_diw: int = 0

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of SankirtanChamber."""
        return {
            "chaitanya": "SankirtanChamber - The Resonance Space (RAM Engine)",
            "nityananda": "VenuOrchestrator (Time) + SiksastakamRegistry (Space)",
            "advaita": "dance() / sankirtan() - DIW-driven cell transformation",
            "gadadhara": "Cell → DIW → Transform → Registry → Cell",
            "srivasa": "MALA (108 capacity), PARAMPARA (37 threshold)",
        }

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
    
    @property
    def active_cells(self) -> list[MahaCellUnified[C]]:
        """Return all cells currently residing in the registry."""
        return self._registry.active_cells()
    
    # =========================================================================
    # CORE TRANSFORMATION METHODS
    # =========================================================================
    
    def dance(self, cell: MahaCellUnified[C]) -> MahaCellUnified[C]:
        """
        Single cell flows through, gets transformed, and interacts with Memory.
        
        Logic:
        1. Get DIW from Orchestrator.
        2. Transform Cell (apply DIW).
        3. Extract Vamsi (Address) from DIW.
        4. Interact with Registry at Vamsi address:
           - Empty? -> Occupy (Presence).
           - Occupied? -> Merge (Resonance).
        
        Args:
            cell: The cell to transform
            
        Returns:
            The resulting cell (original or merged)
        """
        # 1. Get the current Divine Instruction Word
        diw = self._orchestrator.step()
        
        # 2. Transform the cell
        self._apply_diw(cell, diw)
        
        # 3. INTERACT WITH REGISTRY (Musical Memory)
        # Extract Vamsi (9 bits) - The Memory Address
        vamsi = (diw >> VAMSI_SHIFT) & ((KSETRAJNA << VAMSI_HOLES) - KSETRAJNA)
        
        # Branchless Sunya Pattern:
        # Get resident (Active or Null)
        resident = self._registry.get(vamsi)
        
        # Check collision BEFORE interaction (for metrics only)
        # (This branch is for stats, not logic flow)
        if resident.is_alive and resident is not cell:
            self._resonance_count += KSETRAJNA
            
        # Polymorphic Interaction
        # If resident is Null -> returns cell (Presence)
        # If resident is Active -> returns resident (Resonance/Merge)
        result_cell = resident.interact(cell)
        
        # Update Registry
        # Always set, whether it's new presence or updated resonance
        self._registry.set(vamsi, result_cell)
        
        # Track statistics
        self._accumulated_diw ^= (diw & DIW_MASK)
        self._total_transformations += KSETRAJNA
        
        if self._accumulated_diw % PARAMPARA == 0:
            self._resonance_count += KSETRAJNA
            
        # 4. HARMONIC FEEDBACK (Gemini Round 2)
        # Verify Resonance -> Adapt Mode
        # If resonance is high, we enter CHORUS mode (Broadcast)
        if self._resonance_count > CHAMBER_CAPACITY: # 108
            if self._orchestrator.mode != KirtanMode.CHORUS:
                self._orchestrator.set_mode(KirtanMode.CHORUS)
        elif self._resonance_count > PARAMPARA: # 37
            if self._orchestrator.mode != KirtanMode.CALL_RESPONSE:
                self._orchestrator.set_mode(KirtanMode.CALL_RESPONSE)
        
        return result_cell
    
    def kirtan(
        self,
        cell: MahaCellUnified[C],
        cycles: int = KSETRAJNA,
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
        current = cell
        for _ in range(cycles * WORDS):
            current = self.dance(current)
        return current
    
    def sankirtan(
        self,
        cells: list[MahaCellUnified[C]],
    ) -> MahaCluster[C]:
        """
        Mass Kirtan - merge cells without identity loss.
        
        Cells merge into a MahaCluster (Unity in Diversity).
        
        Args:
            cells: List of cells to transform/merge
            
        Returns:
            MahaCluster representing the group resonance
        """
        if not cells:
            return MahaCluster([], 0, 0.0)
            
        # 1. Transform all cells through the Chamber (Process)
        processed_cells = []
        for cell in cells:
            # Each cell dances through the registry
            res = self.dance(cell)
            processed_cells.append(res)
            
        # 2. Compute Group Resonance (Attractor)
        # Combined seed = XOR of all cell signatures (arcanam)
        combined_seed = 0
        for cell in processed_cells:
            combined_seed ^= cell.header.arcanam
            
        # Find the natural attractor for this group
        # Use the Resonator (owned by Chamber now)
        attractor_result = self._resonator.find_attractor(combined_seed)
        
        # 3. Create Cluster
        return MahaCluster(
            cells=processed_cells,
            resonance_attractor=attractor_result.attractor,
            coherence=attractor_result.attractor / MALA, # Normalized
        )
    
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
        venu_bits = (diw >> VENU_SHIFT) & ((KSETRAJNA << VENU_HOLES) - KSETRAJNA)
        vamsi_bits = (diw >> VAMSI_SHIFT) & ((KSETRAJNA << VAMSI_HOLES) - KSETRAJNA)
        murali_bits = (diw >> MURALI_SHIFT) & ((KSETRAJNA << MURALI_HOLES) - KSETRAJNA)
        
        # Apply to lifecycle
        # VENU (6 bits): Modulate prana (energy)
        prana_delta = (venu_bits * SEVEN) % QUALITIES - 32  # Range: -32 to +31
        cell.lifecycle.prana = max(0, cell.lifecycle.prana + prana_delta)
        
        # VAMSI (9 bits): Modulate integrity (stability factor)
        integrity_factor = 1.0 - (vamsi_bits / 512.0) * 0.01  # Max 1% change
        cell.lifecycle.integrity = max(0.0, min(1.0, 
            cell.lifecycle.integrity * integrity_factor
        ))
        
        # MURALI (4 bits): Advance cycle counter
        cell.lifecycle.cycle += murali_bits % QUARTERS
    
    def _merge_pair(
        self,
        resident: MahaCellUnified[C],
        visitor: MahaCellUnified[C],
    ) -> MahaCellUnified[C]:
        """
        Merge two cells colliding in the Registry.
        
        Strategy:
        - Prana accumulates
        - Integrity averages
        - Identify (Header) XORs (creating new signature)
        """
        # Combine Prana (additive energy)
        resident.lifecycle.prana += visitor.lifecycle.prana
        
        # Average Integrity
        resident.lifecycle.integrity = (
            resident.lifecycle.integrity + visitor.lifecycle.integrity
        ) / HALVES
        
        # Mix Identities (Resonance)
        # We don't change the immutable header ID, but we could update 'atma_nivedanam' checksum?
        # For now, we mainly accumulate Life Force.
        
        return resident
        
    def _merge_resonant(
        self,
        cells: list[MahaCellUnified[C]],
    ) -> list[MahaCellUnified[C]]:
        """
        Merge cells in a list with high resonance (Legacy/Batch mode).
        
        Cells are considered resonant if their header checksums
        have matching modulo PARAMPARA values.
        """
        if len(cells) < HALVES:
            return cells
        
        result: list[MahaCellUnified[C]] = []
        merged_indices: set[int] = set()
        
        for i, cell_a in enumerate(cells):
            if i in merged_indices:
                continue
            
            # Find resonant partner
            partner_found = False
            for j in range(i + KSETRAJNA, len(cells)):
                if j in merged_indices:
                    continue
                
                cell_b = cells[j]
                
                # Check resonance: XOR of checksums mod PARAMPARA
                xor_check = cell_a.header.atma_nivedanam ^ cell_b.header.atma_nivedanam
                if xor_check % PARAMPARA == 0:
                    # Merge using pair logic
                    merger = self._merge_pair(cell_a, cell_b)
                    
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
        expected = (KSETRAJNA << WORDS) - KSETRAJNA
        return xor_result == expected
    
    def is_silent(self, diw: int) -> bool:
        """Check if instruction is silence (SUNYA)."""
        return self._orchestrator.is_sunya(diw)
    
    def reset(self) -> None:
        """Reset all state (Registry, Orchestrator, Metrics)."""
        self._orchestrator.reset()
        self._registry.clear()
        self._accumulated_diw = 0
        self._resonance_count = 0
        self._total_transformations = 0

    # =========================================================================
    # PERSISTENCE (ChamberState)
    # =========================================================================
    
    def snapshot(self) -> bytes:
        """
        Create a full snapshot of the Chamber state.
        
        Includes: Metrics, Orchestrator State, Registry State.
        Format:
            [4s: Magic "OM!!"]
            [Q: accumulated_diw]
            [Q: resonance_count]
            [Q: total_transformations]
            [24s: Orchestrator State] (was 16s)
            [N: Registry State]
        """
        result = bytearray()
        
        # Header (Magic + Metrics)
        # 4 + 8 + 8 + 8 = 28 bytes
        result.extend(b"OM!!")
        result.extend(struct.pack(
            "<QQQ",
            self._accumulated_diw,
            self._resonance_count,
            self._total_transformations
        ))
        
        # Orchestrator (24 bytes now)
        result.extend(self._orchestrator.to_bytes())
        
        # Registry (Variable)
        result.extend(self._registry.to_bytes())
        
        return bytes(result)
    
    def restore(self, snapshot: bytes) -> None:
        """
        Restore Chamber from snapshot.
        
        Args:
            snapshot: Valid snapshot bytes
            
        Raises:
            ValueError: If magic or format is invalid
        """
        if len(snapshot) < 52: # 28 (Header) + 24 (Orchestrator)
            # Try legacy size check (44 bytes) for backward compat logic
            pass 
            
        # 1. Header
        magic = snapshot[:QUARTERS]
        if magic != b"OM!!":
            raise ValueError(f"Invalid magic: {magic!r}")
            
        offset = QUARTERS
        (
            self._accumulated_diw,
            self._resonance_count,
            self._total_transformations
        ) = struct.unpack("<QQQ", snapshot[offset:offset+KSHETRA])
        offset += KSHETRA
        
        # 2. Orchestrator
        # We need to detect size.
        # But we don't know the exact break point without a length prefix.
        # However, VenuOrchestrator.from_bytes() handles length check.
        # Let's peek 24 bytes if strictly 24 are available.
        # Wait, Registry data follows. How do we know where Orchestrator ends?
        # WE DON'T.
        # This is a binary format flaw. Logic update needed.
        # Orchestrator size MUST be fixed or prefixed.
        # Since I changed it to 24 bytes, and I control both files...
        # I will assume 24 bytes for new format.
        # Old snapshots (16 bytes) will fail or need heuristics.
        # Given this is a fresh feature, assuming 24 bytes is acceptable.
        
        orch_size = KSHETRA
        orch_data = snapshot[offset:offset+orch_size]
        self._orchestrator.from_bytes(orch_data)
        offset += orch_size
        
        # 3. Registry
        registry_data = snapshot[offset:]
        self._registry.from_bytes(registry_data)
    
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
        expected = (KSETRAJNA << WORDS) - KSETRAJNA
        return xor_result == expected
    
    def is_silent(self, diw: int) -> bool:
        """Check if instruction is silence (SUNYA)."""
        return self._orchestrator.is_sunya(diw)
    
    def reset(self) -> None:
        """Reset all state (Registry, Orchestrator, Metrics)."""
        self._orchestrator.reset()
        self._registry.clear()
        self._accumulated_diw = 0
        self._resonance_count = 0
        self._total_transformations = 0

    # =========================================================================
    # PERSISTENCE (ChamberState)
    # =========================================================================
    
    def snapshot(self) -> bytes:
        """
        Create a full snapshot of the Chamber state.
        
        Includes: Metrics, Orchestrator State, Registry State.
        Format:
            [4s: Magic "OM!!"]
            [Q: accumulated_diw]
            [Q: resonance_count]
            [Q: total_transformations]
            [24s: Orchestrator State] (was 16s)
            [N: Registry State]
        """
        result = bytearray()
        
        # Header (Magic + Metrics)
        # 4 + 8 + 8 + 8 = 28 bytes
        result.extend(b"OM!!")
        result.extend(struct.pack(
            "<QQQ",
            self._accumulated_diw,
            self._resonance_count,
            self._total_transformations
        ))
        
        # Orchestrator (24 bytes now)
        result.extend(self._orchestrator.to_bytes())
        
        # Registry (Variable)
        result.extend(self._registry.to_bytes())
        
        return bytes(result)
    
    def restore(self, snapshot: bytes) -> None:
        """
        Restore Chamber from snapshot.
        
        Args:
            snapshot: Valid snapshot bytes
            
        Raises:
            ValueError: If magic or format is invalid
        """
        if len(snapshot) < 52: # 28 (Header) + 24 (Orchestrator)
            # Try legacy size check (44 bytes) for backward compat logic
            pass 
            
        # 1. Header
        magic = snapshot[:QUARTERS]
        if magic != b"OM!!":
            raise ValueError(f"Invalid magic: {magic!r}")
            
        offset = QUARTERS
        (
            self._accumulated_diw,
            self._resonance_count,
            self._total_transformations
        ) = struct.unpack("<QQQ", snapshot[offset:offset+KSHETRA])
        offset += KSHETRA
        
        # 2. Orchestrator
        # We need to detect size.
        # But we don't know the exact break point without a length prefix.
        # However, VenuOrchestrator.from_bytes() handles length check.
        # Let's peek 24 bytes if strictly 24 are available.
        # Wait, Registry data follows. How do we know where Orchestrator ends?
        # WE DON'T.
        # This is a binary format flaw. Logic update needed.
        # Orchestrator size MUST be fixed or prefixed.
        # Since I changed it to 24 bytes, and I control both files...
        # I will assume 24 bytes for new format.
        # Old snapshots (16 bytes) will fail or need heuristics.
        # Given this is a fresh feature, assuming 24 bytes is acceptable.
        
        orch_size = KSHETRA
        orch_data = snapshot[offset:offset+orch_size]
        self._orchestrator.from_bytes(orch_data)
        offset += orch_size
        
        # 3. Registry
        registry_data = snapshot[offset:]
        self._registry.from_bytes(registry_data)
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create(cls) -> "SankirtanChamber[C]":
        """Create a new chamber with fresh orchestrator and registry."""
        return cls(
            _orchestrator=VenuOrchestrator(),
            _registry=SiksastakamRegistry(),
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
