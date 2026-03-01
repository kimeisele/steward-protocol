"""
EXPERIMENT 29: Maha-Transform on Audio Features
=================================================

MFCCs are LINEAR (DCT). Words that sound slightly different have MFCCs
that are slightly different. DTW can't tell them apart (exp 28: 0/4).

The Maha Algorithm is NON-LINEAR (mod, square, feedback). It AMPLIFIES
small differences into large ones. Different seeds → completely different
attractor basins.

Test: Take the MFCC vectors from each audio segment, transform them
through MahaModularSynth, and check if the resulting attractor patterns
separate words better than raw MFCCs.

Multiple approaches:
  A. Per-frame: MFCC vector → pack into single int → maha_transform → attractor
  B. Per-segment: Average MFCC → pack → maha_transform → attractor
  C. Trajectory: Sequence of per-frame attractors → compare sequences
  D. Hash-like: Fold all 13 MFCCs into a single seed via XOR/mod → attractor
"""

import sys

sys.path.insert(0, ".")
import time
from collections import defaultdict

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MahaModularSynth,
    MahaAlgorithm16,
    MAHA_16_STEPS,
    maha_step,
    SYNTH_PRESETS,
)
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

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
synth = MahaModularSynth(default_preset="quantum")

print(f"MAHA_QUANTUM = {MAHA_QUANTUM}")
print(f"Segments: {n_seg}")
print()


def get_mfcc_frames(seg_idx: int) -> np.ndarray:
    """Get MFCC matrix [N × 13] for segment."""
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


# =============================================================================
# APPROACH A: Pack MFCC into seed → per-frame attractors → histogram
# =============================================================================

print("=" * 70)
print("APPROACH A: MFCC → seed → MahaSynth.transform → attractor histogram")
print("=" * 70)
print()


def mfcc_to_seed(mfcc_vec: np.ndarray) -> int:
    """Convert 13D MFCC vector to a single integer seed.

    Fold all coefficients via multiply-and-accumulate in mod space.
    Skip C0 (energy), use C1-C12 (spectral shape).
    """
    # Quantize to integers (MFCCs are typically in range -20 to +20)
    # Shift to positive, scale to 0-255 range
    quantized = np.clip((mfcc_vec[1:] + 20) * 6.375, 0, 255).astype(int)

    # Fold into single seed using prime-weighted accumulation
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    seed = 0
    for i, (q, p) in enumerate(zip(quantized, primes)):
        seed = (seed * p + q) % (MAHA_QUANTUM * MAHA_QUANTUM)  # mod 137²
    return seed % (MAHA_QUANTUM * 100)  # wider space for more attractors


def segment_attractor_histogram(seg_idx: int) -> dict:
    """Compute attractor histogram for a segment."""
    mfccs = get_mfcc_frames(seg_idx)
    hist = defaultdict(int)
    for vec in mfccs:
        if np.all(vec == 0):
            continue
        seed = mfcc_to_seed(vec)
        transformed = synth.transform(seed)
        hist[transformed] += 1
    return dict(hist)


# Compute histograms for all segments
hists = []
for i in range(n_seg):
    h = segment_attractor_histogram(i)
    hists.append(h)
    # Show compact representation
    top3 = sorted(h.items(), key=lambda x: -x[1])[:3]
    top3_str = ", ".join(f"{k}:{v}" for k, v in top3)
    print(f"  Seg {i:2d} [{TRANSCRIPT[i]:15s}] unique_attractors={len(h):3d}  top3=[{top3_str}]")


def hist_distance(a: dict, b: dict) -> float:
    """Cosine distance between two attractor histograms."""
    all_keys = set(a.keys()) | set(b.keys())
    if not all_keys:
        return 1.0
    va = np.array([a.get(k, 0) for k in all_keys], dtype=float)
    vb = np.array([b.get(k, 0) for k in all_keys], dtype=float)
    dot = np.dot(va, vb)
    na, nb = np.linalg.norm(va), np.linalg.norm(vb)
    if na < 1e-10 or nb < 1e-10:
        return 1.0
    return 1.0 - dot / (na * nb)


# Self-matching: nearest neighbor for repeated words
print()
print("  Nearest-neighbor matching (attractor histogram cosine distance):")
for i in range(n_seg):
    dists = []
    for j in range(n_seg):
        if i == j:
            continue
        d = hist_distance(hists[i], hists[j])
        dists.append((j, TRANSCRIPT[j], d))
    dists.sort(key=lambda x: x[2])
    top3 = dists[:3]
    top3_str = ", ".join(f"{w}:{d:.4f}" for _, w, d in top3)
    match = "✓" if top3[0][1] == TRANSCRIPT[i] else " "
    print(f"    Seg {i:2d} [{TRANSCRIPT[i]:15s}] → {top3[0][1]:15s} {match}  [{top3_str}]")

# Check repeated words
repeated = defaultdict(list)
for i in range(n_seg):
    repeated[TRANSCRIPT[i]].append(i)
repeated = {w: idxs for w, idxs in repeated.items() if len(idxs) > 1}

if repeated:
    same_dists, diff_dists = [], []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                same_dists.append(hist_distance(hists[idxs[a]], hists[idxs[b]]))
    for i in range(n_seg):
        for j in range(i + 1, n_seg):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                diff_dists.append(hist_distance(hists[i], hists[j]))

    print(
        f"\n  Same-word cosine dist: mean={np.mean(same_dists):.4f}  range=[{np.min(same_dists):.4f}, {np.max(same_dists):.4f}]"
    )
    print(
        f"  Diff-word cosine dist: mean={np.mean(diff_dists):.4f}  range=[{np.min(diff_dists):.4f}, {np.max(diff_dists):.4f}]"
    )
    sep = np.max(same_dists) < np.min(diff_dists)
    print(f"  Separation: {'YES!' if sep else 'NO (overlap)'}")


