"""
EXPERIMENT 39: Radio Interview — Bootstrapping Forced Alignment
================================================================

Goal: Scale the Forced Aligner from 14s Japa to 25min multi-speaker English.

Audio: Radio Interview (Enhanced, 690212IV, Los Angeles).wav
       ~25 minutes, 2 speakers (Prabhupada + Interviewer), English.

Strategy:
  1. Parse the transcript.txt → clean word list (strip speaker labels, punctuation)
  2. Extract log-Mel features from full audio
  3. Run Viterbi alignment with existing model (trained on 14s Japa)
  4. Retrain Tiny ASR on the interview's Viterbi labels
  5. Run second Viterbi pass with improved model
  6. Save improved weights (v3) — now trained on ~25min diverse English

The model will learn two speakers' voices, varied intonation, natural
conversation dynamics — all automatically, no manual labeling.
"""

import sys

sys.path.insert(0, ".")
import re
import time

import numpy as np
from scipy.fft import fft
from scipy.io import wavfile

from vibe_core.mahamantra.sound.shabda_intake import _mel_filterbank, N_FFT
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

# =============================================================================
# 1. PARSE TRANSCRIPT
# =============================================================================

print("=" * 70)
print("EXPERIMENT 39: Radio Interview Bootstrapping")
print("=" * 70)

TRANSCRIPT_PATH = "temp/transcript.txt"
AUDIO_PATH = "temp/Radio Interview (Enhanced, 690212IV, Los Angeles).wav"

print(f"\nParsing transcript: {TRANSCRIPT_PATH}")

with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
    raw_text = f.read()

# Strip header lines, speaker labels, and diacritical markup
lines = raw_text.strip().split("\n")
spoken_lines = []
for line in lines:
    line = line.strip()
    # Skip empty lines, header, footer
    if not line:
        continue
    if line.startswith("Radio Interview") or line.startswith("Prabhupada Enhanced"):
        continue
    if "views" in line and "Wrong layout" in line:
        continue
    # Strip speaker labels
    if line.startswith("Interviewer:"):
        line = line[len("Interviewer:") :].strip()
    elif line.startswith("Prabhupāda:"):
        line = line[len("Prabhupāda:") :].strip()
    elif line.startswith("Prabhupada:"):
        line = line[len("Prabhupada:") :].strip()
    if not line:
        continue
    spoken_lines.append(line)

# Join all spoken text, normalize
full_text = " ".join(spoken_lines)

# Remove bracketed annotations like [chuckles], [end], [Bg. 18.66]
full_text = re.sub(r"\[.*?\]", "", full_text)

# Replace diacritical marks for pronunciation lookup
# Kṛṣṇa → krishna, Rāma → rama, etc.
replacements = {
    "Kṛṣṇa": "krishna",
    "kṛṣṇa": "krishna",
    "Rāma": "rama",
    "rāma": "rama",
    "Bhagavad-gītā": "bhagavad gita",
    "bhagavad-gītā": "bhagavad gita",
    "Śrīmad-Bhāgavatam": "srimad bhagavatam",
    "Bhāgavatam": "bhagavatam",
    "gītā": "gita",
    "Gītā": "gita",
    "brāhmaṇa": "brahmana",
    "brāhmaṇas": "brahmanas",
    "kṣatriya": "kshatriya",
    "vaiśya": "vaishya",
    "śūdra": "shudra",
    "śūdras": "shudras",
    "sarva-dharmān": "sarva dharman",
    "parityajya": "parityajya",
    "ekaṁ": "ekam",
    "śaraṇaṁ": "sharanam",
    "mām": "mam",
    "vraja": "vraja",
    "sato vṛtteḥ": "sato vritteh",
    "vṛtti": "vritti",
}

for orig, repl in replacements.items():
    full_text = full_text.replace(orig, repl)

# Tokenize: split into words, strip punctuation, lowercase
raw_words = full_text.split()
clean_words = []
for w in raw_words:
    # Strip punctuation
    w = re.sub(r"[^a-zA-Z'-]", "", w).lower().strip("'-")
    if w and len(w) >= 1:
        clean_words.append(w)

print(f"Total words in transcript: {len(clean_words)}")
print(f"First 20: {' '.join(clean_words[:20])}")
print(f"Last 20:  {' '.join(clean_words[-20:])}")

# =============================================================================
# 2. BUILD PRONUNCIATION DICTIONARY
# =============================================================================

