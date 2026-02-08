"""
RESEARCH: HKR Decomposition — The 3 Names as Basis-Vectors
============================================================

THESIS:
    Every vibration in the Mahamantra system is a MIXTURE of H, K, R.
    Like RGB colors: any color = (r, g, b). Any vibration = (h, k, r).

    H (Hare)    = Energy/Shakti   = v × 7 × adsr + lfo    (multiplication)
    K (Krishna) = Attraction       = v + 10 + pos + feedback (addition)
    R (Rama)    = Bliss/Output     = (v + feedback)²         (squaring)

    The 16 steps always apply the SAME pattern: HKHK KKHH HRHR RRHH
    But different SEEDS produce different DELTAS at each step.

    The HKR-proportion = how much each operation CHANGES the value.
    This is the fine-grained fingerprint WITHIN a basin.

WHAT WE MEASURE:
    For each RAMA coord (0-48), trace the 16-step trajectory.
    At each step, record: |value_after - value_before| for H, K, R separately.
    Sum the deltas: total_H_delta, total_K_delta, total_R_delta.
    Normalize: h = H/(H+K+R), k = K/(H+K+R), r = R/(H+K+R).

    This gives every coord an HKR-color: (h, k, r) where h+k+r = 1.

RUN: python3 -m vibe_core.mahamantra.research.hkr_decomposition
"""
from __future__ import annotations
import sys, os

from typing import Dict, List, Tuple

from vibe_core.mahamantra.substrate.algorithm.maha import (
    BINARY_PATTERN,
    MAHA_16_STEPS,
    MahaModularSynth,
    MahaSynthParams,
)
from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHA_OP_MAP,
    MAHA_SQ,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
    MAHAMANTRA_WORD_PATTERN,
    PANCHA,
    SEVEN,
    TEN,
    WORDS,
)
from vibe_core.mahamantra.substrate.basin_map import COORD_BASIN
from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, ELEMENT_NAMES
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL, rama_to_phoneme
from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast

# Step.name → short key mapping
_NAME_TO_KEY = {
    MAHAMANTRA_NAME_HARE: "H",
    MAHAMANTRA_NAME_KRISHNA: "K",
    MAHAMANTRA_NAME_RAMA: "R",
}
_OP_MAP = MAHA_OP_MAP
_SQ = MAHA_SQ


def hkr_trace(seed: int, mod_space: int = MAHA_QUANTUM) -> dict:
    """
    Trace a seed through all 16 steps, recording per-operation deltas.

    Returns:
        {
            "trajectory": [(step, name, value_before, value_after, delta), ...],
            "h_delta": total absolute delta from H steps,
            "k_delta": total absolute delta from K steps,
            "r_delta": total absolute delta from R steps,
            "hkr": (h, k, r) normalized proportions,
            "final": final value,
        }
    """
    p = MahaSynthParams(mod_space=mod_space, feedback=KSETRAJNA)
    value = seed % mod_space
    feedback_acc = 0
    trajectory = []
    deltas = {"H": 0, "K": 0, "R": 0}

    for step in MAHA_16_STEPS:
        effective_pos = ((step.position - KSETRAJNA + p.phase_offset) % WORDS) + KSETRAJNA

        lfo = 0
        if p.lfo_enabled:
            binary_val = BINARY_PATTERN[(step.position - KSETRAJNA) % WORDS]
            phase_in_lfo = (step.position - KSETRAJNA) % p.lfo_rate
            lfo = binary_val * phase_in_lfo

        adsr_table = (p.adsr_attack, p.adsr_decay, p.adsr_sustain, p.adsr_release)
        adsr = adsr_table[step.phase.value - KSETRAJNA]

        op = _OP_MAP[_NAME_TO_KEY[step.name]]
        mod = mod_space

        mult_coeff = (SEVEN * adsr, KSETRAJNA, KSETRAJNA)[op]
        add_coeff = (lfo, TEN + effective_pos + feedback_acc, feedback_acc)[op]

        v = (value * mult_coeff + add_coeff) % mod
        squared = (v * v) % mod
        new_value = _SQ[op] * squared + (KSETRAJNA - _SQ[op]) * v

        delta = abs(new_value - value)
        op_name = _NAME_TO_KEY[step.name]
        deltas[op_name] += delta

        trajectory.append((step.position, op_name, value, new_value, delta))

        value = new_value
        feedback_acc = (feedback_acc + value * p.feedback) % mod_space

    total = deltas["H"] + deltas["K"] + deltas["R"]
    if total == 0:
        hkr = (0.333, 0.333, 0.334)
    else:
        hkr = (deltas["H"] / total, deltas["K"] / total, deltas["R"] / total)

    return {
        "trajectory": trajectory,
        "h_delta": deltas["H"],
        "k_delta": deltas["K"],
        "r_delta": deltas["R"],
        "hkr": hkr,
        "final": value,
    }


