"""
VARNAMALA CODEC - Sanskrit ↔ RAMA Coordinate Encoding
=====================================================

"varṇamālā" = the garland of letters (49 sounds = POSITION_SUM_RAMA)

This codec encodes IAST Sanskrit text as sequences of RAMA Grid
coordinates. Each coordinate is 6 bits (0-48, fits in VENU field).

NOT a hash. NOT a lookup table. COORDINATES in the 49-space.
The VenuOrchestrator's VENU field (6 bits) addresses one letter per tick.

    IAST text → phoneme tokenization → RAMA coordinates → packed bits
    packed bits → RAMA coordinates → phoneme lookup → IAST text

Every Sanskrit word IS a walk through the RAMA Grid.
The Flute doesn't select words - it SPELLS them.
"""

from __future__ import annotations

from typing import Final, Sequence

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    PRASADAM,
    VENU_HOLES,
    WORDS,
)
from vibe_core.mahamantra.substrate.rama_grid import (
    POSITION_SUM_RAMA,
    SPARSHA_GRID,
    SVARAS,
    VARNAMALA_TOTAL,
)

# =============================================================================
# PHONEME → RAMA COORDINATE (reverse of rama_to_phoneme)
# =============================================================================

# The remaining consonants (positions 41-48)
_REMAINING: Final[tuple[str, ...]] = ("ya", "ra", "la", "va", "śa", "ṣa", "sa", "ha")


def _build_phoneme_index() -> tuple[dict[str, int], dict[str, int]]:
    """
    Build two indices:
    1. Canonical: full phoneme form ("ka", "kha") → RAMA coordinate (49 entries)
    2. IAST: bare consonant forms ("k", "kh") → same coordinate (for tokenization)

    RAMA grid stores consonants WITH inherent 'a' (Sanskrit convention).
    IAST text writes bare consonants when no vowel follows (virama/conjunct).
    Both forms map to the same RAMA coordinate.
    """
    canonical: dict[str, int] = {}
    iast: dict[str, int] = {}

    # Vowels (positions 0-15) - same in both
    for i, svara in enumerate(SVARAS):
        canonical[svara] = i
        iast[svara] = i

    # Sparsha consonants (positions 16-40)
    for row_idx, row in enumerate(SPARSHA_GRID):
        for col_idx, consonant in enumerate(row.consonants):
            coord = WORDS + row_idx * PANCHA + col_idx
            canonical[consonant] = coord
            iast[consonant] = coord
            # Add bare form (strip trailing 'a')
            if consonant.endswith("a") and len(consonant) > 1:
                bare = consonant[:-1]
                iast[bare] = coord

    # Remaining consonants (positions 41-48)
    for i, phoneme in enumerate(_REMAINING):
        coord = WORDS + PRASADAM + i
        canonical[phoneme] = coord
        iast[phoneme] = coord
        # Add bare form
        if phoneme.endswith("a") and len(phoneme) > 1:
            bare = phoneme[:-1]
            iast[bare] = coord

    return canonical, iast


_CANONICAL_INDEX: Final[dict[str, int]]
_IAST_INDEX: Final[dict[str, int]]
_CANONICAL_INDEX, _IAST_INDEX = _build_phoneme_index()

# Verify canonical has exactly 49 entries
assert len(_CANONICAL_INDEX) == VARNAMALA_TOTAL, (
    f"Expected {VARNAMALA_TOTAL} canonical phonemes, got {len(_CANONICAL_INDEX)}"
)

# Coordinate → canonical phoneme (for decoding)
_COORD_TO_PHONEME: Final[dict[int, str]] = {v: k for k, v in _CANONICAL_INDEX.items()}

# =============================================================================
# IAST TOKENIZER
# =============================================================================
# IAST uses multi-character sequences for some phonemes:
#   Aspirated: kh, gh, ch, jh, ṭh, ḍh, th, dh, ph, bh
#   Compound vowels: ai, au
#   Diacriticals: ā, ī, ū, ṛ, ṝ, ḷ, ḹ, ṁ, ḥ, ṅ, ñ, ṭ, ḍ, ṇ, ś, ṣ

# Maximum phoneme length in IAST index (for tokenizer window)
_MAX_IAST_LEN: Final[int] = max(len(p) for p in _IAST_INDEX)

# Characters to skip during tokenization
_SKIP_CHARS: Final[frozenset[str]] = frozenset(" \t\n-;,—.()/'\"0123456789:")


