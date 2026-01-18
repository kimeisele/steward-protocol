"""
POSITION - Die 16 MantraPositionen (Wahrheitstabelle)
=====================================================

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"Es gibt keine Wahrheit, die Mir überlegen wäre.
Alles ruht auf Mir, wie Perlen auf einem Faden aufgereiht."
— Bhagavad Gita 7.7

DAS IST DER FADEN. DIE 16 POSITIONEN SIND DIE PERLEN.

SINGLE SOURCE OF TRUTH:
    MAHAMANTRA_POSITIONS is GENERATED from seed.py ALL_GUARDIANS.
    NO HARDCODED VALUES.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x2f45fe98"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, Tuple, Union

from vibe_core.mahamantra.substrate.byte import HolyName
from vibe_core.mahamantra.substrate.mahajana import (
    Avatara,
    Mahajana,
    Quarter,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode

# === IMPORT FROM SSOT (seed.py) ===
from vibe_core.mahamantra.substrate.seed import (
    # THE SSOT FOR GUARDIANS:
    ALL_GUARDIANS,
    AVATARAS,
    PARAMPARA,
    WORDS,
    WORDS_PER_QUARTER,
)
from vibe_core.mahamantra.substrate.seed import (
    MAHAMANTRA as SEED_MAHAMANTRA,
)
from vibe_core.mahamantra.substrate.seed import get_quarter as seed_get_quarter

# =============================================================================
# GUARDIAN TYPE - Union of Mahajana and Avatara
# =============================================================================

Guardian = Union[Mahajana, Avatara]


# =============================================================================
# MANTRA POSITION - The Atomic Unit of Truth
# =============================================================================


@dataclass(frozen=True)
class MantraPosition:
    """
    Eine einzelne Position im Mahamantra.

    GENERATED FROM seed.py ALL_GUARDIANS - NO HARDCODING.

    Properties:
        index: 0-15 (Position im 16-Wort-Mantra)
        word: HARE, KRISHNA, oder RAMA
        quarter: GENESIS, DHARMA, KARMA, oder MOKSHA
        is_head: True für Positionen 0, 4, 8, 12 (Avatara-owned)
        opcode: Die Instruktion an dieser Position
        guardian: Mahajana oder Avatara
        parampara_vector: (index + 1) * 37
    """

    index: int
    word: HolyName
    quarter: Quarter
    is_head: bool
    opcode: MantraOpCode
    guardian: Guardian

    @property
    def parampara_vector(self) -> int:
        """Parampara vector: (index + 1) * 37."""
        return (self.index + 1) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        """True wenn parampara_vector % 37 == 0."""
        return self.parampara_vector % PARAMPARA == 0


# =============================================================================
# THE 16 POSITIONS - GENERATED FROM seed.py ALL_GUARDIANS
# =============================================================================


def _resolve_guardian(name: str) -> Guardian:
    """Resolve guardian name to Mahajana or Avatara enum."""
    # Check if it's an Avatara (HEAD)
    if name in AVATARAS:
        return Avatara(name)
    # Otherwise it's a Mahajana (WORKER)
    return Mahajana(name)


def _get_quarter_enum(index: int) -> Quarter:
    """Get Quarter enum from seed.get_quarter."""
    seed_quarter = seed_get_quarter(index)
    # seed.Quarter and mahajana.Quarter have same values
    return Quarter(seed_quarter.name.lower())


def _build_mahamantra_positions() -> Tuple[MantraPosition, ...]:
    """
    BUILD MAHAMANTRA_POSITIONS FROM seed.py ALL_GUARDIANS.

    This is the ONLY place where positions are defined.
    Everything else DERIVES from here.
    seed.py ALL_GUARDIANS is the SSOT.
    """
    positions = []

    for i in range(WORDS):
        # GET GUARDIAN FROM SSOT (seed.py ALL_GUARDIANS)
        guardian_name = ALL_GUARDIANS[i]
        guardian = _resolve_guardian(guardian_name)

        # GET WORD FROM SSOT (seed.py MAHAMANTRA)
        seed_word = SEED_MAHAMANTRA[i]
        word = HolyName(seed_word.value)

        # GET QUARTER FROM SSOT (seed.py get_quarter)
        quarter = _get_quarter_enum(i)

        # IS_HEAD: Positions 0, 4, 8, 12 are HEADs (Avataras)
        is_head = i % WORDS_PER_QUARTER == 0

        # OPCODE: Directly from position index
        opcode = MantraOpCode(i)

        positions.append(
            MantraPosition(
                index=i,
                word=word,
                quarter=quarter,
                is_head=is_head,
                opcode=opcode,
                guardian=guardian,
            )
        )

    return tuple(positions)


# THE TRUTH TABLE - GENERATED, NOT HARDCODED
MAHAMANTRA_POSITIONS: Final[Tuple[MantraPosition, ...]] = _build_mahamantra_positions()


# =============================================================================
# VERIFICATION - Ensure SSOT alignment
# =============================================================================


def _verify_ssot_alignment() -> None:
    """Verify MAHAMANTRA_POSITIONS matches seed.py ALL_GUARDIANS."""
    for i, pos in enumerate(MAHAMANTRA_POSITIONS):
        expected_guardian = ALL_GUARDIANS[i]
        actual_guardian = pos.guardian.value
        assert actual_guardian == expected_guardian, (
            f"SSOT VIOLATION at position {i}: expected {expected_guardian}, got {actual_guardian}"
        )


# Run verification at import time
_verify_ssot_alignment()


# =============================================================================
# LOOKUP FUNCTIONS - Pure, typed, no side effects
# =============================================================================


def get_position(index: int) -> MantraPosition:
    """Get position by index (0-15)."""
    if not 0 <= index < WORDS:
        raise ValueError(f"Position index must be 0-{WORDS - 1}, got {index}")
    return MAHAMANTRA_POSITIONS[index]


def get_position_by_guardian(guardian: Guardian) -> MantraPosition:
    """Get position by guardian (Mahajana or Avatara)."""
    for pos in MAHAMANTRA_POSITIONS:
        if pos.guardian == guardian:
            return pos
    raise ValueError(f"Unknown guardian: {guardian}")


def get_position_by_opcode(opcode: MantraOpCode) -> MantraPosition:
    """Get position by opcode."""
    return MAHAMANTRA_POSITIONS[opcode.value]


# Quarter to index mapping
QUARTER_INDEX: dict = {
    Quarter.GENESIS: 0,
    Quarter.DHARMA: 1,
    Quarter.KARMA: 2,
    Quarter.MOKSHA: 3,
}


def get_positions_by_quarter(quarter: Quarter) -> Tuple[MantraPosition, ...]:
    """Get all positions in a quarter."""
    idx = QUARTER_INDEX[quarter]
    start = idx * WORDS_PER_QUARTER
    return MAHAMANTRA_POSITIONS[start : start + WORDS_PER_QUARTER]


def get_head_position(quarter: Quarter) -> MantraPosition:
    """Get the HEAD position for a quarter."""
    idx = QUARTER_INDEX[quarter]
    return MAHAMANTRA_POSITIONS[idx * WORDS_PER_QUARTER]


def get_worker_positions_for_quarter(quarter: Quarter) -> Tuple[MantraPosition, ...]:
    """Get the WORKER positions for a quarter (3 per quarter)."""
    idx = QUARTER_INDEX[quarter]
    start = idx * WORDS_PER_QUARTER
    return MAHAMANTRA_POSITIONS[start + 1 : start + WORDS_PER_QUARTER]


# Alias for backward compatibility
get_worker_positions = get_worker_positions_for_quarter


def get_all_head_positions() -> Tuple[MantraPosition, ...]:
    """Get all 4 HEAD positions (Avataras at 0, 4, 8, 12)."""
    return tuple(p for p in MAHAMANTRA_POSITIONS if p.is_head)


def get_all_worker_positions() -> Tuple[MantraPosition, ...]:
    """Get all 12 WORKER positions (Mahajanas)."""
    return tuple(p for p in MAHAMANTRA_POSITIONS if not p.is_head)


# Alias for singularity.py compatibility
get_quarter_positions = get_positions_by_quarter

# Alias for backward compatibility (tests expect get_position_by_index)
get_position_by_index = get_position


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "Guardian",
    # Constants
    "PARAMPARA",
    # Position
    "MantraPosition",
    "MAHAMANTRA_POSITIONS",
    # Functions
    "get_position",
    "get_position_by_index",  # Alias for get_position
    "get_position_by_guardian",
    "get_position_by_opcode",
    "get_positions_by_quarter",
    "get_head_position",
    "get_worker_positions",
    "get_worker_positions_for_quarter",
    "get_all_head_positions",
    "get_all_worker_positions",
    # Aliases
    "get_quarter_positions",
]
