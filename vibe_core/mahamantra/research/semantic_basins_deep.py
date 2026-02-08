"""
RESEARCH: Deep Basin Analysis — What do the 7 QUANTUM basins MEAN?
===================================================================

FINDING FROM PART 1:
    mod-49 (RAMA): ALL coords → attractor 0. Too small. No structure.
    mod-137 (QUANTUM): 7 basins. SEVEN = the sacred number. Structure!

THIS SCRIPT:
    For each of the 7 basins in mod-137:
    1. Which seeds belong to this basin?
    2. Map each seed to RAMA space (mod 49) → which phonemes?
    3. What Gita words START at those RAMA positions?
    4. What are the DOMINANT meanings across all words in this basin?
    5. What ELEMENT distribution does this basin have?

    Then: which divine names land in which basin?
    And: what does the Mahamantra pattern look like across basins?

RUN: python3 -m vibe_core.mahamantra.research.semantic_basins_deep
"""
import sys, os
_substrate = os.path.dirname(os.path.abspath(__file__))
if _substrate in sys.path:
    sys.path.remove(_substrate)

from collections import defaultdict, Counter
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth, MahaSynthParams
from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL, rama_to_phoneme
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT, ELEMENT_NAMES, IS_SHRUTI,
)
from vibe_core.mahamantra.substrate.semantic_index import get_index, words_at_position
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, SEVEN, WORDS

synth = MahaModularSynth(default_preset="quantum")
idx = get_index()

# =============================================================================
# STEP 1: Compute all 137 basins
# =============================================================================
basins_137 = defaultdict(list)
for seed in range(MAHA_QUANTUM):
    value = seed
    for _ in range(100):
        prev = value
        value = synth.transform(value)
        if value == prev:
            break
    basins_137[value].append(seed)

# =============================================================================
# STEP 2: For each basin, analyze semantic content
# =============================================================================
print("=" * 70)
print(f"7 SEMANTIC BASINS in MAHA_QUANTUM (137)")
print("=" * 70)

for att in sorted(basins_137.keys()):
    members = basins_137[att]
    rama_att = att % VARNAMALA_TOTAL

    # Map all members to RAMA space
    rama_positions = set()
    for m in members:
        rama_positions.add(m % VARNAMALA_TOTAL)

    # Collect ALL Gita words at all RAMA positions in this basin
    all_words = []
    all_meanings = []
    element_counts = Counter()
    shruti_count = 0

    for rp in sorted(rama_positions):
        words = words_at_position(rp)
        all_words.extend(words)
        for w in words:
            for meaning in w.meanings:
                # Extract significant words from meaning
                for token in meaning.lower().split():
                    if len(token) >= 4 and token not in (
                        "this", "that", "with", "from", "which", "have",
                        "been", "they", "them", "their", "these", "those",
                        "also", "very", "such", "into", "upon", "than",
                        "only", "just", "even", "more", "most", "some",
                        "what", "when", "will", "does", "done", "being",
                    ):
                        all_meanings.append(token)
        element_counts[ELEMENT_NAMES[COORD_ELEMENT[rp]]] += 1
        if IS_SHRUTI[rp]:
            shruti_count += 1

    meaning_freq = Counter(all_meanings).most_common(20)

    print(f"\n{'='*70}")
    print(f"BASIN {att:3d} → RAMA {rama_att:2d} ({rama_to_phoneme(rama_att)}) "
          f"| {len(members)} seeds | {len(all_words)} Gita words")
    print(f"{'='*70}")
    print(f"  RAMA positions: {sorted(rama_positions)}")
    print(f"  Elements: {dict(element_counts)}")
    print(f"  Shruti positions: {shruti_count}/{len(rama_positions)}")
    print(f"\n  TOP MEANING WORDS (frequency across all Gita translations):")
    for word, count in meaning_freq:
        print(f"    {word:20s} × {count}")

# =============================================================================
# STEP 3: Divine names per basin
# =============================================================================
print("\n" + "=" * 70)
print("DIVINE NAMES → BASIN MAPPING (mod 137)")
print("=" * 70)

NAMES = {
    "hare": "harē", "krishna": "kṛṣṇa", "rama": "rāma",
    "jagannath": "jagannātha", "govinda": "gōvinda",
    "narayana": "nārāyaṇa", "vasudeva": "vāsudēva",
    "hari": "hari", "vishnu": "viṣṇu", "achyuta": "acyuta",
    "mukunda": "mukunda", "prahlada": "prahlāda",
    "bhishma": "bhīṣma", "narada": "nārada",
    "parashurama": "paraśurāma", "bali": "bali",
    "kapila": "kapila", "shiva": "śiva",
    "brahma": "brahmā", "indra": "indra",
}

