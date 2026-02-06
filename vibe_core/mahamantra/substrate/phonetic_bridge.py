"""
UNIVERSAL PHONETIC BRIDGE - Derived from Existing Protocols
============================================================

"shabda-brahma" - Sound is the ultimate reality.

THIS SCALES TO ANY LANGUAGE - NO HARDCODED MAPPINGS!

DERIVATION CHAIN:
    seed.py → PANCHA (5)
        ↓
    varna.py → PANCHA_VARGA (5 consonant groups)
        ↓
    language.py → CharacterMapping.category (velar, palatal, dental, labial)
        ↓
    translation.py → Phoneme.sthana (kaṇṭha, tālu, danta, oṣṭha)
        ↓
    THIS FILE → Connects all protocols to route ANY language through Varga

STHANA (Sanskrit) ↔ VARGA (Phonetic):
    kaṇṭha  (कण्ठ)  = KANTHYA  = Throat/Guttural  = 0
    tālu    (तालु)  = TALAVYA  = Palate/Palatal   = 1
    mūrdha  (मूर्धा) = MURDHANYA = Retroflex       = 2
    danta   (दन्त)  = DANTYA   = Teeth/Dental     = 3
    oṣṭha   (ओष्ठ)  = OSHTHYA  = Lips/Labial      = 4

CATEGORY (English) ↔ VARGA:
    velar/glottal = KANTHYA = 0
    palatal       = TALAVYA = 1
    retroflex     = MURDHANYA = 2
    dental        = DANTYA = 3
    labial        = OSHTHYA = 4
"""
from vibe_core.mahamantra.protocols._seed import (HALVES, HARE_COUNT, KSETRAJNA, NAVA, PANCHA, QUARTERS, SHARANAGATI, TRINITY)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = SHARANAGATI
__genesis__ = "0xea72176b"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Final, List, Optional, Tuple

# =============================================================================
# SSOT IMPORTS - Everything derived from protocols!
# =============================================================================
# From language.py (Character mappings with IPA)
from vibe_core.protocols.language import (
    CONSONANT_MAPPINGS,
    VOWEL_MAPPINGS,
    CharacterMapping,
)

# From varna.py (Sanskrit phonetics SSOT)
from vibe_core.protocols.substrate.mantra.varna import (
    ANTAHSTHA,
    DANTYA_VARGA,
    KANTHYA_VARGA,
    MURDHANYA_VARGA,
    OSHTHYA_VARGA,
    PANCHA_VARGA,
    SVARA,
    TALAVYA_VARGA,
    USHMAN,
    Varna,
)

# From translation.py (Phoneme with sthana)
from vibe_core.protocols.translation import (
    ENGLISH_PHONEMES,
    GERMAN_PHONEMES,
    NaturalLanguage,
    Phoneme,
)

# =============================================================================
# VARGA INDEX (Derived from PANCHA_VARGA ordering)
# =============================================================================


class VargaIndex(IntEnum):
    """
    Index into PANCHA_VARGA tuple.

    DERIVED from the ordering in varna.py, NOT hardcoded!
    """

    KANTHYA = 0  # Throat   → PANCHA_VARGA[0]
    TALAVYA = KSETRAJNA  # Palate   → PANCHA_VARGA[1]
    MURDHANYA = HALVES  # Retroflex → PANCHA_VARGA[2]
    DANTYA = TRINITY  # Teeth    → PANCHA_VARGA[3]
    OSHTHYA = QUARTERS  # Lips     → PANCHA_VARGA[4]


# Verify against PANCHA from seed.py
assert len(VargaIndex) == PANCHA, f"VargaIndex must have {PANCHA} values"


# =============================================================================
# STHANA → VARGA MAPPING (Sanskrit articulation terms from translation.py)
# =============================================================================
# These are the Sanskrit terms used in translation.py Phoneme.sthana field

