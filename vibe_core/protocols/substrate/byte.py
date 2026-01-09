"""
SUBSTRATE PROTOCOL - Layer 0 (Fractal Edition)
==============================================

"The Word is not 16-bit. The Word is n-bit."

Defines 'MantraBit' as a Fractal Value Type (Infinite Precision).
PROMPT-MANDATE: "Protocol first! No limits."
"""

from dataclasses import dataclass, field
from typing import NewType, Union, List
from datetime import datetime

# Strict Typing for infinite integers
FractalInt = NewType("FractalInt", int)

class MantraBit:
    """
    A Fractal Bit Field.
    Unlike a standard 16-bit integer, this can expand to hold
    the vibration of any n-harmonic universe.
    """
    def __init__(self, value: Union[int, FractalInt]):
        self._val = value

    @classmethod
    def from_n(cls, n: int) -> "MantraBit":
        """Creates a Purnam (Complete) resonance for dimension n."""
        # Equivalent to 2^n - 1 (All bits set to 1)
        # E.g., for n=16 -> 0xFFFF
        # E.g., for n=108 -> 2^108 - 1
        return cls((1 << n) - 1)

    @property
    def is_purnam(self) -> bool:
        """
        Checks if the state is 'Full' (No missing bits).
        Detects voids/holes in the resonance.
        """
        # In binary, a perfect sequence has no zeros between ones if filled.
        # But logically, Purnam means 'All Potential Manifested'.
        # We check if (val + 1) is a power of 2.
        return (self._val & (self._val + 1)) == 0

    def check_resonance(self, target_n: int) -> float:
        """
        Returns the percentage of resonance against a target dimension.
        """
        target = (1 << target_n) - 1
        intersection = self._val & target
        return intersection.bit_count() / target.bit_count()

    def __repr__(self) -> str:
        return f"MantraBit(0x{self._val:X})"

    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self._val == other
        if isinstance(other, MantraBit):
            return self._val == other._val
        return False
    
    # Allow bitwise operations for Fractal Composability
    def __or__(self, other): 
        val = other._val if isinstance(other, MantraBit) else other
        return MantraBit(self._val | val)
    
    def __and__(self, other): 
        val = other._val if isinstance(other, MantraBit) else other
        return MantraBit(self._val & val)
        
    def __xor__(self, other):
        val = other._val if isinstance(other, MantraBit) else other
        return MantraBit(self._val ^ val)
        
    def __invert__(self): return MantraBit(~self._val)
    
    @property
    def value(self) -> int:
        return self._val

    @classmethod
    def full_resonance(cls) -> "MantraBit":
        """Backwards compatibility for 16-bit full resonance."""
        return cls.from_n(16)

# COMPATIBILITY CONSTANTS (Mimic Enum Behavior)
MantraBit.HARE_1 = MantraBit(1 << 0)
MantraBit.KRISHNA_1 = MantraBit(1 << 1)
MantraBit.HARE_2 = MantraBit(1 << 2)
MantraBit.KRISHNA_2 = MantraBit(1 << 3)
MantraBit.KRISHNA_3 = MantraBit(1 << 4)
MantraBit.KRISHNA_4 = MantraBit(1 << 5)
MantraBit.HARE_3 = MantraBit(1 << 6)
MantraBit.HARE_4 = MantraBit(1 << 7)
MantraBit.HARE_5 = MantraBit(1 << 8)
MantraBit.RAMA_1 = MantraBit(1 << 9)
MantraBit.HARE_6 = MantraBit(1 << 10)
MantraBit.RAMA_2 = MantraBit(1 << 11)
MantraBit.RAMA_3 = MantraBit(1 << 12)
MantraBit.RAMA_4 = MantraBit(1 << 13)
MantraBit.HARE_7 = MantraBit(1 << 14)
MantraBit.HARE_8 = MantraBit(1 << 15)



@dataclass(frozen=True)
class GenesisByte:
    """
    The Seed (Bijam).
    Now supports n-dimensional resonance.
    """
    signature: str = ""
    resonance: MantraBit = field(default_factory=lambda: MantraBit(0))
    dimension: int = 16 # Default to 16-bit (Standard Boot)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    parampara_hash: str = "0x25" # 37

    def validate(self) -> bool:
        # 1. Fractal Purnam Check
        # Does the resonance match the claimed dimension?
        target_resonance = MantraBit.from_n(self.dimension)
        
        # Allow resonance to be HIGHER than target (Supremacy), but not lower
        # But logically, Genesis must be EXACT or FULL for that dimension.
        if self.resonance != target_resonance:
             # Calculate missing "Sound"
             raise SystemError(f"Fractal Fracture: Expected {target_resonance}, got {self.resonance}")

        # 2. Mayavad Check
        if not self.signature or self.signature == "None":
             raise PermissionError("Voidist Launch Detected. Identity required.")

        # 3. Lineage (Standard)
        if not self._verify_lineage():
             raise ConnectionError("Sahajiya Fault: Invalid Parampara Hash.")
             
        return True
        
    @property
    def is_valid(self) -> bool:
        """Legacy property check."""
        try:
            return self.validate()
        except Exception:
            return False

    def _verify_lineage(self) -> bool:
        # GURU_PRIME is constant regardless of dimension (37)
        try:
            return (int(self.parampara_hash, 16) % 37) == 0
        except ValueError:
            return False

# =============================================================================
# BACKWARD COMPATIBILITY: THE 16-STEP SEQUENCE
# =============================================================================
MANTRA_SEQUENCE: List[MantraBit] = [
    MantraBit.HARE_1, MantraBit.KRISHNA_1, MantraBit.HARE_2, MantraBit.KRISHNA_2,
    MantraBit.KRISHNA_3, MantraBit.KRISHNA_4, MantraBit.HARE_3, MantraBit.HARE_4,
    MantraBit.HARE_5, MantraBit.RAMA_1, MantraBit.HARE_6, MantraBit.RAMA_2,
    MantraBit.RAMA_3, MantraBit.RAMA_4, MantraBit.HARE_7, MantraBit.HARE_8
]
