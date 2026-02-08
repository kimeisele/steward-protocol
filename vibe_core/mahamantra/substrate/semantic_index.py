"""
SEMANTIC INDEX — Reverse Lookup for the RAMA Lexicon
====================================================

"veda-vit" — the knower of the Vedas

The RAMA Lexicon (rama_lexicon.json) stores 4127 Gita words as:
    packed_hex → {word, coords, length, meanings}

Forward:  word → coords → 4D signature → meaning
Reverse:  4D query → matching words → meanings

This module builds multi-dimensional indices over the lexicon,
enabling queries like:
    - "all words with element=agni"
    - "all words starting at RAMA position 42"
    - "all words whose shruti pattern starts with SS"
    - "all words with harmonic dissolution to position 0"

NO LLM. NO EXTERNAL DEPENDENCIES. PURE COORDINATE LOOKUP.

The indices are built lazily on first access and cached.
"""

from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Dict, Final, FrozenSet, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    SEVEN,
    WORDS,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_SUB,
    COORD_VARGA,
    ELEMENT_NAMES,
    IS_SHRUTI,
)
from vibe_core.mahamantra.substrate.basin_map import (
    BASIN_INDEX,
    BASIN_LIST,
    COORD_BASIN,
    COORD_PHONEME_ATTRACTOR,
    basin_jaccard,
    basin_set,
)
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL

# =============================================================================
# DATA PATH
# =============================================================================

_DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
_LEXICON_PATH: Final[Path] = _DATA_DIR / "rama_lexicon.json"


# =============================================================================
# WORD RECORD (lightweight, no WordEntry dependency)
# =============================================================================

class LexiconWord:
    """A word from the RAMA Lexicon with pre-computed 4D properties."""

    __slots__ = (
        "sanskrit", "meanings", "coords", "packed_hex",
        "first_coord", "element_walk", "varga_walk",
        "shruti_pattern", "harmonic_walk", "basin_walk",
        "phoneme_attractor_walk",
    )

    def __init__(
        self,
        sanskrit: str,
        meanings: Tuple[str, ...],
        coords: Tuple[int, ...],
        packed_hex: str,
    ):
        self.sanskrit = sanskrit
        self.meanings = meanings
        self.coords = coords
        self.packed_hex = packed_hex

        # Pre-computed 4D properties (computed ONCE at index build time)
        self.first_coord = coords[0] if coords else -1
        self.element_walk = tuple(COORD_ELEMENT[c] for c in coords)
        self.varga_walk = tuple(COORD_VARGA[c] for c in coords)
        self.shruti_pattern = tuple(IS_SHRUTI[c] for c in coords)
        self.harmonic_walk = tuple(COORD_HARMONIC[c] for c in coords)
        self.basin_walk = tuple(COORD_BASIN[c] for c in coords)
        self.phoneme_attractor_walk = tuple(COORD_PHONEME_ATTRACTOR[c] for c in coords)

    @property
    def first_element(self) -> int:
        """Element of the first phoneme."""
        return self.element_walk[0] if self.element_walk else -1

    @property
    def basin_set(self) -> FrozenSet[int]:
        """Unique basins touched by this word."""
        return frozenset(self.basin_walk)

    @property
    def first_meaning(self) -> str:
        """Primary English meaning."""
        return self.meanings[0] if self.meanings else ""

    def __repr__(self) -> str:
        return f"LexiconWord({self.sanskrit!r}, {self.first_meaning!r})"


# =============================================================================
# SEMANTIC INDEX
# =============================================================================

