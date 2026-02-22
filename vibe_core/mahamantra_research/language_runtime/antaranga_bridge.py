"""Keystroke → Antaranga Bridge: The Einschlag im Teich.

Each keystroke is not a string operation — it's a physical impact in the
16KB contiguous RAM of the AntarangaRegistry. The character is mapped through
the phonetic protocol layer to a RAMA coordinate, then collided into the
chamber with initial prana derived from its articulatory energy.

Pipeline:
    char → PHONEME_TO_VARGA (articulatory WHERE) → VargaIndex
         → PHONEME_TO_STHANA (articulatory HOW) → SthanaIndex
         → RAMA coordinate (Varga row × PANCHA + Sthana column)
         → antaranga.collide() with prana from STHANA_ENERGY

The VenuOrchestrator tick modulates all active slots via apply_diw(),
creating the standing wave pattern that accumulates as the user types.
"""

from __future__ import annotations

from typing import NamedTuple, Optional

from typing import Dict, Final

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    PANCHA,
    SEVEN,
    WORDS,
)
from vibe_core.mahamantra.substrate.antaranga import (
    ANTARANGA_SLOTS,
    AntarangaRegistry,
    GENESIS_PRANA_U32,
    INTEGRITY_FULL,
)
from vibe_core.mahamantra.substrate.phonetic_bridge import (
    PHONEME_TO_STHANA,
    PHONEME_TO_VARGA,
    STHANA_ENERGY_CF,
    SthanaIndex,
    VargaIndex,
)
from vibe_core.mahamantra.substrate.rama_grid import SVARAS

# English vowel → SVARAS position (protocol-derived from rama_grid.py)
# a→0, i→1, u→2, e→10, o→12 — exact positions in the 16-vowel system
_VOWEL_TO_SVARA: Final[Dict[str, int]] = {s: idx for idx, s in enumerate(SVARAS) if s in "aeiou"}


class ImpactResult(NamedTuple):
    """Result of a keystroke impact in the Antaranga."""

    char: str
    rama_coord: int  # 0-48 RAMA grid position
    slot: int  # 0-511 Antaranga slot
    prana_injected: int  # prana value injected
    resonated: bool  # True if merged with existing, False if new presence
    total_prana_after: int  # total prana in chamber after impact


def char_to_rama_coord(char: str) -> int:
    """Map a single character to a RAMA coordinate via protocol phonetics.

    Vowels: SVARAS position from rama_grid.py (a→0, i→1, u→2, e→10, o→12)
    Consonants: WORDS + VargaIndex × PANCHA + SthanaIndex (SPARSHA grid)

    Returns RAMA coordinate (0-48), or -1 if unmappable.
    """
    c = char.lower()

    # Vowels: direct SVARAS lookup (protocol-derived from rama_grid.py)
    svara_pos = _VOWEL_TO_SVARA.get(c)
    if svara_pos is not None:
        return svara_pos

    # Consonants: PHONEME_TO_VARGA gives row, PHONEME_TO_STHANA gives column
    varga = PHONEME_TO_VARGA.get(c)
    if varga is None:
        return -1

    sthana = PHONEME_TO_STHANA.get(c, SthanaIndex.SPARSHA)
    coord = WORDS + varga.value * PANCHA + min(sthana.value, PANCHA - KSETRAJNA)
    return min(coord, 48)  # Clamp to RAMA space (0-48)


def rama_coord_to_slot(coord: int, seed: int = 0) -> int:
    """Map RAMA coordinate to Antaranga slot index.

    Uses the same hashing as the engine's _resonate(): (coord × 7 + seed) % 512.
    """
    return (coord * SEVEN + seed) % ANTARANGA_SLOTS


def prana_for_char(char: str) -> int:
    """Compute initial prana for a keystroke from its articulatory energy.

    Derived from STHANA_ENERGY_CF (protocol, COSMIC_FRAME space).
    Scaled to fit GENESIS_PRANA_U32 range.
    """
    c = char.lower()
    sthana = PHONEME_TO_STHANA.get(c, SthanaIndex.SPARSHA)
    energy_cf = STHANA_ENERGY_CF.get(sthana, STHANA_ENERGY_CF[SthanaIndex.SPARSHA])
    # Scale: energy_cf is in COSMIC_FRAME space (0-21600)
    # GENESIS_PRANA_U32 = 13700. Scale proportionally.
    return max(KSETRAJNA, (energy_cf * GENESIS_PRANA_U32) // 21600)


def impact_keystroke(
    antaranga: AntarangaRegistry,
    char: str,
    seed: int = 0,
) -> Optional[ImpactResult]:
    """Fire a single keystroke into the Antaranga as a collide() event.

    Returns ImpactResult with the collision outcome, or None if char is unmappable.
    """
    coord = char_to_rama_coord(char)
    if coord < 0:
        return None

    slot = rama_coord_to_slot(coord, seed)
    prana = prana_for_char(char)

    resonated = antaranga.collide(
        slot=slot,
        v_source=coord,
        v_target=seed,
        v_operation=ord(char) & 0xFFFF,
        v_arcanam=0,
        v_atma=0,
        v_prana=prana,
        v_integrity=INTEGRITY_FULL,
        v_cycle=KSETRAJNA,
    )

    return ImpactResult(
        char=char,
        rama_coord=coord,
        slot=slot,
        prana_injected=prana,
        resonated=resonated,
        total_prana_after=antaranga.total_prana(),
    )


def modulate_with_diw(antaranga: AntarangaRegistry, diw: int) -> int:
    """Apply a VenuOrchestrator DIW to all active Antaranga slots.

    Returns the number of slots modulated.
    """
    count = 0
    for slot_idx in range(ANTARANGA_SLOTS):
        if antaranga.is_alive(slot_idx):
            antaranga.apply_diw(slot_idx, diw)
            count += KSETRAJNA
    return count
