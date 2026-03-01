"""
EXPERIMENT 27: Validate DTW on Japa Audio (Controlled Test)
=============================================================

Before trying to recognize English speech, validate that DTW on raw MFCCs
can distinguish KNOWN syllables in a KNOWN recording.

The japa recording has 6 syllables repeated: ha, re, kṛ, ṣṇa, rā, ma
(Hare Krishna mahamantra). shabda_bridge.json gives frame counts per syllable.

Test: Extract MFCC matrices for each syllable occurrence, then use DTW
to match each syllable against all 6 reference templates. If DTW can't
distinguish "ha" from "re" in this ideal case, it won't work for English.

This is the MINIMUM VIABLE TEST for the DTW approach.

Second test: Use word-level templates from the FIRST occurrence of each
syllable, then try to match the SECOND occurrence. This tests whether
DTW generalizes across repetitions of the same word by the same speaker.
"""

import sys

sys.path.insert(0, ".")
import json
import math

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, extract_mfcc

# Load japa audio
intake = ShabdaIntake()
stream = intake.process_file("temp/srila prabhupada japa clip.wav")

hop = int(stream.sample_rate * 10 / 1000)

# Load syllable boundaries from shabda_bridge.json
with open("vibe_core/mahamantra/data/shabda_bridge.json") as f:
    bridge = json.load(f)

meta = bridge["meta"]
syllables = bridge["syllables"]
chant_start = meta["chant_start_frame"]

print(f"Japa: {meta['duration_ms']}ms, {meta['n_frames']} frames, chant starts at frame {chant_start}")
print(f"Syllables: {list(syllables.keys())}")
print()

# The mahamantra pattern: ha re kṛ ṣṇa | ha re kṛ ṣṇa | ha re rā ma | ha re rā ma
# Total: 16 syllables per round. The japa clip has ~1 round (608 chant frames).
# shabda_bridge.json gives aggregate stats per syllable type, not per occurrence.
# But we know the pattern and can segment by the n_frames values.

# Each syllable's aggregate frame count:
# ha: 152, re: 153, kṛ: 76, ṣṇa: 76, rā: 76, ma: 76
# Total: 152+153+76+76+76+76 = 609 ≈ chant frames (608)

# The pattern has:
# 4x "ha" (38 frames each ≈ 152/4)
# 4x "re" (38 frames each ≈ 153/4)
# 2x "kṛ" (38 frames each ≈ 76/2)
# 2x "ṣṇa" (38 frames each ≈ 76/2)
# 2x "rā" (38 frames each ≈ 76/2)
# 2x "ma" (38 frames each ≈ 76/2)
# = 16 syllables × ~38 frames = 608

# Sequence: ha re kṛ ṣṇa ha re kṛ ṣṇa ha re rā ma ha re rā ma
SYLLABLE_SEQUENCE = [
    "ha",
    "re",
    "kṛ",
    "ṣṇa",
    "ha",
    "re",
    "kṛ",
    "ṣṇa",
    "ha",
    "re",
    "rā",
    "ma",
    "ha",
    "re",
    "rā",
    "ma",
]

# Each syllable is approximately equal length
n_syl = len(SYLLABLE_SEQUENCE)
chant_frames = meta["chant_end_frame"] - chant_start
frames_per_syl = chant_frames // n_syl

print(f"Chant frames: {chant_frames}, {n_syl} syllables, ~{frames_per_syl} frames each")
print()


def extract_segment_mfcc(start_frame: int, end_frame: int) -> np.ndarray:
    """Extract MFCC matrix for a frame range from the japa stream."""
    frames = []
    for fi in range(start_frame, end_frame):
        if stream.mfcc_frames and fi < len(stream.mfcc_frames):
            mfcc_ints = stream.mfcc_frames[fi]
            if any(c != 0 for c in mfcc_ints):
                frames.append(np.array([c / 100.0 for c in mfcc_ints]))
                continue

        # Fallback: extract from raw audio
        if stream.raw_samples is not None:
            start_sample = fi * hop
            end_sample = start_sample + stream.n_fft
            if end_sample <= len(stream.raw_samples):
                audio_frame = stream.raw_samples[start_sample:end_sample]
                mfcc_ints = extract_mfcc(audio_frame, stream.sample_rate, stream.n_fft)
                if any(c != 0 for c in mfcc_ints):
                    frames.append(np.array([c / 100.0 for c in mfcc_ints]))
                    continue

        frames.append(np.zeros(13))

    return np.array(frames) if frames else np.zeros((1, 13))


