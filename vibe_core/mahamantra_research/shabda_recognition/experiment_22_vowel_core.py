"""
EXPERIMENT 22: Match words by VOWEL CORE only
===============================================

Finding from exp 20-21: vowel formants now correctly identify AH, EH, etc.
Consonants are still misclassified. But most English words are distinguished
by their vowel sequence alone:
  "but" = AH, "not" = AH, "came" = EY, "preach" = IY, "some" = AH, etc.

Strategy: Extract only the HIGH-CONFIDENCE vowel phonemes from each segment
(frames where RMS > threshold AND formant match > threshold), then match
against dict words using only vowel coords.

This sidesteps the consonant classification problem entirely.
"""
import sys; sys.path.insert(0, ".")
import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake, unpack_frame, extract_formants,
)
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, score_frame, get_pronunciation_dict,
    _stable_coords, _dedup_coords, _score_candidate,
    ARPABET_TO_RAMA, PHONEME_TEMPLATES,
)

# Which ARPAbet phonemes are vowels?
VOWEL_ARPABETS = {
    "AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY", "ER",
    "IH", "IY", "OW", "OY", "UH", "UW",
}

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

pdict = get_pronunciation_dict()
pdict._ensure_loaded()

hop = int(stream.sample_rate * 10 / 1000)
n_fft = stream.n_fft

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = EXPECTED.lower().split()

print("=" * 70)
print("VOWEL-CORE DECODING")
print("=" * 70)

decoded_words = []

for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    # Extract per-frame phoneme scores, keep only confident vowels
    vowel_votes = []  # (arpabet, score) for vowel frames
    prev_rms = 0

    for i, frame in enumerate(seg.frames):
        rms = frame & 0xFF
        if rms < 40:  # higher threshold for confident frames
            prev_rms = rms
            continue

        f1, f2 = 0, 0
        sample_start = (seg.start + i) * hop
        sample_end = sample_start + n_fft
        if stream.raw_samples is not None and sample_end <= len(stream.raw_samples):
            f1, f2 = extract_formants(
                stream.raw_samples[sample_start:sample_end], stream.sample_rate
            )

        if f1 == 0 or f2 == 0:
            prev_rms = rms
            continue

        candidates = score_frame(frame, f1=f1, f2=f2, prev_rms=prev_rms)
        prev_rms = rms

        if not candidates:
            continue

        # Keep only vowel candidates
        for arpabet, score in candidates[:1]:
            if arpabet in VOWEL_ARPABETS and score > 0.70:
                vowel_votes.append((arpabet, score))

    if not vowel_votes:
        decoded_words.append(("?", 0.0))
        continue

    # Count vowel phoneme votes
    from collections import Counter
    vote_counts = Counter(v[0] for v in vowel_votes)
    top_vowel = vote_counts.most_common(1)[0][0]
    top_coord = ARPABET_TO_RAMA[top_vowel]

    # Also get second vowel if significant
    vowel_coords = []
    # Build coord sequence from majority-voted time windows
    window = 3
    for wi in range(0, len(vowel_votes), window):
        chunk = vowel_votes[wi:wi + window]
        chunk_counts = Counter(v[0] for v in chunk)
        winner = chunk_counts.most_common(1)[0][0]
        vowel_coords.append(ARPABET_TO_RAMA[winner])

    vowel_dedup = _dedup_coords(tuple(vowel_coords))

    # Score against dict words using just the vowel coords
    # Extract vowel-only coords from dict words too
    best_word = ""
    best_score = 0.0

    # Search dict
    for lang_dict in [pdict._english, pdict._sanskrit]:
        if lang_dict is None:
            continue
        for word, word_coords in lang_dict.items():
            # Extract vowel coords from dict word
            dict_vowels = tuple(c for c in word_coords if c < 16)
            if not dict_vowels and not vowel_dedup:
                continue

            # Score: compare vowel coord sequences
            score = _score_candidate(vowel_dedup, dict_vowels) if dict_vowels else 0.0
            # Length bonus: prefer words with similar segment duration
            expected_ms = len(word) * 80  # rough estimate
            actual_ms = ms_e - ms_s
            dur_ratio = min(expected_ms, actual_ms) / max(expected_ms, actual_ms, 1)
            score *= (0.7 + 0.3 * dur_ratio)

            if score > best_score:
                best_score = score
                best_word = word

    decoded_words.append((best_word, best_score))

    expected = expected_words[si] if si < len(expected_words) else "?"
    match = "✓" if best_word == expected else " "
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} ({best_score:.3f}) {match}  "
          f"expected={expected:12s}  "
          f"top_vowel={top_vowel}  vowel_dedup={vowel_dedup[:5]}")

# Summary
decoded_text = " ".join(w for w, s in decoded_words)
exact = sum(1 for i, (w, _) in enumerate(decoded_words)
            if i < len(expected_words) and w == expected_words[i])
in_vocab = sum(1 for w, _ in decoded_words if w in set(expected_words))

print(f"\nDECODED:   {decoded_text}")
print(f"EXPECTED:  {EXPECTED}")
print(f"\nExact position: {exact}/{min(len(decoded_words), len(expected_words))}")
print(f"In expected:    {in_vocab}/{len(decoded_words)}")
