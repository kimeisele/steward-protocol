"""
SANSKRIT LOOKUP - Verse Word-for-Word via RAMA Coordinates
==========================================================

"śabdaṁ brahma" - Sound is the Absolute

Entry:  verse_id (e.g. "BG.18.66") or RAMA coordinate sequence
Exit:   Sanskrit word, meaning, H/K/R signature

The Gita is not a book. It is a routing table.
Each verse = sequence of Sanskrit words.
Each word = sequence of RAMA coordinates (0-48).
Each coordinate = one tick of the VenuOrchestrator (VENU field, 6 bits).

The entire Bhagavad Gita word-for-word:
  45,815 phonemes = 935 * VARNAMALA (deduplicated)
  = 34KB packed = 70% of 65K Lotus address space

NO EXTERNAL DEPENDENCIES. NO LLM. PURE COORDINATE LOOKUP.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Final, Optional, Sequence

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    MALA,
    NAVA,
    WORDS,
)
from vibe_core.mahamantra.substrate.varnamala_codec import (
    decode,
    encode,
    pack_word,
    unpack_word,
)

# =============================================================================
# DATA PATH
# =============================================================================

from vibe_core.mahamantra.substrate._paths import DATA_DIR
_DATA_DIR: Final[Path] = DATA_DIR
_LEXICON_PATH: Final[Path] = _DATA_DIR / "rama_lexicon.json"


# =============================================================================
# RESULT TYPE
# =============================================================================


class WordEntry:
    """A Sanskrit word from the Gita word-for-word."""

    __slots__ = ("sanskrit", "meaning", "coords", "packed_hex")

    def __init__(self, sanskrit: str, meaning: str, coords: tuple[int, ...], packed_hex: str):
        self.sanskrit = sanskrit
        self.meaning = meaning
        self.coords = coords
        self.packed_hex = packed_hex

    @property
    def element_walk(self) -> str:
        """PANCHA element walk signature (articulation path = semantic content)."""
        from vibe_core.mahamantra.substrate.pancha_walk import walk_signature

        return walk_signature(self.coords)

    @property
    def derived_sig(self) -> str:
        """3D signature: element + varga + sub (99.97% unique)."""
        from vibe_core.mahamantra.substrate.pancha_walk import derived_signature

        return derived_signature(self.coords)

    @property
    def full_sig(self) -> str:
        """4D signature: element + varga + sub + harmonic (100% unique, bijective)."""
        from vibe_core.mahamantra.substrate.pancha_walk import full_signature

        return full_signature(self.coords)

    @property
    def shruti_pattern(self) -> str:
        """SHRUTI/NAKSHATRA pattern: S=shruti (R-reachable), N=nakshatra."""
        from vibe_core.mahamantra.substrate.pancha_walk import IS_SHRUTI

        return "".join("S" if IS_SHRUTI[c] else "N" for c in self.coords)

    def __repr__(self) -> str:
        return f"WordEntry({self.sanskrit!r}, {self.meaning!r})"


class VerseWords:
    """All word-for-word entries for a single verse."""

    __slots__ = ("ref", "chapter", "verse", "words")

    def __init__(self, ref: str, chapter: int, verse: int, words: tuple[WordEntry, ...]):
        self.ref = ref
        self.chapter = chapter
        self.verse = verse
        self.words = words

    @property
    def phoneme_count(self) -> int:
        return sum(len(w.coords) for w in self.words)

    def __repr__(self) -> str:
        return f"VerseWords({self.ref!r}, {len(self.words)} words)"


# =============================================================================
# LEXICON LOADER (lazy singleton)
# =============================================================================


@lru_cache(maxsize=1)
def _load_lexicon() -> tuple[dict[str, dict], list[dict]]:
    """Load RAMA lexicon. Cached after first call."""
    with open(_LEXICON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["vocabulary"], data["verses"]


def _get_vocab() -> dict[str, dict]:
    return _load_lexicon()[0]


def _get_verses() -> list[dict]:
    return _load_lexicon()[1]


# =============================================================================
# LOOKUP BY VERSE
# =============================================================================


@lru_cache(maxsize=128)
def verse_words(chapter: int, verse: int) -> Optional[VerseWords]:
    """
    Get word-for-word Sanskrit entries for a Gita verse.

    Entry point for VANDANAM (step 6 of NavaBhakti pipeline).

    >>> vw = verse_words(18, 66)
    >>> vw.ref
    'BG.18.66'
    >>> vw.words[0].sanskrit
    'sarva-dharmān'
    """
    ref = f"BG.{chapter}.{verse}"
    vocab = _get_vocab()

    for v in _get_verses():
        if v["ref"] != ref:
            continue

        entries = []
        for w in v.get("words", []):
            packed_hex = w["packed"]
            length = w["length"]
            entry = vocab.get(packed_hex)
            if not entry:
                continue

            coords = tuple(entry["coords"])
            meanings = entry.get("meanings", [])
            entries.append(
                WordEntry(
                    sanskrit=entry["word"],
                    meaning=meanings[0] if meanings else "",
                    coords=coords,
                    packed_hex=packed_hex,
                )
            )

        return VerseWords(
            ref=ref,
            chapter=chapter,
            verse=verse,
            words=tuple(entries),
        )

    return None


# =============================================================================
# LOOKUP BY COORDINATES
# =============================================================================


@lru_cache(maxsize=512)
def word_by_packed(packed_hex: str) -> Optional[WordEntry]:
    """Look up a word by its packed RAMA coordinate hex."""
    vocab = _get_vocab()
    entry = vocab.get(packed_hex)
    if not entry:
        return None
    return WordEntry(
        sanskrit=entry["word"],
        meaning=entry["meanings"][0] if entry["meanings"] else "",
        coords=tuple(entry["coords"]),
        packed_hex=packed_hex,
    )


def word_by_coords(coords: Sequence[int]) -> Optional[WordEntry]:
    """Look up a word by its RAMA coordinate sequence."""
    packed, length = pack_word(coords)
    return word_by_packed(f"{packed:x}")


def word_by_iast(text: str) -> Optional[WordEntry]:
    """Look up a word by IAST text (encode → lookup)."""
    coords = encode(text)
    return word_by_coords(coords)


# =============================================================================
# H/K/R SIGNATURE
# =============================================================================


def hkr_signature(coords: Sequence[int], cycle: int = 0) -> str:
    """
    Compute the Mahamantra name signature of a RAMA coordinate sequence.

    Each coordinate maps back to a Mahamantra position via krishna_route inverse.
    The position's name (H/K/R) gives the signature character.

    The signature is CYCLE-DEPENDENT: the same word gets different spiritual
    "moods" depending on which Mahamantra cycle it's observed through.

    >>> hkr_signature(encode("bhakti"), cycle=0)
    'HHHH'
    """
    from vibe_core.mahamantra.protocols._seed import MAHAMANTRA_WORD_PATTERN

    # krishna_route(pos, cycle) = (pos * 17 + cycle * 16) % 49
    # Inverse: pos = ((coord - cycle * 16) * 26) % 49  (17^-1 mod 49 = 26)
    sig = []
    for coord in coords:
        pos = ((coord - cycle * WORDS) * 26) % 49
        maha_pos = pos % WORDS
        sig.append(MAHAMANTRA_WORD_PATTERN[maha_pos])
    return "".join(sig)


# =============================================================================
# STATISTICS
# =============================================================================


def lexicon_stats() -> dict:
    """Get lexicon statistics."""
    vocab = _get_vocab()
    verses = _get_verses()
    total_phonemes = sum(sum(w["length"] for w in v.get("words", [])) for v in verses)
    return {
        "unique_words": len(vocab),
        "total_verses": len(verses),
        "total_phonemes": total_phonemes,
        "fits_in_65k": total_phonemes <= 65536,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "WordEntry",
    "VerseWords",
    "verse_words",
    "word_by_packed",
    "word_by_coords",
    "word_by_iast",
    "hkr_signature",
    "lexicon_stats",
]
