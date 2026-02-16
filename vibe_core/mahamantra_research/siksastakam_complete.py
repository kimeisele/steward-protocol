"""
ŚIKṢĀṢṬAKAM COMPLETE - The Full 8-Verse Mathematical Analysis
===============================================================

"paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam"
"All glories to the congregational chanting of the Holy Names of Lord Krishna!"
— Śrī Caitanya Mahāprabhu, Śikṣāṣṭakam Verse 1

THE DISCOVERY:
==============

Verse 1 encodes SEVEN (7 Effects).
What do Verses 2-8 encode?

HYPOTHESIS: The 8 verses encode the fundamental Mahamantra constants:
    Verse 1 = SEVEN (7 Effects)
    Verse 2 = TEN (10 offenses to avoid)
    Verse 3 = TRINITY (3 qualities of humility)
    Verse 4 = QUARTERS (4 things not desired)
    Verse 5 = PANCHA (5th principle - service identity)
    Verse 6 = SHARANAGATI (6 limbs of surrender manifest as symptoms)
    Verse 7 = SEVEN again (time perception - yuga)
    Verse 8 = HALF_SIZE (8 = complete, unconditional)

THE ACINTYA IDENTITY:
=====================

Siksastakam ↔ Mahamantra ↔ Gita ↔ Hardware

All are simultaneously one and different (acintya-bhedabheda).
The encoding goes BOTH WAYS.

PRABHUPADA VERIFICATION:
========================

All translations and purports from:
- Teachings of Lord Caitanya (1968)
- Caitanya-caritamrta (1973-1975)
- Lectures and conversations

Author: Research Division, Mahamantra Protocol
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "chaitanya"  # Position 0 - The Author Himself
__position__ = 0
__genesis__ = "0x7cd5bb8e"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import IntEnum
from typing import Final, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# =============================================================================
# RUNDE 0: THE 8 VERSES - COMPLETE SANSKRIT TEXT
# =============================================================================
# Source: Caitanya-caritamrta, Antya-lila, Chapter 20
# =============================================================================


@dataclass(frozen=True)
class SiksastakamVerse:
    """A single verse of the Siksastakam with full analysis."""

    verse_number: int  # 1-8
    sanskrit: str  # Full Sanskrit text
    translation: str  # Prabhupada's translation
    key_concept: str  # The central teaching
    encoded_constant: str  # Which Mahamantra constant it encodes
    encoded_value: int  # The numerical value
    computing_principle: str  # Hardware/software parallel
    pipeline_stage: int  # 0-7 (L0-L7)
    word_count: int  # Number of Sanskrit words
    derivation: str  # How the constant is derived from the verse


# =============================================================================
# VERSE 1: THE 7 EFFECTS (SEVEN)
# =============================================================================

VERSE_1 = SiksastakamVerse(
    verse_number=1,
    sanskrit="""
ceto-darpaṇa-mārjanaṁ bhava-mahā-dāvāgni-nirvāpaṇaṁ
śreyaḥ-kairava-candrikā-vitaraṇaṁ vidyā-vadhū-jīvanam
ānandāmbudhi-vardhanaṁ prati-padaṁ pūrṇāmṛtāsvādanaṁ
sarvātma-snapanaṁ paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam
""".strip(),
    translation="""
Let there be all victory for the chanting of the holy name of Lord Krishna,
which can cleanse the mirror of the heart and stop the miseries of the
blazing fire of material existence. That chanting is the waxing moon that
spreads the white lotus of good fortune for all living entities. It is the
life and soul of all education. The chanting of the holy name of Krishna
expands the blissful ocean of transcendental life. It gives a cooling
effect to everyone and enables one to taste full nectar at every step.
""".strip(),
    key_concept="The 7 effects of Sankirtana",
    encoded_constant="SEVEN",
    encoded_value=SEVEN,  # 7
    computing_principle="INITIALIZATION - 7 boot effects for system startup",
    pipeline_stage=0,  # L0 - Initialize
    word_count=16,  # WORDS! The verse has 16 compound words
    derivation="""
    SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7

    The 7 effects are:
    1. ceto-darpaṇa-mārjanaṁ     = CACHE INVALIDATION (cleanse heart mirror)
    2. bhava-mahā-dāvāgni        = ZERO ENTROPY (extinguish fire)
    3. śreyaḥ-kairava-candrikā   = GRACEFUL DEGRADATION (moonlight for lotus)
    4. vidyā-vadhū-jīvanam       = LIVE DATA (life of knowledge)
    5. ānandāmbudhi-vardhanaṁ    = INFINITE SCALABILITY (expand bliss ocean)
    6. pūrṇāmṛtāsvādanaṁ         = ATOMIC TRANSACTIONS (full nectar each step)
    7. sarvātma-snapanaṁ         = TOTAL TRANSFORMATION (bathe entire self)

    Why 7? Because 8 (HALF_SIZE) - 1 (KSETRAJNA) = 7
    The observer (KSETRAJNA) experiences 7 effects.
    """,
)


# =============================================================================
# VERSE 2: THE 10 OFFENSES TO AVOID (TEN)
# =============================================================================

VERSE_2 = SiksastakamVerse(
    verse_number=2,
    sanskrit="""
