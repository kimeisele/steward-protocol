# OPUS-173: Intent-Backlog Bridge Fortress (MAYA SLAYER)

**Status:** PLANNING → FORTRESS
**Author:** OPUS (Claude)
**Created:** 2025-12-21
**Sanskrit:** संकल्प-कर्म सेतु (Sankalpa-Karma Setu) = Will-Action Bridge
**Philosophy:** "The mind that thinks but cannot act is Maya. The bridge destroys illusion."

---

## MAYA ALERT: The Illusion We're Fighting

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              THE MAYA                                        │
│                                                                             │
│   MANAS THINKS...          BUT USER SEES...          RESULT: DISCONNECT    │
│   ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐  │
│   │ IntentBuffer      │    │ BACKLOG.md        │    │ "Is MANAS even    │  │
│   │ - pending intents │ X  │ - [ ] user tasks  │  = │  working?"        │  │
│   │ - reasoning       │    │ - (nothing from   │    │                   │  │
│   │ - risk analysis   │    │    MANAS visible) │    │ MAYA = ILLUSION   │  │
│   └───────────────────┘    └───────────────────┘    └───────────────────┘  │
│                                                                             │
│   Evidence: manas_intents.json last updated 2025-12-18 (3 DAYS STALE)      │
│   Reason: MANAS only ticks when PRANA/KALA/Heartbeat runs!                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## GAD-000 VIOLATIONS (Critical)

This section identifies FOUNDATIONAL LAW violations that must be fixed.

### Violation 1: OBSERVABILITY FAILURE

**GAD-000 Test:** "Can an AI (or user) see the current state?"

```yaml
current_state:
  IntentBuffer: NOT observable by user (hidden in .opus_state/manas_intents.json)
  BACKLOG.md: Observable but DISCONNECTED from MANAS cognition

violation:
  - User cannot see what MANAS is thinking
  - User cannot observe intent queue state
  - No structured API to query pending intents

fix:
  - IntentBridge syncs pending intents to visible BACKLOG.md
  - Structured metadata preserved for AI parseability
```

### Violation 2: COMPOSABILITY FAILURE

**GAD-000 Test:** "Can operations be chained?"

```yaml
current_state:
  MANAS → generates Intent → IntentBuffer.add() → END (dead end)
  agenda_tools → AddTask → BACKLOG.md → END (separate dead end)

violation:
  - IntentBuffer output doesn't feed BACKLOG.md input
  - BACKLOG.md changes don't inform MANAS
  - No pipeline, no chaining

fix:
  - IntentBridge.sync_to_backlog(): IntentBuffer → BACKLOG.md
  - BacklogSense.perceive(): BACKLOG.md → MANAS awareness
  - Bidirectional composable flow
```

### Violation 3: DISCOVERABILITY FAILURE

**GAD-000 Test:** "Can an AI discover this tool exists?"

```yaml
current_state:
  - IntentBuffer has no CLI/API exposure
  - User cannot list pending MANAS intents
  - No `steward intents` or similar command

violation:
  - MANAS intents are invisible/undiscoverable
  - Human cannot review what MANAS wants to do
  - No approval workflow

fix:
  - BacklogSense makes intents discoverable via BACKLOG.md
  - Add `steward intent list` CLI command
  - Intent approval via completing BACKLOG task
```

### Violation 4: IDEMPOTENCY FAILURE RISK

**GAD-000 Test:** "Can operations be safely retried?"

```yaml
risk:
  - Multiple syncs could create duplicate BACKLOG entries
  - No deduplication key between IntentBuffer and BACKLOG

fix:
  - Use HTML comments for MANAS ID: <!-- manas:intent_id -->
  - Check for existing entry before append
  - Idempotent sync operation
```

---

## ANTI-PATTERNS TO GUARD AGAINST

Based on OPUS-075, OPUS-105, and GAD-000 analysis:

### Anti-Pattern 1: HARDCODED DISPATCH (VEDA-4 Violation)

```python
# BAD - What we're NOT doing
if source == "manas":
    sync_to_backlog()
elif source == "user":
    sync_to_buffer()

# GOOD - What we ARE doing (VEDA-4)
bridge.sync()  # Discovers sources via BacklogSense
```

