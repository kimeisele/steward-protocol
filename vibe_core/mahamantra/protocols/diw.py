"""
THE DIVINE INSTRUCTION WORD (DIW) - 19-Bit Protocol
====================================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

THE LAW:
    19 bits = FLUTE_HOLES_SUM = VENU(6) + VAMSI(9) + MURALI(4)
    19 = GITA_CHAPTERS(18) + KSETRAJNA(1)
    19 = digit_sum(1972)

THE BUG THIS FIXES:
    venu_orchestrator._compute_flute_cycle() produced [Name:2][Position:16]
    chamber._apply_diw() expected [MURALI:4][VAMSI:9][VENU:6]
    Result: semantic noise interpreted as structure.

THE FIX:
    This module defines the SINGLE canonical 19-bit layout.
    All producers MUST emit this format.
    All consumers MUST read this format.

BIT LAYOUT (LSB to MSB):
    Bits  0-5  (6): VENU   = Sharanagati (Quality/Mood)
    Bits  6-14 (9): VAMSI  = Nava Bhakti (Process/Action)
    Bits 15-18 (4): MURALI = Quarters (Phase)

    Total: 19 bits = 0x7FFFF

EXTENDED 32-BIT WORD (for transport):
    Bits  0-18 (19): DIW core
    Bits 19-22  (4): Velocity
    Bits 23-26  (4): Cluster route
    Bit  31     (1): SUNYA (silence/no-op)

ALL VALUES DERIVED FROM SSOT. NO HARDCODING.
"""

from typing import Final, NamedTuple

from vibe_core.mahamantra.protocols._seed import (
    # Flute structure (SSOT)
    VENU_HOLES,       # 6 = SHARANAGATI
    VAMSI_HOLES,      # 9 = NAVA
    MURALI_HOLES,     # 4 = QUARTERS
    FLUTE_HOLES_SUM,  # 19
    # Verification constants
    GITA_CHAPTERS,    # 18
    KSETRAJNA,        # 1
    SHARANAGATI,      # 6
    NAVA,             # 9
    QUARTERS,         # 4
)


# =============================================================================
# VERIFICATION: The Isomorphism (19 = 18 + 1)
# =============================================================================

assert FLUTE_HOLES_SUM == GITA_CHAPTERS + KSETRAJNA, (
    f"19 = 18 + 1: FLUTE({FLUTE_HOLES_SUM}) = GITA({GITA_CHAPTERS}) + KSETRAJNA({KSETRAJNA})"
)
assert VENU_HOLES == SHARANAGATI, "VENU = SHARANAGATI (6)"
assert VAMSI_HOLES == NAVA, "VAMSI = NAVA (9)"
assert MURALI_HOLES == QUARTERS, "MURALI = QUARTERS (4)"


# =============================================================================
# BIT SHIFTS (canonical positions)
# =============================================================================

VENU_SHIFT: Final[int] = 0                                    # bits 0-5
VAMSI_SHIFT: Final[int] = VENU_HOLES                          # bits 6-14
MURALI_SHIFT: Final[int] = VENU_HOLES + VAMSI_HOLES           # bits 15-18
VELOCITY_SHIFT: Final[int] = FLUTE_HOLES_SUM                  # bits 19-22
CLUSTER_SHIFT: Final[int] = FLUTE_HOLES_SUM + MURALI_HOLES    # bits 23-26


# =============================================================================
# BIT MASKS (derived from shifts and widths)
# =============================================================================

VENU_MASK: Final[int] = (KSETRAJNA << VENU_HOLES) - KSETRAJNA        # 0x3F (6 bits)
VAMSI_MASK: Final[int] = (KSETRAJNA << VAMSI_HOLES) - KSETRAJNA      # 0x1FF (9 bits)
MURALI_MASK: Final[int] = (KSETRAJNA << MURALI_HOLES) - KSETRAJNA    # 0xF (4 bits)
DIW_MASK: Final[int] = (KSETRAJNA << FLUTE_HOLES_SUM) - KSETRAJNA    # 0x7FFFF (19 bits)
SUNYA_MASK: Final[int] = KSETRAJNA << 31                              # bit 31