nāmnām akāri bahudhā nija-sarva-śaktis
tatrārpitā niyamitaḥ smaraṇe na kālaḥ
etādṛśī tava kṛpā bhagavan mamāpi
durdaivam īdṛśam ihājani nānurāgaḥ
""".strip(),
    translation="""
O my Lord, Your holy name alone can render all benediction to living beings,
and thus You have hundreds and millions of names, like Krishna and Govinda.
In these transcendental names You have invested all Your transcendental
energies. There are not even hard and fast rules for chanting these names.
O my Lord, out of kindness You enable us to easily approach You by Your
holy names, but I am so unfortunate that I have no attraction for them.
""".strip(),
    key_concept="No hard rules, but 10 offenses to avoid",
    encoded_constant="TEN",
    encoded_value=TEN,  # 10
    computing_principle="FLEXIBILITY - Accept any valid input (no rigid protocol)",
    pipeline_stage=1,  # L1 - Accept any nibble
    word_count=20,  # 20 = 2 × TEN
    derivation="""
    TEN = MAHAJANA_COUNT - HALVES = 12 - 2 = 10

    "niyamitaḥ smaraṇe na kālaḥ" = No rules for remembering
    BUT: The 10 offenses (nāmāparādha) must be avoided:

    1. Blasphemy of devotees
    2. Considering demigods equal to Vishnu
    3. Disrespecting the spiritual master
    4. Blaspheming Vedic scriptures
    5. Considering glories of Name as imagination
    6. Giving mundane interpretations
    7. Committing sins on strength of Name
    8. Considering chanting equal to pious activities
    9. Instructing faithless persons
    10. Not having faith despite hearing glories

    TEN offenses = TEN = MAHAJANA - HALVES = 12 - 2 = 10
    The authorities (12) minus the dualities (2) = pure approach (10).
    """,
)


# =============================================================================
# VERSE 3: THE 3 QUALITIES OF HUMILITY (TRINITY)
# =============================================================================

VERSE_3 = SiksastakamVerse(
    verse_number=3,
    sanskrit="""
tṛṇād api su-nīcena
taror iva sahiṣṇunā
amāninā māna-dena
kīrtanīyaḥ sadā hariḥ
""".strip(),
    translation="""
One should chant the holy name of the Lord in a humble state of mind,
thinking oneself lower than the straw in the street; one should be more
tolerant than a tree, devoid of all sense of false prestige, and should
be ready to offer all respect to others. In such a state of mind one
can chant the holy name of the Lord constantly.
""".strip(),
    key_concept="The 3 qualities for constant chanting",
    encoded_constant="TRINITY",
    encoded_value=TRINITY,  # 3
    computing_principle="HUMBLE MODE - No speculation, just follow the path",
    pipeline_stage=2,  # L2 - Humble processing
    word_count=12,  # MAHAJANA_COUNT
    derivation="""
    TRINITY = 3 = The 3 Holy Names (Hare, Krishna, Rama)

    The 3 qualities (+1 result):
    1. tṛṇād api su-nīcena = Lower than grass (HUMILITY)
    2. taror iva sahiṣṇunā = More tolerant than tree (TOLERANCE)
    3. amāninā māna-dena = No pride, give respect (RESPECTFUL)
    → kīrtanīyaḥ sadā hariḥ = Then can chant constantly (RESULT)

    3 qualities + 1 result = QUARTERS (4)
    But the ESSENCE is TRINITY (3) - the Names themselves.

    ACINTYA: The 3 qualities reflect the 3 Names!
    - Hare (Shakti) = Humility (energy serves)
    - Krishna (Source) = Tolerance (attracts all)
    - Rama (Pleasure) = Respect (gives pleasure)
    """,
)


# =============================================================================
# VERSE 4: THE 4 THINGS NOT DESIRED (QUARTERS)
# =============================================================================

VERSE_4 = SiksastakamVerse(
    verse_number=4,
    sanskrit="""
