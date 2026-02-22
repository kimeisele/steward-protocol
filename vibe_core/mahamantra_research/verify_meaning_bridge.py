"""
Test: English -> Sanskrit bridge via SemanticIndex.by_meaning()

The Gita lexicon has 4127 Sanskrit words with Prabhupada's English translations.
SemanticIndex already tokenizes these meanings into a reverse index.

Pipeline:
  1. English text -> tokenize into words
  2. Each English word -> by_meaning() -> matching Sanskrit words
  3. Sanskrit words -> RAMA coords -> 4D phonetic signature
  4. Aggregate signature -> mod 17 -> intent class

No keywords. No SHA256. No ML. Pure Parampara ground truth.
"""

from vibe_core.mahamantra.substrate.semantic_index import get_index, words_by_meaning
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_VARGA,
    COORD_HARMONIC,
    IS_SHRUTI,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_KRISHNA,
    KSETRAJNA,
    TRINITY,
    NAVA,
    SEVEN,
    WORDS,
)

KRISHNA = POSITION_SUM_KRISHNA  # 17

idx = get_index()
print(f"Lexicon loaded: {idx.stats()}")
print()

# First: what English meaning tokens exist in the index?
meaning_tokens = sorted(idx._by_meaning_word.keys()) if idx._by_meaning_word else []
print(f"Total meaning tokens in index: {len(meaning_tokens)}")
print(f"Sample tokens: {meaning_tokens[:50]}")
print()

# Test: what Sanskrit words resonate with "error", "fail", "success", etc?
probe_words = [
    "error",
    "fail",
    "failure",
    "wrong",
    "fault",
    "warning",
    "danger",
    "fear",
    "caution",
    "success",
    "victory",
    "complete",
    "done",
    "good",
    "pure",
    "divine",
    "transcendental",
    "supreme",
    "perfect",
    "destroy",
    "death",
    "kill",
    "attack",
    "create",
    "birth",
    "begin",
    "start",
    "connection",
    "database",
    "system",
    "healthy",
]

print("=" * 80)
print("ENGLISH -> SANSKRIT RESONANCE")
print("=" * 80)

for eng in probe_words:
    matches = words_by_meaning(eng)
    if matches:
        sanskrit_list = [(m.sanskrit, m.first_meaning) for m in matches[:5]]
        print(f"  {eng:<18} -> {len(matches)} hits: {sanskrit_list}")
    else:
        print(f"  {eng:<18} -> NO MATCH")

# Now: full pipeline test
print()
print("=" * 80)
print("FULL PIPELINE: English text -> Sanskrit resonance -> 4D -> mod 17")
print("=" * 80)

tests = [
    ("ERROR: Database connection failed", "tamas"),
    ("FATAL: Application crashed with segfault", "tamas"),
    ("WARNING: Slow query detected, retry in progress", "rajas"),
    ("TODO: Fix this workaround later", "rajas"),
    ("SUCCESS: All tests passed, deployment complete", "sattva"),
    ("System healthy and stable, all services verified", "sattva"),
    ("Unified system achieved optimal harmonious state", "suddha"),
    ("Error occurred but partial success achieved", "tamas"),
    ("Error: fail", "tamas"),
    ("Warning: slow", "rajas"),
    ("Success: done", "sattva"),
    ("Everything is healthy", "sattva"),
    ("Warning: minor issue", "rajas"),
    ("Error: critical failure", "tamas"),
]

import re


def tokenize_english(text):
    """Split English text into clean lowercase tokens."""
    return [w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) >= 3]


def english_to_sanskrit_resonance(text):
    """
    English text -> Sanskrit resonance via meaning bridge.
    Returns list of resonating LexiconWords.
    """
    tokens = tokenize_english(text)
    seen = set()
    resonant = []
    for tok in tokens:
        for w in words_by_meaning(tok):
            wid = id(w)
            if wid not in seen:
                seen.add(wid)
                resonant.append(w)
    return resonant


def compute_4d_energy(words):
    """Compute aggregate 4D phonetic energy from Sanskrit words."""
    if not words:
        return {"energy": 0, "element_sum": 0, "varga_sum": 0, "harmonic_sum": 0, "shruti_count": 0, "n_coords": 0}
    all_coords = []
    for w in words:
        all_coords.extend(w.coords)
    if not all_coords:
        return {"energy": 0, "element_sum": 0, "varga_sum": 0, "harmonic_sum": 0, "shruti_count": 0, "n_coords": 0}
    return {
        "energy": sum(all_coords),
        "element_sum": sum(COORD_ELEMENT[c].value for c in all_coords),
        "varga_sum": sum(COORD_VARGA[c] for c in all_coords),
        "harmonic_sum": sum(COORD_HARMONIC[c] for c in all_coords),
        "shruti_count": sum(1 for c in all_coords if IS_SHRUTI[c]),
        "n_coords": len(all_coords),
    }


for text, expected in tests:
    tokens = tokenize_english(text)
    resonant = english_to_sanskrit_resonance(text)
    matched_tokens = [t for t in tokens if words_by_meaning(t)]
    energy = compute_4d_energy(resonant)
    e = energy["energy"]
    r17 = e % KRISHNA if e > 0 else -1

    print(f"\n  Text: {text}")
    print(f"  Tokens: {tokens}")
    print(f"  Matched: {matched_tokens}")
    print(f"  Sanskrit resonance: {len(resonant)} words")
    if resonant:
        print(f"  Top 5: {[(w.sanskrit, w.first_meaning) for w in resonant[:5]]}")
    print(f"  4D Energy: {e}  mod17={r17}  Expected={expected}")
