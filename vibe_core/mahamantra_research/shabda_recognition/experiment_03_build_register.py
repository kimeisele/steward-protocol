"""
EXPERIMENT 3: Build MFCC phoneme register from real audio
==========================================================

We know the transcript of prabhupada-talk.wav:
  "Eh... not exactly. But I came to preach the... um... gospel
   of Krishna consciousness, and fortunately I met some
   enthusiastic young boys and girls."

We also know the segment timings from the decoder output.
Using CMU dict we know the phonemes in each word.

Strategy:
- For each segment where we're CONFIDENT of the word, extract MFCCs
- Divide the segment evenly among the word's phonemes
- Average the MFCCs per phoneme across all occurrences
- This gives us a real MFCC register from real speech

This is NOT a perfect forced alignment, but it's a reasonable
first approximation for building the register.
"""
import sys; sys.path.insert(0, ".")
import json
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, extract_mfcc

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
samples = stream.raw_samples
sr = stream.sample_rate
hop = int(sr * stream.hop_ms / 1000)
n_fft = stream.n_fft

# Load CMU dict
import nltk
cmu = nltk.corpus.cmudict.dict()

def get_phonemes(word):
    """Get ARPAbet phonemes for a word (strip stress digits)."""
    prons = cmu.get(word.lower())
    if not prons:
        return None
    return [''.join(c for c in p if not c.isdigit()) for p in prons[0]]

# Manual alignment: (start_ms, end_ms, word)
# Based on segment timings + known transcript
# Only include words we're CONFIDENT about
ALIGNMENT = [
    # "Eh... not exactly"
    (180, 560, "eh"),       # segment 0 - filler
    (970, 1110, "not"),     # roughly
    (1110, 1360, "exactly"),
    # "But I came to preach"
    (1470, 1600, "but"),
    (1600, 1680, "i"),
    (1680, 1780, "came"),
    (1940, 2100, "to"),
    (2100, 2300, "preach"),
    (2350, 2500, "the"),
    # "um... gospel of Krishna consciousness"
    (2670, 2780, "um"),
    (2900, 3200, "gospel"),
    (3230, 3350, "of"),
    # Long gap, then...
    (5890, 6050, "and"),
    (6290, 6460, "fortunately"),  # partial
    (8310, 8500, "some"),
    (8770, 8930, "enthusiastic"),  # partial
    (11090, 11260, "young"),
    (11280, 11500, "boys"),
    (11720, 11900, "and"),
    (11900, 12080, "girls"),
]

# Collect MFCCs per phoneme
phoneme_mfccs: Dict[str, List[np.ndarray]] = defaultdict(list)

for start_ms, end_ms, word in ALIGNMENT:
    phonemes = get_phonemes(word)
    if not phonemes:
        # Handle "eh" and "um" manually
        if word == "eh":
            phonemes = ["EH"]
        elif word == "um":
            phonemes = ["AH", "M"]
        else:
            print(f"  SKIP: '{word}' not in CMU dict")
            continue

    # Convert ms to frame indices
    start_frame = start_ms // 10
    end_frame = end_ms // 10
    n_frames = end_frame - start_frame

    if n_frames < len(phonemes):
        continue  # too short to split

    # Evenly distribute frames among phonemes
    frames_per_phoneme = n_frames / len(phonemes)

    for pi, phoneme in enumerate(phonemes):
        pstart = int(start_frame + pi * frames_per_phoneme)
        pend = int(start_frame + (pi + 1) * frames_per_phoneme)

        # Extract MFCCs from each frame in this phoneme's region
        for fi in range(pstart, pend):
            sample_start = fi * hop
            sample_end = sample_start + n_fft
            if sample_end > len(samples):
                continue
            audio_frame = samples[sample_start:sample_end]
            mfcc = extract_mfcc(audio_frame, sr, n_fft)
            if any(c != 0 for c in mfcc):
                phoneme_mfccs[phoneme].append(np.array(mfcc, dtype=float))

# Average MFCCs per phoneme
register: Dict[str, Tuple[int, ...]] = {}
print(f"\nMFCC PHONEME REGISTER ({len(phoneme_mfccs)} phonemes):")
print(f"{'PHONEME':8s} {'COUNT':6s} {'MFCC[1:5]':30s}")
print("-" * 50)

for phoneme in sorted(phoneme_mfccs.keys()):
    vectors = phoneme_mfccs[phoneme]
    if len(vectors) < 2:
        print(f"  {phoneme:8s} {len(vectors):4d}   SKIP (too few samples)")
        continue

    mean = np.mean(vectors, axis=0)
    # Quantize to int (already ×100 from extract_mfcc)
    prototype = tuple(int(round(v)) for v in mean)
    register[phoneme] = prototype

    # Show first few coefficients
    print(f"  {phoneme:8s} {len(vectors):4d}   {prototype[1:5]}")

print(f"\nTotal phonemes with prototypes: {len(register)}")

# Save register as JSON
output_path = "vibe_core/mahamantra_research/shabda_recognition/mfcc_register.json"
# Convert to JSON-serializable format
json_register = {k: list(v) for k, v in register.items()}
with open(output_path, "w") as f:
    json.dump(json_register, f, indent=2)
print(f"Saved to: {output_path}")

# Also show which ARPAbet phonemes we're MISSING
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import ARPABET_TO_RAMA
all_arpabet = set(ARPABET_TO_RAMA.keys())
covered = set(register.keys())
missing = all_arpabet - covered
print(f"\nCovered: {len(covered)}/{len(all_arpabet)} ARPAbet phonemes")
print(f"Missing: {sorted(missing)}")