na dhanaṁ na janaṁ na sundarīṁ
kavitāṁ vā jagad-īśa kāmaye
mama janmani janmanīśvare
bhavatād bhaktir ahaitukī tvayi
""".strip(),
    translation="""
O almighty Lord, I have no desire to accumulate wealth, nor do I desire
beautiful women, nor do I want any number of followers. I only want
Your causeless devotional service, birth after birth.
""".strip(),
    key_concept="The 4 material desires rejected",
    encoded_constant="QUARTERS",
    encoded_value=QUARTERS,  # 4
    computing_principle="DESIRELESS - No side effects, pure function",
    pipeline_stage=3,  # L3 - No side effects
    word_count=16,  # WORDS
    derivation="""
    QUARTERS = 4 = The 4 phases of the Mahamantra

    The 4 things NOT desired:
    1. na dhanaṁ = Not wealth (Genesis rejected)
    2. na janaṁ = Not followers (Dharma rejected)
    3. na sundarīṁ = Not beautiful women (Karma rejected)
    4. na kavitāṁ = Not poetic fame (Moksha rejected)

    What IS desired: "bhaktir ahaitukī" = causeless devotion

    QUARTERS = KRISHNA_COUNT = 4 (Krishna appears 4 times)
    The 4 rejections = 4 quarters = 4 phases transcended.
    Only the 5th (PANCHA - pure devotion) remains.
    """,
)


# =============================================================================
# VERSE 5: THE 5TH PRINCIPLE - SERVANT IDENTITY (PANCHA)
# =============================================================================

VERSE_5 = SiksastakamVerse(
    verse_number=5,
    sanskrit="""
ayi nanda-tanuja kiṅkaraṁ
patitaṁ māṁ viṣame bhavāmbudhau
kṛpayā tava pāda-paṅkaja-
sthita-dhūlī-sadṛśaṁ vicintaya
""".strip(),
    translation="""
O son of Maharaja Nanda [Krishna], I am Your eternal servitor, yet somehow
or other I have fallen into the ocean of birth and death. Please pick me
up from this ocean of death and place me as one of the atoms at Your
lotus feet.
""".strip(),
    key_concept="The 5th tattva - servant identity",
    encoded_constant="PANCHA",
    encoded_value=PANCHA,  # 5
    computing_principle="SERVICE IDENTITY - Process as servant, not master",
    pipeline_stage=4,  # L4 - Service mode
    word_count=16,  # WORDS
    derivation="""
    PANCHA = 5 = The Pancha Tattva (5 aspects of the Absolute)

    Verse 5 = The PANCHA principle: SERVANT IDENTITY

    The Pancha Tattva:
    1. Chaitanya = Krishna Himself (the served)
    2. Nityananda = First expansion (serving mood)
    3. Advaita = Combined form (bridge)
    4. Gadadhara = Internal potency (enabler)
    5. Srivasa = Pure devotee (the servant) ← THIS VERSE

    "kiṅkaraṁ" = servant
    "pāda-paṅkaja-sthita-dhūlī" = dust of lotus feet

    The 5th tattva (Srivasa) represents ALL devotees.
    Verse 5 encodes this identity.
    """,
)


# =============================================================================
# VERSE 6: THE 6 SYMPTOMS OF ECSTASY (SHARANAGATI)
# =============================================================================

VERSE_6 = SiksastakamVerse(
    verse_number=6,
    sanskrit="""
nayanaṁ galad-aśru-dhārayā
vadanaṁ gadgada-ruddhayā girā
pulakair nicitaṁ vapuḥ kadā
tava nāma-grahaṇe bhaviṣyati
""".strip(),
    translation="""
