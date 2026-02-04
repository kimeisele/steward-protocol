"""
VENU ORCHESTRATOR - The Dancing Mahamantra
==========================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

The 19-bit Divine Instruction Word (DIW):
  VENU (6 bits) + VAMSI (9 bits) + MURALI (4 bits) = 19 bits

ALL VALUES DERIVED FROM SSOT (_seed.py). NO HARDCODING.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xdd4f22d7"  # GenesisByte: parampara % 37 == 0

from typing import Final, ClassVar, Tuple
import struct

from vibe_core.mahamantra.protocols._seed import (
    # Axioms
    WORDS,
    HARE_COUNT,
    # Flute holes
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    FLUTE_HOLES_SUM,
    # Mahamantra pattern
    MAHAMANTRA_WORD_PATTERN,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
    # Verification constants
    MAHA_QUANTUM,
    PARAMPARA,
    POSITION_SUM_RAMA,
    COSMIC_FRAME,
    # Derived numbers
    SEVEN,
    TEN,
)


# =============================================================================
# NAME ENCODING (DERIVED FROM SSOT)
# =============================================================================
# Map name strings to integer encoding
# H=0, K=1, R=2 (matches HolyName enum order from byte.py)

_NAME_TO_ENCODING: Final[dict[str, int]] = {
    MAHAMANTRA_NAME_HARE: 0,      # "H" → 0
    MAHAMANTRA_NAME_KRISHNA: 1,   # "K" → 1
    MAHAMANTRA_NAME_RAMA: 2,      # "R" → 2
}


# =============================================================================
# THE FLUTE CYCLE LUT (DERIVED FROM MAHAMANTRA_WORD_PATTERN)
# =============================================================================
# Format: (name_encoding << 16) | (1 << position)
# This is O(1) lookup instead of runtime calculation


def _compute_flute_cycle() -> Tuple[int, ...]:
    """
    Compute THE_FLUTE_CYCLE from MAHAMANTRA_WORD_PATTERN (SSOT).
    
    Each entry encodes:
      - Bits 0-15: Position bit (1 << position)
      - Bits 16-17: Name encoding (H=0, K=1, R=2)
    """
    result: list[int] = []
    for pos, name in enumerate(MAHAMANTRA_WORD_PATTERN):
        encoding = _NAME_TO_ENCODING[name]
        # Format: (encoding << 16) | (1 << position)
        diw = (encoding << 16) | (1 << pos)
        result.append(diw)
    return tuple(result)


# Pre-computed at module load - O(1) access forever
THE_FLUTE_CYCLE: Final[Tuple[int, ...]] = _compute_flute_cycle()


# =============================================================================
# VERIFICATION: LUT INTEGRITY
# =============================================================================
# Verify the LUT has correct properties

assert len(THE_FLUTE_CYCLE) == WORDS, f"LUT must have {WORDS} entries"

# XOR of all entries should give us 0x7ffff (all 19 bits set)
# But wait - the encoding format puts name in high bits (16-17)
# So the XOR includes those bits. Let's verify the position bits only.
_position_xor = 0
for diw in THE_FLUTE_CYCLE:
    _position_xor ^= (diw & 0xFFFF)  # Only position bits

# P0-FIX: Replace assert with runtime check (asserts removed in python -O)
if _position_xor != (1 << WORDS) - 1:
    raise ValueError("All 16 position bits must be touched exactly once")

# Count name occurrences
_hare_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 0)
_krishna_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 1)
_rama_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 2)

# P0-FIX: Replace asserts with runtime checks
if _hare_count != HARE_COUNT:
    raise ValueError(f"HARE count must be {HARE_COUNT}, got {_hare_count}")
if _krishna_count != 4:
    raise ValueError(f"KRISHNA count must be 4, got {_krishna_count}")
if _rama_count != 4:
    raise ValueError(f"RAMA count must be 4, got {_rama_count}")


# =============================================================================
# MASKS AND CONSTANTS (ALL DERIVED)
# =============================================================================

# 19-bit DIW mask: (1 << FLUTE_HOLES_SUM) - 1 = 0x7FFFF
DIW_MASK: Final[int] = (1 << FLUTE_HOLES_SUM) - 1

# 32-bit SUNYA mask for silence/No-Op
SUNYA_MASK: Final[int] = 1 << 31

# Bit positions for 32-bit instruction word
VENU_SHIFT: Final[int] = 0
VAMSI_SHIFT: Final[int] = VENU_HOLES  # 6
MURALI_SHIFT: Final[int] = VENU_HOLES + VAMSI_HOLES  # 15
VELOCITY_SHIFT: Final[int] = FLUTE_HOLES_SUM  # 19
CLUSTER_SHIFT: Final[int] = FLUTE_HOLES_SUM + 4  # 23


# =============================================================================
# VENU ORCHESTRATOR
# =============================================================================

class VenuOrchestrator:
    """
    The Dancing Mahamantra - LUT-based O(1) Performance.

    Uses pre-computed look-up table derived from MAHAMANTRA_WORD_PATTERN.
    Pattern: rama_grid.py (SVARAS, SPARSHA_GRID as LUTs).

    "The Orchestrator plays Krishna's flute - 19 bits at a time."
    """

    __mahajana__: ClassVar[str] = "narada"
    __position__: ClassVar[int] = 2

    # Flute configuration (from _seed.py)
    VENU_BITS: ClassVar[int] = VENU_HOLES      # 6 - Low register (64 states)
    VAMSI_BITS: ClassVar[int] = VAMSI_HOLES    # 9 - Mid register (512 = SIKSASTAKAM_CACHE)
    MURALI_BITS: ClassVar[int] = MURALI_HOLES  # 4 - High register (16 = WORDS)

    __slots__ = ('_tick', '_prev_state', '_mode')

    def __init__(self) -> None:
        self._tick: int = 0
        self._prev_state: int = 0
        self._mode: int = 0  # 0=Solo, 1=CallResponse, 2=Chorus

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> "TattvaDict":
        """The 5-fold truth of VenuOrchestrator."""
        from vibe_core.mahamantra.protocols._pancha import TattvaDict
        return {
            "chaitanya": "VenuOrchestrator - The Dancing Mahamantra (19-bit DIW)",
            "nityananda": "THE_FLUTE_CYCLE LUT (pre-computed from MAHAMANTRA_WORD_PATTERN)",
            "advaita": "step() - O(1) LUT lookup + XOR + Mode injection",
            "gadadhara": f"VENU({VENU_HOLES}b) + VAMSI({VAMSI_HOLES}b) + MURALI({MURALI_HOLES}b) = 19b",
            "srivasa": f"WORDS ({WORDS}), COSMIC_FRAME ({COSMIC_FRAME})",
        }

    @property
    def tick(self) -> int:
        """Current tick position."""
        return self._tick

    @property
    def mode(self) -> int:
        """Current Kirtan Mode."""
        return self._mode
    
    def step(self) -> int:
        """
        One step through the Mahamantra.
        Returns delta (XOR with previous state) | Mode Flags.
        
        O(1) - just a LUT lookup + XOR + OR.
        """
        # O(1) lookup
        new_state = THE_FLUTE_CYCLE[self._tick % WORDS]
        
        # Calculate delta (the melody)
        delta = self._prev_state ^ new_state
        
        # Update state
        self._prev_state = new_state
        self._tick = (self._tick + 1) % COSMIC_FRAME
        
        # Inject Mode into Cluster Bits (Harmonic Feedback)
        # Cluster bits are 23-26 (CLUSTER_SHIFT = 23)
        # 0=Solo -> 0
        # 1=CallResp -> 1<<23
        # 2=Chorus -> 2<<23
        return delta | (self._mode << CLUSTER_SHIFT)
    
    def cycle(self) -> int:
        """
        Complete 16-step cycle.
        Returns XOR of all position bits from all 16 LUT entries.
        """
        accumulated = 0
        for i in range(WORDS):
            state = THE_FLUTE_CYCLE[i]
            accumulated ^= (state & 0xFFFF)
        
        self._tick = (self._tick + WORDS) % COSMIC_FRAME
        return accumulated
    
    def verify_divinity(self) -> bool:
        """
        The "Beweis Gottes" Test.
        """
        self._tick = 0
        self._prev_state = 0
        xor_positions = self.cycle()
        expected_xor = (1 << WORDS) - 1

        # P0-FIX: Replace assert with runtime check (asserts removed in python -O)
        if xor_positions != expected_xor:
            raise ValueError(f"Position XOR must be {hex(expected_xor)}, got {hex(xor_positions)}")
        if xor_positions % MAHA_QUANTUM != POSITION_SUM_RAMA:
            raise ValueError(f"Must resonate to Rama ({POSITION_SUM_RAMA})")
        if xor_positions % PARAMPARA != HARE_COUNT:
            raise ValueError(f"Must be protected by Hare ({HARE_COUNT})")

        return True
    
    def route(self, seed: int) -> Tuple[int, int, int]:
        """
        Route seed through the orchestra.

        All formulas use SSOT constants (SEVEN, TEN) to ensure
        full coverage of all 16 positions.

        FIX: murali was (seed * seed) % 16 which only produces 4 values
        (quadratic residues mod 16 = {0,1,4,9}). Now uses linear
        combination to reach all 16 positions.
        """
        venu = (seed * SEVEN) % (1 << self.VENU_BITS)
        vamsi = (seed + TEN) % (1 << self.VAMSI_BITS)
        murali = (seed * SEVEN + TEN) % (1 << self.MURALI_BITS)
        return (venu, vamsi, murali)
    
    def harmonize(
        self,
        venu: int,
        vamsi: int,
        murali: int,
        velocity: int = 15,
        cluster_route: int = 0,
        sunya: bool = False,
    ) -> int:
        """Combine three flute states into 32-bit Instruction Word."""
        venu_masked = venu & ((1 << self.VENU_BITS) - 1)
        vamsi_masked = vamsi & ((1 << self.VAMSI_BITS) - 1)
        murali_masked = murali & ((1 << self.MURALI_BITS) - 1)
        
        diw = (murali_masked << MURALI_SHIFT) | (vamsi_masked << VAMSI_SHIFT) | venu_masked
        
        meta = (velocity & 0xF) << VELOCITY_SHIFT
        meta |= (cluster_route & 0xF) << CLUSTER_SHIFT
        if sunya:
            meta |= SUNYA_MASK
        
        return diw | meta
    
    def is_sunya(self, diw: int) -> bool:
        """Check if instruction is silence (No-Op)."""
        return bool(diw & SUNYA_MASK)
    
    def extract_diw(self, full_word: int) -> int:
        """Extract the 19-bit DIW from a 32-bit instruction word."""
        return full_word & DIW_MASK
    
    def reset(self) -> None:
        """Reset orchestrator to initial state."""
        self._tick = 0
        self._prev_state = 0
        self._mode = 0

    def set_mode(self, mode: int) -> None:
        """Set the Kirtan Mode (Harmonic Feedback)."""
        self._mode = mode

    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    def to_bytes(self) -> bytes:
        """Serialize state (tick, prev_state, mode)."""
        return struct.pack("<QQQ", self._tick, self._prev_state, self._mode)
        
    def from_bytes(self, data: bytes) -> None:
        """Restore state."""
        MIN_SIZE = 24 # 3 * 8
        if len(data) < MIN_SIZE:
            # Backwards compatibility check for old 16-byte snapshots
            if len(data) >= 16:
                self._tick, self._prev_state = struct.unpack("<QQ", data[:16])
                self._mode = 0 # Default to Solo
                return
            raise ValueError("Data too short")
            
        self._tick, self._prev_state, self._mode = struct.unpack("<QQQ", data[:24])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "THE_FLUTE_CYCLE",
    "DIW_MASK",
    "SUNYA_MASK",
    "VENU_SHIFT",
    "VAMSI_SHIFT",
    "MURALI_SHIFT",
    # Class
    "VenuOrchestrator",
]