### Anti-Pattern 2: PHANTOM WIRING

```yaml
# BAD - Looks wired but isn't
IntentBridge created but never called
BacklogSense created but not in SenseLoader

# GOOD - Actually wired
IntentBridge.sync_to_backlog() called in CognitiveKernel._persist()
BacklogSense registered in cortex/__init__.py
```

### Anti-Pattern 3: STALE STATE (The 3-Day Bug)

```yaml
# BAD - What happened
IntentBuffer updated: 2025-12-18
Current date: 2025-12-21
Delta: 3 DAYS STALE

# GOOD - What we need
IntentBuffer synced on every MANAS tick
BacklogSense perceives on every MANAS boot
No stale state > 1 hour
```

### Anti-Pattern 4: TICK DEPENDENCY WITHOUT TICK

```yaml
# BAD - Current state
MANAS only generates intents during tick()
tick() only runs when PRANA/Heartbeat calls it
Headless mode = No ticks = No intents

# GOOD - What we need
SessionStart hook triggers MANAS boot/tick
BacklogSense perceives independently of tick
IntentBridge syncs on any state change
```

---

## PRANA/KALA/HEARTBEAT Integration

The Intent-Backlog bridge must connect to the time orchestration layer:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TEMPORAL ORCHESTRATION LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   KALA (Time)              PRANA (Heartbeat)          MANAS (Mind)          │
│   ┌─────────────┐          ┌─────────────┐           ┌─────────────┐        │
│   │ CosmicClock │  ───────>│ Orchestrator│  ────────>│ tick()      │        │
│   │ - sun_phase │          │ - pulse()   │           │ - perceive  │        │
│   │ - is_day    │          │ - on_boot   │           │ - decide    │        │
│   └─────────────┘          └─────────────┘           │ - act       │        │
│                                   │                   └─────────────┘        │
│                                   │                          │               │
│                                   v                          v               │
│                            ┌─────────────┐           ┌─────────────┐        │
│                            │ kernel_tick │           │ IntentBuffer│        │
│                            │ - subscribe │           │ - add()     │        │
│                            │ - on_tick   │           │ - save()    │        │
│                            └─────────────┘           └─────────────┘        │
│                                                              │               │
│                                                              v               │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                      INTENT-BACKLOG BRIDGE (NEW)                       │ │
│   │                                                                        │ │
│   │   IntentBuffer ──────> IntentBridge ──────> BACKLOG.md                │ │
│   │                              ^                    │                    │ │
│   │                              │                    v                    │ │
│   │   MANAS <──────────── BacklogSense <────── (file watch)              │ │
│   │                                                                        │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Points

| Component | Hook | Action |
|-----------|------|--------|
| `kernel_tick.py` | `on_tick_post` | Call `IntentBridge.sync_to_backlog()` |
| `SessionStart hook` | `on_boot` | Boot BacklogSense, initial sync |
| `Weaver` | `commit_runtime_state` | Include BACKLOG.md in state sync |
| `BacklogSense` | `perceive()` | Watch BACKLOG.md for user changes |

---

## The Four Gates (Following OPUS-105 Pattern)

