"""
EXPERIMENT 15: MFCC Imprint — Hear first, then match
======================================================

The intake (mic) already extracts 13 MFCCs per 10ms frame.
But we never accumulate them into a segment-level IMPRINT.

Real STT: accumulate spectral features over time → match pattern.
We have the features. We just skip accumulation.

Approach:
  1. Per audio segment: average MFCCs across all frames → 13-dim "voice print"
  2. Per dictionary word: generate reference MFCC from known phoneme sequence
  3. Match: cosine similarity of 13-dim vectors

This is the simplest possible "hear first" approach:
  - No RAMA coords
  - No phoneme classification per frame
  - Just: what does this stretch of sound LOOK LIKE spectrally?
  - Compare: what SHOULD word X look like spectrally?

The MFCC vector IS the imprint. Each coefficient captures a different
aspect of the spectral shape (like different resonance bands).
"""
import sys; sys.path.insert(0, ".")
import math
import numpy as np
from typing import Dict, List, Tuple, Sequence

from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake, unpack_frame, extract_mfcc,
)
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, get_pronunciation_dict, _MFCC_PROTOTYPES,
    ARPABET_TO_RAMA,
)

# === Load audio ===
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

print(f"Audio: {stream.duration_ms}ms, {len(stream.frames)} frames, {len(segments)} segments")
print(f"MFCC frames available: {len(stream.mfcc_frames) if stream.mfcc_frames else 0}")


# === Part 1: Segment-level MFCC imprints ===
print()
print("=" * 70)
print("PART 1: Audio segment MFCC imprints (averaged over frames)")
print("=" * 70)

def segment_mfcc_imprint(seg_start: int, seg_end: int, all_mfcc) -> Tuple[float, ...]:
    """Average MFCC across all frames in segment → 13-dim vector."""
    if not all_mfcc:
        return (0.0,) * 13
    
    vectors = []
    for i in range(seg_start, min(seg_end, len(all_mfcc))):
        mfcc = all_mfcc[i]
        if any(c != 0 for c in mfcc):
            vectors.append(mfcc)
    
    if not vectors:
        return (0.0,) * 13
    
    # Average each coefficient
    n = len(vectors)
    avg = tuple(sum(v[j] for v in vectors) / n for j in range(13))
    return avg


