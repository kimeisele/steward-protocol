"""
SECTION ROUTER — Attractor → Kapitel 18 Section + Verse Template
================================================================

Kapitel 18 has 78 verses = NADI_RESONANCE(72) + SHARANAGATI(6).
7 sections, each length a derived constant:
    TYAGA(12), SANKHYA(6), TRAIGUNYA(22), VARNASHRAMA(8),
    BRAHMAN(7), RAHASYA(11), SANJAYA(12)

Each section has a verified phonetic signature and a response mode.
"""

from __future__ import annotations

from typing import Dict, Final, List, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    PANCHA,
    QUARTERS,
    QUALITIES,
    SEVEN,
    SHARANAGATI,
)
from vibe_core.mahamantra.protocols.seed._extended import SHRUTIS
from vibe_core.mahamantra.protocols.seed._secondary import NADI_RESONANCE
from vibe_core.mahamantra.protocols.seed._topology import CHAPTER_VERSES
from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, ELEMENT_NAMES
from vibe_core.mahamantra.substrate.sanskrit_lookup import verse_words

# =============================================================================
# KAPITEL 18: INNER TOPOLOGY
# =============================================================================

CHAPTER_18_VERSES: Final[int] = CHAPTER_VERSES[17]
assert CHAPTER_18_VERSES == NADI_RESONANCE + SHARANAGATI  # 72 + 6 = 78

KRISHNA_INSTRUCTION: Final[int] = QUALITIES + HALVES  # 66
SANJAYA_CONCLUSION: Final[int] = MAHAJANA_COUNT  # 12
assert KRISHNA_INSTRUCTION + SANJAYA_CONCLUSION == CHAPTER_18_VERSES

# 7 sections: (Name, Start-Verse, End-Verse, Length)
CHAPTER_18_SECTIONS: Final[Tuple[Tuple[str, int, int, int], ...]] = (
    ("TYAGA", 1, 12, MAHAJANA_COUNT),
    ("SANKHYA", 13, 18, SHARANAGATI),
    ("TRAIGUNYA", 19, 40, SHRUTIS),
    ("VARNASHRAMA", 41, 48, HARE_COUNT),
    ("BRAHMAN", 49, 55, SEVEN),
    ("RAHASYA", 56, 66, MAHAJANA_COUNT - KSETRAJNA),
    ("SANJAYA", 67, 78, MAHAJANA_COUNT),
)

# Verify completeness
_section_sum = sum(s[3] for s in CHAPTER_18_SECTIONS)
assert _section_sum == CHAPTER_18_VERSES
for i in range(len(CHAPTER_18_SECTIONS) - 1):
    assert CHAPTER_18_SECTIONS[i + 1][1] == CHAPTER_18_SECTIONS[i][2] + 1

# Verified section signatures (phonetic + semantic profiles)
SECTION_SIGNATURES: Final[Dict[str, Dict[str, object]]] = {
    "TYAGA": {
        "element": "vayu",
        "attractor_ratio_18_22": 1.13,
        "shesha_pct": 25.5,
        "unique_word_pct": 65.8,
        "semantic": "renunciation",
        "mode": "FILTER",
    },
    "SANKHYA": {
        "element": "jala",
        "attractor_ratio_18_22": 0.50,
        "shesha_pct": 23.3,
        "unique_word_pct": 60.0,
        "semantic": "analysis",
        "mode": "VERB",
    },
    "TRAIGUNYA": {
        "element": "jala",
        "attractor_ratio_18_22": 0.95,
        "shesha_pct": 23.1,
        "unique_word_pct": 79.9,
        "semantic": "qualities",
        "mode": "QUALITY",
    },
    "VARNASHRAMA": {
        "element": "prithvi",
        "attractor_ratio_18_22": 0.69,
        "shesha_pct": 28.8,
        "unique_word_pct": 70.9,
        "semantic": "duty",
        "mode": "CONTEXT",
    },
    "BRAHMAN": {
        "element": "jala",
        "attractor_ratio_18_22": 0.69,
        "shesha_pct": 25.0,
        "unique_word_pct": 68.8,
        "semantic": "liberation",
        "mode": "TARGET",
    },
    "RAHASYA": {
        "element": "vayu",
        "attractor_ratio_18_22": 1.04,
        "shesha_pct": 30.2,
        "unique_word_pct": 72.9,
        "semantic": "devotion",
        "mode": "CORE",
    },
    "SANJAYA": {
        "element": "prithvi",
        "attractor_ratio_18_22": 1.13,
        "shesha_pct": 26.6,
        "unique_word_pct": 78.4,
        "semantic": "conclusion",
        "mode": "CLOSURE",
    },
}


