"""
CHAITANYA TATTVA - The Living Principle
=======================================

Srila Prabhupada's Sri Caitanya-caritamrita (1975 Original Release)

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ
 pūrṇaḥ śuddho nitya-mukto 'bhinnatvān nāma-nāminoḥ"
                                        - Padma Purana

"The Name of Krishna is a transcendental wish-fulfilling gem,
 the embodiment of CAITANYA-RASA (consciousness-mellows).
 It is complete, pure, and eternally liberated, because
 the Name and the Named are NON-DIFFERENT (abhinna)."

THE CHAITANYA PRINCIPLE (from _seed.py):
========================================
CHAITANYA_UNION = KRISHNA_COUNT + HARE_COUNT = 4 + 8 = 12

Chaitanya Mahaprabhu = Krishna in the mood of Radha (Hare)!
He came to GIVE what Krishna came to TAKE:
- Krishna: Takes devotion (accepts bhoga)
- Chaitanya: GIVES devotion (distributes prasadam)

THE BHOGA-PRASADAM CONNECTION:
==============================
Bhoga (24) + Observer (1) = Prasadam (25)

WHO is the Observer in the transformation?
- At individual level: The devotee (chanter)
- At cosmic level: CHAITANYA MAHAPRABHU Himself!

Chaitanya's mission = Making EVERYONE the observer (KSETRAJNA)
through the process of Harinama Sankirtana!
"""

from dataclasses import dataclass
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    BALADEV_WHEELS,
    # Chaitanya constants
    CHAITANYA_UNION,
    CONSECUTIVE_PAIRS,
    GAURA_TITHI,
    HARE_COUNT,
    # Jagannath
    JAGANNATH_WHEELS,
    JIVA_CYCLE,
    # Core
    KRISHNA_COUNT,
    KSETRAJNA,
    KSHETRA,
    MAHAJANA_COUNT,
    # Resonance
    MALA,
    NADI_RESONANCE,
    NAKSHATRAS,
    PAIR_REDUNDANCY,
    # Pancha Tattva
    PANCHA,
    POSITION_SUM_HARE,
    # Position sums
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    PRASADAM,
    RAMA_COUNT,
    RATHAYATRA_WHEELS,
    SUBHADRA_WHEELS,
    TRINITY,
    WORDS,
)

# =============================================================================
# RUNDE 1: THE CHAITANYA EQUATION
# =============================================================================
# From _seed.py: CHAITANYA_UNION = KRISHNA_COUNT + HARE_COUNT = 4 + 8 = 12


@dataclass
class ChaitanyaPrinciple:
    """The mathematical principle of Chaitanya Mahaprabhu."""

    krishna_aspect: int  # 4 = KRISHNA_COUNT
    radha_aspect: int  # 8 = HARE_COUNT (Radha = Hare = Shakti)
    union: int  # 12 = Krishna + Radha = Chaitanya
    meaning: str


CHAITANYA_MATH: Final[ChaitanyaPrinciple] = ChaitanyaPrinciple(
    krishna_aspect=KRISHNA_COUNT,  # 4
    radha_aspect=HARE_COUNT,  # 8
    union=CHAITANYA_UNION,  # 12
    meaning="Krishna (4) + Radha/Hare (8) = Chaitanya (12) - Krishna in the mood of Radha",
)

# VERIFICATION
assert CHAITANYA_MATH.union == CHAITANYA_MATH.krishna_aspect + CHAITANYA_MATH.radha_aspect
assert CHAITANYA_UNION == MAHAJANA_COUNT, "Chaitanya = 12 Mahajanas"
assert CHAITANYA_UNION == SUBHADRA_WHEELS, "Chaitanya = Subhadra (union principle)"


# =============================================================================
# RUNDE 2: PANCHA TATTVA (The Five Aspects)
# =============================================================================
# Sri Chaitanya, Nityananda, Advaita, Gadadhara, Srivasa = 5


@dataclass
class PanchaTattvaMember:
    """A member of the Pancha Tattva."""

    name: str
    tattva: str  # Philosophical category
    role: str  # Role in sankirtana
    mahamantra_connection: str


