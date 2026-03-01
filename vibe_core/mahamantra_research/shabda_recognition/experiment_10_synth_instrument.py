"""
EXPERIMENT 10: Play audio through the MahaModularSynth
=======================================================

The synth is an INSTRUMENT. We feed audio features through it and
see what attractors they converge to.

Key idea: Same audio → different presets → different attractor patterns.
Like tuning a radio to different frequencies to extract different streams.

For each audio segment:
  1. Get VibrationSignatures (articulation, voicing, freq, duration)
  2. Feed signature_id through synth at each preset
  3. Collect attractor pattern = fingerprint of the sound
  4. Compare fingerprint against known word fingerprints

For each dictionary word:
  1. text_to_vibration() → VibrationSignatures
  2. Same synth → attractor pattern = fingerprint
  3. Match by fingerprint similarity
"""

import sys

sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_vibration import stream_to_vibrations
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MahaModularSynth,
    SYNTH_PRESETS,
    MahaSynthParams,
)
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    text_to_vibration,
    VibrationSignature,
)
from typing import List, Tuple, Sequence
import math

# The instrument
synth = MahaModularSynth(default_preset="quantum")

PRESETS_TO_USE = ["quantum", "classical", "pancha", "nava", "wide"]


def vibration_fingerprint(sigs: Sequence[VibrationSignature]) -> Tuple[Tuple[int, ...], ...]:
    """Play VibrationSignatures through the synth at multiple presets.

    Returns: tuple of attractor tuples, one per preset.
    Each attractor tuple has one attractor per phoneme-signature.
    """
    fingerprints = []
    for preset_name in PRESETS_TO_USE:
        attractors = []
        for sig in sigs:
            seed = sig.signature_id
            transformed = synth.transform(seed, preset=preset_name)
            attractors.append(transformed)
        fingerprints.append(tuple(attractors))
    return tuple(fingerprints)


def fingerprint_distance(fp_a: Tuple[Tuple[int, ...], ...], fp_b: Tuple[Tuple[int, ...], ...]) -> float:
    """Compare two multi-preset fingerprints. Lower = more similar."""
    if not fp_a or not fp_b:
        return 1.0

    total_dist = 0.0
    count = 0

    for preset_a, preset_b in zip(fp_a, fp_b):
        # Compare attractor sequences via histogram overlap
        if not preset_a or not preset_b:
            continue

        # Histogram of attractors
        hist_a = {}
        for a in preset_a:
            hist_a[a] = hist_a.get(a, 0) + 1
        hist_b = {}
        for b in preset_b:
            hist_b[b] = hist_b.get(b, 0) + 1

        # Normalize
        total_a = len(preset_a) or 1
        total_b = len(preset_b) or 1

        all_keys = set(hist_a) | set(hist_b)
        dist = sum(abs(hist_a.get(k, 0) / total_a - hist_b.get(k, 0) / total_b) for k in all_keys)
        total_dist += dist / 2.0  # normalize to [0, 1]
        count += 1

    return total_dist / count if count else 1.0


# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

# === Part 1: What do audio fingerprints look like? ===
print("=" * 70)
print("PART 1: Audio segment fingerprints through the synth")
print("=" * 70)

for si, seg in enumerate(segments[:5]):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    vibs = stream_to_vibrations(seg.frames)
    if not vibs:
        continue

    fp = vibration_fingerprint(vibs)
    print(f"\n[{si}] {ms_s}-{ms_e}ms  ({len(vibs)} phonemes)")
    for pi, preset_name in enumerate(PRESETS_TO_USE):
        print(f"  {preset_name:10s}: attractors={fp[pi][:8]}")

# === Part 2: What do TEXT fingerprints look like? ===
print()
print("=" * 70)
print("PART 2: Text word fingerprints through the synth")
print("=" * 70)

WORDS = [
    "the",
    "and",
    "not",
    "but",
    "came",
    "preach",
    "gospel",
    "krishna",
    "consciousness",
    "boys",
    "girls",
    "some",
    "exactly",
]

word_fingerprints = {}
for word in WORDS:
    text_vibs = text_to_vibration(word)
    if not text_vibs:
        continue
    fp = vibration_fingerprint(text_vibs)
    word_fingerprints[word] = fp
    print(f"\n  '{word}' ({len(text_vibs)} phonemes):")
    for pi, preset_name in enumerate(PRESETS_TO_USE):
        print(f"    {preset_name:10s}: {fp[pi][:8]}")

# === Part 3: Match audio segments against word fingerprints ===
print()
print("=" * 70)
print("PART 3: Matching audio fingerprints to word fingerprints")
print("=" * 70)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

words_out = []
for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    vibs = stream_to_vibrations(seg.frames)
    if not vibs:
        continue

    audio_fp = vibration_fingerprint(vibs)

    best_word = ""
    best_dist = float("inf")
    for word, word_fp in word_fingerprints.items():
        dist = fingerprint_distance(audio_fp, word_fp)
        if dist < best_dist:
            best_dist = dist
            best_word = word

    conf = max(0.0, 1.0 - best_dist)
    if conf >= 0.2:
        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:20s} conf={conf:.3f}")
        words_out.append(best_word)

correct = sum(1 for w in words_out if w.lower() in expected_words)
print(f"\nSYNTH TRANSCRIPT: {' '.join(words_out)}")
print(f"Correct: {correct}/{len(words_out)} ({correct / max(1, len(words_out)) * 100:.0f}%)")

# === Part 4: Cross-word fingerprint distances ===
print()
print("=" * 70)
print("PART 4: Inter-word distances (discrimination power)")
print("=" * 70)
print(f"{'':15s}", end="")
for w2 in WORDS[:8]:
    print(f"  {w2:>8s}", end="")
print()
for w1 in WORDS[:8]:
    print(f"{w1:15s}", end="")
    for w2 in WORDS[:8]:
        if w1 in word_fingerprints and w2 in word_fingerprints:
            d = fingerprint_distance(word_fingerprints[w1], word_fingerprints[w2])
            print(f"  {d:8.3f}", end="")
        else:
            print(f"  {'N/A':>8s}", end="")
    print()