```
                           ┌─────────────────────────────────┐
                           │     SYNC OPERATION REQUESTED    │
                           └─────────────────────────────────┘
                                          │
                                          v
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 1: IDEMPOTENCY CHECK                                                    │
│                                                                              │
│   Does BACKLOG.md already contain this intent?                               │
│   Check: grep for <!-- manas:intent_id -->                                   │
│                                                                              │
│   Already exists -> Skip (no duplicate)                                      │
│   New intent -> Continue                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          v
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 2: FORMAT VALIDATION                                                    │
│                                                                              │
│   Is BACKLOG.md valid? (Has Outstanding/Completed sections)                  │
│                                                                              │
│   Invalid -> Create template, then continue                                  │
│   Valid -> Continue                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          v
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 3: PRIORITY MAPPING                                                     │
│                                                                              │
│   Map Intent priority/risk -> BACKLOG priority                               │
│   - CRITICAL/HIGH -> [HIGH]                                                  │
│   - MEDIUM -> [MEDIUM]                                                       │
│   - LOW/SAFE -> [LOW]                                                        │
│                                                                              │
│   Continue                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          v
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 4: APPEND & RECORD                                                      │
│                                                                              │
│   1. Format: "- [ ] [PRIORITY] Title <!-- manas:id -->"                      │
│   2. Append to Outstanding section                                           │
│   3. Record sync in IntentBuffer metadata                                    │
│   4. Log success                                                             │
│                                                                              │
│   SUCCESS -> Intent visible in BACKLOG.md                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Fortress Harness

<!-- @HARNESS
intent: "Verify Intent-Backlog Bridge connects MANAS cognition to user-visible backlog"

files:
  # === BRIDGE CORE ===
  - path: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    required: true
    rationale: "Core bridge between IntentBuffer and BACKLOG.md"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
    required: true
    rationale: "VEDA-4 sense for perceiving BACKLOG.md state"

  # === EXISTING DEPENDENCIES ===
  - path: vibe_core/plugins/opus_assistant/manas/intent_buffer.py
    required: true
    rationale: "Source of truth for cognitive intents"
  - path: vibe_core/tools/agenda_tools.py
    required: true
    rationale: "User-facing backlog tools"
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
    rationale: "MANAS brain - must call bridge in _persist()"

  # === TEMPORAL INTEGRATION ===
  - path: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    required: true
    rationale: "Must trigger sync on tick"
  - path: vibe_core/prana_orchestrator.py
    required: true
    rationale: "Heartbeat orchestration"

  # === TESTS ===
  - path: tests/manas/test_intent_bridge.py
    required: true
    rationale: "Bridge functionality tests"
  - path: tests/manas/cortex/test_backlog_sense.py
    required: true
    rationale: "BacklogSense tests"

wiring:
  # === BRIDGE CORE ===
  - pattern: "class IntentBridge"
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
  - pattern: "def sync_to_backlog"
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
  - pattern: "def sync_from_backlog"
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
  - pattern: "<!-- manas:"
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    rationale: "MANAS ID marker for idempotency"

  # === BACKLOG SENSE ===
  - pattern: "class BacklogSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
  - pattern: "def perceive"
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
  - pattern: "def get_boot_summary"
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
    rationale: "OPUS-172 polymorphic interface"

  # === COGNITIVE KERNEL INTEGRATION ===
  - pattern: "_intent_bridge"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    rationale: "Bridge instance in kernel"
  - pattern: "sync_to_backlog"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    rationale: "Bridge called in _persist()"

  # === VEDA-4 LOADER REGISTRATION ===
  - pattern: "backlog_sense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/__init__.py
    rationale: "BacklogSense must be discoverable by SenseLoader"

semantic:
  # === GAD-000 COMPLIANCE ===
  - type: gad_000_observability
    name: intents_observable
    rationale: "User can see MANAS intents in BACKLOG.md"
    check: "<!-- manas: markers in workspace/BACKLOG.md"

  - type: gad_000_composability
    name: bridge_composes
    rationale: "IntentBuffer -> IntentBridge -> BACKLOG.md chain works"
    check: "IntentBridge has both sync_to and sync_from methods"

  - type: gad_000_idempotency
    name: sync_idempotent
    rationale: "Multiple syncs don't create duplicates"
    check: "_is_in_backlog() check before append"

  # === ANTI-PATTERN GUARDS ===
  - type: no_hardcoded_dispatch
    name: no_source_switch
    pattern: "if source == "
    not_in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    rationale: "No hardcoded source dispatching"

  - type: no_stale_state
    name: sync_on_persist
    check: "sync_to_backlog called in _persist()"
    rationale: "Every MANAS tick syncs to BACKLOG"

  # === METHOD VERIFICATION ===
  - type: method_exists
    name: bridge_sync_to
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    class: IntentBridge
    method: sync_to_backlog

  - type: method_exists
    name: bridge_sync_from
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    class: IntentBridge
    method: sync_from_backlog

  - type: method_exists
    name: sense_perceive
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
    class: BacklogSense
    method: perceive

  - type: class_inherits
    name: backlog_sense_is_sense
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
    class: BacklogSense
    parent: BaseSense

tests:
  # Core tests
  - tests/manas/test_intent_bridge.py
  - tests/manas/cortex/test_backlog_sense.py
  # Integration tests
  - tests/manas/test_manas_integration.py
  # Idempotency tests
  - tests/manas/test_intent_bridge_idempotency.py

config:
  - section: opus_assistant.intent_bridge
    file: vibe_core/plugins/opus_assistant/defaults.yaml
    rationale: "Bridge configuration (sync interval, enabled flag)"
-->

---

## Fire Commands

```bash
# Verify fortress harness
steward verify 173

