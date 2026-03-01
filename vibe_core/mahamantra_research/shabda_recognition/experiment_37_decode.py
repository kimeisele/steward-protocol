"""
EXPERIMENT 37: Phoneme Decoding + Temporal Smoothing
=====================================================

Takes the trained Tiny ASR from Exp 36 and improves the DECODING:
  1. Median smoothing (window=7) on predicted class indices
  2. Minimum-duration filter: each phoneme must last ≥3 frames (30ms)
  3. Phoneme sequence → word matching via pronunciation dictionary
  4. Viterbi-style decoding with transition costs

Frame accuracy was 75% — the model KNOWS the phonemes.
The problem is decoding them into a clean sequence.
"""

import sys

sys.path.insert(0, ".")
import json
import time

import numpy as np
from scipy.fft import fft

from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake,
    _mel_filterbank,
    N_FFT,
)
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

# =============================================================================
# 1. LOAD TRAINED MODEL
# =============================================================================

data = np.load(
    "vibe_core/mahamantra_research/shabda_recognition/tiny_asr_weights.npz",
    allow_pickle=True,
)
W1 = data["W1"]
b1 = data["b1"]
W2 = data["W2"]
b2 = data["b2"]
X_mean = data["X_mean"]
X_std = data["X_std"]
CLASSES = list(data["classes"])
CTX = int(data["context"])

N_CLASSES = len(CLASSES)
SILENCE = "SIL"
sil_idx = CLASSES.index(SILENCE) if SILENCE in CLASSES else -1

print(f"Loaded model: {W1.shape[0]}→{W1.shape[1]}→{W2.shape[1]}")
print(f"Classes ({N_CLASSES}): {CLASSES}")
print(f"Context: ±{CTX} frames")

# =============================================================================
# 2. EXTRACT FEATURES FROM TALK AUDIO
# =============================================================================

SR = 44100
N_MELS = 26
hop = int(SR * 10 / 1000)


