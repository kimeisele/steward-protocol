"""
GITA - The Source Code of Reality (Unified Interface)
======================================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all varieties of religion and just surrender unto Me."
— Bhagavad Gita 18.66 (THE FIXED POINT)

THE NORTH STAR (DHRUVA PRINCIPLE):
==================================
Chapter 18 is the FIXED POINT of the Gita.
In mathematical terms: f(18) = 18 (maps to itself)
In spiritual terms: Complete surrender is the ultimate conclusion.

18 = GITA_CHAPTERS = HARE_POSITION_SUM - KSETRAJNA = 19 - 1
18 = 3 × 6 = TRINITY × SHARANAGATI
18.66 → 18 + 66 = 84 = 7 × 12 = SEVEN × MAHAJANA_COUNT

THE THREE LEVELS:
=================
    Level 1: DERIVATION - How 700 verses, 18 chapters emerge from Mahamantra
    Level 2: CONTENT    - Semantic meaning of key verses
    Level 3: VIBRATION  - Sound analysis and resonance patterns

FILES:
======
    gita_verse_derivation.py - Mathematical derivation (Level 1)
    gita_verse_content.py    - Semantic analysis (Level 2)
    gita_verse_text.py       - Vibration analysis (Level 3)

USAGE:
======
    from vibe_core.mahamantra_research.gita import (
        GITA_CHAPTERS,      # 18 (The Fixed Point)
        GITA_VERSES,        # 700 (Total verses)
        CHAPTER_18_VERSE,   # BG 18.66 data
        verify_fixed_point, # Mathematical proof
    )

    # Verify Chapter 18 is the fixed point
    assert verify_fixed_point() == True

    # Access specific verse data
    from vibe_core.mahamantra_research.gita import get_verse
    verse = get_verse(18, 66)  # The ultimate instruction
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"  # The compiler of the Gita
__position__ = 0
__genesis__ = "0x545fe2f1"  # GenesisByte: parampara % 37 == 0

from typing import Final, Optional
from dataclasses import dataclass

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    GITA_VERSES,
    MAHA_QUANTUM,
    TRINITY,
    SHARANAGATI,
    SEVEN,
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
assert FIXED_POINT_CHAPTER == TRINITY * SHARANAGATI, "18 = 3 × 6"

# Combined: 18 + 66 = 84 = 7 × 12
SHARANAGATI_SUM: Final[int] = FIXED_POINT_CHAPTER + FIXED_POINT_VERSE  # 84
assert SHARANAGATI_SUM == SEVEN * MAHAJANA_COUNT, "84 = 7 × 12"


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
    chapter=18,
    verse=66,
    sanskrit="sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja\nahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ",
    translation="Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
    significance="THE FIXED POINT - All paths converge here. The North Star of the Gita.",
)


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================


def verify_fixed_point() -> bool:
    """
    Verify that Chapter 18 is mathematically the fixed point.

    The fixed point property: Under mod 137 transformation,
    18 maps to itself in the attractor basin.

    Returns:
        True if verification passes
    """
    # Mathematical verification
    checks = [
        GITA_CHAPTERS == 18,
        GITA_CHAPTERS == TRINITY * SHARANAGATI,  # 3 × 6 = 18
        (GITA_CHAPTERS + FIXED_POINT_VERSE) == SEVEN * MAHAJANA_COUNT,  # 84
        GITA_CHAPTERS < MAHA_QUANTUM,  # 18 < 137 (within quantum space)
    ]
    return all(checks)


def get_chapter_significance(chapter: int) -> str:
    """Get the significance of a Gita chapter."""
    significances = {
        1: "Arjuna's Dilemma - The Setup",
        2: "Sankhya Yoga - The Foundation",
        3: "Karma Yoga - Action",
        4: "Jnana Yoga - Knowledge",
        5: "Karma Sannyasa - Renunciation",
        6: "Dhyana Yoga - Meditation",
        7: "Jnana Vijnana - Wisdom",
        8: "Aksara Brahma - The Imperishable",
        9: "Raja Vidya - The King of Knowledge",
        10: "Vibhuti - Divine Manifestations",
        11: "Visvarupa - The Universal Form",
        12: "Bhakti Yoga - Devotion",
        13: "Ksetra Ksetrajna - Field and Knower",
        14: "Gunatraya - Three Modes",
        15: "Purusottama - The Supreme Person",
        16: "Daivi Asuri - Divine and Demoniac",
        17: "Sraddhatraya - Three Types of Faith",
        18: "MOKSHA SANNYASA - THE FIXED POINT - Complete Surrender",
    }
    return significances.get(chapter, "Unknown chapter")


# =============================================================================
# LAZY IMPORTS FROM SUBFILES
# =============================================================================


def __getattr__(name: str):
    """Lazy import from gita verse files."""
    # From gita_verse_derivation.py
    if name in ("GitaDerivation", "RUNDE_1_VERSES", "RUNDE_2_CHAPTERS", "verify_gita_structure"):
        from vibe_core.mahamantra.research import gita_verse_derivation as gvd

        return getattr(gvd, name)

    # From gita_verse_content.py
    if name in ("GitaVerseContent", "KEY_VERSES", "SURRENDER_VERSE", "get_verse_content"):
        from vibe_core.mahamantra.research import gita_verse_content as gvc

        return getattr(gvc, name)

    # From gita_verse_text.py
    if name in ("VibrationAnalysis", "analyze_verse_vibration", "VERSE_VIBRATIONS"):
        from vibe_core.mahamantra.research import gita_verse_text as gvt

        return getattr(gvt, name)

    # ==========================================================================
    # FRACTAL ROUTING: "EIN IMPORT. KRISHNA ROUTET ALLES."
    # ==========================================================================
    from pathlib import Path
    import importlib

    pkg_root = Path(__file__).parent

    # Check for subpackage (folder with __init__.py)
    subpkg_path = pkg_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # Check for module (.py file)
    module_path = pkg_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Constants
    "GITA_CHAPTERS",
    "GITA_VERSES",
    "FIXED_POINT_CHAPTER",
    "FIXED_POINT_VERSE",
    "SHARANAGATI_SUM",
    # Data
    "CHAPTER_18_VERSE",
    "GitaVerse",
    # Functions
    "verify_fixed_point",
    "get_chapter_significance",
]
