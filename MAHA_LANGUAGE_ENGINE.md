# MAHA LANGUAGE ENGINE — Architecture & Wiring Plan

**Status:** Active development on `followup/maha-language-engine`
**Last updated:** 2026-02-15

---

## 1. The Problem

The language engine generates **prosodically correct but semantically empty** output.

```
INPUT:  "How is the codebase?"
OUTPUT: "other faithful activities controlled what speak ought"
```

The words are real English tokens from the WordNet bridge, selected by prosodic
affinity (syllable weight ↔ coordinate mass), but they don't **answer** anything.
The engine doesn't know what the codebase looks like. It has no senses.

**Root cause:** The composer operates in a vacuum. It receives the user's input
wave (rhythm, phonemes, attractor) but never queries the system's actual state.
There is no semantic payload — no "truth" to clothe in rhythm.

---

## 2. The Anatomy (What Exists)

Each organ maps to an existing substrate module. No new modules needed.

| Organ | Vedic | Module | Role |
|-------|-------|--------|------|
| **Ear** | Sravanam | `nadi.py` → `NadiOp.RECEIVE` | Receive input wave |
| **Senses** | Buddhi/Chitta | `maha_state.py` → `MahaState` | Perceive system state |
| **Digestion** | Samana | `samana_bridge.py` → `SamanaDispatch` | Dispatch work if needed |
| **Vocal Cords** | Kirtanam | `language/composer.py` | Compose output |
| **Voice** | Kirtanam | `nadi.py` → `NadiOp.SEND` | Deliver response |

### Current Flow (broken)

```
User Input
    ↓
encode() → phonetic coords, seed, intent
    ↓
route() → guardian, section, template
    ↓
build_character_wave() → antaranga impacts
    ↓
resonate() → word slots in antaranga
    ↓
expand() → derivation tree, branch words
    ↓
compose() → word salad ← NO STATE, NO TRUTH
    ↓
EngineResult
```

### Required Flow

```
User Input
    ↓
encode() → phonetic coords, seed, intent
    ↓
╔══════════════════════════════════════════╗
║  SENSE (NEW): MahaState.get_status()    ║
║  → StateVector (guna, entries, uptime)  ║
║  → Concept seeds for word selection     ║
╚══════════════════════════════════════════╝
    ↓
route() → guardian, section, template
    ↓
compose(state_vector=...) → semantically grounded output
    ↓
EngineResult
```

---

## 3. The Gap: Semantic Injection

### What the composer needs

The composer selects words via `prosodic_affinity(syllable_vector, word_coords)`.
This is the **rhythm** axis. It's correct and stays.

What's missing is the **truth** axis: a numeric signal from `MahaState` that
biases word selection toward tokens that describe reality.

### StateVector Design

A frozen dataclass extracted from `MahaState.get_status()`:

```python
@dataclass(frozen=True)
class StateVector:
    """Numeric summary of system state for semantic injection."""
    guna: int           # 0=TAMAS, 1=RAJAS, 2=SATTVA (from GunaClassifier)
    entry_count: int    # Number of sovereign state entries
    boot_count: int     # How many times booted
    uptime_ratio: float # uptime_seconds / KISHORA_MAX_STALE (0-1, clamped)
    systems_alive: int  # Count of wrapped systems that are available (0-6)
    dirty: bool         # Unsaved state changes pending
    prana_level: int    # Total antaranga prana (from engine stage)
```

### How it enters the composer

The StateVector doesn't add keywords. It adds **numeric bias** to existing scoring:

1. **Guna → Mode weight:** SATTVA boosts DHARMA words, RAJAS boosts KARMA,
   TAMAS boosts GENESIS (creation/renewal needed).
2. **Entry count → Mass preference:** More state entries = prefer heavier words
   (complex system needs complex description).
3. **Uptime ratio → Stress alignment:** High uptime = prefer stressed/confident
   tokens. Low uptime = prefer unstressed/tentative tokens.
4. **Systems alive → Element preference:** Maps to dominant element selection
   (more systems = higher element = more akasha/vayu).

All numeric. All derived from protocol constants. No keywords.

---

## 4. Implementation Plan

### Phase 1: StateVector ✅ DONE (b3ef5a15d)

