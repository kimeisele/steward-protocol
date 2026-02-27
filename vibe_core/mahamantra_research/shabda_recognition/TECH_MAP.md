# SHABDA RECOGNITION — Full Tech Map

## WHAT EXISTS (Surveyed)

### ENCODING (Text → Coordinates) — COMPLETE ✓

| Layer | File | What it does |
|-------|------|--------------|
| **VibrationSignature** | `substrate/phonetics/shabda.py` | `(articulation, voicing, freq, duration)` → `signature_id`. Universal model. |
| **SANSKRIT_PHONEME_MAP** | `substrate/phonetics/shabda.py` | 40+ phonemes → VibrationSignature. Precomputed lookup table. |
| **text_to_vibration()** | `substrate/phonetics/shabda.py` | Text → sequence of VibrationSignatures. |
| **encode_text()** | `substrate/encoding/phonetic_encoder.py` | Any text → RAMA coords (0-48). Letter-by-letter. |
| **ARPABET_TO_RAMA** | `substrate/encoding/phonetic_bridge.py` | ARPAbet phoneme → RAMA coord. 39 mappings. |
| **PhoneticTensor** | `substrate/encoding/phonetic_bridge.py` | Varga/Sthana vectors per phoneme. |

### RESONANCE (Coordinates → Meaning) — COMPLETE ✓

| Layer | File | What it does |
|-------|------|--------------|
| **ResonanceRanker** | `substrate/encoding/resonance_ranker.py` | 7D scoring: element + harmonic + shruti + varga + attractor + HKR + phoneme_attractor |
| **basin_map** | `substrate/core/basin_map.py` | COORD_BASIN[0..48], COORD_HKR[0..48], 7 attractor basins |
| **MahaResonator** | `substrate/resonance/resonator.py` | Seed → attractor via iterated Maha Algorithm |
| **element_walk** | `substrate/pancha_walk.py` | RAMA coords → Element journey (PRTHVI/JALA/AGNI/VAYU/AKASH) |
| **walk_distance** | `substrate/pancha_walk.py` | Compare two coord sequences by element histogram |

### AUDIO (Sound → Features) — COMPLETE ✓

| Layer | File | What it does |
|-------|------|--------------|
| **ShabdaIntake** | `sound/shabda_intake.py` | Audio → uint32 frames (RMS, Varga, F0, Centroid) + MFCC 13D |
| **extract_formants** | `sound/shabda_intake.py` | Audio frame → F1, F2 (now fixed: 95% yield) |
| **extract_mfcc** | `sound/shabda_intake.py` | Audio frame → 13 MFCC coefficients |

### AUDIO → COORDINATES — PARTIAL, WRONG APPROACH

| Layer | File | What it does | Problem |
|-------|------|--------------|---------|
| **stream_to_rama()** | `sound/shabda_processor.py` | Frames → RAMA coords via lookup tables | Different dialect than dictionary |
| **score_frame()** | `sound/shabda_decoder.py` | Frame → ARPAbet via if-else weights | Spaghetti, can't discriminate |
| **_frames_to_phoneme_coords()** | `sound/shabda_decoder.py` | Frames → RAMA via score_frame | Bypasses all resonance infrastructure |

### COGNITION — EXISTS, NOT USED FOR AUDIO

| Layer | File | What it does |
|-------|------|--------------|
| **MahaBuddhi** | `substrate/buddhi.py` | Discriminative intelligence. input → Lotus VM → MahaComposition → BuddhiResult |
| **Sravanam** | `dharma/kumaras/sravanam.py` | Fractal cell scanner. "Hearing" = first step. Currently scans code, not audio. |
| **Chamber** | `substrate/cell_system/chamber.py` | 108 cells, resonance-based processing, DIW modulation |
| **Antaranga** | `substrate/cell_system/antaranga.py` | 16KB contiguous RAM, zero-copy slot access, collision logic |

---

## THE GAP

### What's missing: Audio → VibrationSignature (DECODING)

