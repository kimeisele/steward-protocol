"""
EXPERIMENT 26: Euclidean DTW + Scaled Templates + Real Profiles
================================================================

Combine the best findings:
- Exp 24: Real bootstrapped MFCC profiles (10x better than synthetic)
- Exp 25: Scaled templates (match audio segment length)
- Euclidean distance (better discrimination than cosine)
- Vowel anchor filtering (reduce candidates)

Key fix: Euclidean DTW with per-frame normalization (z-score) to handle
loudness variation. Normalize both audio and template MFCCs before DTW.
"""

import sys

sys.path.insert(0, ".")
import json
import math
import time

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream, _COMMON_ENGLISH
from vibe_core.mahamantra.sound.shabda_dtw import (
    segment_to_mfcc_matrix,
    extract_vowel_anchor_formants,
    _VOWEL_PARAMS,
    _silence_mfcc,
)

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
hop = int(stream.sample_rate * 10 / 1000)

# Load CMU dict
from nltk.corpus import cmudict

cmu = cmudict.dict()

# Load bootstrapped phoneme profiles
with open("vibe_core/mahamantra/data/phoneme_mfcc_profiles.json") as f:
    raw_profiles = json.load(f)

phoneme_profiles = {}
for phone, data in raw_profiles.items():
    phoneme_profiles[phone] = np.array(data["mean"])

# Duration weights
DUR = {
    "B": 1,
    "D": 1,
    "G": 1,
    "P": 1,
    "T": 1,
    "K": 1,
    "CH": 2,
    "JH": 2,
    "F": 2,
    "V": 2,
    "TH": 2,
    "DH": 2,
    "S": 3,
    "Z": 2,
    "SH": 3,
    "ZH": 2,
    "HH": 1,
    "M": 2,
    "N": 2,
    "NG": 2,
    "L": 2,
    "R": 2,
    "W": 2,
    "Y": 2,
    "AA": 4,
    "AE": 4,
    "AH": 3,
    "AO": 4,
    "AW": 5,
    "AY": 5,
    "EH": 3,
    "EY": 5,
    "ER": 4,
    "IH": 3,
    "IY": 4,
    "OW": 5,
    "OY": 5,
    "UH": 3,
    "UW": 4,
}

SIL = _silence_mfcc()

VOWELS = set(_VOWEL_PARAMS.keys())
VOWEL_NEIGHBORS = {
    "AA": {"AH", "AO", "AY", "AW"},
    "AE": {"EH", "AH", "AY"},
    "AH": {"AA", "ER", "AE", "AW", "AY"},
    "AO": {"AA", "OW", "AW"},
    "AW": {"AH", "AA", "UH", "AO"},
    "AY": {"AA", "AH", "AE"},
    "EH": {"AE", "IH", "EY", "AH"},
    "EY": {"EH", "IH", "IY"},
    "ER": {"AH", "UH", "IH"},
    "IH": {"IY", "EH", "EY", "AH"},
    "IY": {"IH", "EY"},
    "OW": {"AO", "UH", "UW"},
    "OY": {"AO", "OW"},
    "UH": {"UW", "AH", "ER", "OW"},
    "UW": {"UH", "OW"},
}


def build_template(phones: list, target_frames: int) -> np.ndarray:
    """Build scaled MFCC template."""
    if not phones:
        return np.array([SIL])
    weights = [DUR.get(p, 2) for p in phones]
    total_w = sum(weights)
    allocs = []
    remaining = target_frames
    for i, w in enumerate(weights):
        if i == len(weights) - 1:
            alloc = max(1, remaining)
        else:
            alloc = max(1, round(target_frames * w / total_w))
            alloc = min(alloc, remaining - (len(weights) - i - 1))
        allocs.append(alloc)
        remaining -= alloc
    frames = []
    for phone, n in zip(phones, allocs):
        vec = phoneme_profiles.get(phone, SIL)
        for _ in range(max(1, n)):
            frames.append(vec)
    return np.array(frames)


def normalize_mfcc(matrix: np.ndarray) -> np.ndarray:
    """Z-score normalize each MFCC coefficient across time (per-segment).

    This removes loudness/gain variation, focusing on spectral shape.
    C0 (energy) is kept but normalized, other coefficients capture shape.
    """
    if len(matrix) < 2:
        return matrix
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    std[std < 1e-6] = 1.0  # avoid division by zero
    return (matrix - mean) / std


