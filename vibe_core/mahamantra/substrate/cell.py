"""
MAHA CELL UNIFIED - The Complete Computational Unit
====================================================

"jīvera 'svarūpa' haya — kṛṣṇera 'nitya-dāsa'"
"The constitutional position of the living entity is that of an eternal servant of Krishna"
— Chaitanya Charitamrita, Madhya 20.108

MahaCellUnified = MahaHeader (Identity) + Lifecycle (Jiva)

This is THE fundamental unit of computation in the Mahamantra architecture.
Every cell carries its 72-byte header and biological state.

ALL VALUES DERIVED FROM SSOT (_seed.py). NO HARDCODING. NO `Any`.
"""

from vibe_core.mahamantra.protocols._seed import HALVES, HARE_COUNT, KSETRAJNA, PANCHA, TEN

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = PANCHA
__genesis__ = "0x001740aa"  # GenesisByte: parampara % 37 == 0

import uuid
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Final, Generic, Optional, Tuple, TypeVar

from vibe_core.mahamantra.protocols._header import (
    HEADER_SIZE_BYTES,
    MahaHeader,
    NavaBhaktiField,
)
from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    # Membrane
    HALF_SIZE,
    JIVA_CYCLE,
    JIVA_QUALITIES,
    # Prana constants
    MAHA_QUANTUM,
    MALA,
    # Cell structure
    NAVA,
    PARAMPARA,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra.protocols.cell import MahaCellProtocol

# =============================================================================
# TYPE VARIABLES
# =============================================================================

S = TypeVar("S")  # State type
M = TypeVar("M")  # Message type


# =============================================================================
# CELL CONSTANTS (DERIVED FROM SSOT)
# =============================================================================

# Initial Prana: 100 × MAHA_QUANTUM = 13700
GENESIS_PRANA: Final[int] = MAHA_QUANTUM * 100

# Metabolic cost per cycle: TRINITY = 3
METABOLIC_COST: Final[int] = TRINITY

# Minimum prana required for mitosis: 2 × MAHA_QUANTUM = 274
MITOSIS_THRESHOLD: Final[int] = MAHA_QUANTUM * HALVES

# Membrane integrity threshold for signal processing: CF // PANCHA = 4320 (20%)
MEMBRANE_MIN_INTEGRITY: Final[int] = COSMIC_FRAME // PANCHA  # 4320

# Signal wear per processing: CF // (TEN * TEN) = 216 (1%)
_SIGNAL_WEAR: Final[int] = COSMIC_FRAME // (TEN * TEN)  # 216

# Maximum age (cycles) before apoptosis: JIVA_CYCLE = 432
MAX_AGE_CYCLES: Final[int] = JIVA_CYCLE

# Maximum prana: GENESIS_PRANA × MALA = 13700 × 108 = 1,479,600
# A cell cannot hold more energy than all chamber cells combined.
MAX_PRANA: Final[int] = MAHA_QUANTUM * 100 * MALA


# =============================================================================
# CELL LIFECYCLE STATE
# =============================================================================


@dataclass
class CellLifecycleState:
    """
    The Jiva aspect of a cell - internal biological state.

    Separate from the header (identity) to allow independent mutation.
    """

    prana: int = GENESIS_PRANA
    integrity: int = COSMIC_FRAME  # 0 to COSMIC_FRAME (membrane health)
    cycle: int = 0
    is_active: bool = False
    dna: str = ""


# =============================================================================
# MAHA CELL UNIFIED
# =============================================================================


