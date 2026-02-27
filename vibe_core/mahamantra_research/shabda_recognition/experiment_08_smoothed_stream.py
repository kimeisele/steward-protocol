"""
EXPERIMENT 8: Smooth acoustic features BEFORE coord assignment
===============================================================

Problem: frame_to_rama() oscillates between coords because centroid/RMS
fluctuate frame-to-frame. A sustained vowel flickers between 3 coords.

Fix: Average the packed features over a window of N frames, THEN feed to
frame_to_rama(). This gives stable, representative coords.

Also test: majority-vote AFTER coord assignment (simpler, no feature change).
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame, pack_frame
from vibe_core.mahamantra.sound.shabda_processor import frame_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _score_candidate, get_pronunciation_dict,
)
from collections import Counter
from typing import List, Tuple

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
pdict = get_pronunciation_dict()


def smoothed_stream_to_rama(frames, window=5) -> Tuple[int, ...]:
    """Smooth features over window, then map to RAMA."""
    n = len(frames)
    if n == 0:
        return ()
    
    half = window // 2
    coords = []
    prev_packed = 0
    
    for i in range(n):
        # Average features in window [i-half, i+half]
        rms_sum, varga_votes, f0_sum, cent_sum = 0, [], 0, 0
        count = 0
        for j in range(max(0, i - half), min(n, i + half + 1)):
            r, v, f, c = unpack_frame(frames[j])
            rms_sum += r
            varga_votes.append(v)
            f0_sum += f
            cent_sum += c
            count += 1
        
        avg_rms = rms_sum // count
        avg_varga = Counter(varga_votes).most_common(1)[0][0]  # mode
        avg_f0 = f0_sum // count
        avg_cent = cent_sum // count
        
        smoothed = pack_frame(avg_rms, avg_varga, avg_f0, avg_cent)
        c = frame_to_rama(smoothed, prev_packed)
        if c >= 0:
            coords.append(c)
        prev_packed = smoothed
    
    return tuple(coords)


def majority_vote_coords(coords, window=5) -> Tuple[int, ...]:
    """Majority vote smoothing on coord sequence."""
    if not coords:
        return ()
    n = len(coords)
    half = window // 2
    smoothed = []
    for i in range(n):
        start = max(0, i - half)
        end = min(n, i + half + 1)
        vote = Counter(coords[start:end]).most_common(1)[0][0]
        smoothed.append(vote)
    return tuple(smoothed)


EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

# Test both approaches
for label, method in [
    ("SMOOTHED(w=5)", lambda frames: smoothed_stream_to_rama(frames, 5)),
    ("SMOOTHED(w=7)", lambda frames: smoothed_stream_to_rama(frames, 7)),
]:
    print(f"\n{'='*70}")
    print(f"METHOD: {label}")
    print(f"{'='*70}")
    
    words_out = []
    for si, seg in enumerate(segments):
        raw = method(seg.frames)
        if not raw:
            continue
        
        # Majority vote then dedup
        voted = majority_vote_coords(raw, 5)
        deduped = _dedup_coords(voted)
        if not deduped:
            continue
        
        # Dict matching
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
        
        if best_score >= 0.3:
            print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:20s} conf={best_score:.3f}  deduped={deduped[:5]} ({len(deduped)})")
            words_out.append(best_word)
    
    correct = sum(1 for w in words_out if w.lower() in expected_words)
    print(f"\nTRANSCRIPT: {' '.join(words_out)}")
    print(f"Correct: {correct}/{len(words_out)} ({correct/max(1,len(words_out))*100:.0f}%)")
