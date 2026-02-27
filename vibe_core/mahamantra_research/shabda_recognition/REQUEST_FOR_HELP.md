# REQUEST FOR HELP: Shabda Decoder — Deterministic Speech-to-Text

## TL;DR

We're building a **deterministic speech recognizer** (no ML, no APIs) that maps audio
to words via phonetic algebra. After 22 experiments over multiple sessions, we have
**0% word accuracy**. The audio feature extraction works. The dictionary/scoring works.
The bridge between them is broken. We need a fresh pair of eyes.

---

## 1. WHAT WE'RE BUILDING

A speech-to-text decoder in Python that:
- Takes a WAV file (e.g. Prabhupada speaking English)
- Extracts acoustic features per 10ms frame (RMS, varga, F0, centroid, F1/F2 formants, 13 MFCCs)
- Identifies phonemes from acoustic features
- Maps phoneme sequences to words via a pronunciation dictionary (CMU dict, 123K words)
- Outputs a transcript

**No neural networks.** Pure signal processing + phonetic algebra + dictionary lookup.

The system is part of a larger "Mahamantra" framework that has extensive infrastructure
for phonetic encoding, resonance scoring, and coordinate-based matching — all of which
works perfectly for text-to-text. The gap is audio-to-text.

---

## 2. THE CODEBASE (what exists, what works)

### Audio Intake — WORKS PERFECTLY
**File:** `vibe_core/mahamantra/sound/shabda_intake.py`

```
ShabdaIntake.process_file("audio.wav") → ShabdaStream
  .frames:       tuple of uint32 (packed: RMS|Varga|F0|Centroid per 10ms)
  .raw_samples:  numpy array of PCM samples
  .mfcc_frames:  tuple of 13-int MFCC vectors per frame
  .sample_rate:  44100
  .duration_ms:  total length
```

Verified: RMS, F0, centroid, varga all extract correctly. F1/F2 formants extract
at 78-100% success rate. MFCCs are 13 coefficients per frame.

### Phonetic Encoding (text → coordinates) — WORKS PERFECTLY
**File:** `vibe_core/mahamantra/substrate/encoding/phonetic_bridge.py`

```python
ARPABET_TO_RAMA: Dict[str, int]  # 39 ARPAbet phonemes → RAMA coords (0-48)
# "B" → 38, "AH" → 0, "T" → 31   so "but" = (38, 0, 31)
```

**File:** `vibe_core/mahamantra/sound/shabda_decoder.py`

```python
PronunciationDict  # CMU dict: 123K words → ARPAbet → RAMA coord sequences
  .lookup("but") → (38, 0, 31)
  .lookup("came") → (16, 10, 40)
  .candidates_for_segment(first_coord, length) → [(word, coords), ...]
```

### Resonance Scoring — WORKS PERFECTLY (for text-to-text)
**File:** `vibe_core/mahamantra/substrate/encoding/resonance_ranker.py`

7-dimensional scoring: element + harmonic + shruti + varga + attractor + HKR + phoneme_attractor.
Proven discrimination on 4000+ word Gita lexicon (scores 0.78-0.88).

### The Decoder — BROKEN
**File:** `vibe_core/mahamantra/sound/shabda_decoder.py`

```
ShabdaDecoder.transcribe(stream) → Transcript
  1. segment_stream(frames) → word-length Segments (by silence/energy dips)
  2. Per segment: _frames_to_phoneme_coords(frames, raw_samples)
     a. Per frame: extract F1/F2, call score_frame(packed, f1, f2)
     b. score_frame: score against 39 PhonemeTemplates → top-1 ARPAbet
     c. ARPAbet → ARPABET_TO_RAMA → RAMA coord
     d. Majority-vote smoothing (window=5)
  3. _stable_coords(raw_coords, min_run=3) → deduplicated coords
  4. Match coords against PronunciationDict via _score_candidate (edit distance)
  5. Best match → TranscriptWord
```

**Result:** Complete nonsense. "at eh smashed etat see machine am ekena..."
Expected: "Eh not exactly but I came to preach the gospel..."

---

## 3. THE THREE BUGS WE FOUND (and fixed, but it wasn't enough)

### BUG 1: Formant templates are for wrong speaker
`_VOWEL_FORMANTS` had textbook American English values (Peterson & Barney 1952).
Speaker is Prabhupada (Bengali/Hindi accent). F2 is systematically +350 Hz higher.

**Evidence** (experiment 21, japa calibration):
```
Syllable  | Prabhupada F2 | Textbook F2 | Diff
ha  (/a/) |    1543       |    1200     | +343
kṛ  (/ṛ/) |    1672       |    1350     | +322
ṣṇa (/a/) |    1656       |    1200     | +456
```

