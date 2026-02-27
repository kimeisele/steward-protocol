"""
EXPERIMENT 17: Centroid calibration — what ARE the actual centroid ranges?
==========================================================================

The _centroid_to_varga() thresholds are:
    < 800 Hz  → OSHTHYA (4, labial)
    < 1200 Hz → KANTHYA (0, throat)
    < 1800 Hz → TALAVYA (1, palatal)
    < 2500 Hz → MURDHANYA (2, retroflex)
    >= 2500 Hz → DANTYA (3, dental)

BUT centroid_100 in packed frames = centroid_hz / 100.
So centroid_100=150 means 15000 Hz, not 150 Hz!

If the thresholds are applied to raw Hz before packing, the packed
centroid_100 ranges should be:
    < 8   → OSHTHYA  (centroid < 800 Hz)
    < 12  → KANTHYA  (centroid < 1200 Hz)
    < 18  → TALAVYA  (centroid < 1800 Hz)
    < 25  → MURDHANYA (centroid < 2500 Hz)
    >= 25 → DANTYA

Let's verify: what centroid_100 values do we actually see, and
what varga did they get?
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame
from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
from collections import Counter

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")

# Histogram of centroid_100 values across ALL voiced frames
cent_hist = Counter()
varga_cent = {v: [] for v in range(5)}  # varga → list of centroid_100 values
total_voiced = 0

for frame in stream.frames:
    rms, varga, f0_x10, cent = unpack_frame(frame)
    if rms < 20:
        continue
    total_voiced += 1
    cent_hist[cent] += 1
    varga_cent[varga].append(cent)

print(f"Total voiced frames: {total_voiced}")
print()

# Centroid distribution
print("Centroid_100 distribution (top 20 values):")
for cent, count in cent_hist.most_common(20):
    pct = count / total_voiced * 100
    hz = cent * 100
    print(f"  cent_100={cent:3d} ({hz:5d} Hz)  count={count:4d} ({pct:5.1f}%)")

print()
print("Varga distribution:")
VARGA_NAMES = ["KANTH", "TALAV", "MURDH", "DANTY", "OSHTH"]
for v in range(5):
    vals = varga_cent[v]
    if vals:
        avg = sum(vals) / len(vals)
        lo = min(vals)
        hi = max(vals)
        print(f"  varga={v} ({VARGA_NAMES[v]:5s}): n={len(vals):4d} "
              f"cent_100: avg={avg:.0f} min={lo} max={hi} "
              f"(Hz: avg={avg*100:.0f} min={lo*100} max={hi*100})")

print()
print("Expected varga from centroid_100 thresholds:")
print("  OSHTHYA (4): cent_100 < 8     (< 800 Hz)")
print("  KANTHYA (0): cent_100 < 12    (< 1200 Hz)")
print("  TALAVYA (1): cent_100 < 18    (< 1800 Hz)")
print("  MURDHANYA(2): cent_100 < 25   (< 2500 Hz)")
print("  DANTYA (3): cent_100 >= 25    (>= 2500 Hz)")

print()
print("=" * 60)
print("ACTUAL centroid_100 ranges per varga (from audio):")
print("=" * 60)
# What centroid_100 values map to each varga?
# The varga was computed from raw centroid_hz BEFORE packing,
# so the boundaries should be:
# varga=4: centroid_hz < 800 → cent_100 < 8
# varga=0: centroid_hz < 1200 → 8 <= cent_100 < 12
# varga=1: centroid_hz < 1800 → 12 <= cent_100 < 18
# varga=2: centroid_hz < 2500 → 18 <= cent_100 < 25
# varga=3: centroid_hz >= 2500 → cent_100 >= 25

# But wait — let me check the packing formula again
# In shabda_intake.py: c = min(511, max(0, centroid_x10 // 100))
# centroid_x10 = int(centroid_hz * 10)
# So cent_100 = centroid_hz * 10 // 100 = centroid_hz // 10
# NOT centroid_hz / 100!

# So: centroid_100 = centroid_hz / 10
# varga=4: centroid_hz < 800 → cent_100 < 80
# varga=0: centroid_hz < 1200 → 80 <= cent_100 < 120
# varga=1: centroid_hz < 1800 → 120 <= cent_100 < 180
# varga=2: centroid_hz < 2500 → 180 <= cent_100 < 250
# varga=3: centroid_hz >= 2500 → cent_100 >= 250

print()
print("CORRECTED: centroid_100 = centroid_hz / 10 (not /100)")
print("  OSHTHYA (4): cent_100 < 80     (< 800 Hz)")
print("  KANTHYA (0): cent_100 80-119   (800-1200 Hz)")
print("  TALAVYA (1): cent_100 120-179  (1200-1800 Hz)")
print("  MURDHANYA(2): cent_100 180-249 (1800-2500 Hz)")
print("  DANTYA (3): cent_100 >= 250    (>= 2500 Hz)")

print()
for v in range(5):
    vals = varga_cent[v]
    if vals:
        lo, hi = min(vals), max(vals)
        print(f"  varga={v} ({VARGA_NAMES[v]:5s}): actual cent_100 range [{lo:3d} - {hi:3d}]")
