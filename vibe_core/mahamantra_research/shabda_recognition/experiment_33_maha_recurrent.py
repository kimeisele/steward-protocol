"""
EXPERIMENT 33: Maha Recurrent Audio Fingerprint
=================================================

THE KEY INSIGHT:
  MahaModularSynth has FEEDBACK (feedback_acc). Each step's output
  affects the next step. This makes it a RECURRENT system.

  Previous experiments (exp 29) applied Maha to each frame INDEPENDENTLY.
  That's wrong — it's like running an RNN with hidden state reset every step.

  The correct approach: feed audio frames as a SEQUENCE through Maha,
  letting the feedback accumulate across frames. The final state after
  all frames encodes the entire acoustic trajectory.

  This is fundamentally different from DTW (which compares frame-by-frame)
  because it produces a SINGLE FINGERPRINT per segment that captures
  the temporal dynamics.

APPROACH:
  For each audio segment:
  1. Take packed frames (RMS, Varga, F0, Centroid) — already integers!
  2. Feed them sequentially as seeds into a modified Maha transform
     where feedback persists across frames
  3. The final (value, feedback_acc) pair = the segment fingerprint
  4. Compare fingerprints with simple Euclidean distance

  Also test: collect the VALUE at each of the 16 steps for each frame,
  giving a [N × 16] trajectory through Maha space.
"""

import sys

sys.path.insert(0, ".")
import time
from collections import defaultdict

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MAHA_16_STEPS,
    BINARY_PATTERN,
    SYNTH_PRESETS,
    MahaSynthParams,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    KSETRAJNA,
    SEVEN,
    TEN,
    WORDS,
    HALVES,
)
from vibe_core.mahamantra.protocols._seed import MAHA_OP_MAP as _OP_MAP
from vibe_core.mahamantra.protocols._seed import MAHA_MULT as _MULT
from vibe_core.mahamantra.protocols._seed import MAHA_ADD as _ADD
from vibe_core.mahamantra.protocols._seed import MAHA_SQ as _SQ

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

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
print(f"MAHA_QUANTUM = {MAHA_QUANTUM}, Segments: {n_seg}")
print()


def maha_recurrent_fingerprint(
    packed_frames: list,
    mod: int = MAHA_QUANTUM,
    preset: str = "quantum",
) -> tuple:
    """Feed audio frames sequentially through Maha with persistent feedback.

    Returns (final_value, final_feedback, trajectory_hash).
    """
    p = SYNTH_PRESETS[preset]

    # State persists across frames
    value = 0
    feedback_acc = 0
    trajectory = []  # collect intermediate values

    for frame_packed in packed_frames:
        rms, varga, f0_x10, centroid_100 = unpack_frame(frame_packed)

        # Use frame features to modulate the Maha transform
        # RMS → seed influence, F0 → phase_offset, Varga → operation selection
        frame_seed = (rms * 137 + f0_x10 * 7 + varga * 49 + centroid_100 * 13) % (mod * mod)

        # Mix frame seed with current state
        value = (value + frame_seed) % mod

        # Run one pass of 16 Maha steps with PERSISTENT feedback
        for step in MAHA_16_STEPS:
            effective_pos = ((step.position - KSETRAJNA + (varga % WORDS)) % WORDS) + KSETRAJNA

            lfo = 0
            if p.lfo_enabled:
                binary_val = BINARY_PATTERN[(step.position - KSETRAJNA) % WORDS]
                phase_in_lfo = (step.position - KSETRAJNA) % p.lfo_rate
                lfo = binary_val * phase_in_lfo

            adsr_table = (p.adsr_attack, p.adsr_decay, p.adsr_sustain, p.adsr_release)
            adsr = adsr_table[step.phase.value - KSETRAJNA]

            op = _OP_MAP[step.name]

            mult_coeff = (SEVEN * adsr, KSETRAJNA, KSETRAJNA)[op]
            add_coeff = (lfo, TEN + effective_pos + feedback_acc, feedback_acc)[op]

            v = (value * mult_coeff + add_coeff) % mod
            squared = (v * v) % mod
            value = _SQ[op] * squared + (KSETRAJNA - _SQ[op]) * v

            feedback_acc = (feedback_acc + value * p.feedback) % mod

        trajectory.append(value)

    # Hash the trajectory for additional discrimination
    traj_hash = 0
    for i, v in enumerate(trajectory):
        traj_hash = (traj_hash * 31 + v * (i + 1)) % (mod * mod * mod)

    return (value, feedback_acc, traj_hash, tuple(trajectory))


# =============================================================================
# TEST A: Single fingerprint per segment, compare Euclidean
# =============================================================================

print("=" * 70)
print("TEST A: Maha Recurrent Fingerprint (final state)")
print("=" * 70)

fps = []
for i in range(n_seg):
    seg = segments[i]
    val, fb, th, traj = maha_recurrent_fingerprint(list(seg.frames))
    fps.append((val, fb, th))
    print(f"  Seg {i:2d} [{TRANSCRIPT[i]:15s}] {len(seg.frames):3d}f → val={val:3d} fb={fb:3d} hash={th:6d}")

# Compare: fingerprint distance = Euclidean on (val, fb, hash)
print()
for i in range(n_seg):
    dists = []
    for j in range(n_seg):
        if i == j:
            continue
        d = np.sqrt(sum((a - b) ** 2 for a, b in zip(fps[i], fps[j])))
        dists.append((j, TRANSCRIPT[j], d))
    dists.sort(key=lambda x: x[2])
    nearest = dists[0][1]
    match = "✓" if nearest == TRANSCRIPT[i] else " "
    top3 = ", ".join(f"{w}:{d:.0f}" for _, w, d in dists[:3])
    print(f"  {i:2d} [{TRANSCRIPT[i]:15s}] → {nearest:15s} {match}  [{top3}]")