**Fix applied:** Shifted all F2 centers +350 Hz. AH vowel now correctly detected
in "but" (frames 4-6 of segment 3 correctly return AH with score 0.87-0.91).

### BUG 2: Formant scoring formula has high-F2 bias
```python
# OLD (biased):
f2_err = abs(f2 - t.f2_center) / max(t.f2_center, 1)
# For f2=1650: AH(1200) err=0.375, EY(2200) err=0.25 → EY wins WRONGLY

# FIXED:
f2_err = abs(f2 - t.f2_center) / 1500.0  # absolute Hz / fixed range
```

### BUG 3: Stops confused with same-varga continuants
B→M, T→S, K→NG. `score_frame()` scores each 10ms frame independently.
A stop consonant is a 10-20ms burst — 1-2 frames — indistinguishable from
a nasal or fricative at the same articulation point in a single frame.

**Fix applied:** Added `prev_rms` parameter to `score_frame()`. When prev_rms < 20
and current rms > 20, boost stop templates, penalize nasals/continuants.

### Result after all 3 fixes: Still 0% word accuracy.

---

## 4. WHY THE FIXES AREN'T ENOUGH (the structural problem)

The decoder architecture classifies **each 10ms frame independently** into one
of 39 phonemes, then reconstructs words from the phoneme sequence. This is
fundamentally wrong because:

1. **Consonants are 1-3 frames (10-30ms).** Too short for reliable per-frame
   classification. Multiple consonants at the same articulation point (B vs M,
   T vs S, K vs NG) produce nearly identical single-frame features.

2. **Varga pre-filter kills coverage.** `score_frame()` only checks templates
   matching the frame's varga ± 1 neighbor. If centroid gives varga=1 (palatal),
   throat vowels like AH (varga=0) might be excluded entirely.

3. **Scoring weights are too coarse.** The formant path uses 5 signals at
   0.15 weight each + formant at 0.40. For consonants (no formant), discrimination
   relies on 0.60 of very blunt features (voicing yes/no, centroid range, RMS class).

4. **Majority-vote smoothing destroys consonants.** Window=5 means a 2-frame
   consonant gets outvoted by surrounding vowels.

5. **Segment boundaries cut through phonemes.** Segmentation by silence/energy dip
   means onset consonants (B in "but") are often in the silence gap between segments,
   lost to the subsequent word's analysis.

### The frame-by-frame trace for "but" (B-AH-T):

```
Frame  RMS  Varga  F0    Cent  F1   F2    Winner  Expected
f0     145  1      1045  156   363  1606  ER      (onset B)
f1     197  1      1130  144   348  1651  ER      (transition)
f2     236  1      1185  120   390  1724  ER      (transition)
f3     230  1      1182  137   413  1736  ER      (transition)
f4     214  0      1148  113   408  1202  AH ✓    (vowel core)
f5     196  0      1136  107   390  1778  AH ✓    (vowel core)
f6     190  0      1119   85   379  1667  AH ✓    (vowel core)
f7     161  4      1065   63   342  1691  UH      (B release, should be B)
f8     136  4      1000   56   301  1626  UH      (should be B/vowel transition)
f9     104  4       944   56   249  1661  M       (should be B region)
f10     82  4       920   79   195  1625  V       (coda)
f11     58  2       859  217     0  1631  R       (T onset, no F1)
f12     46  3       896  354     0  1617  S       (should be T)
f13     48  3       982  403     0  1626  S       (should be T)
```

Stable coords: `(ER, AH, UH, S)` → dict expects `(B, AH, T)`.
Only AH is correct. B and T are invisible to per-frame classification.

---

## 5. WHAT WE HAVE THAT COULD HELP

### Real calibration data
`shabda_bridge.json` — 638 frames of labeled Prabhupada japa with per-syllable
acoustic signatures. 6 syllables: ha, re, kṛ, ṣṇa, rā, ma. Includes avg F1/F2,
RMS, F0, centroid, and RAMA coordinates. **Only ground truth in the codebase.**

### MFCCs (unused by actual decoder path)
`ShabdaStream.mfcc_frames` — 13 MFCC coefficients per 10ms frame, already extracted.
MFCCs encode the full spectral envelope (consonants AND vowels) in a compact vector.
The decoder's `_frames_to_phoneme_coords()` path does NOT use them — it only uses
F1/F2 formants. The MFCC path in `score_frame()` uses synthetic prototypes that
don't match real audio (confirmed experiment 15).

