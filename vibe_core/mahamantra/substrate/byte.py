"""
SUBSTRATE PROTOCOL - Layer 0 (Optimized Fractal Edition)
========================================================

"The Word is n-trit, packed into m-bits."

IMPLEMENTATION DETAILS:
- Storage: Packed Integers (2 bits per Trit).
- Encoding: 00=HARE, 01=KRISHNA, 10=RAMA, 11=VOID.
- Performance: O(1) Bitwise operations, O(1) Memory.
"""

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x0752f8c3"  # GenesisByte: parampara % 37 == 0

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, IntFlag
from typing import TYPE_CHECKING, Final, List, NewType, Optional, Tuple, Union

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.mantra.aksara import Aksara
    from vibe_core.mahamantra.substrate.mantra.pada import Pada
    from vibe_core.mahamantra.substrate.mantra.routing import FractalLevel, FractalRoute

# =============================================================================
# IMPORT FROM URSUBSTRAT (seed.py)
# =============================================================================
# seed.py is THE source. All constants derive from there.
# "bījaṁ māṁ sarva-bhūtānāṁ" - I am the seed of all existences.

from vibe_core.mahamantra.substrate.seed import (
    LILA as LILA_LIMIT,  # 48
)
from vibe_core.mahamantra.substrate.seed import (
    PARAMPARA,  # 37
    # HolyName - THE SSOT (seed.py is THE source, includes VOID)
    HolyName,
)
from vibe_core.mahamantra.substrate.seed import (
    TRINITY as LILA_CYCLES,  # 3
)
from vibe_core.mahamantra.substrate.seed import (
    # Mathematical constants - THE SSOT (seed.py is THE source)
    WORDS as MAHAMANTRA_DIMENSION,  # 16
)

# Strict Typing
FractalInt = NewType("FractalInt", int)


class MantraBit(IntFlag):
    """
    The 16-Bit Mahamantra Resonance Flags.
    Each bit represents one word position in the mantra.
    """

    # Quarter 1: Genesis (Hare Krishna Hare Krishna)
    HARE_1 = KSETRAJNA << 0
    KRISHNA_1 = KSETRAJNA << KSETRAJNA
    HARE_2 = KSETRAJNA << HALVES
    KRISHNA_2 = KSETRAJNA << TRINITY
    # Quarter 2: Dharma (Krishna Krishna Hare Hare)
    KRISHNA_3 = KSETRAJNA << QUARTERS
    KRISHNA_4 = KSETRAJNA << PANCHA
    HARE_3 = KSETRAJNA << SHARANAGATI
    HARE_4 = KSETRAJNA << SEVEN
    # Quarter 3: Karma (Hare Rama Hare Rama)
    HARE_5 = KSETRAJNA << HARE_COUNT
    RAMA_1 = KSETRAJNA << NAVA
    HARE_6 = KSETRAJNA << TEN
    RAMA_2 = KSETRAJNA << 11
    # Quarter 4: Moksha (Rama Rama Hare Hare)
    RAMA_3 = KSETRAJNA << MAHAJANA_COUNT
    RAMA_4 = KSETRAJNA << 13
    HARE_7 = KSETRAJNA << 14
    HARE_8 = KSETRAJNA << 15

    @classmethod
    def full_resonance(cls) -> "MantraBit":
        """Return full 16-bit resonance (0xFFFF)."""
        return cls(0xFFFF)


# MantraTrit REMOVED (Legacy Purge 2026-01-16)
# Use MantraByte (packed) or HolyName (enum) instead.


