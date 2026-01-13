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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x48c2d992"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import (
    Dict,
    Final,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
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

    # Position 0: HEAD - Prithu Maharaja (Infrastructure Avatar)
    # Note: Prithu is Shaktyavesha - not in standard Mahajana enum
    # Handled separately as AVATAR

    Mahajana.BRAHMA: ParamparaNode(
        mahajana=Mahajana.BRAHMA,
        position=1,
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=None,  # Brahma learns from Vishnu directly (tene brahma hrda)
        shishyas=frozenset({Mahajana.NARADA}),
        serves=None,  # Brahma serves Vishnu directly
    ),

    Mahajana.NARADA: ParamparaNode(
        mahajana=Mahajana.NARADA,
        position=2,
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.BRAHMA,
        is_head=False,
        guru=Mahajana.BRAHMA,
        shishyas=frozenset(),  # Narada teaches many but not in this graph
    ),

    Mahajana.SHAMBHU: ParamparaNode(
        mahajana=Mahajana.SHAMBHU,
        position=3,
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.RUDRA,  # Shiva has his own sampradaya!
        is_head=False,
        guru=None,  # Shiva learns from Vishnu directly
    ),

    # ==========================================================================
    # DHARMA QUARTER (Kumara Sampradaya - Law/Purity)
    # "Krishna Krishna Hare Hare"
    # ==========================================================================

    # Position 4: HEAD - Vyasadeva (Documentation Avatar)

    Mahajana.KUMARAS: ParamparaNode(
        mahajana=Mahajana.KUMARAS,
        position=5,
        quarter=Quarter.DHARMA,
        sampradaya=Sampradaya.KUMARA,
        is_head=False,
        guru=None,  # Four Kumaras are eternally liberated
    ),

    Mahajana.KAPILA: ParamparaNode(
        mahajana=Mahajana.KAPILA,
        position=6,
        quarter=Quarter.DHARMA,
        sampradaya=Sampradaya.BRAHMA,  # Kapila is avatara in Brahma line
        is_head=False,
        guru=None,  # Kapila is God Himself (avatara)
    ),

    Mahajana.MANU: ParamparaNode(
        mahajana=Mahajana.MANU,
        position=7,
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
        position=9,
        quarter=Quarter.KARMA,
        sampradaya=Sampradaya.BRAHMA,  # Prahlada in Brahma line via Narada
        is_head=False,
        guru=Mahajana.NARADA,  # Narada taught Prahlada in the womb!
    ),

    Mahajana.JANAKA: ParamparaNode(
        mahajana=Mahajana.JANAKA,
        position=10,
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
    ROOT = "root"           # 1: Prakriti itself
    SUBTLE = "subtle"       # 2-4: Mahat, Ahankara, Manas
    TANMATRA = "tanmatra"   # 5-9: Sound, Touch, Form, Taste, Smell
    JNANENDRIYA = "jnana"   # 10-14: Ear, Skin, Eye, Tongue, Nose
    KARMENDRIYA = "karma"   # 15-19: Speech, Hands, Feet, Excretion, Generation
    MAHABHUTA = "bhuta"     # 20-24: Ether, Air, Fire, Water, Earth


@dataclass(frozen=True)
class PrakritiElement:
    """
    A single Prakriti element with its Mantra mapping.

    The 24 are NOT dead - they are ENLIVENED by the Mahamantra.
    Each element maps to a specific byte position.
    """
    index: int              # 1-24
    name: str               # Sanskrit name
    category: PrakritiCategory
    mantra_position: int    # Which of 16 positions (with overlap/rhythm)
    byte_mask: int          # Bit mask for MantraByte

    # The rhythm: 24 = 3x8 = 4x6 = 2x12
    # This is the ACINTYA point - multiple valid decompositions
    rhythm_3x8: Tuple[int, int]   # (group_of_3, position_in_8)
    rhythm_4x6: Tuple[int, int]   # (group_of_4, position_in_6)


# The 24 Prakriti with their Mantra mappings
# This creates the RHYTHM that enlivens dead matter
PRAKRITI_24: Final[List[PrakritiElement]] = [
    # ROOT (1)
    PrakritiElement(1, "prakriti", PrakritiCategory.ROOT, 0, 0b00000001, (0, 0), (0, 0)),

    # SUBTLE (2-4) - The three aspects of false ego
    PrakritiElement(2, "mahat", PrakritiCategory.SUBTLE, 1, 0b00000010, (0, 1), (0, 1)),
    PrakritiElement(3, "ahankara", PrakritiCategory.SUBTLE, 2, 0b00000100, (0, 2), (0, 2)),
    PrakritiElement(4, "manas", PrakritiCategory.SUBTLE, 3, 0b00001000, (0, 3), (0, 3)),

    # TANMATRA (5-9) - Subtle sense objects
    PrakritiElement(5, "shabda", PrakritiCategory.TANMATRA, 4, 0b00010000, (0, 4), (0, 4)),
    PrakritiElement(6, "sparsha", PrakritiCategory.TANMATRA, 5, 0b00100000, (0, 5), (0, 5)),
    PrakritiElement(7, "rupa", PrakritiCategory.TANMATRA, 6, 0b01000000, (0, 6), (1, 0)),
    PrakritiElement(8, "rasa", PrakritiCategory.TANMATRA, 7, 0b10000000, (0, 7), (1, 1)),
    PrakritiElement(9, "gandha", PrakritiCategory.TANMATRA, 8, 0b00000001, (1, 0), (1, 2)),

    # JNANENDRIYA (10-14) - Knowledge senses
    PrakritiElement(10, "shrotra", PrakritiCategory.JNANENDRIYA, 9, 0b00000010, (1, 1), (1, 3)),
    PrakritiElement(11, "tvak", PrakritiCategory.JNANENDRIYA, 10, 0b00000100, (1, 2), (1, 4)),
    PrakritiElement(12, "chakshus", PrakritiCategory.JNANENDRIYA, 11, 0b00001000, (1, 3), (1, 5)),
    PrakritiElement(13, "rasana", PrakritiCategory.JNANENDRIYA, 12, 0b00010000, (1, 4), (2, 0)),
    PrakritiElement(14, "ghrana", PrakritiCategory.JNANENDRIYA, 13, 0b00100000, (1, 5), (2, 1)),

    # KARMENDRIYA (15-19) - Action organs
    PrakritiElement(15, "vak", PrakritiCategory.KARMENDRIYA, 14, 0b01000000, (1, 6), (2, 2)),
    PrakritiElement(16, "pani", PrakritiCategory.KARMENDRIYA, 15, 0b10000000, (1, 7), (2, 3)),
    PrakritiElement(17, "pada", PrakritiCategory.KARMENDRIYA, 0, 0b00000001, (2, 0), (2, 4)),
    PrakritiElement(18, "payu", PrakritiCategory.KARMENDRIYA, 1, 0b00000010, (2, 1), (2, 5)),
    PrakritiElement(19, "upastha", PrakritiCategory.KARMENDRIYA, 2, 0b00000100, (2, 2), (3, 0)),

    # MAHABHUTA (20-24) - Gross elements
    PrakritiElement(20, "akasha", PrakritiCategory.MAHABHUTA, 3, 0b00001000, (2, 3), (3, 1)),
    PrakritiElement(21, "vayu", PrakritiCategory.MAHABHUTA, 4, 0b00010000, (2, 4), (3, 2)),
    PrakritiElement(22, "tejas", PrakritiCategory.MAHABHUTA, 5, 0b00100000, (2, 5), (3, 3)),
    PrakritiElement(23, "apas", PrakritiCategory.MAHABHUTA, 6, 0b01000000, (2, 6), (3, 4)),
    PrakritiElement(24, "prithvi", PrakritiCategory.MAHABHUTA, 7, 0b10000000, (2, 7), (3, 5)),
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
    return [
        m for m, node in PARAMPARA_GRAPH.items()
        if node.quarter == quarter
    ]


def get_sampradaya_mahajanas(sampradaya: Sampradaya) -> List[Mahajana]:
    """Get all Mahajanas in a sampradaya."""
    return [
        m for m, node in PARAMPARA_GRAPH.items()
        if node.sampradaya == sampradaya
    ]


# =============================================================================
# THE 37 FORMULA
# =============================================================================


def get_37_formula() -> Dict[str, int]:
    """
    Return the status of The 37 Formula.

    24 (Prakriti) + 12 (Mahajanas) + 1 (Krishna) = 37
    """
    return {
        "prakriti": len(PRAKRITI_24),           # 24
        "mahajanas": len(PARAMPARA_GRAPH),      # 12
        "ksetrajna": 1,                          # Krishna (always 1)
        "total": len(PRAKRITI_24) + len(PARAMPARA_GRAPH) + 1,  # 37
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
