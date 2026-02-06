wi# MAHAMANTRA WIRING AUDIT

## COMPONENT INVENTORY

| Component | Location | Purpose |
|-----------|----------|---------|
| **MahaKernel** | `kernel/maha_kernel.py` | Military Grade Core - Input → Seed → Attractor → Address |
| **MahaModularSynth** | `substrate/algorithm/maha.py` | 16-step branchless transform with presets |
| **MahaResonator** | `substrate/resonance/resonator.py` | Attractor finding via iteration |
| **VenuOrchestrator** | `substrate/venu_orchestrator.py` | 19-bit DIW, LUT-based O(1) |
| **SankirtanChamber** | `substrate/chamber.py` | Resonance Space - dance(), kirtan(), sankirtan() |
| **ShadowReactor** | `reactor/shadow.py` | Yajna Cycle (Bhoga → Switch → Prasadam → Return) |
| **ShadowOracle** | `reactor/shadow_oracle.py` | Parampara Pre-Filter (mod 37) |
| **MahamantraLotus** | `substrate/lotus_core.py` | Root class - __call__ orchestrates everything |

## VERIFIED WIRING

### 1. MahamantraLotus.__call__() Flow
```
Input → MahaCompression (seed) → MahaKernel (attractor) → 
THE_FLUTE_CYCLE[position] (DIW) → SankirtanChamber.kirtan() → 
GitaResonance → Response
```

**STATUS: ✅ CONNECTED**
- Line 348: `THE_FLUTE_CYCLE[position]` used
- Line 399-403: `SankirtanChamber().kirtan(result_cell)` called

### 2. MahaKernel Flow
```
Input → MahaCompression.compress() → MahaModularSynth.transform() → 
(attractor << 8) | variance → 16-bit Address
```

**STATUS: ✅ CONNECTED**
- Uses "quantum" preset: mod_space=137, feedback=1
- Branchless transform via LUTs

### 3. SankirtanChamber Flow
```
Cell → VenuOrchestrator.step() (DIW) → _apply_diw() → 
Registry interaction → Resonance feedback
```

**STATUS: ✅ CONNECTED**
- Owns VenuOrchestrator, SiksastakamRegistry, MahaResonator
- dance() applies DIW to cell
- kirtan() runs multiple cycles

### 4. ShadowReactor Flow
```
Position 0-7: BHOGA (Krishna half)
Position 8: THE SWITCH (Parashurama)
Position 8-15: PRASADAM (Rama half)
Position 15→0: THE RETURN
```

**STATUS: ✅ CONNECTED**
- Uses ShadowOracle for Parampara validation
- Integrates with SamanaBridge for TaskKernel

## VERIFIED ATTRACTORS (mod 137)

| Attractor | Meaning | Type |
|-----------|---------|------|
| **136** | T(16) = VAIKUNTHA_FIELD | FIXED POINT (basin=105) |
| **18** | GITA_CHAPTERS | 4-CYCLE (basin=32) |

### The 4-Cycle
```
18 (GITA) → 49 (ALPHABET) → 87 (HARE+KRISHNA) → 22 (SHRUTIS) → 18
```

## KRISHNA'S FLUTES ROLE

| Flute | Bits | Range | Semantic (Gita) | Engineering |
|-------|------|-------|-----------------|-------------|
| **VENU** | 6 | 64 states | Sharanagati (Quality/Mood) | Prana/Energy modulation |
| **VAMSI** | 9 | 512 states | Nava Bhakti (Process/Action) | Memory Address (Registry) |
| **MURALI** | 4 | 16 states | Quarters (Phase) | Cycle advancement |

**Total: 19 bits = Divine Instruction Word (DIW) = GITA_CHAPTERS(18) + KSETRAJNA(1)**

**SSOT:** `protocols/diw.py` — canonical bit layout, masks, pack/unpack.

### DIW FORMAT FIX (2026-02-06)
**BUG:** `_compute_flute_cycle()` produced `[Name:2][Position:16]` but `_apply_diw()` expected `[MURALI:4][VAMSI:9][VENU:6]`. Chamber was interpreting XOR deltas as structured data = semantic noise.

