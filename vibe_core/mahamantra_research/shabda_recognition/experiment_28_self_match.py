"""
EXPERIMENT 28: Self-Matching Test — Can DTW Distinguish English Words?
=======================================================================

The definitive test: extract raw MFCC matrices from the known transcript
segments, then DTW-match each segment against ALL other segments.

If DTW can distinguish "but" from "came" from "preach" using raw MFCCs,
the approach is viable. If not, MFCC-DTW is fundamentally insufficient
for this audio and we need a different feature space.

We test multiple feature variants:
  A. Raw 13D MFCCs
  B. C1-C12 only (drop C0 energy)
  C. C1-C12 + deltas (24D)
  D. Log filterbank energies (26D, pre-DCT)
"""

import sys

sys.path.insert(0, ".")
import time

import numpy as np
from scipy.fft import dct, fft

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, extract_mfcc
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
hop = int(stream.sample_rate * 10 / 1000)

TRANSCRIPT = [
    "eh",
    "not",
    "exactly",
    "but",
    "i",
    "came",
    "to",
    "preach",
    "the",
    "gospel",
    "of",
    "krishna",
    "consciousness",
    "and",
    "fortunately",
    "i",
    "met",
    "some",
    "enthusiastic",
    "young",
    "boys",
    "and",
    "girls",
]

n_seg = min(len(segments), len(TRANSCRIPT))
print(f"Segments: {len(segments)}, using first {n_seg} with known transcript")
print()


def get_segment_mfcc(seg_idx: int) -> np.ndarray:
    """Extract MFCC matrix for segment from pre-computed stream."""
    seg = segments[seg_idx]
    frames = []
    for i in range(len(seg.frames)):
        abs_idx = seg.start + i
        if stream.mfcc_frames and abs_idx < len(stream.mfcc_frames):
            mfcc_ints = stream.mfcc_frames[abs_idx]
            if any(c != 0 for c in mfcc_ints):
                frames.append(np.array([c / 100.0 for c in mfcc_ints]))
                continue
        frames.append(np.zeros(13))
    return np.array(frames)


def dtw(a: np.ndarray, b: np.ndarray) -> float:
    """Standard Euclidean DTW, normalized by max(N,M)."""
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


def add_deltas(m: np.ndarray) -> np.ndarray:
    n = len(m)
    if n < 2:
        return np.hstack([m, np.zeros_like(m)])
    d = np.zeros_like(m)
    d[0] = m[1] - m[0]
    d[-1] = m[-1] - m[-2]
    for i in range(1, n - 1):
        d[i] = (m[i + 1] - m[i - 1]) / 2.0
    return np.hstack([m, d])


# Extract all segment MFCCs
seg_mfccs = [get_segment_mfcc(i) for i in range(n_seg)]


# Feature variants
def feat_raw(m):
    return m


def feat_no_c0(m):
    return m[:, 1:]


def feat_delta(m):
    return add_deltas(m[:, 1:])


def run_test(name: str, feat_fn):
    """Run self-matching test with given feature function."""
    print(f"\n{'=' * 70}")
    print(f"VARIANT: {name}")
    print(f"{'=' * 70}")

    feats = [feat_fn(m) for m in seg_mfccs]
    dim = feats[0].shape[1] if len(feats[0].shape) > 1 else 1
    print(f"Feature dim: {dim}")

    # Compute pairwise DTW cost matrix
    t0 = time.time()
    costs = np.zeros((n_seg, n_seg))
    for i in range(n_seg):
        for j in range(i, n_seg):
            c = dtw(feats[i], feats[j])
            costs[i, j] = c
            costs[j, i] = c
    dt = time.time() - t0
    print(f"DTW matrix: {dt:.1f}s")

    # For each segment, rank all others by DTW cost
    # Check if the "and" segments match each other, "i" segments match, etc.
    print()
    print(f"  {'Seg':>3s} {'Word':>15s} {'Frames':>6s}  Nearest (excl self)")
    print(f"  {'---':>3s} {'----':>15s} {'------':>6s}  ---------------------")

    # Words that appear more than once
    word_indices = {}
    for i in range(n_seg):
        w = TRANSCRIPT[i]
        word_indices.setdefault(w, []).append(i)

    repeated = {w: idxs for w, idxs in word_indices.items() if len(idxs) > 1}

    for i in range(n_seg):
        w = TRANSCRIPT[i]
        nf = len(segments[i].frames)

        # Rank others by cost
        ranked = sorted(range(n_seg), key=lambda j: costs[i, j])
        ranked = [j for j in ranked if j != i]  # exclude self

        top3 = [(TRANSCRIPT[j], costs[i, j]) for j in ranked[:3]]
        top3_str = ", ".join(f"{w2}:{c:.1f}" for w2, c in top3)

        # Is the nearest the same word?
        nearest_word = TRANSCRIPT[ranked[0]]
        match = "✓" if nearest_word == w else " "

        print(f"  {i:3d} {w:>15s} {nf:6d}  {match} [{top3_str}]")

    # Accuracy for repeated words: does the nearest neighbor have the same label?
    if repeated:
        print(f"\n  Repeated words: {list(repeated.keys())}")
        correct = 0
        total = 0
        for w, idxs in repeated.items():
            for i in idxs:
                ranked = sorted(range(n_seg), key=lambda j: costs[i, j])
                ranked = [j for j in ranked if j != i]
                nearest = TRANSCRIPT[ranked[0]]
                if nearest == w:
                    correct += 1
                total += 1
        print(f"  Repeated-word nearest-neighbor accuracy: {correct}/{total}")

    # Discrimination test: for "and" (appears twice), is the DTW cost between
    # the two "and"s lower than between "and" and other words?
    print()
    print("  Discrimination analysis (cost distribution):")
    all_same = []
    all_diff = []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                all_same.append(costs[idxs[a], idxs[b]])
    for i in range(n_seg):
        for j in range(i + 1, n_seg):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                all_diff.append(costs[i, j])

    if all_same and all_diff:
        print(
            f"    Same-word costs:  mean={np.mean(all_same):.2f}  min={np.min(all_same):.2f}  max={np.max(all_same):.2f}"
        )
        print(
            f"    Diff-word costs:  mean={np.mean(all_diff):.2f}  min={np.min(all_diff):.2f}  max={np.max(all_diff):.2f}"
        )
        # Is there separation?
        sep = np.min(all_diff) > np.max(all_same)
        overlap = not sep
        print(f"    Separation: {'YES' if sep else 'NO (overlap)'}")
        if overlap:
            # How much overlap?
            threshold = (np.mean(all_same) + np.mean(all_diff)) / 2
            same_below = sum(1 for c in all_same if c < threshold) / len(all_same)
            diff_above = sum(1 for c in all_diff if c > threshold) / len(all_diff)
            print(
                f"    At midpoint threshold {threshold:.2f}: same-below={same_below:.0%}, diff-above={diff_above:.0%}"
            )


# Run all variants
run_test("A: Raw 13D MFCCs", feat_raw)
run_test("B: C1-C12 (drop energy)", feat_no_c0)
run_test("C: C1-C12 + deltas (24D)", feat_delta)
