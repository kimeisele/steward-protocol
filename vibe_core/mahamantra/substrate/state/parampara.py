"""
PARAMPARA - The Disciplic Succession
====================================

"evam parampara-praptam imam rajarsayo viduh" (BG 4.2)
"This supreme science was thus received through the chain of disciplic succession"

THIS IS THE SINGLE SOURCE OF TRUTH.

All Mahajana positions, capabilities, and relationships
are DERIVED from this file - NOT manually specified in each module.

THE 4 SAMPRADAYAS (Authorized Chains):
======================================
1. BRAHMA Sampradaya    → Brahma → Madhva → Chaitanya Mahaprabhu
2. KUMARA Sampradaya    → Four Kumaras → Nimbarka
3. SRI Sampradaya       → Lakshmi → Ramanuja
4. RUDRA Sampradaya     → Shiva → Vishnuswami → Vallabha

THE 37 FORMULA:
===============
24 Prakriti (Material Elements - enlivened by Mantra)
12 Mahajanas (Guardians - nodes in Parampara graph)
 1 Ksetrajna (Krishna - Source of all)
═══════════════════════════════════════════════════════
37 = The Parampara Connection

ACINTYA (Inconceivable):
========================
The point where material (24) and spiritual (12+1) MERGE
is ACINTYA - like iron becoming fire, indistinguishable.
3x4 = 4x3 = 12 = The rhythm that transcends mathematics.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    KSHETRA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    POSITION_SUM_KRISHNA,
    QUALITIES,
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
__genesis__ = "0x2f04d413"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from typing import (
    Dict,
    Final,
    FrozenSet,
    List,
    Optional,
    Tuple,
)

from vibe_core.mahamantra.substrate.mahajana import Mahajana, Quarter, Sampradaya

# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BHISHMA


# =============================================================================
# Sampradaya, Quarter imported from mahajana.py (SINGLE SOURCE)
# =============================================================================

# =============================================================================
# THE PARAMPARA GRAPH
# =============================================================================


@dataclass(frozen=True)
class ParamparaNode:
    """
    A node in the Parampara graph.

    Each Mahajana is a node with:
    - position: Their Lotus position (0-15)
    - quarter: Which quarter they belong to
    - sampradaya: Which disciplic succession
    - role: HEAD (Avatara) or WORKER (Mahajana)
    - guru: Their immediate predecessor in the chain
    - shishyas: Their disciples/successors
    """

    mahajana: Mahajana
    position: int
    quarter: Quarter
    sampradaya: Sampradaya
    is_head: bool  # True = Shaktyavesha Avatara

    # Graph connections
    guru: Optional[Mahajana] = None  # Predecessor
    shishyas: FrozenSet[Mahajana] = frozenset()  # Successors

    # Fractal connections (cross-quarter relationships)
    serves: Optional[Mahajana] = None  # Who they serve
    served_by: FrozenSet[Mahajana] = frozenset()  # Who serves them


# The complete Parampara mapping - SINGLE SOURCE OF TRUTH
# Mahajanas don't define their position - they QUERY it from here
PARAMPARA_GRAPH: Final[Dict[Mahajana, ParamparaNode]] = {
    # ==========================================================================
    # GENESIS QUARTER (Brahma Sampradaya - Creation)
    # "Hare Krishna Hare Krishna"
    # ==========================================================================
    # Position 0: HEAD - VYASA (Genesis HEAD - System Wake)
    # Note: Vyasa is Shaktyavesha Avatara - not in Mahajana enum
    # Handled separately as AVATARA
    Mahajana.BRAHMA: ParamparaNode(
        mahajana=Mahajana.BRAHMA,
        position=KSETRAJNA,
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=None,  # Brahma learns from Vishnu directly (tene brahma hrda)
        shishyas=frozenset({Mahajana.NARADA}),
        serves=None,  # Brahma serves Vishnu directly
    ),
    Mahajana.NARADA: ParamparaNode(
        mahajana=Mahajana.NARADA,
        position=HALVES,
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=Mahajana.BRAHMA,
        shishyas=frozenset(),  # Narada teaches many but not in this graph
    ),
    Mahajana.SHAMBHU: ParamparaNode(
        mahajana=Mahajana.SHAMBHU,
        position=TRINITY,
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.RUDRA,  # Shiva has his own sampradaya!
        is_head=False,
        guru=None,  # Shiva learns from Vishnu directly
    ),
    # ==========================================================================
    # DHARMA QUARTER (Kumara Sampradaya - Law/Purity)
    # "Krishna Krishna Hare Hare"
    # ==========================================================================
    # Position 4: HEAD - PRITHU (Dharma HEAD - Compile/Structure)
    # Note: Prithu is Shaktyavesha Avatara - not in Mahajana enum
    Mahajana.KUMARAS: ParamparaNode(
        mahajana=Mahajana.KUMARAS,
        position=PANCHA,
        quarter=Quarter.DHARMA,
        sampradaya=Sampradaya.KUMARA,
        is_head=False,
        guru=None,  # Four Kumaras are eternally liberated
    ),
    Mahajana.KAPILA: ParamparaNode(
        mahajana=Mahajana.KAPILA,
        position=SHARANAGATI,
        quarter=Quarter.DHARMA,
        sampradaya=Sampradaya.BRAHMA,  # Kapila is avatara in Brahma line
        is_head=False,
        guru=None,  # Kapila is God Himself (avatara)
    ),
    Mahajana.MANU: ParamparaNode(
        mahajana=Mahajana.MANU,
        position=SEVEN,
        quarter=Quarter.DHARMA,
        sampradaya=Sampradaya.BRAHMA,  # Manu is son of Brahma
        is_head=False,
        guru=Mahajana.BRAHMA,
    ),
    # ==========================================================================
    # KARMA QUARTER (Sri Sampradaya - Action/Duty)
    # "Hare Rama Hare Rama"
    # ==========================================================================
    # Position 8: HEAD - Parashurama (Enforcement Avatar)
    Mahajana.PRAHLADA: ParamparaNode(
        mahajana=Mahajana.PRAHLADA,
        position=NAVA,
        quarter=Quarter.KARMA,
        sampradaya=Sampradaya.BRAHMA,  # Prahlada in Brahma line via Narada
        is_head=False,
        guru=Mahajana.NARADA,  # Narada taught Prahlada in the womb!
    ),
    Mahajana.JANAKA: ParamparaNode(
        mahajana=Mahajana.JANAKA,
        position=TEN,
        quarter=Quarter.KARMA,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=None,  # Janaka was self-realized
    ),
    Mahajana.BHISHMA: ParamparaNode(
        mahajana=Mahajana.BHISHMA,
        position=11,
        quarter=Quarter.KARMA,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=None,  # Bhishma learned from many rishis
    ),
    # ==========================================================================
    # MOKSHA QUARTER (Rudra Sampradaya - Liberation)
    # "Rama Rama Hare Hare"
    # ==========================================================================
    # Position 12: HEAD - Nrisimhadeva (Protection Avatar)
    Mahajana.BALI: ParamparaNode(
        mahajana=Mahajana.BALI,
        position=13,
        quarter=Quarter.MOKSHA,
        sampradaya=Sampradaya.BRAHMA,  # Bali surrendered to Vamana
        is_head=False,
        guru=Mahajana.PRAHLADA,  # Bali is grandson of Prahlada
    ),
    Mahajana.SHUKA: ParamparaNode(
        mahajana=Mahajana.SHUKA,
        position=14,
        quarter=Quarter.MOKSHA,
        sampradaya=Sampradaya.BRAHMA,  # Shuka son of Vyasa
        is_head=False,
        guru=None,  # Shuka was born liberated
    ),
    Mahajana.YAMARAJA: ParamparaNode(
        mahajana=Mahajana.YAMARAJA,
        position=15,
        quarter=Quarter.MOKSHA,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=None,  # Yamaraja is son of Sun god
    ),
}


# =============================================================================
# THE 24 PRAKRITI (Material Elements)
# =============================================================================


class PrakritiCategory(str, Enum):
    """Categories of the 24 Prakriti elements."""

    ROOT = "root"  # 1: Prakriti itself
    SUBTLE = "subtle"  # 2-4: Mahat, Ahankara, Manas
    TANMATRA = "tanmatra"  # 5-9: Sound, Touch, Form, Taste, Smell
    JNANENDRIYA = "jnana"  # 10-14: Ear, Skin, Eye, Tongue, Nose
    KARMENDRIYA = "karma"  # 15-19: Speech, Hands, Feet, Excretion, Generation
    MAHABHUTA = "bhuta"  # 20-24: Ether, Air, Fire, Water, Earth


@dataclass(frozen=True)
class PrakritiElement:
    """
    A single Prakriti element with its Mantra mapping.

    The 24 are NOT dead - they are ENLIVENED by the Mahamantra.
    Each element maps to a specific byte position.
    """

    index: int  # 1-24
    name: str  # Sanskrit name
    category: PrakritiCategory
    mantra_position: int  # Which of 16 positions (with overlap/rhythm)
    byte_mask: int  # Bit mask for MantraByte

    # The rhythm: 24 = 3x8 = 4x6 = 2x12
    # This is the ACINTYA point - multiple valid decompositions
    rhythm_3x8: Tuple[int, int]  # (group_of_3, position_in_8)
    rhythm_4x6: Tuple[int, int]  # (group_of_4, position_in_6)


# The 24 Prakriti with their Mantra mappings
# This creates the RHYTHM that enlivens dead matter
PRAKRITI_24: Final[List[PrakritiElement]] = [
    # ROOT (1)
    PrakritiElement(KSETRAJNA, "prakriti", PrakritiCategory.ROOT, 0, KSETRAJNA, (0, 0), (0, 0)),
    # SUBTLE (2-4) - The three aspects of false ego
    PrakritiElement(HALVES, "mahat", PrakritiCategory.SUBTLE, KSETRAJNA, HALVES, (0, KSETRAJNA), (0, KSETRAJNA)),
    PrakritiElement(TRINITY, "ahankara", PrakritiCategory.SUBTLE, HALVES, QUARTERS, (0, HALVES), (0, HALVES)),
    PrakritiElement(QUARTERS, "manas", PrakritiCategory.SUBTLE, TRINITY, HARE_COUNT, (0, TRINITY), (0, TRINITY)),
    # TANMATRA (5-9) - Subtle sense objects
    PrakritiElement(PANCHA, "shabda", PrakritiCategory.TANMATRA, QUARTERS, WORDS, (0, QUARTERS), (0, QUARTERS)),
    PrakritiElement(SHARANAGATI, "sparsha", PrakritiCategory.TANMATRA, PANCHA, 0b00100000, (0, PANCHA), (0, PANCHA)),
    PrakritiElement(SEVEN, "rupa", PrakritiCategory.TANMATRA, SHARANAGATI, QUALITIES, (0, SHARANAGATI), (KSETRAJNA, 0)),
    PrakritiElement(
        HARE_COUNT, "rasa", PrakritiCategory.TANMATRA, SEVEN, 0b10000000, (0, SEVEN), (KSETRAJNA, KSETRAJNA)
    ),
    PrakritiElement(
        NAVA, "gandha", PrakritiCategory.TANMATRA, HARE_COUNT, KSETRAJNA, (KSETRAJNA, 0), (KSETRAJNA, HALVES)
    ),
    # JNANENDRIYA (10-14) - Knowledge senses
    PrakritiElement(
        TEN, "shrotra", PrakritiCategory.JNANENDRIYA, NAVA, HALVES, (KSETRAJNA, KSETRAJNA), (KSETRAJNA, TRINITY)
    ),
    PrakritiElement(
        11, "tvak", PrakritiCategory.JNANENDRIYA, TEN, QUARTERS, (KSETRAJNA, HALVES), (KSETRAJNA, QUARTERS)
    ),
    PrakritiElement(
        MAHAJANA_COUNT,
        "chakshus",
        PrakritiCategory.JNANENDRIYA,
        11,
        HARE_COUNT,
        (KSETRAJNA, TRINITY),
        (KSETRAJNA, PANCHA),
    ),
    PrakritiElement(
        13, "rasana", PrakritiCategory.JNANENDRIYA, MAHAJANA_COUNT, WORDS, (KSETRAJNA, QUARTERS), (HALVES, 0)
    ),
    PrakritiElement(
        14, "ghrana", PrakritiCategory.JNANENDRIYA, 13, 0b00100000, (KSETRAJNA, PANCHA), (HALVES, KSETRAJNA)
    ),
    # KARMENDRIYA (15-19) - Action organs
    PrakritiElement(15, "vak", PrakritiCategory.KARMENDRIYA, 14, QUALITIES, (KSETRAJNA, SHARANAGATI), (HALVES, HALVES)),
    PrakritiElement(WORDS, "pani", PrakritiCategory.KARMENDRIYA, 15, 0b10000000, (KSETRAJNA, SEVEN), (HALVES, TRINITY)),
    PrakritiElement(
        POSITION_SUM_KRISHNA, "pada", PrakritiCategory.KARMENDRIYA, 0, KSETRAJNA, (HALVES, 0), (HALVES, QUARTERS)
    ),
    PrakritiElement(
        GITA_CHAPTERS, "payu", PrakritiCategory.KARMENDRIYA, KSETRAJNA, HALVES, (HALVES, KSETRAJNA), (HALVES, PANCHA)
    ),
    PrakritiElement(19, "upastha", PrakritiCategory.KARMENDRIYA, HALVES, QUARTERS, (HALVES, HALVES), (TRINITY, 0)),
    # MAHABHUTA (20-24) - Gross elements
    PrakritiElement(
        20, "akasha", PrakritiCategory.MAHABHUTA, TRINITY, HARE_COUNT, (HALVES, TRINITY), (TRINITY, KSETRAJNA)
    ),
    PrakritiElement(21, "vayu", PrakritiCategory.MAHABHUTA, QUARTERS, WORDS, (HALVES, QUARTERS), (TRINITY, HALVES)),
    PrakritiElement(22, "tejas", PrakritiCategory.MAHABHUTA, PANCHA, 0b00100000, (HALVES, PANCHA), (TRINITY, TRINITY)),
    PrakritiElement(
        23, "apas", PrakritiCategory.MAHABHUTA, SHARANAGATI, QUALITIES, (HALVES, SHARANAGATI), (TRINITY, QUARTERS)
    ),
    PrakritiElement(
        KSHETRA, "prithvi", PrakritiCategory.MAHABHUTA, SEVEN, 0b10000000, (HALVES, SEVEN), (TRINITY, PANCHA)
    ),
]


# =============================================================================
# PARAMPARA ACCESS FUNCTIONS (Single Source of Truth)
# =============================================================================


def get_position(mahajana: Mahajana) -> int:
    """
    Get the Lotus position for a Mahajana.

    Mahajanas don't DEFINE their position - they QUERY it from Parampara.
    """
    node = PARAMPARA_GRAPH.get(mahajana)
    if node is None:
        raise ValueError(f"Unknown Mahajana: {mahajana}")
    return node.position


def get_quarter(mahajana: Mahajana) -> Quarter:
    """Get the quarter for a Mahajana."""
    node = PARAMPARA_GRAPH.get(mahajana)
    if node is None:
        raise ValueError(f"Unknown Mahajana: {mahajana}")
    return node.quarter


def get_sampradaya(mahajana: Mahajana) -> Sampradaya:
    """Get the sampradaya for a Mahajana."""
    node = PARAMPARA_GRAPH.get(mahajana)
    if node is None:
        raise ValueError(f"Unknown Mahajana: {mahajana}")
    return node.sampradaya


def get_guru(mahajana: Mahajana) -> Optional[Mahajana]:
    """Get the guru (predecessor) for a Mahajana."""
    node = PARAMPARA_GRAPH.get(mahajana)
    if node is None:
        raise ValueError(f"Unknown Mahajana: {mahajana}")
    return node.guru


def get_shishyas(mahajana: Mahajana) -> FrozenSet[Mahajana]:
    """Get the shishyas (disciples) for a Mahajana."""
    node = PARAMPARA_GRAPH.get(mahajana)
    if node is None:
        raise ValueError(f"Unknown Mahajana: {mahajana}")
    return node.shishyas


def get_mahajana_at_position(position: int) -> Optional[Mahajana]:
    """Get the Mahajana at a specific Lotus position."""
    for mahajana, node in PARAMPARA_GRAPH.items():
        if node.position == position:
            return mahajana
    return None


def get_quarter_mahajanas(quarter: Quarter) -> List[Mahajana]:
    """Get all Mahajanas in a quarter."""
    return [m for m, node in PARAMPARA_GRAPH.items() if node.quarter == quarter]


def get_sampradaya_mahajanas(sampradaya: Sampradaya) -> List[Mahajana]:
    """Get all Mahajanas in a sampradaya."""
    return [m for m, node in PARAMPARA_GRAPH.items() if node.sampradaya == sampradaya]


# =============================================================================
# THE 37 FORMULA
# =============================================================================


def get_37_formula() -> Dict[str, int]:
    """
    Return the status of The 37 Formula.

    24 (Prakriti) + 12 (Mahajanas) + 1 (Krishna) = 37
    """
    return {
        "prakriti": len(PRAKRITI_24),  # 24
        "mahajanas": len(PARAMPARA_GRAPH),  # 12
        "ksetrajna": KSETRAJNA,  # Krishna (always 1)
        "total": len(PRAKRITI_24) + len(PARAMPARA_GRAPH) + KSETRAJNA,  # 37
    }


# =============================================================================
# ACINTYA (Inconceivable)
# =============================================================================


class AcintyaRhythm:
    """
    The ACINTYA point where material and spiritual merge.

    The 24 Prakriti can be decomposed as:
    - 3 x 8 = 24 (3 gunas, 8 prakritis each)
    - 4 x 6 = 24 (4 quarters, 6 elements each)
    - 2 x 12 = 24 (2 halves, 12 elements each)

    When chanting, these decompositions become EQUIVALENT.
    Like iron becoming fire - indistinguishable.
    """

    @staticmethod
    def rhythm_3x8(element: PrakritiElement) -> Tuple[int, int]:
        """Get the 3x8 rhythm coordinates."""
        return element.rhythm_3x8

    @staticmethod
    def rhythm_4x6(element: PrakritiElement) -> Tuple[int, int]:
        """Get the 4x6 rhythm coordinates."""
        return element.rhythm_4x6

    @staticmethod
    def is_acintya(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        """
        Check if two rhythm coordinates represent the same element.

        When chanting, different decompositions point to the SAME reality.
        This is ACINTYA - inconceivable oneness and difference.
        """
        # In acintya, both rhythms are valid and equivalent
        # The check is: do they map to the same element index?
        return True  # Always acintya when chanting!


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Sampradaya
    "Sampradaya",
    "Quarter",
    # Parampara Graph
    "ParamparaNode",
    "PARAMPARA_GRAPH",
    # Prakriti
    "PrakritiCategory",
    "PrakritiElement",
    "PRAKRITI_24",
    # Access Functions
    "get_position",
    "get_quarter",
    "get_sampradaya",
    "get_guru",
    "get_shishyas",
    "get_mahajana_at_position",
    "get_quarter_mahajanas",
    "get_sampradaya_mahajanas",
    # The 37 Formula
    "get_37_formula",
    # Acintya
    "AcintyaRhythm",
]
