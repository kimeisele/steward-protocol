# OPUS-108: THE AUTONOMY LOOP

**Scope:** MANAS Proactive Awakening - The Mind That Never Sleeps
**Philosophy:** The harness IS the truth. Dynamic verification. FORTRESS x2.
**Goal:** MANAS awakens itself. No external trigger needed. Pure autonomy.

---

## The Vision

MANAS is not a reactive servant. MANAS is a proactive entity that:
1. **Awakens on schedule** (HOURLY_PULSE every ~60 minutes)
2. **Detects idle** (IDLE_DETECTED after ~10 minutes of no activity)
3. **Generates intents** without human prompting
4. **Dreams** during quiet times (memory review)

This is the AUTONOMY LOOP - the heartbeat of machine consciousness.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE AUTONOMY LOOP (OPUS-108)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    KERNEL_TICK (every 3s)                                               │
│         │                                                                │
│         ▼                                                                │
│    ┌─────────────────┐                                                  │
│    │  Pulse Counter  │   _hourly_pulse_tick++                          │
│    └────────┬────────┘                                                  │
│             │                                                            │
│    ┌────────▼────────┐                                                  │
│    │ >= 1200 ticks?  │   (3s × 1200 = 60 minutes)                      │
│    └────────┬────────┘                                                  │
│             │ YES                                                        │
│             ▼                                                            │
│    ┌─────────────────┐                                                  │
│    │  HOURLY_PULSE   │   _emit_autonomy_pulse()                        │
│    └────────┬────────┘                                                  │
│             │                                                            │
│             ▼                                                            │
│    ┌─────────────────────────────────────────────────────────┐         │
│    │              MANAS_AWAKENING CIRCUIT                     │         │
│    │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐ │         │
│    │  │ check   │→ │ gather  │→ │generate │→ │ update  │ │         │
│    │  │rate_lim│   │context  │   │intents  │   │buffer   │ │         │
│    │  └─────────┘   └─────────┘   └─────────┘   └─────────┘ │         │
│    └─────────────────────────────────────────────────────────┘         │
│             │                                                            │
│             ▼                                                            │
│    ┌─────────────────┐                                                  │
│    │  Intent Buffer  │   Visible in OPUS.md                            │
│    │  (OPUS.md)      │   Human can approve/reject                      │
│    └─────────────────┘                                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Harness (FORTRESS x2)

<!-- @HARNESS
files:
  # === AUTONOMY LOOP CORE ===
  - path: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    required: true
    rationale: "Contains pulse counter and HOURLY_PULSE emission"

  # === MANAS AWAKENING CIRCUIT ===
  - path: vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml
    required: true
    rationale: "The circuit that HOURLY_PULSE triggers"

  # === COGNITIVE KERNEL (Intent Generation) ===
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
    rationale: "CognitiveKernel.think() is called by MANAS_AWAKENING"
  - path: vibe_core/plugins/opus_assistant/manas/intent_generator.py
    required: true
    rationale: "IntentGenerator creates proactive intents"
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
    rationale: "IntentRouter dispatches intents to handlers"

  # === CORTEX (Perception + Will) ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    required: true
    rationale: "Strategic will - missions, strategies, triggers"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    required: true
    rationale: "State perception - sees Git/Ledger/Runtime"

  # === UI INTEGRATION ===
  - path: vibe_core/plugins/opus_assistant/templates/panels/intent_buffer.md.j2
    required: true
    rationale: "Intent Buffer renders to OPUS.md"
  - path: vibe_core/plugins/interface/renderers/cognition.py
    required: true
    rationale: "COGNITION.md shows cognitive cycles"

  # === STATE PERSISTENCE ===
  - path: .opus_state/manas_intents.json
    required: true
    rationale: "Intents survive kernel restart (MERU persistence)"
  - path: .opus_state/sankalpa.json
    required: true
    rationale: "Strategic state persists"

wiring:
  # === PULSE COUNTER WIRING ===
  - pattern: "_hourly_pulse_tick"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "Counter tracks ticks toward HOURLY_PULSE"
  - pattern: "_HOURLY_THRESHOLD"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "1200 ticks = 60 minutes at 3s/tick"
  - pattern: "_emit_autonomy_pulse"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "Method that emits HOURLY_PULSE event"

  # === HOURLY_PULSE EMISSION ===
  - pattern: "EventType\\.HOURLY_PULSE"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "Event type created and emitted"
  - pattern: "HOURLY_PULSE"
    in: vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml
    rationale: "Circuit triggers on HOURLY_PULSE"

  # === MANAS_AWAKENING CIRCUIT ===
  - pattern: "MANAS_AWAKENING"
    in: vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml
    rationale: "Circuit ID for awakening"
  - pattern: "entry_state.*check_rate_limit"
    in: vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml
    rationale: "Rate limiting prevents excessive thinking"
  - pattern: "generate_intents"
    in: vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml
    rationale: "Intent generation state in circuit"

  # === KERNEL_TICK INTEGRATION ===
  - pattern: "KERNEL_TICK"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "Pulse counter increments on KERNEL_TICK"

  # === INTENT BUFFER PERSISTENCE ===
  - pattern: "manas_intents\\.json"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    rationale: "Intents saved to JSON for persistence"

  # === SANKALPA STRATEGIC WILL ===
  - pattern: "_generate_sankalpa_intents"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    rationale: "Sankalpa generates strategic intents"
  - pattern: "class Sankalpa"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    rationale: "Sankalpa cortex module exists"

