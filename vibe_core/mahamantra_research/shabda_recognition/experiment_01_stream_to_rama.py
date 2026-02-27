"""
EXPERIMENT 1: Use shabda_processor.stream_to_rama() directly
=============================================================

HYPOTHESIS: The existing clean path (frame_to_rama via lookup tables)
should produce RAMA coords that are at least as good as the spaghetti
score_frame() path, since both use the same acoustic features.

The key difference: stream_to_rama uses TRANSITION detection (prev_frame)
which score_frame does NOT. This should catch consonants better.

We compare:
  A) shabda_processor.stream_to_rama() → dedup → dict match
  B) current score_frame path → dedup → dict match

For BOTH paths we use the same dictionary (CMU-based PronunciationDict).
"""
import sys; sys.path.insert(0, ".")
import time

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    ShabdaDecoder, segment_stream, _dedup_coords, _stable_coords,
    _score_candidate, get_pronunciation_dict,
)

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
pdict = get_pronunciation_dict()

print(f"Frames: {len(stream.frames)}, Segments: {len(segments)}")
print(f"Dict: {pdict.sanskrit_count} Sanskrit, {pdict.english_count} English")
print()

# Expected transcript
EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"

print("=" * 80)
print("PATH A: shabda_processor.stream_to_rama() (existing clean path)")
print("=" * 80)

words_a = []
for seg in segments:
    # Use stream_to_rama on the segment frames
    raw_coords = stream_to_rama(seg.frames)
    if not raw_coords:
        continue

    rama_coords = _dedup_coords(raw_coords)
    if not rama_coords:
        continue

    # Dictionary matching (same as decoder)
    first_coord = rama_coords[0]
    coord_len = len(rama_coords)
    candidates = []

    for fc in (first_coord, first_coord - 1, first_coord + 1):
        if 0 <= fc < 49:
            candidates.extend(
                pdict.candidates_for_segment(fc, coord_len, length_tolerance=3)
            )
    if len(candidates) < 10:
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
        score = _score_candidate(rama_coords, word_coords)
        if score > best_score:
            best_score = score
            best_word = word

    if best_score >= 0.3:
        ms_start = seg.start * 10
        ms_end = seg.end * 10
        print(f"  [{ms_start:5d}-{ms_end:5d}ms] {best_word:20s} conf={best_score:.3f}  coords={rama_coords[:6]}...")
        words_a.append(best_word)

print(f"\nPATH A TRANSCRIPT: {' '.join(words_a)}")
print(f"\nEXPECTED: {EXPECTED}")

# Count correct words
expected_words = set(EXPECTED.lower().split())
correct_a = sum(1 for w in words_a if w.lower() in expected_words)
print(f"\nCorrect words (path A): {correct_a}/{len(words_a)} ({correct_a/max(1,len(words_a))*100:.0f}%)")
