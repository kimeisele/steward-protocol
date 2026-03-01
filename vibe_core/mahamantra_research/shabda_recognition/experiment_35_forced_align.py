"""
EXPERIMENT 35: Forced Aligner + Tiny ASR Training
====================================================

THE PLAN:
  1. Take transcript of prabhupada-talk.wav
  2. Convert each word → ARPAbet phoneme sequence (simple lookup dict)
  3. Build a "synthetic" mel template per phoneme (from Japa + phonetic rules)
  4. DTW-align the phoneme template sequence onto the real mel spectrogram
  5. Result: frame-level ARPAbet labels for ALL 1400 frames
  6. Train Tiny ASR on these labels → 40-class phoneme recognizer

This is NOT ML for the alignment step — it's pure DTW (deterministic).
The ML is only for learning the weights that map mel→phoneme.
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
    unpack_frame,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA,
    ARPABET_TO_VARGA,
)
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

# =============================================================================
# 1. SIMPLE PRONUNCIATION DICTIONARY (hand-built for our transcript)
# =============================================================================
# CMU-style: word → list of ARPAbet phonemes
# We only need the ~23 words in our transcript.

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

# Build full phoneme sequence for the sentence
full_phonemes = []
phoneme_word_map = []  # which word each phoneme belongs to
for word in TRANSCRIPT:
    phones = PRONUNCIATIONS[word]
    for p in phones:
        full_phonemes.append(p)
        phoneme_word_map.append(word)

# Add silence tokens between words
SILENCE = "SIL"
spaced_phonemes = []
spaced_word_map = []
for i, word in enumerate(TRANSCRIPT):
    if i > 0:
        spaced_phonemes.append(SILENCE)
        spaced_word_map.append("_silence_")
    phones = PRONUNCIATIONS[word]
    for p in phones:
        spaced_phonemes.append(p)
        spaced_word_map.append(word)

print(f"Transcript: {len(TRANSCRIPT)} words")
print(f"Phonemes (no silence): {len(full_phonemes)}")
print(f"Phonemes (with silence): {len(spaced_phonemes)}")
print(f"Unique phonemes: {sorted(set(full_phonemes))}")
print()

# =============================================================================
# 2. EXTRACT LOG-MEL FROM AUDIO
# =============================================================================

intake = ShabdaIntake()
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


# Extract from talk audio
talk_stream = intake.process_file("temp/prabhupada-talk.wav")
talk_frames_packed = talk_stream.frames
n_talk = len(talk_frames_packed)

print(f"Loading talk audio: {n_talk} frames ({n_talk * 10}ms)")
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
print(f"Talk mel features: {X_talk.shape}")

# Also extract from japa audio for phoneme templates
japa_stream = intake.process_file("temp/srila prabhupada japa clip.wav")
with open("vibe_core/mahamantra/data/shabda_bridge.json") as f:
    bridge = json.load(f)
n_japa = len(bridge["stream"])

X_japa = []
for i in range(n_japa):
    start_sample = i * hop
    end_sample = start_sample + N_FFT
    if japa_stream.raw_samples is not None and end_sample <= len(japa_stream.raw_samples):
        audio = japa_stream.raw_samples[start_sample:end_sample]
        X_japa.append(extract_log_mel(audio))
    else:
        X_japa.append(np.zeros(N_MELS))
X_japa = np.array(X_japa)
print(f"Japa mel features: {X_japa.shape}")

# =============================================================================
# 3. BUILD PHONEME MEL TEMPLATES
# =============================================================================
# From japa ground truth, we know mel profiles for: ha, re, kṛ, ṣṇa, rā, ma
# Map these to ARPAbet and extrapolate for missing phonemes.

# Japa syllable → frame ranges (from shabda_bridge.json)
japa_ranges = {}
frame_idx = bridge["meta"]["chant_start_frame"]
for syl_name, syl_data in bridge["syllables"].items():
    n = syl_data["n_frames"]
    japa_ranges[syl_name] = (frame_idx, frame_idx + n)
    frame_idx += n

# Average mel per japa syllable
japa_mel_avg = {}
for syl, (start, end) in japa_ranges.items():
    japa_mel_avg[syl] = X_japa[start:end].mean(axis=0)

# Map japa syllables to approximate ARPAbet
# ha → HH+AA, re → R+EY, kṛ → K+R+ER, ṣṇa → SH+N+AA, rā → R+AA, ma → M+AA
JAPA_TO_ARPABET = {
    "ha": ["HH", "AA"],
    "re": ["R", "EY"],
    "kṛ": ["K", "R", "ER"],
    "ṣṇa": ["SH", "N", "AA"],
    "rā": ["R", "AA"],
    "ma": ["M", "AA"],
}

# Build initial phoneme templates from japa (rough approximation)
phoneme_templates = {}  # ARPAbet → mel vector (26D)

# Global average mel (for unknown phonemes)
voiced_mask = np.array([f & 0xFF > 20 for f in talk_frames_packed])
global_avg = X_talk[voiced_mask].mean(axis=0) if voiced_mask.any() else X_talk.mean(axis=0)

# Silence template: use actual silence frames
silence_mask = np.array([f & 0xFF < 10 for f in talk_frames_packed])
if silence_mask.any():
    phoneme_templates[SILENCE] = X_talk[silence_mask].mean(axis=0)
else:
    phoneme_templates[SILENCE] = np.full(N_MELS, -20.0)

# From japa data: assign mel averages
for syl, arpabets in JAPA_TO_ARPABET.items():
    mel = japa_mel_avg[syl]
    for arpa in arpabets:
        if arpa not in phoneme_templates:
            phoneme_templates[arpa] = mel.copy()

# For remaining phonemes: use global average with slight perturbations
# based on phonetic class (vowels=more energy in low mels, fricatives=more in high mels)
all_arpabets = sorted(set(full_phonemes))
rng = np.random.RandomState(MAHA_QUANTUM)

for arpa in all_arpabets:
    if arpa in phoneme_templates:
        continue
    # Start from global average
    template = global_avg.copy()

    # Perturb based on Varga (articulation point)
    varga = ARPABET_TO_VARGA.get(arpa, 2)  # default mid

    # Vowels: more energy in low-mid frequency bands
    if arpa in ("AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY", "ER", "IH", "IY", "OW", "OY", "UH", "UW"):
        template[:13] += 1.0  # boost lower mels
        template[13:] -= 0.5

    # Fricatives: more energy in high frequency bands
    elif arpa in ("S", "SH", "Z", "ZH", "F", "TH", "V"):
        template[:8] -= 1.0
        template[15:] += 2.0

    # Stops: brief energy burst, less overall
    elif arpa in ("P", "B", "T", "D", "K", "G"):
        template -= 0.5

    # Nasals: energy in low frequencies
    elif arpa in ("M", "N", "NG"):
        template[:10] += 1.5
        template[15:] -= 1.0

    # Add small Seed-based perturbation for uniqueness
    template += rng.randn(N_MELS) * 0.3

    phoneme_templates[arpa] = template

print(
    f"\nPhoneme templates: {len(phoneme_templates)} "
    f"(from japa: {sum(1 for a in phoneme_templates if a != SILENCE and a in sum(JAPA_TO_ARPABET.values(), []))})"
)

# =============================================================================
# 4. BUILD SYNTHETIC MEL SEQUENCE
# =============================================================================
# Each phoneme gets N frames in the synthetic sequence.
# Duration heuristic: vowels=5 frames (50ms), consonants=3 frames (30ms),
# silence=3 frames (30ms)


def phoneme_duration(p):
    if p == SILENCE:
        return 3
    if p in ("AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY", "ER", "IH", "IY", "OW", "OY", "UH", "UW"):
        return 5  # vowels longer
    return 3  # consonants shorter


synthetic_mel = []
synthetic_labels = []  # ARPAbet label per synthetic frame
synthetic_words = []  # word per synthetic frame

for i, (phone, word) in enumerate(zip(spaced_phonemes, spaced_word_map)):
    dur = phoneme_duration(phone)
    template = phoneme_templates.get(phone, global_avg)
    for _ in range(dur):
        synthetic_mel.append(template)
        synthetic_labels.append(phone)
        synthetic_words.append(word)

synthetic_mel = np.array(synthetic_mel)
print(f"Synthetic sequence: {len(synthetic_mel)} frames ({len(synthetic_mel) * 10}ms)")
print(f"Talk audio: {n_talk} frames ({n_talk * 10}ms)")
print(f"Ratio: {n_talk / len(synthetic_mel):.1f}x")

# =============================================================================
# 5. DTW ALIGNMENT: synthetic → real
# =============================================================================
# Align the synthetic mel sequence onto the real talk mel sequence.
# This tells us which real frame corresponds to which phoneme.

print("\nRunning DTW alignment...")
t0 = time.time()

n_synth = len(synthetic_mel)
n_real = n_talk

# Sakoe-Chiba band DTW (memory efficient)
band = max(n_synth, n_real) // 3 + 10
INF = 1e30

# Cost matrix: we only need 2 rows
prev = np.full(n_real + 1, INF)
curr = np.full(n_real + 1, INF)
prev[0] = 0.0

# Also store backtrace for path recovery
# Using compressed backtrace: 0=diag, 1=left, 2=up
backtrace = np.zeros((n_synth, n_real), dtype=np.int8)

# Full DTW with backtrace (need path, not just cost)
D = np.full((n_synth + 1, n_real + 1), INF)
D[0, 0] = 0.0

for i in range(1, n_synth + 1):
    j_lo = max(1, int(i * n_real / n_synth) - band)
    j_hi = min(n_real, int(i * n_real / n_synth) + band)
    for j in range(j_lo, j_hi + 1):
        cost = np.sqrt(np.sum((synthetic_mel[i - 1] - X_talk[j - 1]) ** 2))
        candidates = [
            D[i - 1, j - 1],  # diagonal
            D[i - 1, j],  # up (advance synthetic, stay real)
            D[i, j - 1],  # left (stay synthetic, advance real)
        ]
        best = np.argmin(candidates)
        D[i, j] = cost + candidates[best]
        backtrace[i - 1, j - 1] = best

dt = time.time() - t0
print(f"DTW done in {dt:.1f}s, cost={D[n_synth, n_real]:.1f}")

# Recover path
path_synth = []
path_real = []
i, j = n_synth - 1, n_real - 1
while i >= 0 and j >= 0:
    path_synth.append(i)
    path_real.append(j)
    bt = backtrace[i, j]
    if bt == 0:  # diag
        i -= 1
        j -= 1
    elif bt == 1:  # up
        i -= 1
    else:  # left
        j -= 1
path_synth.reverse()
path_real.reverse()

print(f"Alignment path: {len(path_synth)} steps")

# =============================================================================
# 6. TRANSFER LABELS: synthetic → real frames
# =============================================================================
# For each real frame, find its aligned synthetic frame and copy the label.

real_labels = [SILENCE] * n_real  # default silence
real_words = ["_silence_"] * n_real

for ps, pr in zip(path_synth, path_real):
    real_labels[pr] = synthetic_labels[ps]
    real_words[pr] = synthetic_words[ps]

# Show label distribution
label_counts = {}
for l in real_labels:
    label_counts[l] = label_counts.get(l, 0) + 1

print(f"\nFrame labels for talk audio ({n_real} frames):")
for label in sorted(label_counts.keys()):
    count = label_counts[label]
    pct = count / n_real * 100
    print(f"  {label:>5}: {count:4d} frames ({pct:.1f}%)")

# Show timeline
print(f"\nLabel timeline (every 10th frame):")
line = ""
for i in range(0, n_real, 10):
    l = real_labels[i]
    if l == SILENCE:
        line += "."
    else:
        line += l[0].lower()
print(f"  {line}")

# Word timeline
print(f"\nWord timeline (every 10th frame):")
prev_w = ""
for i in range(0, n_real, 10):
    w = real_words[i]
    if w != prev_w:
        print(f"  {i * 10:5d}ms: {w}")
        prev_w = w

# =============================================================================
# 7. TRAIN TINY ASR WITH ALIGNED LABELS
# =============================================================================

print("\n" + "=" * 60)
print("TRAINING TINY ASR ON ALIGNED TALK LABELS")
print("=" * 60)

# Build class list (all unique ARPAbet phonemes + silence)
CLASSES = sorted(set(real_labels))
N_CLASSES = len(CLASSES)
class_to_idx = {c: i for i, c in enumerate(CLASSES)}

print(f"Classes: {N_CLASSES} ({CLASSES})")

# Prepare data
y = np.array([class_to_idx[l] for l in real_labels])

# Normalize features
X_mean = X_talk.mean(axis=0)
X_std = X_talk.std(axis=0) + 1e-8
X_norm = (X_talk - X_mean) / X_std

# Model: 26 → 64 → N_CLASSES
HIDDEN = 64
rng = np.random.RandomState(MAHA_QUANTUM)
W1 = rng.randn(N_MELS, HIDDEN).astype(np.float64) * 0.1
b1 = np.zeros(HIDDEN)
W2 = rng.randn(HIDDEN, N_CLASSES).astype(np.float64) * 0.1
b2 = np.zeros(N_CLASSES)

total_params = N_MELS * HIDDEN + HIDDEN + HIDDEN * N_CLASSES + N_CLASSES
print(f"Model: {N_MELS} → {HIDDEN} → {N_CLASSES}")
print(f"Parameters: {total_params} ({total_params * 8 / 1024:.1f} KB)")


def relu(x):
    return np.maximum(0, x)


def softmax(x):
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


# Training loop
LEARNING_RATE = 0.01
EPOCHS = 300
BATCH_SIZE = 128
indices = np.arange(n_real)

for epoch in range(EPOCHS):
    rng.shuffle(indices)
    total_loss = 0.0
    correct = 0

    for batch_start in range(0, n_real, BATCH_SIZE):
        batch_idx = indices[batch_start : batch_start + BATCH_SIZE]
        bx = X_norm[batch_idx]
        by = y[batch_idx]
        B = len(batch_idx)

        h = relu(bx @ W1 + b1)
        logits = h @ W2 + b2
        probs = softmax(logits)

        targets = np.zeros((B, N_CLASSES))
        targets[np.arange(B), by] = 1.0

        loss = -np.sum(targets * np.log(probs + 1e-10)) / B
        total_loss += loss * B
        correct += np.sum(np.argmax(probs, axis=1) == by)

        d_logits = (probs - targets) / B
        dW2 = h.T @ d_logits
        db2 = d_logits.sum(axis=0)
        d_h = d_logits @ W2.T
        d_h[h <= 0] = 0
        dW1 = bx.T @ d_h
        db1 = d_h.sum(axis=0)

        W1 -= LEARNING_RATE * dW1
        b1 -= LEARNING_RATE * db1
        W2 -= LEARNING_RATE * dW2
        b2 -= LEARNING_RATE * db2

    acc = correct / n_real
    avg_loss = total_loss / n_real

    if epoch % 30 == 0 or epoch == EPOCHS - 1:
        print(f"  Epoch {epoch:3d}: loss={avg_loss:.4f}  acc={acc:.1%}")

# Final predictions
print("\n" + "=" * 60)
print("FINAL PREDICTIONS ON TALK AUDIO")
print("=" * 60)

preds = []
for i in range(n_real):
    h = relu(X_norm[i] @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)
    preds.append(np.argmax(probs))
preds = np.array(preds)

acc = np.mean(preds == y)
print(f"Accuracy on training data: {acc:.1%}")

# Per-phoneme accuracy (top 10 most frequent)
for label in sorted(label_counts.keys(), key=lambda l: label_counts[l], reverse=True)[:15]:
    idx = class_to_idx[label]
    mask = y == idx
    if mask.sum() > 0:
        class_acc = np.mean(preds[mask] == idx)
        print(f"  {label:>5}: {class_acc:.1%} ({mask.sum()} frames)")

# Decoded text (CTC-style: collapse repeats, remove SIL)
print("\nDecoded phoneme sequence (collapsed):")
decoded = []
prev_p = -1
for p in preds:
    if p != prev_p:
        decoded.append(CLASSES[p])
        prev_p = p
# Remove silence
decoded_clean = [p for p in decoded if p != SILENCE]
print(f"  {' '.join(decoded_clean[:50])}...")
print(f"  ({len(decoded_clean)} phonemes)")

# Ground truth phoneme sequence
print(f"\nGround truth:")
print(f"  {' '.join(full_phonemes[:50])}...")
print(f"  ({len(full_phonemes)} phonemes)")
