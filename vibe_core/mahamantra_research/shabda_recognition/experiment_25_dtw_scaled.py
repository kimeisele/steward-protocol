"""
EXPERIMENT 25: DTW with Length-Scaled Templates
=================================================

Key insight from exp 24: fixed-duration phoneme templates create huge
length mismatches (5-frame template vs 14-frame audio). DTW can't fix
a 3x length mismatch without massive cost.

Fix: Scale each word template to approximately match the audio segment
length. If audio is 14 frames and "but" has 3 phonemes, scale each
phoneme's profile to fill ~14/3 ≈ 5 frames.

Also: use cosine distance instead of Euclidean for MFCC comparison.
MFCCs encode spectral shape; cosine similarity captures shape match
regardless of absolute magnitude (which varies with loudness).
"""

import sys

sys.path.insert(0, ".")
import json
import math
import time
from collections import defaultdict

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, extract_mfcc
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream,
    _COMMON_ENGLISH,
)
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

print(f"Loaded {len(phoneme_profiles)} phoneme MFCC profiles")


# =============================================================================
# SCALED TEMPLATE BUILDER
# =============================================================================

# Relative duration weights (how long each phoneme type lasts)
DURATION_WEIGHT = {
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

_SILENCE_VEC = _silence_mfcc()


def build_scaled_template(phones: list, target_frames: int) -> np.ndarray:
    """Build word MFCC template scaled to target frame count.

    Each phoneme's duration is proportional to its weight,
    scaled so total frames ≈ target_frames.
    """
    if not phones:
        return np.array([_SILENCE_VEC])

    weights = [DURATION_WEIGHT.get(p, 2) for p in phones]
    total_weight = sum(weights)

    # Allocate frames proportionally
    allocs = []
    remaining = target_frames
    for i, w in enumerate(weights):
        if i == len(weights) - 1:
            alloc = remaining
        else:
            alloc = max(1, round(target_frames * w / total_weight))
            alloc = min(alloc, remaining - (len(weights) - i - 1))
        allocs.append(max(1, alloc))
        remaining -= allocs[-1]

    # Build template: repeat each phoneme's MFCC for its allocated frames
    frames = []
    for phone, n in zip(phones, allocs):
        if phone in phoneme_profiles:
            vec = phoneme_profiles[phone]
        else:
            vec = _SILENCE_VEC
        for _ in range(n):
            frames.append(vec)

    return np.array(frames)


# =============================================================================
# COSINE DTW
# =============================================================================


def cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine distance between two vectors: 1 - cos(a, b)."""
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 1.0
    return 1.0 - dot / (na * nb)


def dtw_cosine(audio: np.ndarray, template: np.ndarray) -> float:
    """DTW with cosine distance. Returns normalized cost."""
    n = len(audio)
    m = len(template)
    if n == 0 or m == 0:
        return float("inf")

    band = max(n, m) // 3 + 1
    INF = 1e30
    cost = np.full((n + 1, m + 1), INF)
    cost[0, 0] = 0.0

    for i in range(1, n + 1):
        j_lo = max(1, i * m // n - band)
        j_hi = min(m, i * m // n + band)
        j_lo = max(1, j_lo)
        j_hi = min(m, j_hi)
        for j in range(j_lo, j_hi + 1):
            d = cosine_dist(audio[i - 1], template[j - 1])
            cost[i, j] = d + min(
                cost[i - 1, j],
                cost[i, j - 1],
                cost[i - 1, j - 1],
            )

    return cost[n, m] / max(n, m)


def dtw_cosine_score(audio: np.ndarray, template: np.ndarray) -> float:
    """Cosine DTW → similarity score [0, 1].

    Cosine distance per frame is in [0, 2]. Normalized DTW cost is in [0, ~2].
    Score = 1 - cost (clamped to [0, 1]).
    """
    cost = dtw_cosine(audio, template)
    if cost == float("inf"):
        return 0.0
    return max(0.0, 1.0 - cost)


# =============================================================================
# VOWEL ANCHOR FILTER
# =============================================================================

VOWEL_NEIGHBORS = {
    "AA": {"AH", "AO", "AY"},
    "AE": {"EH", "AH"},
    "AH": {"AA", "ER", "AE", "AW"},
    "AO": {"AA", "OW", "AW"},
    "AW": {"AH", "AA", "UH", "AO"},
    "AY": {"AA", "AH", "AE"},
    "EH": {"AE", "IH", "EY"},
    "EY": {"EH", "IH", "IY"},
    "ER": {"AH", "UH", "IH"},
    "IH": {"IY", "EH", "EY"},
    "IY": {"IH", "EY"},
    "OW": {"AO", "UH", "UW"},
    "OY": {"AO", "OW"},
    "UH": {"UW", "AH", "ER", "OW"},
    "UW": {"UH", "OW", "OO"},
}

VOWELS = set(_VOWEL_PARAMS.keys())


def vowel_filter(anchor: str, phones_list: list) -> bool:
    """Does this word contain the anchor vowel or a neighbor?"""
    allowed = {anchor}
    allowed.update(VOWEL_NEIGHBORS.get(anchor, set()))
    word_vowels = {p for p in phones_list if p in VOWELS}
    return bool(word_vowels & allowed)


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = EXPECTED.lower().split()

# Build vocabulary
vocab_words = set(_COMMON_ENGLISH)
vocab_words.update(expected_words)

word_phones = {}
for w in vocab_words:
    prons = cmu.get(w)
    if prons:
        word_phones[w] = [p.rstrip("012") for p in prons[0]]
    elif w == "eh":
        word_phones[w] = ["EH"]
    elif w == "krishna":
        word_phones[w] = ["K", "R", "IH", "SH", "N", "AH"]

print(f"Vocab: {len(word_phones)} words")
print()

print("=" * 70)
print("DTW WITH SCALED TEMPLATES + COSINE DISTANCE")
print("=" * 70)

decoded_words = []
total_time = 0.0

for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    expected = expected_words[si] if si < len(expected_words) else "?"
    n_frames = len(seg.frames)

    # Extract audio MFCC matrix
    seg_mfcc = None
    if stream.mfcc_frames is not None:
        seg_mfcc = stream.mfcc_frames[seg.start : seg.end]

    audio_mfcc = segment_to_mfcc_matrix(
        seg.frames,
        stream.raw_samples,
        stream.sample_rate,
        seg.start,
        hop,
        stream.n_fft,
        seg_mfcc,
    )

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
    candidates = []
    for w, phones in word_phones.items():
        # Vowel filter (if anchor available)
        if anchor and not vowel_filter(anchor, phones):
            continue
        # Rough phoneme-count filter: word should have reasonable length
        # ~3 frames per phoneme on average
        expected_frames = len(phones) * 3
        if expected_frames > n_frames * 3 or expected_frames < n_frames * 0.2:
            continue
        candidates.append((w, phones))

    if not candidates:
        # Fallback: no filter
        candidates = [(w, phones) for w, phones in word_phones.items()]

    # DTW scoring with scaled templates
    t0 = time.time()
    best_word = "?"
    best_score = 0.0
    scores_debug = []

    for w, phones in candidates:
        template = build_scaled_template(phones, n_frames)
        score = dtw_cosine_score(audio_mfcc, template)
        scores_debug.append((w, score))
        if score > best_score:
            best_score = score
            best_word = w

    total_time += time.time() - t0

    decoded_words.append(best_word)
    scores_debug.sort(key=lambda x: -x[1])
    top5 = scores_debug[:5]
    top5_str = ", ".join(f"{w}:{s:.3f}" for w, s in top5)

    match = "✓" if best_word == expected else " "
    print(
        f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} ({best_score:.3f}) {match}  "
        f"exp={expected:15s}  anc={anchor or '?':3s}  n_cand={len(candidates):3d}  "
        f"[{top5_str}]"
    )

# Summary
print()
print("=" * 70)
decoded_text = " ".join(decoded_words)
exact = sum(1 for i, w in enumerate(decoded_words) if i < len(expected_words) and w == expected_words[i])
in_exp = sum(1 for w in decoded_words if w in set(expected_words))

print(f"DECODED:   {decoded_text}")
print(f"EXPECTED:  {EXPECTED}")
print(f"\nExact position: {exact}/{min(len(decoded_words), len(expected_words))}")
print(f"In expected:    {in_exp}/{len(decoded_words)}")
print(f"Time: {total_time:.2f}s")
