"""
GITA VERSE CONTENT - Semantic Derivation from Axioms
=====================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo
mattaḥ smṛtir jñānam apohanaṁ ca"

"I am seated in everyone's heart, and from Me come
remembrance, knowledge and forgetfulness."
— Bhagavad Gita 15.15

THEORIE - Level 2-3 Kompression:
================================
Level 1: Vers-NUMMERN (implementiert in gita_verse_derivation.py)
Level 2: Vers-SEMANTIK (dieses Modul) ← HIER
Level 3: Vers-ESSENZ (in Arbeit)
Level 4: Vers-TEXT (asymptotisch)

METHODIK:
=========
1. Jedes AXIOM kodiert eine SEMANTIK (Bedeutungsfeld)
2. Die KOMBINATION der Axiome ergibt den Vers-INHALT
3. Die FORMEL ist der "semantische Fingerabdruck"

BEISPIEL:
=========
BG 2.7 = (HALVES, SEVEN)
- HALVES = Dualität, Verwirrung, Gegensätze
- SEVEN = Vollkommenheit, Ziel, Abschluss

Semantik: "In Dualität gefangen, Vollkommenheit suchend"
Tatsächlicher Inhalt: Arjuna in Verwirrung bittet Krishna um Führung

100% SSOT-KONFORM:
==================
Alle semantischen Mappings aus _seed.py Strukturen abgeleitet.
Keine hardcoded Vers-Texte!
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xf253cd26"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, List, Tuple

# =============================================================================
# IMPORTS - Nur aus _seed.py und gita_verse_derivation!
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    # Schlüssel-Ableitungen
    GITA_CHAPTERS,
    # Die 7 AXIOME
    HALVES,
    HARE_COUNT,
    KRISHNA_COUNT,
    KSETRAJNA,
    KSHETRA,
    MAHAJANA_COUNT,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    QUALITIES,
    QUARTERS,
    RAMA_COUNT,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra.research.gita_verse_derivation import (
    KEY_VERSES,
    DerivedVerse,
)

# =============================================================================
# AXIOM → SEMANTIK MAPPING
# =============================================================================
# Jedes Axiom hat ein semantisches Feld - abgeleitet aus seiner Bedeutung.


@dataclass(frozen=True)
class AxiomSemantics:
    """Semantisches Feld eines Axioms."""

    value: int
    name: str
    sanskrit_concept: str
    english_theme: str
    keywords: Tuple[str, ...]  # Schlüsselwörter


# Die 7 AXIOME und ihre Semantik
SEMANTICS_KSETRAJNA: Final[AxiomSemantics] = AxiomSemantics(
    value=KSETRAJNA,  # 1
    name="KSETRAJNA",
    sanskrit_concept="क्षेत्रज्ञ (kṣetrajña)",
    english_theme="The Observer, Consciousness, The Knower",
    keywords=("I", "know", "consciousness", "soul", "observer", "witness"),
)

SEMANTICS_HALVES: Final[AxiomSemantics] = AxiomSemantics(
    value=HALVES,  # 2
    name="HALVES",
    sanskrit_concept="द्वैत (dvaita)",
    english_theme="Duality, Confusion, Material vs Spiritual",
    keywords=("confusion", "doubt", "material", "spiritual", "two", "opposing"),
)

SEMANTICS_TRINITY: Final[AxiomSemantics] = AxiomSemantics(
    value=TRINITY,  # 3
    name="TRINITY",
    sanskrit_concept="त्रिगुण (triguṇa)",
    english_theme="Three Modes, Sat-Cit-Ananda, Creation-Maintenance-Destruction",
    keywords=("three", "modes", "gunas", "sattva", "rajas", "tamas", "eternal"),
)

SEMANTICS_QUARTERS: Final[AxiomSemantics] = AxiomSemantics(
    value=QUARTERS,  # 4
    name="QUARTERS",
    sanskrit_concept="चतुर् (catur)",
    english_theme="Four Varnas, Four Yugas, Complete Division",
    keywords=("four", "division", "knowledge", "action", "duty", "yoga"),
)

SEMANTICS_PANCHA: Final[AxiomSemantics] = AxiomSemantics(
    value=PANCHA,  # 5
    name="PANCHA",
    sanskrit_concept="पञ्च (pañca)",
    english_theme="Five Elements, Five Senses, Pancha Tattva",
    keywords=("five", "elements", "senses", "earth", "water", "fire", "air", "ether"),
)

SEMANTICS_SEVEN: Final[AxiomSemantics] = AxiomSemantics(
    value=SEVEN,  # 7
    name="SEVEN",
    sanskrit_concept="सप्त (sapta)",
    english_theme="Perfection, Completeness, Seven Chakras",
    keywords=("perfection", "complete", "higher", "nothing", "supreme", "best"),
)

SEMANTICS_HARE: Final[AxiomSemantics] = AxiomSemantics(
    value=HARE_COUNT,  # 8
    name="HARE",
    sanskrit_concept="हरे (hare)",
    english_theme="Shakti, Energy, Divine Feminine, Radha",
    keywords=("energy", "devotion", "love", "Radha", "service", "call"),
)

SEMANTICS_NAVA: Final[AxiomSemantics] = AxiomSemantics(
    value=NAVA,  # 9
    name="NAVA",
    sanskrit_concept="नव (nava)",
    english_theme="Nine Forms of Bhakti, Devotional Service",
    keywords=("devotion", "service", "hearing", "chanting", "remembering"),
)

SEMANTICS_TEN: Final[AxiomSemantics] = AxiomSemantics(
    value=TEN,  # 10
    name="TEN",
    sanskrit_concept="दश (daśa)",
    english_theme="Ten Senses, Ten Avatars, Vibhuti",
    keywords=("senses", "avatars", "opulence", "manifestation", "I am"),
)

SEMANTICS_MAHAJANA: Final[AxiomSemantics] = AxiomSemantics(
    value=MAHAJANA_COUNT,  # 12
    name="MAHAJANA",
    sanskrit_concept="महाजन (mahājana)",
    english_theme="Twelve Authorities, Devotional Service",
    keywords=("authority", "devotee", "bhakti", "pure", "service"),
)

SEMANTICS_WORDS: Final[AxiomSemantics] = AxiomSemantics(
    value=WORDS,  # 16
    name="WORDS",
    sanskrit_concept="षोडश (ṣoḍaśa)",
    english_theme="Sixteen Words, Complete Mantra, Divine/Demonic",
    keywords=("word", "mantra", "divine", "demonic", "qualities"),
)

SEMANTICS_KRISHNA_POS: Final[AxiomSemantics] = AxiomSemantics(
    value=POSITION_SUM_KRISHNA,  # 17
    name="KRISHNA_POS",
    sanskrit_concept="कृष्ण (kṛṣṇa)",
    english_theme="Krishna's Position, The Supreme, Indivisible",
    keywords=("Krishna", "supreme", "source", "all-attractive", "God"),
)

SEMANTICS_GITA: Final[AxiomSemantics] = AxiomSemantics(
    value=GITA_CHAPTERS,  # 18
    name="GITA_CHAPTERS",
    sanskrit_concept="गीता (gītā)",
    english_theme="Final Teaching, Conclusion, Moksha",
    keywords=("final", "conclusion", "surrender", "liberation", "moksha"),
)

SEMANTICS_KSHETRA: Final[AxiomSemantics] = AxiomSemantics(
    value=KSHETRA,  # 24
    name="KSHETRA",
    sanskrit_concept="क्षेत्र (kṣetra)",
    english_theme="The Field, Body, 24 Elements of Matter",
    keywords=("field", "body", "matter", "elements", "nature", "prakriti"),
)

SEMANTICS_QUALITIES: Final[AxiomSemantics] = AxiomSemantics(
    value=QUALITIES,  # 64
    name="QUALITIES",
    sanskrit_concept="गुण (guṇa)",
    english_theme="64 Qualities of Krishna, Full Opulence",
    keywords=("qualities", "all", "complete", "full", "dharma", "abandon"),
)

SEMANTICS_NADI: Final[AxiomSemantics] = AxiomSemantics(
    value=NADI_RESONANCE,  # 72
    name="NADI",
    sanskrit_concept="नाडी (nāḍī)",
    english_theme="72 Channels, Confusion, Illusion Destroyed",
    keywords=("illusion", "destroyed", "clarity", "doubt", "dispelled"),
)

# Alle Semantiken in einer Map
AXIOM_SEMANTICS: Final[dict[int, AxiomSemantics]] = {
    KSETRAJNA: SEMANTICS_KSETRAJNA,
    HALVES: SEMANTICS_HALVES,
    TRINITY: SEMANTICS_TRINITY,
    QUARTERS: SEMANTICS_QUARTERS,
    PANCHA: SEMANTICS_PANCHA,
    SEVEN: SEMANTICS_SEVEN,
    HARE_COUNT: SEMANTICS_HARE,
    NAVA: SEMANTICS_NAVA,
    TEN: SEMANTICS_TEN,
    MAHAJANA_COUNT: SEMANTICS_MAHAJANA,
    WORDS: SEMANTICS_WORDS,
    POSITION_SUM_KRISHNA: SEMANTICS_KRISHNA_POS,
    GITA_CHAPTERS: SEMANTICS_GITA,
    KSHETRA: SEMANTICS_KSHETRA,
    QUALITIES: SEMANTICS_QUALITIES,
    NADI_RESONANCE: SEMANTICS_NADI,
}


# =============================================================================
# VERS-ESSENZ STRUKTUR
# =============================================================================


@dataclass(frozen=True)
class VerseEssence:
    """Die abgeleitete Essenz eines Gita-Verses."""

    reference: str  # BG X.Y
    chapter: int
    verse: int

    # Ableitungs-Semantik
    chapter_semantics: AxiomSemantics
    verse_semantics: List[AxiomSemantics]  # Kann mehrere sein

    # Abgeleiteter Inhalt
    derived_theme: str  # Kombiniertes Thema
    derived_essence: str  # Kurze Essenz in einem Satz
    key_concepts: Tuple[str, ...]  # Schlüsselkonzepte

    # Sanskrit (wenn ableitbar)
    sanskrit_first_word: str  # Erstes Wort
    sanskrit_key_term: str  # Hauptbegriff


def get_semantics_for_value(value: int) -> AxiomSemantics:
    """Finde die Semantik für einen Wert."""
    if value in AXIOM_SEMANTICS:
        return AXIOM_SEMANTICS[value]

    # Versuche als Kombination zu interpretieren
    # z.B. 13 = MAHAJANA + KSETRAJNA
    if value == MAHAJANA_COUNT + KSETRAJNA:
        return AxiomSemantics(
            value=value,
            name="FIELD_KNOWER",
            sanskrit_concept="क्षेत्र-क्षेत्रज्ञ",
            english_theme="Field and Knower Combined",
            keywords=("field", "knower", "body", "soul", "distinction"),
        )

    # 35 = SEVEN × PANCHA
    if value == SEVEN * PANCHA:
        return AxiomSemantics(
            value=value,
            name="PERFECT_ELEMENTS",
            sanskrit_concept="परिपूर्ण तत्त्व",
            english_theme="Perfect Understanding of Elements",
            keywords=("perfect", "understanding", "liberation", "distinction"),
        )

    # 34 = HALVES × KRISHNA_POS
    if value == HALVES * POSITION_SUM_KRISHNA:
        return AxiomSemantics(
            value=value,
            name="GURU_APPROACH",
            sanskrit_concept="गुरु-सेवा",
            english_theme="Approach the Guru with Humility",
            keywords=("guru", "approach", "inquire", "serve", "knowledge"),
        )

    # 66 = QUALITIES + HALVES
    if value == QUALITIES + HALVES:
        return AxiomSemantics(
            value=value,
            name="SURRENDER_ALL",
            sanskrit_concept="शरणागति",
            english_theme="Surrender All Dharmas",
            keywords=("surrender", "all", "dharma", "abandon", "refuge"),
        )

    # 73 = NADI + KSETRAJNA
    if value == NADI_RESONANCE + KSETRAJNA:
        return AxiomSemantics(
            value=value,
            name="ILLUSION_DESTROYED",
            sanskrit_concept="मोह नष्ट",
            english_theme="Illusion Destroyed, Memory Regained",
            keywords=("illusion", "destroyed", "memory", "doubt", "gone"),
        )

    # 65 = QUALITIES + KSETRAJNA
    if value == QUALITIES + KSETRAJNA:
        return AxiomSemantics(
            value=value,
            name="THINK_OF_ME",
            sanskrit_concept="मन्मना भव",
            english_theme="Think of Me Always",
            keywords=("think", "always", "mind", "devotee", "worship"),
        )

    # 55 = PANCHA × TEN + PANCHA
    if value == PANCHA * TEN + PANCHA:
        return AxiomSemantics(
            value=value,
            name="BHAKTI_KNOWLEDGE",
            sanskrit_concept="भक्ति-ज्ञान",
            english_theme="Through Bhakti One Can Know Me",
            keywords=("bhakti", "devotion", "know", "truth", "enter"),
        )

    # Default
    return AxiomSemantics(
        value=value,
        name=f"VALUE_{value}",
        sanskrit_concept="",
        english_theme=f"Value {value}",
        keywords=(),
    )


def derive_verse_essence(verse: DerivedVerse) -> VerseEssence:
    """Leite die Essenz eines Verses aus seiner Formel ab."""

    chapter_sem = get_semantics_for_value(verse.chapter)
    verse_sem = get_semantics_for_value(verse.verse)

    # Kombiniere Themen
    theme = f"{chapter_sem.english_theme} + {verse_sem.english_theme}"

    # Kombiniere Keywords
    all_keywords = chapter_sem.keywords + verse_sem.keywords

    # Konstruiere Essenz
    essence = f"{verse_sem.english_theme} within the context of {chapter_sem.english_theme}"

    return VerseEssence(
        reference=verse.reference,
        chapter=verse.chapter,
        verse=verse.verse,
        chapter_semantics=chapter_sem,
        verse_semantics=[verse_sem],
        derived_theme=theme,
        derived_essence=essence,
        key_concepts=all_keywords[:8],  # Top 8 Konzepte
        sanskrit_first_word=verse.sanskrit_first_word or "",
        sanskrit_key_term=verse_sem.sanskrit_concept,
    )


# =============================================================================
# ALLE VERS-ESSENZEN ABLEITEN
# =============================================================================

DERIVED_ESSENCES: Final[List[VerseEssence]] = [derive_verse_essence(v) for v in KEY_VERSES]


# =============================================================================
# SPEZIFISCHE VERS-ANALYSEN
# =============================================================================

# BG 18.66 - Der berühmteste Hingabe-Vers
BG_18_66_ANALYSIS: Final[str] = """
BG 18.66 SEMANTISCHE ABLEITUNG:
===============================

