"""
SUBSTRATE PROTOCOL - Layer 0 (Optimized Fractal Edition)
========================================================

"The Word is n-trit, packed into m-bits."

IMPLEMENTATION DETAILS:
- Storage: Packed Integers (2 bits per Trit).
- Encoding: 00=HARE, 01=KRISHNA, 10=RAMA, 11=VOID.
- Performance: O(1) Bitwise operations, O(1) Memory.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xc8c185b1"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import IntEnum, IntFlag
from typing import NewType, List, Final, Union, Optional, Tuple, TYPE_CHECKING
from datetime import datetime
import math

# Lazy import to avoid circular dependency
if TYPE_CHECKING:
    from .nama import to_devanagari, to_iast, to_roman
    from .mantra.pada import Pada, PadaType, PADA_BY_TYPE
    from .mantra.aksara import Aksara
    from .mantra.routing import FractalLevel, FractalRoute

# Strict Typing
FractalInt = NewType("FractalInt", int)

class HolyName(IntEnum):
    """The Ternary Basis of Reality."""
    HARE = 0    # 00
    KRISHNA = 1 # 01
    RAMA = 2    # 10
    VOID = 3    # 11 (Maya/Error)


class MantraBit(IntFlag):
    """
    The 16-Bit Mahamantra Resonance Flags.
    Each bit represents one word position in the mantra.
    """
    # Quarter 1: Genesis (Hare Krishna Hare Krishna)
    HARE_1 = 1 << 0
    KRISHNA_1 = 1 << 1
    HARE_2 = 1 << 2
    KRISHNA_2 = 1 << 3
    # Quarter 2: Dharma (Krishna Krishna Hare Hare)
    KRISHNA_3 = 1 << 4
    KRISHNA_4 = 1 << 5
    HARE_3 = 1 << 6
    HARE_4 = 1 << 7
    # Quarter 3: Karma (Hare Rama Hare Rama)
    HARE_5 = 1 << 8
    RAMA_1 = 1 << 9
    HARE_6 = 1 << 10
    RAMA_2 = 1 << 11
    # Quarter 4: Moksha (Rama Rama Hare Hare)
    RAMA_3 = 1 << 12
    RAMA_4 = 1 << 13
    HARE_7 = 1 << 14
    HARE_8 = 1 << 15

    @classmethod
    def full_resonance(cls) -> "MantraBit":
        """Return full 16-bit resonance (0xFFFF)."""
        return cls(0xFFFF)

@dataclass(frozen=True)
class MantraTrit:
    """
    A single vibration unit - The Transcendental Seed.
    Kept for backward compatibility and explicit instantiation,
    but MantraByte now packs these values efficiently.
    """
    value: HolyName
    intensity: float = 1.0  # Amplitude (Bhakti intensity)

    @property
    def devanagari(self) -> str:
        """Original Sanskrit script."""
        from .nama import to_devanagari
        return to_devanagari(self.value.value)

    @property
    def iast(self) -> str:
        """IAST transliteration with diacritics."""
        from .nama import to_iast
        return to_iast(self.value.value)

    @property
    def roman(self) -> str:
        """Western/English representation."""
        from .nama import to_roman
        return to_roman(self.value.value)

    # =========================================================================
    # FRACTAL INTEGRATION (via mantra/)
    # =========================================================================

    @property
    def pada(self) -> "Pada":
        """Full Pada object with aksaras and meaning."""
        from .mantra.pada import PADA_BY_TYPE, PadaType
        return PADA_BY_TYPE.get(PadaType(self.value.value))

    @property
    def aksaras(self) -> Tuple["Aksara", ...]:
        """Component syllables of this word."""
        return self.pada.aksaras if self.value != HolyName.VOID else ()

    @property
    def meaning(self) -> str:
        """Philosophical meaning of this word."""
        return self.pada.meaning if self.value != HolyName.VOID else ""

    def __repr__(self) -> str:
        return f"{self.value.name}({self.intensity:.2f})"

    def __str__(self) -> str:
        """Default to IAST for string output."""
        return self.iast

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

    # =========================================================================
    # TRIPLE ENCODING (via nama.py)
    # =========================================================================

    def to_devanagari(self, separator: str = " ") -> str:
        """Output in original Sanskrit script."""
        from .nama import to_devanagari
        return separator.join(to_devanagari(self.get_trit(i).value) for i in range(self._length))

    def to_iast(self, separator: str = " ") -> str:
        """Output in IAST (with diacritics)."""
        from .nama import to_iast
        return separator.join(to_iast(self.get_trit(i).value) for i in range(self._length))

    def to_roman(self, separator: str = " ") -> str:
        """Output in Western/English."""
        from .nama import to_roman
        return separator.join(to_roman(self.get_trit(i).value) for i in range(self._length))

    def to_triple(self) -> Tuple[str, str, str]:
        """Returns (devanagari, iast, roman)."""
        return (self.to_devanagari(), self.to_iast(), self.to_roman())

    # =========================================================================
    # FRACTAL DECOMPOSITION (via mantra/)
    # =========================================================================

    def to_padas(self) -> List["Pada"]:
        """Decompose to Pada (word) level."""
        from .mantra.pada import PADA_BY_TYPE, PadaType
        return [PADA_BY_TYPE.get(PadaType(self.get_trit(i).value)) for i in range(self._length)]

    def to_aksaras(self) -> List["Aksara"]:
        """Decompose to Aksara (syllable) level - flattened."""
        result = []
        for pada in self.to_padas():
            if pada:
                result.extend(pada.aksaras)
        return result

    def iter_at_level(self, level: "FractalLevel"):
        """
        Iterate through this MantraByte at specified fractal level.

        Args:
            level: Which fractal level (PADA, AKSARA, VARNA)

        Yields:
            Items at that level
        """
        from .mantra.routing import FractalLevel
        if level == FractalLevel.PADA:
            yield from self.to_padas()
        elif level == FractalLevel.AKSARA:
            yield from self.to_aksaras()
        elif level == FractalLevel.VARNA:
            for aksara in self.to_aksaras():
                for char in aksara.devanagari:
                    yield char

    def get_fractal_path(self, pada_index: int, aksara_index: int = 0) -> List["FractalRoute"]:
        """Get the fractal path from Vakya down to Aksara for a position."""
        from .mantra.routing import get_fractal_path
        if 0 <= pada_index < self._length:
            return get_fractal_path(pada_index % 16, aksara_index)
        raise IndexError(f"Invalid pada index: {pada_index}")

    def get_quarter(self, index: int) -> int:
        """Get which quarter (0-3) a position belongs to."""
        from .mantra.routing import get_quarter
        return get_quarter(index % 16)

    def get_padas_in_quarter(self, quarter: int) -> Tuple["Pada", ...]:
        """Get all padas in a quarter from this MantraByte."""
        from .mantra.routing import QUARTERS
        if 0 <= quarter < 4:
            indices = QUARTERS[quarter]
            padas = self.to_padas()
            return tuple(padas[i] for i in indices if i < len(padas))
        raise IndexError(f"Invalid quarter: {quarter}")

    # =========================================================================
    # MAGIC METHODS
    # =========================================================================

    def __repr__(self) -> str:
        return f"MantraByte(len={self._length}, val=0x{self._packed:X})"

    def __str__(self) -> str:
        """Default to IAST for string output."""
        return self.to_iast()

    def __eq__(self, other) -> bool:
        if isinstance(other, MantraByte):
            return self._packed == other._packed and self._length == other._length
        return False

@dataclass(frozen=True)
class GenesisByte:
    """
    The Seed (Bijam).
    Now supports packed ternary resonance and 16-bit MantraBit flags.
    """
    signature: str = ""
    resonance: Union[MantraByte, "MantraBit", int] = field(default_factory=lambda: MantraByte.standard_16())
    dimension: int = 16
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    parampara_hash: str = "0x25" # 37

    def validate(self) -> bool:
        # Handle MantraBit/int resonance
        if isinstance(self.resonance, (int, MantraBit)):
            # Check for full 16-bit resonance (0xFFFF)
            resonance_val = int(self.resonance)
            if resonance_val != 0xFFFF:
                raise PermissionError(f"Incomplete Mantra Resonance: got 0x{resonance_val:04X}, need 0xFFFF")
        else:
            # MantraByte handling
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