```
ENCODING (exists):    Text → VibrationSignature → signature_id → RAMA coord
                      Text → encode_text() → RAMA coords
                      Text → CMU dict → ARPAbet → ARPABET_TO_RAMA → RAMA coords

DECODING (missing):   Audio → VibrationSignature → ???
                      Audio frame → (articulation, voicing, freq, duration) → signature_id

MATCHING (exists):    7D ResonanceRanker — element + harmonic + shruti + varga + attractor + HKR + phoneme_attractor
                      But ONLY used for text→text matching, not audio→text
```

The **VibrationSignature** has 4 dimensions: `(articulation, voicing, freq, duration)`.
From audio we can extract:
- **articulation** → centroid maps to articulation point (KANTHA/TALU/MURDHA/DANTA/OSHTHA)
- **voicing** → F0 present/absent + RMS + centroid → 4 voicing types
- **freq** → F0 fundamental frequency → maps to NADI_RESONANCE multiples
- **duration** → frame count → maps to AKSARA ratio

This means: **we CAN build Audio → VibrationSignature directly!**
The audio features we already extract MAP to the VibrationSignature fields.

---

## THE RADIO ANALOGY

Same audio → MULTIPLE decompositions (like different radio frequencies):

1. **VibrationSignature stream** — (articulation, voicing, freq, duration) per phoneme
2. **Element walk** — PRTHVI/JALA/AGNI/VAYU/AKASH journey
3. **Basin trajectory** — which of 7 attractor basins each phoneme falls in
4. **HKR proportion** — Hare/Krishna/Rama energy distribution
5. **Phoneme attractor charge** — 5-bin histogram of convergence targets

Each "frequency" gives a DIFFERENT view of the same audio.
The 7D ResonanceRanker already combines these for TEXT matching.
We need to extract them from AUDIO and use the SAME ranker.

---

## THE DESIGN

### Step 1: Audio → VibrationSignature (the missing decoder)

```python
def frame_to_vibration(packed: int, prev_packed: int = 0) -> VibrationSignature:
    """Audio frame → VibrationSignature. The INVERSE of text_to_vibration."""
    rms, varga, f0_x10, centroid_100 = unpack_frame(packed)
    
    # Articulation: centroid → 5 points (same as varga mapping)
    articulation = ArticulationPoint(varga)  # varga IS articulation
    
    # Voicing: F0 + RMS + centroid → 4 types (same as _audio_to_sthana)
    voicing = _audio_to_voicing(rms, f0_x10, centroid_100)
    
    # Frequency: F0 → NADI_RESONANCE multiples
    freq = _f0_to_nadi_freq(f0_x10)
    
    # Duration: accumulated from consecutive same-articulation frames
    duration = 1  # per-frame, accumulated later
    
    return VibrationSignature(articulation, voicing, freq, duration)
```

### Step 2: Audio VibrationSignature → Multi-dimensional fingerprint

For each audio segment:
- Convert frame sequence → VibrationSignature sequence
- Accumulate durations (consecutive same articulation+voicing → one phoneme)
- Compute: signature_id sequence, element walk, basin trajectory, HKR proportion

### Step 3: Match using EXISTING 7D ResonanceRanker

For each dictionary word, we already have its RAMA coords.
From RAMA coords we already compute 7D features (element, harmonic, shruti, varga, attractor, HKR, phoneme_attractor).
From audio VibrationSignatures we compute the SAME 7D features.
Match using ResonanceRanker's existing scoring — NO new scoring logic needed.

### What this gives us:

- **No if-else spaghetti** — uses existing protocol-based infrastructure
- **No hand-tuned weights** — ResonanceRanker weights are derived from SSOT
- **Language-agnostic** — VibrationSignature works for any language
- **Multiple frequencies** — 7 dimensions of matching, not 1
- **Data-register approach** — all mappings are precomputed lookup tables
- **Buddhi-compatible** — BuddhiResult can evaluate audio cognition alignment

### Files to create/modify:

1. **NEW: `sound/shabda_vibration.py`** — `frame_to_vibration()`, the missing decoder
2. **MODIFY: `sound/shabda_decoder.py`** — Use VibrationSignature + ResonanceRanker instead of score_frame
3. **NO NEW WEIGHTS** — Everything derived from existing infrastructure

---

## SESSION 4 FINDINGS (Experiments 9-14)

### What WORKS

