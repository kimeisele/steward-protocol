"""
Test: Shabda-first seed computation.

Current: SHA256 XOR Shabda -> SHA256 dominates (Avalanche kills phonetics)
Proposed: Shabda LEADS, SHA256 is salt/fingerprint

The 4D phonetic signature (Element, Varga, Harmonic, Shruti) determines
the CATEGORY. SHA256 determines the POSITION within that category.
"""

import hashlib
import sys
from vibe_core.mahamantra.substrate.phonetics.shabda import text_to_vibration
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_VARGA,
    COORD_HARMONIC,
    IS_SHRUTI,
)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.adapters.synth import MahaSynth
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    QUARTERS,
    MAHA_QUANTUM,
    POSITION_SUM_KRISHNA,
    KSETRAJNA,
    TRINITY,
    SEVEN,
)


def shabda_first_seed(text):
    """
    Shabda-first seed: phonetics LEAD, SHA256 is salt.

    Pipeline:
      1. text -> Shabda vibrations -> RAMA coords
      2. RAMA coords -> spell_cycle -> attractor (phonetic identity)
      3. SHA256(text) -> salt (structural fingerprint)
      4. category = attractor % WORDS (phonetically determined!)
      5. salt refines position WITHIN category
    """
    vibs = text_to_vibration(text)
    if not vibs:
        return 0, 0, 0

    coords = tuple(v.signature_id % 49 for v in vibs)

    # SHABDA LEADS: spell_cycle determines the attractor
    synth = MahaSynth(preset="quantum")
    spell = synth.spell_cycle(coords, seed=0)
    attractor = spell.final_value

    # Category from PHONETICS (not SHA256!)
    category = attractor % WORDS  # 0-15

    # SHA256 is just salt — refines position WITHIN category
    text_hash = int.from_bytes(hashlib.sha256(text.lower().encode()).digest()[:4], "big")
    salt = text_hash % MAHA_QUANTUM

    # Seed: category (phonetic) + salt (structural)
    final_seed = (category * MAHA_QUANTUM) + salt

    return final_seed, category, attractor


def intent_from_category(category):
    """Map 16 categories to 4 Gunas via quarters."""
    quarter = category // QUARTERS
    gunas = ["tamas", "rajas", "sattva", "suddha"]
    return gunas[quarter]


# Test corpus
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

print("=" * 80)
print("SHABDA-FIRST SEED: Phonetics lead, SHA256 is salt")
print("=" * 80)

correct = 0
total = len(tests)

cat_by_guna = {"tamas": [], "rajas": [], "sattva": [], "suddha": []}

for text, expected in tests:
    seed, cat, attr = shabda_first_seed(text)
    got = intent_from_category(cat)
    ok = got == expected
    if ok:
        correct += 1
    mark = "OK" if ok else "XX"
    cat_by_guna[expected].append(cat)
    print(f"  {mark}  cat={cat:>2} attr={attr:>6} got={got:>7} exp={expected:>6}  | {text[:42]}")

print(f"\nScore: {correct}/{total} = {100 * correct / total:.0f}%")

print("\nCategory distribution by expected guna:")
for guna, cats in cat_by_guna.items():
    quarters = [c // QUARTERS for c in cats]
    print(f"  {guna:>7}: cats={sorted(cats)}  quarters={sorted(quarters)}")

# Now test: does spell_cycle attractor cluster by semantic meaning?
print("\n" + "=" * 80)
print("ATTRACTOR CLUSTERING: Do similar-meaning texts get similar attractors?")
print("=" * 80)

groups = {
    "error": ["ERROR: fail", "FATAL: crash", "Exception thrown", "Bug found", "System down"],
    "warning": ["WARNING: slow", "Caution needed", "Deprecation notice", "TODO: fix", "Retry needed"],
    "success": ["SUCCESS: done", "All tests passed", "Deployment complete", "Build green", "Healthy"],
    "transcend": ["Unified harmony", "Optimal state", "Perfect balance", "Pure consciousness", "Liberation"],
}

for label, texts in groups.items():
    attractors = []
    cats = []
    for t in texts:
        _, cat, attr = shabda_first_seed(t)
        attractors.append(attr)
        cats.append(cat)
    print(f"  {label:>10}: cats={cats}  attractors={attractors}")
