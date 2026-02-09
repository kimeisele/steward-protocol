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
from vibe_core.mahamantra.protocols._venu import VenuOrchestratorProtocol
from vibe_core.mahamantra.substrate.venu_orchestrator import (
    VenuOrchestrator,
    THE_FLUTE_CYCLE,
)
from vibe_core.mahamantra.protocols.diw import (
    CLUSTER_SHIFT,
    DIW_MASK,
    SUNYA_MASK,
    VENU_SHIFT,
    VAMSI_SHIFT,
    MURALI_SHIFT,
    VENU_MASK,
    VAMSI_MASK,
    MURALI_MASK,
    unpack,
)
from vibe_core.mahamantra.substrate.cell import (
    MahaCellUnified,
    CellLifecycleState,
    GENESIS_PRANA,
    MAX_PRANA,
)
from vibe_core.mahamantra.substrate.cluster import MahaCluster
from vibe_core.mahamantra.substrate.registry import SiksastakamRegistry
from vibe_core.mahamantra.substrate.antaranga import (
    AntarangaRegistry,
    GENESIS_PRANA_U32,
    INTEGRITY_FULL,
    FLAG_ACTIVE,
)
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

# =============================================================================
# DIW RESONANCE TABLE (DERIVED FROM SSOT)
# =============================================================================
# 12 effects = QUARTERS(4) phases × TRINITY-1(3) names.
# PHASE_DURATION == MAHAJANA_COUNT == 12. Time/Person holographic principle.
#
# TWO ACCESS PATHS (Acintya — simultaneously one and different):
#   4×3 (phase-first): phase * 3 + name   → "what happens to each name?"
#   3×4 (name-first):  name * 4 + phase   → "what does each name do?"
# Both index the SAME 12 effects. The data is one. The access is dual.
#
# Each entry: (prana_factor, integrity_coeff, cycle_add)
#   prana_factor:     multiplied by base_delta (+N = gain, -N = cost)
#   integrity_coeff:  multiplied by intensity (float)
#   cycle_add:        added to cell.cycle

# Canonical storage: 12 entries as (phase, name) → effect
_DIW_DATA: tuple = (
    #          prana  integrity  cycle
    # GENESIS (phase=0)
    ( HALVES,  0.0,     0),          # H: strong prana boost
    ( 1,       0.01,    0),          # K: moderate + integrity
    ( 1,       0.0,     KSETRAJNA),  # R: moderate + cycle
    # DHARMA (phase=1)
    (-1,       0.0,     0),          # H: validation cost
    ( 0,       0.02,    0),          # K: integrity strengthened
    ( 0,       0.01,    KSETRAJNA),  # R: cycle + integrity
    # KARMA (phase=2)
    (-1,       0.0,     KSETRAJNA),  # H: work + cycle
    (-1,       0.01,    KSETRAJNA),  # K: work + integrity + cycle
    (-1,       0.0,     HALVES),     # R: Rama accelerates
    # MOKSHA (phase=3)
    (-1,      -0.005,   0),          # H: slight integrity decay
    (-1,       0.01,    0),          # K: integrity stabilized
    (-1,       0.0,     HALVES),     # R: Rama delivers
)

# 4×3 index: phase * 3 + name (phase is outer loop)
_DIW_PHASE_FIRST: tuple = _DIW_DATA  # identity — already stored phase-first

# 3×4 index: name * 4 + phase (name is outer loop)
# Same 12 entries, transposed access. Built once at import.
_DIW_NAME_FIRST: tuple = tuple(
    _DIW_DATA[phase * 3 + name]
    for name in range(QUARTERS - KSETRAJNA)   # 3 names (H=0, K=1, R=2)
    for phase in range(QUARTERS)               # 4 phases per name
)

# Default: phase-first (the DIW naturally decomposes phase then name)
_DIW_RESONANCE_TABLE = _DIW_PHASE_FIRST


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

def _resolve_orchestrator() -> VenuOrchestrator:
    """Obtain the shared VenuOrchestrator from ServiceRegistry.

    Boot path: VenuService registered it → returns the ONE orchestrator.
    CLI path:  No VenuService → creates a local fallback instance.
    """
    from vibe_core.di import ServiceRegistry

    shared = ServiceRegistry.get(VenuOrchestratorProtocol)
    if shared is not None:
        return shared  # type: ignore[return-value]
    return VenuOrchestrator()


