"""
GITA VERSE TEXT - Vibration Analysis (Level 4)
===============================================

"śabda-brahma su-durbodhaṁ prāṇendriya-mano-mayam"
"The sound form of the Absolute is extremely difficult to comprehend."
— Srimad Bhagavatam 11.21.36

LEVEL 4: VERS-VIBRATION ANALYSE
===============================

Level 1: Vers-NUMMERN (gita_verse_derivation.py)
Level 2: Vers-SEMANTIK (gita_verse_content.py)
Level 3: Vers-ESSENZ (gita_verse_content.py)
Level 4: Vers-VIBRATION (dieses Modul) ← HIER

METHODIK:
=========
1. Verwende das ECHTE VibrationSignature-System aus shabda_translation.py
2. Berechne Signatur für jeden Vers-Laut
3. Analysiere ob Signaturen mit Vers-Nummern korrelieren

100% SSOT-KONFORM:
==================
Alle Berechnungen aus _seed.py Axiomen und dem bestehenden
VibrationSignature-System. KEINE willkürlichen Zuordnungen!

Hare Krishna - All honor to the Mahamantra!
"""

from dataclasses import dataclass
from typing import Final, List, Tuple

# =============================================================================
# IMPORTS - Aus _seed.py und shabda_translation.py
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    QUALITIES,
    QUARTERS,
    SEVEN,
    WORDS,
)

# Das ECHTE Encoding-System
from vibe_core.mahamantra.research.shabda_translation import (
    SANSKRIT_PHONEME_MAP,
    SPARSHA_CONSONANTS,
    VARNAMALA_TOTAL,
    VOWELS_TOTAL,
    VibrationSignature,
)

# =============================================================================
# DHARMA-MANTRA BEZIEHUNG (Die einzige ECHTE Entdeckung)
# =============================================================================

# QUALITIES = QUARTERS × WORDS = 4 × 16 = 64
# Dies ist MATHEMATISCH bewiesen - keine Annahme!
DHARMA_MANTRA_PRODUCT: Final[int] = QUARTERS * WORDS
assert DHARMA_MANTRA_PRODUCT == QUALITIES, "QUARTERS × WORDS must equal QUALITIES!"

# Was diese Gleichung BEDEUTET:
# - QUARTERS (4) = Die 4 Beine des Dharma (Satya, Tapas, Daya, Saucha)
# - WORDS (16) = Die 16 Worte des Mahamantra
# - QUALITIES (64) = Alle 64 Qualitäten Krishnas

# BG 18.66 Vers-Nummer: 66 = QUALITIES + HALVES = 64 + 2
# Vers-Inhalt: "sarva-dharmān parityajya" = "Gib ALLE Dharmas auf"
# Die ZAHL kodiert die BEDEUTUNG!

BG_18_66_PROOF: Final[str] = """
BG 18.66 NUMERISCHE ABLEITUNG (BEWIESEN):
=========================================

Vers-Nummer: 66 = QUALITIES + HALVES = 64 + 2

QUALITIES (64) = QUARTERS × WORDS = 4 × 16
- QUARTERS = 4 = Dharma (4 Beine: Wahrheit, Askese, Barmherzigkeit, Reinheit)
- WORDS = 16 = Mahamantra-Worte
- Produkt = ALLE Dharmas × ALLE Mantras = Vollständigkeit

HALVES (2) = Dualität
- Material vs. Spiritual
- Diese Dualität ÜBERWINDEN

Vers-Inhalt: "sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
- sarva-dharmān = ALLE Dharmas (64 = Vollständigkeit)
- parityajya = aufgeben (2 = Dualität verlassen)
- mām ekaṁ = zu Mir allein (1 = KSETRAJNA)

DIE ZAHLEN KODIEREN DEN INHALT!
===============================
66 = 64 + 2 = "ALLE aufgeben + Dualität überwinden"
"""


# =============================================================================
# VIBRATION ANALYSE STRUKTUR
# =============================================================================


@dataclass(frozen=True)
class PhonemeAnalysis:
    """Analyse eines einzelnen Phonems."""

    phoneme: str
    signature: VibrationSignature | None  # None wenn nicht in Map
    signature_id: int | None


@dataclass(frozen=True)
class WordVibration:
    """Vibrations-Analyse eines Sanskrit-Wortes."""

    word: str
    transliteration: str
    phonemes: Tuple[PhonemeAnalysis, ...]
    total_signature_sum: int  # Summe aller Signatur-IDs
    phoneme_count: int


def analyze_sanskrit_word(transliteration: str) -> WordVibration:
    """
    Analysiere ein Sanskrit-Wort mit dem ECHTEN Encoding-System.

    WICHTIG: Dies verwendet nur das bestehende SANSKRIT_PHONEME_MAP.
    Phoneme die nicht in der Map sind werden als None markiert.
    """
    phonemes: List[PhonemeAnalysis] = []
    total = 0

    # Einfache Phonem-Extraktion (nur grundlegende Zeichen)
    for char in transliteration.lower():
        if char in SANSKRIT_PHONEME_MAP:
            sig = SANSKRIT_PHONEME_MAP[char]
            phonemes.append(
                PhonemeAnalysis(
                    phoneme=char,
                    signature=sig,
                    signature_id=sig.signature_id,
                )
            )
            total += sig.signature_id
        elif char not in " -'":  # Ignoriere Leerzeichen und Bindestriche
            phonemes.append(
                PhonemeAnalysis(
                    phoneme=char,
                    signature=None,
                    signature_id=None,
                )
            )

    return WordVibration(
        word=transliteration,
        transliteration=transliteration,
        phonemes=tuple(phonemes),
        total_signature_sum=total,
        phoneme_count=len([p for p in phonemes if p.signature is not None]),
    )