### Existing resonance infrastructure (unused for audio)
- **MahaCompression**: any data → deterministic 32-bit seed
- **MahaModularSynth**: seed → 16-step transform → attractor (proven discriminative, exp 10)
- **Antaranga**: 512-slot resonance grid with collision/prana accumulation
- **ResonanceRanker**: 7D scoring (proven for text, 0.78-0.88 scores)
- **LotusArrayInt**: 65K-slot O(1) lookup

None of these are used in the audio→text path. The decoder bypasses all of it.

---

## 6. APPROACHES CONSIDERED BUT NOT YET TRIED

### A. Segment-level MFCC + Dynamic Time Warping (DTW)
Instead of per-frame phoneme classification, compare the MFCC trajectory of a
whole audio segment against reference MFCC trajectories for words. Classic
template-matching ASR (pre-deep-learning, proven to work for small vocabularies).
**Problem:** Need reference MFCC templates for dictionary words. Could bootstrap
from the japa data or from a small labeled corpus.

### B. MahaCompression as shared address space
Both audio features (e.g., segment-average MFCCs) and text go through
MahaCompression → seed → MahaSynth → attractor → slot address. Compare
attractor patterns instead of coordinate sequences.
**Advantage:** Uses existing infrastructure. Shared space by construction.
**Problem:** MahaCompression was designed for text/bytes, not acoustic features.
Unclear if it preserves phonetic similarity (similar sounds → similar seeds).

### C. Antaranga as acoustic memory
Feed audio frames into Antaranga slots (collision → prana accumulation).
The resulting prana distribution = acoustic imprint. Pre-compute reference
imprints for dictionary words. Match by cosine similarity.
**Problem:** Experiment 14 showed audio and reference hit DISJOINT slot spaces
(audio: slots 300-500, reference: slots 12-213). Need shared addressing.

### D. Hybrid: formant vowels + transition-based consonants
Keep the (now working) formant vowel identification. For consonants, detect
transitions: varga change = articulation change = consonant boundary. Use the
varga at the transition point + voicing to narrow down the consonant.
**Problem:** Consonant identification still relies on coarse features.

---

## 7. CONSTRAINTS

- **No ML models.** No TensorFlow, no PyTorch, no pre-trained weights.
- **No external APIs.** No Whisper, no Google STT.
- **Deterministic.** Same input → same output, always.
- **Python only.** No C extensions beyond numpy/scipy.
- **Use existing infrastructure** where possible (Mahamantra framework).
- **Speaker:** Prabhupada (Bengali/Hindi accent, known acoustic profile from japa).
- **Test audio:** `temp/prabhupada-talk.wav` (14 seconds of English speech).
- **Expected transcript:** "Eh not exactly but I came to preach the gospel of Krishna
  consciousness and fortunately I met some enthusiastic young boys and girls"

---

## 8. KEY FILES

```
vibe_core/mahamantra/sound/
  shabda_intake.py          # Audio → features (WORKS)
  shabda_decoder.py         # Features → transcript (BROKEN — this is what needs fixing)
  shabda_processor.py       # Alternative audio→RAMA path (NOT used by decoder)
  shabda_vibration.py       # Audio→VibrationSignature (experimental, not integrated)

vibe_core/mahamantra/substrate/encoding/
  phonetic_bridge.py        # ARPABET_TO_RAMA, varga/sthana mappings
  resonance_ranker.py       # 7D scoring (works for text)

vibe_core/mahamantra/substrate/cell_system/
  antaranga.py              # 512-slot resonance grid (unused for audio)

vibe_core/mahamantra/substrate/algorithm/
  maha.py                   # MahaModularSynth (proven discriminative)

vibe_core/mahamantra/data/
  shabda_bridge.json        # Ground truth: Prabhupada japa acoustic signatures

vibe_core/mahamantra_research/shabda_recognition/
  experiment_*.py           # 22 experiments (all in repo)
  TECH_MAP.md               # Detailed technical map of all findings
```

---

## 9. THE QUESTION

Given:
- Working audio feature extraction (F1/F2 formants, MFCCs, RMS, F0, centroid)
- Working pronunciation dictionary (123K words → RAMA coord sequences)
- Working resonance scoring (7D, proven for text)
- Speaker-calibrated formant templates (from japa ground truth)
- 0% accuracy on frame-by-frame phoneme classification

**How should we bridge audio features → word recognition?**

The per-frame phoneme classification approach is structurally broken for consonants.
We need a different strategy for the audio→word mapping that:
1. Handles consonants (which are too short for per-frame classification)
2. Uses the acoustic features we already extract well
3. Ideally leverages the existing Mahamantra resonance infrastructure
4. Produces RAMA coords compatible with the pronunciation dictionary

What would a senior audio/DSP engineer do here?
