"""
RESEARCH: Basin Bridge — Do English words share basins with their Sanskrit equivalents?
========================================================================================

THE CRITICAL QUESTION:
    If "fire" and "agni" converge to the same basins through pure math,
    then we don't need string-lookup. The vibration itself IS the meaning.

    If they DON'T share basins, we need a different bridge.

METHOD:
    1. Encode English word → RAMA coords (via phonetic_encoder)
    2. Encode Sanskrit equivalent → RAMA coords (via varnamala_codec)
    3. Compute basin signature for both (per-syllable attractor in mod-137)
    4. Compare: Jaccard similarity of basin sets

TEST PAIRS:
    fire ↔ agni, water ↔ jala, earth ↔ prithvi, air ↔ vayu,
    sky ↔ akasha, mind ↔ manas, soul ↔ atma, knowledge ↔ jnana,
    devotion ↔ bhakti, surrender ↔ sharanagati, war ↔ yuddha,
    truth ↔ satya, love ↔ prema, death ↔ mrityu

ALSO:
    What about Gita words? Each of the 4127 words has RAMA coords.
    Compute basin signature for ALL of them.
    Then: find words with SIMILAR basin signatures to an input.
    This is the REAL semantic matching — no strings, pure math.

RUN: python3 -m vibe_core.mahamantra.research.basin_bridge
"""

import sys, os

_substrate = os.path.dirname(os.path.abspath(__file__))
if _substrate in sys.path:
    sys.path.remove(_substrate)

from collections import Counter, defaultdict
from typing import List, Tuple

from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth, MahaSynthParams
from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL, rama_to_phoneme
from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, ELEMENT_NAMES
from vibe_core.mahamantra.substrate.semantic_index import get_index
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

synth = MahaModularSynth(default_preset="quantum")
idx = get_index()


def basin_signature(coords: Tuple[int, ...]) -> Tuple[int, ...]:
    """Compute basin signature: per-coord attractor in mod-137."""
    basins = []
    for c in coords:
        value = c
        for _ in range(100):
            prev = value
            value = synth.transform(value)
            if value == prev:
                break
        basins.append(value)
    return tuple(basins)


def basin_set(sig: Tuple[int, ...]) -> frozenset:
    """Unique basins touched by a signature."""
    return frozenset(sig)


def jaccard(a: frozenset, b: frozenset) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def basin_histogram(sig: Tuple[int, ...]) -> Counter:
    """Basin frequency distribution."""
    return Counter(sig)


def histogram_similarity(a: Counter, b: Counter) -> float:
    """Cosine-like similarity between basin histograms."""
    all_basins = set(a.keys()) | set(b.keys())
    if not all_basins:
        return 0.0
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in all_basins)
    mag_a = sum(v * v for v in a.values()) ** 0.5
    mag_b = sum(v * v for v in b.values()) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# =============================================================================
# PART 1: English ↔ Sanskrit pairs — do they share basins?
# =============================================================================
print("=" * 70)
print("PART 1: ENGLISH ↔ SANSKRIT — Basin Comparison")
print("=" * 70)

PAIRS = [
    ("fire", "agni"),
    ("water", "jala"),
    ("earth", "pṛthivī"),
    ("air", "vāyu"),
    ("sky", "ākāśa"),
    ("mind", "manas"),
    ("soul", "ātmā"),
    ("knowledge", "jñāna"),
    ("devotion", "bhakti"),
    ("surrender", "śaraṇāgati"),
    ("war", "yuddha"),
    ("truth", "satya"),
    ("love", "prēma"),
    ("death", "mṛtyu"),
    ("god", "dēva"),
    ("king", "rāja"),
    ("mother", "mātā"),
    ("father", "pitā"),
    ("sun", "sūrya"),
    ("moon", "candra"),
]

print(
    f"\n  {'English':12s} {'Sanskrit':15s} {'EN basins':20s} {'SK basins':20s} "
    f"{'Jaccard':8s} {'Hist-Sim':8s} {'Shared':8s}"
)
print(f"  {'─' * 95}")

shared_count = 0
total_count = 0

for en, sk in PAIRS:
    en_coords = encode_text(en)
    sk_coords = encode_iast(sk)

    if not en_coords or not sk_coords:
        print(f"  {en:12s} {sk:15s} ENCODING FAILED")
        continue

    en_sig = basin_signature(tuple(en_coords))
    sk_sig = basin_signature(tuple(sk_coords))

    en_set = basin_set(en_sig)
    sk_set = basin_set(sk_sig)

    j = jaccard(en_set, sk_set)
    h = histogram_similarity(basin_histogram(en_sig), basin_histogram(sk_sig))
    shared = en_set & sk_set

    total_count += 1
    if shared:
        shared_count += 1

    marker = "✓" if shared else "✗"
    print(
        f"  {en:12s} {sk:15s} {str(sorted(en_set)):20s} {str(sorted(sk_set)):20s} "
        f"{j:7.2f}  {h:7.2f}  {marker} {sorted(shared)}"
    )

print(f"\n  SHARED BASINS: {shared_count}/{total_count} pairs ({shared_count / total_count * 100:.0f}%)")

