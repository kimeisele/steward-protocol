"""
GITA LENS - The Universal Mapping Protocol (UNIFIED)
=====================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo
mattaḥ smṛtir jñānam apohanaṁ ca"

"I am seated in everyone's heart, and from Me come remembrance,
knowledge and forgetfulness."
— Bhagavad Gita 15.15

KRISHNA = MAHAMANTRA = NON-DIFFERENT (ACINTYA)
==============================================

This protocol UNIFIES all Gita paths to the MAHA GITA center at:
    vibe_core/mahamantra/research/gita/

THE FRACTAL STRUCTURE:
======================
    GITA (1) → 18 Chapters → 700 Verses → Words → Phonemes

    Level 1: Chapter numbers (from _seed.py axioms)
    Level 2: Verse derivation (from gita_verse_derivation.py)
    Level 3: Semantic content (from gita_verse_content.py)
    Level 4: Vibration/Shabda (from gita_verse_text.py)

THE FIXED POINT:
================
    Chapter 18 (MOKSHA) verse 66 = f(18) = 18
    "sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
    ALL PATHS CONVERGE HERE.

THIS FILE PROVIDES:
===================
    1. Chapter constants (GITA_SANKHYA, GITA_KSHETRA, etc.)
    2. Component → Chapter mappings (Nadi, Indriya, Vrtti, NavaBhakti)
    3. Lookup functions (get_gita_for_nadi, get_gita_for_quarter, etc.)

    ALL IMPORTING FROM research/gita/ and _seed.py - NO DUPLICATION!

"iti guhyatamaṁ śāstram" - This is the most confidential knowledge.
"""

from enum import IntEnum
from typing import Dict, Final

