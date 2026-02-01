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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 5
__genesis__ = "0xb5c3a829"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Final, ClassVar, Optional, Dict, Generic, TypeVar, Tuple, Any
import uuid

from vibe_core.mahamantra.protocols._seed import (
    # Prana constants
    MAHA_QUANTUM,
    TRINITY,
    PARAMPARA,
    JIVA_QUALITIES,
    JIVA_CYCLE,
    # Cell structure
    NAVA,
    WORDS,
    MALA,
    COSMIC_FRAME,
    # Membrane
    HALF_SIZE,
)
from vibe_core.mahamantra.protocols._header import (
    MahaHeader,
    NavaBhaktiField,
    HEADER_SIZE_BYTES,
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
MITOSIS_THRESHOLD: Final[int] = MAHA_QUANTUM * 2

# Membrane integrity threshold for signal processing: 20%
MEMBRANE_MIN_INTEGRITY: Final[float] = 0.2

# Maximum age (cycles) before apoptosis: JIVA_CYCLE = 432
MAX_AGE_CYCLES: Final[int] = JIVA_CYCLE


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
    integrity: float = 1.0  # 0.0 to 1.0
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
    __position__: ClassVar[int] = 5
    
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
    def membrane_integrity(self) -> float:
        """Health of the boundary (0.0 - 1.0)."""
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
        self.lifecycle.integrity = 1.0
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
        self.lifecycle.cycle += 1
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
        self.lifecycle.integrity -= 0.01  # 1% wear per signal
        if self.lifecycle.integrity < 0:
            self.lifecycle.integrity = 0.0
        
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
            raise RuntimeError(
                f"Not enough prana for mitosis "
                f"(Need {MITOSIS_THRESHOLD}, Has {self.lifecycle.prana})"
            )
        
        # Split prana
        half_prana = self.lifecycle.prana // 2
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
        
        child = MahaCellUnified[S, M](
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
        self.lifecycle.integrity = 0.0
    
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
            
        # I am Active. We Resonate.
        # Merge visitor into self
        self.lifecycle.prana += visitor.lifecycle.prana
        self.lifecycle.integrity = (self.lifecycle.integrity + visitor.lifecycle.integrity) / 2
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
        integrity_fixed = int(self.lifecycle.integrity * (1 << 32))
        result.extend(struct.pack("<Q", integrity_fixed))
        result.extend(struct.pack("<Q", self.lifecycle.cycle))
        
        # Active flag + DNA length
        dna_bytes = self.lifecycle.dna.encode("utf-8")
        flags = (1 if self.lifecycle.is_active else 0) | (len(dna_bytes) << 1)
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
        prana = struct.unpack("<Q", data[offset:offset+8])[0]
        offset += 8
        
        integrity_fixed = struct.unpack("<Q", data[offset:offset+8])[0]
        integrity = integrity_fixed / (1 << 32)
        offset += 8
        
        cycle = struct.unpack("<Q", data[offset:offset+8])[0]
        offset += 8
        
        flags = struct.unpack("<Q", data[offset:offset+8])[0]
        offset += 8
        
        is_active = bool(flags & 1)
        dna_len = flags >> 1
        
        # 3. DNA
        if len(data) < offset + dna_len:
            raise ValueError("Data too short for DNA content")
            
        dna_bytes = data[offset:offset+dna_len]
        dna = dna_bytes.decode("utf-8")
        offset += dna_len
        
        # Reconstruct
        cell = cls(
            header=header,
            lifecycle=CellLifecycleState(
                prana=prana,
                integrity=integrity,
                cycle=cycle,
                is_active=is_active,
                dna=dna
            ),
            payload=None, # Payload not serialized by default in unified model
        )
        
        return cell, offset
    
    def get_organelles(self) -> Dict[str, object]:
        """List internal components."""
        return {
            "nucleus": "active" if self.lifecycle.is_active else "inactive",
            "mitochondria": f"{self.lifecycle.prana} prana",
            "membrane": f"{self.lifecycle.integrity:.2%} integrity",
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
                integrity=1.0,
                cycle=0,
                is_active=True,
                dna=dna,
            ),
            payload=initial_state,
        )
        
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
                integrity=0.0,
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