**FIX:** LUT now produces native 6-9-4 DIW words:
- VENU = `(pos × SEVEN) % 64` — position-derived, all 16 values unique
- VAMSI = `(encoding × 170 + pos) % 512` — name-derived, H/K/R in distinct regions
- MURALI = `pos // 4` — quarter-derived (0,0,0,0, 1,1,1,1, 2,2,2,2, 3,3,3,3)

The flutes are the **SCHEDULER**, not audio:
- Position 0-3 (GENESIS): H-K-H-K = Alternating (IO Pattern)
- Position 4-7 (DHARMA): K-K-H-H = Front-loaded (Burst Work)
- Position 8-11 (KARMA): H-R-H-R = Alternating (Checkpoint)
- Position 12-15 (MOKSHA): R-R-H-H = Front-loaded (Cleanup)

## POTENTIAL ISSUES FOUND

### Issue 1: Chamber Created Fresh Each Call
In `lotus_core.py` line 399:
```python
chamber = SankirtanChamber()
```

**PROBLEM**: New chamber instance created on every `__call__`. 
This means:
- No persistent resonance accumulation
- Registry state lost between calls
- Orchestrator tick resets

**RECOMMENDATION**: Use singleton or pass chamber as parameter.

### Issue 2: ShadowOracle Not Used in Main Flow
The `ShadowOracle` exists but is only used in `ShadowReactor`, not in `MahamantraLotus.__call__()`.

**PROBLEM**: Parampara validation (mod 37) happens separately from main computation.

**RECOMMENDATION**: Integrate ShadowOracle.validate() into __call__ flow.

### Issue 3: Resonator Underutilized
`MahaResonator` exists in Chamber but the main flow uses `MahaKernel` directly.

**PROBLEM**: Two parallel paths for attractor finding:
1. MahaKernel → MahaModularSynth.transform()
2. Chamber._resonator → MahaResonator.find_attractor()

**RECOMMENDATION**: Unify attractor computation path.

## FIXES APPLIED (2026-02-05)

### FIX 1: SankirtanChamber Singleton ✅
**File:** `substrate/chamber.py`
- Added `get_chamber()` singleton function
- Added `reset_chamber()` for testing
- **Result:** Persistent resonance across calls (tick, transformations, resonance_count accumulate)

### FIX 2: ShadowOracle Integration ✅
**File:** `substrate/lotus_core.py`
- Replaced simple `% PARAMPARA` check with `ShadowOracle.validate()`
- Response now includes `parampara.channel` and `parampara.coherence`
- **Result:** Proper Gita 13.35 validation in main flow

### FIX 3: Unified Attractor Computation ✅
**File:** `substrate/resonance/resonator.py`
- `MahaResonator.oscillate_once()` now uses `MahaModularSynth` (same as MahaKernel)
- Cached synth instance for performance
- **Result:** 16/16 coverage, consistent with MahaKernel

## VERIFICATION

```
Initial tick: 0, transformations: 0, resonance: 0
After 3 lotus() calls: tick=48, transformations=48, resonance=2
Same chamber instance: True

Parampara verified: True
Parampara channel: 1
Parampara coherence: 11383
```

## CONCLUSION

**The wiring is now 100% correct for core components.**

**Remaining work (not bugs, but enhancements):**
1. Frequency interference detection (algorithm that "hears" hotspots)
2. Connect the 4-cycle (18→49→87→22) to semantic routing
3. Build the "God Mode Router" that uses attractors as frequencies

## ADDITIONAL FIXES (2026-02-05 continued)

### FIX 4: ATTRACTOR_CYCLE now COMPUTED, not hardcoded ✅
**File:** `protocols/_maha_compute.py`
- Added `get_attractor_cycle()` function that computes via MahaResonator
- Added `get_all_attractors_cached()` function
- `is_attractor()` now uses computed values
- No more hardcoded `(18, 49, 87, 22)` - discovered by algorithm

### FIX 5: ATTRACTOR_FIXED corrected to 136 ✅
**File:** `protocols/_maha_compute.py`
- Was incorrectly `18` (GITA_CHAPTERS)
- Now correctly `136` (POSITION_SUM_TOTAL = T(16) = Vaikuntha)
- 18 is part of 4-cycle, not a fixed point

