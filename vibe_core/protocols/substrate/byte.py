"""
SUBSTRATE PROTOCOL - Layer 0 (Optimized Fractal Edition)
========================================================

"The Word is n-trit, packed into m-bits."

IMPLEMENTATION DETAILS:
- Storage: Packed Integers (2 bits per Trit).
- Encoding: 00=HARE, 01=KRISHNA, 10=RAMA, 11=VOID.
- Performance: O(1) Bitwise operations, O(1) Memory.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import NewType, List, Final, Union, Optional
from datetime import datetime
import math

# Strict Typing
FractalInt = NewType("FractalInt", int)

class HolyName(IntEnum):
    """The Ternary Basis of Reality."""
    HARE = 0    # 00
    KRISHNA = 1 # 01
    RAMA = 2    # 10
    VOID = 3    # 11 (Maya/Error)

@dataclass(frozen=True)
class MantraTrit:
    """
    A single vibration unit.
    Kept for backward compatibility and explicit instantiation,
    but MantraByte now packs these values efficiently.
    """
    value: HolyName
    intensity: float = 1.0  # Amplitude (Bhakti intensity)

    def __repr__(self):
        return f"{self.value.name}({self.intensity:.2f})"

class MantraByte:
    """
    A Packed Fractal Sequence.
    Stores the vibration in a raw integer for maximum performance.
    
    Structure: [Trit N]...[Trit 1][Trit 0]
    """
    __slots__ = ['_packed', '_length', '_coherence_override', '_stability_override']

    def __init__(self, packed_val: int = 0, length: int = 0, coherence: Optional[float] = None, stability: Optional[float] = None):
        if packed_val is None: # Default case logic if needed, but signature has types
             packed_val = 0
        self._packed = packed_val
        self._length = length
        self._coherence_override = coherence
        self._stability_override = stability

    @classmethod
    def from_trits(cls, trits: List[HolyName]) -> "MantraByte":
        """Packs a list of names into a single integer."""
        packed = 0
        for i, name in enumerate(trits):
            if name == HolyName.VOID:
                raise ValueError("Cannot pack VOID into Mantra.")
            # Shift 2 bits per trit. 
            # Note: We pack index 0 at LSB (standard little-endian feel for sequences)
            packed |= (name.value << (i * 2))
        return cls(packed, len(trits))

    @classmethod
    def from_string(cls, mantra_str: str) -> "MantraByte":
        """Parses 'H K H K...' into Packed Integer."""
        mapping = {"H": HolyName.HARE, "K": HolyName.KRISHNA, "R": HolyName.RAMA}
        names = []
        for char in mantra_str.split():
            first = char[0].upper()
            if first in mapping:
                names.append(mapping[first])
        return cls.from_trits(names)

    @classmethod
    def standard_16(cls) -> "MantraByte":
        """Returns the Standard 16-Word Instruction Set (Optimized)."""
        # H K H K K K H H H R H R R R H H
        seq = [
            HolyName.HARE, HolyName.KRISHNA, HolyName.HARE, HolyName.KRISHNA,
            HolyName.KRISHNA, HolyName.KRISHNA, HolyName.HARE, HolyName.HARE,
            HolyName.HARE, HolyName.RAMA, HolyName.HARE, HolyName.RAMA,
            HolyName.RAMA, HolyName.RAMA, HolyName.HARE, HolyName.HARE
        ]
        return cls.from_trits(seq)

    def get_trit(self, index: int) -> HolyName:
        """Extracts the Holy Name at specific index."""
        if index >= self._length or index < 0:
            return HolyName.VOID
        # Mask: 11 (binary 3) shifted to position
        val = (self._packed >> (index * 2)) & 0b11
        return HolyName(val)
    
    @property
    def sequence(self) -> List[MantraTrit]:
        """
        Reconstructs objects for backward compatibility / inspection.
        Expensive! Use iteration or bitwise ops preferred.
        """
        return [MantraTrit(self.get_trit(i)) for i in range(self._length)]

    @property
    def dimension(self) -> int:
        return self._length

    @property
    def coherence(self) -> float:
        """
        Calculates Fractal Coherence against the Standard Pattern.
        """
        if self._coherence_override is not None:
             return self._coherence_override
             
        std = self.standard_16()
        matches = 0
        
        # We iterate and compare. 
        # Ideally we could do bitwise XOR if lengths were same and aligned perfectly.
        # But for fractal resonance (different lengths), loop is safer.
        for i in range(self._length):
            if self.get_trit(i) == std.get_trit(i % 16):
                matches += 1
        
        ratio = matches / self._length if self._length else 0
        return 1.0 - math.exp(-5.0 * ratio)

    @property
    def stability(self) -> float:
        """Rate of integrity maintenance over time."""
        if self._stability_override is not None:
            return self._stability_override
        return self.coherence # Default stability equals coherence

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        """Yields MantraTrit objects to satisfy external consumers expecting objects."""
        for i in range(self._length):
            yield MantraTrit(self.get_trit(i))

    def __repr__(self) -> str:
        return f"MantraByte(len={self._length}, val=0x{self._packed:X})"

    def __eq__(self, other) -> bool:
        if isinstance(other, MantraByte):
            return self._packed == other._packed and self._length == other._length
        return False

@dataclass(frozen=True)
class GenesisByte:
    """
    The Seed (Bijam).
    Now supports packed ternary resonance.
    """
    signature: str = ""
    resonance: MantraByte = field(default_factory=lambda: MantraByte.standard_16())
    dimension: int = 16 
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    parampara_hash: str = "0x25" # 37

    def validate(self) -> bool:
        # 1. Fractal Purnam Check
        if self.resonance.dimension < self.dimension:
             raise SystemError(f"Fractal Fracture: Expected dimension {self.dimension}, got {self.resonance.dimension}")

        # 2. Coherence Check
        if self.resonance.coherence < 0.8:
             raise SystemError(f"Dissonance Detected: Coherence {self.resonance.coherence:.2f} < 0.8")

        # 3. Mayavad Check
        if not self.signature or self.signature == "None":
             raise PermissionError("Voidist Launch Detected. Identity required.")

        # 4. Lineage
        if not self._verify_lineage():
             raise ConnectionError("Sahajiya Fault: Invalid Parampara Hash.")
             
        return True
        
    @property
    def is_valid(self) -> bool:
        try:
            return self.validate()
        except Exception:
            return False

    def _verify_lineage(self) -> bool:
        try:
            return (int(self.parampara_hash, 16) % 37) == 0
        except ValueError:
            return False

# Global Default
MANTRA_SEQUENCE: Final[MantraByte] = MantraByte.standard_16()