# Test bridge sync
python -c "
from vibe_core.plugins.opus_assistant.manas.intent_bridge import IntentBridge
from vibe_core.plugins.opus_assistant.manas.intent_buffer import IntentBuffer
from pathlib import Path

buffer = IntentBuffer(Path.cwd())
bridge = IntentBridge(Path.cwd(), buffer)
synced = bridge.sync_to_backlog()
print(f'Synced {synced} intents to BACKLOG.md')
"

# Test BacklogSense
python -c "
from vibe_core.plugins.opus_assistant.manas.cortex.backlog_sense import BacklogSense
from pathlib import Path

sense = BacklogSense(Path.cwd())
perception = sense.perceive()
print(f'Outstanding: {perception.outstanding_count}')
print(f'MANAS tasks: {len(perception.manas_tasks)}')
print(f'User tasks: {len(perception.user_tasks)}')
"

# Check BACKLOG.md for MANAS markers
grep -o '<!-- manas:[^>]*-->' workspace/BACKLOG.md 2>/dev/null || echo "No MANAS tasks yet"
```

---

## Success Criteria

| Criterion | Test | Pass Condition |
|-----------|------|----------------|
| **Visibility** | Check BACKLOG.md | MANAS intents visible with `<!-- manas: -->` markers |
| **Bidirectional** | Add task manually | BacklogSense detects within 1 tick |
| **Idempotent** | Run sync 3x | No duplicate entries |
| **No Stale** | After MANAS tick | IntentBuffer and BACKLOG.md synchronized |
| **GAD-000** | Run all 6 tests | All pass (Observe, Compose, Discover, Parse, Idempotent, Identity) |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Sync conflicts | Medium | High | IntentBuffer is source of truth |
| Format corruption | Low | High | Validate before write, backup |
| Duplicate entries | Medium | Medium | Idempotency via MANAS ID markers |
| Performance | Low | Low | Lazy sync only on _persist() |
| User confusion | Medium | Medium | Clear `<!-- manas: -->` prefix |

---

## Dependencies

- **OPUS-167**: IntentBuffer extraction (DONE)
- **OPUS-168**: OODA Loop / Chitta integration (DONE)
- **OPUS-172**: VEDA-4 Knowledge Integration (DONE - this session)
- **GAD-000**: Operator Inversion Principle (FOUNDATIONAL)

---

## Implementation Order

1. **IntentBridge core** (`intent_bridge.py`)
   - sync_to_backlog()
   - sync_from_backlog()
   - _is_in_backlog() idempotency check
   - _format_intent_as_task()
   - _parse_task_as_intent()

2. **BacklogSense** (`cortex/backlog_sense.py`)
   - perceive() -> BacklogPerception
   - get_boot_summary() -> OPUS-172 interface
   - generate_intents() -> for untracked user tasks

3. **CognitiveKernel integration**
   - Add _intent_bridge instance
   - Call sync_to_backlog() in _persist()

4. **Tests**
   - test_intent_bridge.py
   - test_backlog_sense.py
   - test_intent_bridge_idempotency.py

5. **Config**
   - Add intent_bridge section to defaults.yaml

---

## The Mantra

```
"MANAS thinks in silence. The bridge speaks to the world.
 What was hidden becomes visible. What was Maya becomes truth.
 The Will (Sankalpa) becomes Action (Karma) through the Bridge (Setu)."
```

---

**Related Docs:**
- [OPUS-075: MANAS Neural Fortress](075-MANAS-RELIABILITY.md) - The original fortress
- [OPUS-105: Genesis Fortress](105-GENESIS-FORTRESS.md) - Four Pillars pattern
- [OPUS-172: VEDA-4 Knowledge Integration](172-AKSHARA-ANALYSIS.md) - Knowledge engines
- [GAD-000: Operator Inversion](../GAD-0XX/GAD-000.md) - Foundational Law