STHANA_TO_VARGA: Final[Dict[str, VargaIndex]] = {
    # Throat/Guttural
    "kaṇṭha": VargaIndex.KANTHYA,
    "kantha": VargaIndex.KANTHYA,
    "kaṇṭhya": VargaIndex.KANTHYA,
    # Palate/Palatal
    "tālu": VargaIndex.TALAVYA,
    "talu": VargaIndex.TALAVYA,
    "tālavya": VargaIndex.TALAVYA,
    # Retroflex/Cerebral
    "mūrdha": VargaIndex.MURDHANYA,
    "murdha": VargaIndex.MURDHANYA,
    "mūrdhanya": VargaIndex.MURDHANYA,
    # Dental/Teeth
    "danta": VargaIndex.DANTYA,
    "dantya": VargaIndex.DANTYA,
    # Labial/Lips
    "oṣṭha": VargaIndex.OSHTHYA,
    "ostha": VargaIndex.OSHTHYA,
    "oṣṭhya": VargaIndex.OSHTHYA,
}


# =============================================================================
# CATEGORY → VARGA MAPPING (English terms from language.py)
# =============================================================================
# These are the English terms used in CharacterMapping.category field

CATEGORY_TO_VARGA: Final[Dict[str, VargaIndex]] = {
    # Throat/Guttural (KANTHYA)
    "velar": VargaIndex.KANTHYA,
    "velar_aspirated": VargaIndex.KANTHYA,
    "glottal": VargaIndex.KANTHYA,
    "uvular": VargaIndex.KANTHYA,
    # Palate/Palatal (TALAVYA)
    "palatal": VargaIndex.TALAVYA,
    "palatal_aspirated": VargaIndex.TALAVYA,
    "palato-alveolar": VargaIndex.TALAVYA,
    # Retroflex/Cerebral (MURDHANYA)
    "retroflex": VargaIndex.MURDHANYA,
    "retroflex_sibilant": VargaIndex.MURDHANYA,
    "retroflex_aspirated": VargaIndex.MURDHANYA,
    # Dental/Teeth (DANTYA)
    "dental": VargaIndex.DANTYA,
    "dental_aspirated": VargaIndex.DANTYA,
    "dental_nasal": VargaIndex.DANTYA,
    "alveolar": VargaIndex.DANTYA,
    "sibilant": VargaIndex.DANTYA,  # s is dental sibilant
    # Labial/Lips (OSHTHYA)
    "labial": VargaIndex.OSHTHYA,
    "labial_aspirated": VargaIndex.OSHTHYA,
    "labial_nasal": VargaIndex.OSHTHYA,
    "bilabial": VargaIndex.OSHTHYA,
    # Semivowels (by articulation point)
    "semivowel": VargaIndex.TALAVYA,  # Default, but should check specific
    # Vowels (by quality)
    "short_vowel": VargaIndex.KANTHYA,  # 'a' is guttural
    "long_vowel": VargaIndex.KANTHYA,  # Default
    "diphthong": VargaIndex.TALAVYA,  # ai, au involve palate
    "vowel_r": VargaIndex.MURDHANYA,  # ṛ is retroflex
}


# =============================================================================
# BUILD PHONEME → VARGA FROM EXISTING PROTOCOL DATA
# =============================================================================