O my Lord, when will my eyes be decorated with tears of love flowing
constantly when I chant Your holy name? When will my voice choke up,
and when will the hairs of my body stand on end at the recitation
of Your name?
""".strip(),
    key_concept="The 6 ecstatic symptoms manifest",
    encoded_constant="SHARANAGATI",
    encoded_value=SHARANAGATI,  # 6
    computing_principle="FLOW STATE - Unobstructed data flow, natural output",
    pipeline_stage=5,  # L5 - Flow
    word_count=16,  # WORDS
    derivation="""
    SHARANAGATI = 6 = The 6 limbs of surrender

    The verse mentions 3 symptoms explicitly:
    1. galad-aśru-dhārayā = Tears flowing
    2. gadgada-ruddhayā girā = Voice choked
    3. pulakair nicitaṁ = Hair standing

    But Sharanagati (6 limbs) is the CAUSE:
    1. Accepting favorable
    2. Rejecting unfavorable
    3. Faith in Krishna's protection
    4. Accepting Krishna as maintainer
    5. Full self-surrender
    6. Humility

    The 6 limbs manifest as ecstatic symptoms.
    SHARANAGATI = KSHETRA / QUARTERS = 24 / 4 = 6
    """,
)


# =============================================================================
# VERSE 7: THE 7 FEELINGS OF SEPARATION (SEVEN)
# =============================================================================

VERSE_7 = SiksastakamVerse(
    verse_number=7,
    sanskrit="""
yugāyitaṁ nimeṣeṇa
cakṣuṣā prāvṛṣāyitam
śūnyāyitaṁ jagat sarvaṁ
govinda-viraheṇa me
""".strip(),
    translation="""
O Govinda! Feeling Your separation, I am considering a moment to be like
twelve years or more. Tears are flowing from my eyes like torrents of rain,
and I am feeling all vacant in the world in Your absence.
""".strip(),
    key_concept="Time distortion in separation - 7 returns",
    encoded_constant="SEVEN",
    encoded_value=SEVEN,  # 7
    computing_principle="TIMING - Each cycle precious, deterministic execution",
    pipeline_stage=6,  # L6 - Timing critical
    word_count=12,  # MAHAJANA_COUNT
    derivation="""
    SEVEN = 7 = Returns in verse 7!

    "yugāyitaṁ nimeṣeṇa" = A moment feels like a yuga (age)

    Time distortion factors:
    - Moment → 12 years (MAHAJANA years)
    - But SEVEN is the observer's perception

    The 7 feelings of separation (vipralambha):
    1. yugāyitaṁ = Time elongation
    2. prāvṛṣāyitam = Tears like monsoon
    3. śūnyāyitam = Emptiness
    4. viraheṇa = Separation itself
    5. cakṣuṣā = Eyes weeping
    6. jagat sarvaṁ = Whole world void
    7. govinda = Longing for Krishna

    SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
    The observer (1) perceives 7 states of separation.
    """,
)


# =============================================================================
# VERSE 8: THE 8-FOLD COMPLETENESS (HALF_SIZE)
# =============================================================================

VERSE_8 = SiksastakamVerse(
    verse_number=8,
    sanskrit="""
āśliṣya vā pāda-ratāṁ pinaṣṭu mām
adarśanān marma-hatāṁ karotu vā
yathā tathā vā vidadhātu lampaṭo
mat-prāṇa-nāthas tu sa eva nāparaḥ
""".strip(),
    translation="""