def dtw_euclidean(audio: np.ndarray, template: np.ndarray) -> float:
    """DTW with Euclidean distance. Returns normalized cost."""
    n, m = len(audio), len(template)
    if n == 0 or m == 0:
        return float("inf")

    band = max(n, m) // 2 + 2  # wider band for scaled templates
    INF = 1e30
    # Use 1D array for memory efficiency
    prev = np.full(m + 1, INF)
    curr = np.full(m + 1, INF)
    prev[0] = 0.0

    for i in range(1, n + 1):
        curr[:] = INF
        j_lo = max(1, i * m // n - band)
        j_hi = min(m, i * m // n + band)
        for j in range(j_lo, j_hi + 1):
            d = np.sqrt(np.sum((audio[i - 1] - template[j - 1]) ** 2))
            curr[j] = d + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev

    return prev[m] / max(n, m)


def dtw_score(audio: np.ndarray, template: np.ndarray) -> float:
    """DTW → score [0, 1]. Exponential decay with tuned scale."""
    cost = dtw_euclidean(audio, template)
    if cost == float("inf"):
        return 0.0
    # After z-norm, typical Euclidean dist between matching frames ~0.5-2.0
    # Between non-matching ~2.0-4.0
    # Scale 2.0 gives: cost=1.0→0.61, cost=2.0→0.37, cost=3.0→0.22
    return math.exp(-cost / 2.0)


# Build vocabulary
EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = EXPECTED.lower().split()

vocab = set(_COMMON_ENGLISH)
vocab.update(expected_words)

word_phones = {}
for w in vocab:
    prons = cmu.get(w)
    if prons:
        word_phones[w] = [p.rstrip("012") for p in prons[0]]
    elif w == "eh":
        word_phones[w] = ["EH"]
    elif w == "krishna":
        word_phones[w] = ["K", "R", "IH", "SH", "N", "AH"]

print(f"Vocab: {len(word_phones)} | Profiles: {len(phoneme_profiles)} | Segments: {len(segments)}")
print()
print("=" * 70)

decoded = []
t_total = 0.0

for si, seg in enumerate(segments):
    ms_s, ms_e = seg.start * 10, seg.end * 10
    exp_w = expected_words[si] if si < len(expected_words) else "?"
    nf = len(seg.frames)

    # Audio MFCC
    seg_mfcc = stream.mfcc_frames[seg.start : seg.end] if stream.mfcc_frames else None
    audio = segment_to_mfcc_matrix(
        seg.frames,
        stream.raw_samples,
        stream.sample_rate,
        seg.start,
        hop,
        stream.n_fft,
        seg_mfcc,
    )
    audio_norm = normalize_mfcc(audio)

    # Vowel anchor
    anchor = extract_vowel_anchor_formants(
        seg.frames,
        stream.raw_samples,
        stream.sample_rate,
        seg.start,
        hop,
        stream.n_fft,
    )

    # Filter candidates
    cands = []
    for w, phones in word_phones.items():
        # Vowel filter
        if anchor:
            allowed = {anchor}
            allowed.update(VOWEL_NEIGHBORS.get(anchor, set()))
            w_vowels = {p for p in phones if p in VOWELS}
            if not (w_vowels & allowed):
                continue
        # Phoneme count filter (rough: ~3 frames per phoneme average)
        est = len(phones) * 3
        if est > nf * 3.5 or est < nf * 0.15:
            continue
        cands.append((w, phones))

    if not cands:
        cands = list(word_phones.items())

    # Score
    t0 = time.time()
    best_w, best_s = "?", 0.0
    debug = []

    for w, phones in cands:
        tmpl = build_template(phones, nf)
        tmpl_norm = normalize_mfcc(tmpl)
        s = dtw_score(audio_norm, tmpl_norm)
        debug.append((w, s))
        if s > best_s:
            best_s = s
            best_w = w

    t_total += time.time() - t0
    decoded.append(best_w)

    debug.sort(key=lambda x: -x[1])
    top5 = ", ".join(f"{w}:{s:.3f}" for w, s in debug[:5])
    m = "✓" if best_w == exp_w else " "
    print(
        f"  [{ms_s:5d}-{ms_e:5d}ms] {best_w:15s} ({best_s:.3f}) {m}  "
        f"exp={exp_w:15s}  anc={anchor or '?':3s}  cands={len(cands):3d}  [{top5}]"
    )

# Summary
print()
txt = " ".join(decoded)
exact = sum(1 for i, w in enumerate(decoded) if i < len(expected_words) and w == expected_words[i])
in_exp = sum(1 for w in decoded if w in set(expected_words))
print(f"DECODED:  {txt}")
print(f"EXPECTED: {EXPECTED}")
print(
    f"\nExact: {exact}/{min(len(decoded), len(expected_words))}  In expected: {in_exp}/{len(decoded)}  Time: {t_total:.1f}s"
)