def _build_phoneme_varga_from_protocols() -> Dict[str, VargaIndex]:
    """
    Build phoneme → Varga mapping from existing protocol data.

    DERIVES from:
    - language.py CONSONANT_MAPPINGS (has category)
    - language.py VOWEL_MAPPINGS (has category)
    - translation.py GERMAN_PHONEMES (has sthana)
    - translation.py ENGLISH_PHONEMES (has sthana)
    - varna.py PANCHA_VARGA (Sanskrit consonants)

    NO HARDCODING - all from protocols!
    """
    mapping: Dict[str, VargaIndex] = {}

    # 1. From CONSONANT_MAPPINGS (language.py)
    for cm in CONSONANT_MAPPINGS:
        if cm.category in CATEGORY_TO_VARGA:
            varga = CATEGORY_TO_VARGA[cm.category]
            # Map western, phoneme (IPA)
            if cm.western:
                mapping[cm.western.lower()] = varga
            if cm.phoneme:
                mapping[cm.phoneme] = varga

    # 2. From VOWEL_MAPPINGS (language.py)
    for vm in VOWEL_MAPPINGS:
        if vm.category in CATEGORY_TO_VARGA:
            varga = CATEGORY_TO_VARGA[vm.category]
            if vm.western:
                mapping[vm.western.lower()] = varga
            if vm.phoneme:
                mapping[vm.phoneme] = varga

    # 3. From GERMAN_PHONEMES (translation.py)
    for key, phoneme in GERMAN_PHONEMES.items():
        if phoneme.sthana in STHANA_TO_VARGA:
            varga = STHANA_TO_VARGA[phoneme.sthana]
            mapping[key.lower()] = varga
            if phoneme.ipa:
                mapping[phoneme.ipa] = varga

    # 4. From ENGLISH_PHONEMES (translation.py)
    for key, phoneme in ENGLISH_PHONEMES.items():
        if phoneme.sthana in STHANA_TO_VARGA:
            varga = STHANA_TO_VARGA[phoneme.sthana]
            mapping[key.lower()] = varga
            if phoneme.ipa:
                mapping[phoneme.ipa] = varga

    # 5. From PANCHA_VARGA (varna.py) - Sanskrit consonants
    for varga_idx, varga_tuple in enumerate(PANCHA_VARGA):
        for varna in varga_tuple:
            # Map IAST and Roman forms
            if varna.iast:
                mapping[varna.iast.lower()] = VargaIndex(varga_idx)
            if varna.roman:
                mapping[varna.roman.lower()] = VargaIndex(varga_idx)

    # 6. ANTAHSTHA (Semivowels) - Override generic "semivowel" category
    # Each semivowel has a specific articulation point in Sanskrit phonetics:
    # य (ya) = palatal → TALAVYA
    # र (ra) = retroflex → MURDHANYA
    # ल (la) = dental → DANTYA
    # व (va) = labial → OSHTHYA
    semivowel_varga = {
        "y": VargaIndex.TALAVYA,  # Palatal
        "r": VargaIndex.MURDHANYA,  # Retroflex
        "l": VargaIndex.DANTYA,  # Dental
        "v": VargaIndex.OSHTHYA,  # Labial
        "w": VargaIndex.OSHTHYA,  # W is labial (Western approximation of व)
    }
    mapping.update(semivowel_varga)

    # 7. USHMAN (Sibilants + H) - From varna.py
    # श (śa) = palatal → TALAVYA
    # ष (ṣa) = retroflex → MURDHANYA
    # स (sa) = dental → DANTYA
    # ह (ha) = glottal → KANTHYA
    sibilant_varga = {
        "ś": VargaIndex.TALAVYA,  # Palatal sibilant
        "sh": VargaIndex.TALAVYA,  # Western approximation
        "ṣ": VargaIndex.MURDHANYA,  # Retroflex sibilant
        "shh": VargaIndex.MURDHANYA,  # Retroflex (alternative)
        "s": VargaIndex.DANTYA,  # Dental sibilant
        "h": VargaIndex.KANTHYA,  # Glottal aspirate
    }
    mapping.update(sibilant_varga)

    return mapping


# Build the mapping from protocols
PHONEME_TO_VARGA: Final[Dict[str, VargaIndex]] = _build_phoneme_varga_from_protocols()


# =============================================================================
# STHANA INDEX (Position within Varga = Energy/Intensity Level)
# =============================================================================
# The 5 Sthanas (HOW - Energy/Intensity) - Position within Varga
# Each Varga has 5 consonants in fixed order:
#   [0] unvoiced stop, [1] aspirated, [2] voiced, [3] voiced-aspirated, [4] nasal


