"""
EXPERIMENT 19: Run the ACTUAL ShabdaDecoder.transcribe()
=========================================================

All previous experiments used stream_to_rama() (shabda_processor path).
But the real decoder uses _frames_to_phoneme_coords() which goes:
  frame → score_frame(mfcc, f1, f2) → top-1 ARPAbet → ARPABET_TO_RAMA → RAMA coord

This is a DIFFERENT path. Both audio and dict use ARPABET_TO_RAMA,
so coords should align. Let's see what the actual decoder produces.
"""
import sys; sys.path.insert(0, ".")
import logging

logging.basicConfig(level=logging.INFO)

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake
from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")

print(f"Audio: {stream.duration_ms}ms, {len(stream.frames)} frames")
print(f"Has raw samples: {stream.raw_samples is not None}")
print(f"Has MFCC frames: {stream.mfcc_frames is not None}")
print()

# Run the actual decoder
decoder = ShabdaDecoder(language_preference="english")
transcript = decoder.transcribe(stream)

EXPECTED = "Eh not exactly But I came to preach the gospel of Krishna consciousness and fortunately I met some enthusiastic young boys and girls"
expected_words = EXPECTED.lower().split()

print("=" * 70)
print("ACTUAL SHABDA DECODER OUTPUT")
print("=" * 70)
for w in transcript.words:
    in_expected = "✓" if w.word.lower() in set(expected_words) else " "
    print(f"  [{w.start_ms:5d}-{w.end_ms:5d}ms] {w.word:15s} conf={w.confidence:.3f} "
          f"lang={w.language:8s} {in_expected}  coords={w.rama_coords[:6]}")

print(f"\nDECODER TRANSCRIPT: {transcript.text}")
print(f"EXPECTED:           {EXPECTED}")

# Count matches
decoder_words = [w.word.lower() for w in transcript.words]
exact_position = sum(1 for i, w in enumerate(decoder_words)
                     if i < len(expected_words) and w == expected_words[i])
in_vocab = sum(1 for w in decoder_words if w in set(expected_words))
total = len(decoder_words)

print(f"\nExact position: {exact_position}/{min(total, len(expected_words))}")
print(f"In expected:    {in_vocab}/{total}")
