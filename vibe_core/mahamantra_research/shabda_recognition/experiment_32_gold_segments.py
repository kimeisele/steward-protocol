"""
EXPERIMENT 32: Gold-Standard Segment Test
==========================================

ROOT CAUSE from exp 31: segment_stream() cuts incorrectly.
"enthusiastic"=100ms, "krishna"=120ms, 780ms gaps.

QUESTION: If we had PERFECT segmentation, would DTW/features work?

Test: Use the FULL audio (no segmentation) and slide a window.
For each known word, find the approximate time range manually.
Then test: can DTW match the two "and"s, the two "i"s?

Approach: Divide the 14s audio into fixed-size overlapping windows
and see if same-word windows cluster. This bypasses segment_stream entirely.

Actually simpler: just re-segment with MUCH more conservative thresholds.
Only split at true silence (RMS<10 for 5+ frames = 50ms+).
This should give us fewer, larger, more correct segments.
"""

import sys

sys.path.insert(0, ".")

import numpy as np
from collections import defaultdict
from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")

# Custom segmentation: much more conservative
# Only split at TRUE silence: RMS < 10 for 5+ consecutive frames (50ms+)
SILENCE_THRESH = 10
SILENCE_GAP = 5
MIN_SEG = 8  # 80ms minimum

frames = stream.frames
n = len(frames)

print(f"Total frames: {n} ({n * 10}ms)")
print()

