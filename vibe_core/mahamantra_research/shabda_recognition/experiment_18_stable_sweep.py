"""
EXPERIMENT 18: Sweep min_run for _stable_coords to find best filtering
========================================================================

The raw coords have the right info but too many transitions.
_stable_coords(min_run=N) keeps only coords that persist N+ frames.
Higher N = fewer spurious coords, but might lose real short consonants.

Also: compare element sequences at different min_run values.
"""

import sys

sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream,
    _dedup_coords,
    _stable_coords,
    get_pronunciation_dict,
    _score_candidate,
)
from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_ELEMENT

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
pdict = get_pronunciation_dict()

EXPECTED = [
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

ELEM_NAMES = ["AK", "VA", "AG", "JA", "PR"]

print("=" * 80)
print("Part 1: Coords at different min_run values vs dict coords")
print("=" * 80)

for si, expected in enumerate(EXPECTED[:8]):
    if si >= len(segments):
        break
    seg = segments[si]
    raw = stream_to_rama(seg.frames)

    dict_c = pdict.lookup(expected)
    d_elems = [ELEM_NAMES[COORD_ELEMENT[c]] for c in dict_c] if dict_c else []
    print(f"\n  [{expected:10s}] DICT: {str(dict_c):40s} elems={d_elems}")

    for mr in [2, 3, 4, 5, 7]:
        stable = _stable_coords(raw, min_run=mr)
        elems = [ELEM_NAMES[COORD_ELEMENT[c]] for c in stable] if stable else []
        score = _score_candidate(stable, dict_c) if stable and dict_c else 0.0
        print(f"  [{expected:10s}] mr={mr}: {str(stable):40s} elems={elems}  score={score:.3f}")


# Part 2: Full decode at each min_run, count accuracy
print()
print("=" * 80)
print("Part 2: Full decode accuracy at each min_run value")
print("=" * 80)

for mr in [2, 3, 4, 5, 7]:
    correct = 0
    total = 0
    words_out = []
    for si, seg in enumerate(segments):
        raw = stream_to_rama(seg.frames)
        coords = _stable_coords(raw, min_run=mr)
        if not coords:
            coords = _dedup_coords(raw)
        if not coords:
            continue

        # Score against expected vocab
        best_word = ""
        best_score = -1.0
        for word in EXPECTED:
            wc = pdict.lookup(word)
            if wc:
                sc = _score_candidate(coords, wc)
                if sc > best_score:
                    best_score = sc
                    best_word = word

        words_out.append(best_word)
        if si < len(EXPECTED) and best_word == EXPECTED[si]:
            correct += 1
        total += 1

    pct = correct / max(1, total) * 100
    transcript = " ".join(words_out[: len(EXPECTED)])
    print(f"  min_run={mr}: {correct}/{min(total, len(EXPECTED))} correct ({pct:.0f}%)")
    print(f"    transcript: {transcript}")

# Part 3: What if we also score against ALL dict words (not just expected)?
print()
print("=" * 80)
print("Part 3: Score against FULL pronunciation dict (best min_run from above)")
print("=" * 80)

best_mr = 3  # use a reasonable default
for si, seg in enumerate(segments[:10]):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    raw = stream_to_rama(seg.frames)
    coords = _stable_coords(raw, min_run=best_mr)
    if not coords:
        coords = _dedup_coords(raw)
    if not coords:
        continue

    # Get candidates from pronunciation dict
    candidates = pdict.all_candidates_for_length(len(coords), length_tolerance=3)

    best_word = ""
    best_score = -1.0
    for word, wc in candidates:
        sc = _score_candidate(coords, wc)
        if sc > best_score:
            best_score = sc
            best_word = word

    expected = EXPECTED[si] if si < len(EXPECTED) else "?"
    match = "✓" if best_word == expected else " "
    print(
        f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} score={best_score:.4f} {match}  "
        f"(expected: {expected})  coords={coords[:6]}"
    )