# =============================================================================
# APPROACH B: Multi-scale Maha — different presets give different views
# =============================================================================

print()
print("=" * 70)
print("APPROACH B: Multi-preset attractor fingerprint")
print("=" * 70)
print("Each preset is a different 'lens' on the same audio.")
print()

PRESETS = ["quantum", "classical", "trinity", "pancha", "nava", "wide"]


def multi_preset_fingerprint(seg_idx: int) -> np.ndarray:
    """Compute attractor histogram for each preset, concatenate into fingerprint."""
    mfccs = get_mfcc_frames(seg_idx)
    fingerprint = []

    for preset_name in PRESETS:
        local_synth = MahaModularSynth(default_preset=preset_name)
        params = SYNTH_PRESETS[preset_name]
        mod = params.mod_space

        hist = defaultdict(int)
        for vec in mfccs:
            if np.all(vec == 0):
                continue
            seed = mfcc_to_seed(vec)
            transformed = local_synth.transform(seed)
            hist[transformed] += 1

        # Convert to fixed-size vector (mod_space bins)
        vec = np.zeros(mod)
        total = sum(hist.values()) or 1
        for k, v in hist.items():
            vec[k % mod] += v / total
        fingerprint.append(vec)

    return np.concatenate(fingerprint)


# Compute fingerprints
fps = [multi_preset_fingerprint(i) for i in range(n_seg)]
fp_dim = len(fps[0])
print(f"Fingerprint dimension: {fp_dim}")

# Pairwise Euclidean distances
print("\n  Nearest-neighbor (multi-preset Euclidean):")
for i in range(n_seg):
    dists = []
    for j in range(n_seg):
        if i == j:
            continue
        d = np.sqrt(np.sum((fps[i] - fps[j]) ** 2))
        dists.append((j, TRANSCRIPT[j], d))
    dists.sort(key=lambda x: x[2])
    top3 = dists[:3]
    top3_str = ", ".join(f"{w}:{d:.3f}" for _, w, d in top3)
    match = "✓" if top3[0][1] == TRANSCRIPT[i] else " "
    print(f"    Seg {i:2d} [{TRANSCRIPT[i]:15s}] → {top3[0][1]:15s} {match}  [{top3_str}]")

if repeated:
    same_e, diff_e = [], []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                same_e.append(np.sqrt(np.sum((fps[idxs[a]] - fps[idxs[b]]) ** 2)))
    for i in range(n_seg):
        for j in range(i + 1, n_seg):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                diff_e.append(np.sqrt(np.sum((fps[i] - fps[j]) ** 2)))

    print(f"\n  Same-word Euclidean: mean={np.mean(same_e):.4f}  range=[{np.min(same_e):.4f}, {np.max(same_e):.4f}]")
    print(f"  Diff-word Euclidean: mean={np.mean(diff_e):.4f}  range=[{np.min(diff_e):.4f}, {np.max(diff_e):.4f}]")
    sep = np.max(same_e) < np.min(diff_e)
    print(f"  Separation: {'YES!' if sep else 'NO (overlap)'}")


# =============================================================================
# APPROACH C: Per-frame attractor SEQUENCE + DTW
# =============================================================================

print()
print("=" * 70)
print("APPROACH C: Per-frame attractor sequence + DTW")
print("=" * 70)
print("Each frame → seed → maha_transform → attractor value.")
print("Compare attractor sequences via DTW (1D integer sequences).")
print()


def segment_attractor_sequence(seg_idx: int) -> np.ndarray:
    """Frame-by-frame attractor sequence."""
    mfccs = get_mfcc_frames(seg_idx)
    seq = []
    for vec in mfccs:
        if np.all(vec == 0):
            seq.append(0)
            continue
        seed = mfcc_to_seed(vec)
        val = synth.transform(seed)
        seq.append(val)
    return np.array(seq, dtype=float).reshape(-1, 1)


seqs = [segment_attractor_sequence(i) for i in range(n_seg)]


def dtw_1d(a: np.ndarray, b: np.ndarray) -> float:
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
            d = abs(a[i - 1, 0] - b[j - 1, 0])
            curr[j] = d + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev
    return prev[m] / max(n, m)


print("  Nearest-neighbor (attractor sequence DTW):")
for i in range(n_seg):
    dists = []
    for j in range(n_seg):
        if i == j:
            continue
        d = dtw_1d(seqs[i], seqs[j])
        dists.append((j, TRANSCRIPT[j], d))
    dists.sort(key=lambda x: x[2])
    top3 = dists[:3]
    top3_str = ", ".join(f"{w}:{d:.1f}" for _, w, d in top3)
    match = "✓" if top3[0][1] == TRANSCRIPT[i] else " "
    print(f"    Seg {i:2d} [{TRANSCRIPT[i]:15s}] → {top3[0][1]:15s} {match}  [{top3_str}]")

if repeated:
    same_d, diff_d = [], []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                same_d.append(dtw_1d(seqs[idxs[a]], seqs[idxs[b]]))
    for i in range(n_seg):
        for j in range(i + 1, n_seg):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                diff_d.append(dtw_1d(seqs[i], seqs[j]))

    print(f"\n  Same-word DTW: mean={np.mean(same_d):.2f}  range=[{np.min(same_d):.2f}, {np.max(same_d):.2f}]")
    print(f"  Diff-word DTW: mean={np.mean(diff_d):.2f}  range=[{np.min(diff_d):.2f}, {np.max(diff_d):.2f}]")
    sep = np.max(same_d) < np.min(diff_d)
    print(f"  Separation: {'YES!' if sep else 'NO (overlap)'}")