PANCHA_TATTVA_MEMBERS: Final[list[PanchaTattvaMember]] = [
    PanchaTattvaMember(
        name="Sri Chaitanya Mahaprabhu",
        tattva="Bhagavan (Supreme Personality)",
        role="Source of the sankirtana movement",
        mahamantra_connection="HARE (8) - Radha's mood embodied",
    ),
    PanchaTattvaMember(
        name="Sri Nityananda Prabhu",
        tattva="Svayam-prakash (First expansion)",
        role="Distributor of mercy to the fallen",
        mahamantra_connection="RAMA (4) - Balarama's mercy form",
    ),
    PanchaTattvaMember(
        name="Sri Advaita Acharya",
        tattva="Ishvara (Controller incarnation)",
        role="Called Chaitanya to appear",
        mahamantra_connection="KRISHNA (4) - Maha-Vishnu aspect",
    ),
    PanchaTattvaMember(
        name="Sri Gadadhara Pandita",
        tattva="Shakti (Internal energy)",
        role="Represents Radha's devotion",
        mahamantra_connection="HARE×KRISHNA - Devotional exchange",
    ),
    PanchaTattvaMember(
        name="Sri Srivasa Thakura",
        tattva="Jiva (Marginal energy)",
        role="Represents the devotee/recipient",
        mahamantra_connection="KSETRAJNA (1) - The observer/chanter",
    ),
]

# VERIFICATION: 5 members
assert len(PANCHA_TATTVA_MEMBERS) == PANCHA, "Pancha Tattva = 5 members"
assert CONSECUTIVE_PAIRS - PAIR_REDUNDANCY == PANCHA, "8 - 3 = 5 unique pairs = Pancha Tattva"


# =============================================================================
# RUNDE 3: GAURA PURNIMA (The Appearance)
# =============================================================================
# Chaitanya appeared on Phalguna Purnima (full moon)


@dataclass
class GauraPurnimaData:
    """Data about Chaitanya's appearance."""

    tithi: int  # 15 = Full moon
    derivation_1: str  # NAKSHATRAS - MAHAJANA
    derivation_2: str  # PANCHA × TRINITY
    year_ce: int  # 1486
    location: str


GAURA_PURNIMA: Final[GauraPurnimaData] = GauraPurnimaData(
    tithi=GAURA_TITHI,  # 15
    derivation_1=f"NAKSHATRAS - MAHAJANA = {NAKSHATRAS} - {MAHAJANA_COUNT} = {GAURA_TITHI}",
    derivation_2=f"PANCHA × TRINITY = {PANCHA} × {TRINITY} = {GAURA_TITHI}",
    year_ce=1486,
    location="Mayapur, Navadvipa",
)

# VERIFICATION
assert GAURA_TITHI == 15, "Purnima = 15th tithi"
assert GAURA_TITHI == NAKSHATRAS - MAHAJANA_COUNT, "15 = 27 - 12"
assert GAURA_TITHI == PANCHA * TRINITY, "15 = 5 × 3"


# =============================================================================
# RUNDE 4: CHAITANYA-CARITAMRITA STRUCTURE (CC 1975)
# =============================================================================
# Prabhupada's original 17-volume CC release


@dataclass
class CCSection:
    """A section of Chaitanya-caritamrita."""

    name: str
    meaning: str
    chapters: int
    mahamantra_connection: str


# The three sections of CC
CC_SECTIONS: Final[list[CCSection]] = [
    CCSection(
        name="Adi-lila",
        meaning="The beginning pastimes",
        chapters=17,  # 17 chapters!
        mahamantra_connection="17 = POSITION_SUM_KRISHNA = WORDS + KSETRAJNA",
    ),
    CCSection(
        name="Madhya-lila",
        meaning="The middle pastimes",
        chapters=25,  # 25 chapters!
        mahamantra_connection="25 = PRASADAM = KSHETRA + KSETRAJNA",
    ),
    CCSection(
        name="Antya-lila",
        meaning="The final pastimes",
        chapters=20,  # 20 chapters
        mahamantra_connection="20 = WORDS + QUARTERS = 16 + 4",
    ),
]

# Total chapters
CC_TOTAL_CHAPTERS: Final[int] = sum(s.chapters for s in CC_SECTIONS)  # 62

# VERIFICATION: Adi-lila = 17 = KRISHNA position sum!
assert CC_SECTIONS[0].chapters == POSITION_SUM_KRISHNA, "Adi-lila = 17 = Krishna!"

# VERIFICATION: Madhya-lila = 25 = PRASADAM!
assert CC_SECTIONS[1].chapters == PRASADAM, "Madhya-lila = 25 = Prasadam!"


