"""
EXPERIMENT 31: Segment Quality Analysis
=========================================

Before ANY feature engineering can work, the SEGMENTS must be correct.
If "and" at position 13 contains audio from "consciousness+and" and
"and" at position 21 contains audio from "boys+and", then NO feature
space will make them match.

This experiment:
1. Shows segment boundaries, lengths, and energy profiles
2. Visualizes what each segment actually sounds like (energy + spectral content)
3. Checks if segments align with word boundaries at all
"""

import sys

sys.path.insert(0, ".")

import numpy as np
from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from vibe_core.mahamantra.sound.shabda_intake import unpack_frame

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
hop = int(stream.sample_rate * 10 / 1000)

TRANSCRIPT = [
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

n_seg = min(len(segments), len(TRANSCRIPT))
total_frames = len(stream.frames)
total_ms = total_frames * 10

print(f"Audio: {total_frames} frames = {total_ms}ms = {total_ms / 1000:.1f}s")
print(f"Segments: {len(segments)} (using {n_seg} with transcript)")
print(f"Sample rate: {stream.sample_rate}, hop: {hop} samples = 10ms")
print()

# Show all segment info
print(f"{'Seg':>3} {'Word':>15} {'Start':>6} {'End':>6} {'Len':>4} {'ms':>6}  {'RMS profile (10 chars)'}")
print(f"{'---':>3} {'----':>15} {'-----':>6} {'---':>6} {'---':>4} {'--':>6}  {'--------------------'}")

for i in range(n_seg):
    seg = segments[i]
    n_frames = len(seg.frames)
    start_ms = seg.start * 10
    end_ms = (seg.start + n_frames) * 10

    # Extract RMS per frame
    rms_vals = []
    for frame_packed in seg.frames:
        rms, _, _, _ = unpack_frame(frame_packed)
        rms_vals.append(rms)

    # Compact RMS visualization (10 chars showing energy profile)
    if rms_vals:
        # Bin into 10 groups
        n_bins = min(10, len(rms_vals))
        bin_size = max(1, len(rms_vals) // n_bins)
        bins = []
        for b in range(n_bins):
            start_b = b * bin_size
            end_b = min(start_b + bin_size, len(rms_vals))
            avg_rms = np.mean(rms_vals[start_b:end_b])
            bins.append(avg_rms)

        # Map to block chars
        max_rms = max(bins) if max(bins) > 0 else 1
        blocks = " ▁▂▃▄▅▆▇█"
        profile = ""
        for b in bins:
            level = int(b / max_rms * 8)
            level = min(8, max(0, level))
            profile += blocks[level]
    else:
        profile = "---"

    avg_rms = np.mean(rms_vals) if rms_vals else 0
    max_r = max(rms_vals) if rms_vals else 0

    word = TRANSCRIPT[i] if i < len(TRANSCRIPT) else "?"
    print(
        f"{i:3d} {word:>15} {seg.start:6d} {seg.start + n_frames:6d} {n_frames:4d} {start_ms:5d}ms  {profile}  rms_avg={avg_rms:.0f} max={max_r}"
    )

# Check gaps and overlaps
print()
print("Gap/overlap between segments:")
for i in range(1, n_seg):
    prev_end = segments[i - 1].start + len(segments[i - 1].frames)
    curr_start = segments[i].start
    gap = curr_start - prev_end
    if gap != 0:
        gap_type = "GAP" if gap > 0 else "OVERLAP"
        print(f"  Seg {i - 1}→{i}: {gap_type} of {abs(gap)} frames ({abs(gap) * 10}ms)")

# Compare repeated words in detail
print()
print("=" * 70)
print("REPEATED WORD ANALYSIS")
print("=" * 70)

word_indices = {}
for i in range(n_seg):
    word_indices.setdefault(TRANSCRIPT[i], []).append(i)

for word, idxs in word_indices.items():
    if len(idxs) < 2:
        continue
    print(f"\n  Word '{word}' appears {len(idxs)} times:")
    for idx in idxs:
        seg = segments[idx]
        n_frames = len(seg.frames)
        rms_vals = [unpack_frame(f)[0] for f in seg.frames]
        f0_vals = [unpack_frame(f)[2] for f in seg.frames]
        voiced = [1 for f0 in f0_vals if f0 > 0]

        # MFCCs: average C1-C4 (spectral shape)
        mfcc_avgs = np.zeros(4)
        count = 0
        for fi in range(n_frames):
            abs_fi = seg.start + fi
            if stream.mfcc_frames and abs_fi < len(stream.mfcc_frames):
                m = stream.mfcc_frames[abs_fi]
                if any(c != 0 for c in m):
                    mfcc_avgs += np.array([m[k] / 100.0 for k in range(1, 5)])
                    count += 1
        if count > 0:
            mfcc_avgs /= count

        print(
            f"    Seg {idx}: {n_frames} frames ({n_frames * 10}ms), "
            f"rms=[{min(rms_vals)}-{max(rms_vals)}] avg={np.mean(rms_vals):.0f}, "
            f"voiced={len(voiced)}/{n_frames}, "
            f"mfcc_avg=[{mfcc_avgs[0]:.1f}, {mfcc_avgs[1]:.1f}, {mfcc_avgs[2]:.1f}, {mfcc_avgs[3]:.1f}]"
        )

# Final analysis: what's the actual segment length distribution?
print()
print("=" * 70)
print("SEGMENT LENGTH DISTRIBUTION")
print("=" * 70)
lengths = [len(segments[i].frames) for i in range(n_seg)]
print(f"  Min: {min(lengths)} frames ({min(lengths) * 10}ms)")
print(f"  Max: {max(lengths)} frames ({max(lengths) * 10}ms)")
print(f"  Mean: {np.mean(lengths):.0f} frames ({np.mean(lengths) * 10:.0f}ms)")
print(f"  Std: {np.std(lengths):.0f} frames")

# Short segments (< 150ms) and long segments (> 500ms)
short = [(i, TRANSCRIPT[i], len(segments[i].frames)) for i in range(n_seg) if len(segments[i].frames) < 15]
long = [(i, TRANSCRIPT[i], len(segments[i].frames)) for i in range(n_seg) if len(segments[i].frames) > 40]
print(f"\n  Short (<150ms): {len(short)}")
for idx, w, n in short:
    print(f"    Seg {idx}: '{w}' = {n} frames ({n * 10}ms)")
print(f"\n  Long (>400ms): {len(long)}")
for idx, w, n in long:
    print(f"    Seg {idx}: '{w}' = {n} frames ({n * 10}ms)")
