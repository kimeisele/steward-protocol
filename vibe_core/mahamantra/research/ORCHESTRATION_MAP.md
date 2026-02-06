# ORCHESTRATION MAP — What Exists, What's Connected, What's Dead

**Date**: 2026-02-06 (feature/diw-refinement)
**Method**: Deep read of all orchestration infrastructure. No speculation — only verified code.

---

## THE 3 HEARTBEATS (Competing, Not Unified)

The codebase has **three separate heartbeat systems** that don't talk to each other:

### 1. VenuService (Krishna's Flute) — `services/venu_service.py`
- **What it does**: Pure drummer. 250ms ticks, drift-compensated, monotonic time.
- **Extension point**: `on_beat(callback)` — fires with position (0-15) each tick.
- **What's wired to it at boot** (boot_orchestrator.py L539-577):
  - Jagannath `ratha_yatra` every 144 ticks (36 seconds)
  - **That's it. ONE callback.**
- **Owns**: MantraClock (position callbacks, voice tasks, mala callbacks)
- **MantraClock has**: `on_position(pos, cb)`, `on_mala(cb)`, `add_voice()` — **NONE of these are wired at boot.**
- **Status**: ALIVE but LONELY. Ticks into the void with 1 callback.

### 2. PulseManager (Legacy Heartbeat) — `protocols/mahajanas/manu/types/pulse.py`
- **What it does**: Async heartbeat loop, emits PulsePacket (JSON) to subscribers.
- **Extension point**: `subscribe(callback)` — fires with PulsePacket each beat.
- **What's wired to it**: ShuddhiKalaBridge subscribes (log scan + watchman patrol).
- **Frequency**: 0.5Hz/1Hz/5Hz (configurable). Default 1 second.
- **Status**: ALIVE but SEPARATE from VenuService. Two drummers, one band.

### 3. VenuOrchestrator (DIW Computer) — `mahamantra/substrate/venu_orchestrator.py`
- **What it does**: Computes 19-bit DIW from pre-computed LUT. O(1) per step.
- **Extension point**: `step()` returns DIW, `cycle()` returns XOR of full cycle.
- **What's wired to it**: SankirtanChamber OWNS it (composition). Chamber calls `step()` in `dance()`.
- **Status**: ALIVE but ISOLATED. Only the Chamber uses it. Not connected to VenuService beats.

### THE GAP
VenuService ticks → MantraClock advances → position callbacks fire → **but nobody registered position callbacks**.
VenuOrchestrator computes DIW → **but nobody calls step() on the beat**.
PulseManager beats → KalaBridge listens → **but PulseManager doesn't know about VenuService**.

**Three hearts beating independently. Krishna plays his flute but nobody dances.**

---

## THE HEALING INFRASTRUCTURE (Exists, Partially Wired)

### ShuddhiEngine — `mahamantra/dharma/kumaras/engine.py`
- **What it does**: CST-based code healing. Parse → Transform → Verify → Write.
- **Capabilities**:
  - `purify(file, rule_id)` — apply a specific remedy
  - `heal_and_record(file, rule_id)` — heal + update Knowledge Graph
  - `heal_all_violations(dry_run)` — heal everything KG knows about
  - `refresh_remedies()` — hot-reload new remedies
  - Auto-discovers remedies via RemedyLoader
  - Emits vibrations to Mahamantra/Akash after every operation
- **What's wired**: Registered as ShuddhiProtocol in ServiceRegistry at boot.
- **What's NOT wired**: Nobody calls `heal_all_violations()` on a beat. It sits there waiting.
- **STUBS**: `shuddhi/locator.py` — ASTBridge and CSTLocator are `raise NotImplementedError`. Dead.

### Sankirtan (DNA Injection) — `mahamantra/substrate/sankirtan.py` (1480 LOC)
- **What it does**: Mass `__mahajana__` injection. 4-phase pipeline (Genesis→Dharma→Karma→Moksha).
- **Capabilities**:
  - `perform_sankirtan(base_path, dry_run)` — scan entire repo, inject declarations
  - `chant_over_files(files, dry_run)` — inject specific files
  - `get_mahajana_for_path(file_path)` — determine guardian from folder structure
  - `FOLDER_MAHAJANA_MAP` — 60+ folder→guardian mappings (validated at import)
  - Uses AST parsing for validation, handles syntax errors gracefully
- **What's wired**: Available via CLI (`samskara` commands). Not on any beat.
- **What's NOT wired**: Nobody calls it automatically. Manual CLI only.