def cosine_sim(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity, skipping c0 (energy) — use c1-c12 only."""
    if len(a) < 2 or len(b) < 2:
        return 0.0
    a_use = a[1:]  # skip c0
    b_use = b[1:]
    dot = sum(x * y for x, y in zip(a_use, b_use))
    na = math.sqrt(sum(x * x for x in a_use))
    nb = math.sqrt(sum(x * x for x in b_use))
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return dot / (na * nb)


for si, seg in enumerate(segments[:8]):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    imprint = segment_mfcc_imprint(seg.start, seg.end, stream.mfcc_frames)
    # Show c1-c4 (most discriminative coefficients)
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] c1-c4: ({imprint[1]:7.1f}, {imprint[2]:7.1f}, "
          f"{imprint[3]:7.1f}, {imprint[4]:7.1f})")


# === Part 2: Reference MFCC imprints from phoneme templates ===
print()
print("=" * 70)
print("PART 2: Word reference MFCC imprints (from ARPAbet phoneme templates)")
print("=" * 70)

# For each word in the pronunciation dict, we know its ARPAbet phoneme sequence
# (via CMU dict). Each phoneme has an MFCC prototype in _MFCC_PROTOTYPES.
# The word's MFCC imprint = average of its phoneme MFCCs (weighted by duration).

pdict = get_pronunciation_dict()
pdict._ensure_loaded()

# Build reverse map: RAMA coord → ARPAbet phoneme
RAMA_TO_ARPABET: Dict[int, str] = {}
for arpabet, rama in ARPABET_TO_RAMA.items():
    RAMA_TO_ARPABET[rama] = arpabet


def word_mfcc_imprint(word: str) -> Tuple[float, ...]:
    """Get reference MFCC imprint for a word from its phoneme sequence."""
    coords = pdict.lookup(word)
    if not coords:
        return (0.0,) * 13
    
    mfccs = []
    for c in coords:
        arpabet = RAMA_TO_ARPABET.get(c)
        if arpabet and arpabet in _MFCC_PROTOTYPES:
            mfccs.append(_MFCC_PROTOTYPES[arpabet])
    
    if not mfccs:
        return (0.0,) * 13
    
    n = len(mfccs)
    avg = tuple(sum(m[j] for m in mfccs) / n for j in range(13))
    return avg


# Build reference imprints for expected vocabulary
VOCAB = ["eh", "not", "exactly", "but", "i", "came", "to", "preach",
         "the", "gospel", "of", "krishna", "consciousness", "and",
         "fortunately", "met", "some", "enthusiastic", "young", 
         "boys", "girls"]

word_imprints: Dict[str, Tuple[float, ...]] = {}
for word in VOCAB:
    imp = word_mfcc_imprint(word)
    if any(c != 0 for c in imp):
        word_imprints[word] = imp
        print(f"  '{word:15s}' c1-c4: ({imp[1]:7.1f}, {imp[2]:7.1f}, "
              f"{imp[3]:7.1f}, {imp[4]:7.1f})")

print(f"\n  Reference imprints built: {len(word_imprints)}/{len(VOCAB)}")


# === Part 3: Cross-word discrimination ===
print()
print("=" * 70)
print("PART 3: Cross-word cosine similarity (discrimination power)")
print("=" * 70)

show_words = [w for w in VOCAB[:10] if w in word_imprints]
print(f"{'':12s}", end="")
for w in show_words:
    print(f" {w:>8s}", end="")
print()
for w1 in show_words:
    print(f"{w1:12s}", end="")
    for w2 in show_words:
        sim = cosine_sim(word_imprints[w1], word_imprints[w2])
        print(f" {sim:8.3f}", end="")
    print()


# === Part 4: Match audio segments to words ===
print()
print("=" * 70)
print("PART 4: Audio → MFCC imprint → match against word imprints")
print("=" * 70)

EXPECTED_WORDS = [
    "eh", "not", "exactly", "but", "i", "came", "to", "preach",
    "the", "gospel", "of", "krishna", "consciousness", "and",
    "fortunately", "i", "met", "some", "enthusiastic", "young",
    "boys", "and", "girls",
]

words_out = []
for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    
    audio_imp = segment_mfcc_imprint(seg.start, seg.end, stream.mfcc_frames)
    if not any(c != 0 for c in audio_imp):
        continue
    
    best_word = ""
    best_sim = -1.0
    for word, ref_imp in word_imprints.items():
        sim = cosine_sim(audio_imp, ref_imp)
        if sim > best_sim:
            best_sim = sim
            best_word = word
    
    expected = EXPECTED_WORDS[si] if si < len(EXPECTED_WORDS) else "?"
    match = "✓" if best_word == expected else " "
    in_vocab = "▪" if best_word in set(EXPECTED_WORDS) else " "
    
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} sim={best_sim:.4f} {match}{in_vocab}  "
          f"(expected: {expected})")
    words_out.append(best_word)

correct = sum(1 for i, w in enumerate(words_out) 
              if i < len(EXPECTED_WORDS) and w == EXPECTED_WORDS[i])
in_vocab = sum(1 for w in words_out if w in set(EXPECTED_WORDS))
total = len(words_out)

print(f"\nMFCC TRANSCRIPT: {' '.join(words_out)}")
print(f"Exact position match: {correct}/{total} ({correct/max(1,total)*100:.0f}%)")
print(f"In expected vocab:    {in_vocab}/{total} ({in_vocab/max(1,total)*100:.0f}%)")
