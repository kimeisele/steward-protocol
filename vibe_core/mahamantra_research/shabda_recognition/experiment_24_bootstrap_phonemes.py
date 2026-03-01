"""
EXPERIMENT 24: Bootstrap Phoneme MFCC Profiles from Real Audio
================================================================

Problem: Synthetic MFCC templates (Gaussian spectra) don't match real audio MFCCs.
Solution: Use KNOWN transcript + CMU dict to force-align phonemes to audio frames,
          then extract REAL MFCC averages per ARPAbet phoneme.

Steps:
  1. We know the transcript: "Eh not exactly but I came to preach..."
  2. We know the segment boundaries from segment_stream()
  3. We align words to segments by order
  4. For each word, CMU dict gives phoneme sequence (e.g. "but" → B AH1 T)
  5. We distribute the segment's frames proportionally across phonemes
     (stops get 1-2 frames, vowels get the rest)
  6. We collect all frames labeled as each phoneme and average their MFCCs

Output: A dictionary of ARPAbet → average MFCC vector (13 floats) + duration stats.
This becomes the REAL phoneme profile for DTW template generation.
"""

import sys

sys.path.insert(0, ".")
import json
from collections import defaultdict

import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, extract_mfcc
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

# Load CMU dict
from nltk.corpus import cmudict

cmu = cmudict.dict()

hop = int(stream.sample_rate * 10 / 1000)

