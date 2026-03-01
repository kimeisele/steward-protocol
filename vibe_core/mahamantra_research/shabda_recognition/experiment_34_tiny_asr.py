"""
EXPERIMENT 34: Tiny Acoustic Model — Pure Python/NumPy
========================================================

WHAT THIS IS:
  The ENTIRE "ML" of speech recognition, stripped to bare minimum.
  No Whisper, no PyTorch, no TensorFlow. Just NumPy matrix math.

WHAT IT DOES:
  mel_frame (26 floats) → W1 (26×32) → ReLU → W2 (32×7) → softmax → phoneme probs

  That's 26×32 + 32 + 32×7 + 7 = 1095 parameters. ~4KB.
  This is what Whisper does, just 35000x smaller.

THE KEY INSIGHT:
  Our 33 experiments failed because we compared features with FIXED RULES.
  (Euclidean distance, DTW, Maha-transform — all fixed, no calibration.)
  An acoustic model uses LEARNED WEIGHTS to map features → phonemes.
  Same math (matrix multiply), but the weights ADAPT to the speaker.

HOW WE GET WEIGHTS:
  1. Initialize from Seed (Maha-derived structure)
  2. Calibrate with shabda_bridge.json (6 labeled syllables, 638 frames)
  3. Simple gradient descent — also just math, no magic:
     "if the model predicted wrong, nudge the weights a tiny bit"

TARGET PHONEMES (from Japa ground truth):
  ha, re, kṛ, ṣṇa, rā, ma + silence = 7 classes
"""

import sys

sys.path.insert(0, ".")
import json
import numpy as np

from scipy.fft import fft
from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake,
    _mel_filterbank,
    N_FFT,
    unpack_frame,
)
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

# =============================================================================
# 1. LOAD GROUND TRUTH
# =============================================================================

with open("vibe_core/mahamantra/data/shabda_bridge.json") as f:
    bridge = json.load(f)

meta = bridge["meta"]
stream_frames = bridge["stream"]
syllables = bridge["syllables"]
SR = meta["sample_rate"]

print(f"Japa audio: {len(stream_frames)} frames, {meta['duration_ms']}ms")
print(f"Syllables: {list(syllables.keys())}")
print()

# Map syllables to class indices
CLASSES = ["silence", "ha", "re", "kṛ", "ṣṇa", "rā", "ma"]
N_CLASSES = len(CLASSES)

# Build frame-level labels from syllable data
# The syllables are sequential: ha(152) + re(153) + kṛ(76) + ṣṇa(76) + rā(76) + ma(76)
# = 609 frames. Chant starts at frame 29.
labels = np.zeros(len(stream_frames), dtype=int)  # 0 = silence
frame_idx = meta["chant_start_frame"]
for syl_name, syl_data in syllables.items():
    class_idx = CLASSES.index(syl_name)
    n = syl_data["n_frames"]
    labels[frame_idx : frame_idx + n] = class_idx
    print(f"  {syl_name}: frames {frame_idx}-{frame_idx + n} ({n} frames) → class {class_idx}")
    frame_idx += n

print(f"\nLabel distribution:")
for i, name in enumerate(CLASSES):
    count = np.sum(labels == i)
    print(f"  {name}: {count} frames ({count * 10}ms)")

# =============================================================================
# 2. EXTRACT LOG-MEL FEATURES FROM RAW AUDIO
# =============================================================================

print("\nExtracting log-mel features from japa audio...")
intake = ShabdaIntake()
japa_stream = intake.process_file("temp/srila prabhupada japa clip.wav")

hop = int(SR * 10 / 1000)  # samples per frame
N_MELS = 26


def extract_log_mel(audio_frame, sr=SR, n_fft=N_FFT, n_mels=N_MELS):
    """26 log-mel energies from raw audio frame."""
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


# Extract features for ALL frames
n_frames = min(len(stream_frames), len(labels))
if japa_stream.raw_samples is not None:
    features = []
    for i in range(n_frames):
        start_sample = i * hop
        end_sample = start_sample + N_FFT
        if end_sample <= len(japa_stream.raw_samples):
            audio = japa_stream.raw_samples[start_sample:end_sample]
            features.append(extract_log_mel(audio))
        else:
            features.append(np.zeros(N_MELS))
    X = np.array(features)  # [N × 26]
