"""
EXPERIMENT 21: Extract REAL formant values from Prabhupada's japa
==================================================================

We have labeled japa audio (shabda_bridge.json gives syllable boundaries).
Extract F1/F2 from each syllable to get speaker-specific formant templates.

Compare with the textbook _VOWEL_FORMANTS (Peterson & Barney, American English).
If they differ significantly, that's why the decoder fails.

Mahamantra syllables and their vowels:
  ha  → vowel: /a/  (open central)
  re  → vowel: /e/  (mid front)
  kṛ  → vowel: /ɹ̩/ (syllabic r)
  ṣṇa → vowel: /a/  (open central)
  rā  → vowel: /aː/ (long open)
  ma  → vowel: /a/  (open central)
"""
import sys; sys.path.insert(0, ".")
import json
import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake, unpack_frame, extract_formants,
)

# Load japa audio
intake = ShabdaIntake()
stream = intake.process_file("temp/srila prabhupada japa clip.wav")
print(f"Japa audio: {stream.duration_ms}ms, {len(stream.frames)} frames, sr={stream.sample_rate}")

# Load bridge data for syllable positions
with open("vibe_core/mahamantra/data/shabda_bridge.json") as f:
    bridge = json.load(f)

meta = bridge["meta"]
chant_start = meta["chant_start_frame"]
chant_end = meta["chant_end_frame"]
n_syllables = 32

SYLLABLES = (
    "ha", "re", "kṛ", "ṣṇa", "ha", "re", "kṛ", "ṣṇa",
    "kṛ", "ṣṇa", "kṛ", "ṣṇa", "ha", "re", "ha", "re",
    "ha", "re", "rā", "ma", "ha", "re", "rā", "ma",
    "rā", "ma", "rā", "ma", "ha", "re", "ha", "re",
)

chant_range = chant_end - chant_start
frames_per_syllable = chant_range // n_syllables

print(f"Chant: frames {chant_start}-{chant_end} ({chant_range} frames)")
print(f"Frames per syllable: ~{frames_per_syllable}")

# Extract formants per syllable
hop = int(stream.sample_rate * 10 / 1000)
n_fft = stream.n_fft

# Collect formants per unique syllable
from collections import defaultdict
syllable_formants = defaultdict(list)  # syllable → [(f1, f2), ...]

print()
print("=" * 70)
print("Per-syllable formant extraction")
print("=" * 70)

for pos in range(n_syllables):
    syl = SYLLABLES[pos]
    frame_start = chant_start + (pos * chant_range) // n_syllables
    frame_end = chant_start + ((pos + 1) * chant_range) // n_syllables

    f1_vals = []
    f2_vals = []

    for fi in range(frame_start, min(frame_end, len(stream.frames))):
        rms = stream.frames[fi] & 0xFF
        if rms < 20:
            continue

        sample_start = fi * hop
        sample_end = sample_start + n_fft
        if stream.raw_samples is not None and sample_end <= len(stream.raw_samples):
            f1, f2 = extract_formants(stream.raw_samples[sample_start:sample_end], stream.sample_rate)
            if f1 > 0 and f2 > 0:
                f1_vals.append(f1)
                f2_vals.append(f2)

    if f1_vals:
        avg_f1 = int(np.mean(f1_vals))
        avg_f2 = int(np.mean(f2_vals))
        syllable_formants[syl].append((avg_f1, avg_f2))
        print(f"  pos={pos:2d} '{syl:4s}' frames={frame_end-frame_start:3d} "
              f"voiced={len(f1_vals):3d}  F1={avg_f1:4d}  F2={avg_f2:4d}")

# Aggregate per unique syllable
print()
print("=" * 70)
print("Averaged formants per syllable (Prabhupada's voice)")
print("=" * 70)

TEXTBOOK = {
    "ha":  ("AH/AA", 520, 1200),  # /a/ → AH in ARPABET
    "re":  ("EH/EY", 530, 1850),  # /e/ → EH
    "kṛ":  ("ER",    490, 1350),  # /ṛ/ → ER
    "ṣṇa": ("AH/AA", 520, 1200),  # /a/ → AH
    "rā":  ("AA",    750, 1200),  # /aː/ → AA
    "ma":  ("AH/AA", 520, 1200),  # /a/ → AH
}

for syl, formant_list in sorted(syllable_formants.items()):
    all_f1 = [f[0] for f in formant_list]
    all_f2 = [f[1] for f in formant_list]
    avg_f1 = int(np.mean(all_f1))
    avg_f2 = int(np.mean(all_f2))
    n = len(formant_list)

    textbook_name, tb_f1, tb_f2 = TEXTBOOK.get(syl, ("?", 0, 0))
    f1_diff = avg_f1 - tb_f1
    f2_diff = avg_f2 - tb_f2

    print(f"  '{syl:4s}' (n={n:2d})  F1={avg_f1:4d}  F2={avg_f2:4d}  "
          f"| textbook({textbook_name}): F1={tb_f1:4d}  F2={tb_f2:4d}  "
          f"| diff: F1={f1_diff:+4d}  F2={f2_diff:+4d}")

# Also: what formants does the TALK audio produce?
print()
print("=" * 70)
print("Talk audio: formant values for first 8 segments")
print("=" * 70)

talk_stream = intake.process_file("temp/prabhupada-talk.wav")
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
segments = segment_stream(talk_stream.frames)

EXPECTED = ["eh", "not", "exactly", "but", "i", "came", "to", "preach"]
VOWEL_MAP = {
    "eh": "EH", "not": "AH", "exactly": "EH", "but": "AH",
    "i": "AY", "came": "EY", "to": "UW", "preach": "IY",
}

hop2 = int(talk_stream.sample_rate * 10 / 1000)
for si in range(min(8, len(segments))):
    seg = segments[si]
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    f1_vals = []
    f2_vals = []
    for fi in range(len(seg.frames)):
        rms = seg.frames[fi] & 0xFF
        if rms < 40:  # higher threshold for talk
            continue
        sample_start = (seg.start + fi) * hop2
        sample_end = sample_start + talk_stream.n_fft
        if talk_stream.raw_samples is not None and sample_end <= len(talk_stream.raw_samples):
            f1, f2 = extract_formants(talk_stream.raw_samples[sample_start:sample_end], talk_stream.sample_rate)
            if f1 > 0 and f2 > 0:
                f1_vals.append(f1)
                f2_vals.append(f2)

    if f1_vals:
        avg_f1 = int(np.mean(f1_vals))
        avg_f2 = int(np.mean(f2_vals))
        expected = EXPECTED[si] if si < len(EXPECTED) else "?"
        expected_vowel = VOWEL_MAP.get(expected, "?")
        tb_f1, tb_f2 = dict(
            AH=(520, 1200), EH=(530, 1850), EY=(400, 2200),
            IY=(280, 2300), AY=(700, 1200), UW=(300, 900),
            AA=(750, 1200),
        ).get(expected_vowel, (0, 0))

        print(f"  [{ms_s:5d}-{ms_e:5d}ms] ({expected:10s})  "
              f"F1={avg_f1:4d}  F2={avg_f2:4d}  "
              f"| expected {expected_vowel}: F1={tb_f1:4d} F2={tb_f2:4d}  "
              f"| diff: F1={avg_f1-tb_f1:+4d} F2={avg_f2-tb_f2:+4d}")
