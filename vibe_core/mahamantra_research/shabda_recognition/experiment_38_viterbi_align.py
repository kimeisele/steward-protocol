"""
EXPERIMENT 38: Viterbi Forced Alignment
========================================

The proper way to do forced alignment:
  - We know the EXACT phoneme sequence from the transcript
  - We have per-frame emission probabilities from the Tiny ASR
  - Viterbi finds the OPTIMAL segmentation: which frames belong to which phoneme

This is NOT free decoding. We constrain the path to follow the known
phoneme sequence. The only degree of freedom is TIMING: when does
each phoneme start and end?

This is how industrial forced aligners (MFA, Kaldi) work internally.

Architecture:
  States = phoneme sequence (with repeated states for duration)
  Transitions = stay-in-same-phoneme OR advance-to-next
  Emissions = Tiny ASR probability for that phoneme at that frame
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
# 1. LOAD MODEL + EXTRACT FEATURES
# =============================================================================

data = np.load(
    "vibe_core/mahamantra_research/shabda_recognition/tiny_asr_weights.npz",
    allow_pickle=True,
)
W1, b1 = data["W1"], data["b1"]
W2, b2 = data["W2"], data["b2"]
X_mean, X_std = data["X_mean"], data["X_std"]
CLASSES = list(data["classes"])
CTX = int(data["context"])
N_CLASSES = len(CLASSES)

# Build class index
c2i = {c: i for i, c in enumerate(CLASSES)}

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


print("Extracting features...")
intake = ShabdaIntake()
talk_stream = intake.process_file("temp/prabhupada-talk.wav")
n_talk = len(talk_stream.frames)

X_talk = []
for i in range(n_talk):
    start_sample = i * hop
    end_sample = start_sample + N_FFT
    if talk_stream.raw_samples is not None and end_sample <= len(talk_stream.raw_samples):
        X_talk.append(extract_log_mel(talk_stream.raw_samples[start_sample:end_sample]))
    else:
        X_talk.append(np.zeros(N_MELS))
X_talk = np.array(X_talk)
X_ctx = add_context(X_talk, CTX)
X_norm = (X_ctx - X_mean) / X_std

# Get frame-level probabilities
print("Running inference...")
frame_probs = np.zeros((n_talk, N_CLASSES))
for i in range(n_talk):
    h = np.maximum(0, X_norm[i] @ W1 + b1)
    logits = h @ W2 + b2
    e = np.exp(logits - logits.max())
    frame_probs[i] = e / e.sum()

print(f"Frame probs: {frame_probs.shape}")

# =============================================================================
# 2. TRANSCRIPT → PHONEME SEQUENCE
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

SILENCE = "SIL"

# Build phoneme sequence WITH silence between words
# Each state = one phoneme (or silence)
states = []  # list of (phoneme, word, state_type)
for wi, word in enumerate(TRANSCRIPT):
    if wi > 0:
        states.append((SILENCE, "_pause_", "silence"))
    phones = PRONUNCIATIONS[word]
    for pi, p in enumerate(phones):
        states.append((p, word, "phoneme"))

N_STATES = len(states)
print(f"\nViterbi states: {N_STATES}")
print(f"Frames: {n_talk}")

# =============================================================================
# 3. VITERBI FORCED ALIGNMENT
# =============================================================================
# State machine:
#   - Each state is one phoneme in the sequence
#   - Transitions: SELF (stay) or NEXT (advance to next phoneme)
#   - Emission: log P(phoneme | frame) from Tiny ASR
#
# Constraints:
#   - Must start at state 0
#   - Must end at state N_STATES-1
#   - Can only go forward (no skipping states, no going back)
#   - Minimum 1 frame per state (implicit in Viterbi)

print("\nRunning Viterbi alignment...")
t0 = time.time()

# Log probabilities for numerical stability
log_probs = np.log(frame_probs + 1e-30)

# Transition probabilities (log space)
# Self-transition: higher for vowels/silence, lower for stops
SELF_PROB = 0.7  # P(stay in same phoneme)
ADVANCE_PROB = 0.3  # P(advance to next phoneme)

log_self = np.log(SELF_PROB)
log_advance = np.log(ADVANCE_PROB)

# Viterbi: V[t, s] = best log-prob of being in state s at time t
V = np.full((n_talk, N_STATES), -np.inf)
BP = np.zeros((n_talk, N_STATES), dtype=np.int32)  # backpointer


# Get emission log-prob for each state at each frame
def emission(t, s):
    """Log P(frame_t | state_s)."""
    phone = states[s][0]
    if phone in c2i:
        return log_probs[t, c2i[phone]]
    else:
        return -10.0  # unknown phoneme, very low prob


# Initialize: t=0, must be in state 0
V[0, 0] = emission(0, 0)

# Fill forward
for t in range(1, n_talk):
    for s in range(N_STATES):
        # Option 1: came from same state (self-transition)
        score_self = V[t - 1, s] + log_self + emission(t, s)

        # Option 2: came from previous state (advance)
        if s > 0:
            score_adv = V[t - 1, s - 1] + log_advance + emission(t, s)
        else:
            score_adv = -np.inf

        if score_self >= score_adv:
            V[t, s] = score_self
            BP[t, s] = s
        else:
            V[t, s] = score_adv
            BP[t, s] = s - 1

        # Also allow skipping silence states (jump from s-2 to s)
        # This handles cases where pause is very short
        if s >= 2 and states[s - 1][2] == "silence":
            score_skip = V[t - 1, s - 2] + log_advance + emission(t, s) - 1.0  # penalty
            if score_skip > V[t, s]:
                V[t, s] = score_skip
                BP[t, s] = s - 2

# Backtrace from last frame, last state
state_path = np.zeros(n_talk, dtype=np.int32)
state_path[-1] = N_STATES - 1

# Find the best ending state (might not reach last state)
# Allow ending in the last few states
best_end = N_STATES - 1
for s in range(max(0, N_STATES - 5), N_STATES):
    if V[-1, s] > V[-1, best_end]:
        best_end = s
state_path[-1] = best_end

for t in range(n_talk - 2, -1, -1):
    state_path[t] = BP[t + 1, state_path[t + 1]]

dt = time.time() - t0
print(f"Viterbi done in {dt:.1f}s")
print(f"Final state: {state_path[-1]}/{N_STATES - 1} ({states[state_path[-1]][0]} in '{states[state_path[-1]][1]}')")

# =============================================================================
# 4. EXTRACT ALIGNMENT RESULTS
# =============================================================================

# Frame → phoneme/word labels
viterbi_labels = [states[s][0] for s in state_path]
viterbi_words = [states[s][1] for s in state_path]

# Show word boundaries
print(f"\nWord boundaries (Viterbi):")
prev_w = ""
word_starts = []
for i in range(n_talk):
    w = viterbi_words[i]
    if w != prev_w and w != "_pause_":
        word_starts.append((i, w))
        prev_w = w if w != "_pause_" else prev_w

for start, word in word_starts:
    # Find end
    end = start
    while end < n_talk and viterbi_words[end] == word:
        end += 1
    dur = (end - start) * 10
    print(f"  {start * 10:5d}-{end * 10:5d}ms ({dur:4d}ms): {word}")

# =============================================================================
# 5. COMPARE WITH PREVIOUS ALIGNMENT
# =============================================================================

# Phoneme sequence from Viterbi
viterbi_phonemes = []
prev_p = ""
for p in viterbi_labels:
    if p != prev_p and p != SILENCE:
        viterbi_phonemes.append(p)
        prev_p = p
    elif p == SILENCE:
        prev_p = p

full_phonemes = []
for w in TRANSCRIPT:
    full_phonemes.extend(PRONUNCIATIONS[w])


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


per = levenshtein(viterbi_phonemes, full_phonemes) / len(full_phonemes)
print(f"\nViterbi decoded: {len(viterbi_phonemes)} phonemes")
print(f"Ground truth:    {len(full_phonemes)} phonemes")
print(f"PER: {per:.1%}")

print(f"\nDecoded: {' '.join(viterbi_phonemes)}")
print(f"Truth:   {' '.join(full_phonemes)}")

# Word-level: check if word boundaries make sense
print(f"\nWord-level analysis:")
print(f"  Words found: {len(word_starts)}")
print(f"  Expected:    {len(TRANSCRIPT)}")

matched = 0
found_words = [w for _, w in word_starts]
for tw in TRANSCRIPT:
    if tw in found_words:
        found_words.remove(tw)
        matched += 1
print(f"  Word recall: {matched}/{len(TRANSCRIPT)} = {matched / len(TRANSCRIPT):.1%}")

# =============================================================================
# 6. RE-TRAIN WITH VITERBI LABELS (better alignment → better model)
# =============================================================================

print("\n" + "=" * 70)
print("RE-TRAINING WITH VITERBI LABELS")
print("=" * 70)

# The key insight: Viterbi alignment constrains the labels to follow
# the correct phoneme sequence. So even if frame-level probs are noisy,
# the LABELS are guaranteed to be in the right order.

CLASSES_V = sorted(set(viterbi_labels))
N_CLASSES_V = len(CLASSES_V)
c2i_v = {c: i for i, c in enumerate(CLASSES_V)}
y_v = np.array([c2i_v[l] for l in viterbi_labels])

# Re-normalize (same features, new labels)
D_in = X_ctx.shape[1]
HIDDEN = 128
rng = np.random.RandomState(MAHA_QUANTUM)
W1_new = rng.randn(D_in, HIDDEN).astype(np.float64) * np.sqrt(2.0 / D_in)
b1_new = np.zeros(HIDDEN)
W2_new = rng.randn(HIDDEN, N_CLASSES_V).astype(np.float64) * np.sqrt(2.0 / HIDDEN)
b2_new = np.zeros(N_CLASSES_V)

X_mean_new = X_ctx.mean(axis=0)
X_std_new = X_ctx.std(axis=0) + 1e-8
X_norm_new = (X_ctx - X_mean_new) / X_std_new

# Training
LR = 0.01
EPOCHS = 400
BS = 128
indices = np.arange(n_talk)

for epoch in range(EPOCHS):
    rng.shuffle(indices)
    total_loss = 0.0
    correct = 0

    for bs in range(0, n_talk, BS):
        bi = indices[bs : bs + BS]
        bx = X_norm_new[bi]
        by = y_v[bi]
        B = len(bi)

        h = np.maximum(0, bx @ W1_new + b1_new)
        logits = h @ W2_new + b2_new
        e = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)

        targets = np.zeros((B, N_CLASSES_V))
        targets[np.arange(B), by] = 1.0

        loss = -np.sum(targets * np.log(probs + 1e-10)) / B
        total_loss += loss * B
        correct += np.sum(np.argmax(probs, axis=1) == by)

        d_logits = (probs - targets) / B
        dW2 = h.T @ d_logits
        db2 = d_logits.sum(axis=0)
        d_h = d_logits @ W2_new.T
        d_h[h <= 0] = 0
        dW1 = bx.T @ d_h
        db1 = d_h.sum(axis=0)

        W1_new -= LR * dW1
        b1_new -= LR * db1
        W2_new -= LR * dW2
        b2_new -= LR * db2

    if epoch % 50 == 0 or epoch == EPOCHS - 1:
        acc = correct / n_talk
        print(f"  Epoch {epoch:3d}: loss={total_loss / n_talk:.4f}  acc={acc:.1%}")

# =============================================================================
# 7. SECOND VITERBI PASS (with retrained model)
# =============================================================================

print("\nSecond Viterbi pass with retrained model...")
frame_probs2 = np.zeros((n_talk, N_CLASSES_V))
for i in range(n_talk):
    h = np.maximum(0, X_norm_new[i] @ W1_new + b1_new)
    logits = h @ W2_new + b2_new
    e = np.exp(logits - logits.max())
    frame_probs2[i] = e / e.sum()

log_probs2 = np.log(frame_probs2 + 1e-30)

# Same Viterbi but with new emission probs
V2 = np.full((n_talk, N_STATES), -np.inf)
BP2 = np.zeros((n_talk, N_STATES), dtype=np.int32)


def emission2(t, s):
    phone = states[s][0]
    if phone in c2i_v:
        return log_probs2[t, c2i_v[phone]]
    return -10.0


V2[0, 0] = emission2(0, 0)

for t in range(1, n_talk):
    for s in range(N_STATES):
        score_self = V2[t - 1, s] + log_self + emission2(t, s)
        score_adv = V2[t - 1, s - 1] + log_advance + emission2(t, s) if s > 0 else -np.inf

        if score_self >= score_adv:
            V2[t, s] = score_self
            BP2[t, s] = s
        else:
            V2[t, s] = score_adv
            BP2[t, s] = s - 1

        if s >= 2 and states[s - 1][2] == "silence":
            score_skip = V2[t - 1, s - 2] + log_advance + emission2(t, s) - 1.0
            if score_skip > V2[t, s]:
                V2[t, s] = score_skip
                BP2[t, s] = s - 2

state_path2 = np.zeros(n_talk, dtype=np.int32)
best_end2 = N_STATES - 1
for s in range(max(0, N_STATES - 5), N_STATES):
    if V2[-1, s] > V2[-1, best_end2]:
        best_end2 = s
state_path2[-1] = best_end2

for t in range(n_talk - 2, -1, -1):
    state_path2[t] = BP2[t + 1, state_path2[t + 1]]

viterbi_labels2 = [states[s][0] for s in state_path2]
viterbi_words2 = [states[s][1] for s in state_path2]

# Results
print(f"\nWord boundaries (Viterbi Round 2):")
prev_w = ""
word_starts2 = []
for i in range(n_talk):
    w = viterbi_words2[i]
    if w != prev_w and w != "_pause_":
        word_starts2.append((i, w))
        prev_w = w if w != "_pause_" else prev_w

for start, word in word_starts2:
    end = start
    while end < n_talk and viterbi_words2[end] == word:
        end += 1
    dur = (end - start) * 10
    print(f"  {start * 10:5d}-{end * 10:5d}ms ({dur:4d}ms): {word}")

viterbi_phonemes2 = []
prev_p = ""
for p in viterbi_labels2:
    if p != prev_p and p != SILENCE:
        viterbi_phonemes2.append(p)
        prev_p = p
    elif p == SILENCE:
        prev_p = p

per2 = levenshtein(viterbi_phonemes2, full_phonemes) / len(full_phonemes)
print(f"\nRound 2 decoded: {len(viterbi_phonemes2)} phonemes, PER={per2:.1%}")
print(f"Decoded: {' '.join(viterbi_phonemes2)}")

# Save improved model
np.savez_compressed(
    "vibe_core/mahamantra_research/shabda_recognition/tiny_asr_weights_v2.npz",
    W1=W1_new,
    b1=b1_new,
    W2=W2_new,
    b2=b2_new,
    X_mean=X_mean_new,
    X_std=X_std_new,
    classes=np.array(CLASSES_V),
    context=CTX,
)
print(f"\nSaved v2 weights ({W1_new.size + b1_new.size + W2_new.size + b2_new.size} params)")

# =============================================================================
# 8. SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY: Viterbi Forced Alignment")
print("=" * 70)
print(f"Round 1 PER: {per:.1%} (DTW-initialized model)")
print(f"Round 2 PER: {per2:.1%} (Viterbi-retrained model)")
print(f"Words found (R1): {len(word_starts)}/{len(TRANSCRIPT)}")
print(f"Words found (R2): {len(word_starts2)}/{len(TRANSCRIPT)}")
print(f"Model: {D_in}→{HIDDEN}→{N_CLASSES_V} ({W1_new.size + b1_new.size + W2_new.size + b2_new.size} params)")
