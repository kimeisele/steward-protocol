"""
EXPERIMENT 30: Log-Mel + Per-Band Maha Transform
==================================================

THE INSIGHT:
  MFCCs = Mel filterbank → log → DCT (linear!) → coefficients
  DCT decorrelates the mel bands, which is good for Gaussian classifiers
  but BAD for us because it linearizes the signal.

  The Mahamantra is non-linear (mod, square, feedback).
  Human hearing is non-linear (Mel scale).

  So: SKIP the DCT. Take the 26 log-mel energies directly.
  Then apply Maha transform PER BAND with cross-band feedback.
  This preserves the non-linear mel structure AND adds non-linear amplification.

TEST VARIANTS:
  A. Raw log-mel (26D) + Euclidean DTW (baseline — is log-mel already better than MFCC?)
  B. Log-mel → per-band maha_step (26D) + Euclidean DTW
  C. Log-mel → per-band maha_step with cross-band feedback (26D) + DTW
  D. Log-mel → full 16-step Maha transform per band (26D) + DTW
"""

import sys

sys.path.insert(0, ".")
import time
from collections import defaultdict

import numpy as np
from scipy.fft import fft

from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake,
    _mel_filterbank,
    N_FFT,
)
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from vibe_core.mahamantra.substrate.algorithm.maha import (
    maha_step,
    MahaModularSynth,
    MahaSynthParams,
    SYNTH_PRESETS,
    MAHA_16_STEPS,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    MAHAMANTRA_WORD_PATTERN,
    KSETRAJNA,
    SEVEN,
    TEN,
)

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
print(f"MAHA_QUANTUM = {MAHA_QUANTUM}")
print(f"Segments: {n_seg}, Pattern: {MAHAMANTRA_WORD_PATTERN}")
print()


