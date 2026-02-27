"""
EXPERIMENT 13: 7D ResonanceRanker on English pronunciation dictionary
======================================================================

The breakthrough chain:
  - smaranam() uses rank_words() with 7D scoring (element, harmonic, shruti, varga, attractor, HKR, phoneme_attractor)
  - rank_words() accepts custom LexiconWord candidates
  - PronunciationDict has English words with RAMA coords (via CMU→ARPAbet→ARPABET_TO_RAMA)
  - We wrap PronunciationDict entries as LexiconWord and score them with the FULL 7D ranker

This replaces the weak edit-distance _score_candidate() with production-grade resonance scoring.
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _stable_coords, get_pronunciation_dict,
)
from vibe_core.mahamantra.substrate.encoding.resonance_ranker import rank_words
from vibe_core.mahamantra.substrate.encoding.semantic_index import LexiconWord
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth

synth = MahaModularSynth(default_preset="quantum")

# === Step 1: Build LexiconWord candidates from PronunciationDict ===
print("Building English LexiconWord candidates from PronunciationDict...")
pdict = get_pronunciation_dict()

# Force load, then access internal dicts
pdict._ensure_loaded()
english_lexicon = []

# English words (CMU dict path)
for word, coords in pdict._english.items():
    if coords and len(coords) >= 1:
        lw = LexiconWord(
            sanskrit=word,
            meanings=(word,),
            coords=tuple(coords),
            packed_hex=f"{hash(word) & 0xFFFFFFFF:08x}",
        )
        english_lexicon.append(lw)

# Also add Sanskrit words (Gita lexicon)
for word, coords in pdict._sanskrit.items():
    if coords and len(coords) >= 1:
        lw = LexiconWord(
            sanskrit=word,
            meanings=(word,),
            coords=tuple(coords),
            packed_hex=f"{hash(word) & 0xFFFFFFFF:08x}",
        )
        english_lexicon.append(lw)

print(f"  English lexicon: {len(english_lexicon)} words")

# === Step 2: Audio → coords → 7D rank_words against English lexicon ===
print()
print("Loading audio...")
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)
print(f"  Segments: {len(segments)}")

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = set(EXPECTED.lower().split())

print()
print("=" * 70)
print("7D RESONANCE RANKING — English pronunciation dictionary")
print("=" * 70)

words_out = []
for si, seg in enumerate(segments):
    ms_s = seg.start * 10
    ms_e = seg.end * 10

    raw_coords = stream_to_rama(seg.frames)
    if not raw_coords:
        continue

    coords = _stable_coords(raw_coords, min_run=2)
    if not coords or len(coords) < 1:
        coords = _dedup_coords(raw_coords)
    if not coords:
        continue

    # Get attractor from coord pattern
    seed = sum(coords) * 7 + len(coords)
    attractor = synth.transform(seed)

    # Pre-filter candidates by first coord (± 3) and length (± 50%)
    coord_len = len(coords)
    first_c = coords[0]
    candidates = []
    for lw in english_lexicon:
        # Length filter
        wlen = len(lw.coords)
        if wlen == 0:
            continue
        ratio = min(wlen, coord_len) / max(wlen, coord_len)
        if ratio < 0.3:
            continue
        # First coord proximity (optional, for speed)
        candidates.append(lw)

    if not candidates:
        continue

    # 7D ranking
    ranked = rank_words(
        input_coords=coords,
        candidates=candidates,
        input_attractor=attractor,
        top_n=5,
    )

    if ranked:
        best = ranked[0]
        word = best.sanskrit  # English word stored in sanskrit field
        score = best.total_score

        in_expected = "✓" if word.lower() in expected_words else " "
        print(f"  [{ms_s:5d}-{ms_e:5d}ms] {word:20s} score={score:.4f} {in_expected}  "
              f"coords={coords[:5]}")
        if len(ranked) > 1:
            r2 = ranked[1]
            print(f"  {'':21s}  2nd: {r2.sanskrit:15s} score={r2.total_score:.4f}")

        words_out.append(word)

correct = sum(1 for w in words_out if w.lower() in expected_words)
total = len(words_out)
print(f"\n7D TRANSCRIPT: {' '.join(words_out)}")
print(f"EXPECTED:      {EXPECTED}")
print(f"\nCorrect: {correct}/{total} ({correct/max(1,total)*100:.0f}%)")
