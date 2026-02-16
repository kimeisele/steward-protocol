"""
RESEARCH: Semantic Basins — Where Meaning Lives in the Mahamantra
=================================================================

HYPOTHESIS:
    The MahaAlgorithm's attractor basins ARE semantic fields.
    Words that converge to the same attractor share meaning.
    This is not a lookup — it's a DERIVATION.

WHAT WE KNOW:
    - MahaModularSynth.transform(seed) applies 16 H/K/R operations
    - H = v * 7 * adsr + lfo (mod space)     — INPUT/ENERGY
    - K = v + 10 + pos + feedback (mod space) — COMPUTE/ATTRACT
    - R = v² + feedback (mod space)           — OUTPUT/BLISS
    - Iterating transform() converges to ATTRACTORS (fixed points or cycles)
    - Seeds that converge to the same attractor are in the same BASIN

QUESTION:
    If we encode divine names to RAMA coords (0-48), transform each coord,
    and find the attractor — do names with related meanings share attractors?

    Jagannath (Lord of Universe) and Govinda (Cow-protector) — same attractor?
    Parashurama (warrior) and Bhishma (commitment) — same basin?

    If YES → the math itself encodes semantic relationships.
    If NO → we need a different bridge.

ALSO:
    What does the Mahamantra itself (Hare Krishna Hare Krishna...) produce?
    Each of the 16 positions has a RAMA coord. Each coord has an attractor.
    The PATTERN of attractors across the 16 positions IS the Mahamantra's
    semantic signature.

RUN: python3 -m vibe_core.mahamantra.research.semantic_basins
"""
import sys, os
_substrate = os.path.dirname(os.path.abspath(__file__))
if _substrate in sys.path:
    sys.path.remove(_substrate)

from collections import defaultdict
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MahaModularSynth, MahaSynthParams, MAHA_16_STEPS, PATTERN,
)
from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL, rama_to_phoneme
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT, COORD_HARMONIC, COORD_VARGA, ELEMENT_NAMES, IS_SHRUTI,
)
from vibe_core.mahamantra.substrate.semantic_index import get_index, words_at_position
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, SEVEN, WORDS

synth = MahaModularSynth(default_preset="quantum")

# =============================================================================
# PART 1: ATTRACTOR BASINS in RAMA space (mod 49)
# =============================================================================
print("=" * 70)
print("PART 1: ATTRACTOR BASINS in RAMA space (mod 49)")
print("=" * 70)

# For each RAMA coord (0-48), find its attractor under the synth
rama_params = MahaSynthParams(mod_space=VARNAMALA_TOTAL)  # mod 49
basins = defaultdict(list)  # attractor → [coords that converge to it]

for coord in range(VARNAMALA_TOTAL):
    # Iterate transform until stable
    value = coord
    seen = {}
    for i in range(50):
        if value in seen:
            break
        seen[value] = i
        value = synth.transform(value, params=rama_params)
    attractor = value
    basins[attractor].append(coord)

print(f"\n{len(basins)} attractor basins found in RAMA space (49 coords):\n")
for att in sorted(basins.keys()):
    members = basins[att]
    phonemes = [rama_to_phoneme(c) for c in members]
    element = ELEMENT_NAMES[COORD_ELEMENT[att]]
    shruti = "SHRUTI" if IS_SHRUTI[att] else "naksha"
    # How many Gita words start at this attractor?
    words_here = words_at_position(att)
    n_words = len(words_here)
    top_meanings = ", ".join(w.first_meaning for w in words_here[:3]) if words_here else "—"
    print(f"  Basin {att:2d} ({rama_to_phoneme(att):4s} {element:8s} {shruti:6s}) "
          f"← {len(members):2d} coords: {' '.join(phonemes[:8])}")
    print(f"           {n_words} Gita words. Top: {top_meanings}")

# =============================================================================
# PART 2: DIVINE NAMES — Do related names share basins?
# =============================================================================
print("\n" + "=" * 70)
print("PART 2: DIVINE NAMES — Attractor Signatures")
print("=" * 70)

NAMES = {
    # Vishnu names
    "hare": "harē",
    "krishna": "kṛṣṇa",
    "rama": "rāma",
    "jagannath": "jagannātha",
    "govinda": "gōvinda",
    "narayana": "nārāyaṇa",
    "vasudeva": "vāsudēva",
    "hari": "hari",
    "vishnu": "viṣṇu",
    "achyuta": "acyuta",
    "mukunda": "mukunda",
    # Guardians
    "prahlada": "prahlāda",
    "bhishma": "bhīṣma",
    "narada": "nārada",
    "parashurama": "paraśurāma",
    "bali": "bali",
    "kapila": "kapila",
}

name_signatures = {}
for name, iast in sorted(NAMES.items()):
    coords = encode_iast(iast)
    if not coords:
        print(f"  {name:15s} — ENCODING FAILED")
        continue

    # Per-syllable attractor
    attractors = []
    for c in coords:
        value = c
        for _ in range(50):
            prev = value
            value = synth.transform(value, params=rama_params)
            if value == prev:
                break
        attractors.append(value)

    # Name-level attractor (sum of coords → transform)
    name_seed = sum(coords) % VARNAMALA_TOTAL
    name_value = name_seed
    for _ in range(50):
        prev = name_value
        name_value = synth.transform(name_value, params=rama_params)
        if name_value == prev:
            break

    elements = [ELEMENT_NAMES[COORD_ELEMENT[c]] for c in coords]
    att_elements = [ELEMENT_NAMES[COORD_ELEMENT[a]] for a in attractors]

    name_signatures[name] = {
        "coords": coords,
        "attractors": tuple(attractors),
        "name_attractor": name_value,
        "elements": elements,
        "att_elements": att_elements,
    }

    print(f"\n  {name:15s} IAST={iast}")
    print(f"    RAMA coords:    {coords}")
    print(f"    Elements:       {' → '.join(elements)}")
    print(f"    Attractors:     {attractors}")
    print(f"    Att. Elements:  {' → '.join(att_elements)}")
    print(f"    Name attractor: {name_value} ({rama_to_phoneme(name_value)} "
          f"{ELEMENT_NAMES[COORD_ELEMENT[name_value]]})")