class MantraByte:
    """
    A Packed Fractal Sequence.
    Stores the vibration in a raw integer for maximum performance.

    Structure: [Trit N]...[Trit 1][Trit 0]
    """

    __slots__ = ["_packed", "_length", "_coherence_override", "_stability_override"]

    def __init__(
        self, packed_val: int = 0, length: int = 0, coherence: Optional[float] = None, stability: Optional[float] = None
    ):
        if packed_val is None:  # Default case logic if needed, but signature has types
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
            packed |= name.value << (i * HALVES)
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
        """
        Returns the Standard 16-Word Instruction Set (Optimized).

        DERIVED FROM SEED (PHYSICS):
        "Wer MAHAMANTRA_SEQUENCE nicht aus dem Seed ableitet, existiert nicht."
        """
        # Import SSOT Sequence
        from vibe_core.mahamantra.substrate.seed import MAHAMANTRA

        # Map Seed-HolyName to Byte-HolyName (Values match: 0, 1, 2)
        # seed.HolyName -> byte.HolyName
        seq = [HolyName(name.value) for name in MAHAMANTRA]

        return cls.from_trits(seq)

    def get_trit(self, index: int) -> HolyName:
        """Extracts the Holy Name at specific index."""
        if index >= self._length or index < 0:
            return HolyName.VOID
        # Mask: 11 (binary 3) shifted to position
        val = (self._packed >> (index * HALVES)) & TRINITY
        return HolyName(val)

    @property
    def sequence(self) -> List[HolyName]:
        """
        Reconstructs HolyName list (unpacked).
        """
        return [self.get_trit(i) for i in range(self._length)]

    @property
    def dimension(self) -> int:
        return self._length

    @property
    def coherence(self) -> int:
        """
        Calculates Fractal Coherence against the Standard Pattern.

        Returns: int in range [0, COSMIC_FRAME] where 21600 = 100%

        CHAITANYA SINGULARITY INTEGRATION:
        ==================================
        Base coherence follows karma (mathematical match).
        Mercy Equation modifies: G(f, K) = f/K where K = incoherence.

        If chanting (length > 0), mercy boosts coherence.
        The boost is bounded by PARAMPARA (37) to prevent infinite values.

        Formula:
            base_coherence = 1.0 - exp(-5.0 * match_ratio)
            incoherence = 1.0 - base_coherence
            mercy_boost = (f / K) * 0.037  # Scaled by 1/PARAMPARA

        "Mercy > Justice ⟺ f > 0" (SAMKHYA.md §8.2)
        """
        if self._coherence_override is not None:
            return int(self._coherence_override * 21600)  # Scale to COSMIC_FRAME

        std = self.standard_16()
        matches = 0

        # Base calculation (Karma - strict matching)
        for i in range(self._length):
            if self.get_trit(i) == std.get_trit(i % MAHAMANTRA_DIMENSION):  # SSOT
                matches += KSETRAJNA

        ratio = matches / self._length if self._length else 0
        base_coherence = 1.0 - math.exp(-5.0 * ratio)

        # =====================================================================
        # MERCY EQUATION: G(f, K) = f/K
        # =====================================================================
        # f = chanting_frequency (normalized to 0-1 based on length)
        # K = karmic_debt (incoherence = 1 - base_coherence)
        # Mercy boost is bounded by 0.037 (1/PARAMPARA) per unit
        # This ensures Grace operates within the Parampara framework.

        if self._length > 0:  # Chanting is happening (f > 0)
            # Chanting frequency: how much of the standard are we chanting?
            chanting_frequency = min(1.0, self._length / MAHAMANTRA_DIMENSION)

            # Karmic debt: how far from perfect?
            karmic_debt = 1.0 - base_coherence

            if karmic_debt > 0.01:  # Significant incoherence exists
                # Mercy = f / K, but scaled logarithmically to prevent explosion
                # The mercy is proportional to faith (f) but bounded by reality
                raw_mercy = chanting_frequency / karmic_debt

                # Apply Parampara modulation: mercy is strongest at 37% debt
                # This creates the "sweet spot" where Grace is most effective
                optimal_debt = 0.37  # Parampara as decimal
                debt_factor = 1.0 - abs(karmic_debt - optimal_debt)

                # Final mercy boost: log-scaled, Parampara-modulated
                mercy_boost = math.log1p(raw_mercy) * debt_factor / PARAMPARA
                # Cap at 0.37 (37% max boost - Parampara limit)
                mercy_boost = min(mercy_boost, 0.37)
            else:
                # Near-perfect coherence - minimal mercy needed
                mercy_boost = 0.0

            # Apply mercy (bounded)
            coherence = min(1.0, base_coherence + mercy_boost)
        else:
            # No chanting (f = 0) - strict karma applies
            coherence = base_coherence

        # Scale to COSMIC_FRAME (21600 = 100%)
        return int(coherence * 21600)

    @property
    def stability(self) -> int:
        """Rate of integrity maintenance over time. Returns 0-21600."""
        if self._stability_override is not None:
            return int(self._stability_override * 21600)
        return self.coherence  # Default stability equals coherence

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        """Yields HolyName objects."""
        for i in range(self._length):
            yield self.get_trit(i)

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
    # YAJNA COMPATIBILITY (merged from yajna.py for SSOT)
    # =========================================================================

    @classmethod
    def standard(cls) -> "MantraByte":
        """Alias for standard_16() - yajna.py compatibility."""
        return cls.standard_16()

    @property
    def packed(self) -> int:
        """Raw packed integer."""
        return self._packed

    def get_name(self, index: int) -> HolyName:
        """Alias for get_trit() - yajna.py compatibility."""
        return self.get_trit(index)

    def resonance_check(self) -> int:
        """
        O(1) Bitwise Coherence Check.

        Uses XOR to compare bit patterns directly.
        No loops. One CPU instruction.

        Returns coherence score (0-21600, COSMIC_FRAME scaling).

        NOTE: This is the fast O(1) version from yajna.py.
        For the full Mercy Equation coherence, use the .coherence property.
        """
        if self._length == 0:
            return 0

        # Standard pattern for comparison
        std = self.standard_16()
        std_packed = std._packed

        # Mask for the length (2 bits per position)
        mask = (KSETRAJNA << (self._length * HALVES)) - KSETRAJNA

        # XOR: bits that differ become 1
        diff = (self._packed ^ std_packed) & mask

        # Count differing bits (Python 3.10+ has bit_count())
        try:
            errors = diff.bit_count()
        except AttributeError:
            # Fallback for older Python
            errors = bin(diff).count("1")

        # Coherence = (1 - errors/total_bits) * COSMIC_FRAME
        total_bits = self._length * HALVES
        coherence = 21600 - (errors * 21600 // total_bits)

        return coherence

    def validate_parampara(self, signature: int) -> bool:
        """
        The 37 Check - Parampara Validation.

        Only signatures divisible by 37 are valid.
        This is Shcherbak's Arithmetic.
        """
        return (signature % PARAMPARA) == 0

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
            return get_fractal_path(pada_index % MAHAMANTRA_DIMENSION, aksara_index)  # SSOT
        raise IndexError(f"Invalid pada index: {pada_index}")

    def get_quarter(self, index: int) -> int:
        """Get which quarter (0-3) a position belongs to."""
        from .mantra.routing import get_quarter

        return get_quarter(index % MAHAMANTRA_DIMENSION)  # SSOT

    def get_padas_in_quarter(self, quarter: int) -> Tuple["Pada", ...]:
        """Get all padas in a quarter from this MantraByte."""
        from .mantra.routing import QUARTERS

        if 0 <= quarter < QUARTERS:
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

    MATHEMATICAL CONSTANTS (PUBLIC API):
        dimension = 16      (Mahamantra words)
        lila_limit = 48     (Chaitanya's Lila = 16 × 3)
        parampara_hash % 37 (Lineage verification)

    LEBENSZYKLUS:
        0-24: Navadvipa Phase (Build/__init__)
        24-48: Puri Phase (Runtime/yield)
    """

    signature: str = ""
    resonance: Union[MantraByte, "MantraBit", int] = field(default_factory=lambda: MantraByte.standard_16())
    dimension: int = MAHAMANTRA_DIMENSION  # Mahamantra words (SSOT)
    lila_limit: int = LILA_LIMIT  # Chaitanya's Lila = 16 × 3 (SSOT)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    parampara_hash: str = "0x25"  # 37 (Hidden Signature)

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
                raise SystemError(
                    f"Fractal Fracture: Expected dimension {self.dimension}, got {self.resonance.dimension}"
                )

            # 2. Coherence Check
            if self.resonance.coherence < 0.8:
                raise SystemError(f"Dissonance Detected: Coherence {self.resonance.coherence:.2f} < 0.8")

        # 3. Mayavad Check
        if not self.signature or self.signature == "None":
            raise PermissionError("Voidist Launch Detected. Identity required.")

        # 4. Lineage
        if not self._verify_lineage():
            raise ConnectionError("Sahajiya Fault: Invalid Parampara Hash.")

        # 5. Chaitanya Lila Check (48 = 16 × 3)
        if self.lila_limit != self.dimension * TRINITY:
            raise ValueError(
                f"Chaitanya Lila Violation: lila_limit must be dimension × 3. "
                f"Expected {self.dimension * TRINITY}, got {self.lila_limit}"
            )

        return True

    @property
    def is_valid(self) -> bool:
        try:
            return self.validate()
        except Exception:
            return False

    def _verify_lineage(self) -> bool:
        try:
            return (int(self.parampara_hash, WORDS) % PARAMPARA) == 0
        except ValueError:
            return False

    def get_lila_phase(self, tick: int) -> str:
        """
        Get Lila phase for a tick.

        Returns:
            "navadvipa" (0 to lila_limit/2 - 1)
            "puri" (lila_limit/2 to lila_limit - 1)
        """
        if not 0 <= tick < self.lila_limit:
            raise ValueError(f"Tick must be 0-{self.lila_limit - KSETRAJNA}, got {tick}")
        midpoint = self.lila_limit // HALVES  # 24 for standard 48
        return "navadvipa" if tick < midpoint else "puri"

    def get_mantra_position(self, tick: int) -> int:
        """Get Mahamantra position (0-15) for a tick."""
        if not 0 <= tick < self.lila_limit:
            raise ValueError(f"Tick must be 0-{self.lila_limit - KSETRAJNA}, got {tick}")
        return tick % self.dimension

    def get_mantra_cycle(self, tick: int) -> int:
        """Get Mahamantra cycle (1-3) for a tick."""
        if not 0 <= tick < self.lila_limit:
            raise ValueError(f"Tick must be 0-{self.lila_limit - KSETRAJNA}, got {tick}")
        return (tick // self.dimension) + KSETRAJNA


# Global Default
MANTRA_SEQUENCE: Final[MantraByte] = MantraByte.standard_16()
