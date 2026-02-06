#!/usr/bin/env python3
"""
RAMA-NATIVE VERSE RESONANCE
============================

Recomputes gita_resonance_index.json entirely from RAMA 4D coordinates.

The previous index was computed from PhoneticClass (12 categories) applied
to combined Sanskrit+English text. Result: all resonance values ~0.140,
zero differentiation between verses. The guna was keyword-matched on
English translations (copyrighted text).

This replaces it with:

1. H/K/R RESONANCE (from VARGA partition):
   - Each phoneme has VARGA ∈ {svara(0), sparsha(1), shesha(2)}
   - svara → H (Hare = prāṇa, breath = vowels)
   - sparsha → K (Krishna = all-pervading, 25 stop consonants)
   - shesha → R (Rama = remaining, semivowels + sibilants)
   - Three values sum to 1.0 (exact partition, not Levenshtein noise)

2. GUNA (from SHRUTI/NAKSHATRA partition):
   - SHRUTI = R²-residues mod 49 = 22 microtones (illuminated, R-reachable)
   - NAKSHATRA = complement = 27 lunar mansions (not R-reachable)
   - shruti_ratio determines guna classification

3. ATTRACTOR (from RAMA coordinate hash):
   - Deterministic seed from Sanskrit phonetics only (no English)
   - MahaResonator → attractor in mod-137 space

4. ELEMENT BALANCE (bonus — 5D distribution per verse):
   - PANCHA element histogram for each verse
   - Dominant element = verse's elemental character

Data source: rama_lexicon.json (45,815 phonemes, 4127 words, 700 verses)
NO copyrighted text. NO vedabase.db. PURE Sanskrit coordinates.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    MAHA_QUANTUM,
    WORDS,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_VARGA,
    IS_SHRUTI,
    Element,
    element_histogram,
)

# =============================================================================
# PATHS
# =============================================================================

_DATA_DIR: Final = Path(__file__).resolve().parents[1] / "data"
_LEXICON_PATH: Final = _DATA_DIR / "rama_lexicon.json"
_OUTPUT_PATH: Final = _DATA_DIR / "gita_resonance_index.json"

# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass
class VerseResonance:
    """RAMA-native verse resonance signature."""

    verse_id: str
    chapter: int
    verse: str

    # H/K/R resonance from VARGA partition (sum = 1.0)
    resonance_hare: float  # svara ratio
    resonance_krishna: float  # sparsha ratio
    resonance_rama: float  # shesha ratio
    dominant_name: str  # max of H/K/R

    # Phonetic identity
    phonetic_hash: str  # SHA256 of full 4D signature
    phonetic_length: int  # total phonemes in verse

    # Guna from SHRUTI/NAKSHATRA
    guna: str  # sattva/rajas/tamas
    guna_seed: int  # deterministic seed from RAMA coords

    # Attractor in mod-137 space
    attractor: int
    position: int  # guna_seed % WORDS

    # Element balance (bonus)
    element_histogram: list[int]  # [akasha, vayu, agni, jala, prithvi]
    dominant_element: str


# =============================================================================
# CORE COMPUTATION
# =============================================================================


def _verse_coords(verse_data: dict, vocab: dict) -> tuple[int, ...]:
    """Collect all RAMA coordinates for a verse from its words."""
    coords: list[int] = []
    for w in verse_data.get("words", []):
        packed_hex = w["packed"]
        entry = vocab.get(packed_hex)
        if entry:
            coords.extend(entry["coords"])
    return tuple(coords)


def _varga_resonance(coords: tuple[int, ...]) -> tuple[float, float, float]:
    """Compute H/K/R resonance from VARGA partition."""
    if not coords:
        return (0.0, 0.0, 0.0)
    counts = Counter(COORD_VARGA[c] for c in coords)
    total = len(coords)
    return (
        counts.get(0, 0) / total,  # svara → H
        counts.get(1, 0) / total,  # sparsha → K
        counts.get(2, 0) / total,  # shesha → R
    )


def _guna_from_shruti(coords: tuple[int, ...], baseline: float, half_std: float) -> str:
    """
    Classify guna from SHRUTI/NAKSHATRA ratio.

    SHRUTI (R²-residues mod 49): phonemes reachable by R(v²) operation.
    Uses EMPIRICAL baseline from actual Gita Sanskrit (not theoretical 22/49).

    Empirical: mean=0.366, stdev=0.065 across 651 verses.
    Threshold: mean ± stdev/2 divides into three roughly equal bands.

    High SHRUTI → sattva (illuminated, R-reachable)
    Balanced    → rajas (active)
    Low SHRUTI  → tamas (obscured, not R-reachable)
    """
    if not coords:
        return "rajas"  # empty = neutral
    shruti_count = sum(1 for c in coords if IS_SHRUTI[c])
    ratio = shruti_count / len(coords)
    if ratio > baseline + half_std:
        return "sattva"
    elif ratio < baseline - half_std:
        return "tamas"
    else:
        return "rajas"


def _coord_seed(coords: tuple[int, ...], verse_id: str = "") -> int:
    """Deterministic 32-bit seed from RAMA coordinates + verse identity.

    verse_id breaks clone symmetry: grouped verses sharing the same
    word-for-word (= same coords) get different seeds → different attractors.
    """
    key = f"{coords}:{verse_id}" if verse_id else str(coords)
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")


def _full_sig_hash(coords: tuple[int, ...], verse_id: str = "") -> str:
    """SHA256 of concatenated 4D signatures + verse identity."""
    from vibe_core.mahamantra.substrate.pancha_walk import full_signature

    sig = full_signature(coords)
    key = f"{sig}:{verse_id}" if verse_id else sig
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _dominant_name(h: float, k: float, r: float) -> str:
    """Determine dominant holy name."""
    if h >= k and h >= r:
        return "HARE"
    if k >= h and k >= r:
        return "KRISHNA"
    return "RAMA"


_ELEMENT_NAMES = ("akasha", "vayu", "agni", "jala", "prithvi")


def compute_verse_resonance(
    verse_data: dict,
    vocab: dict,
    resonator,
    baseline: float,
    half_std: float,
) -> VerseResonance:
    """Compute RAMA-native resonance for a single verse."""
    ref = verse_data["ref"]
    chapter = verse_data["chapter"]
    verse = verse_data["verse"]

    # Get all RAMA coordinates
    coords = _verse_coords(verse_data, vocab)

    # H/K/R from VARGA
    res_h, res_k, res_r = _varga_resonance(coords)
    dominant = _dominant_name(res_h, res_k, res_r)

    # Phonetic identity
    phon_hash = _full_sig_hash(coords) if coords else "0" * 16
    phon_len = len(coords)

    # Guna from SHRUTI/NAKSHATRA
    guna = _guna_from_shruti(coords, baseline, half_std)

    # Attractor
    seed = _coord_seed(coords)
    attractor = resonator.find_attractor(seed).attractor
    position = seed % WORDS

    # Element balance
    hist = list(element_histogram(coords)) if coords else [0] * 5
    dom_elem = _ELEMENT_NAMES[hist.index(max(hist))] if coords else "akasha"

    return VerseResonance(
        verse_id=ref,
        chapter=chapter,
        verse=str(verse),
        resonance_hare=round(res_h, 6),
        resonance_krishna=round(res_k, 6),
        resonance_rama=round(res_r, 6),
        dominant_name=dominant,
        phonetic_hash=phon_hash,
        phonetic_length=phon_len,
        guna=guna,
        guna_seed=seed,
        attractor=attractor,
        position=position,
        element_histogram=hist,
        dominant_element=dom_elem,
    )


# =============================================================================
# FULL EXTRACTION
# =============================================================================


def extract_rama_resonance(lexicon_path: Path = _LEXICON_PATH) -> dict:
    """
    Extract RAMA-native resonance index from rama_lexicon.json.

    Handles grouped verses: secondary verses in multi-verse groups
    (e.g. "Texts 16-18") inherit coords from the primary verse.

    Returns the complete index ready for JSON serialization.
    """
    import statistics

    from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator

    # Load lexicon
    with open(lexicon_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vocab = data["vocabulary"]
    verses_raw = data["verses"]
    resonator = MahaResonator(mod_space=MAHA_QUANTUM)

    # Build grouped_with map and primary verse index for inheritance
    primary_coords: dict[str, tuple[int, ...]] = {}
    for v in verses_raw:
        if v.get("words") and "grouped_with" not in v:
            primary_coords[v["ref"]] = _verse_coords(v, vocab)

    # First pass: compute SHRUTI ratios to determine empirical baseline
    shruti_ratios: list[float] = []
    for v in verses_raw:
        ref = v["ref"]
        grouped_with = v.get("grouped_with")
        if grouped_with:
            coords = primary_coords.get(grouped_with, ())
        else:
            coords = _verse_coords(v, vocab)
        if coords:
            shruti = sum(1 for c in coords if IS_SHRUTI[c])
            shruti_ratios.append(shruti / len(coords))

    baseline = statistics.mean(shruti_ratios) if shruti_ratios else 0.366
    half_std = statistics.stdev(shruti_ratios) / 2 if len(shruti_ratios) > 1 else 0.033

    # Second pass: compute per-verse resonance
    verses: list[dict] = []
    chapter_data: dict[int, list[VerseResonance]] = {}

    for v in verses_raw:
        # For grouped verses, temporarily inject primary's words
        grouped_with = v.get("grouped_with")
        if grouped_with and not v.get("words"):
            # Find the primary verse and use its coords
            primary = next((p for p in verses_raw if p["ref"] == grouped_with), None)
            if primary:
                v_with_words = dict(v)
                v_with_words["words"] = primary.get("words", [])
                res = compute_verse_resonance(v_with_words, vocab, resonator, baseline, half_std)
            else:
                res = compute_verse_resonance(v, vocab, resonator, baseline, half_std)
        else:
            res = compute_verse_resonance(v, vocab, resonator, baseline, half_std)

        verses.append(asdict(res))
        chapter_data.setdefault(res.chapter, []).append(res)

    # Chapter signatures
    chapter_signatures: dict[str, dict] = {}
    for ch, sigs in sorted(chapter_data.items()):
        n = len(sigs)
        avg_h = sum(s.resonance_hare for s in sigs) / n
        avg_k = sum(s.resonance_krishna for s in sigs) / n
        avg_r = sum(s.resonance_rama for s in sigs) / n
        guna_counts = Counter(s.guna for s in sigs)
        dominant_guna = guna_counts.most_common(1)[0][0]
        chapter_signatures[str(ch)] = {
            "verse_count": n,
            "avg_resonance_hare": round(avg_h, 6),
            "avg_resonance_krishna": round(avg_k, 6),
            "avg_resonance_rama": round(avg_r, 6),
            "dominant_guna": dominant_guna,
        }

    # Global averages
    total = len(verses)
    avg_h = sum(v["resonance_hare"] for v in verses) / total
    avg_k = sum(v["resonance_krishna"] for v in verses) / total
    avg_r = sum(v["resonance_rama"] for v in verses) / total

    return {
        "book_code": "BG",
        "total_verses": total,
        "total_chapters": len(chapter_signatures),
        "avg_resonance_hare": round(avg_h, 6),
        "avg_resonance_krishna": round(avg_k, 6),
        "avg_resonance_rama": round(avg_r, 6),
        "chapter_signatures": chapter_signatures,
        "verses": verses,
        "extraction_version": "2.0.0",
        "extraction_method": "rama_4d_coordinate_resonance",
    }


# =============================================================================
# ANALYSIS
# =============================================================================


def analyze(index: dict) -> None:
    """Print analysis comparing old vs new approach."""
    verses = index["verses"]
    total = len(verses)

    print(f"\n{'=' * 60}")
    print("RAMA-NATIVE RESONANCE ANALYSIS")
    print(f"{'=' * 60}")

    # Global resonance
    print("\nGlobal H/K/R resonance:")
    print(f"  HARE:    {index['avg_resonance_hare']:.4f}")
    print(f"  KRISHNA: {index['avg_resonance_krishna']:.4f}")
    print(f"  RAMA:    {index['avg_resonance_rama']:.4f}")

    # Compare with old (all ~0.140)
    print("\n  OLD: all ~0.140 (zero differentiation)")
    print(
        f"  NEW: H={index['avg_resonance_hare']:.4f}, "
        f"K={index['avg_resonance_krishna']:.4f}, "
        f"R={index['avg_resonance_rama']:.4f}"
    )

    # Dominant name distribution
    name_counts = Counter(v["dominant_name"] for v in verses)
    print("\nDominant name distribution:")
    for name in ("HARE", "KRISHNA", "RAMA"):
        count = name_counts.get(name, 0)
        print(f"  {name:8s}: {count:3d} verses ({count / total * 100:.1f}%)")

    # Guna distribution
    guna_counts = Counter(v["guna"] for v in verses)
    print("\nGuna distribution:")
    for guna in ("sattva", "rajas", "tamas"):
        count = guna_counts.get(guna, 0)
        print(f"  {guna:8s}: {count:3d} verses ({count / total * 100:.1f}%)")

    # Attractor distribution
    attractor_counts = Counter(v["attractor"] for v in verses)
    unique_attractors = len(attractor_counts)
    print("\nAttractor distribution:")
    print(f"  Unique attractors: {unique_attractors}")
    print(f"  Most common: {attractor_counts.most_common(5)}")

    # Element distribution
    elem_counts = Counter(v["dominant_element"] for v in verses)
    print("\nDominant element distribution:")
    for elem in ("akasha", "vayu", "agni", "jala", "prithvi"):
        count = elem_counts.get(elem, 0)
        print(f"  {elem:8s}: {count:3d} verses ({count / total * 100:.1f}%)")

    # Resonance variance (should be HIGH, unlike old ~0.0001)
    import statistics

    h_values = [v["resonance_hare"] for v in verses]
    k_values = [v["resonance_krishna"] for v in verses]
    r_values = [v["resonance_rama"] for v in verses]

    print("\nResonance variance (should be >0, old was ~0.0000):")
    print(f"  HARE    stdev: {statistics.stdev(h_values):.4f}")
    print(f"  KRISHNA stdev: {statistics.stdev(k_values):.4f}")
    print(f"  RAMA    stdev: {statistics.stdev(r_values):.4f}")

    # Verse with highest HARE resonance
    max_h = max(verses, key=lambda v: v["resonance_hare"])
    max_k = max(verses, key=lambda v: v["resonance_krishna"])
    max_r = max(verses, key=lambda v: v["resonance_rama"])
    print("\nPeak resonance verses:")
    print(f"  Highest HARE:    {max_h['verse_id']} ({max_h['resonance_hare']:.4f})")
    print(f"  Highest KRISHNA: {max_k['verse_id']} ({max_k['resonance_krishna']:.4f})")
    print(f"  Highest RAMA:    {max_r['verse_id']} ({max_r['resonance_rama']:.4f})")

    # Fixed point check
    bg1866 = next((v for v in verses if v["verse_id"] == "BG.18.66"), None)
    if bg1866:
        print("\nFixed point BG.18.66:")
        print(
            f"  H={bg1866['resonance_hare']:.4f} K={bg1866['resonance_krishna']:.4f} R={bg1866['resonance_rama']:.4f}"
        )
        print(f"  dominant: {bg1866['dominant_name']}, guna: {bg1866['guna']}")
        print(f"  attractor: {bg1866['attractor']}, element: {bg1866['dominant_element']}")

    # Grouped/empty verses
    empty = sum(1 for v in verses if v["phonetic_length"] == 0)
    print(f"\n  Empty verses (no word-for-word): {empty}")


# =============================================================================
# MAIN
# =============================================================================


if __name__ == "__main__":
    print("Extracting RAMA-native resonance index...")
    index = extract_rama_resonance()

    # Analysis first
    analyze(index)

    # Save
    with open(_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {_OUTPUT_PATH} ({_OUTPUT_PATH.stat().st_size // 1024}KB)")
