"""
MĀDHURYA ANALYSIS - Names as Derived Functions
==============================================

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ
pūrṇaḥ śuddho nitya-mukto 'bhinnatvān nāma-nāminoḥ"

"The holy name of Krishna is transcendentally blissful.
It bestows all spiritual benedictions, for it is Krishna Himself,
the reservoir of all pleasure. It is complete, pure, eternally liberated—
because the name and the named are non-different."
— Padma Purana

THE KEY INSIGHT:
================
Names are DERIVED from qualities and activities.
The PERSON is fundamental.
Names are descriptions.

MADHURYA (माधुर्य) = 8 letters = OCTET = SIKSASTAKAM!
Chaitanya is the MĀDHURYA-RASA AVATARA.

HIERARCHY:
==========
1. PERSON (sat-cit-ānanda) - ETERNAL
2. QUALITIES (guṇa) - ASPECTS
3. ACTIVITIES (līlā) - EXPRESSIONS
4. NAMES (nāma) - DESCRIPTIONS

ABHINNA (Non-difference):
=========================
"nāma-nāminoḥ" - the name and the named are non-different.
This is ACINTYA - inconceivable.
The derivation doesn't make the name LESS than the Person.
The derivation shows HOW the name manifests.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xf1ef3526"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Callable, Final

# =============================================================================
# MAHAMANTRA IMPORTS (Single Source of Truth)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    NAVA,
    PANCHA,
    QUALITIES,
    QUARTERS,
)

# Derived constants
OCTET: Final[int] = 8  # Siksastakam verses
PRASADAM: Final[int] = 25  # KSHETRA + KSETRAJNA = 24 + 1


# =============================================================================
# MĀDHURYA = 8 LETTERS = OCTET
# =============================================================================

MADHURYA_LETTERS: Final[str] = "MADHURYA"
MADHURYA_LENGTH: Final[int] = len(MADHURYA_LETTERS)  # 8

# Verify the connection
assert MADHURYA_LENGTH == OCTET, "MADHURYA = 8 letters = OCTET"


@dataclass(frozen=True)
class MadhuryaQuality:
    """One of Krishna's four exclusive qualities (61-64)."""

    number: int
    sanskrit: str
    english: str
    prefix: str
    prefix_length: int
    mahamantra_constant: str


LILA_MADHURYA: Final[MadhuryaQuality] = MadhuryaQuality(
    number=61,
    sanskrit="Līlā-mādhurya",
    english="Wonderful Pastimes",
    prefix="LILA",
    prefix_length=4,
    mahamantra_constant="QUARTERS (4)",
)

PREMA_MADHURYA: Final[MadhuryaQuality] = MadhuryaQuality(
    number=62,
    sanskrit="Prema-mādhurya",
    english="Wonderful Love",
    prefix="PREMA",
    prefix_length=5,
    mahamantra_constant="PANCHA (5)",
)

VENU_MADHURYA: Final[MadhuryaQuality] = MadhuryaQuality(
    number=63,
    sanskrit="Veṇu-mādhurya",
    english="Wonderful Flute",
    prefix="VENU",
    prefix_length=4,
    mahamantra_constant="QUARTERS (4) + 72 Hz!",
)

RUPA_MADHURYA: Final[MadhuryaQuality] = MadhuryaQuality(
    number=64,
    sanskrit="Rūpa-mādhurya",
    english="Wonderful Beauty",
    prefix="RUPA",
    prefix_length=4,
    mahamantra_constant="QUARTERS (4) → QUALITIES (64)",
)

ALL_MADHURYA: Final[tuple[MadhuryaQuality, ...]] = (
    LILA_MADHURYA,
    PREMA_MADHURYA,
    VENU_MADHURYA,
    RUPA_MADHURYA,
)

# Sum of quality numbers
MADHURYA_SUM: Final[int] = sum(m.number for m in ALL_MADHURYA)  # 250
assert MADHURYA_SUM == 250, "61+62+63+64 = 250"
assert MADHURYA_SUM == HALVES * (PANCHA**3), "250 = 2 × 125"