# =============================================================================
# TEST B: Trajectory DTW (compare Maha-space trajectories, not MFCC)
# =============================================================================

print()
print("=" * 70)
print("TEST B: Maha-space trajectory comparison")
print("=" * 70)
print("Instead of MFCC trajectories, compare Maha VALUE trajectories.")
print("Each frame produces one value in [0, 136]. DTW on these 1D sequences.")

trajs = []
for i in range(n_seg):
    seg = segments[i]
    _, _, _, traj = maha_recurrent_fingerprint(list(seg.frames))
    trajs.append(np.array(traj, dtype=float).reshape(-1, 1))


def dtw_1d(a, b):
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


print()
for i in range(n_seg):
    dists = []
    for j in range(n_seg):
        if i == j:
            continue
        d = dtw_1d(trajs[i], trajs[j])
        dists.append((j, TRANSCRIPT[j], d))
    dists.sort(key=lambda x: x[2])
    nearest = dists[0][1]
    match = "✓" if nearest == TRANSCRIPT[i] else " "
    top3 = ", ".join(f"{w}:{d:.1f}" for _, w, d in dists[:3])
    print(f"  {i:2d} [{TRANSCRIPT[i]:15s}] → {nearest:15s} {match}  [{top3}]")

# Separation analysis
repeated = defaultdict(list)
for i in range(n_seg):
    repeated[TRANSCRIPT[i]].append(i)
repeated = {w: idxs for w, idxs in repeated.items() if len(idxs) > 1}

if repeated:
    for test_name, data in [("A: fingerprint", fps), ("B: trajectory", trajs)]:
        if test_name == "A: fingerprint":

            def dist_fn(a, b):
                return np.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
        else:

            def dist_fn(a, b):
                return dtw_1d(a, b)

        same_d, diff_d = [], []
        for w, idxs in repeated.items():
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    same_d.append(dist_fn(data[idxs[a]], data[idxs[b]]))
        for i in range(n_seg):
            for j in range(i + 1, n_seg):
                if TRANSCRIPT[i] != TRANSCRIPT[j]:
                    diff_d.append(dist_fn(data[i], data[j]))

        print(f"\n  {test_name}:")
        print(f"    Same: mean={np.mean(same_d):.2f} [{np.min(same_d):.2f}, {np.max(same_d):.2f}]")
        print(f"    Diff: mean={np.mean(diff_d):.2f} [{np.min(diff_d):.2f}, {np.max(diff_d):.2f}]")
        sep = np.max(same_d) < np.min(diff_d)
        pooled_std = np.sqrt((np.var(same_d) + np.var(diff_d)) / 2) or 1
        dprime = (np.mean(diff_d) - np.mean(same_d)) / pooled_std
        print(f"    Separation: {'YES!' if sep else 'NO'}  d'={dprime:.2f}")


# =============================================================================
# TEST C: Multi-preset recurrent fingerprint
# =============================================================================

print()
print("=" * 70)
print("TEST C: Multi-preset recurrent fingerprint")
print("=" * 70)
print("Run each segment through multiple presets, concatenate states.")

PRESETS = ["quantum", "classical", "trinity", "pancha", "nava"]

multi_fps = []
for i in range(n_seg):
    seg = segments[i]
    combined = []
    for preset in PRESETS:
        val, fb, th, _ = maha_recurrent_fingerprint(list(seg.frames), preset=preset)
        combined.extend([val, fb, th])
    multi_fps.append(np.array(combined, dtype=float))
    if i < 5:
        print(f"  Seg {i:2d} [{TRANSCRIPT[i]:15s}] fp={combined[:6]}...")

print()
for i in range(n_seg):
    dists = []
    for j in range(n_seg):
        if i == j:
            continue
        d = np.sqrt(np.sum((multi_fps[i] - multi_fps[j]) ** 2))
        dists.append((j, TRANSCRIPT[j], d))
    dists.sort(key=lambda x: x[2])
    nearest = dists[0][1]
    match = "✓" if nearest == TRANSCRIPT[i] else " "
    top3 = ", ".join(f"{w}:{d:.0f}" for _, w, d in dists[:3])
    print(f"  {i:2d} [{TRANSCRIPT[i]:15s}] → {nearest:15s} {match}  [{top3}]")

if repeated:
    same_d, diff_d = [], []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                same_d.append(np.sqrt(np.sum((multi_fps[idxs[a]] - multi_fps[idxs[b]]) ** 2)))
    for i in range(n_seg):
        for j in range(i + 1, n_seg):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                diff_d.append(np.sqrt(np.sum((multi_fps[i] - multi_fps[j]) ** 2)))

    print(f"\n  Same: mean={np.mean(same_d):.0f} [{np.min(same_d):.0f}, {np.max(same_d):.0f}]")
    print(f"  Diff: mean={np.mean(diff_d):.0f} [{np.min(diff_d):.0f}, {np.max(diff_d):.0f}]")
    sep = np.max(same_d) < np.min(diff_d)
    pooled_std = np.sqrt((np.var(same_d) + np.var(diff_d)) / 2) or 1
    dprime = (np.mean(diff_d) - np.mean(same_d)) / pooled_std
    print(f"  Separation: {'YES!' if sep else 'NO'}  d'={dprime:.2f}")
