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

#### Phase 1: Bridge (This PR)
- Create `NaradaBridge` class implementing `DIWSubscriberProtocol`
- Bridge holds current DIW state (tick, position, phase, diw)
- Bridge wraps existing `EventBus` — zero changes to 48 consumer call-sites
- `get_event_bus()` returns the bridge (which delegates to inner EventBus)
- Register bridge as DIW subscriber at boot → auto-discovered
- Every agent event now carries DIW context in `details`

#### Phase 2: DIW-Stamped Events (Future)
- `Event` dataclass gets optional `diw_context: DIWContext` field
- Agent events carry position/phase/tick natively (not in details dict)
- EventBus history becomes time-indexed by tick (not wall-clock)
- Replay: reconstruct exact system state from tick sequence

#### Phase 3: Phase-Aware Scheduling (Future)
- SudarshanaGuard uses Venu phase for rate-limiting policy
  - GENESIS (0-3): IO burst allowed (H-K-H-K alternating)
  - DHARMA (4-7): Front-loaded work burst (K-K-H-H)
  - KARMA (8-11): Checkpoint phase — reduce throughput
  - MOKSHA (12-15): Cleanup — only system events
- EventTypes become phase-aware (some events only valid in certain phases)
- Agents receive phase hints: "you're in DHARMA, burst now"

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

### Files Changed (Phase 1)

- **NEW:** `vibe_core/services/narada_bridge.py` — NaradaBridge class
- **EDIT:** `vibe_core/services/diw_discovery.py` — add NaradaBridge to subscriber list
- **EDIT:** `vibe_core/mahamantra/substrate/event_bus.py` — `get_event_bus()` returns bridge-aware bus
- **TEST:** `tests/services/test_narada_bridge.py` — bridge receives DIW, stamps events
