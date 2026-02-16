"""
Test: Remnant Theorem (mod 17) on PHONETIC ENERGY for intent classification.

The key insight: SHA256 destroys Shabda. We must bypass SHA256 entirely.
Instead: text -> Shabda phonemes -> RAMA coords -> sum -> mod 17 -> intent class.

No SHA256. No keywords. Pure phonetic vibration through the Remnant Theorem.
"""

import sys
from vibe_core.mahamantra.substrate.phonetics.shabda import text_to_vibration
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT, COORD_VARGA, COORD_HARMONIC, IS_SHRUTI,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_KRISHNA, KSETRAJNA, TRINITY, NAVA,
)

KRISHNA = POSITION_SUM_KRISHNA  # 17


def phonetic_energy(text):
    """Text -> Shabda vibrations -> RAMA coords -> energy sum."""
    vibs = text_to_vibration(text)
    if not vibs:
        return 0
    coords = [v.signature_id % 49 for v in vibs]
    return sum(coords)


def phonetic_4d_signature(text):
    """Full 4D decomposition of phonetic energy."""
    vibs = text_to_vibration(text)
    if not vibs:
        return {"energy": 0, "element_sum": 0, "varga_sum": 0, "harmonic_sum": 0, "shruti_count": 0}
    coords = [v.signature_id % 49 for v in vibs]
    return {
        "energy": sum(coords),
        "element_sum": sum(COORD_ELEMENT[c].value for c in coords),
        "varga_sum": sum(COORD_VARGA[c] for c in coords),
        "harmonic_sum": sum(COORD_HARMONIC[c] for c in coords),
        "shruti_count": sum(1 for c in coords if IS_SHRUTI[c]),
        "n_phonemes": len(coords),
    }


def remnant_class(value):
    """Remnant Theorem: value mod 17."""
    r = value % KRISHNA
    labels = {0: "CLASSICAL", 1: "QUANTUM", 3: "TRINITY", 9: "NAVA"}
    return r, labels.get(r, f"OTHER_{r}")


# Test corpus: same as compression tests
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
print("REMNANT THEOREM INTENT TEST")
print(f"KRISHNA = {KRISHNA} (SEVEN + TEN = 17, PRIME)")
print("=" * 80)

# First: just look at the raw data. What does mod 17 produce?
print(f"\n{'Text':<50} {'Energy':>6} {'%17':>4} {'Class':<12} {'Expected':<8}")
print("-" * 90)

remnant_by_guna = {"tamas": [], "rajas": [], "sattva": [], "suddha": []}

for text, expected in tests:
    energy = phonetic_energy(text)
    r, label = remnant_class(energy)
    remnant_by_guna[expected].append(r)
    print(f"{text[:48]:<50} {energy:>6} {r:>4} {label:<12} {expected:<8}")

# Do the remnants cluster by guna?
print("\n" + "=" * 80)
print("REMNANT DISTRIBUTION BY GUNA")
print("=" * 80)
for guna, remnants in remnant_by_guna.items():
    print(f"  {guna:>7}: {sorted(remnants)}")

# Now try 4D decomposition
print("\n" + "=" * 80)
print("4D PHONETIC SIGNATURE")
print("=" * 80)
print(f"\n{'Text':<40} {'E':>4} {'El':>4} {'Va':>4} {'Ha':>4} {'Sh':>3} {'N':>3} {'E%17':>4} {'El%17':>5} {'Va%17':>5} {'Ha%17':>5}")
print("-" * 90)

for text, expected in tests:
    sig = phonetic_4d_signature(text)
    e = sig["energy"]
    el = sig["element_sum"]
    va = sig["varga_sum"]
    ha = sig["harmonic_sum"]
    sh = sig["shruti_count"]
    n = sig["n_phonemes"]
    print(f"{text[:38]:<40} {e:>4} {el:>4} {va:>4} {ha:>4} {sh:>3} {n:>3} {e%17:>4} {el%17:>5} {va%17:>5} {ha%17:>5}")

# Normalize by phoneme count to remove length bias
print("\n" + "=" * 80)
print("NORMALIZED (per phoneme) — removes length bias")
print("=" * 80)
print(f"\n{'Text':<40} {'E/N':>6} {'El/N':>6} {'Va/N':>6} {'Ha/N':>6} {'Sh%':>5} {'Exp':<8}")
print("-" * 80)

for text, expected in tests:
    sig = phonetic_4d_signature(text)
    n = sig["n_phonemes"] or 1
    e_n = sig["energy"] / n
    el_n = sig["element_sum"] / n
    va_n = sig["varga_sum"] / n
    ha_n = sig["harmonic_sum"] / n
    sh_pct = sig["shruti_count"] / n * 100
    print(f"{text[:38]:<40} {e_n:>6.1f} {el_n:>6.2f} {va_n:>6.2f} {ha_n:>6.1f} {sh_pct:>5.1f} {expected:<8}")