# =============================================================================
# RUNDE 5: THE BHOGA-PRASADAM-CHAITANYA CONNECTION
# =============================================================================
# Chaitanya's mission IS the Bhoga→Prasadam transformation at scale!


@dataclass
class TransformationParallel:
    """Parallel between individual and cosmic transformation."""

    level: str
    bhoga_equivalent: str
    ksetrajna_equivalent: str
    prasadam_equivalent: str


TRANSFORMATION_PARALLELS: Final[list[TransformationParallel]] = [
    TransformationParallel(
        level="Individual",
        bhoga_equivalent="Material food (24 elements)",
        ksetrajna_equivalent="Devotee offering (1)",
        prasadam_equivalent="Spiritualized food (25)",
    ),
    TransformationParallel(
        level="Sound",
        bhoga_equivalent="Material sound (16 words)",
        ksetrajna_equivalent="Chanter's consciousness (1)",
        prasadam_equivalent="Holy Name (17 = Krishna)",
    ),
    TransformationParallel(
        level="Cosmic",
        bhoga_equivalent="Material world (KSHETRA)",
        ksetrajna_equivalent="Chaitanya Mahaprabhu (KSETRAJNA)",
        prasadam_equivalent="Sankirtana movement (PRASADAM)",
    ),
]

# Chaitanya IS the cosmic KSETRAJNA who transforms the entire world
CHAITANYA_AS_KSETRAJNA: Final[str] = """
Chaitanya Mahaprabhu = The cosmic Observer (KSETRAJNA = 1)
His mission: Transform the entire material world (KSHETRA = 24)
Into a spiritualized reality (PRASADAM = 25) through Harinama Sankirtana!

Mathematical proof:
- CHAITANYA_UNION = 12 = KRISHNA (4) + HARE (8)
- 12 mod 17 = 12 (not 0, not 1 - because He IS the transformer, not the transformed!)
- But His GIFT (the Holy Name) = 137 mod 17 = 1 (KSETRAJNA embedded!)
"""


# =============================================================================
# RUNDE 6: HARINAMA SANKIRTANA (The Method)
# =============================================================================


@dataclass
class SankirtanaFormula:
    """The formula for congregational chanting."""

    participants: int  # Number of chanters
    individual_mantras: int  # MALA = 108
    group_multiplier: int  # From KIRTAN_RESONANCE
    total_potency: int


def calculate_sankirtana_potency(participants: int) -> SankirtanaFormula:
    """
    Calculate the potency of congregational chanting.

    In Kali Yuga, congregational chanting is especially powerful.
    The potency grows with participants.
    """
    individual = MALA  # 108 per round

    # Group multiplier based on Chaitanya principle
    # Each participant adds KSETRAJNA (1) to the collective field
    multiplier = participants * KSETRAJNA + CHAITANYA_UNION  # participants + 12 (Chaitanya's blessing)

    total = individual * multiplier

    return SankirtanaFormula(
        participants=participants,
        individual_mantras=individual,
        group_multiplier=multiplier,
        total_potency=total,
    )


# Standard sankirtana (5 participants = Pancha Tattva)
PANCHA_TATTVA_SANKIRTANA: Final[SankirtanaFormula] = calculate_sankirtana_potency(PANCHA)

# VERIFICATION
assert PANCHA_TATTVA_SANKIRTANA.participants == 5, "Pancha Tattva = 5"


# =============================================================================
# RUNDE 7: THE 1975 CONNECTION (CC Original Release)
# =============================================================================

CC_1975_FACTS: Final[dict[str, str]] = {
    "year": "1975",
    "publisher": "Bhaktivedanta Book Trust (BBT)",
    "translator": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupada",
    "volumes": "17 volumes (original hardcover set)",
    "significance": "First complete English translation with Gaudiya Vaishnava purports",
    "mathematical_connection": "17 volumes = POSITION_SUM_KRISHNA = WORDS + KSETRAJNA",
}

# 17 volumes = Krishna's position sum!
CC_VOLUMES: Final[int] = 17

# VERIFICATION
assert CC_VOLUMES == POSITION_SUM_KRISHNA, "17 volumes = Krishna position sum!"
assert CC_VOLUMES == WORDS + KSETRAJNA, "17 = 16 + 1 (Mahamantra + Observer)"


# =============================================================================
# RUNDE 8: CAITANYA-RASA-VIGRAHA (Embodiment of Consciousness-Mellow)
# =============================================================================
# From Padma Purana: "caitanya-rasa-vigrahaḥ" - embodiment of conscious rasa


