# Architecture Audit — 2026-02-17
## Branch: architecture/consolidation

Status: PHASE 1 COMPLETE (Inventory + Wiring Check)

---

## kernel/ (6 files)

| File | Lines | Status | Consumers | Notes |
|------|-------|--------|-----------|-------|
| singularity.py | 1230 | ACTIVE | 4 direct (aliased as `_singularity`) | Central heartbeat, routing, governance |
| maha_kernel.py | 218 | ACTIVE | Multiple via `get_kernel()` | Seed→Address only. `__getattr__` proxy REMOVED |
| intent.py | 408 | PREPARED | Wired in Singularity.tick() removed | MantraKernel: 0 resolvers registered → no-op |
| daemon.py | ~500 | ACTIVE | CLI entry point | MahamantraDaemon, alternative heartbeat path |
| fractal.py | 379 | ACTIVE | 6+ consumers (hologram, engine, protocols) | FractalNode/Tree data structures |
| phoenix.py | 172 | UNWIRED | 0 consumers (maha_state has own _load_state) | State persistence — nobody imports it |

### kernel/ Findings:
- **phoenix.py**: Prepared infrastructure, 0 consumers. `maha_state.py` reimplemented its own persistence. Candidate for revival or deprecation.
- **intent.py**: `MantraKernel` has 0 registered resolvers → `process_queue()` is a no-op. Was wired in Singularity.tick() but removed (double-tick fix). Infrastructure ready but unused.
- **3x `get_kernel()` naming collision**: `maha_kernel.py`, `maha_llm_kernel.py`, `intent.py` all export `get_kernel()`. Different singletons, same function name. LOW priority — no actual bugs, just confusing.

---

## substrate/ (52 files)

### ZERO IMPORTS (not in __init__.py either):
| File | Lines | Notes |
|------|-------|-------|
| clock.py | 266 | Pure stateless tick library. Useful but unwired. |
| lipta.py | 48 | degree↔lipta conversion. Useful but unwired. |

### Via __init__.py lazy-load (NOT dead):
- `_legacy.py` — Legacy types (Declaration, Phase, etc.)
- `parampara.py` — ParamparaNode, graph, position lookup
- All adapters/ files — lazy-loaded via adapters/__init__.py

### LOW imports (1-2 consumers):
| File | Consumers | Notes |
|------|-----------|-------|
| boot.py | 1 | Boot sequence |
| cluster.py | 1 | Cluster management |
| errors.py | 1 | Error types |
| gita.py | 1 | Gita verse data |
| kala.py | 1 | TimeKeeper (used by Singularity) — CRITICAL |
| lila_chronology.py | 1 | Lila timeline |
| memory.py | 1 | Memory subsystem |
| orbit.py | 1 | Orbital mechanics |
| process_manager.py | 1 | Process management |
| registry.py | 1 | SiksastakamRegistry (used by chamber.py) |
| yajna.py | 1 | Yajna cycle types |

### Key substrate files (well-wired):
- **lotus_core.py** — Root class, 64+ importers via `from vibe_core.mahamantra import mahamantra`
- **bridge.py** — offer() pipeline, atomically decomposed
- **venu_orchestrator.py** — DIW producer, 19-bit flute cycle
- **chamber.py** — SankirtanChamber + Antaranga (16KB bytearray)
- **gate_providers.py** — 5 TattvaGate observers, wired via boot_orchestrator
- **cell.py** — MahaCellUnified, core data structure
- **lotus_projection.py** — Boot-time auto-wiring (used by proxy.py, factory.py)

---

## venu/ (4 files)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| tick.py | 73 | ACTIVE | MantraTick — atomic time unit (pos 0-15, cycle, mala) |
| voice.py | 91 | PREPARED | MantraVoice — 0 registered voices. Infrastructure ready. |
| clock.py | 136 | ACTIVE | MantraClock — 1 consumer (boot_orchestrator: on_mala flush) |
| __init__.py | ~50 | ACTIVE | Re-exports |

