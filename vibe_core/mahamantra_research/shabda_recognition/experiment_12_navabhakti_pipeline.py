"""
EXPERIMENT 12: Feed audio through the EXISTING NavaBhakti pipeline
===================================================================

The pipeline already exists in lotus_core.py:
    1. Sravanam  — receive input
    2. Kirtanam  — compress to seed (MahaCompression)
    3. Pada Sevanam — seed → attractor via MahaSynth
    4. Smaranam  — attractor + coords → ranked words (7D ResonanceRanker)

For TEXT this works: text → encode_text() → RAMA coords → smaranam()
For AUDIO we do:   audio → VibrationSignature → RAMA coords → smaranam()

The key: smaranam() takes (input_coords, attractor) and returns ranked words.
We already have coords from stream_to_rama/vibration path.
We can get attractors from the synth.

This experiment: use the PRODUCTION pipeline on audio segments.
"""

import sys

sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_vibration import (
    stream_to_vibrations,
    vibrations_to_coords,
)
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream,
    _dedup_coords,
    _stable_coords,
)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text

# Try to use the real smaranam pipeline
try:
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

    lotus = get_mahamantra()
    HAS_LOTUS = True
    print("LOTUS VM loaded successfully")
except Exception as e:
    HAS_LOTUS = False
    print(f"LOTUS VM not available: {e}")
    # Fallback: use ResonanceRanker directly
    from vibe_core.mahamantra.substrate.encoding.resonance_ranker import rank_words

synth = MahaModularSynth(default_preset="quantum")

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

print(f"\nSegments: {len(segments)}")
print()

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

# === Approach 1: stream_to_rama coords → synth → smaranam ===
print("=" * 70)
print("APPROACH 1: stream_to_rama → attractor → smaranam (7D ranker)")
print("=" * 70)

words_out = []
for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    # Get RAMA coords from audio
    raw_coords = stream_to_rama(seg.frames)
    if not raw_coords:
        continue

    coords = _stable_coords(raw_coords, min_run=2)
    if not coords or len(coords) < 1:
        coords = _dedup_coords(raw_coords)
    if not coords:
        continue

    # Get attractor from first coord's seed through synth
    seed = sum(coords) * 7 + len(coords)  # simple deterministic seed from coord pattern
    attractor = synth.transform(seed)

    # Use smaranam (7D ResonanceRanker)
    if HAS_LOTUS:
        ranked = lotus.smaranam(coords, attractor)
    else:
        ranked = rank_words(
            input_coords=coords,
            input_attractor=attractor,
            top_n=5,
        )

    if ranked:
        best = ranked[0]
        word = best.sanskrit if hasattr(best, "sanskrit") else str(best)
        score = best.total_score if hasattr(best, "total_score") else 0.0
        meanings = best.first_meaning if hasattr(best, "first_meaning") else ""

        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {word:20s} score={score:.3f}  meaning='{meanings}' coords={coords[:5]}")
        words_out.append(word)

print(f"\nSMARANAM TRANSCRIPT: {' '.join(words_out)}")
correct = sum(1 for w in words_out if w.lower() in expected_words)
print(f"Correct (exact): {correct}/{len(words_out)}")

# Check if meanings match expected words
meaning_matches = 0
for w in words_out:
    # Check if any ranked word's meaning contains an expected word
    pass  # We'll print meanings above to see

# === Approach 2: VibrationSignature coords → attractor → smaranam ===
print()
print("=" * 70)
print("APPROACH 2: VibrationSignature → coords → attractor → smaranam")
print("=" * 70)

words_out2 = []
for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    vibs = stream_to_vibrations(seg.frames)
    if not vibs:
        continue

    # Use signature_ids to derive attractor
    sig_sum = sum(v.signature_id for v in vibs)
    attractor = synth.transform(sig_sum)

    # Also get coords from vibration path
    vib_coords = vibrations_to_coords(vibs)
    if not vib_coords:
        continue

    deduped = _dedup_coords(vib_coords)
    if not deduped:
        continue

    # Use smaranam
    if HAS_LOTUS:
        ranked = lotus.smaranam(deduped, attractor)
    else:
        ranked = rank_words(
            input_coords=deduped,
            input_attractor=attractor,
            top_n=5,
        )

    if ranked:
        best = ranked[0]
        word = best.sanskrit if hasattr(best, "sanskrit") else str(best)
        score = best.total_score if hasattr(best, "total_score") else 0.0
        meanings = best.first_meaning if hasattr(best, "first_meaning") else ""

        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {word:20s} score={score:.3f}  meaning='{meanings}' coords={deduped[:5]}")
        words_out2.append(word)

print(f"\nVIBRATION TRANSCRIPT: {' '.join(words_out2)}")

# === Approach 3: Full MahaKernel __call__ on vibration text ===
print()
print("=" * 70)
print("APPROACH 3: Vibration → nearest phoneme text → MahaKernel.__call__")
print("=" * 70)

# For each segment, convert vibrations to phoneme text, then feed to Lotus
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    vibration_to_sanskrit,
    SANSKRIT_PHONEME_MAP,
    VibrationSignature,
)

words_out3 = []
for si, seg in enumerate(segments[:10]):  # first 10 only for speed
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    vibs = stream_to_vibrations(seg.frames)
    if not vibs:
        continue

    # Convert audio vibrations → nearest Sanskrit phonemes → text
    shabda_text = vibration_to_sanskrit(list(vibs))

    if HAS_LOTUS:
        # Feed the phoneme text through the FULL pipeline
        result = lotus(shabda_text)

        # Extract ranked words from smaranam
        smaranam = result.get("smaranam", [])
        if smaranam:
            best = smaranam[0]
            word = best.sanskrit if hasattr(best, "sanskrit") else str(best)
            score = best.total_score if hasattr(best, "total_score") else 0.0
            print(f"  [{ms_s:5d}-{ms_e:5d}ms] shabda='{shabda_text[:20]}' → {word:20s} score={score:.3f}")
            words_out3.append(word)
        else:
            print(f"  [{ms_s:5d}-{ms_e:5d}ms] shabda='{shabda_text[:20]}' → no smaranam")
    else:
        # Without Lotus, just encode the shabda text
        coords = encode_text(shabda_text)
        if coords:
            attractor = synth.transform(sum(coords))
            ranked = rank_words(input_coords=coords, input_attractor=attractor, top_n=3)
            if ranked:
                best = ranked[0]
                word = best.sanskrit
                print(
                    f"  [{ms_s:5d}-{ms_e:5d}ms] shabda='{shabda_text[:20]}' → {word:20s} score={best.total_score:.3f}"
                )
                words_out3.append(word)

if words_out3:
    print(f"\nFULL PIPELINE TRANSCRIPT: {' '.join(words_out3)}")
