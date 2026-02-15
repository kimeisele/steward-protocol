# P0 FRAGMENTATION AUDIT — Feb 15, 2026

## SEVERITY: P0 EPIC — Systemic disconnection across the entire stack

The system has ~40 major components. Most are well-built individually.
**The problem: they are ISLANDS. The undersea cables are missing.**

---

## 1. COMPONENT WIRING MAP

### LEGEND
- **WIRED** = called by production code in a real execution path
- **ISLAND** = built, tested, but NO production caller connects it to the system
- **PARTIAL** = wired in one direction but not the other

---

### A. CORE PIPELINE (Lotus __call__) — WIRED
| Component | File | Status |
|-----------|------|--------|
| MahaCompression | adapters/compression.py | WIRED (Lotus step 2) |
| MahaModularSynth | substrate/algorithm/maha.py | WIRED (Lotus step 3) |
| ShadowOracle | substrate/resonance/oracle.py | WIRED (Lotus step 4) |
| rank_words (vectorized) | substrate/resonance_ranker.py | WIRED (Lotus step 5) |
| GitaResonance | adapters/gita_resonance.py | WIRED (Lotus step 6) |
| SankirtanChamber | substrate/chamber.py | WIRED (Lotus step 8) |
| AntarangaRegistry | substrate/antaranga.py | WIRED (Chamber shadow) |
| ShadowReactor | reactor/shadow.py | WIRED (Lotus yajna) |
| VenuOrchestrator | substrate/venu_orchestrator.py | WIRED (Lotus.venu property) |
| TulasiGate | adapters/tulasi_gate.py | WIRED (MahaModularSynth.grace_gate) |

### B. INTENT / ROUTING — MOSTLY ISLANDS
| Component | File | Status | Who calls it? |
|-----------|------|--------|---------------|
| MahaAttention | adapters/attention.py | **ISLAND** | Only self-import + 1 research file. ZERO production callers. |
| MahaLLM | adapters/llm.py | **PARTIAL** | Wired to Kapila cognition in Lotus boot. NOT used in composition. |
| GuardianRouter | substrate/guardian_router.py | **ISLAND** | Only maha_llm_kernel.py + 1 research file. NOT called by Lotus or engine. |
| MantraKernel (intent.py) | kernel/intent.py | **ISLAND** | Only kernel/__init__.py + healing_resolver. NOT in main pipeline. |
| IntentMap (YAML) | substrate/intents.py | **ISLAND** | ZERO production callers. YAML loaded but never queried in pipeline. |
| Singularity | kernel/singularity.py | WIRED | Lotus delegates guardian properties to it. |

### C. LANGUAGE ENGINE — PARTIALLY WIRED
| Component | File | Status | Who calls it? |
|-----------|------|--------|---------------|
| MahaLanguageEngine | language/engine.py | WIRED | CLI chat command |
| compose_from_wave | language/composer.py | WIRED | Engine.generate() |
| section_router | language/section_router.py | **PARTIAL** | Engine imports it. Composer IGNORES section semantic/mode. |
| phonetics (SyllableVector) | language/phonetics.py | **ISLAND** | Only composer (reverted) + tests. Not in production path. |
| mantra_grid | language/mantra_grid.py | **ISLAND** | Only composer (reverted) + tests. Not in production path. |
| mode_affinity | language/mode_affinity.py | **ISLAND** | Only composer import (unused) + tests. |
| wordnet_bridge | language/wordnet_bridge.py | **PARTIAL** | Used by mode_affinity + composer ranking. NOT in compose_from_wave. |