# Known transcript aligned to segments (manual alignment by position)
# From experiment output, we know the segment count and boundaries.
# The first ~23 segments correspond to these words:
TRANSCRIPT_WORDS = [
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

print(f"Segments: {len(segments)}, Transcript words: {len(TRANSCRIPT_WORDS)}")
print()

# Get CMU pronunciations for each word
word_phones = {}
for w in TRANSCRIPT_WORDS:
    prons = cmu.get(w)
    if prons:
        word_phones[w] = [p.rstrip("012") for p in prons[0]]
    else:
        # Fallback for words not in CMU dict
        if w == "eh":
            word_phones[w] = ["EH"]
        elif w == "krishna":
            word_phones[w] = ["K", "R", "IH", "SH", "N", "AH"]
        else:
            print(f"  WARNING: '{w}' not in CMU dict, skipping")

print("Word → Phonemes:")
for w in TRANSCRIPT_WORDS:
    if w in word_phones:
        print(f"  {w:15s} → {' '.join(word_phones[w])}")
print()

# Phoneme duration model (in relative units)
# Vowels are longer, stops are shorter
PHONEME_DURATION_WEIGHT = {
    # Stops: very short (burst only)
    "B": 1,
    "D": 1,
    "G": 1,
    "P": 1,
    "T": 1,
    "K": 1,
    # Affricates
    "CH": 2,
    "JH": 2,
    # Fricatives: medium
    "F": 2,
    "V": 2,
    "TH": 2,
    "DH": 2,
    "S": 3,
    "Z": 2,
    "SH": 3,
    "ZH": 2,
    "HH": 1,
    # Nasals: medium
    "M": 2,
    "N": 2,
    "NG": 2,
    # Liquids/Glides: medium
    "L": 2,
    "R": 2,
    "W": 2,
    "Y": 2,
    # Vowels: long
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

# Collect per-phoneme MFCC frames
phoneme_mfccs = defaultdict(list)  # ARPAbet → list of MFCC vectors (13 floats)
phoneme_frame_counts = defaultdict(int)

n_aligned = min(len(segments), len(TRANSCRIPT_WORDS))

for si in range(n_aligned):
    seg = segments[si]
    word = TRANSCRIPT_WORDS[si]

    if word not in word_phones:
        continue

    phones = word_phones[word]
    n_frames = len(seg.frames)

    if n_frames < 2 or not phones:
        continue

    # Compute proportional frame allocation per phoneme
    weights = [PHONEME_DURATION_WEIGHT.get(p, 3) for p in phones]
    total_weight = sum(weights)

    # Allocate frames proportionally, minimum 1 per phoneme
    frame_alloc = []
    remaining = n_frames
    for i, w in enumerate(weights):
        if i == len(weights) - 1:
            alloc = remaining  # last phoneme gets whatever's left
        else:
            alloc = max(1, round(n_frames * w / total_weight))
            alloc = min(alloc, remaining - (len(weights) - i - 1))  # leave at least 1 for each remaining
        frame_alloc.append(alloc)
        remaining -= alloc

    # Extract MFCCs and assign to phonemes
    frame_idx = 0
    for pi, phone in enumerate(phones):
        n_phone_frames = frame_alloc[pi]

        for fi in range(n_phone_frames):
            abs_frame = frame_idx + fi
            if abs_frame >= n_frames:
                break

            # Get MFCC from pre-computed stream data
            abs_stream_idx = seg.start + abs_frame
            mfcc_vec = None

            if stream.mfcc_frames and abs_stream_idx < len(stream.mfcc_frames):
                mfcc_ints = stream.mfcc_frames[abs_stream_idx]
                if any(c != 0 for c in mfcc_ints):
                    mfcc_vec = np.array([c / 100.0 for c in mfcc_ints])

            # Fallback: extract from raw audio
            if mfcc_vec is None and stream.raw_samples is not None:
                start_sample = abs_stream_idx * hop
                end_sample = start_sample + stream.n_fft
                if end_sample <= len(stream.raw_samples):
                    audio_frame = stream.raw_samples[start_sample:end_sample]
                    mfcc_ints = extract_mfcc(audio_frame, stream.sample_rate, stream.n_fft)
                    if any(c != 0 for c in mfcc_ints):
                        mfcc_vec = np.array([c / 100.0 for c in mfcc_ints])

            if mfcc_vec is not None:
                phoneme_mfccs[phone].append(mfcc_vec)
                phoneme_frame_counts[phone] += 1

        frame_idx += n_phone_frames

# Compute average MFCC per phoneme
print("=" * 70)
print("PHONEME MFCC PROFILES (bootstrapped from real audio)")
print("=" * 70)

phoneme_profiles = {}  # ARPAbet → (mean_mfcc, std_mfcc, n_frames)

for phone in sorted(phoneme_mfccs.keys()):
    vecs = np.array(phoneme_mfccs[phone])
    mean = vecs.mean(axis=0)
    std = vecs.std(axis=0)
    n = len(vecs)
    phoneme_profiles[phone] = (mean, std, n)

    is_vowel = (
        phone in PHONEME_DURATION_WEIGHT and PHONEME_DURATION_WEIGHT.get(phone, 0) >= 3 and phone not in ("S", "SH")
    )
    vtype = "VOWEL" if is_vowel else "CONS "
    print(
        f"  {phone:3s} ({vtype}) n={n:3d}  mean_c0={mean[0]:6.2f}  std_c0={std[0]:5.2f}  "
        f"mean_c1={mean[1]:6.2f}  mean_c2={mean[2]:6.2f}"
    )

print()
print(f"Total phonemes profiled: {len(phoneme_profiles)}")
print(f"Total frames used: {sum(phoneme_frame_counts.values())}")

# Now test: build word templates from REAL profiles and DTW-match
print()
print("=" * 70)
print("DTW TEST WITH REAL PROFILES")
print("=" * 70)

from vibe_core.mahamantra.sound.shabda_dtw import (
    dtw_score,
    segment_to_mfcc_matrix,
    _silence_mfcc,
    extract_vowel_anchor_formants,
    filter_candidates_by_vowel,
    _VOWEL_PARAMS,
)
from vibe_core.mahamantra.sound.shabda_decoder import _COMMON_ENGLISH


def real_word_template(phones_list):
    """Build word MFCC template from REAL bootstrapped profiles."""
    frames = []
    for phone in phones_list:
        clean = phone.rstrip("012")
        if clean in phoneme_profiles:
            mean_mfcc, _, n = phoneme_profiles[clean]
            # Duration: use the proportional model
            dur = PHONEME_DURATION_WEIGHT.get(clean, 2)
            for _ in range(dur):
                frames.append(mean_mfcc)
        else:
            # Unknown phoneme: use silence
            frames.append(_silence_mfcc())
    if not frames:
        frames.append(_silence_mfcc())
    return np.array(frames)


# Build vocab + templates
vocab_words = set(_COMMON_ENGLISH)
vocab_words.update(TRANSCRIPT_WORDS)

word_phones_all = {}
for w in vocab_words:
    prons = cmu.get(w)
    if prons:
        word_phones_all[w] = [p.rstrip("012") for p in prons[0]]
    elif w == "eh":
        word_phones_all[w] = ["EH"]
    elif w == "krishna":
        word_phones_all[w] = ["K", "R", "IH", "SH", "N", "AH"]

# Pre-compute real templates
word_templates = {}
for w, phones in word_phones_all.items():
    word_templates[w] = real_word_template(phones)

print(f"Vocab: {len(word_templates)} words with real-profile templates")
print()

# Decode
decoded_words = []
EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = EXPECTED.lower().split()

for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    expected = expected_words[si] if si < len(expected_words) else "?"

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

    # Vowel anchor filter
    anchor = extract_vowel_anchor_formants(
        seg.frames,
        stream.raw_samples,
        stream.sample_rate,
        seg.start,
        hop,
        stream.n_fft,
    )

    if anchor:
        filtered = filter_candidates_by_vowel(
            anchor,
            [(w, phones) for w, phones in word_phones_all.items()],
        )
        candidate_words = [w for w, _ in filtered]
    else:
        candidate_words = list(word_phones_all.keys())

    # Duration filter
    seg_frames = len(seg.frames)
    duration_filtered = []
    for w in candidate_words:
        tmpl = word_templates.get(w)
        if tmpl is None:
            continue
        ratio = len(tmpl) / max(seg_frames, 1)
        if 0.15 < ratio < 4.0:
            duration_filtered.append(w)
    if duration_filtered:
        candidate_words = duration_filtered

    # DTW scoring
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

    decoded_words.append(best_word)
    scores_debug.sort(key=lambda x: -x[1])
    top3 = scores_debug[:3]
    top3_str = ", ".join(f"{w}:{s:.3f}" for w, s in top3)

    match = "✓" if best_word == expected else " "
    print(
        f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} ({best_score:.3f}) {match}  "
        f"exp={expected:15s}  anchor={anchor or '?':3s}  [{top3_str}]"
    )

# Summary
decoded_text = " ".join(decoded_words)
exact = sum(1 for i, w in enumerate(decoded_words) if i < len(expected_words) and w == expected_words[i])
in_expected = sum(1 for w in decoded_words if w in set(expected_words))

print(f"\nDECODED:   {decoded_text}")
print(f"EXPECTED:  {EXPECTED}")
print(f"\nExact position: {exact}/{min(len(decoded_words), len(expected_words))}")
print(f"In expected:    {in_expected}/{len(decoded_words)}")

# Save profiles for reuse
profile_data = {}
for phone, (mean, std, n) in phoneme_profiles.items():
    profile_data[phone] = {
        "mean": mean.tolist(),
        "std": std.tolist(),
        "n_frames": n,
    }

out_path = "vibe_core/mahamantra/data/phoneme_mfcc_profiles.json"
with open(out_path, "w") as f:
    json.dump(profile_data, f, indent=2)
print(f"\nProfiles saved to {out_path}")