| Component | Result |
|-----------|--------|
| **frame_to_vibration()** | Produces real VibrationSignatures from audio. Articulation, voicing, freq, duration correctly extracted. |
| **MahaModularSynth** | Experiment 10: Quantum preset (mod 137) gives rich attractor landscape. Different words → different attractor sequences. 100% match on 13-word vocab. |
| **7D ResonanceRanker (smaranam)** | Experiment 12: 0.78-0.88 scores, real discrimination between Gita words. The ranker IS production-grade. |
| **Antaranga as drum membrane** | Experiment 14: Collision+prana accumulation works. Active slots, prana distribution, top-K pattern are meaningful per-segment fingerprints. |

### What DOESN'T WORK

| Problem | Evidence | Root Cause |
|---------|----------|------------|
| **Synth histogram blur** | Exp 11: All words 0.93-0.99 cosine similarity (degenerate) | Histogram loses sequence order. signature_id values too large for mod space. |
| **VibrationSignature → RAMA coords** | Exp 9: `sig_id % 49` gives different coords than `encode_text()` for same word | signature_id was NEVER designed to project into RAMA via modulo. Different spaces. |
| **7D ranker on English** | Exp 13: 3% accuracy. Mostly returns Sanskrit words. | Gita lexicon dominates (4127 Sanskrit vs ~2000 English). Coord dialect mismatch persists. |
| **Antaranga slot overlap** | Exp 14: Audio hits slots 300-500, reference hits 12-213. Zero cosine. | Audio features and RAMA coords span DIFFERENT numeric spaces. |

### THE REAL ROOT CAUSE (confirmed across 14 experiments)

**The acoustic→symbolic translation is the fundamental gap.**

```
AUDIO SPACE:   RMS (0-255), F0 (0-4000), centroid (0-40000), varga (0-4)
SYMBOLIC SPACE: RAMA coords (0-48), elements (0-4), vargas (0-2), sub (0-4)
```

`stream_to_rama()` maps audio → RAMA via lookup tables, but the resulting
coords DON'T match `encode_text()` or `CMU→ARPABET→RAMA` for the same word.

Example: Speaker says "exactly"
  - Audio coords:  (12, 10, 5, 12, 44) — elements: KJSKK
  - Dict coords:   (1, 16, 48, 0, 16, 32, 43, 1) — elements: JSVSVSKS
  - ZERO overlap.

No downstream scorer (edit distance, 7D ranker, synth attractors, Antaranga
imprints) can fix coords that don't match in the first place.

### THE PATH FORWARD: HEARING FIRST (Sravanam)

The user's insight: **we classify before we hear.**

Current: frame → classify phoneme → match word (LINEAR, premature)
Needed:  frame → HIT RESONANCE GRID → imprint forms → READ imprint (RECEIVED)

The Antaranga IS the drum membrane:
  - Sound hits → prana accumulates at collision points
  - The PATTERN of accumulated prana = the acoustic imprint
  - Multiple dimensions: rhythm (cycle), intensity (prana), articulation (source), timbre (target)

But the slot addressing must be in a SHARED space — both real audio
and reference patterns must land on the SAME slots.

**Key concept**: Don't try to convert audio to RAMA coords.
Instead, let both audio AND dictionary words create imprints
on the SAME resonance surface. Compare imprints, not coords.

This requires:
1. A shared address space (not RAMA coords, not raw audio features)
2. The synth as the address generator (audio → seed → synth → slot)
3. Reference imprints pre-computed from text (text → seed → synth → slot)
4. Matching by imprint shape (prana distribution cosine similarity)

The existing tech that contributes:
- **MahaCompression**: text → deterministic seed (shared space!)
- **MahaSynth**: seed → attractor → address
- **LotusArrayInt**: 65K O(1) slots for pre-computed reference
- **Antaranga**: 512-slot resonance membrane for live audio
- **ResonanceRanker**: 7D scoring once we have matching coords

---

## SESSION 4 SYNTHESIS: What We Actually Know

### The 3 Layers (now clearly separated)