# First: show RMS profile of entire audio to find natural word boundaries
print("Full audio RMS profile (every 10th frame):")
for i in range(0, n, 10):
    rms = frames[i] & 0xFF
    bar = "█" * (rms // 10)
    print(f"  {i * 10:5d}ms (f{i:4d}): rms={rms:3d} {bar}")

print()
print("=" * 70)
print("CONSERVATIVE SEGMENTATION (silence_thresh=10, gap=50ms)")
print("=" * 70)

# Segment with conservative thresholds
segments = []  # (start, end)
seg_start = -1
silence_count = 0

for i in range(n):
    rms = frames[i] & 0xFF

    if rms < SILENCE_THRESH:
        silence_count += 1
    else:
        silence_count = 0

    if seg_start < 0 and rms >= SILENCE_THRESH:
        seg_start = i
        silence_count = 0
        continue

    if seg_start < 0:
        continue

    if silence_count >= SILENCE_GAP:
        seg_end = i - silence_count + 1
        if seg_end - seg_start >= MIN_SEG:
            segments.append((seg_start, seg_end))
        seg_start = -1

# Flush
if seg_start >= 0 and n - seg_start >= MIN_SEG:
    segments.append((seg_start, n))

print(f"Found {len(segments)} segments:")
for i, (s, e) in enumerate(segments):
    dur = (e - s) * 10
    rms_vals = [frames[j] & 0xFF for j in range(s, e)]
    avg_rms = np.mean(rms_vals)
    print(f"  Seg {i}: [{s * 10:5d}-{e * 10:5d}ms] = {dur:4d}ms  avg_rms={avg_rms:.0f}  frames={e - s}")

# The transcript for this audio is approximately:
# "eh not exactly but I came to preach the gospel of Krishna consciousness
#  and fortunately I met some enthusiastic young boys and girls"
# ~23 words over ~14s. But Prabhupada speaks with pauses.
# We should get ~5-8 phrase-level segments with conservative thresholds.

print()
print("=" * 70)
print("MEDIUM SEGMENTATION (silence_thresh=15, gap=40ms)")
print("=" * 70)

segments2 = []
seg_start = -1
silence_count = 0

for i in range(n):
    rms = frames[i] & 0xFF
    if rms < 15:
        silence_count += 1
    else:
        silence_count = 0

    if seg_start < 0 and rms >= 15:
        seg_start = i
        silence_count = 0
        continue
    if seg_start < 0:
        continue
    if silence_count >= 4:
        seg_end = i - silence_count + 1
        if seg_end - seg_start >= MIN_SEG:
            segments2.append((seg_start, seg_end))
        seg_start = -1

if seg_start >= 0 and n - seg_start >= MIN_SEG:
    segments2.append((seg_start, n))

print(f"Found {len(segments2)} segments:")
for i, (s, e) in enumerate(segments2):
    dur = (e - s) * 10
    rms_vals = [frames[j] & 0xFF for j in range(s, e)]
    avg_rms = np.mean(rms_vals)
    print(f"  Seg {i}: [{s * 10:5d}-{e * 10:5d}ms] = {dur:4d}ms  avg_rms={avg_rms:.0f}  frames={e - s}")


# Now let's try even finer: split on RMS dips but with HIGHER threshold
# to approximate word boundaries
print()
print("=" * 70)
print("WORD-LEVEL SEGMENTATION (split at RMS dips < 40 for 2+ frames)")
print("=" * 70)

DIP_THRESH = 40
DIP_GAP = 2

segments3 = []
seg_start = -1
dip_count = 0

for i in range(n):
    rms = frames[i] & 0xFF
    if rms < DIP_THRESH:
        dip_count += 1
    else:
        dip_count = 0

    if seg_start < 0 and rms >= DIP_THRESH:
        seg_start = i
        dip_count = 0
        continue
    if seg_start < 0:
        continue
    if dip_count >= DIP_GAP:
        seg_end = i - dip_count + 1
        if seg_end - seg_start >= MIN_SEG:
            segments3.append((seg_start, seg_end))
        seg_start = -1

if seg_start >= 0 and n - seg_start >= MIN_SEG:
    segments3.append((seg_start, n))

print(f"Found {len(segments3)} segments:")

# Approximate transcript alignment for word-level segments
# We know there are 23 words, let's see how many segments we get
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

for i, (s, e) in enumerate(segments3):
    dur = (e - s) * 10
    rms_vals = [frames[j] & 0xFF for j in range(s, e)]
    avg_rms = np.mean(rms_vals)
    word = TRANSCRIPT[i] if i < len(TRANSCRIPT) else "?"
    print(f"  Seg {i:2d}: [{s * 10:5d}-{e * 10:5d}ms] = {dur:4d}ms  avg_rms={avg_rms:.0f}  ({word}?)")


# Now the key test: with THIS segmentation, does DTW self-match work?
# Extract MFCCs for each segment and do nearest-neighbor
print()
print("=" * 70)
print("DTW SELF-MATCH WITH WORD-LEVEL SEGMENTS")
print("=" * 70)

n_seg3 = min(len(segments3), len(TRANSCRIPT))


def get_mfcc(start, end):
    """Get MFCC matrix for frame range."""
    rows = []
    for fi in range(start, end):
        if stream.mfcc_frames and fi < len(stream.mfcc_frames):
            m = stream.mfcc_frames[fi]
            if any(c != 0 for c in m):
                rows.append(np.array([c / 100.0 for c in m]))
                continue
        rows.append(np.zeros(13))
    return np.array(rows)


def dtw(a, b):
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return float("inf")
    band = max(n, m) // 2 + 2
    INF = 1e30
    prev = np.full(m + 1, INF)
    curr = np.full(m + 1, INF)
    prev[0] = 0.0
    for i in range(1, n + 1):
        curr[:] = INF
        j_lo = max(1, i * m // n - band)
        j_hi = min(m, i * m // n + band)
        for j in range(j_lo, j_hi + 1):
            d = np.sqrt(np.sum((a[i - 1] - b[j - 1]) ** 2))
            curr[j] = d + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev
    return prev[m] / max(n, m)


seg3_mfccs = [get_mfcc(s, e) for s, e in segments3[:n_seg3]]

# Find repeated words
repeated = defaultdict(list)
for i in range(n_seg3):
    repeated[TRANSCRIPT[i]].append(i)
repeated = {w: idxs for w, idxs in repeated.items() if len(idxs) > 1}

# Compute pairwise DTW
print(f"\nUsing {n_seg3} segments")
costs = np.zeros((n_seg3, n_seg3))
for i in range(n_seg3):
    for j in range(i, n_seg3):
        c = dtw(seg3_mfccs[i], seg3_mfccs[j])
        costs[i, j] = c
        costs[j, i] = c

# Show nearest neighbors
nn_correct = 0
for i in range(n_seg3):
    ranked = sorted(range(n_seg3), key=lambda j: costs[i, j])
    ranked = [j for j in ranked if j != i]
    nearest = TRANSCRIPT[ranked[0]]
    match = "✓" if nearest == TRANSCRIPT[i] else " "
    if nearest == TRANSCRIPT[i]:
        nn_correct += 1
    top3 = [(TRANSCRIPT[j], costs[i, j]) for j in ranked[:3]]
    top3_str = ", ".join(f"{w}:{c:.1f}" for w, c in top3)
    n_frames = segments3[i][1] - segments3[i][0]
    print(f"  {i:2d} [{TRANSCRIPT[i]:15s}] {n_frames:3d}f → {nearest:15s} {match}  [{top3_str}]")

print(f"\nNN accuracy: {nn_correct}/{n_seg3}")

if repeated:
    same_d, diff_d = [], []
    for w, idxs in repeated.items():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                same_d.append(costs[idxs[a], idxs[b]])
    for i in range(n_seg3):
        for j in range(i + 1, n_seg3):
            if TRANSCRIPT[i] != TRANSCRIPT[j]:
                diff_d.append(costs[i, j])

    print(f"Same-word: mean={np.mean(same_d):.2f} [{np.min(same_d):.2f}, {np.max(same_d):.2f}]")
    print(f"Diff-word: mean={np.mean(diff_d):.2f} [{np.min(diff_d):.2f}, {np.max(diff_d):.2f}]")
    sep = np.max(same_d) < np.min(diff_d)
    print(f"Separation: {'YES!' if sep else 'NO (overlap)'}")