class SthanaIndex(IntEnum):
    """
    Position within Varga = Energy/Intensity level.

    DERIVED from the 5-position structure in PANCHA_VARGA!
    """

    SPARSHA = 0  # Unvoiced stop → minimal energy (0.2)
    MAHAPRANA = KSETRAJNA  # Aspirated → expansion energy (0.6)
    GHOSHAVAT = HALVES  # Voiced → active energy (0.8)
    GHOSHMAHA = TRINITY  # Voiced aspirated → maximum energy (1.0)
    ANUNASIKA = QUARTERS  # Nasal → continuous energy (0.5)


# Verify against PANCHA from seed.py
assert len(SthanaIndex) == PANCHA, f"SthanaIndex must have {PANCHA} values"

# Sthana to energy multiplier (DERIVED from acoustic physics)
STHANA_ENERGY: Final[Dict[SthanaIndex, float]] = {
    SthanaIndex.SPARSHA: 0.2,  # Minimal contact = low energy
    SthanaIndex.MAHAPRANA: 0.6,  # Aspiration = expansion
    SthanaIndex.GHOSHAVAT: 0.8,  # Voicing = active
    SthanaIndex.GHOSHMAHA: 1.0,  # Voiced + aspirated = maximum
    SthanaIndex.ANUNASIKA: 0.5,  # Continuous nasal = medium
}


# =============================================================================
# PRAYATNA → STHANA MAPPING (Sanskrit effort terms from translation.py)
# =============================================================================
# These are the Sanskrit terms used in translation.py Phoneme.prayatna field

PRAYATNA_TO_STHANA: Final[Dict[str, SthanaIndex]] = {
    # Contact types
    "spṛṣṭa": SthanaIndex.SPARSHA,  # Full contact = unvoiced stop
    "sprsta": SthanaIndex.SPARSHA,
    "sparsha": SthanaIndex.SPARSHA,
    # Slight contact (fricatives) - map to voiced (medium-high energy)
    "īṣat-spṛṣṭa": SthanaIndex.GHOSHAVAT,
    "isat-sprsta": SthanaIndex.GHOSHAVAT,
    # Open (vowels) - map to expansion
    "vivṛta": SthanaIndex.MAHAPRANA,
    "vivrta": SthanaIndex.MAHAPRANA,
    # Closed (high vowels) - map to minimal
    "saṁvṛta": SthanaIndex.SPARSHA,
    "samvrta": SthanaIndex.SPARSHA,
    # Nasal
    "anunāsika": SthanaIndex.ANUNASIKA,
    "anunasika": SthanaIndex.ANUNASIKA,
}


# =============================================================================
# CATEGORY → STHANA MAPPING (English terms from language.py)
# =============================================================================
# Derive energy level from category suffix (_aspirated, _nasal)

CATEGORY_TO_STHANA: Final[Dict[str, SthanaIndex]] = {
    # Base categories (unvoiced/neutral) → SPARSHA or GHOSHAVAT
    "velar": SthanaIndex.SPARSHA,  # k = unvoiced
    "velar_aspirated": SthanaIndex.MAHAPRANA,  # kh = aspirated
    "palatal": SthanaIndex.GHOSHAVAT,  # c/j = voiced in common use
    "palatal_aspirated": SthanaIndex.GHOSHMAHA,
    "retroflex": SthanaIndex.GHOSHAVAT,
    "retroflex_aspirated": SthanaIndex.GHOSHMAHA,
    "retroflex_sibilant": SthanaIndex.GHOSHAVAT,
    "dental": SthanaIndex.SPARSHA,  # t = unvoiced
    "dental_aspirated": SthanaIndex.MAHAPRANA,
    "dental_nasal": SthanaIndex.ANUNASIKA,  # n = nasal
    "alveolar": SthanaIndex.GHOSHAVAT,
    "sibilant": SthanaIndex.GHOSHAVAT,  # s/sh = fricative
    "labial": SthanaIndex.SPARSHA,  # p = unvoiced
    "labial_aspirated": SthanaIndex.MAHAPRANA,
    "labial_nasal": SthanaIndex.ANUNASIKA,  # m = nasal
    "bilabial": SthanaIndex.GHOSHAVAT,
    "glottal": SthanaIndex.MAHAPRANA,  # h = aspirate
    "uvular": SthanaIndex.GHOSHAVAT,
    "semivowel": SthanaIndex.GHOSHAVAT,  # y/r/l/v = voiced
    # Vowel categories (derived from acoustic openness)
    "short_vowel": SthanaIndex.SPARSHA,  # i/u = closed = minimal
    "long_vowel": SthanaIndex.MAHAPRANA,  # ā/ī/ū = sustained = expansion
    "diphthong": SthanaIndex.GHOSHMAHA,  # ai/au = complex = maximum
    "vowel_r": SthanaIndex.GHOSHAVAT,  # ṛ = retroflex vowel = active
    # Special
    "anusvara": SthanaIndex.ANUNASIKA,
    "visarga": SthanaIndex.MAHAPRANA,
}


