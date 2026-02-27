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