def tokenize_iast(text: str) -> list[str]:
    """
    Tokenize IAST text into phoneme tokens.

    Greedy longest-match against the Varnamala IAST index.
    Handles both full ("ka") and bare ("k") consonant forms.
    Non-phonemic characters (spaces, hyphens, punctuation) are skipped.
    """
    tokens: list[str] = []
    i = 0
    while i < len(text):
        if text[i] in _SKIP_CHARS:
            i += 1
            continue

        # Greedy match: try longest phoneme first
        matched = False
        for length in range(min(_MAX_IAST_LEN, len(text) - i), 0, -1):
            candidate = text[i : i + length]
            if candidate in _IAST_INDEX:
                tokens.append(candidate)
                i += length
                matched = True
                break

        if not matched:
            i += 1

    return tokens


def encode(text: str) -> tuple[int, ...]:
    """
    Encode IAST Sanskrit text as RAMA coordinate sequence.

    Each coordinate is 0-48, fitting in 6 bits (VENU field).
    """
    tokens = tokenize_iast(text)
    return tuple(_IAST_INDEX[t] for t in tokens)


def decode(coords: Sequence[int]) -> str:
    """
    Decode RAMA coordinate sequence back to canonical IAST phonemes.

    Returns phonemes in their canonical (with inherent 'a') form.
    """
    return "".join(_COORD_TO_PHONEME.get(c, "?") for c in coords)


# =============================================================================
# PACKED ENCODING (bit-level)
# =============================================================================
# Each RAMA coordinate needs 6 bits (VENU_HOLES).
# Pack sequences into integers for compact storage.

BITS_PER_COORD: Final[int] = VENU_HOLES  # 6


def pack_word(coords: Sequence[int]) -> tuple[int, int]:
    """
    Pack RAMA coordinate sequence into a single integer.

    Returns (packed_value, length).
    Length is needed because leading zeros are significant.

    Max word length for 64-bit: 10 phonemes (60 bits).
    Max word length for 128-bit: 21 phonemes (126 bits).
    """
    packed = 0
    for i, coord in enumerate(coords):
        packed |= (coord & 0x3F) << (i * BITS_PER_COORD)
    return packed, len(coords)


def unpack_word(packed: int, length: int) -> tuple[int, ...]:
    """
    Unpack integer back to RAMA coordinate sequence.

    >>> unpack_word(*pack_word((19, 47, 0, 42, 25, 0)))
    (19, 47, 0, 42, 25, 0)
    """
    coords = []
    for i in range(length):
        coord = (packed >> (i * BITS_PER_COORD)) & 0x3F
        coords.append(coord)
    return tuple(coords)


# =============================================================================
# VERSE ENCODING
# =============================================================================


def encode_verse_words(synonyms_text: str) -> list[dict]:
    """
    Encode all word-for-word entries from a verse's synonyms field.

    Returns list of {sanskrit, meaning, rama_coords, packed, length}.
    """
    entries = []
    for pair in synonyms_text.split(";"):
        pair = pair.strip()
        if "—" not in pair:
            continue
        parts = pair.split("—", 1)
        sanskrit = parts[0].strip()
        meaning = parts[1].strip()
        if not sanskrit or not meaning:
            continue

        coords = encode(sanskrit)
        packed, length = pack_word(coords)
        entries.append(
            {
                "sanskrit": sanskrit,
                "meaning": meaning,
                "rama_coords": coords,
                "packed": packed,
                "length": length,
            }
        )

    return entries


# =============================================================================
# VENU INTEGRATION
# =============================================================================


def coords_to_venu_sequence(coords: Sequence[int]) -> list[int]:
    """
    Convert RAMA coordinates to VENU field values for VenuOrchestrator.

    Each coordinate becomes a VENU value (6 bits, 0-63).
    RAMA coordinates are 0-48, always fit in VENU (0-63).

    The VenuOrchestrator can play this sequence to spell the word.
    """
    return [c & ((1 << VENU_HOLES) - 1) for c in coords]


# =============================================================================
# VERIFICATION
# =============================================================================


def verify_codec() -> bool:
    """
    Verify the codec round-trips correctly.

    Tests encoding and decoding of key architectural words.
    """
    test_words = [
        "hare",
        "kṛṣṇa",
        "rāma",
        "dharma",
        "yoga",
        "bhakti",
        "śaraṇam",
    ]

    for word in test_words:
        coords = encode(word)
        # Each coordinate must be valid RAMA address
        for c in coords:
            if c >= POSITION_SUM_RAMA:
                raise ValueError(f"Coordinate {c} exceeds RAMA space ({POSITION_SUM_RAMA}) for word '{word}'")
        # Pack/unpack must round-trip
        packed, length = pack_word(coords)
        recovered = unpack_word(packed, length)
        if recovered != coords:
            raise ValueError(f"Pack/unpack mismatch for '{word}': {coords} != {recovered}")

    return True


__all__ = [
    "tokenize_iast",
    "encode",
    "decode",
    "pack_word",
    "unpack_word",
    "encode_verse_words",
    "coords_to_venu_sequence",
    "verify_codec",
    "BITS_PER_COORD",
]