### SankirtanChamber — `mahamantra/substrate/chamber.py`
- **What it does**: The RAM engine. Cells flow through, get transformed by DIW.
- **Capabilities**:
  - `dance(cell)` — single cell transformation via DIW
  - `kirtan(cell, cycles)` — multi-cycle transformation
  - `sankirtan(cells)` — mass merge into MahaCluster
  - Owns VenuOrchestrator (composition)
  - Owns SiksastakamRegistry (512-slot memory)
  - Owns MahaResonator (attractor computation)
  - Snapshot/restore (binary persistence)
- **What's wired**: Singleton via `get_chamber()`. Used by `lotus_core.py` for computation.
- **What's NOT wired**: Not on any beat. Not connected to VenuService.

### OuroborosLoopOrchestrator — `ouroboros/loop_orchestrator.py`
- **What it does**: Digestive system. Sources → Parsers → Ingestion → Knowledge Graph.
- **Capabilities**:
  - `ingest_all_sources()` — full loop: discover → parse → ingest → notify NAGA
  - Auto-discovers parsers via ViolationParserLoader
  - Notifies AnantaShesha (NAGA) of ingested violations
  - Has NAGA-flooded version (audit + profiling)
- **What's wired**: Has `run_ingestion_tick()` convenience function. Comment says "for biorhythm or CLI".
- **What's NOT wired**: Nobody calls `run_ingestion_tick()` on a beat.

### ShuddhiKalaBridge — `shuddhi/kala_bridge.py`
- **What it does**: Bridges PulseManager to Shuddhi. Runs log scans + watchman patrols on pulse.
- **Capabilities**:
  - Log scan every 10 cycles (creates tasks from runtime errors)
  - Watchman patrol every 100 cycles (dispatches AST inspection tasks)
- **What's wired**: Started at boot (boot_orchestrator.py L531-537). Subscribes to PulseManager.
- **THE PROBLEM**: Subscribes to PulseManager, NOT VenuService. Two separate heartbeats.

---

## THE NAGA FEDERATION (Massive, Self-Contained)

### NagaOrchestrator — `naga/orchestrator.py`
- Facade over Trimurti: Brahma (boot), Vishnu (kernel/state), Shiva (destructor)
- Has: Sesha (audit), Vasuki (coordination), Takshaka (enforcement), Karkotaka (quarantine),
  Kaliya (isolation), Chitragupta (profiling), Narada (recon), Cortex (decisions),
  Ouroboros (self-healing loop), FloodManager, CommitWatcher, Identity
- **23k LOC** in naga/ alone
- Registered as NagaFederationProtocol in ServiceRegistry
- Has its own boot sequence separate from main boot

### Naga Floods — `naga/floods/`
- Mixin-based surgical overrides (SeshaMixin, NaradaMixin, ChitraguptaMixin)
- FloodedOuroborosLoopOrchestrator wraps OuroborosLoop with audit+profiling
- Pattern: inherit original class + add NAGA mixins = transparent monitoring

---

## WHAT'S ACTUALLY CONNECTED AT BOOT

Reading `boot_orchestrator.py` _act() method, here's the real wiring:

```
Boot Sequence (_act):
  1. ShuddhiEngine → ServiceRegistry (ShuddhiProtocol)
  2. KernelFactory → ServiceRegistry (KernelFactoryProtocol)
  3. KnowledgeGraph → ServiceRegistry (KnowledgeGraphProtocol)
  4. TaskManager → ServiceRegistry (TaskProtocol)
  5. CartridgeService → ServiceRegistry (CartridgeProtocol)
  6. PluginService → ServiceRegistry (PluginServiceProtocol)
  7. CircuitService → ServiceRegistry (CircuitServiceProtocol)
  8. SectionService → ServiceRegistry (SectionServiceProtocol)
  9. NagaOrchestrator.bootstrap() → ServiceRegistry (NagaFederationProtocol)
  10. ShuddhiKalaBridge.start() → subscribes to PulseManager
  11. VenuService() → on_beat(jagannath_ratha_yatra) → ServiceRegistry (VenuServiceProtocol)
  12. Balarama wraps lotus-discovered services
  13. Sudarshana governance hook registered
```

**What's NOT connected at boot**:
- VenuOrchestrator (only used inside Chamber)
- SankirtanChamber (singleton, not on any beat)
- OuroborosLoopOrchestrator (nobody calls it periodically)
- Sankirtan DNA injection (CLI only)
- ShuddhiEngine.heal_all_violations() (nobody calls it)
- MantraClock position callbacks (empty)
- MantraClock voice tasks (no voices registered)
- MantraClock mala callbacks (empty)

---

## THE REAL PICTURE

