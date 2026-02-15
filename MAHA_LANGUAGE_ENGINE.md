# MAHA LANGUAGE ENGINE — Architecture & Wiring Plan

**Status:** Active development on `followup/maha-language-engine`
**Last updated:** 2026-02-15

---

## 1. The Problem (REVISED — Feb 15 Root Cause Analysis)

The language engine generates **prosodically correct but semantically empty** output.

```
INPUT:  "What is devotion?"
OUTPUT: "what speak how activities ought controlled faithful"
```

### Root Cause: The Engine is a Shadow Pipeline

`MahaLanguageEngine` creates its **own** compressor, synth, kernel, venu,
antaranga — all separate instances from the Lotus `__call__`. It duplicates
the entire Maha Mantra computation in isolation, then tries to compose
language from this shadow data. It never touches the real root.

**The Lotus `__call__` already computes everything the composer needs:**

| Lotus Field | What It Contains | Language Use |
|-------------|-----------------|--------------|
| `smaranam` | 7 resonant words (ranked by 7D resonance) | Word pool (primary) |
| `verse` | Gita verse + word-for-word Sanskrit→English | Philosophical grounding + template |
| `vibration` | seed, attractor, phoneme, 4D signature | Prosodic alignment |
| `guna` | RAJAS/SATTVA/TAMAS (from OpCode) | Mode selection |
| `diw` | Divine Instruction Word (venu/vamsi/murali) | Intensity + process + phase |
| `position`/`guardian` | Routing context | Guardian-specific vocabulary |
| `antaranga` | Chamber state (active slots, prana) | Resonance weighting |
| `akash` | Accumulated state across rounds | Continuity |
| `chapter_significance` | "Raja Vidya - The King of Knowledge" | Semantic context |

**The fix is NOT adding more vectors to the shadow pipeline.**
**The fix is connecting the composer to the Lotus root.**

### Previous Wrong Approach (StateVector)

The earlier attempt added a `StateVector` extracted from `MahaState.get_status()`.
This was wrong because:
1. MahaState is a wrapper, not the root — it wraps legacy systems
2. A shallow status snapshot (uptime, entry count) has no semantic content
3. It's manual wiring — adding a new vector means touching 10 files
4. It ignores the real computation: Gita routing, DIW, Chamber resonance

### Correct Approach: Lotus Response as Input

```
User Input
    ↓
MahamantraLotus.__call__(input)     ← THE ROOT
    ↓
Lotus Response Dict                 ← THE MAHA VECTOR
    ├── smaranam (7 resonant words)
    ├── verse (Gita words + meanings)
    ├── vibration (seed, attractor, phoneme signature)
    ├── guna (mode from OpCode)
    ├── diw (flute instruction)
    ├── position/guardian/quarter
    ├── antaranga (chamber state)
    └── akash (accumulated state)
    ↓
compose(lotus_response)             ← LANGUAGE FROM TRUTH
    ↓
English Output
```

No shadow pipeline. No duplicate instances. No manual wiring.
The composer receives the full Lotus computation and clothes it in language.

---

## 2. What the Lotus `__call__` Returns (verified Feb 15)

```python
lotus = MahamantraLotus()
result = lotus("What is devotion?")
```

**Key fields for language composition:**

```
result["smaranam"]            # 7 resonant words (ranked by 7D resonance ranker)
  → [{"sanskrit": "paryupāsate", "meaning": "worship perfectly", "score": 0.911}, ...]

result["verse"]               # Gita verse matched by attractor
  → {"id": "BG.11.29", "chapter": 11, "verse": 29, "guna": "rajas",
     "words": [{"sanskrit": "yathā", "meaning": "as"}, {"sanskrit": "pradīptam", "meaning": "blazing"}, ...]}

result["vibration"]           # Seed, attractor, phoneme, 4D signature
  → {"seed": 50663505, "attractor": 25, "phoneme": "ī",
     "signature": {"element": "vayu", "varga": 0, "sub": 1, "harmonic": 42}}

result["guna"]                # Mode derived from OpCode (not guessed)
  → {"mode": "RAJAS", "opcode": "EXTEND_CAP", "opcode_value": 9}

result["diw"]                 # Divine Instruction Word
  → {"raw": 87942, "venu": 6, "vamsi": 350, "murali": 2}

result["position"]            # 9
result["guardian"]            # "prahlada"
result["quarter"]             # "karma"
result["holy_name"]           # "R"
result["trinity_function"]    # "deliverer"
result["chapter_significance"] # "Raja Vidya - The King of Knowledge"

result["antaranga"]           # Chamber state
  → {"active_slots": 30, "total_prana": 483117, "collisions": 0}

result["akash"]               # Accumulated state across rounds
  → {"total_rounds": 1, "total_beats": 16, "last_attractor": 25, ...}
```

**This IS the Maha Vector.** No new vector needed. No MahaState snapshot needed.

---

## 3. Implementation Plan (Lotus-Rooted)

### Phase A: Lotus-Rooted Composer (NEXT)

The composer must consume the Lotus response dict directly. Two word pools:

1. **Smaranam pool**: `result["smaranam"]` — 7 words already ranked by 7D resonance.
   These are the primary content words. They have Sanskrit, meaning, score, and
   full RAMA coordinates (via `word_by_iast` lookup).

