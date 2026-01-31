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
__genesis__ = "0xa2b9f456"  # GenesisByte: parampara % 37 == 0

from typing import Final, ClassVar, Tuple

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
assert _position_xor == (1 << WORDS) - 1, "All 16 position bits must be touched exactly once"

# Count name occurrences
_hare_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 0)
_krishna_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 1)
_rama_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 2)
assert _hare_count == HARE_COUNT, f"HARE count must be {HARE_COUNT}"
assert _krishna_count == 4, "KRISHNA count must be 4"
assert _rama_count == 4, "RAMA count must be 4"


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
    
    __slots__ = ('_tick', '_prev_state')
    
    def __init__(self) -> None:
        self._tick: int = 0
        self._prev_state: int = 0
    
    @property
    def tick(self) -> int:
        """Current tick position."""
        return self._tick
    
    def step(self) -> int:
        """
        One step through the Mahamantra.
        Returns delta (XOR with previous state) = the melody.
        
        O(1) - just a LUT lookup, no ALU operations.
        """
        # O(1) lookup - no computation!
        new_state = THE_FLUTE_CYCLE[self._tick % WORDS]
        
        # Calculate delta (the melody!)
        delta = self._prev_state ^ new_state
        
        # Update state
        self._prev_state = new_state
        self._tick = (self._tick + 1) % COSMIC_FRAME  # Prevent overflow
        
        return delta
    
    def cycle(self) -> int:
        """
        Complete 16-step cycle.
        Returns XOR of all position bits from all 16 LUT entries.
        
        This is the "Mathematical Proof of Divinity" test.
        XOR(all 16 position bits) = 0xFFFF (each bit set exactly once).
        
        Note: This reads directly from the LUT for verification purposes,
        while step() is for runtime execution with delta tracking.
        """
        accumulated = 0
        for i in range(WORDS):
            # Direct LUT read - get the state at position i
            state = THE_FLUTE_CYCLE[i]
            # Accumulate position bits (lower 16 bits)
            accumulated ^= (state & 0xFFFF)
        
        # Advance tick (for consistency if called during runtime)
        self._tick = (self._tick + WORDS) % COSMIC_FRAME
        
        return accumulated
    
    def verify_divinity(self) -> bool:
        """
        The "Beweis Gottes" Test.
        
        Runs full cycle and asserts:
        - XOR of positions = 0xFFFF (all 16 position bits touched)
        - Total XOR % MAHA_QUANTUM = POSITION_SUM_RAMA (49)
        - Total XOR % PARAMPARA = HARE_COUNT (8)
        
        Returns True if all assertions pass.
        Raises AssertionError if any fail.
        """
        # Reset state for clean test
        self._tick = 0
        self._prev_state = 0
        
        # Run one complete cycle
        xor_positions = self.cycle()
        
        # The expected value: all 16 bits set = 0xFFFF = 65535
        expected_xor = (1 << WORDS) - 1
        
        assert xor_positions == expected_xor, \
            f"Position XOR must be {hex(expected_xor)}, got {hex(xor_positions)}"
        
        # Verify modular properties against SSOT constants
        # 65535 % 137 = 49 = POSITION_SUM_RAMA
        assert xor_positions % MAHA_QUANTUM == POSITION_SUM_RAMA, \
            f"Must resonate to Rama ({POSITION_SUM_RAMA})"
        
        # 65535 % 37 = 8 = HARE_COUNT
        assert xor_positions % PARAMPARA == HARE_COUNT, \
            f"Must be protected by Hare ({HARE_COUNT})"
        
        return True
    
    def route(self, seed: int) -> Tuple[int, int, int]:
        """
        Route seed through the orchestra.
        
        Args:
            seed: Input value to route
            
        Returns:
            (venu_state, vamsi_state, murali_state)
        """
        # Modulate seed through each flute
        venu = (seed * SEVEN) % (1 << self.VENU_BITS)
        vamsi = (seed + TEN) % (1 << self.VAMSI_BITS)
        murali = (seed * seed) % (1 << self.MURALI_BITS)
        
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
        """
        Combine three flute states into 32-bit Instruction Word.
        
        Bits 0-5:   VENU (6 bits)
        Bits 6-14:  VAMSI (9 bits)
        Bits 15-18: MURALI (4 bits)
        Bits 19-22: Velocity (4 bits)
        Bits 23-26: Cluster routing (4 bits)
        Bits 27-30: Reserved (4 bits)
        Bit 31:     SUNYA flag (silence/no-op)
        """
        # Mask each component to its bit width
        venu_masked = venu & ((1 << self.VENU_BITS) - 1)
        vamsi_masked = vamsi & ((1 << self.VAMSI_BITS) - 1)
        murali_masked = murali & ((1 << self.MURALI_BITS) - 1)
        
        # 19-bit DIW core
        diw = (murali_masked << MURALI_SHIFT) | (vamsi_masked << VAMSI_SHIFT) | venu_masked
        
        # 13-bit metadata
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