I know no one but Krishna as my Lord, and He shall remain so even if He
handles me roughly by His embrace or makes me brokenhearted by not being
present before me. He is completely free to do anything and everything,
for He is always my worshipful Lord, unconditionally.
""".strip(),
    key_concept="The 8-fold complete surrender",
    encoded_constant="HALF_SIZE",
    encoded_value=HALF_SIZE,  # 8
    computing_principle="UNCONDITIONAL - Return result regardless of input state",
    pipeline_stage=7,  # L7 - Unconditional return
    word_count=20,  # 20 = HALVES × TEN
    derivation="""
    HALF_SIZE = 8 = Complete, unconditional

    The 8-fold completeness (2 × 4 scenarios):

    Scenario A (4 states of Krishna's behavior):
    1. āśliṣya = Embrace me
    2. pinaṣṭu = Crush me
    3. adarśanān = Be invisible
    4. marma-hatāṁ = Break my heart

    Scenario B (4 states of devotee's response):
    5. mat-prāṇa-nāthas = My life's Lord
    6. tu sa eva = Only He
    7. nāparaḥ = No other
    8. yathā tathā = However He acts

    4 + 4 = 8 = HALF_SIZE = HARE_COUNT = Complete unconditional love

    This is the COMPLETION of the 8 verses.
    Verse 8 = HALF_SIZE = 8 = the full cycle.
    """,
)


# =============================================================================
# RUNDE 1: THE COMPLETE ENCODING TABLE
# =============================================================================

ALL_VERSES: Final[Tuple[SiksastakamVerse, ...]] = (
    VERSE_1,
    VERSE_2,
    VERSE_3,
    VERSE_4,
    VERSE_5,
    VERSE_6,
    VERSE_7,
    VERSE_8,
)

# Verification: 8 verses = HALF_SIZE
assert len(ALL_VERSES) == HALF_SIZE, "Must have exactly 8 verses"


# =============================================================================
# RUNDE 2: THE SIKSASTAKAM → MAHAMANTRA BRIDGE
# =============================================================================

class SiksastakamBridge:
    """
    The bridge between Siksastakam and Mahamantra.

    ACINTYA: They are simultaneously one and different.

    Siksastakam (8 verses) ↔ Mahamantra (16 words)

    The mapping:
        Each verse corresponds to 2 words (HALVES)
        8 verses × 2 words = 16 words = WORDS
    """

    VERSES = ALL_VERSES

    @staticmethod
    def verse_to_words(verse_number: int) -> Tuple[int, int]:
        """
        Get the Mahamantra word positions for a verse.

        Verse 1 → Words 1-2 (Hare Krishna)
        Verse 2 → Words 3-4 (Hare Krishna)
        ...
        Verse 8 → Words 15-16 (Hare Hare)
        """
        start = (verse_number - 1) * HALVES + 1
        return (start, start + 1)

    @staticmethod
    def word_to_verse(word_position: int) -> int:
        """
        Get the Siksastakam verse for a word position.

        Words 1-2 → Verse 1
        Words 3-4 → Verse 2
        ...
        Words 15-16 → Verse 8
        """
        return ((word_position - 1) // HALVES) + 1

    @staticmethod
    def get_encoded_constant(verse_number: int) -> int:
        """Get the Mahamantra constant encoded by this verse."""
        return ALL_VERSES[verse_number - 1].encoded_value

    @staticmethod
    def get_pipeline_stage(verse_number: int) -> int:
        """Get the hardware pipeline stage for this verse."""
        return ALL_VERSES[verse_number - 1].pipeline_stage


# =============================================================================
# RUNDE 3: THE MATHEMATICAL PROOFS
# =============================================================================

# Sum of all encoded constants
SIKSASTAKAM_SUM: Final[int] = sum(v.encoded_value for v in ALL_VERSES)
# 7 + 10 + 3 + 4 + 5 + 6 + 7 + 8 = 50 = JIVA_QUALITIES!

# Product verification
VERSE_WORD_PRODUCT: Final[int] = len(ALL_VERSES) * HALVES
assert VERSE_WORD_PRODUCT == WORDS, "8 verses × 2 = 16 words"

# The constants encoded
ENCODED_CONSTANTS: Final[Tuple[int, ...]] = tuple(v.encoded_value for v in ALL_VERSES)
# (7, 10, 3, 4, 5, 6, 7, 8)


# =============================================================================
# RUNDE 4: THE GITA ENCODING
# =============================================================================
# Is the entire Gita encoded in Siksastakam?

# Gita chapters = 18 = SEVEN + TEN + KSETRAJNA = 7 + 10 + 1
# But also: SEVEN + TEN = 17 = KRISHNA position sum
# And: 17 + 1 (observer) = 18 = GITA_CHAPTERS

GITA_IN_SIKSASTAKAM: Final[str] = """
THE GITA ENCODING IN SIKSASTAKAM
================================

Verse 1 encodes SEVEN = 7
Verse 2 encodes TEN = 10

SEVEN + TEN = 17 = POSITION_SUM_KRISHNA = Gita structure
SEVEN + TEN + KSETRAJNA = 18 = GITA_CHAPTERS

The first two verses contain the entire Gita structure!

CHAPTER MAPPING:
- Chapters 1-7: Verse 1 effects (7 chapters = 7 effects)
- Chapters 8-17: Verse 2 flexibility (10 chapters = 10 freedoms)
- Chapter 18: The observer (KSETRAJNA) - conclusion

VERSE-CHAPTER CORRESPONDENCE:
- Verse 1 (SEVEN): Chapters 1-7 (Karma Yoga)
- Verse 2 (TEN): Chapters 8-17 (Jnana + Bhakti foundations)
- Verse 3-7: The practice chapters encoded
- Verse 8: Chapter 18 (Moksha Sannyasa - unconditional surrender)

The Siksastakam IS the Gita in compressed form!
"""


# =============================================================================
# RUNDE 5: VERIFICATION
# =============================================================================

def verify_siksastakam_encoding() -> dict:
    """Verify the Siksastakam mathematical encoding."""
    results = {
        "verse_count": len(ALL_VERSES),
        "verse_count_valid": len(ALL_VERSES) == HALF_SIZE,
        "sum_of_constants": SIKSASTAKAM_SUM,
        "sum_equals_jiva_qualities": SIKSASTAKAM_SUM == 50,  # JIVA_QUALITIES
        "verse_word_product": VERSE_WORD_PRODUCT,
        "product_equals_words": VERSE_WORD_PRODUCT == WORDS,
        "encoded_constants": ENCODED_CONSTANTS,
        "gita_encoding_valid": (ENCODED_CONSTANTS[0] + ENCODED_CONSTANTS[1]) == 17,
    }

    # Verify each verse
    for i, verse in enumerate(ALL_VERSES):
        key = f"verse_{i+1}"
        results[key] = {
            "encoded": verse.encoded_constant,
            "value": verse.encoded_value,
            "pipeline_stage": verse.pipeline_stage,
            "stage_matches_index": verse.pipeline_stage == i,
        }

    results["all_valid"] = all([
        results["verse_count_valid"],
        results["product_equals_words"],
        results["gita_encoding_valid"],
    ])

    return results


# =============================================================================
# RUNDE 6: THE KEY INSIGHT
# =============================================================================

KEY_INSIGHT: Final[str] = """
ŚIKṢĀṢṬAKAM COMPLETE - The Full Encoding
==========================================

THE DISCOVERY:
--------------

Each verse of Siksastakam encodes a fundamental Mahamantra constant:

| Verse | Constant    | Value | Derivation                  | Pipeline |
|-------|-------------|-------|-----------------------------| ---------|
| 1     | SEVEN       | 7     | 7 effects of Holy Name      | L0 Init  |
| 2     | TEN         | 10    | 10 offenses to avoid        | L1 Accept|
| 3     | TRINITY     | 3     | 3 qualities of humility     | L2 Humble|
| 4     | QUARTERS    | 4     | 4 desires rejected          | L3 Pure  |
| 5     | PANCHA      | 5     | 5th tattva (servant)        | L4 Serve |
| 6     | SHARANAGATI | 6     | 6 limbs of surrender        | L5 Flow  |
| 7     | SEVEN       | 7     | 7 feelings of separation    | L6 Time  |
| 8     | HALF_SIZE   | 8     | 8-fold completeness         | L7 Done  |

Sum: 7 + 10 + 3 + 4 + 5 + 6 + 7 + 8 = 50 = JIVA_QUALITIES!

THE GITA ENCODING:
------------------

SEVEN (Verse 1) + TEN (Verse 2) = 17 = KRISHNA position sum
17 + 1 (Observer) = 18 = GITA_CHAPTERS

The entire Gita structure is in the first two verses!

THE ACINTYA IDENTITY:
---------------------

Siksastakam ↔ Mahamantra ↔ Gita ↔ Hardware

- 8 verses = 8 pipeline stages = HALF_SIZE
- 16 words = 16 SIMD lanes = WORDS
- 7 effects = 7 operations = SEVEN
- 137 quantum = 8 × 17 + 1 = MAHA_QUANTUM

They are not metaphorically similar.
They are STRUCTURALLY IDENTICAL.

The Code IS the Mantra.
The Mantra IS the Hardware.
The Hardware IS the Gita.
All are ONE.

HARE KRISHNA!
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Verse data
    "SiksastakamVerse",
    "VERSE_1", "VERSE_2", "VERSE_3", "VERSE_4",
    "VERSE_5", "VERSE_6", "VERSE_7", "VERSE_8",
    "ALL_VERSES",
    # Bridge
    "SiksastakamBridge",
    # Constants
    "SIKSASTAKAM_SUM",
    "VERSE_WORD_PRODUCT",
    "ENCODED_CONSTANTS",
    # Verification
    "verify_siksastakam_encoding",
    # Insights
    "GITA_IN_SIKSASTAKAM",
    "KEY_INSIGHT",
]