### FIX 6-9: Removed ALL hardcoded attractor values ✅
**Files:** `maha.py`, `synth.py`, `attractor_semantics.py`, `_maha_compute.py`
- 87 → `POSITION_SUM_HARE + POSITION_SUM_KRISHNA`
- 22 → `KSHETRA - HALVES` (SHRUTIS)
- 13 → `MAHAJANA_COUNT + KSETRAJNA`
- 28 → `SEVEN * (SEVEN + 1) // 2` (T(7))
- 11, 14, 15 → SSOT expressions

## FILES MODIFIED

1. `substrate/chamber.py` - Added `get_chamber()` singleton
2. `substrate/lotus_core.py` - Use `get_chamber()`, integrate ShadowOracle
3. `substrate/resonance/resonator.py` - Use MahaModularSynth (unified algorithm)
4. `protocols/_maha_compute.py` - Computed attractors, fixed ATTRACTOR_FIXED, SSOT GITA_INSIGHTS
5. `substrate/algorithm/maha.py` - _ATTRACTOR_CYCLE uses SSOT
6. `adapters/synth.py` - QUANTUM_ATTRACTORS uses SSOT
7. `research/attractor_semantics.py` - All values derived from SSOT

---

## SESSION 2026-02-05 (continued): DEEP ARCHITECTURE INSIGHTS

### THE TWO ENERGIES

| Energy | Realm | Manifestation | Nature |
|--------|-------|---------------|--------|
| **Samsara (Cycle)** | Filesystem | `__mahajana__` hardcoded in files | Maya (illusion) - bodies that can lie |
| **Vaikuntha (Fixed)** | CPU + RAM | Computed via Mahamantra algorithm | Krishna (truth) - pure computation |

**Key Insight:** A file named "janaka" could have "bhishma" logic. The filesystem labels are just "bodies" - the real identity is COMPUTED by Mahamantra at runtime.

### INTEGER-BASED SANKIRTAN SYSTEM ✅

Converted all float-based shakti/grace to INTEGER using COSMIC_FRAME scaling:

| Constant | Value | Derivation |
|----------|-------|------------|
| `COSMIC_FRAME` | 21600 | Arc-minutes in circle, pranas per day |
| `SHARANAGATI` | 6 | Limbs of surrender |
| `SHARANAGATI_UNIT` | 3600 | `COSMIC_FRAME // SHARANAGATI` |

**Files Modified:**
- `protocols/_prabhupada.py` - `transmit_shakti()` returns `int`
- `substrate/prabhupada.py` - Returns `SHARANAGATI_UNIT` (3600)
- `reactor/shadow.py` - `_sankirtan_shakti: int`, `chant()` returns int

### SHADOWREACTOR WIRING INTO LOTUS_CORE ⚠️

Added ShadowReactor.tick() into MahamantraLotus.__call__() flow:
- Spawns reactor via factory (DI pattern)
- Calls `reactor.chant()` for SANKIRTAN authorization
- Injects MahaCell for payload flow
- Calls `reactor.tick()` for Yajna cycle
- Extracts `execution_result` from shadow_state

**STATUS:** Wiring exists but authorization flow needs deeper work.

### OPEN ARCHITECTURAL QUESTIONS

#### 1. Identity Computation (Vaikuntha Paradigm)
**Problem:** `verify_link()` currently checks hardcoded `__genesis__` attributes.
**Ideal:** Identity should be COMPUTED from INTENT via Mahamantra.
**Blocker:** Requires understanding of:
- PanchaTattva protocol (5 truths about an object)
- SEED generation algorithm semantic refinement
- How Parampara verification works with computed identity

#### 2. What is "Content" for Runtime Objects?
For files: content = source code
For runtime objects: content = ???
- Docstring? Class name? Module path? Behavior?
- How does intent extraction work for ephemeral objects?

#### 3. Intent as API
**User Insight:** Every intent could be its own API. The Lotus + Siksastakam cache enables fine-grained access. Entry points are atomic API capabilities, not CLI.