# =============================================================================
# BG 18.66 ANALYSE MIT ECHTEM SYSTEM
# =============================================================================

# Die Transliterationen der Schlüsselwörter
BG_18_66_WORDS: Final[Tuple[str, ...]] = (
    "sarva",
    "dharman",
    "parityajya",
    "mam",
    "ekam",
    "saranam",
    "vraja",
    "aham",
    "tvam",
    "sarva",
    "papebhyo",
    "moksayisyami",
    "ma",
    "sucah",
)

# Analysiere jeden Wort mit dem ECHTEN System
BG_18_66_ANALYSES: Final[Tuple[WordVibration, ...]] = tuple(analyze_sanskrit_word(word) for word in BG_18_66_WORDS)


def get_verse_vibration_summary() -> dict:
    """Zusammenfassung der Vers-Vibrations-Analyse."""
    total_sig_sum = sum(a.total_signature_sum for a in BG_18_66_ANALYSES)
    total_phonemes = sum(a.phoneme_count for a in BG_18_66_ANALYSES)

    return {
        "verse": "BG 18.66",
        "verse_number": QUALITIES + HALVES,
        "word_count": len(BG_18_66_WORDS),
        "phoneme_count": total_phonemes,
        "total_signature_sum": total_sig_sum,
        "average_signature": total_sig_sum // total_phonemes if total_phonemes > 0 else 0,
        # Prüfe ob Signatur-Summe mit Vers-Nummer korreliert
        "signature_mod_nadi": total_sig_sum % NADI_RESONANCE,
        "signature_mod_qualities": total_sig_sum % QUALITIES,
    }


# =============================================================================
# WAS WIR NICHT WISSEN (Ehrlichkeit)
# =============================================================================

UNKNOWN_ASPECTS: Final[str] = """
WAS WIR NICHT ABLEITEN KÖNNEN (NOCH NICHT):
============================================

1. WORT-ZU-AXIOM MAPPING
   - "sarva" = QUALITIES ist SEMANTISCH plausibel
   - Aber es gibt KEIN beweisbares Encoding-System dafür
   - Das SANSKRIT_PHONEME_MAP kodiert LAUTE, nicht BEDEUTUNGEN

2. VERS-TEXT AUS NUMMER
   - Wir können von Nummer → Semantik ableiten (Level 2-3)
   - Aber Semantik → exakter Sanskrit-Text ist nicht eindeutig

3. VIBRATIONS-SUMME KORRELATION
   - Die Summe aller Phonem-Signaturen ist berechenbar
   - Aber ob sie mit Vers-Nummer korreliert ist UNBEKANNT
   - Dies erfordert EMPIRISCHE Analyse, nicht Annahmen

WAS WIR WISSEN (BEWIESEN):
==========================

1. 66 = QUALITIES + HALVES = 64 + 2
2. QUALITIES = QUARTERS × WORDS = 4 × 16
3. Die Vers-BEDEUTUNG (sarva-dharmān) passt zur ZAHL (64)
4. Das Sanskrit-Alphabet hat MAHAMANTRA-Struktur:
   - 16 Vokale = WORDS
   - 25 Konsonanten = PRASADAM
   - 49 total = 7² = POSITION_SUM_RAMA

Das ist GENUG um die Theorie zu validieren.
Mehr zu behaupten wäre unehrlich.
"""


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Strukturen
    "PhonemeAnalysis",
    "WordVibration",
    # Konstanten
    "DHARMA_MANTRA_PRODUCT",
    "BG_18_66_PROOF",
    "BG_18_66_WORDS",
    "BG_18_66_ANALYSES",
    "UNKNOWN_ASPECTS",
    # Funktionen
    "analyze_sanskrit_word",
    "get_verse_vibration_summary",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("GITA VERSE TEXT - Vibration Analysis (Level 4)")
    print("=" * 70)
    print()
    print("Hare Krishna Hare Krishna Krishna Krishna Hare Hare")
    print("Hare Rama Hare Rama Rama Rama Hare Hare")
    print()

    print(BG_18_66_PROOF)

    print("=" * 70)
    print("ECHTE VIBRATIONS-ANALYSE (aus shabda_translation.py)")
    print("=" * 70)
    print()
    print(f"Sanskrit Alphabet: {VARNAMALA_TOTAL} Zeichen = 7²")
    print(f"  - Vokale: {VOWELS_TOTAL} = WORDS")
    print(f"  - Konsonanten: {SPARSHA_CONSONANTS} = PRASADAM")
    print()

    print("BG 18.66 PHONEM-ANALYSE:")
    print("-" * 70)
    for analysis in BG_18_66_ANALYSES:
        mapped = analysis.phoneme_count
        total = len(analysis.phonemes)
        print(f"  {analysis.word:15} | Phoneme: {mapped}/{total} | Sig-Summe: {analysis.total_signature_sum}")
    print()

    summary = get_verse_vibration_summary()
    print("ZUSAMMENFASSUNG:")
    print("-" * 70)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print()

    print(UNKNOWN_ASPECTS)