print("\nBuilding pronunciation dictionary...")

# Load CMU dict
try:
    from nltk.corpus import cmudict

    cmu = cmudict.dict()
    print(f"CMU dict loaded: {len(cmu)} entries")
except Exception:
    cmu = {}
    print("WARNING: CMU dict not available")

# Builtin fallbacks for words not in CMU
BUILTIN = {
    "a": ["AH"],
    "an": ["AE", "N"],
    "the": ["DH", "AH"],
    "i": ["AY"],
    "is": ["IH", "Z"],
    "am": ["AE", "M"],
    "are": ["AA", "R"],
    "was": ["W", "AA", "Z"],
    "not": ["N", "AA", "T"],
    "but": ["B", "AH", "T"],
    "and": ["AE", "N", "D"],
    "or": ["AO", "R"],
    "to": ["T", "UW"],
    "of": ["AH", "V"],
    "in": ["IH", "N"],
    "it": ["IH", "T"],
    "he": ["HH", "IY"],
    "she": ["SH", "IY"],
    "we": ["W", "IY"],
    "you": ["Y", "UW"],
    "they": ["DH", "EY"],
    "this": ["DH", "IH", "S"],
    "that": ["DH", "AE", "T"],
    "so": ["S", "OW"],
    "yes": ["Y", "EH", "S"],
    "no": ["N", "OW"],
    "oh": ["OW"],
    "eh": ["EH"],
    "come": ["K", "AH", "M"],
    "came": ["K", "EY", "M"],
    "go": ["G", "OW"],
    "krishna": ["K", "R", "IH", "SH", "N", "AH"],
    "consciousness": ["K", "AA", "N", "SH", "AH", "S", "N", "AH", "S"],
    "hare": ["HH", "AA", "R", "EY"],
    "rama": ["R", "AA", "M", "AH"],
    "gita": ["G", "IY", "T", "AH"],
    "bhagavad": ["B", "AH", "G", "AH", "V", "AH", "D"],
    "vedic": ["V", "EY", "D", "IH", "K"],
    "brahmana": ["B", "R", "AA", "M", "AH", "N", "AH"],
    "brahmanas": ["B", "R", "AA", "M", "AH", "N", "AH", "Z"],
    "kshatriya": ["K", "SH", "AA", "T", "R", "IY", "AH"],
    "vaishya": ["V", "AY", "SH", "Y", "AH"],
    "shudra": ["SH", "UW", "D", "R", "AH"],
    "shudras": ["SH", "UW", "D", "R", "AH", "Z"],
    "srimad": ["SH", "R", "IY", "M", "AH", "D"],
    "bhagavatam": ["B", "AH", "G", "AH", "V", "AH", "T", "AH", "M"],
    "mohammedan": ["M", "OW", "HH", "AE", "M", "AH", "D", "AH", "N"],
    "koran": ["K", "AO", "R", "AE", "N"],
    "zen": ["Z", "EH", "N"],
    "sarva": ["S", "AA", "R", "V", "AH"],
    "dharman": ["D", "AA", "R", "M", "AH", "N"],
    "parityajya": ["P", "AA", "R", "IH", "T", "Y", "AH", "JH", "Y", "AH"],
    "ekam": ["EY", "K", "AH", "M"],
    "sharanam": ["SH", "AA", "R", "AH", "N", "AH", "M"],
    "mam": ["M", "AA", "M"],
    "vraja": ["V", "R", "AH", "JH", "AH"],
    "sato": ["S", "AA", "T", "OW"],
    "vritteh": ["V", "R", "IH", "T", "EH"],
    "vritti": ["V", "R", "IH", "T", "IY"],
}


def get_pronunciation(word):
    """Get ARPAbet phones for a word. CMU first, then builtin."""
    if word in BUILTIN:
        return BUILTIN[word]
    if word in cmu:
        return [p.rstrip("012") for p in cmu[word][0]]
    return None


# Check coverage
missing = set()
for w in clean_words:
    if get_pronunciation(w) is None:
        missing.add(w)

if missing:
    print(f"\nWARNING: {len(missing)} words without pronunciation:")
    for w in sorted(missing)[:30]:
        print(f"  '{w}'")
    print(f"\nFiltering transcript to words with known pronunciation...")

# Filter transcript to words with pronunciation
transcript_words = [w for w in clean_words if get_pronunciation(w) is not None]
print(
    f"Usable words: {len(transcript_words)}/{len(clean_words)} ({len(transcript_words) / len(clean_words) * 100:.1f}%)"
)