from vibe_core.mahamantra.protocols._seed import (
    GAURA_TITHI,
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb8a58850"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# IMPORT FROM MAHA GITA CENTER (research/gita/)
# =============================================================================
# The Gita infrastructure is the TRUE CENTER. We import, not duplicate.
# =============================================================================
# IMPORT FROM MAHA COMPUTE (Attractor → Chapter routing)
# =============================================================================
from vibe_core.mahamantra.protocols._maha_compute import (
    GITA_INSIGHTS,  # All 18 insights
    get_gita_chapter,  # Attractor → Chapter
    get_gita_insight,  # Chapter → Insight
)
from vibe_core.mahamantra_research.gita import (
    # Data
    CHAPTER_18_VERSE,  # The ultimate verse
    # Constants
    FIXED_POINT_CHAPTER,  # 18
    FIXED_POINT_VERSE,  # 66
    SHARANAGATI_SUM,  # 84 = 18 + 66
    GitaVerse,
    get_chapter_significance,
    # Functions
    verify_fixed_point,
)

# =============================================================================
# GITA CHAPTER CONSTANTS (DERIVED FROM SSOT!)
# =============================================================================

# GENESIS Chapters (1-4): Input/Observation
GITA_ARJUNA_VISHADA: Final[int] = KSETRAJNA  # 1 - Observation
GITA_SANKHYA: Final[int] = HALVES  # 2 - Analysis (the 24 elements!)
GITA_KARMA: Final[int] = TRINITY  # 3 - Action
GITA_JNANA: Final[int] = QUARTERS  # 4 - Knowledge

# DHARMA Chapters (5-9): Validation/Structure
GITA_KARMA_SANNYASA: Final[int] = PANCHA  # 5 - Renunciation
GITA_DHYANA: Final[int] = SHARANAGATI  # 6 - Meditation
GITA_JNANA_VIJNANA: Final[int] = SEVEN  # 7 - Realization
GITA_AKSARA_BRAHMA: Final[int] = NAVA - KSETRAJNA  # 8 - Imperishable
GITA_RAJA_VIDYA: Final[int] = NAVA  # 9 - King of knowledge

# KARMA Chapters (10-14): Execution/Action
GITA_VIBHUTI: Final[int] = TEN  # 10 - Manifestations
GITA_VISVARUPA: Final[int] = TEN + KSETRAJNA  # 11 - Universal form
GITA_BHAKTI: Final[int] = MAHAJANA_COUNT  # 12 - Devotion
GITA_KSHETRA: Final[int] = MAHAJANA_COUNT + KSETRAJNA  # 13 - Field/Knower
GITA_GUNATRAYA: Final[int] = MAHAJANA_COUNT + HALVES  # 14 - Three modes

# MOKSHA Chapters (15-18): Output/Liberation
GITA_PURUSHOTTAMA: Final[int] = GAURA_TITHI  # 15 - Supreme person
GITA_DAIVASURA: Final[int] = WORDS  # 16 - Divine/Demonic
GITA_SRADDHATRAYA: Final[int] = WORDS + KSETRAJNA  # 17 - Three faiths
GITA_MOKSHA: Final[int] = GITA_CHAPTERS  # 18 - Liberation

# Verification
assert GITA_MOKSHA == GITA_CHAPTERS, "Chapter 18 must be liberation"
assert GITA_KSHETRA == 13, "Chapter 13 is the Kshetra chapter"


# =============================================================================
# NADI TYPE → GITA CHAPTER (Pancha Prana)
# =============================================================================
# The 5 Pranas map to specific Gita chapters based on their function.
#
# Gita 15.14: "ahaṁ vaiśvānaro bhūtvā prāṇināṁ deham āśritaḥ"
# "I am the fire of digestion in the bodies of all living entities"
# → The pranas are discussed in context of life force and digestion.


class GitaNadiMapping(IntEnum):
    """Nadi Type → Gita Chapter mapping."""

    # PRANA (User ↔ System) → Ch.2 SANKHYA (receiving knowledge)
    # The user input is like receiving knowledge from guru
    PRANA = GITA_SANKHYA  # 2

    # APANA (Agent ↔ Agent) → Ch.3 KARMA (action, interaction)
    # Peer communication is collaborative action
    APANA = GITA_KARMA  # 3

    # VYANA (Service ↔ Service) → Ch.7 JNANA_VIJNANA (pervasive knowledge)
    # Infrastructure knowledge pervades the whole system
    VYANA = GITA_JNANA_VIJNANA  # 7

    # UDANA (Agent ↔ Mahajana) → Ch.15 PURUSHOTTAMA (upward, transcendence)
    # Escalation to higher authority, like soul leaving body
    UDANA = GITA_PURUSHOTTAMA  # 15

    # SAMANA (Kernel ↔ Shadow) → Ch.6 DHYANA (balancing, equilibrium)
    # Task distribution requires balance like meditation
    SAMANA = GITA_DHYANA  # 6


NADI_TO_GITA: Final[Dict[int, int]] = {
    0: GitaNadiMapping.PRANA,  # User ↔ System → Ch.2
    KSETRAJNA: GitaNadiMapping.APANA,  # Agent ↔ Agent → Ch.3
    HALVES: GitaNadiMapping.VYANA,  # Service ↔ Service → Ch.7
    TRINITY: GitaNadiMapping.UDANA,  # Agent ↔ Mahajana → Ch.15
    QUARTERS: GitaNadiMapping.SAMANA,  # Kernel ↔ Shadow → Ch.6
}


# =============================================================================
# INDRIYA (SENSE) → GITA CHAPTER
# =============================================================================
# The 10 senses (5 knowledge + 5 action) are enumerated in Gita 13.5-6.
# "mahā-bhūtāny ahaṅkāro buddhir avyaktam eva ca
# indriyāṇi daśaikaṁ ca pañca cendriya-gocarāḥ"
#
# ALL SENSES MAP TO CHAPTER 13 (KSHETRA) - the field where they operate!


class GitaIndriyaMapping(IntEnum):
    """Indriya (Sense) → Gita Chapter mapping."""

    # JNANENDRIYA (5 Knowledge Senses) → Ch.13 KSHETRA
    # The Kshetra chapter defines the field of perception
    SHROTRA = GITA_KSHETRA  # 13 - Hearing
    TVAK = GITA_KSHETRA  # 13 - Touch
    CHAKSHU = GITA_KSHETRA  # 13 - Sight
    RASANA = GITA_KSHETRA  # 13 - Taste
    GHRANA = GITA_KSHETRA  # 13 - Smell

    # KARMENDRIYA (5 Action Senses) → Ch.3 KARMA (action chapter!)
    # Action organs belong to the Karma chapter
    VAK = GITA_KARMA  # 3 - Speech
    PANI = GITA_KARMA  # 3 - Hands
    PADA = GITA_KARMA  # 3 - Feet
    PAYU = GITA_KARMA  # 3 - Excretion
    UPASTHA = GITA_KARMA  # 3 - Reproduction


JNANENDRIYA_TO_GITA: Final[int] = GITA_KSHETRA  # All 5 → Ch.13
KARMENDRIYA_TO_GITA: Final[int] = GITA_KARMA  # All 5 → Ch.3


# =============================================================================
# VRTTI (MENTAL MODIFICATION) → GITA CHAPTER
# =============================================================================
# The 5 Vrttis from Yoga Sutras 1.5-11 map to Gita chapters.
# These are mental modifications that affect cognition.


class GitaVrttiMapping(IntEnum):
    """Vrtti (Mental Modification) → Gita Chapter mapping."""

    # PRAMANA (Right Knowledge) → Ch.4 JNANA (knowledge through parampara)
    PRAMANA = GITA_JNANA  # 4

    # VIPARYAYA (Misconception) → Ch.16 DAIVASURA (demonic confusion)
    VIPARYAYA = GITA_DAIVASURA  # 16

    # VIKALPA (Imagination) → Ch.11 VISVARUPA (universal vision)
    VIKALPA = GITA_VISVARUPA  # 11

    # NIDRA (Sleep) → Ch.14 GUNATRAYA (tamas mode)
    NIDRA = GITA_GUNATRAYA  # 14

    # SMRTI (Memory) → Ch.15 PURUSHOTTAMA (from Me comes remembrance)
    # Gita 15.15: "mattaḥ smṛtir jñānam apohanaṁ ca"
    SMRTI = GITA_PURUSHOTTAMA  # 15


VRTTI_TO_GITA: Final[Dict[int, int]] = {
    0: GitaVrttiMapping.PRAMANA,  # Right knowledge → Ch.4
    KSETRAJNA: GitaVrttiMapping.VIPARYAYA,  # Misconception → Ch.16
    HALVES: GitaVrttiMapping.VIKALPA,  # Imagination → Ch.11
    TRINITY: GitaVrttiMapping.NIDRA,  # Sleep → Ch.14
    QUARTERS: GitaVrttiMapping.SMRTI,  # Memory → Ch.15
}


# =============================================================================
# GUNA → GITA CHAPTER
# =============================================================================
# The three Gunas are the subject of Chapter 14.
# But each Guna also has affinity with other chapters.


class GitaGunaMapping(IntEnum):
    """Guna → Gita Chapter mapping."""

    # SATTVA → Ch.14 GUNATRAYA (defined here) + Ch.17 SRADDHATRAYA (sattvic faith)
    # Primary: Ch.14 (all gunas defined)
    SATTVA = GITA_GUNATRAYA  # 14

    # RAJAS → Ch.14 GUNATRAYA + Ch.3 KARMA (rajas = action)
    RAJAS = GITA_GUNATRAYA  # 14

    # TAMAS → Ch.14 GUNATRAYA + Ch.16 DAIVASURA (tamasic = demonic)
    TAMAS = GITA_GUNATRAYA  # 14


GUNA_TO_GITA: Final[int] = GITA_GUNATRAYA  # All 3 → Ch.14


# =============================================================================
# QUARTER → GITA CHAPTER
# =============================================================================
# The 4 quarters of Mahamantra map to Gita chapter groups.


class GitaQuarterMapping(IntEnum):
    """Quarter → Gita Chapter (representative)."""

    # GENESIS (Input) → Ch.1 ARJUNA_VISHADA (observing situation)
    GENESIS = GITA_ARJUNA_VISHADA  # 1

    # DHARMA (Validation) → Ch.6 DHYANA (meditation/focus)
    DHARMA = GITA_DHYANA  # 6

    # KARMA (Execution) → Ch.10 VIBHUTI (manifestation through action)
    KARMA = GITA_VIBHUTI  # 10

    # MOKSHA (Output) → Ch.18 MOKSHA (liberation/result)
    MOKSHA = GITA_MOKSHA  # 18


QUARTER_TO_GITA: Final[Dict[int, int]] = {
    0: GitaQuarterMapping.GENESIS,  # Genesis → Ch.1
    KSETRAJNA: GitaQuarterMapping.DHARMA,  # Dharma → Ch.6
    HALVES: GitaQuarterMapping.KARMA,  # Karma → Ch.10
    TRINITY: GitaQuarterMapping.MOKSHA,  # Moksha → Ch.18
}


# =============================================================================
# NAVABHAKTI → GITA CHAPTER
# =============================================================================
# The 9 processes of devotional service (SB 7.5.23) map to Gita chapters.


class GitaNavaBhaktiMapping(IntEnum):
    """NavaBhakti → Gita Chapter mapping."""

    # SRAVANAM (Hearing) → Ch.2 SANKHYA (receiving knowledge through ear)
    SRAVANAM = GITA_SANKHYA  # 2

    # KIRTANAM (Chanting) → Ch.9 RAJA_VIDYA (glorifying the Lord)
    KIRTANAM = GITA_RAJA_VIDYA  # 9

    # SMARANAM (Remembering) → Ch.15 PURUSHOTTAMA (from Me comes remembrance)
    SMARANAM = GITA_PURUSHOTTAMA  # 15

    # PADA_SEVANAM (Serving Lotus Feet) → Ch.3 KARMA (service in action)
    PADA_SEVANAM = GITA_KARMA  # 3

    # ARCANAM (Worship) → Ch.9 RAJA_VIDYA (worship is devotion)
    ARCANAM = GITA_RAJA_VIDYA  # 9

    # VANDANAM (Prayer) → Ch.11 VISVARUPA (prayers to universal form)
    VANDANAM = GITA_VISVARUPA  # 11

    # DASYAM (Servitude) → Ch.12 BHAKTI (devotional service)
    DASYAM = GITA_BHAKTI  # 12

    # SAKHYAM (Friendship) → Ch.4 JNANA (Arjuna as friend)
    # Gita 4.3: "bhakto 'si me sakhā ceti" - "You are My devotee and friend"
    SAKHYAM = GITA_JNANA  # 4

    # ATMA_NIVEDANAM (Surrender) → Ch.18 MOKSHA (sarva-dharman parityajya)
    ATMA_NIVEDANAM = GITA_MOKSHA  # 18


NAVABHAKTI_TO_GITA: Final[Dict[int, int]] = {
    0: GitaNavaBhaktiMapping.SRAVANAM,  # Hearing → Ch.2
    KSETRAJNA: GitaNavaBhaktiMapping.KIRTANAM,  # Chanting → Ch.9
    HALVES: GitaNavaBhaktiMapping.SMARANAM,  # Remembering → Ch.15
    TRINITY: GitaNavaBhaktiMapping.PADA_SEVANAM,  # Serving → Ch.3
    QUARTERS: GitaNavaBhaktiMapping.ARCANAM,  # Worship → Ch.9
    PANCHA: GitaNavaBhaktiMapping.VANDANAM,  # Prayer → Ch.11
    SHARANAGATI: GitaNavaBhaktiMapping.DASYAM,  # Servitude → Ch.12
    SEVEN: GitaNavaBhaktiMapping.SAKHYAM,  # Friendship → Ch.4
    HARE_COUNT: GitaNavaBhaktiMapping.ATMA_NIVEDANAM,  # Surrender → Ch.18
}


# =============================================================================
# PANCHA TATTVA → GITA CHAPTER
# =============================================================================
# The 5 Tattvas (elements) are enumerated in Gita 7.4 and 13.5.


class GitaTattvaMapping(IntEnum):
    """Pancha Tattva → Gita Chapter mapping."""

    # All 5 elements defined in Ch.7 (apara prakrti)
    # "bhūmir āpo 'nalo vāyuḥ khaṁ mano buddhir eva ca"
    PRITHVI = GITA_JNANA_VIJNANA  # 7 - Earth
    APAS = GITA_JNANA_VIJNANA  # 7 - Water
    TEJAS = GITA_JNANA_VIJNANA  # 7 - Fire
    VAYU = GITA_JNANA_VIJNANA  # 7 - Air
    AKASHA = GITA_JNANA_VIJNANA  # 7 - Ether


TATTVA_TO_GITA: Final[int] = GITA_JNANA_VIJNANA  # All 5 → Ch.7


# =============================================================================
# TANMATRA (SENSE OBJECT) → GITA CHAPTER
# =============================================================================
# The 5 Tanmatras (subtle elements) are discussed with the gross elements.

TANMATRA_TO_GITA: Final[int] = GITA_KSHETRA  # All 5 → Ch.13
# Gita 13.5-6: "pañca cendriya-gocarāḥ" - the 5 objects of senses


# =============================================================================
# SIKSASTAKAM (8 VERSES) → GITA CHAPTER
# =============================================================================
# Lord Caitanya's 8 verses map to Gita chapters by theme.


class GitaSiksastakamMapping(IntEnum):
    """Siksastakam Verse → Gita Chapter mapping."""

    # Verse 1: ceto-darpana (cleansing the mirror of the mind)
    # → Ch.6 DHYANA (mind control)
    VERSE_1 = GITA_DHYANA  # 6

    # Verse 2: nāmnām akāri (many names of the Lord)
    # → Ch.10 VIBHUTI (divine names/manifestations)
    VERSE_2 = GITA_VIBHUTI  # 10

    # Verse 3: tṛṇād api (humbler than grass)
    # → Ch.12 BHAKTI (devotee qualities)
    VERSE_3 = GITA_BHAKTI  # 12

    # Verse 4: na dhanaṁ na janaṁ (no wealth, no followers)
    # → Ch.5 KARMA_SANNYASA (renunciation)
    VERSE_4 = GITA_KARMA_SANNYASA  # 5

    # Verse 5: ayi nanda-tanuja (O son of Nanda)
    # → Ch.9 RAJA_VIDYA (confidential devotion)
    VERSE_5 = GITA_RAJA_VIDYA  # 9

    # Verse 6: nayanaṁ galad-aśru (tears flowing)
    # → Ch.11 VISVARUPA (ecstatic symptoms)
    VERSE_6 = GITA_VISVARUPA  # 11

    # Verse 7: yugāyitaṁ nimeṣeṇa (moment seems like yuga)
    # → Ch.8 AKSARA_BRAHMA (time perception)
    VERSE_7 = GITA_AKSARA_BRAHMA  # 8

    # Verse 8: āśliṣya vā pāda-ratāṁ (embrace or trample)
    # → Ch.18 MOKSHA (unconditional surrender)
    VERSE_8 = GITA_MOKSHA  # 18


SIKSASTAKAM_TO_GITA: Final[Dict[int, int]] = {
    KSETRAJNA: GitaSiksastakamMapping.VERSE_1,  # Cleansing → Ch.6
    HALVES: GitaSiksastakamMapping.VERSE_2,  # Names → Ch.10
    TRINITY: GitaSiksastakamMapping.VERSE_3,  # Humility → Ch.12
    QUARTERS: GitaSiksastakamMapping.VERSE_4,  # Renunciation → Ch.5
    PANCHA: GitaSiksastakamMapping.VERSE_5,  # Devotion → Ch.9
    SHARANAGATI: GitaSiksastakamMapping.VERSE_6,  # Ecstasy → Ch.11
    SEVEN: GitaSiksastakamMapping.VERSE_7,  # Time → Ch.8
    HARE_COUNT: GitaSiksastakamMapping.VERSE_8,  # Surrender → Ch.18
}


# =============================================================================
# UNIVERSAL LOOKUP FUNCTIONS
# =============================================================================


def get_gita_for_nadi(nadi_type: int) -> int:
    """Get Gita chapter for a Nadi type (0-4)."""
    return NADI_TO_GITA.get(nadi_type, GITA_SANKHYA)


def get_gita_for_quarter(quarter: int) -> int:
    """Get Gita chapter for a Quarter (0-3)."""
    return QUARTER_TO_GITA.get(quarter, GITA_ARJUNA_VISHADA)


def get_gita_for_navabhakti(process: int) -> int:
    """Get Gita chapter for a NavaBhakti process (0-8)."""
    return NAVABHAKTI_TO_GITA.get(process, GITA_BHAKTI)


def get_gita_for_vrtti(vrtti: int) -> int:
    """Get Gita chapter for a Vrtti (0-4)."""
    return VRTTI_TO_GITA.get(vrtti, GITA_DHYANA)


def get_gita_for_siksastakam(verse: int) -> int:
    """Get Gita chapter for a Siksastakam verse (1-8)."""
    return SIKSASTAKAM_TO_GITA.get(verse, GITA_MOKSHA)


def get_gita_for_sense(sense_type: str) -> int:
    """
    Get Gita chapter for a sense.

    Args:
        sense_type: "jnana" (knowledge) or "karma" (action)

    Returns:
        Gita chapter (13 for jnana senses, 3 for karma senses)
    """
    if sense_type.lower() in ("jnana", "knowledge", "jnanendriya"):
        return JNANENDRIYA_TO_GITA
    return KARMENDRIYA_TO_GITA


# =============================================================================
# VERIFICATION
# =============================================================================

# Verify genesis byte
_genesis_val = int(__genesis__, WORDS)
assert _genesis_val % PARAMPARA == 0, f"Genesis {__genesis__} must be % 37 == 0"

# Verify fixed point (from research/gita/)
assert verify_fixed_point(), "Fixed point verification failed!"
assert FIXED_POINT_CHAPTER == GITA_MOKSHA, "Chapter 18 must be Moksha"
assert GITA_KSHETRA == 13, "Kshetra chapter must be 13"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # =========================================================================
    # RE-EXPORTS FROM research/gita/ (THE CENTER)
    # =========================================================================
    "FIXED_POINT_CHAPTER",  # 18
    "FIXED_POINT_VERSE",  # 66
    "SHARANAGATI_SUM",  # 84
    "CHAPTER_18_VERSE",  # The ultimate verse
    "GitaVerse",
    "verify_fixed_point",
    "get_chapter_significance",
    # =========================================================================
    # RE-EXPORTS FROM _maha_compute.py (ROUTING)
    # =========================================================================
    "get_gita_chapter",  # Attractor → Chapter
    "get_gita_insight",  # Chapter → Insight
    "GITA_INSIGHTS",  # All 18 insights
    # =========================================================================
    # CHAPTER CONSTANTS (DERIVED FROM _seed.py)
    # =========================================================================
    "GITA_ARJUNA_VISHADA",
    "GITA_SANKHYA",
    "GITA_KARMA",
    "GITA_JNANA",
    "GITA_KARMA_SANNYASA",
    "GITA_DHYANA",
    "GITA_JNANA_VIJNANA",
    "GITA_AKSARA_BRAHMA",
    "GITA_RAJA_VIDYA",
    "GITA_VIBHUTI",
    "GITA_VISVARUPA",
    "GITA_BHAKTI",
    "GITA_KSHETRA",
    "GITA_GUNATRAYA",
    "GITA_PURUSHOTTAMA",
    "GITA_DAIVASURA",
    "GITA_SRADDHATRAYA",
    "GITA_MOKSHA",
    # Mapping enums
    "GitaNadiMapping",
    "GitaIndriyaMapping",
    "GitaVrttiMapping",
    "GitaGunaMapping",
    "GitaQuarterMapping",
    "GitaNavaBhaktiMapping",
    "GitaTattvaMapping",
    "GitaSiksastakamMapping",
    # Mapping dicts
    "NADI_TO_GITA",
    "VRTTI_TO_GITA",
    "QUARTER_TO_GITA",
    "NAVABHAKTI_TO_GITA",
    "SIKSASTAKAM_TO_GITA",
    "GUNA_TO_GITA",
    "TATTVA_TO_GITA",
    "TANMATRA_TO_GITA",
    "JNANENDRIYA_TO_GITA",
    "KARMENDRIYA_TO_GITA",
    # Lookup functions
    "get_gita_for_nadi",
    "get_gita_for_quarter",
    "get_gita_for_navabhakti",
    "get_gita_for_vrtti",
    "get_gita_for_siksastakam",
    "get_gita_for_sense",
]