def extract_log_mel(frame_data: np.ndarray, sr: int, n_fft: int = N_FFT, n_mels: int = 26) -> np.ndarray:
    """Extract 26 log-mel energies from audio frame (NO DCT)."""
    zeros = np.zeros(n_mels)
    if len(frame_data) < n_fft:
        return zeros
    emphasized = np.append(frame_data[0], frame_data[1:] - 0.97 * frame_data[:-1])
    windowed = emphasized[:n_fft] * np.hanning(n_fft)
    spec = np.abs(fft(windowed))[: n_fft // 2]
    power = (spec**2) / n_fft
    if np.sum(power) < 1e-10:
        return zeros
    fb = _mel_filterbank(sr, n_fft, n_mels)
    mel_energies = fb @ power
    mel_energies = np.maximum(mel_energies, 1e-10)
    return np.log(mel_energies)


def get_segment_logmel(seg_idx: int) -> np.ndarray:
    """Extract log-mel matrix [N × 26] for segment from raw audio."""
    seg = segments[seg_idx]
    frames = []
    for i in range(len(seg.frames)):
        abs_idx = seg.start + i
        start_sample = abs_idx * hop
        end_sample = start_sample + N_FFT
        if stream.raw_samples is not None and end_sample <= len(stream.raw_samples):
            audio_frame = stream.raw_samples[start_sample:end_sample]
            lm = extract_log_mel(audio_frame, stream.sample_rate)
            frames.append(lm)
        else:
            frames.append(np.zeros(26))
    return np.array(frames)


# Pre-extract all segments
all_logmel = [get_segment_logmel(i) for i in range(n_seg)]
print(f"Extracted log-mel for {n_seg} segments, shapes: {[m.shape for m in all_logmel[:3]]}...")
print()


# ==========================================================================
# Maha transform variants applied per-band
# ==========================================================================


def quantize_to_mod(val: float, mod: int = MAHA_QUANTUM) -> int:
    """Map a log-mel value (typically -23 to 0) into [0, mod-1]."""
    # log-mel range is roughly [-25, 2], map to [0, mod-1]
    normalized = (val + 25.0) / 27.0  # → [0, 1]
    normalized = max(0.0, min(1.0, normalized))
    return int(normalized * (mod - 1))


def maha_per_band(logmel_frame: np.ndarray) -> np.ndarray:
    """Apply single Maha step per band. No cross-band interaction."""
    result = np.zeros(len(logmel_frame))
    names = MAHAMANTRA_WORD_PATTERN  # H K H K | K K H H | H R H R | R R H H
    for i, val in enumerate(logmel_frame):
        seed = quantize_to_mod(val)
        name = names[i % len(names)]  # cycle through 16 names for 26 bands
        result[i] = maha_step(seed, name, MAHA_QUANTUM)
    return result


def maha_per_band_feedback(logmel_frame: np.ndarray) -> np.ndarray:
    """Apply Maha steps with cross-band feedback (like ModularSynth)."""
    result = np.zeros(len(logmel_frame))
    names = MAHAMANTRA_WORD_PATTERN
    feedback = 0
    for i, val in enumerate(logmel_frame):
        seed = (quantize_to_mod(val) + feedback) % MAHA_QUANTUM
        name = names[i % len(names)]
        transformed = maha_step(seed, name, MAHA_QUANTUM)
        result[i] = transformed
        feedback = (feedback + transformed) % MAHA_QUANTUM
    return result


synth = MahaModularSynth(default_preset="quantum")


def maha_full_transform(logmel_frame: np.ndarray) -> np.ndarray:
    """Full 16-step Maha transform per band."""
    result = np.zeros(len(logmel_frame))
    for i, val in enumerate(logmel_frame):
        seed = quantize_to_mod(val, MAHA_QUANTUM * 100)  # wider input space
        result[i] = synth.transform(seed)
    return result


# ==========================================================================
# DTW
# ==========================================================================


def dtw(a: np.ndarray, b: np.ndarray) -> float:
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


# ==========================================================================
# Run tests
# ==========================================================================

repeated = defaultdict(list)
for i in range(n_seg):
    repeated[TRANSCRIPT[i]].append(i)
repeated = {w: idxs for w, idxs in repeated.items() if len(idxs) > 1}


def run_variant(name: str, transform_fn=None):
    """Run nearest-neighbor self-matching test."""
    print(f"\n{'=' * 70}")
    print(f"VARIANT: {name}")
    print(f"{'=' * 70}")

    t0 = time.time()

    # Apply transform to all segments
    if transform_fn is None:
        feats = all_logmel  # raw log-mel
    else:
        feats = []
        for lm in all_logmel:
            transformed_frames = np.array([transform_fn(frame) for frame in lm])
            feats.append(transformed_frames)

    # Compute pairwise DTW
    costs = np.zeros((n_seg, n_seg))
    for i in range(n_seg):
        for j in range(i, n_seg):
            c = dtw(feats[i], feats[j])
            costs[i, j] = c
            costs[j, i] = c

    dt = time.time() - t0
    print(f"Computed in {dt:.1f}s")

    # Nearest neighbor
    nn_correct = 0
    print()
    for i in range(n_seg):
        ranked = sorted(range(n_seg), key=lambda j: costs[i, j])
        ranked = [j for j in ranked if j != i]
        nearest = TRANSCRIPT[ranked[0]]
        match = "✓" if nearest == TRANSCRIPT[i] else " "
        if nearest == TRANSCRIPT[i]:
            nn_correct += 1
        top3 = [(TRANSCRIPT[j], costs[i, j]) for j in ranked[:3]]
        top3_str = ", ".join(f"{w}:{c:.1f}" for w, c in top3)
        print(f"  {i:2d} [{TRANSCRIPT[i]:15s}] → {nearest:15s} {match}  [{top3_str}]")

    # Separation analysis
    same_d, diff_d = [], []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                same_d.append(costs[idxs[a], idxs[b]])
    for i in range(n_seg):
        for j in range(i + 1, n_seg):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                diff_d.append(costs[i, j])

    print(f"\n  NN accuracy: {nn_correct}/{n_seg}")
    if same_d and diff_d:
        print(f"  Same-word: mean={np.mean(same_d):.2f} [{np.min(same_d):.2f}, {np.max(same_d):.2f}]")
        print(f"  Diff-word: mean={np.mean(diff_d):.2f} [{np.min(diff_d):.2f}, {np.max(diff_d):.2f}]")
        sep = np.max(same_d) < np.min(diff_d)
        # Also compute discriminability: (mean_diff - mean_same) / std_pooled
        pooled_std = np.sqrt((np.var(same_d) + np.var(diff_d)) / 2) or 1
        discriminability = (np.mean(diff_d) - np.mean(same_d)) / pooled_std
        print(f"  Separation: {'YES!' if sep else 'NO'}  d-prime={discriminability:.2f}")


# A: Raw log-mel baseline
run_variant("A: Raw log-mel (26D) — no Maha")

# B: Per-band maha_step (no feedback)
run_variant("B: Per-band maha_step (no feedback)", maha_per_band)

# C: Per-band maha_step WITH cross-band feedback
run_variant("C: Per-band maha_step + cross-band feedback", maha_per_band_feedback)

# D: Full 16-step transform per band
run_variant("D: Full MahaModularSynth.transform per band", maha_full_transform)
