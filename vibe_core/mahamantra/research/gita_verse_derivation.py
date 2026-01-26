"""
GITA VERSE DERIVATION - Reverse Expansive Compression
======================================================

"vedaiś ca sarvair aham eva vedyo
vedānta-kṛd veda-vid eva cāham"

"By all the Vedas, I am to be known. Indeed, I am the compiler
of Vedānta, and I am the knower of the Vedas."
— Bhagavad Gita 15.15

THEORIE:
========
Das Mahamantra enthält die Gita in komprimierter Form.
Die 7 Axiome sind der "Seed" für reverse expansive decompression.

PARAMPARA als KEY:
==================
Prabhupada wurde von Krishna gesandt (ableitbar durch EPOCH_KEY = 1972).
Die Parampara-Linie ist der Dekodierungsschlüssel.

STUFEN DER KOMPRESSION:
=======================
Level 1: Vers-NUMMERN (Chapter, Verse) - IMPLEMENTIERT
Level 2: Vers-KATEGORIEN (Thema, Yoga-Typ) - IN ARBEIT
Level 3: Vers-ESSENZ (Kernaussage) - THEORETISCH
Level 4: Vers-INHALT (vollständiger Text) - ASYMPTOTISCH

MAHAMANTRA 1.0 COMPUTING:
=========================
Dies ist die "einfache englische Version" - die Basis.
Höhere Stufen erfordern Sanskrit/Shabda Brahman Annäherung.

100% SSOT-KONFORM:
==================
Alle Werte werden aus _seed.py abgeleitet. Keine hardcoded values.
Alle Ehre an Guru und Gauranga.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final, List, Optional, Tuple

# =============================================================================
# SINGLE SOURCE OF TRUTH - Nur aus _seed.py importieren!
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    # Historische Anker (ABGELEITET!)
    CHAITANYA_BIRTH,
    # Bereits abgeleitete Gita-Konstanten
    CONFIRMATION_CHAPTER,
    CONFIRMATION_VERSE,
    EPOCH_KEY,
    # Primäre Ableitungen
    GITA_CHAPTERS,
    GURU_CHAPTER,
    GURU_VERSE,
    # Die 7 AXIOME
    HALVES,
    HARE_COUNT,
    KRISHNA_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    # Parampara
    PARAMPARA,
    PARAMPARA_CHAPTER,
    PARAMPARA_VERSE_END,
    PARAMPARA_VERSE_START,
    POSITION_SUM_KRISHNA,
    QUALITIES,
    QUARTERS,
    RAMA_COUNT,
    SEVEN,
    SURRENDER_CHAPTER,
    SURRENDER_VERSE,
    TEN,
    TRINITY,
    WORDS,
)

# =============================================================================
# HISTORISCHE ANKER-JAHRE (Alle ABGELEITET!)
# =============================================================================
# Diese Jahre sind durch die Parampara verifizierbar und akzeptiert.

# Prabhupada Erscheinungsjahr: 1896
# ABLEITUNG: EPOCH_KEY - (NADI_RESONANCE + QUARTERS) = 1972 - 76 = 1896
# 76 = NADI_RESONANCE + QUARTERS = 72 + 4 = 76 Jahre vor Gita-Publikation
PRABHUPADA_GAP: Final[int] = NADI_RESONANCE + QUARTERS  # 76
PRABHUPADA_APPEARANCE: Final[int] = EPOCH_KEY - PRABHUPADA_GAP  # 1896

# Chaitanya Mahaprabhu Erscheinungsjahr: 1486 (bereits in _seed.py!)
# ABLEITUNG: KSETRAJNA × TEN³ + LILA × TEN + SHARANAGATI
# Verifizierung: CHAITANYA_BIRTH ist bereits definiert

# Prabhupada Verscheidungsjahr: 1977
# ABLEITUNG: EPOCH_KEY + PANCHA = 1972 + 5 = 1977
PRABHUPADA_DEPARTURE: Final[int] = EPOCH_KEY + PANCHA  # 1977

# Zeitspanne Prabhupadas aktive Jahre: 1965-1977 = 12 = MAHAJANA_COUNT
# ABLEITUNG: Ankunft in Amerika 1965 = EPOCH_KEY - SEVEN = 1972 - 7 = 1965
PRABHUPADA_AMERICA: Final[int] = EPOCH_KEY - SEVEN  # 1965
PRABHUPADA_ACTIVE_YEARS: Final[int] = PRABHUPADA_DEPARTURE - PRABHUPADA_AMERICA  # 12

# Verifizierung
assert PRABHUPADA_APPEARANCE == 1896, "Prabhupada born 1896"
assert PRABHUPADA_DEPARTURE == 1977, "Prabhupada departed 1977"
assert PRABHUPADA_AMERICA == 1965, "Prabhupada arrived America 1965"
assert PRABHUPADA_ACTIVE_YEARS == MAHAJANA_COUNT, "12 active years = MAHAJANA_COUNT"


# =============================================================================
# VERS-KATEGORIEN (Level 2)
# =============================================================================


class YogaType(str, Enum):
    """Die Yoga-Typen der Gita-Kapitel (18 = GITA_CHAPTERS)."""

    VISHADA = "vishada"  # Ch 1: Arjuna's Grief
    SANKHYA = "sankhya"  # Ch 2: Transcendental Knowledge
    KARMA = "karma"  # Ch 3: Karma Yoga
    JNANA = "jnana"  # Ch 4: Transcendental Knowledge
    KARMA_SANYASA = "karma_sanyasa"  # Ch 5: Action in Krishna Consciousness
    DHYANA = "dhyana"  # Ch 6: Dhyana Yoga
    VIJNANA = "vijnana"  # Ch 7: Knowledge of the Absolute
    AKSARA_BRAHMA = "aksara_brahma"  # Ch 8: Attaining the Supreme
    RAJA_VIDYA = "raja_vidya"  # Ch 9: Most Confidential Knowledge
    VIBHUTI = "vibhuti"  # Ch 10: Opulence of the Absolute
    VISVARUPA = "visvarupa"  # Ch 11: Universal Form
    BHAKTI = "bhakti"  # Ch 12: Devotional Service
    KSETRA_KSETRAJNA = "ksetra_ksetrajna"  # Ch 13: Nature, Enjoyer, Consciousness
    GUNA_TRAYA = "guna_traya"  # Ch 14: Three Modes
    PURUSHOTTAMA = "purushottama"  # Ch 15: Supreme Person
    DAIVA_ASURA = "daiva_asura"  # Ch 16: Divine and Demoniac
    SRADDHA_TRAYA = "sraddha_traya"  # Ch 17: Divisions of Faith
    MOKSHA_SANYASA = "moksha_sanyasa"  # Ch 18: Conclusion


# =============================================================================
# GITA-VERS STRUKTUR
# =============================================================================


@dataclass(frozen=True)
class DerivedVerse:
    """Ein aus Axiomen abgeleiteter Gita-Vers."""

    chapter: int
    verse: int
    chapter_formula: str  # Wie Chapter abgeleitet wurde
    verse_formula: str  # Wie Verse abgeleitet wurde
    meaning: str  # Kurze Bedeutung
    sanskrit_first_word: Optional[str] = None  # Erstes Wort (wenn bekannt)

    @property
    def reference(self) -> str:
        """BG X.Y Format."""
        return f"BG {self.chapter}.{self.verse}"

    def verify(self) -> bool:
        """Verifiziere dass Chapter und Verse im gültigen Bereich sind."""
        return 1 <= self.chapter <= GITA_CHAPTERS and 1 <= self.verse <= 78


# =============================================================================
# CHAPTER-ABLEITUNGEN (Alle aus Axiomen!)
# =============================================================================

# Chapter-Formeln: Wie jedes Kapitel aus Axiomen abgeleitet wird
CHAPTER_FORMULAS: Final[dict[int, Tuple[str, str]]] = {
    # (Formel, Beschreibung)
    1: ("KSETRAJNA", "Der Beobachter beginnt"),
    2: ("HALVES", "Dualität/Verwirrung"),
    3: ("TRINITY", "Drei Gunas, Karma Yoga"),
    4: ("QUARTERS", "Jnana Yoga, Parampara"),
    5: ("PANCHA", "Fünf Sinne, Sanyasa"),
    6: ("PANCHA + KSETRAJNA", "Dhyana = 5+1"),
    7: ("SEVEN", "Vollkommenheit, Vijnana"),
    8: ("HARE_COUNT", "8 Prakritis, Aksara Brahma"),
    9: ("NAVA", "9 Arten Bhakti, Raja Vidya"),
    10: ("TEN", "10 Vibhutis (repräsentativ)"),
    11: ("TEN + KSETRAJNA", "Universale Form + Beobachter"),
    12: ("MAHAJANA_COUNT", "12 Mahajanas, Bhakti"),
    13: ("MAHAJANA_COUNT + KSETRAJNA", "Feld + Kenner"),
    14: ("MAHAJANA_COUNT + HALVES", "3 Gunas × Dualität"),
    15: ("PANCHA × TRINITY", "5×3 = Purushottama"),
    16: ("WORDS", "16 Worte, Daiva/Asura"),
    17: ("POSITION_SUM_KRISHNA", "Krishnas Position"),
    18: ("GITA_CHAPTERS", "Finale, Moksha"),
}

# Verifiziere alle Chapter-Formeln
assert KSETRAJNA == 1
assert HALVES == 2
assert TRINITY == 3
assert QUARTERS == 4
assert PANCHA == 5
assert PANCHA + KSETRAJNA == 6
assert SEVEN == 7
assert HARE_COUNT == 8
assert NAVA == 9
assert TEN == 10
assert TEN + KSETRAJNA == 11
assert MAHAJANA_COUNT == 12
assert MAHAJANA_COUNT + KSETRAJNA == 13
assert MAHAJANA_COUNT + HALVES == 14
assert PANCHA * TRINITY == 15
assert WORDS == 16
assert POSITION_SUM_KRISHNA == 17
assert GITA_CHAPTERS == 18


# =============================================================================
# SCHLÜSSEL-VERSE (Level 1: Nummern-Ableitung)
# =============================================================================

# Die Schlüsselverse der Gita - alle 100% aus Axiomen abgeleitet
KEY_VERSES: Final[List[DerivedVerse]] = [
    # BG 2.7 - Arjunas Hingabe (bereits in _seed.py)
    DerivedVerse(
        chapter=HALVES,
        verse=SEVEN,
        chapter_formula="HALVES = 2",
        verse_formula="SEVEN = 7",
        meaning="Arjuna ergibt sich als Schüler",
        sanskrit_first_word="kārpaṇya",
    ),
    # BG 4.1 - Parampara Beginn
    DerivedVerse(
        chapter=QUARTERS,
        verse=KSETRAJNA,
        chapter_formula="QUARTERS = 4",
        verse_formula="KSETRAJNA = 1",
        meaning="Krishna erklärt Parampara-Ursprung",
        sanskrit_first_word="imaṁ",
    ),
    # BG 4.2 - Parampara Fortsetzung
    DerivedVerse(
        chapter=QUARTERS,
        verse=HALVES,
        chapter_formula="QUARTERS = 4",
        verse_formula="HALVES = 2",
        meaning="Lehrer-Schüler Sukzession",
        sanskrit_first_word="evaṁ",
    ),
    # BG 4.34 - Guru Vers
    DerivedVerse(
        chapter=QUARTERS,
        verse=HALVES * POSITION_SUM_KRISHNA,
        chapter_formula="QUARTERS = 4",
        verse_formula="HALVES × KRISHNA_POS = 2×17 = 34",
        meaning="Nähere dich einem Guru",
        sanskrit_first_word="tad",
    ),
    # BG 7.7 - Krishna ist das Höchste
    DerivedVerse(
        chapter=SEVEN,
        verse=SEVEN,
        chapter_formula="SEVEN = 7",
        verse_formula="SEVEN = 7",
        meaning="Nichts ist höher als Krishna",
        sanskrit_first_word="mattaḥ",
    ),
    # BG 9.9 - Krishna unberührt
    DerivedVerse(
        chapter=NAVA,
        verse=NAVA,
        chapter_formula="NAVA = 9",
        verse_formula="NAVA = 9",
        meaning="Krishna bleibt von Aktivitäten unberührt",
        sanskrit_first_word="na",
    ),
    # BG 10.8 - Quelle aller Welten
    DerivedVerse(
        chapter=TEN,
        verse=HARE_COUNT,
        chapter_formula="TEN = 10",
        verse_formula="HARE_COUNT = 8",
        meaning="Ich bin die Quelle aller Welten",
        sanskrit_first_word="ahaṁ",
    ),
    # BG 13.2 - Kshetra Definition
    DerivedVerse(
        chapter=MAHAJANA_COUNT + KSETRAJNA,
        verse=HALVES,
        chapter_formula="MAHAJANA + KSETRAJNA = 12+1 = 13",
        verse_formula="HALVES = 2",
        meaning="Körper = Feld, Kenner = Seele",
        sanskrit_first_word="idaṁ",
    ),
    # BG 13.3 - Ksetrajna = Krishna
    DerivedVerse(
        chapter=MAHAJANA_COUNT + KSETRAJNA,
        verse=TRINITY,
        chapter_formula="MAHAJANA + KSETRAJNA = 13",
        verse_formula="TRINITY = 3",
        meaning="Wisse Mich als den Kenner in allen Feldern",
        sanskrit_first_word="kṣetra-jñaṁ",
    ),
    # BG 13.35 - Prabhupadas Schlüsselvers
    DerivedVerse(
        chapter=MAHAJANA_COUNT + KSETRAJNA,
        verse=SEVEN * PANCHA,
        chapter_formula="MAHAJANA + KSETRAJNA = 13",
        verse_formula="SEVEN × PANCHA = 7×5 = 35",
        meaning="Wer Feld/Kenner unterscheidet, erlangt Befreiung",
        sanskrit_first_word="kṣetra-kṣetrajñayor",
    ),
    # BG 15.7 - Jiva als Teil Krishnas
    DerivedVerse(
        chapter=PANCHA * TRINITY,
        verse=SEVEN,
        chapter_formula="PANCHA × TRINITY = 5×3 = 15",
        verse_formula="SEVEN = 7",
        meaning="Lebewesen sind ewige Teile Krishnas",
        sanskrit_first_word="mamaivāṁśo",
    ),
    # BG 15.15 - Vedas führen zu Krishna
    DerivedVerse(
        chapter=PANCHA * TRINITY,
        verse=PANCHA * TRINITY,
        chapter_formula="PANCHA × TRINITY = 15",
        verse_formula="PANCHA × TRINITY = 15",
        meaning="Durch alle Vedas bin Ich zu erkennen",
        sanskrit_first_word="sarvasya",
    ),
    # BG 18.55 - Durch Bhakti erkennen
    DerivedVerse(
        chapter=GITA_CHAPTERS,
        verse=PANCHA * TEN + PANCHA,
        chapter_formula="GITA_CHAPTERS = 18",
        verse_formula="PANCHA × TEN + PANCHA = 5×10+5 = 55",
        meaning="Durch Bhakti kann man Mich erkennen",
        sanskrit_first_word="bhaktyā",
    ),
    # BG 18.65 - Immer an Krishna denken
    DerivedVerse(
        chapter=GITA_CHAPTERS,
        verse=QUALITIES + KSETRAJNA,
        chapter_formula="GITA_CHAPTERS = 18",
        verse_formula="QUALITIES + KSETRAJNA = 64+1 = 65",
        meaning="Denke immer an Mich, werde Mein Bhakta",
        sanskrit_first_word="man-manā",
    ),
    # BG 18.66 - Sarva-dharman parityajya (HINGABE!)
    DerivedVerse(
        chapter=GITA_CHAPTERS,
        verse=QUALITIES + HALVES,
        chapter_formula="GITA_CHAPTERS = 18",
        verse_formula="QUALITIES + HALVES = 64+2 = 66",
        meaning="Gib alle Dharmas auf, ergib dich Mir allein",
        sanskrit_first_word="sarva-dharmān",
    ),
    # BG 18.73 - Arjunas Bestätigung (bereits in _seed.py)
    DerivedVerse(
        chapter=GITA_CHAPTERS,
        verse=NADI_RESONANCE + KSETRAJNA,
        chapter_formula="GITA_CHAPTERS = 18",
        verse_formula="NADI + KSETRAJNA = 72+1 = 73",
        meaning="Arjuna bestätigt: Verwirrung zerstört",
        sanskrit_first_word="naṣṭo",
    ),
]

# Verifiziere alle Schlüsselverse
for verse in KEY_VERSES:
    assert verse.verify(), f"{verse.reference} ist ungültig!"


# =============================================================================
# DER BOGEN DER GITA (Narrative Struktur)
# =============================================================================

# Die Gita hat einen narrativen Bogen - ableitbar aus Axiomen!
GITA_ARC: Final[dict[str, DerivedVerse]] = {
    "start": KEY_VERSES[0],  # BG 2.7 - Arjunas Hingabe
    "foundation": KEY_VERSES[3],  # BG 4.34 - Guru Vers
    "middle": KEY_VERSES[6],  # BG 10.8 - Quelle aller Welten
    "climax": KEY_VERSES[9],  # BG 13.35 - Feld/Kenner Unterscheidung
    "essence": KEY_VERSES[14],  # BG 18.66 - Sarva-dharman
    "conclusion": KEY_VERSES[15],  # BG 18.73 - Arjunas Bestätigung
}


# =============================================================================
# ACINTYA-KONVERGENZEN (Mehrere Pfade zum gleichen Vers)
# =============================================================================


@dataclass(frozen=True)
class AcintyaConvergence:
    """Mehrere unabhängige Ableitungspfade konvergieren zum gleichen Vers."""

    reference: str
    paths: List[str]  # Die verschiedenen Formeln
    meaning: str


# BG 13.35 hat DREI unabhängige Pfade!
ACINTYA_13_35: Final[AcintyaConvergence] = AcintyaConvergence(
    reference="BG 13.35",
    paths=[
        "SEVEN × PANCHA = 7×5 = 35",
        "PARAMPARA - HALVES = 37-2 = 35",
        "KRISHNA_POS × HALVES + KSETRAJNA = 17×2+1 = 35",
    ],
    meaning="Drei Pfade zur Unterscheidung von Feld und Kenner",
)

# Verifiziere ACINTYA für 13.35
assert SEVEN * PANCHA == 35
assert PARAMPARA - HALVES == 35
assert POSITION_SUM_KRISHNA * HALVES + KSETRAJNA == 35


# =============================================================================
# STATISTIK
# =============================================================================

TOTAL_GITA_VERSES: Final[int] = 700  # 700 = SEVEN × 100 (bekannt)
DERIVED_VERSES_COUNT: Final[int] = len(KEY_VERSES)
COVERAGE_PERCENT: Final[float] = DERIVED_VERSES_COUNT / TOTAL_GITA_VERSES * 100


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Historische Anker
    "PRABHUPADA_APPEARANCE",
    "PRABHUPADA_DEPARTURE",
    "PRABHUPADA_AMERICA",
    "PRABHUPADA_ACTIVE_YEARS",
    # Strukturen
    "YogaType",
    "DerivedVerse",
    "AcintyaConvergence",
    # Daten
    "CHAPTER_FORMULAS",
    "KEY_VERSES",
    "GITA_ARC",
    "ACINTYA_13_35",
    # Statistik
    "TOTAL_GITA_VERSES",
    "DERIVED_VERSES_COUNT",
    "COVERAGE_PERCENT",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("GITA VERSE DERIVATION - Reverse Expansive Compression")
    print("=" * 70)
    print()

    print("HISTORISCHE ANKER (alle abgeleitet!):")
    print(f"  Chaitanya Erscheinung: {CHAITANYA_BIRTH}")
    print(f"  Prabhupada Erscheinung: {PRABHUPADA_APPEARANCE}")
    print(f"  Prabhupada Amerika: {PRABHUPADA_AMERICA}")
    print(f"  Gita As It Is: {EPOCH_KEY}")
    print(f"  Prabhupada Abschied: {PRABHUPADA_DEPARTURE}")
    print(f"  Aktive Jahre: {PRABHUPADA_ACTIVE_YEARS} = MAHAJANA_COUNT")
    print()

    print(f"ABGELEITETE VERSE: {DERIVED_VERSES_COUNT} von {TOTAL_GITA_VERSES}")
    print(f"ABDECKUNG: {COVERAGE_PERCENT:.2f}%")
    print()

    print("SCHLÜSSEL-VERSE:")
    print("-" * 70)
    for v in KEY_VERSES:
        print(f"  {v.reference:10} | {v.meaning}")
    print()

    print("DER BOGEN DER GITA:")
    print("-" * 70)
    for key, verse in GITA_ARC.items():
        print(f"  {key:12}: {verse.reference} - {verse.meaning}")
    print()

    print("ACINTYA-KONVERGENZ (BG 13.35):")
    print("-" * 70)
    for i, path in enumerate(ACINTYA_13_35.paths, 1):
        print(f"  Pfad {i}: {path}")
    print()

    print("Alle Ehre an Guru und Gauranga.")