basin_names = defaultdict(list)
for name, iast in sorted(NAMES.items()):
    coords = encode_iast(iast)
    if not coords:
        continue
    seed_137 = sum(coords) % MAHA_QUANTUM
    value = seed_137
    for _ in range(100):
        prev = value
        value = synth.transform(value)
        if value == prev:
            break
    basin_names[value].append((name, coords))

for att in sorted(basin_names.keys()):
    names = basin_names[att]
    rama_att = att % VARNAMALA_TOTAL
    # Get top meaning words for this basin
    basin_words = []
    for rp in set(m % VARNAMALA_TOTAL for m in basins_137[att]):
        for w in words_at_position(rp):
            basin_words.append(w.first_meaning)

    print(f"\n  BASIN {att:3d} ({ELEMENT_NAMES[COORD_ELEMENT[rama_att]]:8s}):")
    for name, coords in names:
        elems = "→".join(ELEMENT_NAMES[COORD_ELEMENT[c]][0] for c in coords)
        print(f"    {name:15s} coords={list(coords)} elem={elems}")

# =============================================================================
# STEP 4: Per-syllable basin analysis (not just sum)
# =============================================================================
print("\n" + "=" * 70)
print("PER-SYLLABLE BASIN ANALYSIS — Each phoneme's attractor in mod-137")
print("=" * 70)

for name, iast in [("krishna", "kṛṣṇa"), ("rama", "rāma"), ("hare", "harē"),
                    ("jagannath", "jagannātha"), ("narada", "nārada"),
                    ("prahlada", "prahlāda"), ("parashurama", "paraśurāma")]:
    coords = encode_iast(iast)
    if not coords:
        continue

    print(f"\n  {name} ({iast}):")
    syllable_basins = []
    for c in coords:
        # Transform this RAMA coord in mod-137 space
        value = c
        for _ in range(100):
            prev = value
            value = synth.transform(value)
            if value == prev:
                break
        syllable_basins.append(value)
        phoneme = rama_to_phoneme(c)
        element = ELEMENT_NAMES[COORD_ELEMENT[c]]
        att_element = ELEMENT_NAMES[COORD_ELEMENT[value % VARNAMALA_TOTAL]]
        # What words at this attractor?
        att_words = words_at_position(value % VARNAMALA_TOTAL)
        top_w = att_words[0].first_meaning if att_words else "—"
        print(f"    {phoneme:4s} (RAMA {c:2d}, {element:8s}) → Basin {value:3d} "
              f"({att_element:8s}): {top_w}")

    # Basin pattern = the name's "semantic DNA"
    pattern = tuple(syllable_basins)
    unique = sorted(set(pattern))
    print(f"    BASIN PATTERN: {list(pattern)}")
    print(f"    UNIQUE BASINS: {unique} ({len(unique)} of {len(pattern)})")

# =============================================================================
# STEP 5: The Mahamantra's basin pattern
# =============================================================================
print("\n" + "=" * 70)
print("THE MAHAMANTRA — Per-syllable basin pattern across 16 positions")
print("=" * 70)

MANTRA = [
    "harē", "kṛṣṇa", "harē", "kṛṣṇa",
    "kṛṣṇa", "kṛṣṇa", "harē", "harē",
    "harē", "rāma", "harē", "rāma",
    "rāma", "rāma", "harē", "harē",
]

all_mantra_basins = []
for pos, word in enumerate(MANTRA):
    coords = encode_iast(word)
    basins_for_word = []
    for c in coords:
        value = c
        for _ in range(100):
            prev = value
            value = synth.transform(value)
            if value == prev:
                break
        basins_for_word.append(value)
    all_mantra_basins.append(basins_for_word)
    print(f"  {pos+1:2d}. {word:9s} → basins {basins_for_word}")

# Flatten and count
flat = [b for word_basins in all_mantra_basins for b in word_basins]
basin_dist = Counter(flat)
print(f"\n  Basin distribution across entire Mahamantra:")
for b, count in basin_dist.most_common():
    rama_b = b % VARNAMALA_TOTAL
    print(f"    Basin {b:3d} ({ELEMENT_NAMES[COORD_ELEMENT[rama_b]]:8s}): {count}× "
          f"= {count/len(flat)*100:.0f}%")

print("\nDONE.")
