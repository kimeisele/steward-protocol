"""
EXPERIMENT 7: stream_to_rama + _stable_coords + encode_text dictionary
=======================================================================

The SAME dialect on both sides:
  Audio: stream_to_rama() → _stable_coords(min_run=3) → short coord sequence
  Dict:  encode_text() → coords (letter-by-letter IAST)

Both use the same RAMA space. stream_to_rama gives articulatory coords,
encode_text gives letter-based coords. They should be in the same element
neighborhoods because the RAMA coord system IS structured by articulation.

Key insight from experiment 6: elements MATCH even when exact coords differ.
The element-weighted edit distance handles this.
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _stable_coords, _score_candidate,
    get_pronunciation_dict, PronunciationDict,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

# Build dictionary using encode_text (same dialect as stream_to_rama)
pdict = get_pronunciation_dict()

print(f"Segments: {len(segments)}")
print()

words_out = []
for si, seg in enumerate(segments):
    raw = stream_to_rama(seg.frames)
    if not raw:
        continue

    stable = _stable_coords(raw, min_run=3)
    if not stable or len(stable) < 1:
        continue

    # Dictionary matching
    first_coord = stable[0]
    coord_len = len(stable)
    candidates = []

    # Wider search: ±2 on first coord + length-based
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
        score = _score_candidate(stable, word_coords)
        if score > best_score:
            best_score = score
            best_word = word

    ms_s = seg.start * 10
    ms_e = seg.end * 10

    if best_score >= 0.25:
        deduped = _dedup_coords(raw)
        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:20s} conf={best_score:.3f}  "
              f"stable={stable[:5]} (raw={len(raw)},ded={len(deduped)},stab={len(stable)})")
        words_out.append(best_word)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

print(f"\nTRANSCRIPT: {' '.join(words_out)}")
print(f"\nEXPECTED: {EXPECTED}")

correct = sum(1 for w in words_out if w.lower() in expected_words)
print(f"\nCorrect: {correct}/{len(words_out)} ({correct/max(1,len(words_out))*100:.0f}%)")