# =============================================================================
# PART 1: HKR color for every RAMA coord
# =============================================================================
print("=" * 70)
print("PART 1: HKR COLOR for every RAMA coordinate (0-48)")
print("=" * 70)
print(f"\n  {'Coord':5s} {'Phon':4s} {'Elem':8s} {'Basin':5s} "
      f"{'H%':6s} {'K%':6s} {'R%':6s} {'Dominant':8s} {'H∆':6s} {'K∆':6s} {'R∆':6s}")
print(f"  {'─'*75}")

coord_hkr = {}
for c in range(VARNAMALA_TOTAL):
    trace = hkr_trace(c)
    h, k, r = trace["hkr"]
    coord_hkr[c] = (h, k, r)

    dominant = "HARE" if h >= k and h >= r else ("KRISHNA" if k >= r else "RAMA")
    phoneme = rama_to_phoneme(c)
    element = ELEMENT_NAMES[COORD_ELEMENT[c]]
    basin = COORD_BASIN[c]

    print(f"  {c:5d} {phoneme:4s} {element:8s} {basin:5d} "
          f"{h:5.1%} {k:5.1%} {r:5.1%} {dominant:8s} "
          f"{trace['h_delta']:6d} {trace['k_delta']:6d} {trace['r_delta']:6d}")

# =============================================================================
# PART 2: HKR uniqueness — how many unique HKR signatures?
# =============================================================================
print("\n" + "=" * 70)
print("PART 2: HKR UNIQUENESS — do different coords have different colors?")
print("=" * 70)

# Round to 2 decimal places for grouping
hkr_groups: Dict[Tuple[int, int, int], List[int]] = {}
for c, (h, k, r) in coord_hkr.items():
    key = (round(h * 100), round(k * 100), round(r * 100))
    hkr_groups.setdefault(key, []).append(c)

print(f"\n  {len(hkr_groups)} unique HKR signatures (rounded to 1%) from 49 coords")
for key in sorted(hkr_groups.keys()):
    members = hkr_groups[key]
    h, k, r = key
    phonemes = [rama_to_phoneme(c) for c in members]
    print(f"  H={h:2d}% K={k:2d}% R={r:2d}%: {len(members):2d} coords — {' '.join(phonemes[:10])}")

# =============================================================================
# PART 3: Divine names — HKR color comparison
# =============================================================================
print("\n" + "=" * 70)
print("PART 3: DIVINE NAMES — HKR color signatures")
print("=" * 70)

NAMES = {
    "hare": "harē", "krishna": "kṛṣṇa", "rama": "rāma",
    "jagannath": "jagannātha", "govinda": "gōvinda",
    "narayana": "nārāyaṇa", "prahlada": "prahlāda",
    "bhishma": "bhīṣma", "narada": "nārada",
    "parashurama": "paraśurāma", "bali": "bali",
    "kapila": "kapila",
}

name_hkr = {}
for name, iast in sorted(NAMES.items()):
    coords = encode_iast(iast)
    if not coords:
        continue

    # Per-syllable HKR
    syllable_hkr = [coord_hkr[c] for c in coords]

    # Name-level HKR: average of syllable HKRs
    avg_h = sum(s[0] for s in syllable_hkr) / len(syllable_hkr)
    avg_k = sum(s[1] for s in syllable_hkr) / len(syllable_hkr)
    avg_r = sum(s[2] for s in syllable_hkr) / len(syllable_hkr)

    name_hkr[name] = (avg_h, avg_k, avg_r)

    dominant = "HARE" if avg_h >= avg_k and avg_h >= avg_r else (
        "KRISHNA" if avg_k >= avg_r else "RAMA")

    print(f"\n  {name:15s} ({iast})")
    print(f"    HKR color: H={avg_h:.1%} K={avg_k:.1%} R={avg_r:.1%} → {dominant}")
    for i, c in enumerate(coords):
        h, k, r = coord_hkr[c]
        ph = rama_to_phoneme(c)
        print(f"      {ph:4s} (RAMA {c:2d}): H={h:.1%} K={k:.1%} R={r:.1%}")

# =============================================================================
# PART 4: fire vs agni — same basin, same HKR?
# =============================================================================
print("\n" + "=" * 70)
print("PART 4: CROSS-LANGUAGE HKR — fire vs agni, water vs jala, etc.")
print("=" * 70)

from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text

PAIRS = [
    ("fire", "agni"), ("water", "jala"), ("earth", "pṛthivī"),
    ("devotion", "bhakti"), ("surrender", "śaraṇāgati"),
    ("knowledge", "jñāna"), ("truth", "satya"), ("love", "prēma"),
    ("guru", "guru"), ("dharma", "dharma"),
]

