"""
ROUTING - Fractal Connections
==============================

The routing layer connects all fractal levels:
Varna (letter) → Aksara (syllable) → Pada (word) → Vakya (mantra) → Mala (round)

FRACTAL PROPERTY:
Each level contains the whole - zoom in or out, the pattern repeats.

COMPUTATIONAL MAPPING:
- Varna = Bit (smallest addressable unit)
- Aksara = Byte (pronounceable unit)
- Pada = Word (semantic unit)
- Vakya = Instruction (16 words = 16 opcodes)
- Mala = Round (108 instructions)

The 37 Formula at each level:
24 Varnas (field) + 12 Aksaras (protectors) + 1 Pada (knower) = 37
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xdc43f18c"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, Tuple, List, Iterator, Optional
from enum import IntEnum

from .varna import Varna, VYANJANA, SVARA
from .aksara import Aksara, MAHAMANTRA_AKSARAS
from .pada import Pada, PadaType, MAHAMANTRA_SEQUENCE, PADA_HARE, PADA_KRISHNA, PADA_RAMA

# FractalLevel imported from SSOT (mahamantra/substrate)
# This inverts the dependency: protocols → mahamantra (correct DAG)
from vibe_core.mahamantra.substrate.fractal import FractalLevel


@dataclass(frozen=True)
class FractalRoute:
    """
    A route through the fractal hierarchy.

    Describes how to navigate from one level to another.
    """
    level: FractalLevel
    index: int  # Position at this level
    parent_index: Optional[int] = None  # Position in parent level

    def __repr__(self) -> str:
        return f"Route({self.level.name}[{self.index}])"


# =============================================================================
# FRACTAL DIMENSIONS
# =============================================================================

# How many units at each level
DIMENSIONS: Final[dict] = {
    FractalLevel.VARNA: 50,      # ~50 varnas in Sanskrit alphabet
    FractalLevel.AKSARA: 6,      # 6 unique syllables in Mahamantra
    FractalLevel.PADA: 3,        # 3 unique words (Hare, Krishna, Rama)
    FractalLevel.VAKYA: 16,      # 16 words per mantra
    FractalLevel.MALA: 108,      # 108 mantras per round
    FractalLevel.SADHANA: 16,    # 16 rounds minimum
}

# Total count in full Mahamantra
MAHAMANTRA_COUNTS: Final[dict] = {
    FractalLevel.PADA: 16,       # 16 words
    FractalLevel.AKSARA: 32,     # ~2 syllables per word
    FractalLevel.VARNA: 64,      # ~2 letters per syllable
}


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def route_pada_to_aksaras(pada: Pada) -> Tuple[Aksara, ...]:
    """Route from word level down to syllable level."""
    return pada.aksaras


def route_index_to_pada(index: int) -> Pada:
    """Route from position (0-15) to the Pada at that position."""
    if 0 <= index < 16:
        return MAHAMANTRA_SEQUENCE[index]
    raise IndexError(f"Invalid pada index: {index}")


def route_index_to_type(index: int) -> PadaType:
    """Route from position (0-15) to the PadaType."""
    return route_index_to_pada(index).pada_type


def iter_mahamantra(level: FractalLevel = FractalLevel.PADA) -> Iterator:
    """
    Iterate through the Mahamantra at specified level.

    Args:
        level: Which fractal level to iterate at

    Yields:
        Items at that level (Pada, Aksara, or Varna)
    """
    if level == FractalLevel.PADA:
        yield from MAHAMANTRA_SEQUENCE
    elif level == FractalLevel.AKSARA:
        for pada in MAHAMANTRA_SEQUENCE:
            yield from pada.aksaras
    elif level == FractalLevel.VARNA:
        # This would need full varna decomposition
        # For now, yield string characters
        for pada in MAHAMANTRA_SEQUENCE:
            for aksara in pada.aksaras:
                for char in aksara.devanagari:
                    yield char


def get_fractal_path(pada_index: int, aksara_index: int = 0) -> List[FractalRoute]:
    """
    Get the full fractal path from Vakya down to Aksara.

    Args:
        pada_index: Which word (0-15)
        aksara_index: Which syllable within the word

    Returns:
        List of routes from top to bottom
    """
    pada = route_index_to_pada(pada_index)
    return [
        FractalRoute(FractalLevel.VAKYA, 0),  # Always in first mantra
        FractalRoute(FractalLevel.PADA, pada_index, parent_index=0),
        FractalRoute(FractalLevel.AKSARA, aksara_index, parent_index=pada_index),
    ]


# =============================================================================
# QUARTER ROUTING (4 quarters of 4 words each)
# =============================================================================

QUARTER_1: Final[Tuple[int, ...]] = (0, 1, 2, 3)    # Hare Krishna Hare Krishna
QUARTER_2: Final[Tuple[int, ...]] = (4, 5, 6, 7)    # Krishna Krishna Hare Hare
QUARTER_3: Final[Tuple[int, ...]] = (8, 9, 10, 11)  # Hare Rama Hare Rama
QUARTER_4: Final[Tuple[int, ...]] = (12, 13, 14, 15)  # Rama Rama Hare Hare

QUARTERS: Final[Tuple[Tuple[int, ...], ...]] = (QUARTER_1, QUARTER_2, QUARTER_3, QUARTER_4)


def get_quarter(index: int) -> int:
    """Get which quarter (0-3) a pada index belongs to."""
    return index // 4


def get_padas_in_quarter(quarter: int) -> Tuple[Pada, ...]:
    """Get all padas in a quarter."""
    if 0 <= quarter < 4:
        indices = QUARTERS[quarter]
        return tuple(MAHAMANTRA_SEQUENCE[i] for i in indices)
    raise IndexError(f"Invalid quarter: {quarter}")


__all__ = [
    "FractalLevel",
    "FractalRoute",
    "DIMENSIONS",
    "MAHAMANTRA_COUNTS",
    # Routing functions
    "route_pada_to_aksaras",
    "route_index_to_pada",
    "route_index_to_type",
    "iter_mahamantra",
    "get_fractal_path",
    # Quarters
    "QUARTER_1",
    "QUARTER_2",
    "QUARTER_3",
    "QUARTER_4",
    "QUARTERS",
    "get_quarter",
    "get_padas_in_quarter",
]