# =============================================================================
# PART 2: ALL 4127 Gita words — basin signatures
# =============================================================================
print("\n" + "=" * 70)
print("PART 2: BASIN SIGNATURES for ALL 4127 Gita words")
print("=" * 70)

# Compute basin signature for every word in the lexicon
word_basins = {}
basin_to_words = defaultdict(list)

for word in idx.words:
    if not word.coords:
        continue
    sig = basin_signature(word.coords)
    bset = basin_set(sig)
    word_basins[word.packed_hex] = {
        "word": word,
        "sig": sig,
        "bset": bset,
        "hist": basin_histogram(sig),
    }
    # Index by basin set (frozen)
    basin_to_words[bset].append(word)

# How many unique basin signatures?
unique_sigs = set()
for wb in word_basins.values():
    unique_sigs.add(wb["sig"])

unique_bsets = set()
for wb in word_basins.values():
    unique_bsets.add(wb["bset"])

print(f"\n  Total words with coords: {len(word_basins)}")
print(f"  Unique basin signatures: {len(unique_sigs)}")
print(f"  Unique basin SETS:       {len(unique_bsets)}")

# Distribution of basin set sizes
set_sizes = Counter(len(wb["bset"]) for wb in word_basins.values())
print(f"\n  Basin set size distribution:")
for size in sorted(set_sizes.keys()):
    print(f"    {size} basins: {set_sizes[size]} words")

# Top basin sets (most words)
print(f"\n  Top 10 basin sets (most words):")
sorted_bsets = sorted(basin_to_words.items(), key=lambda x: -len(x[1]))
for bset, words in sorted_bsets[:10]:
    sample = ", ".join(w.first_meaning for w in words[:3])
    print(f"    {str(sorted(bset)):25s}: {len(words):4d} words. e.g. {sample}")

# =============================================================================
# PART 3: BASIN-BASED MATCHING — "fire" → find Gita words by basin similarity
# =============================================================================
print("\n" + "=" * 70)
print("PART 3: BASIN-BASED MATCHING — English → Gita words (NO string lookup)")
print("=" * 70)

TEST_WORDS = [
    "fire",
    "water",
    "knowledge",
    "devotion",
    "surrender",
    "war",
    "truth",
    "love",
    "death",
    "mind",
    "soul",
    "god",
]

for test_word in TEST_WORDS:
    en_coords = encode_text(test_word)
    if not en_coords:
        print(f"\n  '{test_word}' — encoding failed")
        continue

    en_sig = basin_signature(tuple(en_coords))
    en_bset = basin_set(en_sig)
    en_hist = basin_histogram(en_sig)

    # Score all Gita words by basin similarity
    scores = []
    for hex_key, wb in word_basins.items():
        j = jaccard(en_bset, wb["bset"])
        h = histogram_similarity(en_hist, wb["hist"])
        combined = 0.4 * j + 0.6 * h  # Weight histogram more (captures proportion)
        scores.append((combined, j, h, wb["word"]))

    scores.sort(key=lambda x: -x[0])

    print(f"\n  '{test_word}' basins={sorted(en_bset)}")
    print(f"    {'Score':6s} {'Jacc':5s} {'Hist':5s} {'Sanskrit':15s} {'Meaning'}")
    for combined, j, h, word in scores[:8]:
        print(f"    {combined:.3f}  {j:.2f}  {h:.2f}  {word.sanskrit:15s} {word.first_meaning}")

# =============================================================================
# PART 4: COMPARISON — Basin matching vs String lookup vs Phonetic ranking
# =============================================================================
print("\n" + "=" * 70)
print("PART 4: THREE METHODS COMPARED — Basin vs String vs Phonetic")
print("=" * 70)

from vibe_core.mahamantra.substrate.resonance_ranker import rank_words, resonate

for test_word in ["fire", "devotion", "knowledge", "surrender"]:
    print(f"\n  '{test_word}':")

    # Method 1: Basin matching (pure math, no strings)
    en_coords = encode_text(test_word)
    if en_coords:
        en_sig = basin_signature(tuple(en_coords))
        en_bset = basin_set(en_sig)
        en_hist = basin_histogram(en_sig)
        scores = []
        for hex_key, wb in word_basins.items():
            j = jaccard(en_bset, wb["bset"])
            h = histogram_similarity(en_hist, wb["hist"])
            scores.append((0.4 * j + 0.6 * h, wb["word"]))
        scores.sort(key=lambda x: -x[0])
        basin_top = [w.first_meaning for _, w in scores[:5]]
    else:
        basin_top = ["FAILED"]

    # Method 2: String lookup (current by_meaning)
    string_hits = idx.by_meaning(test_word)
    string_top = [w.first_meaning for w in string_hits[:5]]

    # Method 3: Current resonate() (phonetic + string boost)
    resonated = resonate(test_word, top_n=5)
    resonate_top = [rw.word.first_meaning for rw in resonated]

    print(f"    BASIN (pure math):  {basin_top}")
    print(f"    STRING (grep):      {string_top}")
    print(f"    RESONATE (hybrid):  {resonate_top}")

print("\nDONE.")