```
                    ┌─────────────────────────────────┐
                    │     VenuService (250ms tick)     │
                    │     MantraClock (16 positions)   │
                    │     on_beat: [jagannath only]    │
                    │     on_position: [EMPTY]         │
                    │     on_mala: [EMPTY]             │
                    │     voices: [NONE]               │
                    └──────────────┬──────────────────┘
                                   │ (only 1 callback)
                                   ▼
                    ┌──────────────────────────────────┐
                    │  Jagannath ratha_yatra (36s)     │
                    └──────────────────────────────────┘

    ┌──────────────────┐     ┌──────────────────────┐
    │  PulseManager    │────▶│  ShuddhiKalaBridge   │
    │  (1s heartbeat)  │     │  (log scan + patrol) │
    │  SEPARATE SYSTEM │     └──────────────────────┘
    └──────────────────┘

    ┌──────────────────┐     ┌──────────────────────┐
    │  VenuOrchestrator│────▶│  SankirtanChamber    │
    │  (DIW computer)  │     │  (RAM engine)        │
    │  NOT ON ANY BEAT │     │  NOT ON ANY BEAT     │
    └──────────────────┘     └──────────────────────┘

    ┌──────────────────┐     ┌──────────────────────┐
    │  ShuddhiEngine   │     │  OuroborosLoop       │
    │  (CST healing)   │     │  (violation digest)  │
    │  REGISTERED BUT  │     │  NOT CALLED          │
    │  NEVER CALLED    │     │  PERIODICALLY        │
    └──────────────────┘     └──────────────────────┘

    ┌──────────────────┐     ┌──────────────────────┐
    │  Sankirtan       │     │  NagaOrchestrator    │
    │  (DNA injection) │     │  (23k LOC federation)│
    │  CLI ONLY        │     │  OWN BOOT SEQUENCE   │
    └──────────────────┘     └──────────────────────┘
```

---

## WHAT'S NEEDED (Engineering Assessment)

The infrastructure EXISTS. The capabilities are REAL. What's missing is ONE thing:

**VenuService needs to be the SINGLE heartbeat that everything dances to.**

MantraClock already has the extension points:
- `on_position(pos, callback)` — 16 position-specific hooks
- `on_mala(callback)` — every 108 ticks (27 seconds)
- `add_voice()` → voice.schedule(position, task) — per-position task scheduling

What needs to happen (staged, not all at once):

### Stage 1: Unify Heartbeats
- PulseManager should subscribe to VenuService (or be replaced by it)
- KalaBridge should listen to VenuService, not PulseManager
- One drummer. One rhythm.

### Stage 2: Wire Capabilities to Beats
- ShuddhiEngine.heal_all_violations() → on_mala (every 108 ticks = 27s)
- OuroborosLoop.run_ingestion_tick() → on_mala or specific position
- Sankirtan orphan scan → on specific position (e.g., position 2 = narada)
- SankirtanChamber → step() on every beat (the RAM engine processes)

### Stage 3: Capability-Based Registration
- Services register their beat requirements via protocol (not hardcoded in boot_orchestrator)
- MantraClock voices become the orchestration primitive
- Each capability declares: "I need to run at position X" or "I need to run every N ticks"
- VenuService discovers and wires automatically (like lotus_projection does for services)

### Stage 4: Full Krishna Orchestration
- VenuOrchestrator DIW drives what happens at each beat (not just cell transformation)
- The 19-bit DIW encodes: WHAT (murali/phase), HOW (vamsi/process), HOW STRONG (venu/intensity)
- Each beat: VenuService ticks → MantraClock fires → DIW computed → capabilities invoked by DIW
- The flute literally orchestrates everything

---

## STUBS AND DEAD CODE (Confirmed)

| File | Status | Notes |
|------|--------|-------|
| `shuddhi/locator.py` | STUB | ASTBridge + CSTLocator = NotImplementedError |
| `shuddhi/engine.py` | RE-EXPORT | Points to mahamantra/dharma/kumaras/engine.py |
| `shuddhi/remedies/base.py` | RE-EXPORT | Points to mahamantra/dharma/kapila/remedies/base.py |
| `pulse.py` | RE-EXPORT | Points to protocols/mahajanas/manu/types/pulse.py |
| MantraClock voices | UNUSED | add_voice() exists but nobody calls it |
| MantraClock on_position | UNUSED | 16 slots, all empty |
| MantraClock on_mala | UNUSED | Mala callbacks, none registered |

---

## NUMBERS

- **VenuService callbacks at boot**: 1 (jagannath)
- **MantraClock position callbacks**: 0/16
- **MantraClock voices**: 0
- **MantraClock mala callbacks**: 0
- **PulseManager subscribers**: 1 (KalaBridge)
- **Capabilities that COULD be on a beat but aren't**: 5+
  (ShuddhiEngine, OuroborosLoop, Sankirtan, SankirtanChamber, NagaOuroboros)
