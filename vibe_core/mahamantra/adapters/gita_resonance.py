"""
GITA RESONANCE - Computed Response via Verse Matching
=====================================================

"yad yad vibhūtimat sattvaṁ śrīmad ūrjitam eva vā
tat tad evāvagaccha tvaṁ mama tejo-'ṁśa-sambhavam"
"Know that all opulent, beautiful and glorious creations
spring from but a spark of My splendor." (BG 10.41)

NEUTRAL ARCHITECTURE:
    Source: rama_lexicon.json (the WAV — raw RAMA coordinates, algorithm-independent)
    Compute: MahaResonator (the EQ — attractor/guna/resonance, runtime-dependent)

    Changing the algorithm changes the routing. The data stays.

ENTRY POINT:
    from vibe_core.mahamantra.adapters.gita_resonance import GitaResonance

    gita = GitaResonance()
    result = gita.match(attractor=88)

EXIT POINT:
    result.verse_id     → "BG.13.1"
    result.chapter      → 13
    result.verse        → 1
    result.attractor    → 88
    result.guna         → "sattva"

NO EXTERNAL LLM. PURE COMPUTED RESONANCE.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x5ad7f6c5"

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    CHAPTER_VERSES,
    GITA_CHAPTERS,
    MAHA_QUANTUM,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.protocols.gita import (
    ChapterResult,
    GitaResonanceProtocol,
    ResonanceStats,
    VerseResult,
)

# =============================================================================
# MAHAMANTRA CONSTANTS (DERIVED FROM _seed.py SSOT)
# =============================================================================

TOTAL_VERSES: Final[int] = 700

assert len(CHAPTER_VERSES) == GITA_CHAPTERS, "18 chapters in Gita"
assert sum(CHAPTER_VERSES) == TOTAL_VERSES, "Prabhupada's Gita = 700 verses"

# =============================================================================
# DATA PATH — rama_lexicon.json IS the neutral source
# =============================================================================

_DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
_LEXICON_PATH: Final[Path] = _DATA_DIR / "rama_lexicon.json"

# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class VerseMatch:
    """A matched verse — computed from RAMA coordinates at load time."""

    verse_id: str  # "BG.1.1"
    chapter: int  # 1-18
    verse: int  # verse number
    attractor: int  # computed by current MahaResonator
    guna: str  # sattva/rajas/tamas (from SHRUTI ratio)
    dominant_name: str  # HARE/KRISHNA/RAMA (from VARGA partition)
    resonance_hare: float
    resonance_krishna: float
    resonance_rama: float
    phonetic_hash: str
    position: int  # 0-699

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
    """Result of a resonance match query."""

    query_attractor: int
    query_type: str  # "exact", "chapter", "nearest"
    matches: Tuple[VerseMatch, ...]
    chapter_signature: Optional[ChapterSignature] = None

    @property
    def best_match(self) -> Optional[VerseMatch]:
        return self.matches[0] if self.matches else None

    @property
    def verse_id(self) -> Optional[str]:
        return self.best_match.verse_id if self.best_match else None


# =============================================================================
# VERSE COMPUTATION — Pure functions from RAMA coordinates
# =============================================================================


def _verse_coords(verse_data: dict, vocab: dict) -> Tuple[int, ...]:
    """Extract flat RAMA coordinate sequence from a verse."""
    coords: List[int] = []
    for w in verse_data.get("words", []):
        entry = vocab.get(w["packed"])
        if entry:
            coords.extend(entry["coords"])
    return tuple(coords)


def _compute_resonance(coords: Tuple[int, ...]) -> Tuple[float, float, float]:
    """H/K/R resonance from VARGA partition. Algorithm-independent."""
    from vibe_core.mahamantra.substrate.pancha_walk import COORD_VARGA

    if not coords:
        return (0.0, 0.0, 0.0)
    counts = Counter(COORD_VARGA[c] for c in coords)
    total = len(coords)
    return (
        round(counts.get(0, 0) / total, 4),  # svara → HARE
        round(counts.get(1, 0) / total, 4),  # sparsha → KRISHNA
        round(counts.get(2, 0) / total, 4),  # shesha → RAMA
    )


def _compute_guna(coords: Tuple[int, ...], baseline: float, half_std: float) -> str:
    """Guna from SHRUTI/NAKSHATRA ratio. Algorithm-independent."""
    from vibe_core.mahamantra.substrate.pancha_walk import IS_SHRUTI

    if not coords:
        return "rajas"
    ratio = sum(1 for c in coords if IS_SHRUTI[c]) / len(coords)
    if ratio > baseline + half_std:
        return "sattva"
    if ratio < baseline - half_std:
        return "tamas"
    return "rajas"


def _compute_dominant(h: float, k: float, r: float) -> str:
    """Dominant holy name from resonance values."""
    if h >= k and h >= r:
        return "HARE"
    if k >= h and k >= r:
        return "KRISHNA"
    return "RAMA"


def _coord_seed(coords: Tuple[int, ...], verse_id: str) -> int:
    """Deterministic 32-bit seed. verse_id breaks clone symmetry."""
    key = f"{coords}:{verse_id}"
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:4], "big")


def _phonetic_hash(coords: Tuple[int, ...], verse_id: str) -> str:
    """Stable hash from 4D full_signature + verse identity."""
    from vibe_core.mahamantra.substrate.pancha_walk import full_signature

    if not coords:
        return "0" * 16
    sig = full_signature(coords)
    return hashlib.sha256(f"{sig}:{verse_id}".encode("utf-8")).hexdigest()[:16]


# =============================================================================
# GITA RESONANCE — NEUTRAL ARCHITECTURE
# =============================================================================


class GitaResonance(GitaResonanceProtocol):
    """
    Computed response via Gita verse resonance matching.

    Source: rama_lexicon.json (neutral RAMA coordinates)
    Compute: MahaResonator (current algorithm, applied at load time)

    ENTRY POINT: match(attractor) or match_chapter(chapter)
    EXIT POINT: MatchResult with verse data
    """

    def __init__(self, lexicon_path: Optional[Path] = None):
        self._lexicon_path = lexicon_path or _LEXICON_PATH
        self._verses: Optional[List[VerseMatch]] = None
        self._by_attractor: Optional[Dict[int, List[int]]] = None
        self._by_chapter: Optional[Dict[int, List[int]]] = None
        self._chapter_sigs: Optional[Dict[int, ChapterSignature]] = None
        self._stats: Optional[Dict] = None

    def _ensure_loaded(self) -> None:
        """Lazy load lexicon and compute all verse metadata."""
        if self._verses is not None:
            return

        if not self._lexicon_path.exists():
            raise FileNotFoundError(f"RAMA lexicon not found: {self._lexicon_path}")

        with open(self._lexicon_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        vocab = data["vocabulary"]
        verses_raw = data["verses"]

        # Build primary coords for grouped verse inheritance
        primary_words: Dict[str, list] = {}
        for v in verses_raw:
            if v.get("words") and "grouped_with" not in v:
                primary_words[v["ref"]] = v["words"]

        # Pass 1: compute SHRUTI baseline from all verse coords
        import statistics as st

        from vibe_core.mahamantra.substrate.pancha_walk import IS_SHRUTI

        shruti_ratios: List[float] = []
        all_coords: List[Tuple[int, ...]] = []

        for v in verses_raw:
            words = v.get("words") or primary_words.get(v.get("grouped_with", ""), [])
            v_data = dict(v, words=words)
            coords = _verse_coords(v_data, vocab)
            all_coords.append(coords)
            if coords:
                shruti_ratios.append(sum(1 for c in coords if IS_SHRUTI[c]) / len(coords))

        baseline = st.mean(shruti_ratios) if shruti_ratios else 0.366
        half_std = st.stdev(shruti_ratios) / 2 if len(shruti_ratios) > 1 else 0.033

        # Pass 2: compute per-verse metadata using current MahaResonator
        from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator

        resonator = MahaResonator()
        self._verses = []
        self._by_attractor = {}
        self._by_chapter = {}
        chapter_data: Dict[int, List[VerseMatch]] = {}

        for idx, v in enumerate(verses_raw):
            ref = v["ref"]
            chapter = v["chapter"]
            verse_num = v["verse"]
            coords = all_coords[idx]

            # Resonance from VARGA partition
            res_h, res_k, res_r = _compute_resonance(coords)
            dominant = _compute_dominant(res_h, res_k, res_r)

            # Guna from SHRUTI ratio
            guna = _compute_guna(coords, baseline, half_std)

            # Attractor from current algorithm
            seed = _coord_seed(coords, ref)
            attractor = resonator.find_attractor(seed).attractor

            # Phonetic identity
            phash = _phonetic_hash(coords, ref)

            vm = VerseMatch(
                verse_id=ref,
                chapter=chapter,
                verse=verse_num,
                attractor=attractor,
                guna=guna,
                dominant_name=dominant,
                resonance_hare=res_h,
                resonance_krishna=res_k,
                resonance_rama=res_r,
                phonetic_hash=phash,
                position=idx,
            )
            self._verses.append(vm)

            # Index by attractor
            self._by_attractor.setdefault(attractor, []).append(idx)

            # Index by chapter
            self._by_chapter.setdefault(chapter, []).append(idx)

            # Collect for chapter signatures
            chapter_data.setdefault(chapter, []).append(vm)

        # Build chapter signatures
        self._chapter_sigs = {}
        for ch, vms in chapter_data.items():
            n = len(vms)
            guna_counts = Counter(vm.guna for vm in vms)
            self._chapter_sigs[ch] = ChapterSignature(
                chapter=ch,
                verse_count=n,
                avg_resonance_hare=round(sum(vm.resonance_hare for vm in vms) / n, 4),
                avg_resonance_krishna=round(sum(vm.resonance_krishna for vm in vms) / n, 4),
                avg_resonance_rama=round(sum(vm.resonance_rama for vm in vms) / n, 4),
                dominant_guna=max(guna_counts, key=guna_counts.get),
            )

        # Compute stats
        all_vms = self._verses
        n = len(all_vms)
        self._stats = {
            "total_verses": n,
            "total_chapters": len(chapter_data),
            "unique_attractors": len(self._by_attractor),
            "avg_resonance_hare": round(sum(vm.resonance_hare for vm in all_vms) / n, 4),
            "avg_resonance_krishna": round(sum(vm.resonance_krishna for vm in all_vms) / n, 4),
            "avg_resonance_rama": round(sum(vm.resonance_rama for vm in all_vms) / n, 4),
        }

    # =========================================================================
    # ENTRY POINTS
    # =========================================================================

    def match(self, attractor: int) -> MatchResult:
        """Match by attractor value."""
        self._ensure_loaded()
        attractor = attractor % MAHA_QUANTUM

        # Exact match
        if attractor in self._by_attractor:
            indices = self._by_attractor[attractor]
            matches = tuple(self._verses[i] for i in indices)
            return MatchResult(
                query_attractor=attractor,
                query_type="exact",
                matches=matches,
            )

        # Nearest attractor
        nearest = self._find_nearest_attractor(attractor)
        if nearest is not None:
            indices = self._by_attractor[nearest]
            matches = tuple(self._verses[i] for i in indices)
            return MatchResult(
                query_attractor=attractor,
                query_type="nearest",
                matches=matches,
            )

        return MatchResult(query_attractor=attractor, query_type="none", matches=())

    def match_chapter(self, chapter: int) -> MatchResult:
        """Match by chapter number."""
        self._ensure_loaded()

        if not (1 <= chapter <= GITA_CHAPTERS):
            return MatchResult(query_attractor=0, query_type="invalid_chapter", matches=())

        indices = self._by_chapter.get(chapter, [])
        matches = tuple(self._verses[i] for i in indices)
        return MatchResult(
            query_attractor=0,
            query_type="chapter",
            matches=matches,
            chapter_signature=self._chapter_sigs.get(chapter),
        )

    def match_verse(self, chapter: int, verse: int) -> MatchResult:
        """Match specific verse."""
        self._ensure_loaded()
        verse_id = f"BG.{chapter}.{verse}"

        for vm in self._verses:
            if vm.verse_id == verse_id:
                return MatchResult(
                    query_attractor=vm.attractor,
                    query_type="verse",
                    matches=(vm,),
                    chapter_signature=self._chapter_sigs.get(chapter),
                )

        return MatchResult(query_attractor=0, query_type="verse_not_found", matches=())

    def match_trajectory(self, seed: int) -> MatchResult:
        """Match based on trajectory — seed → MahaResonator → attractor → verses."""
        self._ensure_loaded()
        from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator

        attractor = MahaResonator().find_attractor(seed).attractor
        return self.match(attractor)

    def _find_nearest_attractor(self, target: int) -> Optional[int]:
        """Find nearest attractor by distance."""
        if not self._by_attractor:
            return None

        import bisect

        available = sorted(self._by_attractor.keys())
        if not available:
            return None

        pos = bisect.bisect_left(available, target)
        if pos == 0:
            return available[0]
        if pos == len(available):
            return available[-1]

        before, after = available[pos - 1], available[pos]
        return before if target - before <= after - target else after

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def stats(self) -> Dict:
        """Get computed index statistics."""
        self._ensure_loaded()
        return dict(self._stats)


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


def match_trajectory(seed: int) -> MatchResult:
    """Quick trajectory-based match."""
    return get_gita_resonance().match_trajectory(seed)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "VerseMatch",
    "ChapterSignature",
    "MatchResult",
    "GitaResonance",
    "get_gita_resonance",
    "match_attractor",
    "match_chapter",
    "match_verse",
    "GITA_CHAPTERS",
    "verify_fixed_point",
    "CHAPTER_18_VERSE",
]


def verify_fixed_point() -> bool:
    """Verify that the system has a stable attractor structure."""
    res = get_gita_resonance().stats()
    return res["unique_attractors"] > 0 and res["total_verses"] == TOTAL_VERSES


@dataclass
class _LazyVerse1866:
    chapter: int = 18
    verse: int = 66


CHAPTER_18_VERSE = _LazyVerse1866()


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== GITA RESONANCE - Neutral Architecture ===\n")

    gita = GitaResonance()

    # Stats
    print("1. INDEX STATS (computed from rama_lexicon.json)")
    stats = gita.stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")

    # Attractor distribution
    print("\n2. ATTRACTOR BASINS")
    gita._ensure_loaded()
    for attr in sorted(gita._by_attractor.keys()):
        count = len(gita._by_attractor[attr])
        print(f"   attractor {attr:3d}: {count:3d} verses ({count / 700 * 100:.1f}%)")

    # Match by attractor
    print("\n3. MATCH BY ATTRACTOR")
    for attr in sorted(gita._by_attractor.keys()):
        result = gita.match(attr)
        m = result.best_match
        print(f"   {attr:3d} → {m.verse_id} (guna={m.guna}, name={m.dominant_name})")

    # Match specific verse
    print("\n4. BG 18.66 (Fixed Point)")
    result = gita.match_verse(18, 66)
    if result.best_match:
        m = result.best_match
        print(f"   {m.verse_id}: attractor={m.attractor}, guna={m.guna}, name={m.dominant_name}")
        print(f"   H={m.resonance_hare} K={m.resonance_krishna} R={m.resonance_rama}")

    # Guna distribution
    print("\n5. GUNA DISTRIBUTION")
    guna_counts = Counter(vm.guna for vm in gita._verses)
    for g in ("sattva", "rajas", "tamas"):
        c = guna_counts.get(g, 0)
        print(f"   {g:8s}: {c:3d} ({c / 700 * 100:.1f}%)")

    # Dominant name
    print("\n6. DOMINANT NAME")
    name_counts = Counter(vm.dominant_name for vm in gita._verses)
    for n in ("HARE", "KRISHNA", "RAMA"):
        c = name_counts.get(n, 0)
        print(f"   {n:8s}: {c:3d} ({c / 700 * 100:.1f}%)")

    print("\n=== VERIFICATION COMPLETE ===")