@dataclass
class CaitanyaRasa:
    """The mellows of devotional consciousness."""

    rasa: str
    english: str
    chaitanya_connection: str


# The five primary rasas in relation to Chaitanya
CAITANYA_RASAS: Final[list[CaitanyaRasa]] = [
    CaitanyaRasa(
        rasa="Shanta",
        english="Neutrality",
        chaitanya_connection="Advaita Acharya's contemplative aspect",
    ),
    CaitanyaRasa(
        rasa="Dasya",
        english="Servitude",
        chaitanya_connection="Devotees serving Chaitanya's mission",
    ),
    CaitanyaRasa(
        rasa="Sakhya",
        english="Friendship",
        chaitanya_connection="Nityananda's brotherly love",
    ),
    CaitanyaRasa(
        rasa="Vatsalya",
        english="Parental",
        chaitanya_connection="Sachi Mata's motherly affection",
    ),
    CaitanyaRasa(
        rasa="Madhurya",
        english="Conjugal",
        chaitanya_connection="Radha's mood - Chaitanya's inner experience",
    ),
]

# 5 rasas = PANCHA
assert len(CAITANYA_RASAS) == PANCHA, "5 rasas = Pancha"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Chaitanya math
    "ChaitanyaPrinciple",
    "CHAITANYA_MATH",
    # Pancha Tattva
    "PanchaTattvaMember",
    "PANCHA_TATTVA_MEMBERS",
    # Gaura Purnima
    "GauraPurnimaData",
    "GAURA_PURNIMA",
    # CC structure
    "CCSection",
    "CC_SECTIONS",
    "CC_TOTAL_CHAPTERS",
    "CC_1975_FACTS",
    "CC_VOLUMES",
    # Transformation
    "TransformationParallel",
    "TRANSFORMATION_PARALLELS",
    "CHAITANYA_AS_KSETRAJNA",
    # Sankirtana
    "SankirtanaFormula",
    "calculate_sankirtana_potency",
    "PANCHA_TATTVA_SANKIRTANA",
    # Rasa
    "CaitanyaRasa",
    "CAITANYA_RASAS",
]


if __name__ == "__main__":
    print("=== CHAITANYA TATTVA - The Living Principle ===\n")

    print("1. THE CHAITANYA EQUATION")
    print(f"   KRISHNA_COUNT = {KRISHNA_COUNT}")
    print(f"   HARE_COUNT (Radha) = {HARE_COUNT}")
    print(f"   CHAITANYA_UNION = {CHAITANYA_UNION} = Krishna in the mood of Radha!")

    print("\n2. PANCHA TATTVA (5 Aspects)")
    for i, member in enumerate(PANCHA_TATTVA_MEMBERS, 1):
        print(f"   {i}. {member.name}: {member.tattva}")

    print("\n3. GAURA PURNIMA")
    print(f"   Tithi: {GAURA_PURNIMA.tithi} (Purnima = Full Moon)")
    print(f"   Derivation: {GAURA_PURNIMA.derivation_2}")
    print(f"   Year: {GAURA_PURNIMA.year_ce} CE, {GAURA_PURNIMA.location}")

    print("\n4. CHAITANYA-CARITAMRITA (1975)")
    print(f"   Volumes: {CC_VOLUMES} = POSITION_SUM_KRISHNA!")
    for section in CC_SECTIONS:
        print(f"   {section.name}: {section.chapters} chapters")
        print(f"      → {section.mahamantra_connection}")

    print("\n5. BHOGA-PRASADAM-CHAITANYA CONNECTION")
    for tp in TRANSFORMATION_PARALLELS:
        print(f"   {tp.level}: {tp.bhoga_equivalent} + {tp.ksetrajna_equivalent} = {tp.prasadam_equivalent}")

    print("\n6. SANKIRTANA POTENCY (Pancha Tattva)")
    print(f"   {PANCHA_TATTVA_SANKIRTANA.participants} chanters")
    print(f"   Multiplier: {PANCHA_TATTVA_SANKIRTANA.group_multiplier}")
    print(f"   Total potency: {PANCHA_TATTVA_SANKIRTANA.total_potency}")

    print("\n7. CAITANYA-RASA-VIGRAHA (5 Mellows)")
    for rasa in CAITANYA_RASAS:
        print(f"   {rasa.rasa} ({rasa.english})")