```
LAYER 1 — RECEPTION (Mic / Intake)         ✅ WORKS
  audio → PCM → 4D frames (RMS, varga, F0, centroid)
  + MFCCs (13 coefficients per frame)
  + Formants (F1, F2 via LPC)
  ShabdaIntake does this correctly. No changes needed.

LAYER 2 — HEARING (Imprint / Accumulation)  ❌ MISSING
  Frames → pattern over time → acoustic fingerprint
  The system SKIPS this entirely.
  Current flow: frame → score_frame() → phoneme (per frame!)
  Needed: frames → accumulate → segment-level imprint
  Antaranga collision/prana IS designed for this but isn't wired to audio.

LAYER 3 — RECOGNITION (Matching / Decoding) ✅ EXISTS but fed wrong data
  Coords → ResonanceRanker (7D) → ranked words
  Coords → PronunciationDict → edit distance → transcript
  Both work IF the input coords are correct. They aren't.
```

### The Root Problem (one sentence)

**Layer 2 doesn't exist.** We jump from raw frames to phoneme labels
without letting the sound form its pattern first.

### What Each Experiment Proved

| # | What | Result | Lesson |
|---|------|--------|--------|
| 9 | VibrationSignature → RAMA | 0% | Different coordinate spaces. No modulo bridge. |
| 10 | Synth attractor sequences | 100% on 13 words | Attractors ARE discriminative. Sequence order matters. |
| 11 | Synth histogram (60 freqs) | 0.93+ everything | Histogram destroys order information. Degenerate. |
| 12 | NavaBhakti smaranam on audio | Sanskrit words, 0.78-0.88 scores | 7D ranker works. But matches Gita lexicon, not English. |
| 13 | 7D ranker on English dict | 3% | Coord dialect mismatch. Sanskrit dominates lexicon. |
| 14 | Antaranga drum membrane | Audio/ref disjoint slot spaces | Numeric spaces don't overlap. Need shared addressing. |
| 15 | MFCC imprint (avg per segment) | Everything → "eh" | Synthetic prototypes are junk. Real vs synthetic = opposite signs. |

### Key Assets Discovered

1. **shabda_bridge.json** — 638 frames of REAL Prabhupada japa with per-syllable
   acoustic signatures (avg_rms, avg_f0, avg_centroid, rama_coords, element_histogram).
   This is the ONLY ground truth acoustic→RAMA mapping in the entire codebase.

2. **Antaranga** — 512-slot contiguous RAM with collision→resonance logic.
   "membrane health" (integrity), prana accumulation, phase-dependent transformation.
   Designed exactly for "sound hitting a surface and forming a pattern."

3. **MahaModularSynth** — 16-step transformer with ADSR, LFO, feedback, presets.
   Quantum preset (mod 137) gives richest attractor landscape.
   Every input converges to a basin. Different inputs → different basins (with enough space).

4. **ResonanceRanker** — 7D scoring: element, harmonic, shruti, varga, attractor,
   HKR color, phoneme_attractor. Production-grade discrimination on Gita lexicon.

### Philosophical Reframe (from user)

"Krishna's names are non-different from the person. But 'water' is an
abstracted label. What IS language? Maybe a polluted version of Sanskrit,
existing only to explain absolute truth."

"A microphone doesn't need to understand. The spiritual sound itself is
purifying. The moment of HEARING is more important than the output."

"Think in syllables: vibration, rhythm, pitch, intensity, resonance,
melody, intervals."

Implication: Don't build generic STT. Build **vibration recognition** —
let sound form its natural pattern on the resonance grid, then read
which known vibration patterns it most closely resembles. The meaning
(English word) is a secondary lookup, not the primary operation.

### What's Actually Needed Next

Not more experiments. **Architectural clarity.**

The question is: what is Layer 2 concretely?
- Input: stream of 4D frames + MFCCs from ShabdaIntake
- Output: something the existing scorers (7D ranker, edit distance) can consume
- The "something" must be in the SAME coordinate space as dictionary entries

Options being considered:
  A. Fix stream_to_rama() to produce coords that match CMU dict (calibrate the translation)
  B. Build an Antaranga-based imprint that both audio and text can produce (shared surface)
  C. Use Prabhupada's 6 syllable signatures as calibration anchors for acoustic→RAMA
  D. Something else entirely that leverages the architecture more naturally