1. ✅ `StateVector` NamedTuple in `language/types.py`
2. ✅ `state_bridge.py`: `extract_state_vector()` from `MahaState.get_status()`
3. ✅ Wired into `engine.py` after `_resonate()`, passed to `compose(state=...)`
4. ✅ `state_affinity()` in `composer.py`: guna→mode, entries→mass, uptime→confidence
5. ✅ Integrated into `rank_resonant_by_rhythm()` as 4th scoring axis
6. ✅ 13 new tests (StateVector, state_affinity, extract_state_vector)

### Phase 1b: SVO Assembly ✅ DONE (b3ef5a15d)

1. ✅ `_word_role()`: classify pool words by coordinate mass → role
2. ✅ `_SVO_ORDER`: REF → VERB → NOUN → QUALITY → PREP → PARTICLE
3. ✅ `_assemble()` rewritten: role-bucket placement, template anchor injection
4. ✅ `_resolve_coords()`: IAST lookup for expansion/branch words (fixes mass=0)

### Phase 2: Nadi Integration (future)

1. Engine receives input via `NadiOp.RECEIVE` (SRAVANAM)
2. Engine sends output via `NadiOp.SEND` (KIRTANAM)
3. State queries via `NadiOp.REQUEST` (VANDANAM)
4. Full message-passing loop instead of direct function call

### Phase 3: Output Coherence (next priority)

The SVO structure is correct but output is still word salad. Root causes:
1. **Token selection quality**: `_pick_token()` picks longest WN token, but
   longest ≠ most relevant. Need semantic relevance to input.
2. **Too many words from unrelated branches**: Expansion/branch words dilute
   the pool with semantically distant tokens.
3. **No input echo**: The user's actual words never appear in output.
   "What is devotion?" should echo "devotion" prominently.
4. **Missing connective tissue**: No articles, prepositions, or conjunctions
   to glue content words into readable phrases.

---

## 5. Branchless Principles (CLAUDE.md)

Every decision in this architecture MUST follow:

- **No hardcoded keywords.** Word classification from coordinates, not strings.
- **No magic numbers.** All thresholds from `_seed.py` protocol constants.
- **No if/else string matching.** Roles from mass + position, modes from graph distance.
- **Existing infrastructure first.** WordNet bridge, mode_affinity, pancha_walk, hkr_signature.
- **Each module = one responsibility.** Don't mix state sensing into composition.

---

## 6. File Map

```
substrate/
├── language/
│   ├── __init__.py          # Public API: generate(), MahaLanguageEngine
│   ├── types.py             # EngineResult, RhythmProfile, SyllableVector, StateVector (NEW)
│   ├── phonetics.py         # 3D syllable vectors from CMU ARPAbet
│   ├── mantra_grid.py       # 32-step sequencer (16 words × 2 beats)
│   ├── mode_affinity.py     # WordNet graph-distance mode classification
│   ├── section_router.py    # Attractor → section + verse template
│   ├── composer.py          # Prosodic composition (rhythm + semantic + state)
│   └── engine.py            # Thin orchestrator wiring all stages
├── maha_state.py            # Sovereign state adapter (Balarama pattern)
├── nadi.py                  # Universal message passing (Pancha Nadi × Nava Ops)
├── samana_bridge.py         # TaskKernel ↔ ShadowReactor
├── wordnet_bridge.py        # Semantic graph + precomputed tokens
├── pancha_walk.py           # RAMA coordinate element/varga mappings
└── antaranga.py             # 512-slot collision chamber
```

---

## 7. What Was Already Done

### Commit ee9c7987b: Branchless composer + section_router

- `composer.py`: Removed ALL keyword lists. Token extraction from WN bridge.
  Prosodic affinity scoring. Assembly via grid mode walk.
- `section_router.py`: `_infer_role(coords, position, total)` replaces keyword
  matching. Role from coordinate mass + verse position.
- 181/181 language tests pass. Zero regressions.

---

## 8. Open Questions

1. **Should StateVector be cached per-tick or per-request?**
   Per-request is simpler. Per-tick via VenuOrchestrator is more "alive".

2. **How deep should Guna diagnosis go?**
   `diagnose_guna(workspace)` requires filesystem access. For the language engine,
   a lightweight `get_status()` summary may suffice initially.

3. **Should the engine ever trigger SamanaDispatch?**
   Only if the prompt requires computation (e.g., "run tests"). For now, the
   language engine is read-only: it senses state but doesn't change it.