@dataclass
class MahaCellUnified(MahaCellProtocol[S, object], Generic[S]):
    """
    The Complete Computational Unit.

    Combines:
    - MahaHeader: 72-byte identity (immutable)
    - CellLifecycleState: Jiva state (mutable)
    - Payload: Generic state S

    Pattern: Composition, not inheritance.

    SSOT Derivation:
        GENESIS_PRANA = MAHA_QUANTUM × 100 = 137 × 100 = 13700
        METABOLIC_COST = TRINITY = 3
        MAX_AGE_CYCLES = JIVA_CYCLE = 432
        MITOSIS_THRESHOLD = MAHA_QUANTUM × 2 = 274
    """

    __mahajana__: ClassVar[str] = "prahlada"
    __position__: ClassVar[int] = PANCHA

    # Identity (immutable)
    header: MahaHeader

    # Lifecycle (mutable)
    lifecycle: CellLifecycleState = field(default_factory=CellLifecycleState)

    # Payload (generic state)
    payload: Optional[S] = None

    # Cell ID (derived from header source)
    _cell_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        """Validate cell on creation."""
        if not self.header.is_valid():
            raise ValueError("Cell header must be valid (parampara + checksum)")

    @property
    def id(self) -> str:
        """Unique cell ID."""
        return self._cell_id

    @property
    def state(self) -> Optional[S]:
        """Current internal state (Observation)."""
        return self.payload

    @property
    def prana(self) -> int:
        """Current energy level."""
        return self.lifecycle.prana

    @property
    def membrane_integrity(self) -> int:
        """Health of the boundary (0 to COSMIC_FRAME, 21600 = 100%)."""
        return self.lifecycle.integrity

    @property
    def is_alive(self) -> bool:
        """Check if cell is alive."""
        return self.lifecycle.is_active and self.lifecycle.prana > 0

    @property
    def age(self) -> int:
        """Number of metabolic cycles completed."""
        return self.lifecycle.cycle

    # =========================================================================
    # LIFECYCLE METHODS
    # =========================================================================

    def conceive(self, dna: str, genesis_state: S) -> None:
        """
        Initialize the cell (Birth/Janma).

        Args:
            dna: Genetic code (instructions)
            genesis_state: Initial payload state
        """
        self.lifecycle.dna = dna
        self.lifecycle.is_active = True
        self.lifecycle.cycle = 0
        self.lifecycle.integrity = COSMIC_FRAME
        self.lifecycle.prana = GENESIS_PRANA
        self.payload = genesis_state

    def metabolize(self, energy: int) -> int:
        """
        Process energy (Karma).

        Cost of living = TRINITY (3) units per cycle.

        Args:
            energy: Energy to absorb

        Returns:
            New prana level, 0 if cell died
        """
        if not self.lifecycle.is_active:
            return 0

        # Metabolic cost
        self.lifecycle.prana -= METABOLIC_COST
        self.lifecycle.prana += energy

        # Check starvation
        if self.lifecycle.prana <= 0:
            self.lifecycle.prana = 0
            self.apoptosis()
            return 0

        # Age check
        self.lifecycle.cycle += KSETRAJNA
        if self.lifecycle.cycle >= MAX_AGE_CYCLES:
            self.apoptosis()
            return 0

        return self.lifecycle.prana

    def signal(self, message: object) -> Optional[object]:
        """
        Process incoming signal via Membrane.

        Requires integrity > MEMBRANE_MIN_INTEGRITY (20%).

        Args:
            message: Incoming signal

        Returns:
            Processed message or None if rejected
        """
        if not self.lifecycle.is_active:
            return None

        # Membrane check
        if self.lifecycle.integrity < MEMBRANE_MIN_INTEGRITY:
            return None  # Membrane too weak

        # Signal processing costs integrity
        self.lifecycle.integrity -= _SIGNAL_WEAR  # 216 per signal (1%)
        if self.lifecycle.integrity < 0:
            self.lifecycle.integrity = 0

        return message

    def mitosis(self) -> "MahaCellUnified[S]":
        """
        Divide into two cells (Reproduction).

        Requires prana >= MITOSIS_THRESHOLD (274).
        Both parent and child get half the prana.

        Returns:
            New child cell

        Raises:
            RuntimeError: If not enough prana
        """
        if self.lifecycle.prana < MITOSIS_THRESHOLD:
            raise RuntimeError(f"Not enough prana for mitosis (Need {MITOSIS_THRESHOLD}, Has {self.lifecycle.prana})")

        # Split prana
        half_prana = self.lifecycle.prana // HALVES
        self.lifecycle.prana = half_prana

        # Create child with new header (same source/target, new link)
        child_header = MahaHeader.create(
            source=self.header.sravanam,
            target=self.header.kirtanam,
            operation=self.header.pada_sevanam,
            link=hash(self._cell_id) & 0xFFFFFFFFFFFFFFFF,
            intent=self.header.vandanam,
            ttl=self.header.dasyam,
            state=self.header.sakhyam,
        )

        child = MahaCellUnified[S](
            header=child_header,
            lifecycle=CellLifecycleState(
                prana=half_prana,
                integrity=self.lifecycle.integrity,
                cycle=0,  # Child starts fresh
                is_active=True,
                dna=self.lifecycle.dna,
            ),
            payload=self.payload,  # Clone payload reference
        )

        return child

    def apoptosis(self) -> None:
        """Self-destruct (Death/Mrityu)."""
        self.lifecycle.is_active = False
        self.lifecycle.prana = 0
        self.lifecycle.integrity = 0

    def homeostasis(self) -> bool:
        """
        Maintain balance.

        Checks Prana and Integrity. Triggers apoptosis if invalid.

        Returns:
            True if cell remains alive
        """
        if self.lifecycle.prana <= 0:
            self.apoptosis()
            return False

        if self.lifecycle.integrity <= 0:
            self.apoptosis()
            return False

        return True

    # =========================================================================
    # INTERACTION METHODS (Branchless Sunya)
    # =========================================================================

    def interact(self, visitor: "MahaCellUnified[S, M]") -> "MahaCellUnified[S, M]":
        """
        Interact with a visitor cell.

        Polymorphic behavior:
        - If I am NULL (Silence): I disappear, Visitor takes the spot (Presence).
        - If I am ACTIVE (Sound): We Resonate/Merge.

        Args:
            visitor: The incoming cell

        Returns:
            The resulting cell (Visitor or Merged)
        """
        # If I am inactive (Null/Silence), checking Prana or Flag
        if not self.lifecycle.is_active:
            # I am Silence. Visitor becomes the Sound.
            return visitor

        # Self-interaction is a no-op (identity, not resonance)
        if self is visitor:
            return self

        # I am Active. We Resonate.
        # Merge visitor into self (capped at MAX_PRANA to prevent overflow)
        self.lifecycle.prana = min(self.lifecycle.prana + visitor.lifecycle.prana, MAX_PRANA)
        self.lifecycle.integrity = (self.lifecycle.integrity + visitor.lifecycle.integrity) // HALVES
        # Note: We return SELF (the Resident), now empowered.
        return self

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_bytes(self) -> bytes:
        """
        Serialize cell to bytes.

        Format:
            [72 bytes: header]
            [8 bytes: prana (uint64)]
            [8 bytes: integrity as fixed-point (uint64)]
            [8 bytes: cycle (uint64)]
            [8 bytes: is_active + dna_length (uint64)]
            [N bytes: dna (utf-8)]

        Returns:
            bytes representation
        """
        import struct

        result = bytearray()

        # Header (72 bytes)
        result.extend(self.header.to_bytes())

        # Lifecycle state
        result.extend(struct.pack("<Q", self.lifecycle.prana))
        result.extend(struct.pack("<Q", self.lifecycle.integrity))
        result.extend(struct.pack("<Q", self.lifecycle.cycle))

        # Active flag + DNA length
        dna_bytes = self.lifecycle.dna.encode("utf-8")
        flags = (KSETRAJNA if self.lifecycle.is_active else 0) | (len(dna_bytes) << KSETRAJNA)
        result.extend(struct.pack("<Q", flags))

        # DNA
        result.extend(dna_bytes)

        return bytes(result)

    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple["MahaCellUnified", int]:
        """
        Deserialize cell from bytes.

        Args:
            data: Byte stream

        Returns:
            Tuple[Cell, bytes_consumed]
        """
        import struct

        # Base size check
        # Header (72) + Prana (8) + Integrity (8) + Cycle (8) + Flags (8) = 104
        MIN_SIZE = HEADER_SIZE_BYTES + 32

        if len(data) < MIN_SIZE:
            raise ValueError(f"Data too short for MahaCellUnified (min {MIN_SIZE})")

        # 1. Header
        header = MahaHeader.from_bytes(data[:HEADER_SIZE_BYTES])
        offset = HEADER_SIZE_BYTES

        # 2. Lifecycle
        prana = struct.unpack("<Q", data[offset : offset + HARE_COUNT])[0]
        offset += HARE_COUNT

        integrity = struct.unpack("<Q", data[offset : offset + HARE_COUNT])[0]
        offset += HARE_COUNT

        cycle = struct.unpack("<Q", data[offset : offset + HARE_COUNT])[0]
        offset += HARE_COUNT

        flags = struct.unpack("<Q", data[offset : offset + HARE_COUNT])[0]
        offset += HARE_COUNT

        is_active = bool(flags & KSETRAJNA)
        dna_len = flags >> KSETRAJNA

        # 3. DNA
        if len(data) < offset + dna_len:
            raise ValueError("Data too short for DNA content")

        dna_bytes = data[offset : offset + dna_len]
        dna = dna_bytes.decode("utf-8")
        offset += dna_len

        # Reconstruct
        cell = cls(
            header=header,
            lifecycle=CellLifecycleState(prana=prana, integrity=integrity, cycle=cycle, is_active=is_active, dna=dna),
            payload=None,  # Payload not serialized by default in unified model
        )

        return cell, offset

    def get_organelles(self) -> Dict[str, object]:
        """List internal components."""
        return {
            "nucleus": "active" if self.lifecycle.is_active else "inactive",
            "mitochondria": f"{self.lifecycle.prana} prana",
            "membrane": f"{self.lifecycle.integrity / COSMIC_FRAME:.2%} integrity",
            "dna_length": len(self.lifecycle.dna),
            "cycles": self.lifecycle.cycle,
            "jiva_qualities": JIVA_QUALITIES,  # 50
            "header_valid": self.header.is_valid(),
        }

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================

    @classmethod
    def create(
        cls,
        source: int,
        target: int,
        operation: int,
        *,
        dna: str = "",
        initial_state: Optional[S] = None,
    ) -> "MahaCellUnified[S, M]":
        """
        Create a new cell with auto-generated header.

        Args:
            source: Source ID
            target: Target ID
            operation: Operation code
            dna: Genetic instructions
            initial_state: Initial payload

        Returns:
            New MahaCellUnified instance
        """
        header = MahaHeader.create(
            source=source,
            target=target,
            operation=operation,
        )

        cell = cls(
            header=header,
            lifecycle=CellLifecycleState(
                prana=GENESIS_PRANA,
                integrity=COSMIC_FRAME,
                cycle=0,
                is_active=True,
                dna=dna,
            ),
            payload=initial_state,
        )

        return cell

    @classmethod
    def from_content(
        cls,
        content: str,
        *,
        target: int = 0,
        initial_state: Optional[S] = None,
        register: bool = True,
    ) -> "MahaCellUnified[S]":
        """
        MahaCell = ANYTHING. Address computed from content.

        The content IS the cell. The address IS computed.
        No manual IDs - mahamantra computes everything.
        Auto-registers in global CellRouter for O(1) lookup.

        Args:
            content: Any string (file, request, data, etc.)
            target: Optional target address (default 0)
            initial_state: Optional payload state
            register: Auto-register in global router (default True)

        Returns:
            MahaCellUnified with:
            - header.sravanam = address (from MahaCompression seed)
            - header.pada_sevanam = position (0-15 in mahamantra)
            - lifecycle.dna = content
        """
        from vibe_core.mahamantra.adapters.compression import MahaCompression

        compression = MahaCompression()
        result = compression.compress(content)

        cell = cls.create(
            source=result.seed,  # ADDRESS aus content
            target=target,
            operation=result.position,  # POSITION im mahamantra (0-15)
            dna=content,
            initial_state=initial_state,
        )

        # Auto-register in global router for O(1) lookup
        if register:
            from vibe_core.mahamantra.substrate.cell_router import register_cell

            register_cell(cell)

        return cell

    @classmethod
    def null(cls) -> "MahaCellUnified[None, None]":
        """
        Create a null/sentinel cell.

        Returns:
            Inactive cell with null header
        """
        return cls(
            header=MahaHeader.null(),
            lifecycle=CellLifecycleState(
                prana=0,
                integrity=0,
                cycle=0,
                is_active=False,
                dna="",
            ),
            payload=None,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "GENESIS_PRANA",
    "METABOLIC_COST",
    "MITOSIS_THRESHOLD",
    "MAX_AGE_CYCLES",
    # Types
    "CellLifecycleState",
    "MahaCellUnified",
]