class SemanticIndex:
    """
    Multi-dimensional reverse index over the RAMA Lexicon.

    Indices:
        by_first_coord[c]     → words starting at RAMA position c
        by_first_element[e]   → words starting with element e
        by_first_varga[v]     → words starting with varga v
        by_first_shruti[bool] → words starting with shruti/nakshatra
        by_harmonic_target[h] → words whose first phoneme dissolves to h
        by_meaning_word[w]    → words whose English meaning contains w

    All indices are built lazily and cached.
    """

    def __init__(self) -> None:
        self._words: Optional[Tuple[LexiconWord, ...]] = None
        self._by_first_coord: Optional[Dict[int, List[LexiconWord]]] = None
        self._by_first_element: Optional[Dict[int, List[LexiconWord]]] = None
        self._by_first_varga: Optional[Dict[int, List[LexiconWord]]] = None
        self._by_first_shruti: Optional[Dict[bool, List[LexiconWord]]] = None
        self._by_harmonic_target: Optional[Dict[int, List[LexiconWord]]] = None
        self._by_meaning_word: Optional[Dict[str, List[LexiconWord]]] = None
        self._by_basin: Optional[Dict[int, List[LexiconWord]]] = None

    # =========================================================================
    # LOADING
    # =========================================================================

    def _ensure_loaded(self) -> None:
        """Load and index the lexicon on first access."""
        if self._words is not None:
            return

        with open(_LEXICON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        vocab = data["vocabulary"]
        words = []

        for packed_hex, entry in vocab.items():
            coords = tuple(entry.get("coords", []))
            if not coords:
                continue
            # Validate coords are in range
            if any(c < 0 or c >= VARNAMALA_TOTAL for c in coords):
                continue

            words.append(LexiconWord(
                sanskrit=entry["word"],
                meanings=tuple(entry.get("meanings", [])),
                coords=coords,
                packed_hex=packed_hex,
            ))

        self._words = tuple(words)
        self._build_indices()

    def _build_indices(self) -> None:
        """Build all reverse indices."""
        assert self._words is not None

        by_coord: Dict[int, List[LexiconWord]] = defaultdict(list)
        by_elem: Dict[int, List[LexiconWord]] = defaultdict(list)
        by_varga: Dict[int, List[LexiconWord]] = defaultdict(list)
        by_shruti: Dict[bool, List[LexiconWord]] = defaultdict(list)
        by_harmonic: Dict[int, List[LexiconWord]] = defaultdict(list)
        by_meaning: Dict[str, List[LexiconWord]] = defaultdict(list)
        by_basin: Dict[int, List[LexiconWord]] = defaultdict(list)

        for w in self._words:
            if w.first_coord < 0:
                continue

            by_coord[w.first_coord].append(w)
            by_elem[w.first_element].append(w)
            by_varga[w.varga_walk[0]].append(w)
            by_shruti[w.shruti_pattern[0]].append(w)
            by_harmonic[w.harmonic_walk[0]].append(w)

            # Basin index: index by each unique basin touched
            for b in set(w.basin_walk):
                by_basin[b].append(w)

            # Meaning index: split English meanings into individual words
            for meaning in w.meanings:
                for token in meaning.lower().split():
                    # Strip punctuation
                    clean = token.strip(".,;:!?()[]'\"")
                    if len(clean) >= 3:  # Skip tiny words
                        by_meaning[clean].append(w)

        self._by_first_coord = dict(by_coord)
        self._by_first_element = dict(by_elem)
        self._by_first_varga = dict(by_varga)
        self._by_first_shruti = dict(by_shruti)
        self._by_harmonic_target = dict(by_harmonic)
        self._by_meaning_word = dict(by_meaning)
        self._by_basin = dict(by_basin)

    # =========================================================================
    # QUERIES
    # =========================================================================

    @property
    def words(self) -> Tuple[LexiconWord, ...]:
        """All indexed words."""
        self._ensure_loaded()
        return self._words  # type: ignore

    def by_rama_position(self, coord: int) -> List[LexiconWord]:
        """All words starting at a specific RAMA coordinate (0-48)."""
        self._ensure_loaded()
        return self._by_first_coord.get(coord, [])  # type: ignore

    def by_element(self, element: int) -> List[LexiconWord]:
        """All words starting with a specific element (0-4: akasha..prithvi)."""
        self._ensure_loaded()
        return self._by_first_element.get(element, [])  # type: ignore

    def by_element_name(self, name: str) -> List[LexiconWord]:
        """All words starting with a named element ('akasha', 'vayu', etc.)."""
        try:
            idx = ELEMENT_NAMES.index(name)
        except ValueError:
            return []
        return self.by_element(idx)

    def by_varga(self, varga: int) -> List[LexiconWord]:
        """All words starting with a specific varga (0=svara, 1=sparsha, 2=shesha)."""
        self._ensure_loaded()
        return self._by_first_varga.get(varga, [])  # type: ignore

    def by_shruti(self, is_shruti: bool = True) -> List[LexiconWord]:
        """All words starting with a shruti (True) or nakshatra (False) phoneme."""
        self._ensure_loaded()
        return self._by_first_shruti.get(is_shruti, [])  # type: ignore

    def by_harmonic_target(self, target: int) -> List[LexiconWord]:
        """All words whose first phoneme dissolves to target position."""
        self._ensure_loaded()
        return self._by_harmonic_target.get(target, [])  # type: ignore

    def by_meaning(self, english_word: str) -> List[LexiconWord]:
        """All words whose English meaning contains the given word."""
        self._ensure_loaded()
        return self._by_meaning_word.get(english_word.lower(), [])  # type: ignore

    def by_basin(self, basin: int) -> List[LexiconWord]:
        """All words touching a specific attractor basin."""
        self._ensure_loaded()
        return self._by_basin.get(basin, [])  # type: ignore

    def by_basin_set(self, basins: FrozenSet[int]) -> List[LexiconWord]:
        """All words whose basin set intersects with the given basins."""
        self._ensure_loaded()
        result_ids: set = set()
        result: List[LexiconWord] = []
        for b in basins:
            for w in self.by_basin(b):
                wid = id(w)
                if wid not in result_ids:
                    result_ids.add(wid)
                    result.append(w)
        return result

    def by_4d_query(
        self,
        element: Optional[int] = None,
        varga: Optional[int] = None,
        is_shruti: Optional[bool] = None,
        harmonic_target: Optional[int] = None,
    ) -> List[LexiconWord]:
        """
        Multi-dimensional query: intersect multiple constraints.

        Returns words matching ALL specified criteria.
        """
        self._ensure_loaded()

        # Start with all words, then intersect
        candidates: Optional[set] = None

        if element is not None:
            s = set(id(w) for w in self.by_element(element))
            candidates = s if candidates is None else candidates & s

        if varga is not None:
            s = set(id(w) for w in self.by_varga(varga))
            candidates = s if candidates is None else candidates & s

        if is_shruti is not None:
            s = set(id(w) for w in self.by_shruti(is_shruti))
            candidates = s if candidates is None else candidates & s

        if harmonic_target is not None:
            s = set(id(w) for w in self.by_harmonic_target(harmonic_target))
            candidates = s if candidates is None else candidates & s

        if candidates is None:
            return list(self._words)  # type: ignore

        # Rebuild list preserving order
        id_set = candidates
        return [w for w in self._words if id(w) in id_set]  # type: ignore

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def stats(self) -> Dict:
        """Index statistics."""
        self._ensure_loaded()
        return {
            "total_words": len(self._words),  # type: ignore
            "rama_positions_covered": len(self._by_first_coord),  # type: ignore
            "elements_covered": len(self._by_first_element),  # type: ignore
            "meaning_tokens": len(self._by_meaning_word),  # type: ignore
            "basins_indexed": len(self._by_basin),  # type: ignore
            "shruti_words": len(self.by_shruti(True)),
            "nakshatra_words": len(self.by_shruti(False)),
        }


# =============================================================================
# SINGLETON (lazy)
# =============================================================================

_INDEX: Optional[SemanticIndex] = None


def get_index() -> SemanticIndex:
    """Get or create the global SemanticIndex singleton."""
    global _INDEX
    if _INDEX is None:
        _INDEX = SemanticIndex()
    return _INDEX


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def words_at_position(coord: int) -> List[LexiconWord]:
    """All Gita words starting at RAMA position coord."""
    return get_index().by_rama_position(coord)


def words_by_element(element_name: str) -> List[LexiconWord]:
    """All Gita words starting with the named element."""
    return get_index().by_element_name(element_name)


def words_by_meaning(english_word: str) -> List[LexiconWord]:
    """All Gita words whose meaning contains the English word."""
    return get_index().by_meaning(english_word)


def semantic_query(
    element: Optional[int] = None,
    varga: Optional[int] = None,
    is_shruti: Optional[bool] = None,
    harmonic_target: Optional[int] = None,
) -> List[LexiconWord]:
    """Multi-dimensional semantic query over the Gita vocabulary."""
    return get_index().by_4d_query(
        element=element, varga=varga,
        is_shruti=is_shruti, harmonic_target=harmonic_target,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "LexiconWord",
    "SemanticIndex",
    "get_index",
    "words_at_position",
    "words_by_element",
    "words_by_meaning",
    "semantic_query",
]
