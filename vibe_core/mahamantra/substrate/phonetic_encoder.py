"""
PHONETIC ENCODER — Any Language → RAMA Coordinates
===================================================

"sarva-bhūtāni" — all living beings

The RAMA Grid is Sanskrit (49 phonemes). But human input is English/German/etc.
This module bridges the gap:

    English text → IPA phonemes → nearest RAMA coordinate → 4D signature

The mapping is LOSSY by design — English has ~44 phonemes, Sanskrit has 49.
Some English sounds have no exact Sanskrit equivalent (th, w, f, z).
We map to the NEAREST articulatory equivalent.

This is NOT a transliteration. It's a PHONETIC PROJECTION:
    The English word "fire" → /faɪər/ → [pa, ai, ra] → RAMA [36, 11, 42]
    Because 'f' is labial (like 'pa'), 'ai' is a diphthong, 'r' is 'ra'.

The projection preserves ARTICULATORY POSITION (= Element in Pancha Walk).
What's lost is aspiration detail and some vowel length distinctions.

LANGUAGE DETECTION:
    Simple heuristic: if text contains IAST diacriticals → Sanskrit path.
    Otherwise → phonetic projection path.
    Fast. No external dependencies.

NO LLM. NO EXTERNAL API. PURE PHONETIC MAPPING.
"""

from __future__ import annotations

from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    ELEMENT_NAMES,
)
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL

# =============================================================================
# IAST DETECTION
# =============================================================================

# Characters that indicate IAST Sanskrit (not present in English/German)
_IAST_MARKERS: Final[frozenset[str]] = frozenset("āīūṛṝḷḹṁḥṅñṭḍṇśṣ")


def detect_language(text: str) -> str:
    """
    Detect input language for routing.

    Returns:
        'sanskrit' if IAST diacriticals detected
        'latin' for English/German/etc (Latin alphabet without diacriticals)
    """
    for ch in text:
        if ch in _IAST_MARKERS:
            return "sanskrit"
    return "latin"


# =============================================================================
# ENGLISH/GERMAN → IPA → RAMA MAPPING
# =============================================================================

# English consonant graphemes → nearest RAMA coordinate
# Mapping principle: same articulatory position (place + manner)
#
# RAMA Grid structure:
#   Vowels:     0-15  (a, i, u, ṛ, ḷ, ā, ī, ū, ṝ, ḹ, e, ai, o, au, ṁ, ḥ)
#   Sparsha:    16-40 (5×5: ka-ṅa, ca-ña, ṭa-ṇa, ta-na, pa-ma)
#   Remaining:  41-48 (ya, ra, la, va, śa, ṣa, sa, ha)

_CONSONANT_MAP: Final[Dict[str, int]] = {
    # Velars (kantha = throat) → ka-row (RAMA 16-20)
    "k": 16,   # ka — unvoiced velar stop
    "g": 18,   # ga — voiced velar stop
    "ng": 20,  # ṅa — velar nasal

    # Palatals (talu = palate) → ca-row (RAMA 21-25)
    "ch": 21,  # ca — unvoiced palatal
    "j": 23,   # ja — voiced palatal
    "ny": 25,  # ña — palatal nasal

    # Retroflexes (murdha = roof) → ṭa-row (RAMA 26-30)
    "t": 26,   # ṭa — English 't' is closer to retroflex than dental
    "d": 28,   # ḍa — English 'd' is closer to retroflex than dental

    # Dentals (danta = teeth) → ta-row (RAMA 31-35)
    "th": 31,  # ta — English 'th' (voiceless) → dental unvoiced
    "dh": 33,  # da — English 'th' (voiced, as in 'the') → dental voiced
    "n": 35,   # na — dental nasal

    # Labials (oshtha = lips) → pa-row (RAMA 36-40)
    "p": 36,   # pa — unvoiced labial
    "b": 38,   # ba — voiced labial
    "f": 37,   # pha — 'f' ≈ aspirated labial (closest match)
    "v": 44,   # va — labial semivowel
    "m": 40,   # ma — labial nasal
    "w": 44,   # va — 'w' ≈ va (labial approximant)

    # Semivowels (RAMA 41-44)
    "y": 41,   # ya — palatal semivowel
    "r": 42,   # ra — retroflex semivowel
    "l": 43,   # la — dental lateral

    # Sibilants (RAMA 45-47)
    "sh": 45,  # śa — palatal sibilant
    "s": 47,   # sa — dental sibilant
    "z": 23,   # ja — 'z' ≈ voiced palatal (closest)

    # Glottal (RAMA 48)
    "h": 48,   # ha — glottal

    # German-specific
    "sch": 45,  # śa — German 'sch' = palatal sibilant
    "ch_soft": 45,  # śa — German 'ich' sound
    "ch_hard": 16,  # ka — German 'ach' sound (velar)
    "pf": 36,  # pa — German 'pf' ≈ labial
    "ts": 21,  # ca — German 'z/ts' ≈ palatal affricate
    "x": 16,   # ka — 'x' = /ks/ → velar component
    "q": 16,   # ka — 'q' = /kw/ → velar component
    "c_hard": 16,  # ka — 'c' as in 'cat'
    "c_soft": 47,  # sa — 'c' as in 'city'
}