### venu/ Findings:
- **MantraVoice**: 0 registered voices → tick_once() iterates empty list. Prepared infrastructure.
- **MantraClock**: 1 real consumer (mala flush callback from boot_orchestrator). Works correctly.
- **MantraTick**: Used by MantraClock internally. Correct.

---

## services/ (Heartbeat Chain)

### The ONE heartbeat path (verified, no double-ticking):
```
VenuService._beat_loop()
  → _dispatch_beat_subscribers(position)   # 5 BeatSubscribers
  → _singularity.tick()                    # Kala.advance() + VenuOrchestrator.step() + _broadcast()
  → _clock.tick_once()                     # MantraClock (1 mala callback)
```

### 5 BeatSubscribers (beat_discovery.py):
1. OuroborosSubscriber (healing_subscribers.py)
2. ShuddhiSubscriber (healing_subscribers.py)
3. KalaBridgeSubscriber (shuddhi/kala_bridge.py)
4. JagannathSubscriber (jagannath_subscriber.py)
5. LotusBridgeSubscriber (lotus_bridge.py)

### 2 DIWSubscribers (diw_discovery.py):
1. DIWTelemetrySubscriber (diw_telemetry.py)
2. NaradaBridge (narada_bridge.py)

### 7 Dispatch Mechanisms (3 active, 4 prepared):
1. **ACTIVE**: DIWSubscriberProtocol (VenuOrchestrator._emit) — 2 subscribers
2. **ACTIVE**: BeatSubscriberProtocol (VenuService) — 5 subscribers
3. **ACTIVE**: Singularity._listeners (_broadcast) — 1+ listeners
4. PREPARED: MantraClock/Voice — 0 voices, 1 mala callback
5. PREPARED: MantraKernel/Intent — 0 resolvers
6. PREPARED: gate_hooks (on_gate callbacks) — wired via gate_providers at boot
7. PREPARED: TattvaRegistry — wired via gate_providers at boot

---

## 17x tick() Methods (Verified — No Conflicts)

The `tick()` name is overloaded but each lives in its own domain:
- **Singularity.tick()** — THE heartbeat (called by VenuService)
- **VenuOrchestrator.tick()** — alias for step() (DIW production)
- **MantraClock.tick()** — MantraTick.advance (internal)
- **SankirtanChamber.tick()** — chamber state advance
- **Lotus.tick()** — delegates to Singularity.tick()
- **ShadowReactor.tick()** — yajna cycle tick
- **LilaChronology.tick()** — lila timeline
- Others: adapters/orchestrator, protocols, manifestation_service, learning_loop

No double-ticking. Each tick() is called by its own consumer chain.

---

## Split-Brain Issues (from SPLIT_BRAIN_DIAGNOSIS.md):
- P1 Naming Clarity: DONE
- P2 Dead Code Paths: DONE (this audit documents them)
- P3 MahaKernel Singleton: DONE

## Key Architectural Decisions (2026-02-17):
1. `__call__()` is PURE — no gates inside (fixed)
2. Gates fire at boundary only (execute/GovardhanGateway)
3. Lotus→Singularity is valid Facade pattern, not a merge target
4. MahaKernel.__getattr__ proxy removed (was dead code)
5. research/ moved to mahamantra_research/ (routing tests xfailed)
6. Singularity.tick() is clean — no MantraClock or MantraKernel calls inside
7. VenuService is the ONE heartbeat driver

## Prepared Infrastructure (not dead, not active):
- MantraVoice (0 voices)
- MantraKernel IntentResolver (0 resolvers)
- phoenix.py (0 consumers — maha_state.py has own persistence)
- substrate/clock.py (0 imports — pure stateless library)
- substrate/lipta.py (0 imports — pure conversion library)

## Next Steps:
1. Decide: revive or deprecate phoenix.py (maha_state.py duplicates it)
2. Decide: wire MantraKernel resolvers or keep as prepared infrastructure
3. Decide: wire MantraVoice or keep as prepared infrastructure
4. Consider renaming the 3x get_kernel() to avoid confusion
5. Deep-dive into adapters/ and protocols/ for further split-brains
