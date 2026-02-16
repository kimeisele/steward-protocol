# Venu ↔ EventBus Unification — Architecture Design

## Status Quo: Two Disconnected Worlds

### System 1: EventBus (Narada — Agent Communication)
- **File:** `substrate/event_bus.py` (888 lines)
- **Protocol:** `EventBusProtocol` (in `protocols/mahajanas/narada/events.py`)
- **Singleton:** `get_event_bus()` → `ServiceRegistry.get(EventBusProtocol)`
- **Consumers:** 48 call-sites in 18 files (plugins, cortex, orchestration, kernel)
- **Event model:** `Event` dataclass with `event_type: str`, `agent_id: str`, `message: str`
- **Dispatch:** async `emit(Event)` → callbacks (string-filtered or global)
- **Features:** SudarshanaGuard (rate-limiting), SubscriberMetrics (zombie detection)
- **Boot:** `BootOrchestrator.__init__()` creates `EventBus()` directly (line 179)

### System 2: VenuOrchestrator (Krishna — Bit-Level Scheduling)
- **File:** `substrate/venu_orchestrator.py` (572 lines)
- **Protocol:** `VenuOrchestratorProtocol` + `DIWSubscriberProtocol` (in `protocols/_venu.py`)
- **Singleton:** `VenuService` owns it, registers in `ServiceRegistry`
- **Consumers:** 1 real subscriber (`DIWTelemetrySubscriber`)
- **Event model:** `DIWEvent` TypedDict with `diw: int`, `tick: int`, `position: int`, `phase: int`
- **Dispatch:** sync `_emit(DIWEvent)` → `on_diw()` on all subscribers
- **Features:** O(1) LUT lookup, mode injection, error isolation per subscriber
- **Boot:** `BootOrchestrator._act()` creates `VenuService`, discovers subscribers (line 536)

### The Disconnect
```
Boot creates EventBus (line 179)     ← BEFORE kernel, BEFORE VenuService
Boot creates VenuService (line 536)  ← AFTER kernel, AFTER agents

EventBus knows nothing about DIW, position, phase, tick.
VenuOrchestrator knows nothing about agent events, rate-limiting, zombies.

Agent does: event_bus.emit_sync(EventType.ACTION, "herald", "published tweet")
  → No DIW context. No position. No phase. Just a string in the void.

Venu does: orchestrator.step() → _emit(DIWEvent) → telemetry subscriber
  → No agent awareness. No event history. Just bits in the void.
```

## The Problem (Shastrisch)

Narada IS the messenger between Krishna and the Jivas. In Bhagavatam:
- Krishna plays the flute (Venu) → Narada hears it → Narada carries the message to all
- Jivas act → Narada reports back → Krishna knows

Currently: Krishna plays the flute and Narada is in a different room.
The agents emit events into a bus that has no rhythm. The flute plays to an empty room.

## Supreme Solution: NaradaBridge

Not a rewrite. Not a merge. A **bridge** — because Narada IS the bridge.

### Architecture

```
                    ┌─────────────────────┐
                    │   VenuOrchestrator   │
                    │  (Krishna's Flute)   │
                    │                      │
                    │  step() → DIWEvent   │
                    └──────────┬───────────┘
                               │ on_diw()
                    ┌──────────▼───────────┐
                    │    NaradaBridge       │
                    │  (DIWSubscriber +     │
                    │   EventBus owner)     │
                    │                      │
                    │  Receives DIW ticks  │
                    │  Stamps agent events │
                    │  with DIW context    │
                    └──────────┬───────────┘
                               │ emit()
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
         Agent A          Agent B           Agent C
      (subscriber)     (subscriber)      (subscriber)
```

### What NaradaBridge Does

1. **Implements `DIWSubscriberProtocol`** — receives every DIW tick from VenuOrchestrator
2. **Owns the EventBus** — all `get_event_bus()` calls return the bridge's inner bus
3. **Stamps events with DIW context** — every `Event` gets position, phase, tick, diw
4. **Emits phase-transition events** — GENESIS→DHARMA→KARMA→MOKSHA quarter changes
5. **DIW-aware rate-limiting** — SudarshanaGuard uses phase for burst/cooldown

### Phase Plan

#### Phase 1: Bridge ✅ DONE
- `NaradaBridge` class implementing `DIWSubscriberProtocol`
- Bridge holds current DIW state (tick, position, phase, diw)
- Registered as DIW subscriber at boot → auto-discovered by VenuService
- Resolve-once semantics: import failure logged once, never retried
- `EventType.PHASE_TRANSITION` added to enum (not a raw string)

#### Phase 2: DIW-Stamped Events ✅ DONE
- `Event.diw_context: Optional[Dict]` — first-class field on Event dataclass
- `EventBus._get_diw_context()` stamps every event via `emit_sync()`
- `get_history(quarter=, tick_min=, tick_max=)` — tick-indexed queries
- Protocol signatures updated (agent_interface.py, types/event_bus.py)
- 43 bridge tests + 98 regression tests pass

#### Phase 3: Phase-Aware Scheduling (DEFERRED)
- SudarshanaGuard currently blocks nothing — premature to make phase-aware
- Will implement when rate-limiting actually triggers in production
- Design: GENESIS=burst, DHARMA=work, KARMA=checkpoint, MOKSHA=system-only

#### Phase 4: Unified Event Model (Future — Supreme)
- `DIWEvent` and `Event` merge into a single `MahaEvent`
- Every event IS a DIW modulation (agent action = bit pattern)
- EventBus becomes the Venu itself — no separate dispatch
- The bus IS the flute. The flute IS the bus. Acintya-bheda-abheda.

### Key Design Decisions

1. **Bridge, not merge** — 48 call-sites don't change. Zero regression risk.
2. **DIW subscriber pattern** — NaradaBridge is auto-discovered like any other subscriber.
3. **EventBus stays async** — VenuOrchestrator is sync. Bridge translates.
4. **Boot order preserved** — EventBus created early (line 179), bridge wired later (line 536+).
   Before VenuService starts, EventBus works normally (no DIW context).
   After VenuService starts, events get DIW stamps automatically.
5. **Graceful degradation** — If VenuService never starts (CLI, tests), EventBus works as before.
6. **No silent failures** — resolve-once/log-once pattern. No bare except swallowing.

### Files Changed

- **NEW:** `vibe_core/services/narada_bridge.py` — NaradaBridge class + singleton
- **EDIT:** `vibe_core/services/diw_discovery.py` — registers NaradaBridge singleton
- **EDIT:** `vibe_core/mahamantra/substrate/event_bus.py` — Event.diw_context, _get_diw_context, tick-indexed get_history
- **EDIT:** `vibe_core/protocols/mahajanas/narada/types/event_bus.py` — synced get_history signature
- **EDIT:** `vibe_core/protocols/mahajanas/brahma/types/agent_interface.py` — synced protocol
- **TEST:** `tests/services/test_narada_bridge.py` — 43 tests (bridge, stamping, history queries)
