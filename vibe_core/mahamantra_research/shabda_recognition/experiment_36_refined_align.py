"""
EXPERIMENT 36: Iterative Forced Alignment + Context-Frame ASR
==============================================================

Improvements over Exp 35:
  1. CONTEXT FRAMES: Each frame sees ±2 neighbors → 130D input (5×26)
  2. ITERATIVE REFINEMENT: After first alignment + training,
     update phoneme templates from REAL mel averages per label,
     re-align, re-train. Repeat 3×.
  3. LARGER MODEL: 128 hidden units.

The key insight: initial templates are garbage (global avg + perturbation).
But after one round of alignment + training, we have REAL mel averages
per phoneme class. These become much better templates for the NEXT alignment.
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
# 1. PRONUNCIATION DICTIONARY + TRANSCRIPT
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


def build_phoneme_sequence():
    """Build spaced phoneme sequence with silence between words."""
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
    return spaced_phonemes, spaced_word_map


spaced_phonemes, spaced_word_map = build_phoneme_sequence()
full_phonemes = [p for p in spaced_phonemes if p != SILENCE]

print(f"Transcript: {len(TRANSCRIPT)} words, {len(full_phonemes)} phonemes")
print(f"With silence tokens: {len(spaced_phonemes)}")

# =============================================================================
# 2. EXTRACT LOG-MEL FROM AUDIO
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


intake = ShabdaIntake()

print("Loading talk audio...")
talk_stream = intake.process_file("temp/prabhupada-talk.wav")
talk_frames_packed = talk_stream.frames
n_talk = len(talk_frames_packed)

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

print("Loading japa audio...")
japa_stream = intake.process_file("temp/srila prabhupada japa clip.wav")
with open("vibe_core/mahamantra/data/shabda_bridge.json") as f:
    bridge = json.load(f)

X_japa = []
n_japa = len(bridge["stream"])
for i in range(n_japa):
    start_sample = i * hop
    end_sample = start_sample + N_FFT
    if japa_stream.raw_samples is not None and end_sample <= len(japa_stream.raw_samples):
        audio = japa_stream.raw_samples[start_sample:end_sample]
        X_japa.append(extract_log_mel(audio))
    else:
        X_japa.append(np.zeros(N_MELS))
X_japa = np.array(X_japa)

print(f"Talk: {X_talk.shape}, Japa: {X_japa.shape}")

# =============================================================================
# 3. CONTEXT FRAME BUILDER
# =============================================================================


def add_context(X, ctx=2):
    """Stack ±ctx neighboring frames → (N, (2*ctx+1)*D) feature matrix."""
    N, D = X.shape
    X_ctx = np.zeros((N, (2 * ctx + 1) * D))
    for i in range(N):
        for k in range(-ctx, ctx + 1):
            j = max(0, min(N - 1, i + k))
            X_ctx[i, (k + ctx) * D : (k + ctx + 1) * D] = X[j]
    return X_ctx


# =============================================================================
# 4. INITIAL PHONEME TEMPLATES (from Japa + heuristics)
# =============================================================================


def build_initial_templates(X_japa, bridge):
    """Build initial mel templates from japa data + phonetic heuristics."""
    japa_ranges = {}
    frame_idx = bridge["meta"]["chant_start_frame"]
    for syl_name, syl_data in bridge["syllables"].items():
        n = syl_data["n_frames"]
        japa_ranges[syl_name] = (frame_idx, frame_idx + n)
        frame_idx += n

    japa_mel_avg = {}
    for syl, (start, end) in japa_ranges.items():
        japa_mel_avg[syl] = X_japa[start:end].mean(axis=0)

    JAPA_TO_ARPABET = {
        "ha": ["HH", "AA"],
        "re": ["R", "EY"],
        "kṛ": ["K", "R", "ER"],
        "ṣṇa": ["SH", "N", "AA"],
        "rā": ["R", "AA"],
        "ma": ["M", "AA"],
    }

    templates = {}

    # Silence: use low-energy frames from talk
    silence_mask = np.array([f & 0xFF < 10 for f in talk_frames_packed])
    if silence_mask.any():
        templates[SILENCE] = X_talk[silence_mask].mean(axis=0)
    else:
        templates[SILENCE] = np.full(N_MELS, -20.0)

    # From japa
    for syl, arpabets in JAPA_TO_ARPABET.items():
        mel = japa_mel_avg[syl]
        for arpa in arpabets:
            if arpa not in templates:
                templates[arpa] = mel.copy()

    # Global voiced average for filling in unknowns
    voiced_mask = np.array([f & 0xFF > 20 for f in talk_frames_packed])
    global_avg = X_talk[voiced_mask].mean(axis=0) if voiced_mask.any() else X_talk.mean(axis=0)

    all_arpabets = sorted(set(full_phonemes))
    rng = np.random.RandomState(MAHA_QUANTUM)

    for arpa in all_arpabets:
        if arpa in templates:
            continue
        template = global_avg.copy()

        if arpa in ("AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY", "ER", "IH", "IY", "OW", "OY", "UH", "UW"):
            template[:13] += 1.0
            template[13:] -= 0.5
        elif arpa in ("S", "SH", "Z", "ZH", "F", "TH", "V"):
            template[:8] -= 1.0
            template[15:] += 2.0
        elif arpa in ("P", "B", "T", "D", "K", "G"):
            template -= 0.5
        elif arpa in ("M", "N", "NG"):
            template[:10] += 1.5
            template[15:] -= 1.0

        template += rng.randn(N_MELS) * 0.3
        templates[arpa] = template

    return templates, global_avg


# =============================================================================
# 5. DTW ALIGNMENT FUNCTION
# =============================================================================


def dtw_align(synthetic_mel, real_mel):
    """DTW alignment: synthetic → real. Returns (path_synth, path_real)."""
    n_synth = len(synthetic_mel)
    n_real = len(real_mel)
    band = max(n_synth, n_real) // 3 + 10
    INF = 1e30

    D = np.full((n_synth + 1, n_real + 1), INF)
    D[0, 0] = 0.0
    backtrace = np.zeros((n_synth, n_real), dtype=np.int8)

    for i in range(1, n_synth + 1):
        j_lo = max(1, int(i * n_real / n_synth) - band)
        j_hi = min(n_real, int(i * n_real / n_synth) + band)
        for j in range(j_lo, j_hi + 1):
            cost = np.sqrt(np.sum((synthetic_mel[i - 1] - real_mel[j - 1]) ** 2))
            candidates = [D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]]
            best = np.argmin(candidates)
            D[i, j] = cost + candidates[best]
            backtrace[i - 1, j - 1] = best

    # Recover path
    path_synth, path_real = [], []
    i, j = n_synth - 1, n_real - 1
    while i >= 0 and j >= 0:
        path_synth.append(i)
        path_real.append(j)
        bt = backtrace[i, j]
        if bt == 0:
            i -= 1
            j -= 1
        elif bt == 1:
            i -= 1
        else:
            j -= 1
    path_synth.reverse()
    path_real.reverse()

    return path_synth, path_real, D[n_synth, n_real]


# =============================================================================
# 6. BUILD SYNTHETIC SEQUENCE
# =============================================================================


def build_synthetic(templates, global_avg):
    """Build synthetic mel sequence from phoneme sequence + templates."""

    def dur(p):
        if p == SILENCE:
            return 3
        if p in ("AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY", "ER", "IH", "IY", "OW", "OY", "UH", "UW"):
            return 5
        return 3

    synth_mel, synth_labels, synth_words = [], [], []
    for phone, word in zip(spaced_phonemes, spaced_word_map):
        d = dur(phone)
        tmpl = templates.get(phone, global_avg)
        for _ in range(d):
            synth_mel.append(tmpl)
            synth_labels.append(phone)
            synth_words.append(word)
    return np.array(synth_mel), synth_labels, synth_words


# =============================================================================
# 7. TRANSFER LABELS
# =============================================================================


def transfer_labels(path_synth, path_real, synth_labels, synth_words, n_real):
    """Map aligned labels from synthetic → real frames."""
    labels = [SILENCE] * n_real
    words = ["_silence_"] * n_real
    for ps, pr in zip(path_synth, path_real):
        labels[pr] = synth_labels[ps]
        words[pr] = synth_words[ps]
    return labels, words


# =============================================================================
# 8. TRAIN MODEL
# =============================================================================


def train_model(X_ctx, labels, n_epochs=300, hidden=128, lr=0.01, batch_size=128):
    """Train a single-hidden-layer MLP on context features → phoneme labels."""
    CLASSES = sorted(set(labels))
    N_CLASSES = len(CLASSES)
    class_to_idx = {c: i for i, c in enumerate(CLASSES)}

    N = len(labels)
    y = np.array([class_to_idx[l] for l in labels])

    # Normalize
    X_mean = X_ctx.mean(axis=0)
    X_std = X_ctx.std(axis=0) + 1e-8
    X_norm = (X_ctx - X_mean) / X_std

    D_in = X_ctx.shape[1]
    rng = np.random.RandomState(MAHA_QUANTUM)
    W1 = rng.randn(D_in, hidden).astype(np.float64) * np.sqrt(2.0 / D_in)
    b1 = np.zeros(hidden)
    W2 = rng.randn(hidden, N_CLASSES).astype(np.float64) * np.sqrt(2.0 / hidden)
    b2 = np.zeros(N_CLASSES)

    indices = np.arange(N)

    for epoch in range(n_epochs):
        rng.shuffle(indices)
        total_loss = 0.0
        correct = 0

        for bs in range(0, N, batch_size):
            bi = indices[bs : bs + batch_size]
            bx = X_norm[bi]
            by = y[bi]
            B = len(bi)

            h = np.maximum(0, bx @ W1 + b1)
            logits = h @ W2 + b2
            e = np.exp(logits - logits.max(axis=1, keepdims=True))
            probs = e / e.sum(axis=1, keepdims=True)

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

            W1 -= lr * dW1
            b1 -= lr * db1
            W2 -= lr * dW2
            b2 -= lr * db2

        if epoch % 50 == 0 or epoch == n_epochs - 1:
            acc = correct / N
            avg_loss = total_loss / N
            print(f"    Epoch {epoch:3d}: loss={avg_loss:.4f}  acc={acc:.1%}")

    return W1, b1, W2, b2, CLASSES, class_to_idx, X_mean, X_std


# =============================================================================
# 9. MAIN: ITERATIVE REFINEMENT LOOP
# =============================================================================

print("\n" + "=" * 70)
print("ITERATIVE FORCED ALIGNMENT + TRAINING")
print("=" * 70)

N_ROUNDS = 3
CTX = 2  # ±2 context frames

# Context features
X_talk_ctx = add_context(X_talk, CTX)
print(f"Context features: {X_talk_ctx.shape} (±{CTX} frames)")

# Initial templates
templates, global_avg = build_initial_templates(X_japa, bridge)
print(f"Initial templates: {len(templates)} phonemes")

best_acc = 0
best_model = None

for round_idx in range(N_ROUNDS):
    print(f"\n{'=' * 50}")
    print(f"ROUND {round_idx + 1}/{N_ROUNDS}")
    print(f"{'=' * 50}")

    # Build synthetic sequence
    synth_mel, synth_labels, synth_words = build_synthetic(templates, global_avg)
    print(f"  Synthetic: {len(synth_mel)} frames")

    # DTW align
    t0 = time.time()
    ps, pr, cost = dtw_align(synth_mel, X_talk)
    dt = time.time() - t0
    print(f"  DTW: {dt:.1f}s, cost={cost:.1f}")

    # Transfer labels
    real_labels, real_words = transfer_labels(ps, pr, synth_labels, synth_words, n_talk)

    # Show distribution
    counts = {}
    for l in real_labels:
        counts[l] = counts.get(l, 0) + 1
    print(
        f"  Labels: {len(counts)} classes, "
        f"SIL={counts.get(SILENCE, 0)} ({counts.get(SILENCE, 0) / n_talk * 100:.0f}%), "
        f"voiced={n_talk - counts.get(SILENCE, 0)}"
    )

    # Show word timeline
    print(f"  Word timeline:")
    prev_w = ""
    for i in range(0, n_talk, 10):
        w = real_words[i]
        if w != prev_w:
            print(f"    {i * 10:5d}ms: {w}")
            prev_w = w

    # Train model
    print(f"  Training (ctx={CTX}, hidden=128)...")
    W1, b1, W2, b2, CLASSES, c2i, X_mean, X_std = train_model(
        X_talk_ctx, real_labels, n_epochs=300, hidden=128, lr=0.01
    )

    # Evaluate
    X_norm = (X_talk_ctx - X_mean) / X_std
    preds = []
    for i in range(n_talk):
        h = np.maximum(0, X_norm[i] @ W1 + b1)
        logits = h @ W2 + b2
        preds.append(np.argmax(logits))
    preds = np.array(preds)
    y = np.array([c2i[l] for l in real_labels])
    acc = np.mean(preds == y)
    print(f"  Accuracy: {acc:.1%}")

    if acc > best_acc:
        best_acc = acc
        best_model = (W1.copy(), b1.copy(), W2.copy(), b2.copy(), CLASSES[:], dict(c2i), X_mean.copy(), X_std.copy())

    # UPDATE TEMPLATES from real data for next round
    print(f"  Updating templates from real mel averages...")
    new_templates = {}
    for label in set(real_labels):
        mask = np.array([l == label for l in real_labels])
        if mask.sum() >= 3:  # need at least 3 frames
            new_templates[label] = X_talk[mask].mean(axis=0)
        elif label in templates:
            new_templates[label] = templates[label]
    templates = new_templates
    print(f"  Templates updated: {len(templates)} phonemes")

# =============================================================================
# 10. FINAL ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print(f"BEST MODEL: {best_acc:.1%} accuracy")
print("=" * 70)

W1, b1, W2, b2, CLASSES, c2i, X_mean, X_std = best_model
N_CLASSES = len(CLASSES)

# Per-class accuracy
X_norm = (X_talk_ctx - X_mean) / X_std
preds = []
probs_all = []
for i in range(n_talk):
    h = np.maximum(0, X_norm[i] @ W1 + b1)
    logits = h @ W2 + b2
    e = np.exp(logits - logits.max())
    p = e / e.sum()
    preds.append(np.argmax(p))
    probs_all.append(p)
preds = np.array(preds)

print(f"\nPer-phoneme accuracy (top 15 by frequency):")
for label in sorted(counts.keys(), key=lambda l: counts[l], reverse=True)[:15]:
    if label not in c2i:
        continue
    idx = c2i[label]
    mask = y == idx
    if mask.sum() > 0:
        class_acc = np.mean(preds[mask] == idx)
        print(f"  {label:>5}: {class_acc:.1%} ({mask.sum()} frames)")

# Decoded text
print(f"\nDecoded phoneme sequence (collapsed):")
decoded = []
prev_p = -1
for p in preds:
    if p != prev_p:
        decoded.append(CLASSES[p])
        prev_p = p
decoded_clean = [p for p in decoded if p != SILENCE]
print(f"  {' '.join(decoded_clean[:60])}...")
print(f"  ({len(decoded_clean)} total phonemes)")

print(f"\nGround truth phoneme sequence:")
print(f"  {' '.join(full_phonemes[:60])}...")
print(f"  ({len(full_phonemes)} phonemes)")


# Phoneme-level edit distance (Levenshtein)
def levenshtein(s1, s2):
    """Compute Levenshtein edit distance between two sequences."""
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


per = levenshtein(decoded_clean, full_phonemes) / max(len(full_phonemes), 1)
print(f"\nPhoneme Error Rate (PER): {per:.1%}")
print(f"  (Edit distance: {levenshtein(decoded_clean, full_phonemes)}, reference length: {len(full_phonemes)})")

# Save model
total_params = W1.size + b1.size + W2.size + b2.size
print(f"\nModel size: {total_params} params ({total_params * 8 / 1024:.1f} KB)")
print(f"Architecture: {W1.shape[0]}→{W1.shape[1]}→{W2.shape[1]}")

# Save weights for integration
np.savez_compressed(
    "vibe_core/mahamantra_research/shabda_recognition/tiny_asr_weights.npz",
    W1=W1,
    b1=b1,
    W2=W2,
    b2=b2,
    X_mean=X_mean,
    X_std=X_std,
    classes=np.array(CLASSES),
    context=CTX,
)
print("Weights saved to tiny_asr_weights.npz")