# Total prefix letters + MADHURYA = PRASADAM
TOTAL_PREFIX_LETTERS: Final[int] = sum(m.prefix_length for m in ALL_MADHURYA)  # 17
TOTAL_MADHURYA_LETTERS: Final[int] = TOTAL_PREFIX_LETTERS + MADHURYA_LENGTH  # 25
assert TOTAL_MADHURYA_LETTERS == PRASADAM, "Total = 25 = PRASADAM!"


# =============================================================================
# NAME DERIVATION (Names as Functions)
# =============================================================================


@dataclass(frozen=True)
class NameDerivation:
    """How a name is derived from its root meaning."""

    name: str
    sanskrit_root: str
    root_meaning: str
    derived_meaning: str
    function_notation: str


KRISHNA_DERIVATION: Final[NameDerivation] = NameDerivation(
    name="KRISHNA",
    sanskrit_root="KARSH (कर्ष्)",
    root_meaning="to attract, to draw",
    derived_meaning="The All-Attractive One",
    function_notation="KRISHNA = f(KARSH)",
)

RAMA_DERIVATION: Final[NameDerivation] = NameDerivation(
    name="RAMA",
    sanskrit_root="RAM (रम्)",
    root_meaning="to enjoy, to please, to delight",
    derived_meaning="The Source of All Pleasure",
    function_notation="RAMA = f(RAM)",
)

HARE_DERIVATION: Final[NameDerivation] = NameDerivation(
    name="HARE",
    sanskrit_root="HAR (हर्)",
    root_meaning="to take away, to steal, to remove",
    derived_meaning="The Remover of Obstacles / Stealer of Hearts",
    function_notation="HARE = f(HAR)",
)

ALL_DERIVATIONS: Final[tuple[NameDerivation, ...]] = (
    KRISHNA_DERIVATION,
    RAMA_DERIVATION,
    HARE_DERIVATION,
)


# =============================================================================
# THE HIERARCHY (Person > Qualities > Activities > Names)
# =============================================================================


@dataclass(frozen=True)
class HierarchyLevel:
    """A level in the ontological hierarchy."""

    level: int
    sanskrit: str
    english: str
    nature: str
    computing_parallel: str


LEVEL_PERSON: Final[HierarchyLevel] = HierarchyLevel(
    level=1,
    sanskrit="Puruṣa (पुरुष)",
    english="Person",
    nature="ETERNAL, FUNDAMENTAL (sat-cit-ānanda)",
    computing_parallel="PROTOCOL (the kernel)",
)

LEVEL_QUALITIES: Final[HierarchyLevel] = HierarchyLevel(
    level=2,
    sanskrit="Guṇa (गुण)",
    english="Qualities",
    nature="ASPECTS of the Person",
    computing_parallel="CONSTANTS (the seed values)",
)

LEVEL_ACTIVITIES: Final[HierarchyLevel] = HierarchyLevel(
    level=3,
    sanskrit="Līlā (लीला)",
    english="Activities/Pastimes",
    nature="EXPRESSIONS of the Person",
    computing_parallel="FUNCTIONS (the research modules)",
)

LEVEL_NAMES: Final[HierarchyLevel] = HierarchyLevel(
    level=4,
    sanskrit="Nāma (नाम)",
    english="Names",
    nature="DESCRIPTIONS of Qualities and Activities",
    computing_parallel="VARIABLES (the exports)",
)

ALL_LEVELS: Final[tuple[HierarchyLevel, ...]] = (
    LEVEL_PERSON,
    LEVEL_QUALITIES,
    LEVEL_ACTIVITIES,
    LEVEL_NAMES,
)

# The count is QUARTERS
assert len(ALL_LEVELS) == QUARTERS, "4 hierarchy levels"


# =============================================================================
# ABHINNA PRINCIPLE (Non-Difference)
# =============================================================================


