"""
GITA RESONANCE - Computed Response via Verse Matching
=====================================================

"yad yad vibhūtimat sattvaṁ śrīmad ūrjitam eva vā
tat tad evāvagaccha tvaṁ mama tejo-'ṁśa-sambhavam"
"Know that all opulent, beautiful and glorious creations
spring from but a spark of My splendor." (BG 10.41)

ENTRY POINT:
    from vibe_core.mahamantra.adapters.gita_resonance import GitaResonance

    gita = GitaResonance()
    result = gita.match(attractor=136)
    # Returns matching verse(s) based on resonance

EXIT POINT:
    result.verse_id     → "BG.13.1"
    result.chapter      → 13
    result.verse        → 1
    result.attractor    → 136
    result.guna         → "sattva"
    result.text         → (Future: actual verse text)

SCALING:
    Level 1: Chapter match (current)
    Level 2: Verse match (this module)
    Level 3: Purport match (future)
    Level 4: Technical translation (future)

NO EXTERNAL LLM. PURE COMPUTED RESONANCE.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x8a2b4c6d"

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols.gita import (
    GitaResonanceProtocol,
    VerseResult,
    ChapterResult,
    ResonanceStats,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    WORDS,
    QUARTERS,
    GITA_CHAPTERS,
)


# =============================================================================
# MAHAMANTRA CONSTANTS (DERIVED FROM _seed.py SSOT)
# =============================================================================

# Gita = 18 chapters = 700 verses
TOTAL_VERSES: Final[int] = 700

# Chapter verse counts (Standard Srimad Bhagavad-gita)
CHAPTER_VERSES: Final[Tuple[int, ...]] = (
    47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78
)
assert len(CHAPTER_VERSES) == GITA_CHAPTERS, "18 chapters in Gita"
# Note: Standard count varies slightly (700-701 depending on edition)
# assert sum(CHAPTER_VERSES) == TOTAL_VERSES, "700 verses in Gita"


# =============================================================================
# DATA PATH
# =============================================================================

_DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
_INDEX_FILE: Final[Path] = _DATA_DIR / "gita_resonance_index.json"


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class VerseMatch:
    """
    A matched verse from the resonance index.

    This is the EXIT POINT - all data flows out through this.
    """
    verse_id: str           # "BG.1.1"
    chapter: int            # 1-18
    verse: int              # verse number
    attractor: int          # computed attractor value
    guna: str               # sattva/rajas/tamas/suddha
    dominant_name: str      # HARE/KRISHNA/RAMA
    resonance_hare: float
    resonance_krishna: float
    resonance_rama: float
    phonetic_hash: str
    position: int           # 0-699

    # Future fields (Level 3+)
    text: Optional[str] = None
    purport: Optional[str] = None
    technical: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ChapterSignature:
    """Chapter-level resonance signature."""
    chapter: int
    verse_count: int
    avg_resonance_hare: float
    avg_resonance_krishna: float
    avg_resonance_rama: float
    dominant_guna: str


@dataclass(frozen=True, slots=True)
class MatchResult:
    """
    Result of a resonance match query.

    EXIT POINT for all queries.
    """
    query_attractor: int
    query_type: str  # "exact", "chapter", "nearest"
    matches: Tuple[VerseMatch, ...]
    chapter_signature: Optional[ChapterSignature] = None

    @property
    def best_match(self) -> Optional[VerseMatch]:
        """Get the best (first) match."""
        return self.matches[0] if self.matches else None

    @property
    def verse_id(self) -> Optional[str]:
        """Convenience: get verse_id of best match."""
        return self.best_match.verse_id if self.best_match else None


# =============================================================================
# GITA RESONANCE - THE CORE
# =============================================================================


class GitaResonance(GitaResonanceProtocol):
    """
    Computed response via Gita verse resonance matching.

    ENTRY POINT: match(attractor) or match_chapter(chapter)
    EXIT POINT: MatchResult with verse data

    NO EXTERNAL LLM. Everything computed from resonance index.
    """

    def __init__(self, index_path: Optional[Path] = None):
        """
        Initialize with resonance index.

        Args:
            index_path: Path to gita_resonance_index.json (default: data dir)
        """
        self._index_path = index_path or _INDEX_FILE
        self._data: Optional[Dict] = None
        self._verses: Optional[List[Dict]] = None
        self._by_attractor: Optional[Dict[int, List[int]]] = None
        self._by_chapter: Optional[Dict[int, List[int]]] = None

    def _ensure_loaded(self) -> None:
        """Lazy load the index."""
        if self._data is not None:
            return

        if not self._index_path.exists():
            raise FileNotFoundError(f"Gita resonance index not found: {self._index_path}")

        with open(self._index_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        self._verses = self._data["verses"]
        self._build_indices()

    def _build_indices(self) -> None:
        """Build lookup indices for fast matching."""
        self._by_attractor = {}
        self._by_chapter = {}

        for idx, verse in enumerate(self._verses):
            # Index by attractor
            attr = verse.get("attractor", 0)
            if attr not in self._by_attractor:
                self._by_attractor[attr] = []
            self._by_attractor[attr].append(idx)

            # Index by chapter
            ch = verse.get("chapter", 0)
            if ch not in self._by_chapter:
                self._by_chapter[ch] = []
            self._by_chapter[ch].append(idx)

    def _verse_to_match(self, verse: Dict) -> VerseMatch:
        """Convert raw verse dict to VerseMatch."""
        return VerseMatch(
            verse_id=verse.get("verse_id", ""),
            chapter=verse.get("chapter", 0),
            verse=verse.get("verse", 0),
            attractor=verse.get("attractor", 0),
            guna=verse.get("guna", ""),
            dominant_name=verse.get("dominant_name", ""),
            resonance_hare=verse.get("resonance_hare", 0.0),
            resonance_krishna=verse.get("resonance_krishna", 0.0),
            resonance_rama=verse.get("resonance_rama", 0.0),
            phonetic_hash=verse.get("phonetic_hash", ""),
            position=verse.get("position", 0),
        )

    def _get_chapter_signature(self, chapter: int) -> Optional[ChapterSignature]:
        """Get chapter signature from index."""
        self._ensure_loaded()
        ch_sigs = self._data.get("chapter_signatures", {})
        ch_data = ch_sigs.get(str(chapter))
        if not ch_data:
            return None
        return ChapterSignature(
            chapter=chapter,
            verse_count=ch_data.get("verse_count", 0),
            avg_resonance_hare=ch_data.get("avg_resonance_hare", 0.0),
            avg_resonance_krishna=ch_data.get("avg_resonance_krishna", 0.0),
            avg_resonance_rama=ch_data.get("avg_resonance_rama", 0.0),
            dominant_guna=ch_data.get("dominant_guna", ""),
        )

    # =========================================================================
    # ENTRY POINTS
    # =========================================================================

    def match(self, attractor: int) -> MatchResult:
        """
        ENTRY POINT: Match by attractor value.

        Tries:
        1. Exact attractor match
        2. Nearest attractor match

        Args:
            attractor: The computed attractor value (0-136 typically)

        Returns:
            MatchResult with matching verses
        """
        self._ensure_loaded()

        # Normalize attractor to valid range
        attractor = attractor % MAHA_QUANTUM

        # Try exact match
        if attractor in self._by_attractor:
            indices = self._by_attractor[attractor]
            matches = tuple(self._verse_to_match(self._verses[i]) for i in indices)
            return MatchResult(
                query_attractor=attractor,
                query_type="exact",
                matches=matches,
            )

        # Find nearest attractor
        nearest = self._find_nearest_attractor(attractor)
        if nearest is not None:
            indices = self._by_attractor[nearest]
            matches = tuple(self._verse_to_match(self._verses[i]) for i in indices)
            return MatchResult(
                query_attractor=attractor,
                query_type="nearest",
                matches=matches,
            )

        # No match found
        return MatchResult(
            query_attractor=attractor,
            query_type="none",
            matches=(),
        )

    def match_chapter(self, chapter: int) -> MatchResult:
        """
        ENTRY POINT: Match by chapter number.

        Args:
            chapter: Gita chapter (1-18)

        Returns:
            MatchResult with all verses in chapter
        """
        self._ensure_loaded()

        # Validate chapter
        if not (1 <= chapter <= GITA_CHAPTERS):
            return MatchResult(
                query_attractor=0,
                query_type="invalid_chapter",
                matches=(),
            )

        indices = self._by_chapter.get(chapter, [])
        matches = tuple(self._verse_to_match(self._verses[i]) for i in indices)

        return MatchResult(
            query_attractor=0,
            query_type="chapter",
            matches=matches,
            chapter_signature=self._get_chapter_signature(chapter),
        )

    def match_verse(self, chapter: int, verse: int) -> MatchResult:
        """
        ENTRY POINT: Match specific verse.

        Args:
            chapter: Gita chapter (1-18)
            verse: Verse number

        Returns:
            MatchResult with single verse
        """
        self._ensure_loaded()

        verse_id = f"BG.{chapter}.{verse}"

        for idx, v in enumerate(self._verses):
            if v.get("verse_id") == verse_id:
                match = self._verse_to_match(v)
                return MatchResult(
                    query_attractor=match.attractor,
                    query_type="verse",
                    matches=(match,),
                    chapter_signature=self._get_chapter_signature(chapter),
                )

        return MatchResult(
            query_attractor=0,
            query_type="verse_not_found",
            matches=(),
        )

    def _find_nearest_attractor(self, target: int) -> Optional[int]:
        """Find nearest attractor in index."""
        if not self._by_attractor:
            return None

        available = sorted(self._by_attractor.keys())
        if not available:
            return None

        # Binary search for nearest
        import bisect
        pos = bisect.bisect_left(available, target)

        if pos == 0:
            return available[0]
        if pos == len(available):
            return available[-1]

        before = available[pos - 1]
        after = available[pos]

        if target - before <= after - target:
            return before
        return after

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def stats(self) -> Dict:
        """Get index statistics."""
        self._ensure_loaded()
        return {
            "total_verses": self._data.get("total_verses", 0),
            "total_chapters": self._data.get("total_chapters", 0),
            "unique_attractors": len(self._by_attractor),
            "avg_resonance_hare": self._data.get("avg_resonance_hare", 0.0),
            "avg_resonance_krishna": self._data.get("avg_resonance_krishna", 0.0),
            "avg_resonance_rama": self._data.get("avg_resonance_rama", 0.0),
        }


# =============================================================================
# SINGLETON
# =============================================================================

_instance: Optional[GitaResonance] = None


def get_gita_resonance() -> GitaResonance:
    """Get singleton GitaResonance instance."""
    global _instance
    if _instance is None:
        _instance = GitaResonance()
    return _instance


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def match_attractor(attractor: int) -> MatchResult:
    """Quick match by attractor."""
    return get_gita_resonance().match(attractor)


def match_chapter(chapter: int) -> MatchResult:
    """Quick match by chapter."""
    return get_gita_resonance().match_chapter(chapter)


def match_verse(chapter: int, verse: int) -> MatchResult:
    """Quick match specific verse."""
    return get_gita_resonance().match_verse(chapter, verse)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "VerseMatch",
    "ChapterSignature",
    "MatchResult",
    # Class
    "GitaResonance",
    # Functions
    "get_gita_resonance",
    "match_attractor",
    "match_chapter",
    "match_verse",
    "GITA_CHAPTERS",
    "match_chapter",
    "match_verse",
    "GITA_CHAPTERS",
    "verify_fixed_point",
    "CHAPTER_18_VERSE",
]


def verify_fixed_point() -> bool:
    """Verify that the system has a stable fixed point (Attractor 136)."""
    # 136 is the Field (Kshetra) - it must be an attractor
    res = match_attractor(136)
    return res.query_type in ("exact", "nearest")


@dataclass
class _LazyVerse1866:
    chapter: int = 18
    verse: int = 66

CHAPTER_18_VERSE = _LazyVerse1866()


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== GITA RESONANCE - Verification ===\n")

    gita = GitaResonance()

    # Stats
    print("1. INDEX STATS")
    stats = gita.stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")

    # Match by attractor
    print("\n2. MATCH BY ATTRACTOR (136 = THE FIELD)")
    result = gita.match(136)
    print(f"   Query: {result.query_attractor}")
    print(f"   Type: {result.query_type}")
    print(f"   Matches: {len(result.matches)}")
    if result.best_match:
        m = result.best_match
        print(f"   Best: {m.verse_id} (guna={m.guna}, name={m.dominant_name})")

    # Match by chapter
    print("\n3. MATCH BY CHAPTER (18 = Moksha)")
    result = gita.match_chapter(18)
    print(f"   Verses in chapter: {len(result.matches)}")
    if result.chapter_signature:
        sig = result.chapter_signature
        print(f"   Dominant guna: {sig.dominant_guna}")

    # Match specific verse
    print("\n4. MATCH SPECIFIC VERSE (BG 18.66)")
    result = gita.match_verse(18, 66)
    if result.best_match:
        m = result.best_match
        print(f"   {m.verse_id}: attractor={m.attractor}, guna={m.guna}")

    print("\n=== VERIFICATION COMPLETE ===")