# English vowel graphemes → nearest RAMA coordinate
_VOWEL_MAP: Final[Dict[str, int]] = {
    # Short vowels
    "a_short": 0,   # a — as in 'but'
    "e_short": 10,  # e — as in 'bet'
    "i_short": 1,   # i — as in 'bit'
    "o_short": 12,  # o — as in 'hot'
    "u_short": 2,   # u — as in 'put'

    # Long vowels
    "a_long": 5,    # ā — as in 'father'
    "e_long": 10,   # e — as in 'bay' (no exact Sanskrit long e)
    "i_long": 6,    # ī — as in 'see'
    "o_long": 12,   # o — as in 'go'
    "u_long": 7,    # ū — as in 'moon'

    # Diphthongs
    "ai": 11,       # ai — as in 'my'
    "au": 13,       # au — as in 'how'
    "oi": 11,       # ai — as in 'boy' (≈ ai)
    "ou": 13,       # au — as in 'out'
    "ei": 10,       # e — as in 'day'

    # Schwa
    "schwa": 0,     # a — the neutral vowel
}


# =============================================================================
# SIMPLE ENGLISH TOKENIZER
# =============================================================================

def _tokenize_english(text: str) -> List[Tuple[str, int]]:
    """
    Tokenize English text into (grapheme_cluster, rama_coord) pairs.

    Uses greedy longest-match on consonant digraphs,
    then maps vowels by simple position rules.

    This is intentionally simple — not a full IPA converter.
    The goal is ARTICULATORY POSITION, not perfect pronunciation.
    """
    result: List[Tuple[str, int]] = []
    text = text.lower().strip()
    i = 0

    while i < len(text):
        ch = text[i]

        # Skip non-alpha
        if not ch.isalpha():
            i += 1
            continue

        # Try digraphs first (longest match)
        matched = False
        if i + 2 < len(text):
            tri = text[i:i+3]
            if tri == "sch":
                result.append(("sch", _CONSONANT_MAP["sch"]))
                i += 3
                matched = True
                continue

        if i + 1 < len(text):
            di = text[i:i+2]
            if di in ("sh", "ch", "th", "ng", "ny", "dh", "pf", "ts"):
                coord = _CONSONANT_MAP.get(di)
                if coord is not None:
                    result.append((di, coord))
                    i += 2
                    matched = True
                    continue

        if matched:
            continue

        # Single character
        if ch in "bcdfghjklmnpqrstvwxyz":
            # Consonant
            if ch == "c":
                # 'c' before e/i = soft, otherwise hard
                if i + 1 < len(text) and text[i+1] in "ei":
                    coord = _CONSONANT_MAP["c_soft"]
                else:
                    coord = _CONSONANT_MAP["c_hard"]
            elif ch == "x":
                coord = _CONSONANT_MAP["x"]
            elif ch == "q":
                coord = _CONSONANT_MAP["q"]
            else:
                coord = _CONSONANT_MAP.get(ch, 48)  # default to 'ha'
            result.append((ch, coord))
            i += 1

        elif ch in "aeiou":
            # Vowel — simple heuristic for length
            # Double vowel or vowel + e at end = long
            is_long = False
            if i + 1 < len(text) and text[i+1] == ch:
                is_long = True
            elif i + 1 < len(text) and text[i+1] == "e" and (i + 2 >= len(text) or not text[i+2].isalpha()):
                is_long = True

            # Check for diphthongs
            if i + 1 < len(text):
                di = text[i:i+2]
                if di in ("ai", "au", "oi", "ou", "ei"):
                    coord = _VOWEL_MAP.get(di, 0)
                    result.append((di, coord))
                    i += 2
                    continue

            suffix = "_long" if is_long else "_short"
            key = f"{ch}{suffix}"
            coord = _VOWEL_MAP.get(key, 0)
            result.append((ch, coord))
            i += 1
        else:
            # Unknown → schwa
            result.append((ch, 0))
            i += 1

    return result


