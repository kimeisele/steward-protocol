# SHABDA RECOGNITION — Research

## THE PROBLEM

The Shabda Decoder should transcribe real audio to text.
Current output for Prabhupada saying "Eh... not exactly. But I came to preach...":
→ "of eh smashed etat say message am ekena..."  (garbage)

## ROOT CAUSE ANALYSIS

### What already exists (PRODUCTION, CLEAN):

1. **`shabda_intake.py`** — audio → uint32 frames (RMS, Varga, F0, Centroid)
2. **`shabda_processor.py`** — frames → RAMA coords via lookup tables
   - `frame_to_rama()`: Element → SoundClass → SubIndex → exact coord
   - Uses `_ELEMENT_VARGA_TO_COORDS` precomputed table (NOT if-else)
   - Uses `COORD_SUB` from substrate (data register, NOT weights)
3. **`phonetic_bridge.py`** — ARPABET↔RAMA↔Varga↔Sthana mappings (data tables)
4. **`shabda_translation.py` (research)** — VibrationSignature model (universal)

### What the decoder does WRONG:

1. **Duplicates shabda_processor** — `score_frame()` reinvents phoneme detection
   with hand-tuned weights, if-else branches, synthetic MFCC prototypes.
   This is Web 2.0 approach. shabda_processor already does it protocol-based.

2. **Dictionary mismatch** — Audio coords come from `score_frame()` (ARPAbet path)
   but dictionary words encoded via `encode_text()` (letter-by-letter IAST path).
   Two different RAMA dialects. CMU dict fix helped but didn't solve it.

3. **No data register for MFCC** — Prototypes are SYNTHETIC (generated from
   formant synthesis). Max 0.44 cosine similarity to real speech. Useless.
   Should be trained once from real labeled audio and stored as a data file
   (like `rama_lexicon.json`).

## THE RIGHT QUESTIONS

### Q1: Can we use `shabda_processor.stream_to_rama()` as-is?

It's the clean, existing path. frame_to_rama() narrows 49→1 using:
- Varga (from centroid) → 10 candidates
- Sound class (from RMS/F0 transitions) → 2-5 candidates
- Sub-index (from Sthana detection) → 1 candidate

BUT: its coords reflect ARTICULATORY POSITION, not specific phoneme identity.
Two different words with similar spectral profiles → similar coords.
This is fine for resonance (same varga = similar meaning), but NOT for
transcription (we need EXACT phoneme identity).

### Q2: What additional signal do we need for phoneme identity?

The missing piece is **MFCC** — 13 coefficients that capture the spectral
envelope (the "fingerprint" of each phoneme). But the prototypes must be
REAL, not synthetic.

**Data register approach**: 
- Use labeled audio datasets (e.g., TIMIT, or our own from prabhupada-talk.wav
  aligned with known transcript via forced alignment)
- For each of 39 ARPAbet phonemes, collect N real MFCC vectors
- Average them → 39 × 13 integer matrix = ~2KB of data
- Store as JSON or Python constant (like `SANSKRIT_PHONEME_MAP`)
- One-time computation, zero runtime cost

### Q3: How does this fit the architecture?

```
shabda_intake.py        →  uint32 frames + MFCC vectors (ALREADY extracted)
shabda_processor.py     →  RAMA coords (articulatory, coarse)
NEW: phoneme_register   →  MFCC lookup table (39 × 13, trained from data)
shabda_decoder.py       →  RAMA + MFCC → dictionary match → transcript
```

The phoneme register is a DATA FILE, not code. No if-else. No weights.
Just `cosine_similarity(frame_mfcc, register[phoneme])` → best match.

### Q4: Language-agnostic design?

The VibrationSignature model in shabda_translation.py already shows the way:
- Every sound = (articulation, voicing, frequency, duration)
- This is UNIVERSAL — works for ANY language
- MFCC is also language-agnostic (spectral envelope doesn't care about language)
- The register can be extended: start with English (CMU dict), add Hindi, Sanskrit, etc.

## RESEARCH PLAN

1. **Experiment 1**: Use `shabda_processor.stream_to_rama()` directly in decoder
   (remove the spaghetti `score_frame()` path). Compare output.

2. **Experiment 2**: Build real MFCC register from labeled audio.
   - Option A: Use forced alignment on prabhupada-talk.wav (we know the transcript)
   - Option B: Synthesize phoneme audio with festival/espeak TTS → extract MFCCs
   - Option C: Use TIMIT dataset (standard, but requires download)

3. **Experiment 3**: Combine shabda_processor RAMA coords + MFCC register.
   - RAMA gives coarse position (element/varga)
   - MFCC gives fine identity (specific phoneme)
   - Together: full phoneme identification without if-else

4. **Production integration**: Replace `score_frame()` with register lookup.
   Clean, data-driven, protocol-based. No hand-tuned weights.