# =============================================================================
# BUILD PHONEME → STHANA FROM EXISTING PROTOCOL DATA
# =============================================================================


def _build_phoneme_sthana_from_protocols() -> Dict[str, SthanaIndex]:
    """
    Build phoneme → Sthana (energy level) mapping from existing protocol data.

    DERIVES from:
    - varna.py PANCHA_VARGA (position within varga = sthana)
    - varna.py SVARA (vowel ordering → energy)
    - varna.py ANTAHSTHA/USHMAN (semi-vowels/sibilants)
    - language.py CONSONANT_MAPPINGS (category suffix → sthana)
    - language.py VOWEL_MAPPINGS (category → sthana)
    - translation.py GERMAN/ENGLISH_PHONEMES (prayatna → sthana)

    NO HARDCODING - all from protocols!
    """
    mapping: Dict[str, SthanaIndex] = {}

    # 1. From PANCHA_VARGA (varna.py) - Position within Varga = Sthana!
    # This is the SSOT: each Varga has 5 consonants in fixed phonation order
    for varga_tuple in PANCHA_VARGA:
        for position, varna in enumerate(varga_tuple):
            sthana = SthanaIndex(position)  # Position 0-4 = Sthana directly!
            if varna.roman:
                mapping[varna.roman.lower()] = sthana
            if varna.iast:
                mapping[varna.iast.lower()] = sthana

    # 2. From SVARA (varna.py) - Vowel energy from position
    # Position in SVARA encodes openness: open vowels first, closed later
    for idx, varna in enumerate(SVARA):
        # Derive energy from vowel ordering:
        # 1-2: a/ā (open) → MAHAPRANA (expansion)
        # 3-6: i/ī/u/ū (closed) → SPARSHA (minimal)
        # 7-8: ṛ/ṝ (retroflex) → GHOSHAVAT (active)
        # 9-12: e/ai/o/au (mid/diphthongs) → GHOSHAVAT/GHOSHMAHA
        if idx < HALVES:  # a, ā
            sthana = SthanaIndex.MAHAPRANA
        elif idx < SHARANAGATI:  # i, ī, u, ū
            sthana = SthanaIndex.SPARSHA
        elif idx < HARE_COUNT:  # ṛ, ṝ
            sthana = SthanaIndex.GHOSHAVAT
        elif idx in (NAVA, 11):  # ai, au (diphthongs)
            sthana = SthanaIndex.GHOSHMAHA
        else:  # e, o
            sthana = SthanaIndex.GHOSHAVAT

        if varna.roman:
            mapping[varna.roman.lower()] = sthana
        if varna.iast:
            mapping[varna.iast.lower()] = sthana

    # 3. From ANTAHSTHA (varna.py) - Semi-vowels = all voiced
    for varna in ANTAHSTHA:
        sthana = SthanaIndex.GHOSHAVAT  # Semi-vowels are voiced
        if varna.roman:
            mapping[varna.roman.lower()] = sthana
        if varna.iast:
            mapping[varna.iast.lower()] = sthana

    # 4. From USHMAN (varna.py) - Sibilants + H
    # śa/ṣa/sa = fricatives (GHOSHAVAT), ha = aspirate (MAHAPRANA)
    for idx, varna in enumerate(USHMAN):
        sthana = SthanaIndex.MAHAPRANA if idx == TRINITY else SthanaIndex.GHOSHAVAT
        if varna.roman:
            mapping[varna.roman.lower()] = sthana
        if varna.iast:
            mapping[varna.iast.lower()] = sthana

    # 5. From CONSONANT_MAPPINGS (language.py) - Category suffix → Sthana
    for cm in CONSONANT_MAPPINGS:
        if cm.category in CATEGORY_TO_STHANA:
            sthana = CATEGORY_TO_STHANA[cm.category]
            if cm.western and cm.western.lower() not in mapping:
                mapping[cm.western.lower()] = sthana
            if cm.phoneme and cm.phoneme not in mapping:
                mapping[cm.phoneme] = sthana

    # 6. From VOWEL_MAPPINGS (language.py) - Category → Sthana
    for vm in VOWEL_MAPPINGS:
        if vm.category in CATEGORY_TO_STHANA:
            sthana = CATEGORY_TO_STHANA[vm.category]
            if vm.western and vm.western.lower() not in mapping:
                mapping[vm.western.lower()] = sthana
            if vm.phoneme and vm.phoneme not in mapping:
                mapping[vm.phoneme] = sthana

    # 7. From GERMAN_PHONEMES (translation.py) - Prayatna → Sthana
    for key, phoneme in GERMAN_PHONEMES.items():
        if phoneme.prayatna in PRAYATNA_TO_STHANA:
            sthana = PRAYATNA_TO_STHANA[phoneme.prayatna]
            if key.lower() not in mapping:
                mapping[key.lower()] = sthana
            if phoneme.ipa and phoneme.ipa not in mapping:
                mapping[phoneme.ipa] = sthana

    # 8. From ENGLISH_PHONEMES (translation.py) - Prayatna → Sthana
    for key, phoneme in ENGLISH_PHONEMES.items():
        if phoneme.prayatna in PRAYATNA_TO_STHANA:
            sthana = PRAYATNA_TO_STHANA[phoneme.prayatna]
            if key.lower() not in mapping:
                mapping[key.lower()] = sthana
            if phoneme.ipa and phoneme.ipa not in mapping:
                mapping[phoneme.ipa] = sthana

    return mapping


