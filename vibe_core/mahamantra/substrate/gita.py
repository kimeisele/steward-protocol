"""
MAHA GITA - The Source Code of Reality
=======================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all varieties of religion and just surrender unto Me."
— Bhagavad Gita 18.66 (THE FIXED POINT)

This module provides the core Gita constants and the fixed-point logic
required for Mahamantra resonance.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (GITA_CHAPTERS, HALVES, HARE_COUNT, KSETRAJNA, MAHAJANA_COUNT, NAVA, PANCHA, POSITION_SUM_KRISHNA, QUARTERS, SEVEN, SHARANAGATI, TEN, TRINITY, WORDS)

from dataclasses import dataclass
from typing import Final, Dict

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x545fe2f1"

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    GITA_VERSES,
    MAHA_QUANTUM,
    TRINITY,
    SHARANAGATI,
    SEVEN,
    MAHA_WORDS,
    MAHAJANA_COUNT,
    KSETRAJNA,
    QUALITIES,
    HALVES,
)

# =============================================================================
# THE FIXED POINT (Chapter 18)
# =============================================================================

FIXED_POINT_CHAPTER: Final[int] = GITA_CHAPTERS  # 18
FIXED_POINT_VERSE: Final[int] = QUALITIES + HALVES  # 66

# Mathematical proof: 18 = 3 × 6
# 18 + 66 = 84 = 7 × 12
SHARANAGATI_SUM: Final[int] = FIXED_POINT_CHAPTER + FIXED_POINT_VERSE  # 84

@dataclass(frozen=True)
class GitaVerse:
    """A verse from the Bhagavad Gita."""
    chapter: int
    verse: int
    sanskrit: str
    translation: str
    significance: str

# The ultimate verse - BG 18.66
CHAPTER_18_VERSE: Final[GitaVerse] = GitaVerse(
    chapter=GITA_CHAPTERS,
    verse=66,
    sanskrit="sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja\\nahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ",
    translation="Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
    significance="THE FIXED POINT - All paths converge here. The North Star of the Gita.",
)

# =============================================================================
# UTILITIES
# =============================================================================

def verify_fixed_point() -> bool:
    """Verify that Chapter 18 is mathematically the fixed point."""
    checks = [
        GITA_CHAPTERS == GITA_CHAPTERS,
        GITA_CHAPTERS == TRINITY * SHARANAGATI,
        (GITA_CHAPTERS + FIXED_POINT_VERSE) == SEVEN * MAHAJANA_COUNT,
        GITA_CHAPTERS < MAHA_QUANTUM,
    ]
    return all(checks)

def get_chapter_significance(chapter: int) -> str:
    """Get the significance of a Gita chapter."""
    significances = {
        KSETRAJNA: "Arjuna's Dilemma - The Setup",
        HALVES: "Sankhya Yoga - The Foundation",
        TRINITY: "Karma Yoga - Action",
        QUARTERS: "Jnana Yoga - Knowledge",
        PANCHA: "Karma Sannyasa - Renunciation",
        SHARANAGATI: "Dhyana Yoga - Meditation",
        SEVEN: "Jnana Vijnana - Wisdom",
        HARE_COUNT: "Aksara Brahma - The Imperishable",
        NAVA: "Raja Vidya - The King of Knowledge",
        TEN: "Vibhuti - Divine Manifestations",
        11: "Visvarupa - The Universal Form",
        MAHAJANA_COUNT: "Bhakti Yoga - Devotion",
        13: "Ksetra Ksetrajna - Field and Knower",
        14: "Gunatraya - Three Modes",
        15: "Purusottama - The Supreme Person",
        WORDS: "Daivi Asuri - Divine and Demoniac",
        POSITION_SUM_KRISHNA: "Sraddhatraya - Three Types of Faith",
        GITA_CHAPTERS: "MOKSHA SANNYASA - THE FIXED POINT - Complete Surrender",
    }
    return significances.get(chapter, "Unknown chapter")

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GITA_CHAPTERS",
    "GITA_VERSES",
    "FIXED_POINT_CHAPTER",
    "FIXED_POINT_VERSE",
    "SHARANAGATI_SUM",
    "CHAPTER_18_VERSE",
    "GitaVerse",
    "verify_fixed_point",
    "get_chapter_significance",
]