@dataclass(frozen=True)
class AbhinnaPrinciple:
    """The principle of non-difference (nāma-nāminoḥ abhinna)."""

    aspect: str
    difference: str
    non_difference: str
    acintya_resolution: str


ABHINNA_NAME_NAMED: Final[AbhinnaPrinciple] = AbhinnaPrinciple(
    aspect="Name and Named",
    difference="Name is a description, Named is the reality",
    non_difference="In spiritual realm, name IS the named (Padma Purana)",
    acintya_resolution="Simultaneously different AND non-different",
)

ABHINNA_QUALITY_PERSON: Final[AbhinnaPrinciple] = AbhinnaPrinciple(
    aspect="Quality and Person",
    difference="Quality is an aspect, Person is the whole",
    non_difference="Krishna's qualities are inseparable from Krishna",
    acintya_resolution="The part contains the whole (holographic)",
)

ABHINNA_ACTIVITY_PERSON: Final[AbhinnaPrinciple] = AbhinnaPrinciple(
    aspect="Activity and Person",
    difference="Activity is an expression, Person is the source",
    non_difference="Remembering Krishna's pastimes = meeting Krishna",
    acintya_resolution="The expression IS the source manifesting",
)

ALL_ABHINNA: Final[tuple[AbhinnaPrinciple, ...]] = (
    ABHINNA_NAME_NAMED,
    ABHINNA_QUALITY_PERSON,
    ABHINNA_ACTIVITY_PERSON,
)


# =============================================================================
# CHAITANYA = MĀDHURYA-RASA AVATARA
# =============================================================================


@dataclass(frozen=True)
class ChaitanyaPurpose:
    """One of the three purposes for Chaitanya's appearance (CC Adi 4.15-16)."""

    number: int
    sanskrit: str
    english: str
    relation_to_madhurya: str


PURPOSE_RADHA_LOVE: Final[ChaitanyaPurpose] = ChaitanyaPurpose(
    number=1,
    sanskrit="śrī-rādhāyāḥ praṇaya-mahimā",
    english="To understand the glory of Radha's love",
    relation_to_madhurya="Radha's love IS the essence of Mādhurya",
)

PURPOSE_OWN_SWEETNESS: Final[ChaitanyaPurpose] = ChaitanyaPurpose(
    number=2,
    sanskrit="adbhuta-madhurimā",
    english="To experience His own wonderful sweetness (Mādhurya)",
    relation_to_madhurya="MĀDHURYA = the word itself!",
)

PURPOSE_RADHA_BLISS: Final[ChaitanyaPurpose] = ChaitanyaPurpose(
    number=3,
    sanskrit="saukhyaṁ cāsyā",
    english="To taste the bliss Radha experiences",
    relation_to_madhurya="The result of experiencing Mādhurya",
)

ALL_PURPOSES: Final[tuple[ChaitanyaPurpose, ...]] = (
    PURPOSE_RADHA_LOVE,
    PURPOSE_OWN_SWEETNESS,
    PURPOSE_RADHA_BLISS,
)

# Three purposes = TRINITY
assert len(ALL_PURPOSES) == 3, "3 purposes = TRINITY"


# =============================================================================
# THE UNIVERSAL FORMULA
# =============================================================================

# NAME = f(QUALITY, ACTIVITY)
# This is the universal formula for name derivation


def derive_name(quality: str, activity: str) -> str:
    """
    Derive a name from quality and activity.

    In spiritual reality, this is not a creation but a DESCRIPTION.
    The Person already exists eternally.
    The name describes what we can perceive of the Person.
    """
    return f"NAME = f({quality}, {activity})"


# Examples
KRISHNA_FORMULA: Final[str] = derive_name("ALL_ATTRACTIVE", "ATTRACTS_ALL")
RAMA_FORMULA: Final[str] = derive_name("ALL_PLEASING", "GIVES_PLEASURE")
HARE_FORMULA: Final[str] = derive_name("ALL_REMOVING", "TAKES_AWAY_ILLUSION")


# =============================================================================
# KEY INSIGHT
# =============================================================================

