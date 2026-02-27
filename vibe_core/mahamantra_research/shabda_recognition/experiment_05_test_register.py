"""
EXPERIMENT 5: Test the real MFCC register
==========================================

Replace synthetic prototypes with trained ones from mfcc_register.json.
Use pure cosine similarity (no if-else weights) to classify frames.
Then: frame → best ARPAbet → ARPABET_TO_RAMA → dedup → dict match.

This is the DATA REGISTER approach: no score_frame(), no hand-tuned weights.
Just argmax(cosine_sim) over the register.
"""
import sys; sys.path.insert(0, ".")
import json
import math
from typing import Dict, List, Tuple

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, extract_mfcc
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _stable_coords,
    _score_candidate, get_pronunciation_dict,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import ARPABET_TO_RAMA

# Load trained register
with open("vibe_core/mahamantra_research/shabda_recognition/mfcc_register.json") as f:
    REGISTER: Dict[str, List[int]] = json.load(f)

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
samples = stream.raw_samples
sr = stream.sample_rate
hop = int(sr * stream.hop_ms / 1000)
n_fft = stream.n_fft

segments = segment_stream(stream.frames)
pdict = get_pronunciation_dict()


def cosine_sim(a: Tuple[int, ...], b: List[int]) -> float:
    """Cosine similarity between two MFCC vectors (skip c0 = energy)."""
    # Skip c0, use c1-c12
    va = a[1:13] if len(a) >= 13 else a
    vb = b[1:13] if len(b) >= 13 else b
    n = min(len(va), len(vb))
    if n == 0:
        return 0.0
    dot = sum(va[i] * vb[i] for i in range(n))
    na = math.sqrt(sum(x * x for x in va[:n]))
    nb = math.sqrt(sum(x * x for x in vb[:n]))
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return dot / (na * nb)


def frame_mfcc_to_arpabet(mfcc: Tuple[int, ...]) -> str:
    """Classify a frame's MFCC vector to the best ARPAbet phoneme."""
    best_phone = ""
    best_sim = -1.0
    for phone, proto in REGISTER.items():
        sim = cosine_sim(mfcc, proto)
        if sim > best_sim:
            best_sim = sim
            best_phone = phone
    return best_phone


print(f"Segments: {len(segments)}, Register: {len(REGISTER)} phonemes")
print()

words_out = []
for si, seg in enumerate(segments):
    # For each frame: extract MFCC → classify → ARPABET_TO_RAMA
    coords = []
    for i in range(len(seg.frames)):
        rms = seg.frames[i] & 0xFF
        if rms < 15:
            continue  # silence

        frame_idx = seg.start + i
        mfcc = stream.mfcc_frames[frame_idx]
        if not any(c != 0 for c in mfcc):
            continue

        phone = frame_mfcc_to_arpabet(mfcc)
        rama = ARPABET_TO_RAMA.get(phone)
        if rama is not None:
            coords.append(rama)

    if not coords:
        continue

    # Dedup (CTC-style)
    rama_coords = _dedup_coords(tuple(coords))
    if not rama_coords:
        continue

    # Dictionary matching
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

    ms_start = seg.start * 10
    ms_end = seg.end * 10

    if best_score >= 0.3:
        print(f"  [{ms_start:5d}-{ms_end:5d}ms] {best_word:20s} conf={best_score:.3f}  coords={rama_coords[:5]}")
        words_out.append(best_word)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

print(f"\nREGISTER TRANSCRIPT: {' '.join(words_out)}")
print(f"\nEXPECTED: {EXPECTED}")

correct = sum(1 for w in words_out if w.lower() in expected_words)
print(f"\nCorrect words: {correct}/{len(words_out)} ({correct/max(1,len(words_out))*100:.0f}%)")