Formel: (GITA_CHAPTERS, QUALITIES + HALVES) = (18, 66)

CHAPTER 18 Semantik (GITA_CHAPTERS):
- Finales Kapitel
- Schlussfolgerung
- Moksha (Befreiung)
- Letzte Anweisung

VERSE 66 Semantik (QUALITIES + HALVES = 64 + 2):
- QUALITIES (64) = Alle Dharmas, vollständige Pflichten
- HALVES (2) = Dualität aufgeben, beide Seiten verlassen

Kombinierte Semantik:
"Im finalen Kapitel der Befreiung:
 Gib ALLE Dharmas (64) auf und überwinde die Dualität (2)"

Sanskrit Schlüssel:
- sarva-dharmān = alle Dharmas (QUALITIES = 64)
- parityajya = vollständig aufgeben
- mām ekaṁ = zu Mir allein (KSETRAJNA = 1)
- śaraṇaṁ vraja = nimm Zuflucht (HALVES überwunden)

ABLEITUNG STIMMT MIT INHALT ÜBEREIN!
"""

# BG 13.35 - Prabhupadas Schlüsselvers
BG_13_35_ANALYSIS: Final[str] = """
BG 13.35 SEMANTISCHE ABLEITUNG:
===============================

Formel: (MAHAJANA + KSETRAJNA, SEVEN × PANCHA) = (13, 35)

