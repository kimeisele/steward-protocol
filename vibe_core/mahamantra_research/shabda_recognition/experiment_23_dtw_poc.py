"""
EXPERIMENT 23: DTW Proof of Concept
=====================================

Test the new Late Binding approach:
  Audio segment → MFCC matrix → DTW against word templates → best match

Instead of classifying each frame into a phoneme (early binding),
we keep the audio as-is and compare the whole MFCC trajectory
against synthetic word templates.

Vowel anchor filtering reduces candidates from 123K to ~100.
"""

import sys

sys.path.insert(0, ".")
import time

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream,
    get_pronunciation_dict,
    PronunciationDict,
)
from vibe_core.mahamantra.sound.shabda_dtw import (
    segment_to_mfcc_matrix,
    word_mfcc_template,
    dtw_score,
    extract_vowel_anchor_formants,
    filter_candidates_by_vowel,
    _VOWEL_PARAMS,
)

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

# Load CMU dict directly for ARPAbet sequences
try:
    from nltk.corpus import cmudict

    cmu = cmudict.dict()
except Exception:
    print("ERROR: nltk cmudict required")
    sys.exit(1)

hop = int(stream.sample_rate * 10 / 1000)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = EXPECTED.lower().split()

print("=" * 70)
print("EXPERIMENT 23: DTW LATE-BINDING DECODER")
print("=" * 70)

# Build a focused candidate list: common English + expected words
# For PoC, we test against a manageable vocabulary
from vibe_core.mahamantra.sound.shabda_decoder import _COMMON_ENGLISH

vocab_words = set(_COMMON_ENGLISH)
vocab_words.update(expected_words)

# Build ARPAbet sequences for all vocab words
word_phones: dict = {}  # word → list of ARPAbet strings
for w in vocab_words:
    prons = cmu.get(w)
    if prons:
        word_phones[w] = [p.rstrip("012") for p in prons[0]]

print(f"Vocab: {len(word_phones)} words with CMU pronunciations")
print()

# Pre-compute word MFCC templates (cache for speed)
print("Pre-computing word MFCC templates...")
t0 = time.time()
word_templates: dict = {}  # word → np.ndarray [frames × 13]
for w, phones in word_phones.items():
    word_templates[w] = word_mfcc_template(phones)
t1 = time.time()
print(f"  {len(word_templates)} templates in {t1 - t0:.2f}s")
print()

# Decode each segment
print("=" * 70)
print("DECODING")
print("=" * 70)

decoded_words = []
total_dtw_time = 0.0

for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    expected = expected_words[si] if si < len(expected_words) else "?"

    # Step 1: Extract audio MFCC matrix
    seg_mfcc_frames = None
    if stream.mfcc_frames is not None:
        seg_mfcc_frames = stream.mfcc_frames[seg.start : seg.end]

    audio_mfcc = segment_to_mfcc_matrix(
        seg.frames,
        stream.raw_samples,
        stream.sample_rate,
        seg.start,
        hop,
        stream.n_fft,
        seg_mfcc_frames,
    )

    # Step 2: Vowel anchor for filtering
    anchor = extract_vowel_anchor_formants(
        seg.frames,
        stream.raw_samples,
        stream.sample_rate,
        seg.start,
        hop,
        stream.n_fft,
    )

    # Step 3: Filter candidates by vowel anchor
    if anchor:
        filtered = filter_candidates_by_vowel(
            anchor,
            [(w, phones) for w, phones in word_phones.items()],
        )
        candidate_words = [w for w, _ in filtered]
    else:
        candidate_words = list(word_phones.keys())

    # Duration filter: reject words whose template is wildly different length
    seg_frames = len(seg.frames)
    duration_filtered = []
    for w in candidate_words:
        tmpl = word_templates.get(w)
        if tmpl is None:
            continue
        ratio = len(tmpl) / max(seg_frames, 1)
        if 0.15 < ratio < 4.0:  # generous range
            duration_filtered.append(w)
    candidate_words = duration_filtered if duration_filtered else candidate_words[:200]

    # Step 4: DTW scoring
    t_dtw = time.time()
    best_word = "?"
    best_score = 0.0
    scores_debug = []

    for w in candidate_words:
        tmpl = word_templates.get(w)
        if tmpl is None:
            continue
        score = dtw_score(audio_mfcc, tmpl)
        scores_debug.append((w, score))
        if score > best_score:
            best_score = score
            best_word = w

    total_dtw_time += time.time() - t_dtw

    decoded_words.append(best_word)

    # Show top 3 candidates
    scores_debug.sort(key=lambda x: -x[1])
    top3 = scores_debug[:3]
    top3_str = ", ".join(f"{w}:{s:.3f}" for w, s in top3)

    match = "✓" if best_word == expected else " "
    print(
        f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} ({best_score:.3f}) {match}  "
        f"expected={expected:15s}  anchor={anchor or '?':3s}  "
        f"cands={len(candidate_words):4d}  top3=[{top3_str}]"
    )

# Summary
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

decoded_text = " ".join(decoded_words)
exact = sum(1 for i, w in enumerate(decoded_words) if i < len(expected_words) and w == expected_words[i])
in_expected = sum(1 for w in decoded_words if w in set(expected_words))

print(f"DECODED:   {decoded_text}")
print(f"EXPECTED:  {EXPECTED}")
print(f"\nExact position: {exact}/{min(len(decoded_words), len(expected_words))}")
print(f"In expected:    {in_expected}/{len(decoded_words)}")
print(f"DTW time:       {total_dtw_time:.2f}s total")
