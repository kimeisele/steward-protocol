"""
PROOF: Basin-enhanced resonance vs old string-only approach
============================================================

Compare the NEW ranker (with real basin scoring) against:
1. Pure phonetic (no string boost, no basin)
2. String-only (grep in meaning index)
3. New hybrid (phonetic + basin + string boost)

Also test: words that have NO string match but should resonate semantically.
These are the TRUE test — can the math find meaning without grep?

RUN: python3 -m vibe_core.mahamantra.research.basin_vs_string
"""

import sys, os

from vibe_core.mahamantra.substrate.resonance_ranker import resonate, rank_words
from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
from vibe_core.mahamantra.substrate.semantic_index import get_index
from vibe_core.mahamantra.substrate.basin_map import basin_signature, basin_set, COORD_BASIN

idx = get_index()

# =============================================================================
# TEST 1: Words WITH string matches — does basin improve ranking?
# =============================================================================
print("=" * 70)
print("TEST 1: Words with string matches — basin-enhanced vs old")
print("=" * 70)

for word in ["fire", "devotion", "knowledge", "surrender", "war", "death", "soul", "god", "truth", "love"]:
    results = resonate(word, top_n=5)
    meanings = [r.first_meaning for r in results]
    print(f"\n  '{word}' → {meanings}")
    if results:
        r = results[0]
        print(f"    Top: {r.sanskrit} ({r.first_meaning})")
        print(
            f"    Scores: elem={r.element_score:.2f} harm={r.harmonic_score:.2f} "
            f"shruti={r.shruti_score:.2f} varga={r.varga_score:.2f} "
            f"basin={r.attractor_score:.2f} TOTAL={r.total_score:.3f}"
        )

# =============================================================================
# TEST 2: Words WITHOUT string matches — pure resonance
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: Words WITHOUT string matches — pure math resonance")
print("=" * 70)

# These words don't appear in the Gita meaning index, so string boost = 0.
# Only phonetic + basin scoring can find them.
NO_MATCH_WORDS = [
    "dharma",  # The central concept — but not in English meanings
    "karma",  # Same
    "yoga",  # Same
    "mantra",  # Same
    "guru",  # Same
    "avatar",  # Same
    "chakra",  # Same
    "prana",  # Same
    "moksha",  # Same
    "samsara",  # Same
    "ahimsa",  # Same
    "nirvana",  # Same
]

for word in NO_MATCH_WORDS:
    # Check if string match exists
    string_hits = idx.by_meaning(word)
    has_string = len(string_hits) > 0

    results = resonate(word, top_n=5)
    meanings = [r.first_meaning for r in results]

    # Get basin info
    coords = encode_text(word)
    if coords:
        bsig = basin_signature(tuple(coords))
        bset = basin_set(tuple(coords))
    else:
        bsig = ()
        bset = frozenset()

    marker = "STRING" if has_string else "PURE"
    print(f"\n  '{word}' [{marker}] basins={sorted(bset)}")
    print(f"    → {meanings}")
    if results:
        r = results[0]
        print(f"    basin_score={r.attractor_score:.3f} total={r.total_score:.3f}")

# =============================================================================
# TEST 3: Cross-language resonance — German words
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: Cross-language — German words (no string match possible)")
print("=" * 70)

GERMAN_WORDS = [
    ("Feuer", "fire"),
    ("Wasser", "water"),
    ("Erde", "earth"),
    ("Luft", "air"),
    ("Seele", "soul"),
    ("Wahrheit", "truth"),
    ("Liebe", "love"),
    ("Tod", "death"),
    ("Krieg", "war"),
    ("Wissen", "knowledge"),
    ("Hingabe", "devotion"),
]

for de, en in GERMAN_WORDS:
    de_results = resonate(de, top_n=3)
    en_results = resonate(en, top_n=3)

    de_meanings = [r.first_meaning for r in de_results]
    en_meanings = [r.first_meaning for r in en_results]

    # Basin comparison
    de_coords = encode_text(de)
    en_coords = encode_text(en)
    if de_coords and en_coords:
        de_bset = basin_set(tuple(de_coords))
        en_bset = basin_set(tuple(en_coords))
        shared = de_bset & en_bset
        overlap = f"{len(shared)}/{len(de_bset | en_bset)} basins shared"
    else:
        overlap = "encoding failed"

    print(f"\n  {de:12s} (DE) → {de_meanings}")
    print(f"  {en:12s} (EN) → {en_meanings}")
    print(f"  Basin overlap: {overlap}")

# =============================================================================
# TEST 4: Guardian resonance with basin scoring
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: Guardian resonance — basin-enhanced vocabulary")
print("=" * 70)

from vibe_core.mahamantra.substrate.resonance_ranker import guardian_resonance

GUARDIANS = ["prahlada", "bhishma", "narada", "parashurama", "bali", "kapila"]

for g in GUARDIANS:
    try:
        results = guardian_resonance(g, top_n=5)
        meanings = [f"{r.first_meaning} (b={r.attractor_score:.2f})" for r in results]
        print(f"\n  {g:15s} → {meanings}")
    except Exception as e:
        print(f"\n  {g:15s} → ERROR: {e}")

print("\nDONE.")