KEY_INSIGHT: Final[str] = """
MĀDHURYA ANALYSIS - Names as Derived Functions
==============================================

DIE SCHLÜSSEL-ENTDECKUNG:
-------------------------
MADHURYA = 8 Buchstaben = OCTET = SIKSASTAKAM!

M-A-D-H-U-R-Y-A = 8 Buchstaben
Chaitanya schrieb 8 Verse über MĀDHURYA-RASA!

DIE VIER PRÄFIXE IN MAHAMANTRA-KONSTANTEN:
------------------------------------------
  LĪLĀ  = 4 Buchstaben = QUARTERS
  PREMA = 5 Buchstaben = PANCHA
  VEṆU  = 4 Buchstaben = QUARTERS (+ 72 Hz!)
  RŪPA  = 4 Buchstaben = QUARTERS

  TOTAL: 4 + 5 + 4 + 4 + 8 = 25 = PRASADAM!

NAMEN = ABGELEITETE FUNKTIONEN:
-------------------------------
  NAME = f(QUALITÄT, AKTIVITÄT)

  KRISHNA = f(KARSH) = der Alles-Anziehende
  RAMA = f(RAM) = der Freude-Gebende
  HARE = f(HAR) = der Wegnehmende

  Die FUNKTION ist die PERSON.
  Die PARAMETER sind die MANIFESTATIONEN.
  Das ERGEBNIS ist der NAME.

DIE HIERARCHIE (Was am Ende bleibt):
------------------------------------
  1. PERSON (sat-cit-ānanda) - EWIG, FUNDAMENTAL
  2. QUALITÄTEN (guṇa) - ASPEKTE der Person
  3. AKTIVITÄTEN (līlā) - AUSDRÜCKE der Person
  4. NAMEN (nāma) - BESCHREIBUNGEN von 2 und 3

  Nur die PERSON ist fundamental.
  Namen sind abgeleitet.

ABHINNA (Nicht-Verschiedenheit):
--------------------------------
  "nāma-nāminoḥ" - Name und Benannter sind nicht verschieden.

  Die Ableitung macht den Namen NICHT WENIGER als die Person.
  Die Ableitung zeigt WIE der Name sich manifestiert.

  Das ist ACINTYA - unbegreiflich:
  Abgeleitet UND nicht-verschieden gleichzeitig.

IN CODE:
--------
  PERSON → QUALITÄTEN → AKTIVITÄTEN → NAMEN
  (sat)     (cit)         (ānanda)      (nāma)

  PROTOCOL → CONSTANTS → FUNCTIONS → VARIABLES
  (Kernel)   (Seed)      (Research)   (Exports)

CHAITANYA = MĀDHURYA-RASA AVATARA:
----------------------------------
  Er kam um 3 Dinge zu erfahren (CC Adi 4.15-16):
  1. Die Größe von Radhas Liebe
  2. Seine EIGENE MĀDHURYA (Süße)
  3. Die Glückseligkeit die SIE erfährt

  MĀDHURYA ist das ZENTRALE Wort.
  Chaitanya ist die VERKÖRPERUNG von Mādhurya.
"""


# =============================================================================
# VERIFICATION
# =============================================================================

# Madhurya = OCTET
assert MADHURYA_LENGTH == 8, "MADHURYA = 8 letters"

# Total letters = PRASADAM
assert TOTAL_MADHURYA_LETTERS == 25, "Total = PRASADAM"

# Madhurya sum = 250 = HALVES × PANCHA³
assert MADHURYA_SUM == HALVES * PANCHA**3, "250 = 2 × 125"

# Hierarchy levels = QUARTERS
assert len(ALL_LEVELS) == 4, "4 levels"

# Purposes = TRINITY
assert len(ALL_PURPOSES) == 3, "3 purposes"

# Derivations = TRINITY (3 names in Mahamantra)
assert len(ALL_DERIVATIONS) == 3, "3 name derivations"

if __name__ == "__main__":
    print(KEY_INSIGHT)