else:
    print("ERROR: no raw_samples in japa stream")
    sys.exit(1)

print(f"Features: {X.shape}")
print(f"Feature range: [{X.min():.1f}, {X.max():.1f}]")

# Normalize features (zero mean, unit variance per band)
X_mean = X.mean(axis=0)
X_std = X.std(axis=0) + 1e-8
X_norm = (X - X_mean) / X_std

# =============================================================================
# 3. BUILD TINY MODEL — Seed-initialized weights
# =============================================================================

HIDDEN = 32  # hidden layer size

# Initialize weights from Seed (deterministic!)
rng = np.random.RandomState(seed=MAHA_QUANTUM)  # 137 — the Seed IS the init
W1 = rng.randn(N_MELS, HIDDEN).astype(np.float64) * 0.1  # 26×32
b1 = np.zeros(HIDDEN)
W2 = rng.randn(HIDDEN, N_CLASSES).astype(np.float64) * 0.1  # 32×7
b2 = np.zeros(N_CLASSES)

total_params = N_MELS * HIDDEN + HIDDEN + HIDDEN * N_CLASSES + N_CLASSES
print(f"\nModel: {N_MELS}→{HIDDEN}→{N_CLASSES}")
print(f"Parameters: {total_params} ({total_params * 8 / 1024:.1f} KB)")
print(f"Seed: MAHA_QUANTUM = {MAHA_QUANTUM}")


def relu(x):
    return np.maximum(0, x)


def softmax(x):
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def forward(x):
    """x: [N_MELS] → [N_CLASSES] probabilities"""
    h = relu(x @ W1 + b1)  # [HIDDEN]
    logits = h @ W2 + b2  # [N_CLASSES]
    return softmax(logits)


def predict(x):
    """x: [N_MELS] → class index"""
    return np.argmax(forward(x))


# =============================================================================
# 4. TEST BEFORE TRAINING (random Seed-initialized weights)
# =============================================================================

print("\n" + "=" * 60)
print("BEFORE TRAINING (Seed-initialized weights)")
print("=" * 60)

y_true = labels[:n_frames]
y_pred = np.array([predict(X_norm[i]) for i in range(n_frames)])
acc = np.mean(y_pred == y_true)
print(f"Accuracy: {acc:.1%} ({np.sum(y_pred == y_true)}/{n_frames})")

# Per-class accuracy
for c in range(N_CLASSES):
    mask = y_true == c
    if mask.sum() > 0:
        class_acc = np.mean(y_pred[mask] == c)
        print(f"  {CLASSES[c]:>8}: {class_acc:.1%} ({np.sum(y_pred[mask] == c)}/{mask.sum()})")

# =============================================================================
# 5. TRAIN — simple gradient descent
# =============================================================================
# This is the "calibration" step. We nudge the weights so the model
# predicts the correct syllable for each frame.
# Cross-entropy loss + backprop through 2 layers. All NumPy.

print("\n" + "=" * 60)
print("TRAINING (calibrating weights with japa ground truth)")
print("=" * 60)

LEARNING_RATE = 0.01
EPOCHS = 200
BATCH_SIZE = 64

n_train = n_frames
indices = np.arange(n_train)