# =============================================================================
# PART 3: BASIN SHARING — Which names share attractor basins?
# =============================================================================
print("\n" + "=" * 70)
print("PART 3: BASIN SHARING — Names grouped by name-attractor")
print("=" * 70)

att_groups = defaultdict(list)
for name, sig in name_signatures.items():
    att_groups[sig["name_attractor"]].append(name)

for att in sorted(att_groups.keys()):
    names = att_groups[att]
    if len(names) > 1:
        print(f"\n  SHARED BASIN {att} ({rama_to_phoneme(att)} "
              f"{ELEMENT_NAMES[COORD_ELEMENT[att]]}):")
        for n in names:
            print(f"    → {n}")
    else:
        n = names[0]
        print(f"  Basin {att:2d} ({ELEMENT_NAMES[COORD_ELEMENT[att]]:8s}): {n}")

# =============================================================================
# PART 4: THE MAHAMANTRA ITSELF — 16 positions as semantic signature
# =============================================================================
print("\n" + "=" * 70)
print("PART 4: THE MAHAMANTRA — 16 positions, their attractors, their words")
print("=" * 70)

# The 16 words of the Mahamantra
MANTRA_WORDS = [
    "harē", "kṛṣṇa", "harē", "kṛṣṇa",
    "kṛṣṇa", "kṛṣṇa", "harē", "harē",
    "harē", "rāma", "harē", "rāma",
    "rāma", "rāma", "harē", "harē",
]

print(f"\n  Pos  Word      H/K/R  Coords → Attractors → Element → Gita Words")
print(f"  {'─'*75}")

for pos in range(WORDS):
    word = MANTRA_WORDS[pos]
    op = PATTERN[pos]  # H, K, or R
    coords = encode_iast(word)

    # Per-coord attractors
    attractors = []
    for c in coords:
        value = c
        for _ in range(50):
            prev = value
            value = synth.transform(value, params=rama_params)
            if value == prev:
                break
        attractors.append(value)

    # Unique attractors → words at those positions
    unique_atts = sorted(set(attractors))
    gita_words = []
    for a in unique_atts:
        ws = words_at_position(a)
        if ws:
            gita_words.append(ws[0].first_meaning)

    att_elements = [ELEMENT_NAMES[COORD_ELEMENT[a]][0] for a in attractors]

    print(f"  {pos+1:2d}   {word:9s} {op}      "
          f"{list(coords)} → {attractors} "
          f"{''.join(att_elements):5s} "
          f"{', '.join(gita_words[:3])}")

# =============================================================================
# PART 5: MAHA_QUANTUM (137) BASINS — The full algorithm space
# =============================================================================
print("\n" + "=" * 70)
print("PART 5: MAHA_QUANTUM (137) BASINS — Full algorithm space")
print("=" * 70)

basins_137 = defaultdict(list)
for seed in range(MAHA_QUANTUM):
    value = seed
    for _ in range(100):
        prev = value
        value = synth.transform(value)  # default = mod 137
        if value == prev:
            break
    basins_137[value].append(seed)

print(f"\n{len(basins_137)} attractor basins in mod-137 space:\n")
for att in sorted(basins_137.keys()):
    members = basins_137[att]
    # Map attractor to RAMA space for semantic lookup
    rama_att = att % VARNAMALA_TOTAL
    words_here = words_at_position(rama_att)
    top = words_here[0].first_meaning if words_here else "—"
    print(f"  Basin {att:3d} (→RAMA {rama_att:2d} {rama_to_phoneme(rama_att):4s}): "
          f"{len(members):3d} seeds. Gita: {top}")

# =============================================================================
# PART 6: CROSS-SPACE RESONANCE — Same name in mod-49 vs mod-137
# =============================================================================
print("\n" + "=" * 70)
print("PART 6: CROSS-SPACE — Name attractors in RAMA(49) vs QUANTUM(137)")
print("=" * 70)

for name, sig in sorted(name_signatures.items()):
    coords = sig["coords"]
    # mod-49 attractor (already computed)
    att_49 = sig["name_attractor"]
    # mod-137 attractor
    seed_137 = sum(coords) % MAHA_QUANTUM
    value = seed_137
    for _ in range(100):
        prev = value
        value = synth.transform(value)
        if value == prev:
            break
    att_137 = value

    # Do they map to the same RAMA position?
    att_137_rama = att_137 % VARNAMALA_TOTAL
    same = "✓ SAME" if att_137_rama == att_49 else "✗ DIFF"

    print(f"  {name:15s}  RAMA={att_49:2d}({ELEMENT_NAMES[COORD_ELEMENT[att_49]]:8s})  "
          f"QUANTUM={att_137:3d}→RAMA={att_137_rama:2d}({ELEMENT_NAMES[COORD_ELEMENT[att_137_rama]]:8s})  {same}")

print("\nDONE.")