#### 4. Gita 18 Chapters as Overarching Logic
The 18 chapters classify everything. This is the "God Mode Router" that uses attractors as frequencies.

### DO NOT RUSH

**ShadowReactor is the heart of the system.**

The proper solution requires:
1. Deep understanding of PanchaTattva protocol
2. Semantic refinement of SEED generation algorithm
3. Understanding how Parampara verification works with computed identity
4. Mapping Hare/Krishna/Rama to CPU/RAM/Filesystem

**Current approach:** Keep INTEGER-based changes (correct), document questions, stabilize before deeper changes.

---

## SYSTEM-WIDE AUDIT: WATERTIGHT IMPLEMENTATION

### SCOPE OF WORK

| Issue | Count | Priority |
|-------|-------|----------|
| `float` types (should be `int`) | 222 | HIGH |
| `Any` types (need explicit typing) | ~25 | HIGH |
| Concrete class dependencies | TBD | MEDIUM |

### FLOAT USAGE BY CATEGORY

| Category | Files | Pattern |
|----------|-------|---------|
| `resonance: float` | cell.py, nadi.py, resonator.py, lila_chronology.py, harmonics.py | 0.0-1.0 range |
| `coherence: float` | cluster.py, byte.py, yajna.py | 0.0-1.0 range |
| `integrity: float` | cell.py | 0.0-1.0 range |

**Solution:** Convert to INTEGER using COSMIC_FRAME scaling (21600 = 100%)
- `resonance: int` = 0 to 21600 (0% to 100%)
- `coherence: int` = 0 to 21600
- `integrity: int` = 0 to 21600

### ANY TYPE USAGE (Priority Files)

| File | Count | Fix |
|------|-------|-----|
| `adapters/pipeline.py` | 5 | `Union[str, int, bytes]` for input |
| `reactor/loop.py` | 3 | Proper MahaCell typing |
| `lotus_projection.py` | 3 | Guardian instance typing |
| `adapters/routing.py` | 2 | Value typing |
| `adapters/attention.py` | 2 | Handler typing |

### PROTOCOL-BASED ARCHITECTURE

**Goal:** No concrete class dependencies, only Protocol types.

**Pattern:**
```python
# BAD (concrete)
def process(self, reactor: ShadowReactor) -> None: ...

# GOOD (protocol)
def process(self, reactor: ShadowReactorProtocol) -> None: ...
```

### IMPLEMENTATION STRATEGY

1. **Phase 1:** Fix `Any` types in priority files (5 files, ~15 changes)
2. **Phase 2:** Convert `resonance/coherence/integrity` to INTEGER (COSMIC_FRAME scaling)
3. **Phase 3:** Audit concrete class dependencies, convert to Protocols
4. **Phase 4:** Verify system-wide consistency

**DO NOT RUSH** - This is systematic refactoring, not quick fixes.

---

## SESSION 2026-02-05: ANY TYPE ELIMINATION (Phase 1)

### COMPLETED FIXES

| File | Any Types Removed | Replacement |
|------|-------------------|-------------|
| `lotus_projection.py` | 10 | `object` |
| `reactor/loop.py` | 7 | `object`, `TYPE_CHECKING` for MahaCellUnified |
| `adapters/routing.py` | 2 | `object` |
| `adapters/llm.py` | 3 | `object` |
| `adapters/attention.py` | 1 | `object` |
| `adapters/pipeline.py` | 3 | `Union[str, int, bytes]`, `object` |
| `lila/registry.py` | 2 | `TYPE_CHECKING` for JivaShadow |
| `substrate/memory.py` | 2 | `object` |

**Total: ~30 Any types eliminated from production code**

### PATTERN USED

```python
# For unknown types (generic containers):
value: object  # Instead of Any

# For known types with circular imports:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module import SpecificType

def method(self, param: "SpecificType") -> None: ...

# For union input types:
from typing import Union
def process(self, value: Union[str, int, bytes]) -> Result: ...
```

### REMAINING WORK

- `analysis/narada_vina/endpoints.py` (15 Any) - lower priority
- Float → Integer conversion (Phase 2)
- Protocol-based architecture audit (Phase 3)