# =============================================================================
# PUBLIC API
# =============================================================================


def encode_text(text: str) -> Tuple[int, ...]:
    """
    Encode ANY text (Sanskrit, English, German) to RAMA coordinates.

    Auto-detects language:
        - IAST diacriticals → Sanskrit path (exact encoding via varnamala_codec)
        - Latin alphabet → phonetic projection (approximate)

    Returns:
        Tuple of RAMA coordinates (0-48).
    """
    lang = detect_language(text)

    if lang == "sanskrit":
        from vibe_core.mahamantra.substrate.varnamala_codec import encode
        return encode(text)

    # Latin path: English/German phonetic projection
    tokens = _tokenize_english(text)
    return tuple(coord for _, coord in tokens)


def encode_with_detail(text: str) -> List[Dict]:
    """
    Encode text with full detail about each mapping.

    Returns list of {grapheme, rama_coord, phoneme, element, is_exact}.
    """
    lang = detect_language(text)

    if lang == "sanskrit":
        from vibe_core.mahamantra.substrate.varnamala_codec import encode
        from vibe_core.mahamantra.substrate.rama_grid import rama_to_phoneme as r2p
        coords = encode(text)
        return [
            {
                "grapheme": r2p(c),
                "rama_coord": c,
                "phoneme": r2p(c),
                "element": ELEMENT_NAMES[COORD_ELEMENT[c]],
                "is_exact": True,
            }
            for c in coords
        ]

    tokens = _tokenize_english(text)
    from vibe_core.mahamantra.substrate.rama_grid import rama_to_phoneme as r2p
    return [
        {
            "grapheme": grapheme,
            "rama_coord": coord,
            "phoneme": r2p(coord),
            "element": ELEMENT_NAMES[COORD_ELEMENT[coord]],
            "is_exact": False,  # Phonetic projection, not exact
        }
        for grapheme, coord in tokens
    ]


def text_to_words(
    text: str,
    seed: int = 0,
    preset: str = "quantum",
) -> "SeedResult":
    """
    THE FULL PIPELINE: Any text → RAMA coords → Synth → Resonant words.

    This is the top-level entry point for the MahaLLM.

    Args:
        text: Any text (Sanskrit, English, German)
        seed: Starting seed for the synth
        preset: Synth preset

    Returns:
        SeedResult with resonant words and meanings.
    """
    from vibe_core.mahamantra.substrate.seed_to_words import spell_to_words, SeedResult

    lang = detect_language(text)

    if lang == "sanskrit":
        # Direct path: Sanskrit → spell through synth
        return spell_to_words(text, seed=seed, preset=preset)

    # Phonetic projection path
    coords = encode_text(text)
    if not coords:
        from vibe_core.mahamantra.substrate.seed_to_words import SeedResult
        return SeedResult(seed=seed, preset=preset, coords=(), attractor=None)

    # Feed projected coords through synth
    from vibe_core.mahamantra.adapters.synth import create_synth
    from vibe_core.mahamantra.substrate.seed_to_words import CoordResult

    synth = create_synth(preset=preset)
    cycle = synth.spell_cycle(tuple(coords), seed)

    coord_results = []
    for i, step in enumerate(cycle.steps):
        rama_coord = step.output_value % VARNAMALA_TOTAL
        coord_results.append(CoordResult(
            step=i,
            synth_value=step.output_value,
            rama_coord=rama_coord,
        ))

    return SeedResult(
        seed=seed,
        preset=preset,
        coords=tuple(coord_results),
        attractor=cycle.final_value % VARNAMALA_TOTAL,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "detect_language",
    "encode_text",
    "encode_with_detail",
    "text_to_words",
]