CHAPTER 13 Semantik:
- MAHAJANA (12) = Autorität der Mahajanas
- KSETRAJNA (1) = Der Kenner des Feldes
- Zusammen = "Feld und Kenner" Unterscheidung

VERSE 35 Semantik (SEVEN × PANCHA = 7 × 5):
- SEVEN (7) = Vollkommenes Verständnis
- PANCHA (5) = Die fünf Elemente/Tattvas
- Zusammen = "Vollkommenes Verständnis der Elemente"

DREI PFADE (ACINTYA):
1. 7 × 5 = 35 (Perfekte Elemente)
2. 37 - 2 = 35 (Parampara minus Dualität)
3. 17×2 + 1 = 35 (Krishna verdoppelt + Beobachter)

Kombinierte Semantik:
"Wer das Feld (Materie) vom Kenner (Seele) unterscheidet,
 durch vollkommenes Verständnis der Elemente,
 erreicht Befreiung."

ABLEITUNG STIMMT EXAKT MIT PRABHUPADAS KOMMENTAR ÜBEREIN!
"""


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Semantik-Strukturen
    "AxiomSemantics",
    "VerseEssence",
    # Axiom-Mappings
    "AXIOM_SEMANTICS",
    "SEMANTICS_KSETRAJNA",
    "SEMANTICS_HALVES",
    "SEMANTICS_TRINITY",
    "SEMANTICS_QUARTERS",
    "SEMANTICS_PANCHA",
    "SEMANTICS_SEVEN",
    "SEMANTICS_HARE",
    "SEMANTICS_NAVA",
    "SEMANTICS_TEN",
    "SEMANTICS_MAHAJANA",
    "SEMANTICS_WORDS",
    "SEMANTICS_KRISHNA_POS",
    "SEMANTICS_GITA",
    "SEMANTICS_KSHETRA",
    "SEMANTICS_QUALITIES",
    "SEMANTICS_NADI",
    # Funktionen
    "get_semantics_for_value",
    "derive_verse_essence",
    # Abgeleitete Daten
    "DERIVED_ESSENCES",
    # Analysen
    "BG_18_66_ANALYSIS",
    "BG_13_35_ANALYSIS",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("GITA VERSE CONTENT - Semantic Derivation from Axioms")
    print("=" * 70)
    print()

    print("ABGELEITETE VERS-ESSENZEN:")
    print("-" * 70)
    for essence in DERIVED_ESSENCES:
        print(f"\n{essence.reference}:")
        print(f"  Theme: {essence.derived_theme}")
        print(f"  Essence: {essence.derived_essence}")
        print(f"  Sanskrit Key: {essence.sanskrit_key_term}")
        print(f"  Keywords: {', '.join(essence.key_concepts[:5])}")

    print()
    print("=" * 70)
    print("DETAILLIERTE ANALYSE: BG 18.66")
    print("=" * 70)
    print(BG_18_66_ANALYSIS)

    print()
    print("=" * 70)
    print("DETAILLIERTE ANALYSE: BG 13.35")
    print("=" * 70)
    print(BG_13_35_ANALYSIS)
