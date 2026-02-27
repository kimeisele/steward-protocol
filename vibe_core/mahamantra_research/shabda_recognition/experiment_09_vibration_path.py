"""
EXPERIMENT 9: VibrationSignature path — audio → vibrations → coords → dict match
==================================================================================

The NEW pipeline:
    Audio frames → stream_to_vibrations() → VibrationSignature per phoneme
    VibrationSignatures → vibrations_to_coords() → RAMA coords
    RAMA coords → ResonanceRanker 7D scoring against dictionary

Compare: How do vibration-derived coords compare to stream_to_rama coords?
Do they give better word matching?
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_vibration import (
    stream_to_vibrations,
    vibrations_to_coords,
    stream_to_vibration_coords,
)
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _score_candidate, get_pronunciation_dict,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text
from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, COORD_VARGA

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
pdict = get_pronunciation_dict()

ELEM_NAMES = ["PRTHVI", "JALA", "AGNI", "VAYU", "AKASH"]

print(f"Segments: {len(segments)}")
print()

# === Part 1: Examine VibrationSignature output ===
print("=" * 70)
print("PART 1: VibrationSignature decomposition")
print("=" * 70)
for si, seg in enumerate(segments[:5]):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    vibs = stream_to_vibrations(seg.frames)
    vib_coords = vibrations_to_coords(vibs)
    old_coords = stream_to_rama(seg.frames)
    old_deduped = _dedup_coords(old_coords)

    print(f"\n[{si}] {ms_s}-{ms_e}ms ({len(seg.frames)} frames)")
    print(f"  VibSignatures: {len(vibs)} phonemes")
    for v in vibs[:6]:
        print(f"    art={v.articulation.name:8s} voicing={v.voicing.name:20s} "
              f"freq={v.base_frequency:4d} dur={v.duration_ratio:2d} "
              f"sig_id={v.signature_id}")
    print(f"  Vibration coords ({len(vib_coords)}): {vib_coords[:8]}")
    print(f"  stream_to_rama  ({len(old_deduped)}): {old_deduped[:8]}")

# === Part 2: Dictionary matching with vibration coords ===
print()
print("=" * 70)
print("PART 2: Dictionary matching — vibration path")
print("=" * 70)

words_out = []
for si, seg in enumerate(segments):
    vib_coords = stream_to_vibration_coords(seg.frames)
    if not vib_coords:
        continue

    deduped = _dedup_coords(vib_coords)
    if not deduped:
        continue

    # Dictionary matching
    first_coord = deduped[0]
    coord_len = len(deduped)
    candidates = []

    for fc in range(max(0, first_coord - 2), min(49, first_coord + 3)):
        candidates.extend(
            pdict.candidates_for_segment(fc, coord_len, length_tolerance=3)
        )
    if len(candidates) < 20:
        candidates.extend(
            pdict.all_candidates_for_length(coord_len, length_tolerance=2)
        )

    best_word = ""
    best_score = 0.0
    seen = set()
    for word, word_coords in candidates:
        if word in seen:
            continue
        seen.add(word)
        score = _score_candidate(deduped, word_coords)
        if score > best_score:
            best_score = score
            best_word = word

    ms_s = seg.start * 10
    ms_e = seg.end * 10

    if best_score >= 0.25:
        elems = [ELEM_NAMES[COORD_ELEMENT[c]] for c in deduped[:5]]
        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:20s} conf={best_score:.3f}  "
              f"coords={deduped[:5]} elems={elems}")
        words_out.append(best_word)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

print(f"\nVIBRATION TRANSCRIPT: {' '.join(words_out)}")
print(f"\nEXPECTED: {EXPECTED}")

correct = sum(1 for w in words_out if w.lower() in expected_words)
print(f"\nCorrect: {correct}/{len(words_out)} ({correct/max(1,len(words_out))*100:.0f}%)")

# === Part 3: Compare vibration coords vs encode_text for known words ===
print()
print("=" * 70)
print("PART 3: Vibration signature_id distribution")
print("=" * 70)
for word in ["the", "and", "krishna", "consciousness", "boys", "girls", "gospel"]:
    from vibe_core.mahamantra.substrate.phonetics.shabda import text_to_vibration
    text_vibs = text_to_vibration(word)
    text_sig_ids = [v.signature_id % 49 for v in text_vibs]
    text_coords = encode_text(word)
    print(f"  '{word}': encode_text={text_coords}  text_vib_coords={tuple(text_sig_ids)}")