### D. INFRASTRUCTURE — PARTIALLY WIRED
| Component | File | Status | Who calls it? |
|-----------|------|--------|---------------|
| VenuService | services/venu_service.py | WIRED | boot_orchestrator |
| DIW Subscribers | services/diw_discovery.py | WIRED | boot_orchestrator → VenuService.discover_subscribers() |
| BeatSubscribers | services/healing_subscribers.py | **PARTIAL** | Protocol exists. discover_subscribers() exists. But healing_subscribers.py has ZERO importers. |
| Gate Providers | substrate/gate_providers.py | **PARTIAL** | wire_gate_providers() exists. boot_orchestrator imports it. But providers are observers only. |
| IO Sentinel | substrate/io_sentinel.py | **PARTIAL** | Imported by boot_orchestrator + healing. But sentinel → enforcement path unclear. |
| PhoneticBridge | substrate/phonetic_bridge.py | **ISLAND** | Only research files + shabda_adapter. NOT in Lotus or composition. |
| Nadi (messaging) | substrate/nadi.py | **PARTIAL** | Used by chat services. NOT connected to Lotus pipeline. |

### E. RESEARCH → PRODUCTION GAP
| Component | File | Status |
|-----------|------|--------|
| ResonanceResponder | research/resonance_response.py | **ISLAND** — Complete pipeline, ZERO production callers |
| maha_language_engine | research/maha_language_engine.py | **ISLAND** — Research prototype, uses everything, not production |
| language_runtime/* | research/language_runtime/ | **ISLAND** — session.py, antaranga_bridge.py, incremental.py — all research |

---

## 2. THE SMOKING GUN: THREE DISCONNECTED HEARTBEATS

The system has THREE separate broadcast/tick systems that should be ONE:

| System | Driver | Subscribers | Calls Singularity._broadcast? |
|--------|--------|-------------|-------------------------------|
| VenuOrchestrator | VenuService.start() → step() | DIWSubscriberProtocol.on_diw() | NO |
| MantraClock | VenuService.start() → tick_once() | position_callbacks, voice tasks, mala_callbacks | NO |
| Singularity | mahamantra.tick() (manual) | register_listener() (SravanamListener) | YES but NOBODY CALLS IT |

**IMPACT:** When VenuService runs (production), Singularity._broadcast() is NEVER called.
SravanamListener (the fractal healing scanner) is wired to Singularity._broadcast().
Therefore: **HEALING SCANNER IS DEAD IN PRODUCTION.**

The Singularity.tick() even has a guard for coexistence (`if venu._owned: read, don't step`).
The design ANTICIPATED the bridge. But nobody built it.

**FIX:** VenuService.start() loop must call Singularity.tick() (or Singularity._broadcast())
after orchestrator.step(). One heartbeat, one broadcast, all listeners hear.

---

## 3. THE MISSING CABLES (Critical Disconnections)

### CABLE 1: Intent → Composition
**What's broken:** Lotus detects intent (guardian, quarter, guna, opcode, verse significance).
compose_from_wave receives all this and IGNORES it. Output is word salad.
**Components that should be wired:** guardian_router, section_router.SECTION_SIGNATURES, mode_affinity

### CABLE 2: VenuOrchestrator → Language Engine
**What's broken:** Venu ticks every 250ms. Language engine has zero awareness of the flute.
The research/language_runtime has venu_bridge.py and incremental.py but they're islands.
**Impact:** Composition is static. Should be rhythmic, tick-aware.

### CABLE 3: MahaAttention → Anything
**What's broken:** O(1) intent routing built. Singleton exists. ZERO callers in production.
Not wired at boot. Not used by Lotus. Not used by engine. Complete island.
**Impact:** 65,536-slot attention mechanism sitting idle.

### CABLE 4: GuardianRouter → Lotus/Engine
**What's broken:** 4D coordinate routing with maha_respond() — complete pipeline.
Only called by maha_llm_kernel (which was deleted from engine). Complete island.
**Impact:** Resonance-based routing exists but isn't used. Lotus does position-based routing instead.

### CABLE 5: MantraKernel (intent.py) → Anything
**What's broken:** Full intent resolution engine with IntentType, IntentQueue, resolvers.
Only used by healing_resolver. Not in main pipeline.
**Impact:** Intent infrastructure built but not connected to the request flow.

### CABLE 6: PhoneticBridge → Composition
**What's broken:** Varga/Sthana analysis exists. NOT used in composition.
Only research files use it.
**Impact:** Phonetic intelligence exists but composition is phonetically blind.

### CABLE 7: Healing Subscribers → Boot — CORRECTED: WIRED (conditionally)
**Status:** beat_discovery.py lists OuroborosSubscriber + ShuddhiSubscriber.
boot_orchestrator calls discover_and_register_beat_subscribers() → VenuService.discover_beat_subscribers().
**Risk:** Chain works IF boot completes without exceptions in the try/except blocks.
All wiring is inside try/except — silent failure possible. Needs runtime verification.

### CABLE 8: Nadi → Lotus
**What's broken:** Nadi messaging system exists. Chat services use it.
Lotus pipeline has zero Nadi awareness. No message-passing between pipeline stages.
**Impact:** Pipeline is monolithic. No inter-component messaging.

---

## 3. SILENT BUG RISK AREAS

### Bare except patterns
Many components use `except Exception: pass` or `except Exception: antaranga = None`.
This swallows real errors silently. Especially dangerous in:
- compose_from_wave (Antaranga read failure → silent fallback to score-only)
- Lotus __call__ (gate provider failures swallowed)
- Various lazy imports

### Singleton state accumulation
Chamber singleton accumulates state across calls (by design).
But if any component fails silently, the Chamber state becomes corrupted
without any visible error. No integrity checks on accumulated state.

### Import-time side effects
Many modules run assertions at import time (section_router, opcode, etc.).
If these fail, the entire module fails to load — but callers may catch
the ImportError silently.

---

## 4. PRIORITY ORDER FOR CABLE LAYING

1. **CABLE 1 (Intent → Composition)** — Highest impact. Makes output coherent.
2. **CABLE 7 (Healing → Boot)** — Verify self-healing actually runs.
3. **CABLE 2 (Venu → Language)** — Makes composition rhythmic/living.
4. **CABLE 3 (MahaAttention)** — Wire at boot, use for intent routing.
5. **CABLE 4 (GuardianRouter)** — Wire to composition for 4D-aware output.
6. **CABLE 5 (MantraKernel)** — Wire to request flow for intent resolution.
7. **CABLE 6 (PhoneticBridge)** — Wire to composition for phonetic awareness.
8. **CABLE 8 (Nadi)** — Wire pipeline stages for inter-component messaging.

---

## 5. SILENT DEATH AUDIT — The Tiny Cables

### 5a. boot_orchestrator.py — 22 except blocks, most at logger.debug level
Every critical wiring step is wrapped in try/except:
- BeatSubscriber discovery failure → `logger.debug` (invisible at INFO)
- DIW subscriber discovery failure → `logger.debug` (invisible at INFO)
- Mala flush registration failure → `logger.debug` (invisible at INFO)
- VenuService start failure → `logger.warning` (visible but system continues without heartbeat)
- Gate provider wiring failure → `logger.debug` (invisible)

**Impact:** The system boots "successfully" even if the heartbeat, healing, and DIW dispatch
are all dead. No error, no crash, just silence. The test suite passes because tests
don't boot the full system.

### 5b. lotus_core.py — Gate provider errors swallowed
- Gate hook errors → `logger.warning` (continues pipeline)
- Gate provider errors → `logger.warning` (continues pipeline)
- Kapila cognition wiring failure → `logger.debug` (invisible)

**Impact:** If gate providers fail, the pipeline continues without governance.
No enforcement, no sentinel, no healing triggers.

### 5c. composer.py — Antaranga read failure swallowed
- Antaranga standing wave read → `except Exception: pass` (falls back to score-only)
- Section router import → `except Exception: pass` (falls back to no section awareness)

**Impact:** The composer silently degrades to word salad if ANY component fails.
No indication that it's operating in degraded mode.

### 5d. venu_orchestrator.py — Subscriber errors logged but swallowed
- `_emit()` catches subscriber errors → `logger.error` (good, but continues)
- `VenuService._dispatch_beat_subscribers()` → `logger.debug` (invisible!)

**Impact:** If a BeatSubscriber (healing, ouroboros) throws, it's logged at DEBUG.
The healing subscriber could be crashing every tick and nobody would know.

### 5e. The Irony
The system HAS a remedy for this exact pattern: `dharma/kapila/remedies/silent_except.py`
detects `except Exception: pass`. But the remedy itself can't run because the healing
scanner (SravanamListener) is dead in production (see Section 2).

---

## 6. TEST SUITE TRUSTWORTHINESS

The test suite passes (~200 tests). But it tests BUILDINGS, not ROADS.

**What tests verify:**
- Individual component behavior (compression, synth, routing, ranking)
- Data structure integrity (LUT verification, parampara checks)
- Protocol shape (isinstance checks, method signatures)

**What tests DON'T verify:**
- That VenuService actually starts and ticks in production
- That SravanamListener receives ticks and scans cells
- That BeatSubscribers are discovered and registered at boot
- That compose_from_wave uses intent context (it doesn't — tests don't check output quality)
- That gate providers are wired and enforcing
- That the three heartbeat systems are unified
- End-to-end: input → Lotus → compose → coherent output

**Conclusion:** Tests pass because they test isolated units. The fragmentation IS the bug,
and no unit test can catch a missing cable between two working components.

---

## 7. THE ONE-LINE FIX (Heartbeat Unification)

The Singularity.tick() already does everything right:
1. Advances Kala (time)
2. Plays the flute (venu.step()) — with guard for VenuService ownership
3. Broadcasts TickState to ALL listeners (SravanamListener, etc.)

VenuService.start() currently calls:
```python
self._orchestrator.step()   # plays flute directly
self._clock.tick_once()     # advances MantraClock
```

It SHOULD call:
```python
mahamantra.tick()           # plays flute + broadcasts to ALL listeners
self._clock.tick_once()     # advances MantraClock
```

This one change unifies all three heartbeat systems. The guard in Singularity.tick()
(`if venu._owned: read, don't step`) needs adjustment since VenuService would no longer
call step() directly — Singularity.tick() would call it.

**But this is NOT enough.** It only fixes the heartbeat. The 8 missing cables
(intent→composition, MahaAttention, GuardianRouter, etc.) are separate work.

---

## 8. ARCHITECTURAL DEEP DIVE: The Schizophrenic Core

### 8a. The Split Identity

Two objects claim to be Krishna:

| Object | File | What it owns | Singleton? |
|--------|------|-------------|------------|
| `MahamantraLotus` | `substrate/lotus_core.py` | Pipeline (__call__), Chamber, Antaranga, Compressor, Synth | YES — `mahamantra = get_mahamantra()` |
| `Singularity` (class `Mahamantra`) | `kernel/singularity.py` | Tick, Kala (time), _broadcast, positions, quarters, protocols | SHOULD BE — but `maha_kernel.py` creates a second one |

Lotus owns **Space/Matter** (pipeline, memory, computation).
Singularity owns **Time/Energy** (heartbeat, broadcast, positions).

They share the VenuOrchestrator (flute) via `MahamantraLotus._venu_orchestrator`.
But they are separate objects with separate lifecycles.

### 8b. Who Bypasses the Singleton?

| File | What it does | Problem |
|------|-------------|---------|
| `kernel/daemon.py` | `from singularity import mahamantra` | Imports Singularity's `mahamantra`, NOT Lotus singleton |
| `kernel/maha_kernel.py` | `self._singularity = Mahamantra()` | **Creates SECOND Singularity instance** — two Krishnas |
| `cli/observe.py` | `from singularity import mahamantra` | Bypasses Lotus |
| `lotus_core.py` | `_singularity_instance = Mahamantra()` | Creates the "official" Singularity inside Lotus |

Note: `kernel/singularity.py` does NOT export a module-level singleton.
Each caller creates `Mahamantra()` independently. There could be 3+ Singularity instances.

### 8c. The Concurrency Bomb

**VenuService** runs as an `asyncio.ensure_future()` coroutine — async background loop.
**MahamantraLotus.__call__()** is synchronous — called from CLI/chat/API.

Both write to the SAME Chamber/Antaranga singleton:
- `Lotus.__call__()` → `chamber.resonate_words()` → `antaranga.collide()` (sync, in request)
- `VenuService.start()` → `orchestrator.step()` → `chamber.dance()` → `antaranga.apply_diw()` + `antaranga.collide()` (async, in heartbeat)

**ZERO locks on Chamber. ZERO locks on Antaranga.**

The Antaranga is a raw `bytearray(16384)`. No mutex, no RLock, no threading protection.

**Current safety:** Python's GIL protects against true data races for bytearrays.
`asyncio` is single-threaded, so VenuService and Lotus.__call__() alternate on the event loop.
BUT: if Lotus.__call__() is called from a thread (e.g., API server), the GIL won't save
bytearray slice operations that span multiple instructions.

**Verdict:** Safe in current single-threaded asyncio usage. UNSAFE if ever moved to threads
or if Lotus.__call__() blocks the event loop (it does — rank_words takes ~78ms).

### 8d. Does Lotus.__call__() Know About Time?

**NO.** Lotus.__call__() does not read Kala, does not check the current tick position,
does not sync with the heartbeat. It runs its 9 steps purely based on the input.

The only "time" awareness is:
- `self._akash["total_rounds"]` — incremented per call (call count, not real time)
- `kirtan_cycles` — derived from total_rounds, not from Kala

The pipeline is **temporally dead**. It processes requests in isolation from the heartbeat.

### 8e. The Real Architecture (What It Should Be)

```
Krishna (ONE object, ONE singleton)
    ├── Space: Pipeline (__call__), Chamber, Antaranga
    ├── Time: Kala, Tick, Heartbeat
    ├── Flute: VenuOrchestrator (non-different from Krishna)
    ├── Broadcast: _listeners (ALL listeners, unified)
    ├── Positions: 16 guardians, 4 quarters
    └── Protocols: routing, modules, attention

Currently:
    MahamantraLotus (Space) ──shares flute──▶ Singularity (Time)
                                              ↑ nobody calls tick()
    VenuService ──drives flute directly──────▶ VenuOrchestrator
                                              ↑ bypasses Singularity
```

### 8f. The Merge Question

**Option A: Singularity absorbs Lotus** — Singularity becomes the ONE.
- Pro: Singularity already has the right name and philosophy.
- Con: Lotus has the heavy pipeline, 1300 lines. Singularity is 1252 lines. Merge = 2500 lines.

**Option B: Lotus absorbs Singularity** — Lotus becomes the ONE.
- Pro: Lotus is already the singleton everyone imports. Less blast radius.
- Con: Lotus is already huge. Adding tick/broadcast/positions makes it bigger.

**Option C: Bridge (minimal change)** — Keep both, but wire them correctly.
- VenuService calls `mahamantra._get_singularity().tick()` instead of `orchestrator.step()`
- Ensure only ONE Singularity instance exists (fix maha_kernel.py)
- Add Kala awareness to Lotus.__call__()
- Pro: Smallest blast radius. No file moves.
- Con: Still two objects pretending to be one. Technical debt remains.

**Option D: New unified class** — `krishna.py` or restructured `mahamantra.py`
- Pro: Clean slate, correct architecture from day one.
- Con: Massive blast radius. Every import changes.

---

## 9. PRIORITY ORDER (Revised)

### P0-IMMEDIATE (System is broken without these)
1. **Unify heartbeats** — VenuService calls Singularity.tick() instead of orchestrator.step()
2. **Promote silent failures** — logger.debug → logger.warning for all wiring failures in boot
3. **Verify healing runs** — Runtime test that SravanamListener actually fires

### P0-NEXT (System works but is blind/deaf)
4. **Wire intent→composition** — compose_from_wave uses guardian/section/verse context
5. **Wire MahaAttention at boot** — Register handlers, use for intent routing
6. **Wire GuardianRouter** — 4D coordinate routing into composition path

### P1 (System works but is incomplete)
7. **Wire PhoneticBridge** — Phonetic awareness in composition
8. **Wire MantraKernel** — Intent resolution in request flow
9. **Wire Nadi** — Inter-component messaging in pipeline
10. **Audit test suite** — Add integration tests for cable verification