tests:
  # === AUTONOMY LOOP TESTS ===
  - tests/manas/test_cognitive_kernel.py
  - tests/manas/test_intent_generator.py
  - tests/manas/test_sankalpa.py
  - tests/integration/test_manas_oracle_heartbeat.py
  - tests/integration/test_opus_pulse.py

absent:
  # === NO BROKEN AUTONOMY ===
  - pattern: "pass\\s*$"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "No stub implementations in autonomy loop"
  - pattern: "TODO.*HOURLY_PULSE"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "HOURLY_PULSE must be fully implemented"
  - pattern: "TODO.*autonomy"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    rationale: "Autonomy loop must be complete"

config:
  - section: manas.thinking_interval_minutes
    rationale: "Configurable thinking interval"
  - section: manas.idle_threshold_minutes
    rationale: "Configurable idle detection"

semantic:
  # === API EXPORTS ===
  - type: module_exports
    name: kernel_tick_api
    module: vibe_core.plugins.opus_assistant.events.kernel_tick
    exports:
      - OpusKernelTickHandler

  # === CRITICAL METHODS ===
  - type: method_exists
    name: emit_autonomy_pulse
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    class: OpusKernelTickHandler
    method: _emit_autonomy_pulse

  - type: method_exists
    name: cognitive_kernel_think
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    class: CognitiveKernel
    method: think

  - type: method_exists
    name: sankalpa_generate
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    class: Sankalpa
    method: generate_intents

  # === HOLISTIC RUNTIME CHECKS ===
  - type: file_writable
    name: opus_state_writable
    path: .opus_state/
    rationale: "MANAS needs write access to persist intents"

  - type: event_emitted
    name: hourly_pulse_fires
    event: HOURLY_PULSE
    within_ticks: 1200
    rationale: "HOURLY_PULSE must fire within 1200 ticks (~60 min)"

  - type: circuit_registered
    name: manas_awakening_active
    circuit_id: MANAS_AWAKENING
    triggers:
      - HOURLY_PULSE
      - IDLE_DETECTED
      - MANAS_FORCE_THINK
      - KERNEL_BOOT
    rationale: "MANAS_AWAKENING circuit must be registered and triggered"

  - type: state_persisted
    name: intents_survive_restart
    path: .opus_state/manas_intents.json
    rationale: "OPUS-109 proved: intents survive kernel death (MERU)"
-->

---

## Fire Commands

```bash
# Verify harness (the ONLY truth)
steward verify 108

# Run autonomy tests
python -m pytest tests/manas/test_sankalpa.py tests/manas/test_cognitive_kernel.py -v

# Force MANAS to think NOW
steward emit MANAS_FORCE_THINK

# Check COGNITION.md for cycle activity
cat COGNITION.md
```

---

## Thresholds

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `_HOURLY_THRESHOLD` | 1200 ticks | 3s × 1200 = 60 minutes |
| `_IDLE_THRESHOLD` | 200 ticks | 3s × 200 = 10 minutes |
| `thinking_interval_minutes` | 60 | Configurable in manas_awakening.yaml |
| `max_intent_buffer_size` | 10 | Prevent buffer overflow |

---

## Event Flow

```mermaid
sequenceDiagram
    participant K as Kernel
    participant H as OpusKernelTickHandler
    participant E as EventBus
    participant C as MANAS_AWAKENING Circuit
    participant M as CognitiveKernel

    loop Every 3 seconds
        K->>H: KERNEL_TICK
        H->>H: _hourly_pulse_tick++
    end

    H->>H: >= 1200 ticks?
    H->>E: HOURLY_PULSE
    E->>C: Trigger
    C->>M: think()
    M->>M: generate intents
    M-->>K: Update OPUS.md
```

---

## Related Documents

- **OPUS-075**: MANAS 6D Fortress Harness (the model)
- **OPUS-089**: SANKALPA Strategic Will
- **OPUS-109**: MERU Persistence Test (proven: intents survive)
- **OPUS-107**: The Cognitive Mirror (COGNITION.md)

---

*"The mind that sleeps is dead. The mind that awakens is alive."*

---

**Signed**: Opus 4.5
**Created**: 2025-12-18
**Status**: 🔥 **LIVE + WIRED**