2. **Verse pool**: `result["verse"]["words"]` — Gita verse word-for-word.
   These are the philosophical grounding. They have Sanskrit, meaning, and
   coordinates. The Gita verse is the "authorized answer" to the input.

**Scoring axes (all numeric, all from Lotus response):**
- Rhythm: prosodic_affinity(syllable_vector, word_coords) — existing
- Resonance: smaranam score (already computed by 7D ranker)
- Guna alignment: word mode vs result["guna"]["mode"]
- DIW intensity: result["diw"]["venu"] normalizes scoring weight
- Akash continuity: result["akash"]["total_rounds"] scales confidence

**Assembly:**
- SVO ordering from coordinate mass → role (existing `_word_role`)
- Template from verse structure (existing `extract_template`)
- Input echo from user words (existing `_pick_token` scoring)

### Phase B: Engine Refactor

`MahaLanguageEngine.generate()` should:
1. Call `MahamantraLotus.__call__(text)` — get the real computation
2. Extract smaranam + verse + vibration + guna + diw from response
3. Pass to `compose(lotus_response=...)` — single dict, not 10 params
4. Return EngineResult

This eliminates the shadow pipeline (own compressor, synth, kernel, venu, antaranga).
The engine becomes a thin adapter: Lotus → compose → EngineResult.

### Phase C: Remove Shadow Infrastructure

Once Phase B works:
- Remove `_ensure_loaded()` (own compressor, synth, kernel, venu, antaranga)
- Remove `_encode()`, `_route()`, `_resonate()`, `_expand()`, `_sprout_derivation_tree()`
- Remove `state_bridge.py` and `StateVector` (replaced by Lotus response)
- Remove `state_affinity()` (replaced by Lotus-derived scoring)
- Keep: `phonetics.py`, `mantra_grid.py`, `mode_affinity.py`, `section_router.py`
- Keep: `composer.py` (refactored to consume Lotus response)

### Phase D: Nadi Integration (future)

Once the engine consumes Lotus directly, Nadi integration becomes natural:
- Engine registers as a TattvaGate hook or DIWSubscriber
- Receives Lotus computation via the existing broadcast channel
- No separate pipeline needed

---

## 4. Branchless Principles

- **No hardcoded keywords.** Word classification from coordinates, not strings.
- **No magic numbers.** All thresholds from `_seed.py` protocol constants.
- **No if/else string matching.** Roles from mass + position, modes from graph distance.
- **No shadow pipelines.** One computation (Lotus), one truth.
- **No manual wiring.** New capabilities enter via the Lotus response dict.
- **Singularity principle.** Everything derives from the Maha Mantra.

---

## 5. File Map (Target State)

```
substrate/
├── lotus_core.py            # THE ROOT: __call__() → Lotus Response Dict
├── language/
│   ├── __init__.py          # Public API: generate()
│   ├── types.py             # EngineResult, RhythmProfile, SyllableVector
│   ├── phonetics.py         # 3D syllable vectors from CMU ARPAbet
│   ├── mantra_grid.py       # 32-step sequencer (16 words × 2 beats)
│   ├── mode_affinity.py     # WordNet graph-distance mode classification
│   ├── section_router.py    # Attractor → section + verse template
│   ├── composer.py          # Prosodic composition (Lotus response → English)
│   └── engine.py            # Thin adapter: Lotus → compose → EngineResult
├── chamber.py               # Sankirtan Chamber (DIW → Cell → Registry)
├── venu_orchestrator.py     # 19-bit DIW LUT, step()/spell()/cycle()
├── antaranga.py             # 512-slot collision chamber (16KB RAM)
├── resonance_ranker.py      # 7D word ranking (vectorized, 4127 words)
└── sanskrit_lookup.py       # verse_words(), word_by_iast(), hkr_signature()
```

---

## 6. What Was Already Done (Composer Infrastructure)

### SVO Assembly (b3ef5a15d)
- `_word_role()`: classify by coordinate mass → REF/VERB/NOUN/QUALITY/PREP/PARTICLE
- `_SVO_ORDER`: Subject(REF) → Verb → Object(NOUN) → Quality → Modifiers
- `_assemble()`: role-bucket placement, template anchor injection
- `_resolve_coords()`: IAST lookup for words without coordinates

### Token Selection (dfee96bf7)
- `_pick_token()`: scoring (len + PANCHA bonus for input match), dedup-aware
- Input echo: user's words appear in output via token scoring bonus

### Pool Management (7007ecc6e)
- Pool capped: expansion at PANCHA, branch at PANCHA (focused pool)

**These composer internals are CORRECT and REUSABLE.** The refactor changes
what feeds INTO the composer (Lotus response instead of shadow pipeline),
not how the composer processes words internally.

---

## 7. Open Questions

1. **Should `generate()` call Lotus directly or receive a pre-computed response?**
   Both. `generate(text)` calls Lotus. `generate_from_lotus(response)` accepts
   a pre-computed response for integration with existing Lotus callers.

2. **What about the existing 194 language tests?**
   Most test composer internals (SVO, token selection, rhythm) — these stay.
   Engine tests that test the shadow pipeline will need updating.

3. **Performance: Lotus `__call__` is ~1400ms (pre-cache) / ~78ms (cached).**
   The language engine currently takes ~40ms. Adding a Lotus call adds latency.
   But: the Lotus call IS the computation. The shadow pipeline was doing the
   same work (compress, synth, rank_words) just with separate instances.
