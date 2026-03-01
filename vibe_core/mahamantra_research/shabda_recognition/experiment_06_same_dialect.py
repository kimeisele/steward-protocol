"""
EXPERIMENT 6: Same coordinate dialect for both sides
=====================================================

THE KEY QUESTION: If both audio AND dictionary use the same RAMA dialect,
does matching work?

Current problem: audio uses stream_to_rama() (articulatory coords) but
dictionary uses encode_text() or CMU→ARPABET_TO_RAMA (phonemic coords).
These are DIFFERENT dialects in the same 0-48 space.

FIX: Build dictionary entries using the SAME path as audio.
  For each word: get its text → encode_text() → coords (current)
  Instead:       get its text → synthesize through the SAME acoustic
                 features that stream_to_rama() uses

But we CAN'T synthesize audio for every word. What we CAN do:
  Use encode_text() coords for the dictionary (letter-by-letter IAST).
  And use stream_to_rama() coords for audio.
  Then measure the actual DISTANCE between them.

If the distance is small (same varga/element), edit distance with
element-weighted costs should still match. If the distance is huge,
the dialects are truly incompatible.

Let's measure this for known words in the transcript.
"""

import sys

sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream,
    _dedup_coords,
    _score_candidate,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text
from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_ELEMENT, COORD_VARGA

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

# Known alignment: (segment_index, expected_word)
# Based on transcript timing analysis
KNOWN = [
    (0, "eh"),
    (1, "eh"),
]

# Print what stream_to_rama produces for EVERY segment, with element names
ELEM_NAMES = ["PRTHVI", "JALA", "AGNI", "VAYU", "AKASH"]
VARGA_NAMES = ["SVARA", "SPARSHA", "SHESHA"]

print("SEGMENT ANALYSIS: stream_to_rama output")
print("=" * 80)

for si, seg in enumerate(segments):
    raw = stream_to_rama(seg.frames)
    deduped = _dedup_coords(raw)
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    # Show element/varga pattern
    elem_pattern = [ELEM_NAMES[COORD_ELEMENT[c]] for c in deduped[:8]]
    varga_pattern = [VARGA_NAMES[COORD_VARGA[c]] for c in deduped[:8]]

    print(f"\n[{si:2d}] {ms_s:5d}-{ms_e:5d}ms ({ms_e - ms_s:4d}ms, {len(seg.frames):3d}fr)")
    print(f"     raw({len(raw)}) deduped({len(deduped)}): {deduped[:8]}")
    print(f"     elements: {elem_pattern}")
    print(f"     vargas:   {varga_pattern}")

    # Score against some known words using encode_text
    for word in ["eh", "not", "exactly", "but", "came", "preach", "the", "gospel", "of", "i", "and", "some"]:
        word_coords = encode_text(word)
        if not word_coords:
            continue
        score = _score_candidate(deduped, word_coords)
        if score > 0.3:
            w_elem = [ELEM_NAMES[COORD_ELEMENT[c]] for c in word_coords[:5]]
            print(f"     -> '{word}' score={score:.3f} dict_coords={word_coords} elems={w_elem}")

    if si > 10:
        break