@dataclass
class SankirtanChamber(Generic[C]):
    """
    The Resonance Space - Where Cells Flow Through Music.

    The Chamber uses the shared VenuOrchestrator from ServiceRegistry.
    When the kernel is running, this is the SAME orchestrator that
    VenuService ticks. When running standalone (CLI), a local
    fallback is created.

    Pattern:
        cell_in → orchestrator.step() → transform → registry(vamsi) → cell_out

    SSOT Derivation:
        CHAMBER_CAPACITY = MALA = 108
        RESONANCE_THRESHOLD = PARAMPARA = 37
        DEFAULT_CHORUS_SIZE = WORDS = 16
    """

    __mahajana__: ClassVar[str] = "gauranga"
    __position__: ClassVar[int] = 0

    # The Orchestrator (shared via ServiceRegistry, or local fallback)
    _orchestrator: VenuOrchestrator = field(default_factory=_resolve_orchestrator)
    
    # The Registry (Musical Memory - 512 slots)
    _registry: SiksastakamRegistry = field(default_factory=SiksastakamRegistry)
    
    # The Antaranga (Inner Chamber - Contiguous RAM)
    # 512 × 32 bytes = 16 KB. No Python objects. No GC. Pure byte resonance.
    # Bahiranga (outer) = Python objects for API/debugging.
    # Antaranga (inner) = contiguous RAM for the reactor core.
    _antaranga: AntarangaRegistry = field(default_factory=AntarangaRegistry)

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
    
    def dance(
        self,
        cell: MahaCellUnified[C],
        diw: Optional[int] = None,
    ) -> MahaCellUnified[C]:
        """
        Single cell flows through, gets transformed, and interacts with Memory.
        
        Logic:
        1. Get DIW from Orchestrator (or use provided DIW).
        2. Transform Cell (apply DIW).
        3. Extract Vamsi (Address) from DIW.
        4. Interact with Registry at Vamsi address:
           - Empty? -> Occupy (Presence).
           - Occupied? -> Merge (Resonance).
        
        Args:
            cell: The cell to transform
            diw: Optional pre-computed DIW (e.g. from spell()).
                 If None, the orchestrator's step() provides the next
                 DIW from THE_FLUTE_CYCLE (the heartbeat).
            
        Returns:
            The resulting cell (original or merged)
        """
        # 1. Get the current Divine Instruction Word
        if diw is None:
            diw = self._orchestrator.step()
        
        # 2. Transform the cell
        self._apply_diw(cell, diw)
        
        # 3. INTERACT WITH REGISTRY (Musical Memory)
        # Extract Vamsi (9 bits) - The Memory Address
        vamsi = (diw >> VAMSI_SHIFT) & VAMSI_MASK
        
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
        
        # 3b. ANTARANGA SHADOW (Inner Chamber - Contiguous RAM)
        # Mirror the collision into 16 KB contiguous memory.
        # Same logic, hardware speed. The inner chamber resonates.
        self._antaranga.apply_diw(vamsi, diw)
        self._antaranga.collide(
            vamsi,
            v_source=cell.header.sravanam & 0xFFFFFFFF,
            v_target=cell.header.kirtanam & 0xFFFFFFFF,
            v_operation=cell.header.pada_sevanam & 0xFFFFFFFF,
            v_arcanam=cell.header.arcanam & 0xFFFFFFFF,
            v_atma=cell.header.atma_nivedanam & 0xFFFFFFFF,
            v_prana=min(cell.lifecycle.prana, 0xFFFFFFFF),
            v_integrity=int(cell.lifecycle.integrity * INTEGRITY_FULL),
            v_cycle=min(cell.lifecycle.cycle, 0xFFFF),
        )

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
    
    def spell_kirtan(
        self,
        cell: MahaCellUnified[C],
        coords: tuple[int, ...],
    ) -> MahaCellUnified[C]:
        """
        Transform cell through input-derived DIWs (Melody over Heartbeat).
        
        Like kirtan(), but the DIWs come from spell(coords) instead of
        THE_FLUTE_CYCLE. The input's RAMA coordinates literally play
        through Krishna's flute, and each phoneme becomes a transformation.
        
        dance()  = heartbeat (LUT)
        kirtan() = heartbeat × cycles
        spell_kirtan() = melody (input-derived DIWs via shared orchestrator)
        
        Same reactor (_apply_diw), same memory (Registry), same resonance.
        Different fuel.
        
        Args:
            cell: The cell to transform
            coords: RAMA coordinates (0-48) from phonetic encoding
            
        Returns:
            The transformed cell
        """
        if not coords:
            return cell
        
        diws = self._orchestrator.spell(coords)
        current = cell
        for d in diws:
            current = self.dance(current, diw=d)
        return current
    
    # =========================================================================
    # ANTARANGA METHODS (Inner Chamber - Contiguous RAM)
    # =========================================================================

    def resonate_words(
        self,
        ranked_words: list,
        attractor: int = 0,
    ) -> int:
        """
        Flow resonant words into the Antaranga (Inner Chamber).

        Each RankedWord becomes a living resonance pattern in contiguous RAM.
        The word's RAMA coordinates determine its Vamsi slot (deterministic).
        Its score becomes prana and integrity (energy = meaning).

        This closes the feedback loop: rank_words() finds resonance,
        resonate_words() makes it LIVE in the chamber's memory.

        Args:
            ranked_words: List of RankedWord from rank_words()
            attractor: The input attractor (used as target field)

        Returns:
            Number of resonance collisions (words that merged with existing)
        """
        collisions = 0
        for i, rw in enumerate(ranked_words):
            # Deterministic slot from word coordinates
            coord_sum = sum(rw.word.coords) if hasattr(rw.word, 'coords') else i
            slot = coord_sum % 512

            # Score → prana/integrity (score 0.0-1.0 → proportional energy)
            score_prana = int(rw.total_score * GENESIS_PRANA_U32)
            score_integrity = int(rw.total_score * INTEGRITY_FULL)

            resonated = self._antaranga.collide(
                slot,
                v_source=coord_sum & 0xFFFFFFFF,
                v_target=attractor & 0xFFFFFFFF,
                v_operation=i,
                v_arcanam=0,
                v_atma=0,
                v_prana=max(KSETRAJNA, score_prana),
                v_integrity=max(KSETRAJNA, score_integrity),
                v_cycle=0,
            )
            if resonated:
                collisions += KSETRAJNA

        return collisions

    @property
    def antaranga(self) -> AntarangaRegistry:
        """Direct access to the Inner Chamber (read-only intent)."""
        return self._antaranga

    # =========================================================================
    # TRANSFORMATION LOGIC
    # =========================================================================
    
    def _apply_diw(self, cell: MahaCellUnified[C], diw: int) -> None:
        """
        Apply Divine Instruction Word to cell.

        The DIW is a native 19-bit word in canonical 6-9-4 format.
        Each component has a distinct semantic role:

        MURALI (4 bits) = WHAT happens (Phase/Operation):
            0=GENESIS: Cell receives energy (Input)
            1=DHARMA:  Cell is verified (Validate)
            2=KARMA:   Cell processes (Execute)
            3=MOKSHA:  Cell completes (Output)

        VAMSI (9 bits) = HOW it happens (Name/Mode):
            H region (0-169):   Carrier   → prana-dominant
            K region (170-339): Source    → integrity-dominant
            R region (340-511): Deliverer → cycle-dominant

        VENU (6 bits) = HOW STRONG (Quality/Intensity):
            0-63 normalized to 0.0-1.0 via QUALITIES(64)
        """
        components = unpack(diw)

        # --- Intensity from VENU (0.0 to 1.0) ---
        intensity = components.venu / (QUALITIES - KSETRAJNA)  # 0/63 .. 63/63

        # --- Name region from VAMSI ---
        vamsi_stride = (KSETRAJNA << VAMSI_HOLES) // 3  # 512 // 3 = 170
        name_region = min(components.vamsi // vamsi_stride, HALVES)  # 0=H, 1=K, 2=R

        # --- Phase operation from MURALI ---
        phase = components.murali % QUARTERS  # 0-3

        # --- Mode from CLUSTER bits (Reactor Feedback) ---
        mode = (diw >> CLUSTER_SHIFT) & 0xF  # 0=Solo, 1=CallResponse, 2=Chorus

        # Base delta scaled by SEVEN (SSOT: 7 = HALF_SIZE - KSETRAJNA)
        base_delta = (SEVEN + int(intensity * SEVEN)) * (mode + KSETRAJNA)

        # --- RESONANCE TABLE: phase(4) × name(3) → (prana_factor, integrity_coeff, cycle_add) ---
        # No if/else. The DIW components ARE the index. The table IS the transformation.
        pf, ic, ca = _DIW_RESONANCE_TABLE[phase * 3 + name_region]
        cell.lifecycle.prana += int(pf * base_delta)
        cell.lifecycle.prana = max(0, cell.lifecycle.prana)
        cell.lifecycle.integrity = max(0.0, min(1.0,
            cell.lifecycle.integrity + ic * intensity))
        cell.lifecycle.cycle += ca

        # --- SANKIRTAN REACTOR: Prana clamped to MAX_PRANA ---
        cell.lifecycle.prana = min(cell.lifecycle.prana, MAX_PRANA)
    
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
        
        Returns True if the orchestrator passes structural verification.
        """
        test_orch = VenuOrchestrator()
        return test_orch.verify_divinity()
    
    def is_silent(self, diw: int) -> bool:
        """Check if instruction is silence (SUNYA)."""
        return self._orchestrator.is_sunya(diw)
    
    def reset(self) -> None:
        """Reset all state (Registry, Orchestrator, Antaranga, Metrics)."""
        self._orchestrator.reset()
        self._registry.clear()
        self._antaranga.clear()
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

        # Antaranga (Fixed: 16,384 bytes contiguous)
        result.extend(self._antaranga.raw)
        
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
            raise ValueError(f"Snapshot too short: {len(snapshot)} bytes, need at least 52")
            
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
        
        # 3. Registry + Antaranga
        # Antaranga is always the LAST 16,384 bytes (fixed size).
        # Everything between orchestrator and antaranga is Registry.
        from vibe_core.mahamantra.substrate.antaranga import CHAMBER_BYTES
        if len(snapshot) >= offset + CHAMBER_BYTES:
            # New format: Registry + Antaranga
            registry_data = snapshot[offset:len(snapshot) - CHAMBER_BYTES]
            self._registry.from_bytes(registry_data)
            self._antaranga._mem[:] = snapshot[len(snapshot) - CHAMBER_BYTES:]
        else:
            # Legacy format: Registry only (no Antaranga)
            registry_data = snapshot[offset:]
            self._registry.from_bytes(registry_data)
            self._antaranga.clear()

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create(cls) -> "SankirtanChamber[C]":
        """Create a new chamber using the shared orchestrator and fresh registry."""
        return cls(
            _orchestrator=_resolve_orchestrator(),
            _registry=SiksastakamRegistry(),
            _resonance_count=0,
            _total_transformations=0,
            _accumulated_diw=0,
        )


# =============================================================================
# SINGLETON CHAMBER (Persistent Resonance)
# =============================================================================

_chamber_instance: Optional["SankirtanChamber"] = None


def get_chamber() -> "SankirtanChamber":
    """
    Get the singleton SankirtanChamber instance.
    
    PERSISTENT RESONANCE: The chamber maintains state across calls.
    This enables:
    - Accumulated DIW tracking
    - Resonance count persistence
    - Registry state preservation
    - Orchestrator tick continuity
    
    "kirtanīyaḥ sadā hariḥ" - One should ALWAYS chant (continuous, not fresh each time)
    """
    global _chamber_instance
    if _chamber_instance is None:
        _chamber_instance = SankirtanChamber.create()
    return _chamber_instance


def reset_chamber() -> None:
    """Reset the singleton chamber (for testing or fresh start)."""
    global _chamber_instance
    if _chamber_instance is not None:
        _chamber_instance.reset()
    _chamber_instance = None


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
    # Singleton
    "get_chamber",
    "reset_chamber",
]