# Extract MFCC for each syllable occurrence
syllable_mfccs = []  # (label, mfcc_matrix)
for i, label in enumerate(SYLLABLE_SEQUENCE):
    start = chant_start + i * frames_per_syl
    end = start + frames_per_syl
    mfcc = extract_segment_mfcc(start, end)
    syllable_mfccs.append((label, mfcc))
    print(f"  Syl {i:2d}: {label:4s}  frames [{start}-{end}]  mfcc shape {mfcc.shape}")

print()


# DTW implementation (inline, Euclidean)
def dtw_cost(a: np.ndarray, b: np.ndarray) -> float:
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return float("inf")
    band = max(n, m) // 2 + 2
    INF = 1e30
    prev = np.full(m + 1, INF)
    curr = np.full(m + 1, INF)
    prev[0] = 0.0
    for i in range(1, n + 1):
        curr[:] = INF
        j_lo = max(1, i * m // n - band)
        j_hi = min(m, i * m // n + band)
        for j in range(j_lo, j_hi + 1):
            d = np.sqrt(np.sum((a[i - 1] - b[j - 1]) ** 2))
            curr[j] = d + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev
    return prev[m] / max(n, m)


# =============================================================================
# TEST 1: Build reference from FIRST occurrence, match ALL occurrences
# =============================================================================

print("=" * 70)
print("TEST 1: Match each syllable against first-occurrence references")
print("=" * 70)

# Build references from first occurrence of each unique syllable
unique_syls = ["ha", "re", "kṛ", "ṣṇa", "rā", "ma"]
references = {}  # label → mfcc_matrix (from first occurrence)
for label, mfcc in syllable_mfccs:
    if label not in references:
        references[label] = mfcc

print(f"References: {list(references.keys())}")
print()

# Match each occurrence
correct = 0
total = 0
confusion = {}  # (true, predicted) → count

for i, (true_label, test_mfcc) in enumerate(syllable_mfccs):
    costs = {}
    for ref_label, ref_mfcc in references.items():
        costs[ref_label] = dtw_cost(test_mfcc, ref_mfcc)

    predicted = min(costs, key=costs.get)
    is_correct = predicted == true_label
    if is_correct:
        correct += 1
    total += 1

    costs_sorted = sorted(costs.items(), key=lambda x: x[1])
    top3 = ", ".join(f"{l}:{c:.2f}" for l, c in costs_sorted[:3])

    mark = "✓" if is_correct else "✗"
    print(f"  Syl {i:2d} [{true_label:4s}] → {predicted:4s} {mark}  costs: [{top3}]")

    key = (true_label, predicted)
    confusion[key] = confusion.get(key, 0) + 1

print(f"\nAccuracy: {correct}/{total} = {correct / total * 100:.1f}%")

# Print confusion matrix
print("\nConfusion matrix:")
print(f"      {'  '.join(f'{l:4s}' for l in unique_syls)}")
for tl in unique_syls:
    row = []
    for pl in unique_syls:
        row.append(str(confusion.get((tl, pl), 0)))
    print(f"  {tl:4s} {'    '.join(f'{r:>2s}' for r in row)}")

# =============================================================================
# TEST 2: Leave-one-out cross-validation
# =============================================================================

print()
print("=" * 70)
print("TEST 2: Leave-one-out (use all OTHER occurrences as reference)")
print("=" * 70)

# For each syllable, compute its DTW cost against the AVERAGE of other
# occurrences of each syllable type

# Group by label
from collections import defaultdict

label_groups = defaultdict(list)
for i, (label, mfcc) in enumerate(syllable_mfccs):
    label_groups[label].append((i, mfcc))

correct2 = 0
total2 = 0

for i, (true_label, test_mfcc) in enumerate(syllable_mfccs):
    costs = {}
    for ref_label in unique_syls:
        # Use the nearest OTHER occurrence as reference
        other_mfccs = [m for j, m in label_groups[ref_label] if j != i]
        if not other_mfccs:
            # Only one occurrence — use it (it's the same, so cost ~0)
            other_mfccs = [m for _, m in label_groups[ref_label]]
        # Take minimum DTW cost across all other occurrences
        min_cost = float("inf")
        for ref_mfcc in other_mfccs:
            c = dtw_cost(test_mfcc, ref_mfcc)
            if c < min_cost:
                min_cost = c
        costs[ref_label] = min_cost

    predicted = min(costs, key=costs.get)
    is_correct = predicted == true_label
    if is_correct:
        correct2 += 1
    total2 += 1

    costs_sorted = sorted(costs.items(), key=lambda x: x[1])
    top3 = ", ".join(f"{l}:{c:.2f}" for l, c in costs_sorted[:3])
    mark = "✓" if is_correct else "✗"
    print(f"  Syl {i:2d} [{true_label:4s}] → {predicted:4s} {mark}  costs: [{top3}]")

print(f"\nLOO Accuracy: {correct2}/{total2} = {correct2 / total2 * 100:.1f}%")

# =============================================================================
# TEST 3: Drop C0 + add delta MFCCs
# =============================================================================

print()
print("=" * 70)
print("TEST 3: DTW with C0-dropped + delta MFCCs")
print("=" * 70)
print("C0 (energy) dominates Euclidean distance. Dropping it focuses on spectral shape.")
print("Delta MFCCs capture frame-to-frame transitions (key for consonants).")
print()


def add_deltas(mfcc: np.ndarray) -> np.ndarray:
    """Add delta (velocity) features: [N×D] → [N×2D].

    Delta at frame i = (frame[i+1] - frame[i-1]) / 2
    Edges: use forward/backward difference.
    """
    n = len(mfcc)
    if n < 2:
        return np.hstack([mfcc, np.zeros_like(mfcc)])
    deltas = np.zeros_like(mfcc)
    deltas[0] = mfcc[1] - mfcc[0]
    deltas[-1] = mfcc[-1] - mfcc[-2]
    for i in range(1, n - 1):
        deltas[i] = (mfcc[i + 1] - mfcc[i - 1]) / 2.0
    return np.hstack([mfcc, deltas])


def prepare_features(mfcc: np.ndarray) -> np.ndarray:
    """Drop C0, add deltas → [N × 24] feature matrix."""
    # Drop C0 (column 0)
    static = mfcc[:, 1:]  # [N × 12]
    # Add deltas
    return add_deltas(static)  # [N × 24]


# Re-extract with features
syllable_feats = [(label, prepare_features(mfcc)) for label, mfcc in syllable_mfccs]

# Build references from first occurrence
refs3 = {}
for label, feat in syllable_feats:
    if label not in refs3:
        refs3[label] = feat

# Test 3a: First-occurrence reference
correct3 = 0
total3 = 0
for i, (true_label, test_feat) in enumerate(syllable_feats):
    costs = {}
    for ref_label, ref_feat in refs3.items():
        costs[ref_label] = dtw_cost(test_feat, ref_feat)
    predicted = min(costs, key=costs.get)
    is_correct = predicted == true_label
    if is_correct:
        correct3 += 1
    total3 += 1
    costs_sorted = sorted(costs.items(), key=lambda x: x[1])
    top3 = ", ".join(f"{l}:{c:.2f}" for l, c in costs_sorted[:3])
    mark = "✓" if is_correct else "✗"
    print(f"  Syl {i:2d} [{true_label:4s}] → {predicted:4s} {mark}  costs: [{top3}]")

print(f"\nTest 3a (first-ref): {correct3}/{total3} = {correct3 / total3 * 100:.1f}%")

# Test 3b: Leave-one-out
correct3b = 0
total3b = 0
label_feat_groups = defaultdict(list)
for i, (label, feat) in enumerate(syllable_feats):
    label_feat_groups[label].append((i, feat))

for i, (true_label, test_feat) in enumerate(syllable_feats):
    costs = {}
    for ref_label in unique_syls:
        others = [f for j, f in label_feat_groups[ref_label] if j != i]
        if not others:
            others = [f for _, f in label_feat_groups[ref_label]]
        min_c = min(dtw_cost(test_feat, ref) for ref in others)
        costs[ref_label] = min_c
    predicted = min(costs, key=costs.get)
    is_correct = predicted == true_label
    if is_correct:
        correct3b += 1
    total3b += 1
    mark = "✓" if is_correct else "✗"
    costs_sorted = sorted(costs.items(), key=lambda x: x[1])
    top3 = ", ".join(f"{l}:{c:.2f}" for l, c in costs_sorted[:3])
    print(f"  Syl {i:2d} [{true_label:4s}] → {predicted:4s} {mark}  costs: [{top3}]")

print(f"\nTest 3b (LOO): {correct3b}/{total3b} = {correct3b / total3b * 100:.1f}%")