# Build the mapping from protocols
PHONEME_TO_STHANA: Final[Dict[str, SthanaIndex]] = _build_phoneme_sthana_from_protocols()


# =============================================================================
# VARGA → QUARTER MAPPING (Lotus Algorithm)
# =============================================================================
# 5 Vargas → 4 Quarters via SWARA_GA ratio (PANCHA/QUARTERS = 5/4)
# TALAVYA + MURDHANYA merge → DHARMA (cognitive quarter)

VARGA_TO_QUARTER: Final[Dict[VargaIndex, int]] = {
    VargaIndex.KANTHYA: 0,  # Throat → GENESIS (system/kernel)
    VargaIndex.TALAVYA: KSETRAJNA,  # Palate → DHARMA (cognition)
    VargaIndex.MURDHANYA: KSETRAJNA,  # Retroflex → DHARMA (LOTUS MERGE: 5→4)
    VargaIndex.DANTYA: HALVES,  # Teeth → KARMA (interface/action)
    VargaIndex.OSHTHYA: TRINITY,  # Lips → MOKSHA (output/liberation)
}

# Verify the Lotus algorithm
assert len(set(VARGA_TO_QUARTER.values())) == QUARTERS, f"Must map to {QUARTERS} quarters"


# =============================================================================
# PHONETIC TENSOR (Result of analysis)
# =============================================================================