for en, sk in PAIRS:
    en_coords = encode_text(en)
    sk_coords = encode_iast(sk)

    if not en_coords or not sk_coords:
        print(f"\n  {en:12s} / {sk:15s} — encoding failed")
        continue

    en_hkr_list = [coord_hkr.get(c, (0.33, 0.33, 0.34)) for c in en_coords]
    sk_hkr_list = [coord_hkr.get(c, (0.33, 0.33, 0.34)) for c in sk_coords]

    en_h = sum(s[0] for s in en_hkr_list) / len(en_hkr_list)
    en_k = sum(s[1] for s in en_hkr_list) / len(en_hkr_list)
    en_r = sum(s[2] for s in en_hkr_list) / len(en_hkr_list)

    sk_h = sum(s[0] for s in sk_hkr_list) / len(sk_hkr_list)
    sk_k = sum(s[1] for s in sk_hkr_list) / len(sk_hkr_list)
    sk_r = sum(s[2] for s in sk_hkr_list) / len(sk_hkr_list)

    # HKR distance (Euclidean in 3D)
    dist = ((en_h - sk_h)**2 + (en_k - sk_k)**2 + (en_r - sk_r)**2) ** 0.5
    similarity = max(0, 1.0 - dist * 2)  # Scale: 0 = opposite, 1 = identical

    print(f"\n  {en:12s} H={en_h:.1%} K={en_k:.1%} R={en_r:.1%}")
    print(f"  {sk:12s} H={sk_h:.1%} K={sk_k:.1%} R={sk_r:.1%}")
    print(f"  HKR similarity: {similarity:.2f}  (distance: {dist:.4f})")

# =============================================================================
# PART 5: The Mahamantra itself — HKR per position
# =============================================================================
print("\n" + "=" * 70)
print("PART 5: THE MAHAMANTRA — HKR color per position")
print("=" * 70)

MANTRA = [
    "harē", "kṛṣṇa", "harē", "kṛṣṇa",
    "kṛṣṇa", "kṛṣṇa", "harē", "harē",
    "harē", "rāma", "harē", "rāma",
    "rāma", "rāma", "harē", "harē",
]

print(f"\n  {'Pos':3s} {'Word':9s} {'Op':3s} {'H%':6s} {'K%':6s} {'R%':6s} {'Dominant':8s}")
print(f"  {'─'*50}")

total_h = total_k = total_r = 0.0
n_syllables = 0

for pos in range(16):
    word = MANTRA[pos]
    op = MAHAMANTRA_WORD_PATTERN[pos]
    coords = encode_iast(word)
    if not coords:
        continue

    syllable_hkr = [coord_hkr[c] for c in coords]
    avg_h = sum(s[0] for s in syllable_hkr) / len(syllable_hkr)
    avg_k = sum(s[1] for s in syllable_hkr) / len(syllable_hkr)
    avg_r = sum(s[2] for s in syllable_hkr) / len(syllable_hkr)

    total_h += avg_h * len(coords)
    total_k += avg_k * len(coords)
    total_r += avg_r * len(coords)
    n_syllables += len(coords)

    dominant = "HARE" if avg_h >= avg_k and avg_h >= avg_r else (
        "KRISHNA" if avg_k >= avg_r else "RAMA")

    print(f"  {pos+1:3d} {word:9s} {op:3s} {avg_h:5.1%} {avg_k:5.1%} {avg_r:5.1%} {dominant}")

if n_syllables > 0:
    print(f"\n  MAHAMANTRA TOTAL HKR COLOR:")
    print(f"    H = {total_h/n_syllables:.1%}")
    print(f"    K = {total_k/n_syllables:.1%}")
    print(f"    R = {total_r/n_syllables:.1%}")

# =============================================================================
# PART 6: Basin × HKR — does HKR differentiate WITHIN basins?
# =============================================================================
print("\n" + "=" * 70)
print("PART 6: BASIN × HKR — differentiation within basins")
print("=" * 70)

from collections import defaultdict
basin_hkr_spread: Dict[int, List[Tuple[float, float, float]]] = defaultdict(list)

for c in range(VARNAMALA_TOTAL):
    basin = COORD_BASIN[c]
    basin_hkr_spread[basin].append(coord_hkr[c])

for basin in sorted(basin_hkr_spread.keys()):
    members = basin_hkr_spread[basin]
    h_vals = [m[0] for m in members]
    k_vals = [m[1] for m in members]
    r_vals = [m[2] for m in members]

    h_range = max(h_vals) - min(h_vals)
    k_range = max(k_vals) - min(k_vals)
    r_range = max(r_vals) - min(r_vals)

    print(f"\n  Basin {basin:3d} ({len(members)} coords):")
    print(f"    H range: {min(h_vals):.1%} — {max(h_vals):.1%} (spread: {h_range:.1%})")
    print(f"    K range: {min(k_vals):.1%} — {max(k_vals):.1%} (spread: {k_range:.1%})")
    print(f"    R range: {min(r_vals):.1%} — {max(r_vals):.1%} (spread: {r_range:.1%})")

print("\nDONE.")