# Total phonemes
total_phones = sum(len(get_pronunciation(w)) for w in transcript_words)
print(f"Total phonemes: {total_phones}")

# =============================================================================
# 3. LOAD MODEL + EXTRACT FEATURES
# =============================================================================

print("\n" + "=" * 70)
print("LOADING MODEL + EXTRACTING FEATURES")
print("=" * 70)

# Load existing model (v2 from Exp 38)
data = np.load(
    "vibe_core/mahamantra_research/shabda_recognition/tiny_asr_weights_v2.npz",
    allow_pickle=True,
)
W1, b1 = data["W1"], data["b1"]
W2, b2 = data["W2"], data["b2"]
X_mean_old, X_std_old = data["X_mean"], data["X_std"]
CLASSES = list(data["classes"])
CTX = int(data["context"])
N_CLASSES = len(CLASSES)
c2i = {c: i for i, c in enumerate(CLASSES)}

print(f"Model loaded: {W1.shape[0]}→{W1.shape[1]}→{W2.shape[1]} ({N_CLASSES} classes)")
print(f"Classes: {CLASSES}")

# Extract features from the full interview
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


print(f"\nLoading audio: {AUDIO_PATH}")
t0 = time.time()
file_sr, raw = wavfile.read(AUDIO_PATH)
if raw.ndim > 1:
    raw = raw.mean(axis=1)  # stereo → mono
if raw.dtype == np.int16:
    raw = raw.astype(np.float64) / 32768.0
elif raw.dtype == np.int32:
    raw = raw.astype(np.float64) / 2147483648.0
else:
    raw = raw.astype(np.float64)

# Resample to 44100 if needed
if file_sr != SR:
    print(f"  Resampling {file_sr}→{SR}Hz...")
    ratio = SR / file_sr
    n_out = int(len(raw) * ratio)
    x_old = np.arange(len(raw))
    x_new = np.linspace(0, len(raw) - 1, n_out)
    raw = np.interp(x_new, x_old, raw)

n_frames = (len(raw) - N_FFT) // hop
duration_s = n_frames * 10 / 1000
print(f"Audio loaded: {len(raw)} samples, {n_frames} frames ({duration_s:.1f}s / {duration_s / 60:.1f}min)")

print("Extracting log-Mel features...")
X_full = np.zeros((n_frames, N_MELS))
for i in range(n_frames):
    start_sample = i * hop
    X_full[i] = extract_log_mel(raw[start_sample : start_sample + N_FFT])

dt = time.time() - t0
print(f"Features extracted in {dt:.1f}s: {X_full.shape}")

# =============================================================================
# 4. FIRST PASS: INFERENCE + VITERBI WITH EXISTING MODEL
# =============================================================================

print("\n" + "=" * 70)
print("PASS 1: VITERBI ALIGNMENT (existing model from 14s Japa)")
print("=" * 70)

print("Adding context and normalizing...")
X_ctx = add_context(X_full, CTX)
X_norm = (X_ctx - X_mean_old) / X_std_old

print("Running inference...")
t0 = time.time()
frame_probs = np.zeros((n_frames, N_CLASSES))
BS_INF = 512  # batch inference for speed
for batch_start in range(0, n_frames, BS_INF):
    batch_end = min(batch_start + BS_INF, n_frames)
    batch = X_norm[batch_start:batch_end]
    h = np.maximum(0, batch @ W1 + b1)
    logits = h @ W2 + b2
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    frame_probs[batch_start:batch_end] = e / e.sum(axis=1, keepdims=True)
dt = time.time() - t0
print(f"Inference done in {dt:.1f}s")

# Quick check: what phonemes does the model predict most?
preds = np.argmax(frame_probs, axis=1)
phone_counts = {}
for p in preds:
    phone_counts[CLASSES[p]] = phone_counts.get(CLASSES[p], 0) + 1