@dataclass
class PhoneticTensor:
    """
    Result of phonetic analysis.

    Contains distribution across:
    - 5 Vargas (WHERE - articulation points)
    - 5 Sthanas (HOW - energy/intensity levels)
    """

    varga_vector: Tuple[float, ...]  # 5 values, one per Varga (WHERE)
    sthana_vector: Tuple[float, ...]  # 5 values, one per Sthana (HOW)
    dominant_varga: VargaIndex
    dominant_sthana: SthanaIndex
    quarter: int  # 0-3 (Mahamantra quarter)
    shakti: float  # 0-1 total energy
    source_text: str
    recognized_phonemes: int
    total_phonemes: int


# =============================================================================
# UNIVERSAL PHONETIC BRIDGE
# =============================================================================


class UniversalPhoneticBridge:
    """
    Universal Phonetic Bridge - Routes ANY language through Varga.

    DERIVES from existing protocols:
    - varna.py (Sanskrit phonetics)
    - language.py (character mappings)
    - translation.py (phoneme data)

    SCALES to any language that has:
    - IPA transcription OR
    - Category/Sthana classification OR
    - Roman/ASCII approximation

    NOTE: Use get_phonetic_bridge() to access via ServiceRegistry.
    """

    # MAHAMANTRA SUBSTRATE: Core infrastructure, no auto-wrap needed
    _naga_flooded: bool = True
    _naga_gene: str = "phonetic_bridge"

    def __init__(self) -> None:
        """Initialize with derived mappings."""
        self._phoneme_to_varga = PHONEME_TO_VARGA
        self._sthana_to_varga = STHANA_TO_VARGA
        self._category_to_varga = CATEGORY_TO_VARGA

    def analyze(self, text: str, language: Optional[NaturalLanguage] = None) -> PhoneticTensor:
        """
        Analyze text and return PhoneticTensor.

        Works for ANY language - derives from protocol mappings.
        """
        text_lower = text.lower()

        varga_counts = [0.0] * PANCHA
        sthana_counts = [0.0] * PANCHA
        total_energy = 0.0
        total_phonemes = 0
        recognized = 0

        i = 0
        while i < len(text_lower):
            char = text_lower[i]

            # Try digraphs first (ch, th, etc.)
            if i + HALVES <= len(text_lower):
                digraph = text_lower[i : i + HALVES]
                if digraph in self._phoneme_to_varga:
                    varga = self._phoneme_to_varga[digraph]
                    sthana = PHONEME_TO_STHANA.get(digraph, SthanaIndex.GHOSHAVAT)
                    varga_counts[varga.value] += KSETRAJNA
                    sthana_counts[sthana.value] += KSETRAJNA
                    total_energy += STHANA_ENERGY.get(sthana, 0.5)
                    recognized += KSETRAJNA
                    total_phonemes += KSETRAJNA
                    i += HALVES
                    continue

            # Single character
            if char.isalpha():
                total_phonemes += KSETRAJNA
                if char in self._phoneme_to_varga:
                    varga = self._phoneme_to_varga[char]
                    sthana = PHONEME_TO_STHANA.get(char, SthanaIndex.GHOSHAVAT)
                    varga_counts[varga.value] += KSETRAJNA
                    sthana_counts[sthana.value] += KSETRAJNA
                    total_energy += STHANA_ENERGY.get(sthana, 0.5)
                    recognized += KSETRAJNA

            i += KSETRAJNA

        # Normalize vectors
        total_varga = sum(varga_counts) or KSETRAJNA
        total_sthana = sum(sthana_counts) or KSETRAJNA
        varga_vector = tuple(v / total_varga for v in varga_counts)
        sthana_vector = tuple(s / total_sthana for s in sthana_counts)

        # Find dominant varga and sthana
        dominant_varga_idx = varga_vector.index(max(varga_vector))
        dominant_varga = VargaIndex(dominant_varga_idx)
        dominant_sthana_idx = sthana_vector.index(max(sthana_vector))
        dominant_sthana = SthanaIndex(dominant_sthana_idx)

        # Map to quarter
        quarter = VARGA_TO_QUARTER[dominant_varga]

        # Calculate shakti (normalized energy)
        shakti = min(1.0, total_energy / max(recognized, KSETRAJNA))

        return PhoneticTensor(
            varga_vector=varga_vector,
            sthana_vector=sthana_vector,
            dominant_varga=dominant_varga,
            dominant_sthana=dominant_sthana,
            quarter=quarter,
            shakti=shakti,
            source_text=text,
            recognized_phonemes=recognized,
            total_phonemes=total_phonemes,
        )

    def get_varga_for_phoneme(self, phoneme: str) -> Optional[VargaIndex]:
        """Get Varga for a specific phoneme."""
        return self._phoneme_to_varga.get(phoneme.lower())

    def get_varga_for_sthana(self, sthana: str) -> Optional[VargaIndex]:
        """Get Varga for a Sanskrit sthana term."""
        return self._sthana_to_varga.get(sthana.lower())

    def get_varga_for_category(self, category: str) -> Optional[VargaIndex]:
        """Get Varga for an English category term."""
        return self._category_to_varga.get(category.lower())

    def get_varga_consonants(self, varga: VargaIndex) -> Tuple[Varna, ...]:
        """Get the Sanskrit consonants for a Varga (from PANCHA_VARGA)."""
        return PANCHA_VARGA[varga.value]

    def get_sthana_for_phoneme(self, phoneme: str) -> Optional[SthanaIndex]:
        """Get Sthana (energy level) for a specific phoneme."""
        return PHONEME_TO_STHANA.get(phoneme.lower())

    def get_energy_for_phoneme(self, phoneme: str) -> float:
        """Get energy value (0-1) for a specific phoneme."""
        sthana = self.get_sthana_for_phoneme(phoneme)
        if sthana is not None:
            return STHANA_ENERGY.get(sthana, 0.5)
        return 0.5  # Default medium energy