def extract_log_mel(audio_frame, sr=SR, n_fft=N_FFT, n_mels=N_MELS):
    if len(audio_frame) < n_fft:
        return np.zeros(n_mels)
    emphasized = np.append(audio_frame[0], audio_frame[1:] - 0.97 * audio_frame[:-1])
    windowed = emphasized[:n_fft] * np.hanning(n_fft)
    spec = np.abs(fft(windowed))[: n_fft // 2]
    power = (spec**2) / n_fft
    if np.sum(power) < 1e-10:
        return np.zeros(n_mels)
    fb = _mel_filterbank(sr, n_fft, n_mels)
    mel_energies = fb @ power
    mel_energies = np.maximum(mel_energies, 1e-10)
    return np.log(mel_energies)


def add_context(X, ctx=2):
    N, D = X.shape
    X_ctx = np.zeros((N, (2 * ctx + 1) * D))
    for i in range(N):
        for k in range(-ctx, ctx + 1):
            j = max(0, min(N - 1, i + k))
            X_ctx[i, (k + ctx) * D : (k + ctx + 1) * D] = X[j]
    return X_ctx


print("\nExtracting features...")
intake = ShabdaIntake()
talk_stream = intake.process_file("temp/prabhupada-talk.wav")
n_talk = len(talk_stream.frames)

X_talk = []
for i in range(n_talk):
    start_sample = i * hop
    end_sample = start_sample + N_FFT
    if talk_stream.raw_samples is not None and end_sample <= len(talk_stream.raw_samples):
        audio = talk_stream.raw_samples[start_sample:end_sample]
        X_talk.append(extract_log_mel(audio))
    else:
        X_talk.append(np.zeros(N_MELS))
X_talk = np.array(X_talk)
X_ctx = add_context(X_talk, CTX)

# Normalize
X_norm = (X_ctx - X_mean) / X_std

# =============================================================================
# 3. RAW PREDICTIONS (frame-level)
# =============================================================================

print("Running inference...")
raw_preds = []
raw_probs = []
for i in range(n_talk):
    h = np.maximum(0, X_norm[i] @ W1 + b1)
    logits = h @ W2 + b2
    e = np.exp(logits - logits.max())
    p = e / e.sum()
    raw_preds.append(np.argmax(p))
    raw_probs.append(p)
raw_preds = np.array(raw_preds)
raw_probs = np.array(raw_probs)

print(f"Raw predictions: {n_talk} frames")

# =============================================================================
# 4. DECODING STRATEGIES
# =============================================================================

PRONUNCIATIONS = {
    "eh": ["EH"],
    "not": ["N", "AA", "T"],
    "exactly": ["IH", "G", "Z", "AE", "K", "T", "L", "IY"],
    "but": ["B", "AH", "T"],
    "i": ["AY"],
    "came": ["K", "EY", "M"],
    "to": ["T", "UW"],
    "preach": ["P", "R", "IY", "CH"],
    "the": ["DH", "AH"],
    "gospel": ["G", "AA", "S", "P", "AH", "L"],
    "of": ["AH", "V"],
    "krishna": ["K", "R", "IH", "SH", "N", "AH"],
    "consciousness": ["K", "AA", "N", "SH", "AH", "S", "N", "AH", "S"],
    "and": ["AE", "N", "D"],
    "fortunately": ["F", "AO", "R", "CH", "AH", "N", "AH", "T", "L", "IY"],
    "met": ["M", "EH", "T"],
    "some": ["S", "AH", "M"],
    "enthusiastic": ["EH", "N", "TH", "UW", "Z", "IY", "AE", "S", "T", "IH", "K"],
    "young": ["Y", "AH", "NG"],
    "boys": ["B", "OY", "Z"],
    "girls": ["G", "ER", "L", "Z"],
}

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

full_phonemes = []
for w in TRANSCRIPT:
    full_phonemes.extend(PRONUNCIATIONS[w])


def collapse(preds, classes, silence="SIL"):
    """CTC-style collapse: remove consecutive duplicates, then silence."""
    result = []
    prev = -1
    for p in preds:
        if p != prev:
            label = classes[p]
            if label != silence:
                result.append(label)
            prev = p
    return result


def levenshtein(s1, s2):
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[n][m]


print(f"\nGround truth: {' '.join(full_phonemes)}")
print(f"({len(full_phonemes)} phonemes)")

# --- Strategy A: Raw collapse ---
decoded_raw = collapse(raw_preds, CLASSES)
per_raw = levenshtein(decoded_raw, full_phonemes) / len(full_phonemes)
print(f"\n[A] Raw collapse: {len(decoded_raw)} phonemes, PER={per_raw:.1%}")
print(f"    {' '.join(decoded_raw[:50])}...")


# --- Strategy B: Median filter (window=7) + collapse ---
def median_filter(preds, window=7):
    N = len(preds)
    smoothed = preds.copy()
    half = window // 2
    for i in range(N):
        lo = max(0, i - half)
        hi = min(N, i + half + 1)
        segment = preds[lo:hi]
        # Most common value
        counts = np.bincount(segment, minlength=max(segment) + 1)
        smoothed[i] = np.argmax(counts)
    return smoothed


preds_median = median_filter(raw_preds, window=7)
decoded_median = collapse(preds_median, CLASSES)
per_median = levenshtein(decoded_median, full_phonemes) / len(full_phonemes)
print(f"\n[B] Median(7) + collapse: {len(decoded_median)} phonemes, PER={per_median:.1%}")
print(f"    {' '.join(decoded_median[:50])}...")

# --- Strategy C: Median(11) + min-duration(3) + collapse ---
preds_median11 = median_filter(raw_preds, window=11)


def min_duration_filter(preds, min_dur=3):
    """Remove phoneme segments shorter than min_dur frames."""
    N = len(preds)
    result = preds.copy()
    i = 0
    while i < N:
        j = i
        while j < N and preds[j] == preds[i]:
            j += 1
        seg_len = j - i
        if seg_len < min_dur and i > 0:
            # Replace short segment with previous phoneme
            result[i:j] = result[i - 1]
        i = j
    return result


preds_clean = min_duration_filter(preds_median11, min_dur=3)
decoded_clean = collapse(preds_clean, CLASSES)
per_clean = levenshtein(decoded_clean, full_phonemes) / len(full_phonemes)
print(f"\n[C] Median(11) + minDur(3) + collapse: {len(decoded_clean)} phonemes, PER={per_clean:.1%}")
print(f"    {' '.join(decoded_clean[:50])}...")


# --- Strategy D: Probability smoothing + collapse ---
# Instead of smoothing predicted classes, smooth the probability vectors
def smooth_probs(probs, window=9):
    """Moving average on probability vectors."""
    N = len(probs)
    smoothed = np.zeros_like(probs)
    half = window // 2
    for i in range(N):
        lo = max(0, i - half)
        hi = min(N, i + half + 1)
        smoothed[i] = probs[lo:hi].mean(axis=0)
    return smoothed


probs_smooth = smooth_probs(raw_probs, window=9)
preds_prob = np.argmax(probs_smooth, axis=1)
decoded_prob = collapse(preds_prob, CLASSES)
per_prob = levenshtein(decoded_prob, full_phonemes) / len(full_phonemes)
print(f"\n[D] ProbSmooth(9) + collapse: {len(decoded_prob)} phonemes, PER={per_prob:.1%}")
print(f"    {' '.join(decoded_prob[:50])}...")

# --- Strategy E: Prob smoothing + median + min-duration ---
preds_prob_med = median_filter(preds_prob, window=7)
preds_prob_clean = min_duration_filter(preds_prob_med, min_dur=4)
decoded_prob_clean = collapse(preds_prob_clean, CLASSES)
per_prob_clean = levenshtein(decoded_prob_clean, full_phonemes) / len(full_phonemes)
print(
    f"\n[E] ProbSmooth(9) + Median(7) + minDur(4) + collapse: {len(decoded_prob_clean)} phonemes, PER={per_prob_clean:.1%}"
)
print(f"    {' '.join(decoded_prob_clean[:50])}...")

# --- Strategy F: Wider prob smoothing + aggressive cleanup ---
probs_smooth15 = smooth_probs(raw_probs, window=15)
preds_p15 = np.argmax(probs_smooth15, axis=1)
preds_p15_med = median_filter(preds_p15, window=11)
preds_p15_clean = min_duration_filter(preds_p15_med, min_dur=5)
decoded_p15 = collapse(preds_p15_clean, CLASSES)
per_p15 = levenshtein(decoded_p15, full_phonemes) / len(full_phonemes)
print(f"\n[F] ProbSmooth(15) + Median(11) + minDur(5) + collapse: {len(decoded_p15)} phonemes, PER={per_p15:.1%}")
print(f"    {' '.join(decoded_p15)}")

# =============================================================================
# 5. WORD MATCHING: decoded phonemes → transcript words
# =============================================================================

print("\n" + "=" * 70)
print("WORD-LEVEL MATCHING")
print("=" * 70)

# Use best decoding strategy
best_strategies = [
    ("A-raw", decoded_raw, per_raw),
    ("B-median7", decoded_median, per_median),
    ("C-med11+dur3", decoded_clean, per_clean),
    ("D-probSmooth9", decoded_prob, per_prob),
    ("E-prob+med+dur", decoded_prob_clean, per_prob_clean),
    ("F-aggressive", decoded_p15, per_p15),
]
best_strategies.sort(key=lambda x: x[2])
print(f"\nBest strategy: {best_strategies[0][0]} (PER={best_strategies[0][2]:.1%})")

best_decoded = best_strategies[0][1]


# Try to match decoded phonemes against words in transcript
def match_words(decoded, vocab):
    """Greedy left-to-right matching of phonemes against word pronunciations."""
    words_found = []
    i = 0
    while i < len(decoded):
        best_word = None
        best_len = 0
        for word, phones in vocab.items():
            plen = len(phones)
            if i + plen <= len(decoded):
                # Count matching phonemes
                matches = sum(1 for a, b in zip(decoded[i : i + plen], phones) if a == b)
                # Allow 1 error per 3 phonemes
                if matches >= max(1, plen - plen // 3) and plen > best_len:
                    best_word = word
                    best_len = plen
        if best_word:
            words_found.append(best_word)
            i += best_len
        else:
            i += 1  # skip unmatched phoneme
    return words_found


words_matched = match_words(best_decoded, PRONUNCIATIONS)
print(f"\nMatched words: {' '.join(words_matched)}")
print(f"Ground truth:  {' '.join(TRANSCRIPT)}")

# Word-level accuracy
correct_words = 0
matched_set = list(words_matched)
for tw in TRANSCRIPT:
    if tw in matched_set:
        matched_set.remove(tw)
        correct_words += 1

word_acc = correct_words / len(TRANSCRIPT)
print(f"\nWord recall: {correct_words}/{len(TRANSCRIPT)} = {word_acc:.1%}")
print(f"Spurious words: {len(words_matched) - correct_words}")

# =============================================================================
# 6. SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Model: {W1.shape[0]}→{W1.shape[1]}→{W2.shape[1]} ({W1.size + b1.size + W2.size + b2.size} params)")
print(f"\nDecoding comparison:")
for name, dec, per in best_strategies:
    print(f"  {name:20s}: {len(dec):3d} phonemes, PER={per:.1%}")
print(f"\nGround truth: {len(full_phonemes)} phonemes")
print(f"Best PER: {best_strategies[0][2]:.1%} ({best_strategies[0][0]})")
print(f"Word recall: {word_acc:.1%}")