# =============================================================================
# VERIFICATION: Masks are correct
# =============================================================================

assert VENU_MASK == 0x3F, f"VENU_MASK must be 0x3F, got {hex(VENU_MASK)}"
assert VAMSI_MASK == 0x1FF, f"VAMSI_MASK must be 0x1FF, got {hex(VAMSI_MASK)}"
assert MURALI_MASK == 0xF, f"MURALI_MASK must be 0xF, got {hex(MURALI_MASK)}"
assert DIW_MASK == 0x7FFFF, f"DIW_MASK must be 0x7FFFF, got {hex(DIW_MASK)}"


# =============================================================================
# DIW STRUCTURE (The Atomic Unit)
# =============================================================================

class DIW(NamedTuple):
    """
    The 19-bit Divine Instruction Word — decomposed view.

    This is NOT a conversion. It is a VIEW on the same integer.
    The raw word and this struct are non-different (abhinna).
    """
    venu: int     # 6 bits: Quality/Mood (Sharanagati)
    vamsi: int    # 9 bits: Process/Action (Nava Bhakti)
    murali: int   # 4 bits: Phase/Quarter (Quarters)


# =============================================================================
# PACK / UNPACK (The Dual View)
# =============================================================================

def pack(venu: int, vamsi: int, murali: int) -> int:
    """
    Pack three flute components into a 19-bit DIW.

    Args:
        venu: 6-bit value (0-63) — Quality
        vamsi: 9-bit value (0-511) — Process
        murali: 4-bit value (0-15) — Phase

    Returns:
        19-bit integer
    """
    return (
        (venu & VENU_MASK)
        | ((vamsi & VAMSI_MASK) << VAMSI_SHIFT)
        | ((murali & MURALI_MASK) << MURALI_SHIFT)
    )


def unpack(word: int) -> DIW:
    """
    Unpack a 19-bit DIW into its three components.

    Args:
        word: 19-bit integer (or wider — only low 19 bits used)

    Returns:
        DIW(venu, vamsi, murali)
    """
    return DIW(
        venu=(word >> VENU_SHIFT) & VENU_MASK,
        vamsi=(word >> VAMSI_SHIFT) & VAMSI_MASK,
        murali=(word >> MURALI_SHIFT) & MURALI_MASK,
    )


def pack_full(
    venu: int,
    vamsi: int,
    murali: int,
    velocity: int = 0,
    cluster: int = 0,
    sunya: bool = False,
) -> int:
    """
    Pack into a full 32-bit transport word.

    Args:
        venu: 6-bit Quality
        vamsi: 9-bit Process
        murali: 4-bit Phase
        velocity: 4-bit intensity (0-15)
        cluster: 4-bit routing (0-15)
        sunya: silence flag

    Returns:
        32-bit integer
    """
    word = pack(venu, vamsi, murali)
    word |= (velocity & 0xF) << VELOCITY_SHIFT
    word |= (cluster & 0xF) << CLUSTER_SHIFT
    if sunya:
        word |= SUNYA_MASK
    return word


def is_sunya(word: int) -> bool:
    """Check if word is silence (no-op)."""
    return bool(word & SUNYA_MASK)


def extract_core(word: int) -> int:
    """Extract the 19-bit DIW core from a 32-bit transport word."""
    return word & DIW_MASK


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Shifts
    "VENU_SHIFT",
    "VAMSI_SHIFT",
    "MURALI_SHIFT",
    "VELOCITY_SHIFT",
    "CLUSTER_SHIFT",
    # Masks
    "VENU_MASK",
    "VAMSI_MASK",
    "MURALI_MASK",
    "DIW_MASK",
    "SUNYA_MASK",
    # Type
    "DIW",
    # Functions
    "pack",
    "unpack",
    "pack_full",
    "is_sunya",
    "extract_core",
]