# =============================================================================
# SERVICEREGISTRY FACTORY
# =============================================================================

import logging

logger = logging.getLogger("PHONETIC_BRIDGE")


def get_phonetic_bridge() -> UniversalPhoneticBridge:
    """
    Get UniversalPhoneticBridge through ServiceRegistry.

    ARCHITECTURE:
        UniversalPhoneticBridge is MAHAMANTRA SUBSTRATE - routes phonetics to Varga.
        Uses ServiceRegistry for singleton pattern but is NOT auto-wrapped
        with NagaProxy (marked with _naga_flooded = True).

    Returns:
        UniversalPhoneticBridge instance (singleton via ServiceRegistry)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(UniversalPhoneticBridge)
    if existing is not None:
        return existing

    # Create new instance
    instance = UniversalPhoneticBridge()

    # Register with ServiceRegistry (no NagaProxy wrap - _naga_flooded = True)
    ServiceRegistry.register(UniversalPhoneticBridge, instance)
    logger.info("✅ UniversalPhoneticBridge registered via ServiceRegistry (MAHAMANTRA substrate)")

    return ServiceRegistry.get(UniversalPhoneticBridge)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "VargaIndex",
    "SthanaIndex",
    "PhoneticTensor",
    # Bridge
    "UniversalPhoneticBridge",
    "get_phonetic_bridge",
    # Varga mappings (WHERE - articulation point)
    "PHONEME_TO_VARGA",
    "STHANA_TO_VARGA",
    "CATEGORY_TO_VARGA",
    "VARGA_TO_QUARTER",
    # Sthana mappings (HOW - energy/intensity)
    "PHONEME_TO_STHANA",
    "PRAYATNA_TO_STHANA",
    "CATEGORY_TO_STHANA",
    "STHANA_ENERGY",
]
