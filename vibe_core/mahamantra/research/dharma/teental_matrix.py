"""
TEENTAL BINARY MATRIX - The Drum Pattern Encoding
==================================================

"śravaṇaṁ kīrtanaṁ viṣṇoḥ smaraṇaṁ pāda-sevanam"
"Hearing and chanting about Vishnu, remembering Him, serving His lotus feet..."
— Srimad Bhagavatam 7.5.23

TEENTAL is the most common Tala in North Indian Kirtan.
16 beats = 16 words in Mahamantra. This is NOT coincidence.

MRIDANGA ENCODING (2-bit per beat):
===================================
  Bit 0 = Treble (daya) active
  Bit 1 = Bass (baya) active

  Dha  = Both heads, resonant  = 11 = 3
  Dhin = Both heads, muted     = 11 = 3 (same structural pattern)
  Tin  = Treble only, damped   = 01 = 1
  Ta   = Bass only             = 10 = 2

MAHAMANTRA CORRELATION:
=======================
  Bass (baya)   = HARE energy (grounding shakti)
  Treble (daya) = NAME identity (Krishna/Rama clarity)

  Dha/Dhin (both) = HARE + NAME = Complete invocation
  Tin (treble)    = NAME only   = Pure identity (like KRISHNA KRISHNA)
  Ta (bass)       = HARE only   = Pure energy (like HARE HARE)

ALL CONSTANTS FROM seed.py - NO HARDCODED VALUES
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x00000559"  # GenesisByte: 1369 = 37² = PARAMPARA²

from dataclasses import dataclass
from enum import IntEnum
from typing import Final, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KHALI_POSITION,
    MATRA_PER_VIBHAG,
    MRIDANGA_HEADS,
    NAVA,
    QUARTERS,
    SAM_SUM,
    SEVEN,
    TEENTAL_MATRA,
    VIBHAG_COUNT,
    WORDS,
)

# =============================================================================
# MRIDANGA STROKE ENCODING (Derived from MRIDANGA_HEADS = 2)
# =============================================================================


class MridangaStroke(IntEnum):
    """
    Mridanga stroke types encoded as 2-bit values.

    Bit 0 = Treble (daya) head active
    Bit 1 = Bass (baya) head active

    HALVES = 2 heads → 2 bits → 4 possible states
    """

    SILENT = 0b00  # 0 - No stroke (rest)
    TIN = 0b01  # 1 - Treble only (daya)
    TA = 0b10  # 2 - Bass only (baya)
    DHA = 0b11  # 3 - Both heads (resonant)
    DHIN = 0b11  # 3 - Both heads (muted) - same bits, different timbre

    @property
    def bass_active(self) -> bool:
        """Is the bass (baya) head struck?"""
        return bool(self.value & 0b10)

    @property
    def treble_active(self) -> bool:
        """Is the treble (daya) head struck?"""
        return bool(self.value & 0b01)

    @property
    def both_heads(self) -> bool:
        """Are both heads struck?"""
        return self.value == 0b11


# Verify encoding uses HALVES bits
assert MridangaStroke.DHA.bit_length() <= MRIDANGA_HEADS, "Stroke encoding must fit in MRIDANGA_HEADS bits"


# =============================================================================
# TEENTAL PATTERN (16 beats = WORDS)
# =============================================================================

# The traditional Teental pattern as stroke types
# This is the ONLY place where actual bols are encoded
_TEENTAL_BOLS: Final[Tuple[str, ...]] = (
    # Vibhag 1 (beats 1-4) - SAM
    "Dha",
    "Dhin",
    "Dhin",
    "Dha",
    # Vibhag 2 (beats 5-8)
    "Dha",
    "Dhin",
    "Dhin",
    "Dha",
    # Vibhag 3 (beats 9-12) - KHALI
    "Dha",
    "Tin",
    "Tin",
    "Ta",
    # Vibhag 4 (beats 13-16)
    "Ta",
    "Dhin",
    "Dhin",
    "Dha",
)

# Verify length matches WORDS
assert len(_TEENTAL_BOLS) == TEENTAL_MATRA == WORDS, f"Teental must have {WORDS} beats"


def _bol_to_stroke(bol: str) -> MridangaStroke:
    """Convert a bol name to its stroke encoding."""
    bol_upper = bol.upper()
    if bol_upper == "DHA":
        return MridangaStroke.DHA
    elif bol_upper == "DHIN":
        return MridangaStroke.DHIN
    elif bol_upper == "TIN":
        return MridangaStroke.TIN
    elif bol_upper == "TA":
        return MridangaStroke.TA
    else:
        return MridangaStroke.SILENT


# Build the binary pattern
TEENTAL_STROKES: Final[Tuple[MridangaStroke, ...]] = tuple(_bol_to_stroke(bol) for bol in _TEENTAL_BOLS)

# Build the binary values (2-bit per beat)
TEENTAL_BINARY: Final[Tuple[int, ...]] = tuple(stroke.value for stroke in TEENTAL_STROKES)

# Verify structure
assert len(TEENTAL_STROKES) == WORDS
assert len(TEENTAL_BINARY) == WORDS


# =============================================================================
# VIBHAG STRUCTURE (4 sections × 4 beats = 16)
# =============================================================================


@dataclass(frozen=True)
class Vibhag:
    """One section (vibhag) of Teental."""

    number: int  # 1-4
    start_beat: int  # 1-indexed
    is_sam: bool  # Is this the SAM (main) vibhag?
    is_khali: bool  # Is this the KHALI (empty) vibhag?
    strokes: Tuple[MridangaStroke, ...]

    @property
    def binary_value(self) -> int:
        """Convert 4 strokes to 8-bit value."""
        result = 0
        for i, stroke in enumerate(self.strokes):
            result |= stroke.value << (i * 2)
        return result


def _build_vibhags() -> Tuple[Vibhag, ...]:
    """Build the 4 vibhags from TEENTAL_STROKES."""
    vibhags = []
    for v in range(VIBHAG_COUNT):
        start = v * MATRA_PER_VIBHAG
        end = start + MATRA_PER_VIBHAG

        vibhags.append(
            Vibhag(
                number=v + 1,
                start_beat=start + 1,
                is_sam=(v == 0),  # First vibhag is SAM
                is_khali=(start + 1 == KHALI_POSITION),  # Vibhag 3 contains KHALI
                strokes=TEENTAL_STROKES[start:end],
            )
        )

    return tuple(vibhags)


TEENTAL_VIBHAGS: Final[Tuple[Vibhag, ...]] = _build_vibhags()


# =============================================================================
# SAM AND KHALI POSITIONS (Derived from seed.py)
# =============================================================================

# SAM positions: Beginning of each vibhag (1, 5, 9, 13)
SAM_POSITIONS: Final[Tuple[int, ...]] = tuple(1 + (v * MATRA_PER_VIBHAG) for v in range(VIBHAG_COUNT))

# Verify SAM_SUM matches seed.py
_computed_sam_sum = sum(SAM_POSITIONS)
assert _computed_sam_sum == SAM_SUM, f"SAM sum must be {SAM_SUM}, got {_computed_sam_sum}"

# KHALI position from seed.py
assert KHALI_POSITION == NAVA, "KHALI must be at NAVA (9)"


# =============================================================================
# BINARY ANALYSIS
# =============================================================================


def get_bass_pattern() -> Tuple[int, ...]:
    """Extract bass-only pattern (bit 1 of each stroke)."""
    return tuple((s.value >> 1) & 1 for s in TEENTAL_STROKES)


def get_treble_pattern() -> Tuple[int, ...]:
    """Extract treble-only pattern (bit 0 of each stroke)."""
    return tuple(s.value & 1 for s in TEENTAL_STROKES)


def teental_to_decimal() -> int:
    """
    Convert full Teental pattern to decimal.

    32 bits total (16 beats × 2 bits per beat).
    """
    result = 0
    for i, stroke in enumerate(TEENTAL_STROKES):
        result |= stroke.value << (i * 2)
    return result


# The complete Teental as a single 32-bit value
TEENTAL_DECIMAL: Final[int] = teental_to_decimal()


# =============================================================================
# MAHAMANTRA CORRELATION
# =============================================================================


def analyze_mahamantra_correlation() -> dict:
    """
    Analyze correlation between Teental strokes and Mahamantra pattern.

    Hypothesis:
    - Bass (baya) correlates with HARE (energy/shakti)
    - Treble (daya) correlates with NAME (Krishna/Rama identity)
    """
    # MAHAMANTRA_WORD_PATTERN: Direct import from _seed.py (THE SSOT!)
    # _seed.py derives this from:
    #   MAHAMANTRA_HARE_POS_HALF = (KSETRAJNA, TRINITY, HALF_SIZE-KSETRAJNA, HARE_COUNT)
    #   MAHAMANTRA_NAME_POS_HALF = (HALVES, QUARTERS, PANCHA, SHARANAGATI)
    #   MAHAMANTRA_HALF_BINARY + MAHAMANTRA_NAME_HARE/KRISHNA/RAMA
    # NO LOCAL DERIVATION - ALL FROM SSOT!
    from vibe_core.mahamantra.protocols._seed import MAHAMANTRA_WORD_PATTERN
    
    MAHAMANTRA_PATTERN = MAHAMANTRA_WORD_PATTERN

    correlations = []
    bass_pattern = get_bass_pattern()
    treble_pattern = get_treble_pattern()

    for i in range(WORDS):
        name = MAHAMANTRA_PATTERN[i]
        bass = bass_pattern[i]
        treble = treble_pattern[i]
        stroke = TEENTAL_STROKES[i]

        # HARE = energy (bass?), NAME = identity (treble?)
        is_hare = name == "H"
        is_name = name in ("K", "R")

        correlations.append(
            {
                "position": i + 1,
                "mahamantra": name,
                "stroke": _TEENTAL_BOLS[i],
                "bass": bass,
                "treble": treble,
                "is_hare": is_hare,
                "is_name": is_name,
            }
        )

    # Count matches
    hare_bass_matches = sum(1 for c in correlations if c["is_hare"] and c["bass"])
    name_treble_matches = sum(1 for c in correlations if c["is_name"] and c["treble"])

    return {
        "correlations": correlations,
        "hare_bass_matches": hare_bass_matches,
        "name_treble_matches": name_treble_matches,
        "total_hare": sum(1 for c in correlations if c["is_hare"]),
        "total_name": sum(1 for c in correlations if c["is_name"]),
    }


# =============================================================================
# KARTAL PATTERN (Derived from SAM positions)
# =============================================================================

# Kartals typically accent on SAM positions (1, 5, 9, 13)
KARTAL_PATTERN: Final[Tuple[int, ...]] = tuple(1 if (i + 1) in SAM_POSITIONS else 0 for i in range(WORDS))

# The sum of Kartal accents = number of SAM positions = VIBHAG_COUNT
assert sum(KARTAL_PATTERN) == VIBHAG_COUNT


# =============================================================================
# COMBINED KIRTAN MATRIX (Mridanga + Kartal)
# =============================================================================


@dataclass(frozen=True)
class KirtanBeat:
    """One beat in the Kirtan rhythm pattern."""

    position: int  # 1-16
    mridanga_stroke: MridangaStroke
    kartal_accent: bool
    is_sam: bool
    is_khali: bool
    vibhag: int  # 1-4

    @property
    def binary_value(self) -> int:
        """
        3-bit encoding per beat:
        - Bits 0-1: Mridanga stroke (2 bits)
        - Bit 2: Kartal accent (1 bit)
        """
        return self.mridanga_stroke.value | (int(self.kartal_accent) << 2)


def _build_kirtan_matrix() -> Tuple[KirtanBeat, ...]:
    """Build the complete Kirtan matrix."""
    beats = []
    for i in range(WORDS):
        pos = i + 1
        vibhag_num = (i // MATRA_PER_VIBHAG) + 1

        beats.append(
            KirtanBeat(
                position=pos,
                mridanga_stroke=TEENTAL_STROKES[i],
                kartal_accent=(pos in SAM_POSITIONS),
                is_sam=(pos == 1),  # Only beat 1 is the true SAM
                is_khali=(pos == KHALI_POSITION),
                vibhag=vibhag_num,
            )
        )

    return tuple(beats)


KIRTAN_MATRIX: Final[Tuple[KirtanBeat, ...]] = _build_kirtan_matrix()


# =============================================================================
# 48-BIT KIRTAN WORD (LILA encoding)
# =============================================================================


def kirtan_to_48bit() -> int:
    """
    Encode full Kirtan pattern as 48-bit value.

    16 beats × 3 bits = 48 bits = LILA!

    This is NOT coincidence. LILA = WORDS × TRINITY = 48.
    """
    result = 0
    for i, beat in enumerate(KIRTAN_MATRIX):
        result |= beat.binary_value << (i * 3)
    return result


KIRTAN_48BIT: Final[int] = kirtan_to_48bit()


# =============================================================================
# VERIFICATION
# =============================================================================

# Structure verification
assert len(TEENTAL_VIBHAGS) == VIBHAG_COUNT == QUARTERS
assert all(len(v.strokes) == MATRA_PER_VIBHAG for v in TEENTAL_VIBHAGS)
assert TEENTAL_VIBHAGS[2].is_khali, "Vibhag 3 must be KHALI"

# SAM verification
assert SAM_POSITIONS == (1, 5, 9, 13), "SAM at beginning of each vibhag"
assert sum(SAM_POSITIONS) == SAM_SUM == 28, "SAM_SUM = T(7) = 28"

# KHALI verification
assert KHALI_POSITION == 9 == NAVA, "KHALI at beat 9 = NAVA"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Stroke types
    "MridangaStroke",
    # Teental pattern
    "TEENTAL_STROKES",
    "TEENTAL_BINARY",
    "TEENTAL_DECIMAL",
    "TEENTAL_VIBHAGS",
    # SAM/KHALI
    "SAM_POSITIONS",
    "KARTAL_PATTERN",
    # Combined matrix
    "KirtanBeat",
    "KIRTAN_MATRIX",
    "KIRTAN_48BIT",
    # Analysis
    "get_bass_pattern",
    "get_treble_pattern",
    "analyze_mahamantra_correlation",
    # Data structures
    "Vibhag",
]