print("\nTop predicted phonemes (before alignment):")
for p, c in sorted(phone_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {p:4s}: {c:6d} frames ({c / n_frames * 100:.1f}%)")

# Build state sequence
SILENCE = "SIL"
states = []
for wi, word in enumerate(transcript_words):
    if wi > 0:
        states.append((SILENCE, "_pause_", "silence"))
    phones = get_pronunciation(word)
    for p in phones:
        states.append((p, word, "phoneme"))

N_STATES = len(states)
print(f"\nViterbi states: {N_STATES} (from {len(transcript_words)} words)")
print(f"Frames: {n_frames}")
print(f"Ratio: {n_frames / N_STATES:.1f} frames/state")

# Run Viterbi
print("\nRunning Viterbi alignment (this may take a while for 25min audio)...")
t0 = time.time()

log_probs = np.log(frame_probs + 1e-30)
SELF_PROB = 0.7
ADVANCE_PROB = 0.3
log_self = np.log(SELF_PROB)
log_advance = np.log(ADVANCE_PROB)

# For large audio, we use a band constraint to speed up Viterbi.
# The alignment path should roughly follow a diagonal through the
# (frames × states) matrix. We only compute within a band around this diagonal.
BAND_WIDTH = max(500, n_frames // 10)  # frames of slack


# Expected state at frame t (linear interpolation)
def expected_state(t):
    return int(t * N_STATES / n_frames)


V = np.full((n_frames, N_STATES), -np.inf)
BP = np.zeros((n_frames, N_STATES), dtype=np.int32)


def emission(t, s):
    phone = states[s][0]
    if phone in c2i:
        return log_probs[t, c2i[phone]]
    return -10.0


V[0, 0] = emission(0, 0)

for t in range(1, n_frames):
    # Band constraint
    center = expected_state(t)
    s_min = max(0, center - BAND_WIDTH)
    s_max = min(N_STATES, center + BAND_WIDTH)

    for s in range(s_min, s_max):
        score_self = V[t - 1, s] + log_self + emission(t, s)
        score_adv = V[t - 1, s - 1] + log_advance + emission(t, s) if s > 0 else -np.inf

        if score_self >= score_adv:
            V[t, s] = score_self
            BP[t, s] = s
        else:
            V[t, s] = score_adv
            BP[t, s] = s - 1

        if s >= 2 and states[s - 1][2] == "silence":
            score_skip = V[t - 1, s - 2] + log_advance + emission(t, s) - 1.0
            if score_skip > V[t, s]:
                V[t, s] = score_skip
                BP[t, s] = s - 2

    # Progress
    if t % 10000 == 0:
        pct = t / n_frames * 100
        elapsed = time.time() - t0
        eta = elapsed / (t / n_frames) - elapsed if t > 0 else 0
        print(f"  {pct:5.1f}% ({t}/{n_frames} frames, elapsed={elapsed:.0f}s, ETA={eta:.0f}s)")

# Backtrace
state_path = np.zeros(n_frames, dtype=np.int32)
best_end = N_STATES - 1
for s in range(max(0, N_STATES - 20), N_STATES):
    if V[-1, s] > V[-1, best_end]:
        best_end = s
state_path[-1] = best_end

for t in range(n_frames - 2, -1, -1):
    state_path[t] = BP[t + 1, state_path[t + 1]]

dt = time.time() - t0
print(f"\nViterbi Pass 1 done in {dt:.1f}s")
print(f"Final state: {state_path[-1]}/{N_STATES - 1}")

# Extract word boundaries
viterbi_labels = [states[s][0] for s in state_path]
viterbi_words = [states[s][1] for s in state_path]

prev_w = ""
word_starts = []
for i in range(n_frames):
    w = viterbi_words[i]
    if w != prev_w and w != "_pause_":
        word_starts.append((i, w))
        prev_w = w if w != "_pause_" else prev_w

print(f"\nPass 1: Found {len(word_starts)} word boundaries (expected {len(transcript_words)})")

# Show first/last 10 word boundaries
print("\nFirst 10 words:")
for start, word in word_starts[:10]:
    end = start
    while end < n_frames and viterbi_words[end] == word:
        end += 1
    dur = (end - start) * 10
    print(f"  {start * 10:6d}-{end * 10:6d}ms ({dur:5d}ms): {word}")

print("\nLast 10 words:")
for start, word in word_starts[-10:]:
    end = start
    while end < n_frames and viterbi_words[end] == word:
        end += 1
    dur = (end - start) * 10
    print(f"  {start * 10:6d}-{end * 10:6d}ms ({dur:5d}ms): {word}")

# PER
viterbi_phonemes = []
prev_p = ""
for p in viterbi_labels:
    if p != prev_p and p != SILENCE:
        viterbi_phonemes.append(p)
        prev_p = p
    elif p == SILENCE:
        prev_p = p

expected_phonemes = []
for w in transcript_words:
    expected_phonemes.extend(get_pronunciation(w))


def levenshtein(s1, s2):
    n, m = len(s1), len(s2)
    if n == 0:
        return m
    if m == 0:
        return n
    # Memory-efficient: only keep two rows
    prev = list(range(m + 1))
    curr = [0] * (m + 1)
    for i in range(1, n + 1):
        curr[0] = i
        for j in range(1, m + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev
    return prev[m]


per1 = levenshtein(viterbi_phonemes, expected_phonemes) / max(len(expected_phonemes), 1)
print(f"\nPass 1 PER: {per1:.1%}")
print(f"Decoded phonemes: {len(viterbi_phonemes)}, Expected: {len(expected_phonemes)}")

# Word recall
matched = 0
found_words = [w for _, w in word_starts]
tw_copy = list(transcript_words)
for fw in found_words:
    if fw in tw_copy:
        tw_copy.remove(fw)
        matched += 1
recall = matched / max(len(transcript_words), 1)
print(f"Word recall: {matched}/{len(transcript_words)} = {recall:.1%}")

# =============================================================================
# 5. RE-TRAIN TINY ASR ON INTERVIEW DATA
# =============================================================================

print("\n" + "=" * 70)
print("RE-TRAINING TINY ASR ON INTERVIEW DATA")
print("=" * 70)

# Build class set from alignment labels
ALL_CLASSES = sorted(set(viterbi_labels))
N_CLS = len(ALL_CLASSES)
c2i_new = {c: i for i, c in enumerate(ALL_CLASSES)}
y_train = np.array([c2i_new[l] for l in viterbi_labels])

print(f"Classes: {N_CLS} ({ALL_CLASSES})")
print(f"Training frames: {n_frames}")

# Fresh model, seed-initialized
D_in = X_ctx.shape[1]
HIDDEN = 128
rng = np.random.RandomState(MAHA_QUANTUM)
W1_new = rng.randn(D_in, HIDDEN).astype(np.float64) * np.sqrt(2.0 / D_in)
b1_new = np.zeros(HIDDEN)
W2_new = rng.randn(HIDDEN, N_CLS).astype(np.float64) * np.sqrt(2.0 / HIDDEN)
b2_new = np.zeros(N_CLS)

# Normalize with interview data stats
X_mean_new = X_ctx.mean(axis=0)
X_std_new = X_ctx.std(axis=0) + 1e-8
X_norm_new = (X_ctx - X_mean_new) / X_std_new

# Training
LR = 0.01
EPOCHS = 200
BS = 256
indices = np.arange(n_frames)

print(f"\nTraining: {EPOCHS} epochs, lr={LR}, batch={BS}")
t0 = time.time()

for epoch in range(EPOCHS):
    rng.shuffle(indices)
    total_loss = 0.0
    correct = 0

    for bs in range(0, n_frames, BS):
        bi = indices[bs : bs + BS]
        bx = X_norm_new[bi]
        by = y_train[bi]
        B = len(bi)

        h = np.maximum(0, bx @ W1_new + b1_new)
        logits = h @ W2_new + b2_new
        e = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)

        targets = np.zeros((B, N_CLS))
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

    if epoch % 25 == 0 or epoch == EPOCHS - 1:
        acc = correct / n_frames
        elapsed = time.time() - t0
        print(f"  Epoch {epoch:3d}: loss={total_loss / n_frames:.4f}  acc={acc:.1%}  ({elapsed:.0f}s)")

dt_train = time.time() - t0
print(f"\nTraining done in {dt_train:.1f}s")

# =============================================================================
# 6. SECOND VITERBI PASS (retrained model)
# =============================================================================

print("\n" + "=" * 70)
print("PASS 2: VITERBI ALIGNMENT (retrained model)")
print("=" * 70)

print("Running inference with retrained model...")
frame_probs2 = np.zeros((n_frames, N_CLS))
for batch_start in range(0, n_frames, BS_INF):
    batch_end = min(batch_start + BS_INF, n_frames)
    batch = X_norm_new[batch_start:batch_end]
    h = np.maximum(0, batch @ W1_new + b1_new)
    logits = h @ W2_new + b2_new
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    frame_probs2[batch_start:batch_end] = e / e.sum(axis=1, keepdims=True)

log_probs2 = np.log(frame_probs2 + 1e-30)

print("Running Viterbi Pass 2...")
t0 = time.time()

V2 = np.full((n_frames, N_STATES), -np.inf)
BP2 = np.zeros((n_frames, N_STATES), dtype=np.int32)


def emission2(t, s):
    phone = states[s][0]
    if phone in c2i_new:
        return log_probs2[t, c2i_new[phone]]
    return -10.0


V2[0, 0] = emission2(0, 0)

for t in range(1, n_frames):
    center = expected_state(t)
    s_min = max(0, center - BAND_WIDTH)
    s_max = min(N_STATES, center + BAND_WIDTH)

    for s in range(s_min, s_max):
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

    if t % 10000 == 0:
        pct = t / n_frames * 100
        elapsed = time.time() - t0
        eta = elapsed / (t / n_frames) - elapsed if t > 0 else 0
        print(f"  {pct:5.1f}% (elapsed={elapsed:.0f}s, ETA={eta:.0f}s)")

state_path2 = np.zeros(n_frames, dtype=np.int32)
best_end2 = N_STATES - 1
for s in range(max(0, N_STATES - 20), N_STATES):
    if V2[-1, s] > V2[-1, best_end2]:
        best_end2 = s
state_path2[-1] = best_end2

for t in range(n_frames - 2, -1, -1):
    state_path2[t] = BP2[t + 1, state_path2[t + 1]]

dt = time.time() - t0
print(f"\nViterbi Pass 2 done in {dt:.1f}s")

# Extract results
viterbi_labels2 = [states[s][0] for s in state_path2]
viterbi_words2 = [states[s][1] for s in state_path2]

prev_w = ""
word_starts2 = []
for i in range(n_frames):
    w = viterbi_words2[i]
    if w != prev_w and w != "_pause_":
        word_starts2.append((i, w))
        prev_w = w if w != "_pause_" else prev_w

viterbi_phonemes2 = []
prev_p = ""
for p in viterbi_labels2:
    if p != prev_p and p != SILENCE:
        viterbi_phonemes2.append(p)
        prev_p = p
    elif p == SILENCE:
        prev_p = p

per2 = levenshtein(viterbi_phonemes2, expected_phonemes) / max(len(expected_phonemes), 1)

matched2 = 0
found2 = [w for _, w in word_starts2]
tw_copy2 = list(transcript_words)
for fw in found2:
    if fw in tw_copy2:
        tw_copy2.remove(fw)
        matched2 += 1
recall2 = matched2 / max(len(transcript_words), 1)

print(f"\nPass 2 Results:")
print(f"  PER: {per2:.1%}")
print(f"  Word recall: {matched2}/{len(transcript_words)} = {recall2:.1%}")
print(f"  Words found: {len(word_starts2)}")

# =============================================================================
# 7. SAVE IMPROVED WEIGHTS
# =============================================================================

out_path = "vibe_core/mahamantra_research/shabda_recognition/tiny_asr_weights_v3_interview.npz"
np.savez_compressed(
    out_path,
    W1=W1_new,
    b1=b1_new,
    W2=W2_new,
    b2=b2_new,
    X_mean=X_mean_new,
    X_std=X_std_new,
    classes=np.array(ALL_CLASSES),
    context=CTX,
)
n_params = W1_new.size + b1_new.size + W2_new.size + b2_new.size
print(f"\nSaved v3 weights: {out_path}")
print(f"  Model: {D_in}→{HIDDEN}→{N_CLS} ({n_params} params)")
print(f"  Trained on: {duration_s:.0f}s of audio ({n_frames} frames)")

# =============================================================================
# 8. SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY: Experiment 39 — Radio Interview Bootstrapping")
print("=" * 70)
print(f"Audio: {AUDIO_PATH}")
print(f"Duration: {duration_s:.0f}s ({duration_s / 60:.1f}min)")
print(f"Frames: {n_frames}")
print(f"Transcript words: {len(transcript_words)} (of {len(clean_words)} total)")
print(f"Total phonemes: {total_phones}")
print(f"Viterbi states: {N_STATES}")
print(f"")
print(f"Pass 1 (Japa model): PER={per1:.1%}, Word recall={recall:.1%}")
print(f"Pass 2 (retrained):  PER={per2:.1%}, Word recall={recall2:.1%}")
print(f"")
print(f"Model: {D_in}→{HIDDEN}→{N_CLS} ({n_params} params)")
print(f"Weights saved: {out_path}")
