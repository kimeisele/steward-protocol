# SHABDA RECOGNITION — Key Finding

## THE ROOT CAUSE: Three Coordinate Dialects

The RAMA space (0-48) is used by THREE paths that produce DIFFERENT coords
for the SAME sound:

| Path | "not" | "of" | "the" | Used by |
|------|-------|------|-------|---------|
| `encode_text()` (letter) | (35,12,31) | (12,37) | (32,10) | Old dictionary |
| CMU→ARPABET→RAMA | (35,5,31) | (0,44) | (34,0) | New dictionary |
| `stream_to_rama()` (audio) | (32,3,1,46,45,46) | ? | ? | Audio path |

**All three are in 0-48 RAMA space, but they disagree on what each coord means.**

### Why they disagree:

1. **`encode_text()`** — maps LETTERS one by one. "o" → coord 12 (vowel O in IAST).
   This is a SPELLING-based encoding, not phonetic.

2. **CMU→ARPABET→RAMA** — maps PHONEMES. "of" = /AH V/ → (0, 44).
   coord 0 = AH (short A), coord 44 = V (labial semivowel).
   This is PHONETICALLY correct.

3. **`stream_to_rama()` (audio)** — maps ACOUSTIC FEATURES via lookup tables.
   Uses centroid→varga, RMS→sound_class, F0→sthana.
   Produces coords based on WHERE in the mouth, not WHAT phoneme.
   coord 32 = dental+mahaprana (aspirated dental consonant) — but the 
   speaker might be saying ANY sound with that centroid/RMS pattern.

### The fix:

**Audio must produce the SAME coords as CMU→ARPABET→RAMA.**

This means: `audio frame → ARPAbet phoneme → ARPABET_TO_RAMA[phoneme]`.

The missing step is `audio frame → ARPAbet phoneme`. This requires a
**phoneme classifier** — not if-else weights, but a DATA REGISTER of
what each phoneme sounds like (its MFCC fingerprint).

## THE SOLUTION: MFCC Phoneme Register

### What it is:
A precomputed lookup table: `phoneme → MFCC prototype vector (13 ints)`.
39 phonemes × 13 coefficients = 507 integers = ~2KB.

### How to build it:
1. Get labeled audio with known phoneme boundaries (forced alignment)
2. For each phoneme occurrence, extract MFCC from that audio region
3. Average all MFCCs for the same phoneme → prototype
4. Store as a JSON/Python data file (like rama_lexicon.json)

### How to use it:
```python
# Per frame:
frame_mfcc = extract_mfcc(audio_frame, sr)  # already exists!
best_phoneme = max(REGISTER, key=lambda p: cosine_sim(frame_mfcc, REGISTER[p]))
rama_coord = ARPABET_TO_RAMA[best_phoneme]
```

No if-else. No weights. Pure data-driven lookup.
The register is trained ONCE and stored as a data file.

### Data sources for building the register:
- **Option A**: Forced alignment on prabhupada-talk.wav 
  (we know the transcript, align phoneme boundaries, extract MFCCs)
- **Option B**: Use espeak/festival TTS to synthesize each phoneme
  at multiple pitches, extract MFCCs, average
- **Option C**: Use TIMIT dataset (standard labeled speech corpus)

### Integration:
```
shabda_intake.py     →  uint32 frames + MFCC vectors
phoneme_register.json →  39 × 13 trained MFCC prototypes  
shabda_decoder.py    →  cosine_sim(frame_mfcc, register) → ARPAbet → ARPABET_TO_RAMA → dict match
```

This replaces ALL of:
- score_frame() with its hand-tuned weights
- The sound_class/varga/voicing/formant if-else tree
- The synthetic MFCC prototypes

With a single `argmax(cosine_similarity)` over a data register.

## EXPERIMENT RESULTS (8 experiments run)

| # | Method | Accuracy | Notes |
|---|--------|----------|-------|
| 1 | `stream_to_rama()` raw | 0% | Articulatory coords, wrong dialect |
| 2 | Coord comparison | N/A | Proved three dialects are incompatible |
| 3 | Built MFCC register (30 phonemes) | N/A | Real MFCCs from speech |
| 4 | Filled to 39 phonemes | N/A | Interpolation for missing |
| 5 | MFCC register classification | 0% | Bad alignment = bad prototypes |
| 6 | `stream_to_rama` + `encode_text` dict | 0% | Elements match but coords too long |
| 7 | `stream_to_rama` + `_stable_coords` | 3% | Stability filter too aggressive |
| 8 | Smoothed features + majority vote | 0% | Coords collapse to 3-4 values |

## THE REAL ARCHITECTURAL GAP

**The recognition step (audio frame → specific phoneme) cannot be solved
with lookup tables, if-else trees, or hand-tuned weights.**

Why:
- 4 acoustic features (RMS, varga, F0, centroid) carry ~3 bits per frame
- Need ~5-6 bits to identify 39 phonemes
- MFCC has 13 dimensions (enough bits) but requires REAL prototypes
- Real prototypes require ACCURATE phoneme-level alignment (±5ms)
- Accurate alignment requires... a phoneme recognizer (circular!)

## WHAT ACTUALLY WORKS IN SPEECH RECOGNITION

Every successful speech recognition system uses ONE of:

1. **GMM-HMM** (classical): Gaussian Mixture Models for phoneme emission,
   Hidden Markov Models for sequencing. Trained on 100+ hours of labeled speech.
   Small models (~5MB). This is what HTK/Kaldi do.

2. **Neural CTC** (modern): Small neural network (Conv1D + CTC loss).
   Can be tiny (<1MB). Trained on labeled speech.
   This is what DeepSpeech/wav2letter do at minimum.

3. **Template matching with DTW** (simplest): Dynamic Time Warping
   against known word templates. No training needed, but requires
   one example of each word. Very limited vocabulary.

## PROPOSAL: Minimal Viable Phoneme Register

The cleanest path that fits the architecture:

1. **Use a small pre-trained model** to build the MFCC register ONCE.
   Not at runtime — at BUILD TIME (like `rama_lexicon.json`).
   Run a tiny phoneme recognizer on ~10 minutes of labeled speech,
   extract per-phoneme MFCC centroids, save as JSON.

2. **Alternatively**: Use Montreal Forced Aligner (MFA) — an open-source
   tool that gives phoneme-level timestamps for any audio + transcript.
   Run MFA once → get precise phoneme boundaries → extract real MFCCs
   → build register. No model needed at RUNTIME.

3. **At runtime**: Pure data register lookup. `cosine_sim(frame, register)`.
   No neural network. No external dependency. Just a 2KB JSON file.

This preserves the architecture: data register (like `rama_lexicon.json`),
not code logic. Build-time computation, zero runtime cost.