def route_to_section(attractor: int, seed: int = 0) -> Tuple[str, int, int]:
    """Route an attractor + seed to a Kapitel 18 section.

    Two-stage routing:
        1. Attractor element → section pool
        2. Seed selects from pool + verse within section

    Returns: (section_name, verse_number, section_index)
    """
    from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL

    rama_coord = attractor % VARNAMALA_TOTAL
    element = int(COORD_ELEMENT[rama_coord])
    elem_name = ELEMENT_NAMES[element]

    section_pools = {
        "akasha": [("RAHASYA", 5), ("TYAGA", 0)],
        "vayu": [("TYAGA", 0), ("RAHASYA", 5)],
        "agni": [("TRAIGUNYA", 2), ("SANKHYA", 1)],
        "jala": [("SANKHYA", 1), ("BRAHMAN", 4), ("TRAIGUNYA", 2)],
        "prithvi": [("VARNASHRAMA", 3), ("SANJAYA", 6)],
    }

    pool = section_pools.get(elem_name, [("RAHASYA", 5)])
    pool_idx = seed % len(pool)
    section_name, section_idx = pool[pool_idx]

    _, start, end, _ = CHAPTER_18_SECTIONS[section_idx]
    verse_range = end - start + 1
    verse_offset = (seed // len(pool)) % verse_range
    verse_num = start + verse_offset

    return section_name, verse_num, section_idx


def extract_template(chapter: int, verse: int) -> List[Dict]:
    """Extract a grammatical template from a Gita verse.

    Each word becomes a slot with sanskrit, meaning, role, coords.
    Role inferred from coordinate mass + verse position (no keyword lists).
    """
    vw = verse_words(chapter, verse)
    if vw is None:
        return []

    slots = []
    total = len(vw.words)
    for i, w in enumerate(vw.words):
        meaning = w.meaning if w.meaning else ""
        role = _infer_role(w.coords, i, total)
        slots.append(
            {
                "position": i,
                "sanskrit": w.sanskrit,
                "meaning": meaning,
                "role": role,
                "coords": w.coords,
            }
        )
    return slots


def _infer_role(coords: Sequence[int], position: int, total: int) -> str:
    """Infer grammatical role from RAMA coordinate properties.

    Coordinate mass (len(coords)) correlates with grammatical function:
        mass ≤ HALVES (2)                  → PARTICLE (function words)
        mass ≤ QUARTERS (4) at edges       → REF (pronouns, deictics)
        mass ≥ PANCHA + HALVES (7)         → QUALITY (heavy compounds)
        mass ≤ QUARTERS (4) mid-verse      → PREP (relational)
        last QUARTERS positions in verse   → VERB (Sanskrit SOV: verb at end)
        otherwise                          → NOUN

    Position in verse provides structural signal:
        Sanskrit is SOV — verbs cluster at the end of the verse.
        Subjects/references cluster at the beginning.
    """
    mass = len(coords)

    # Lightest words are particles (connectors, emphasis)
    if mass <= HALVES:
        return "PARTICLE"

    # Heavy compounds are qualities/descriptions
    if mass >= PANCHA + HALVES:
        return "QUALITY"

    # Position signal: last QUARTERS positions tend to be verbs (SOV)
    if total > 0 and position >= total - QUARTERS and mass > HALVES:
        return "VERB"

    # Light words at verse edges are references (subject/object)
    if mass <= QUARTERS and (position < HALVES or position >= total - HALVES):
        return "REF"

    # Light words mid-verse are relational (prepositions)
    if mass <= QUARTERS:
        return "PREP"

    return "NOUN"
