"""
EXPERIMENT 11: Synth parameter sweep — many frequencies from one instrument
============================================================================

Experiment 10 showed: quantum preset gives meaningful attractor patterns.
But 5 presets isn't enough for a full dictionary.

The synth has adjustable parameters. Each combination is a different
radio frequency. We sweep across:
  - mod_space: 137, 37, 49, 17, 512  (different resolution)
  - feedback: 0, 1, 3, 5            (different coupling)
  - phase_offset: 0, 4, 8           (different alignment)

This gives 5 × 4 × 3 = 60 "frequencies" per phoneme.
The attractor histogram across all frequencies = high-dimensional fingerprint.

THEN: compare fingerprints using existing infrastructure (cosine similarity).
"""

import sys

sys.path.insert(0, ".")
import math
from typing import Dict, List, Sequence, Tuple

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_vibration import stream_to_vibrations
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MahaModularSynth,
    MahaSynthParams,
)
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    text_to_vibration,
    VibrationSignature,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PANCHA,
    NAVA,
    QUARTERS,
    SEVEN,
    WORDS,
)

synth = MahaModularSynth(default_preset="quantum")

# Parameter sweep: different "frequencies"
SWEEP_PARAMS: List[MahaSynthParams] = []
for mod in [MAHA_QUANTUM, 37, 49, 17, 512]:
    for fb in [0, 1, 3, 5]:
        for offset in [0, 4, 8]:
            SWEEP_PARAMS.append(
                MahaSynthParams(
                    mod_space=mod,
                    feedback=fb,
                    phase_offset=offset,
                )
            )

N_FREQS = len(SWEEP_PARAMS)
print(f"Sweep: {N_FREQS} frequency combinations")


def multi_freq_fingerprint(sigs: Sequence[VibrationSignature]) -> Tuple[float, ...]:
    """Play phonemes through all frequency combinations.

    Returns: histogram of attractors across all frequencies.
    Bin count = largest mod_space (512) → 512-dim vector.
    """
    BINS = 512
    hist = [0.0] * BINS

    for sig in sigs:
        seed = sig.signature_id
        for params in SWEEP_PARAMS:
            attractor = synth.transform(seed, params=params)
            hist[attractor % BINS] += 1.0

    # Normalize
    total = sum(hist)
    if total > 0:
        hist = [h / total for h in hist]

    return tuple(hist)


def cosine_sim(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    """Cosine similarity between two histograms."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return dot / (na * nb)


# Build word fingerprints
VOCAB = [
    "the",
    "and",
    "not",
    "but",
    "i",
    "came",
    "to",
    "preach",
    "gospel",
    "of",
    "krishna",
    "consciousness",
    "fortunately",
    "met",
    "some",
    "enthusiastic",
    "young",
    "boys",
    "girls",
    "eh",
    "exactly",
]

print(f"\nBuilding fingerprints for {len(VOCAB)} words...")
word_fps: Dict[str, Tuple[float, ...]] = {}
for word in VOCAB:
    text_vibs = text_to_vibration(word)
    if text_vibs:
        word_fps[word] = multi_freq_fingerprint(text_vibs)
print("Done.")

# Cross-word discrimination
print(f"\n{'':15s}", end="")
for w in VOCAB[:10]:
    print(f" {w:>7s}", end="")
print()
for w1 in VOCAB[:10]:
    print(f"{w1:15s}", end="")
    for w2 in VOCAB[:10]:
        sim = cosine_sim(word_fps[w1], word_fps[w2])
        print(f" {sim:7.3f}", end="")
    print()

# Audio matching
print()
print("=" * 70)
print("AUDIO MATCHING")
print("=" * 70)

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

words_out = []
for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    vibs = stream_to_vibrations(seg.frames)
    if not vibs:
        continue

    audio_fp = multi_freq_fingerprint(vibs)

    best_word = ""
    best_sim = -1.0
    for word, word_fp in word_fps.items():
        sim = cosine_sim(audio_fp, word_fp)
        if sim > best_sim:
            best_sim = sim
            best_word = word

    if best_sim >= 0.3:
        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:20s} sim={best_sim:.3f}")
        words_out.append(best_word)

correct = sum(1 for w in words_out if w.lower() in expected_words)
print(f"\nTRANSCRIPT: {' '.join(words_out)}")
print(f"EXPECTED:   {EXPECTED}")
print(f"\nCorrect: {correct}/{len(words_out)} ({correct / max(1, len(words_out)) * 100:.0f}%)")
