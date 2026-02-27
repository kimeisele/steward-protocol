"""
EXPERIMENT 20: Trace what score_frame() actually does per frame
================================================================

The decoder uses _frames_to_phoneme_coords() which calls score_frame()
with f1/f2 formants (NOT mfcc). The formant path in score_frame() uses:
  voicing(0.15) + varga(0.15) + sound_class(0.15) + centroid(0.15) + formant(0.40)

Let's trace: for each frame in a segment, what phoneme wins and WHY?
Also: are formants actually being extracted?
"""
import sys; sys.path.insert(0, ".")
import numpy as np

from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaIntake, unpack_frame, extract_formants,
)
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, score_frame, _frames_to_phoneme_coords,
    _stable_coords, _dedup_coords, get_pronunciation_dict,
    ARPABET_TO_RAMA,
)

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

EXPECTED = ["eh", "not", "exactly", "but", "i", "came", "to", "preach"]

# Part 1: Check formant extraction success rate
print("=" * 70)
print("PART 1: Formant extraction success rate per segment")
print("=" * 70)

hop = int(stream.sample_rate * 10 / 1000)
n_fft = stream.n_fft

for si in range(min(8, len(segments))):
    seg = segments[si]
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    f1_ok = 0
    f2_ok = 0
    total = 0
    for i, frame in enumerate(seg.frames):
        rms = frame & 0xFF
        if rms < 15:
            continue
        total += 1

        start_sample = (seg.start + i) * hop
        end_sample = start_sample + n_fft
        if stream.raw_samples is not None and end_sample <= len(stream.raw_samples):
            f1, f2 = extract_formants(stream.raw_samples[start_sample:end_sample], stream.sample_rate)
            if f1 > 0:
                f1_ok += 1
            if f2 > 0:
                f2_ok += 1

    expected = EXPECTED[si] if si < len(EXPECTED) else "?"
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] ({expected:10s}) "
          f"voiced={total:3d}  f1_ok={f1_ok:3d}({f1_ok*100//max(1,total):2d}%)  "
          f"f2_ok={f2_ok:3d}({f2_ok*100//max(1,total):2d}%)")

# Part 2: Frame-by-frame score_frame trace for segment 3 ("but")
print()
print("=" * 70)
print("PART 2: score_frame() trace for segment 3 ('but' expected)")
print("=" * 70)

seg = segments[3]
for i, frame in enumerate(seg.frames[:15]):
    rms, varga, f0_x10, cent = unpack_frame(frame)
    if rms < 15:
        continue

    start_sample = (seg.start + i) * hop
    end_sample = start_sample + n_fft
    f1, f2 = 0, 0
    if stream.raw_samples is not None and end_sample <= len(stream.raw_samples):
        f1, f2 = extract_formants(stream.raw_samples[start_sample:end_sample], stream.sample_rate)

    candidates = score_frame(frame, f1=f1, f2=f2)
    top3 = candidates[:3] if candidates else []
    top3_str = ", ".join(f"{p}:{s:.3f}" for p, s in top3)

    print(f"  f{i:2d}: rms={rms:3d} vg={varga} f0={f0_x10:4d} cent={cent:3d} "
          f"f1={f1:4d} f2={f2:4d} → {top3_str}")

# Part 3: Full _frames_to_phoneme_coords output for first 8 segments
print()
print("=" * 70)
print("PART 3: _frames_to_phoneme_coords output vs dict coords")
print("=" * 70)

pdict = get_pronunciation_dict()
pdict._ensure_loaded()

for si in range(min(8, len(segments))):
    seg = segments[si]
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    seg_raw = None
    if stream.raw_samples is not None:
        start_sample = seg.start * hop
        end_sample = (seg.end + 1) * hop + n_fft
        if end_sample <= len(stream.raw_samples):
            seg_raw = stream.raw_samples[start_sample:end_sample]

    raw_coords = _frames_to_phoneme_coords(
        seg.frames, seg_raw, stream.sample_rate, 10, n_fft,
    )
    stable = _stable_coords(raw_coords, min_run=3)

    expected = EXPECTED[si] if si < len(EXPECTED) else "?"
    dict_c = pdict.lookup(expected) if expected != "?" else ()

    # Show ARPAbet sequence before RAMA conversion
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] ({expected:10s})")
    print(f"    raw_coords({len(raw_coords)}): {raw_coords[:12]}")
    print(f"    stable:          {stable[:8]}")
    print(f"    dict:            {dict_c}")