for epoch in range(EPOCHS):
    rng.shuffle(indices)

    total_loss = 0.0
    correct = 0

    for batch_start in range(0, n_train, BATCH_SIZE):
        batch_idx = indices[batch_start : batch_start + BATCH_SIZE]
        batch_x = X_norm[batch_idx]  # [B × 26]
        batch_y = y_true[batch_idx]  # [B]
        B = len(batch_idx)

        # Forward pass
        h = relu(batch_x @ W1 + b1)  # [B × 32]
        logits = h @ W2 + b2  # [B × 7]
        probs = softmax(logits)  # [B × 7]

        # One-hot targets
        targets = np.zeros((B, N_CLASSES))
        targets[np.arange(B), batch_y] = 1.0

        # Cross-entropy loss
        loss = -np.sum(targets * np.log(probs + 1e-10)) / B
        total_loss += loss * B

        # Predictions
        preds = np.argmax(probs, axis=1)
        correct += np.sum(preds == batch_y)

        # Backward pass (gradient computation)
        # dL/d_logits = probs - targets (standard softmax+CE gradient)
        d_logits = (probs - targets) / B  # [B × 7]

        # Gradients for W2, b2
        dW2 = h.T @ d_logits  # [32 × 7]
        db2 = d_logits.sum(axis=0)  # [7]

        # Backprop through ReLU
        d_h = d_logits @ W2.T  # [B × 32]
        d_h[h <= 0] = 0  # ReLU gradient

        # Gradients for W1, b1
        dW1 = batch_x.T @ d_h  # [26 × 32]
        db1 = d_h.sum(axis=0)  # [32]

        # Update weights (gradient descent)
        W1 -= LEARNING_RATE * dW1
        b1 -= LEARNING_RATE * db1
        W2 -= LEARNING_RATE * dW2
        b2 -= LEARNING_RATE * db2

    acc = correct / n_train
    avg_loss = total_loss / n_train

    if epoch % 20 == 0 or epoch == EPOCHS - 1:
        print(f"  Epoch {epoch:3d}: loss={avg_loss:.4f}  acc={acc:.1%}")

# =============================================================================
# 6. TEST AFTER TRAINING
# =============================================================================

print("\n" + "=" * 60)
print("AFTER TRAINING")
print("=" * 60)

y_pred = np.array([predict(X_norm[i]) for i in range(n_frames)])
acc = np.mean(y_pred == y_true)
print(f"Accuracy: {acc:.1%} ({np.sum(y_pred == y_true)}/{n_frames})")

for c in range(N_CLASSES):
    mask = y_true == c
    if mask.sum() > 0:
        class_acc = np.mean(y_pred[mask] == c)
        print(f"  {CLASSES[c]:>8}: {class_acc:.1%} ({np.sum(y_pred[mask] == c)}/{mask.sum()})")

# Show prediction timeline (compact)
print("\nPrediction timeline (every 5th frame):")
line_true = ""
line_pred = ""
for i in range(0, n_frames, 5):
    t = CLASSES[y_true[i]][0] if y_true[i] > 0 else "."
    p = CLASSES[y_pred[i]][0] if y_pred[i] > 0 else "."
    line_true += t
    line_pred += p

print(f"  TRUE: {line_true}")
print(f"  PRED: {line_pred}")
print(f"  {''.join(['|' if line_true[i] == line_pred[i] else 'x' for i in range(len(line_true))])}")

# =============================================================================
# 7. NOW THE REAL TEST: Apply to prabhupada-talk.wav (UNSEEN audio)
# =============================================================================

print("\n" + "=" * 60)
print("GENERALIZATION TEST: prabhupada-talk.wav (unseen)")
print("=" * 60)

talk_stream = intake.process_file("temp/prabhupada-talk.wav")
if talk_stream.raw_samples is not None:
    talk_frames = []
    for i in range(len(talk_stream.frames)):
        start_sample = i * hop
        end_sample = start_sample + N_FFT
        if end_sample <= len(talk_stream.raw_samples):
            audio = talk_stream.raw_samples[start_sample:end_sample]
            talk_frames.append(extract_log_mel(audio))
        else:
            talk_frames.append(np.zeros(N_MELS))
    X_talk = np.array(talk_frames)
    X_talk_norm = (X_talk - X_mean) / X_std  # use SAME normalization

    # Predict
    talk_preds = np.array([predict(X_talk_norm[i]) for i in range(len(X_talk))])

    # Show prediction timeline
    print(f"Frames: {len(talk_preds)}")
    print("\nPrediction timeline (every 5th frame, first 8s):")
    line = ""
    for i in range(0, min(800, len(talk_preds)), 5):
        p = CLASSES[talk_preds[i]][0] if talk_preds[i] > 0 else "."
        line += p
    print(f"  {line}")

    # Count phoneme distribution
    print("\nPhoneme distribution in talk:")
    for c in range(N_CLASSES):
        count = np.sum(talk_preds == c)
        pct = count / len(talk_preds) * 100
        print(f"  {CLASSES[c]:>8}: {count:4d} frames ({pct:.1f}%)")
else:
    print("ERROR: no raw_samples")
