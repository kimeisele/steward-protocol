# OPUS-078: MANAS Execution Loop - Closing the Circuit

**Scope:** Wire Intent Execution in Headless Mode
**Philosophy:** Intents without execution are wishes. The loop must close.
**Goal:** `manas.think()` → Intent Generated → Intent Executed → Memory Updated

---

## The Problem

Prior to OPUS-078, MANAS generated intents but never executed them:

```
MANAS.think() → Intent → "circuit_queued" → STOP (dead end)
```

The `_execution_callback` hook existed but was never wired. Intents were filed, logged, and forgotten.

---

## The Fix

**3 lines. Zero spaghetti.**

The `IntentRouter` already had a factory function `create_execution_callback()` designed for this exact purpose. We simply connected the wires in `heartbeat.py`.

---

## The Harness

<!-- @HARNESS
files:
  # === EXECUTION LOOP COMPONENTS ===
  - path: scripts/heartbeat.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true

wiring:
  # === FACTORY PATTERN ===
  # IntentRouter provides the factory
  - pattern: "def create_execution_callback"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py

  # === HEARTBEAT WIRING (OPUS-078) ===
  # Import the factory
  - pattern: "from vibe_core.plugins.opus_assistant.manas.intent_router import create_execution_callback"
    in: scripts/heartbeat.py

  # Create the callback
  - pattern: "create_execution_callback\\(workspace=project_root\\)"
    in: scripts/heartbeat.py

  # Wire to MANAS
  - pattern: "self\\.manas\\.set_execution_callback\\(callback\\)"
    in: scripts/heartbeat.py

  # === COGNITIVE KERNEL HOOKS ===
  # The hook must exist
  - pattern: "def set_execution_callback"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # The hook must be called
  - pattern: "self\\._execution_callback\\(intent\\)"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # === INTENT ROUTER HANDLERS ===
  # Router must handle different intent types
  - pattern: "class IntentRouter"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "def route"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py

semantic:
  # === CALLBACK SIGNATURE ===
  - type: method_exists
    name: execution_callback_factory
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
    method: create_execution_callback

  - type: method_exists
    name: cognitive_kernel_set_callback
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    class: CognitiveKernel
    method: set_execution_callback

  # === EXECUTION COMPLETENESS ===
  - type: method_exists
    name: intent_router_route
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
    class: IntentRouter
    method: route
-->

---

## Architecture

```
                    HEARTBEAT.PY
                         │
                         │ 1. Creates callback via factory
                         │    callback = create_execution_callback(workspace)
                         ▼
┌─────────────────────────────────────────────────┐
│              COGNITIVE KERNEL                    │
│                                                  │
│  __init__()                                      │
│    └── _execution_callback = None               │
│                                                  │
│  set_execution_callback(callback) ◄─────────────│ 2. Wires callback
│    └── _execution_callback = callback           │
│                                                  │
│  think() ───► _execute_auto()                   │
│                    │                             │
│                    ▼                             │
│              _execution_callback(intent) ───────│► 3. Executes!
│                                                  │
└─────────────────────────────────────────────────┘
                         │
                         │ 4. Routes to handler
                         ▼
┌─────────────────────────────────────────────────┐
│               INTENT ROUTER                      │
│                                                  │
│  route(intent) ──► handler.execute()            │
│    │                                            │
│    ├─ code → CodeHandler                        │
│    ├─ docs → DocsHandler                        │
│    ├─ tests → TestHandler                       │
│    ├─ refactor → RefactorHandler                │
│    └─ circuit → CircuitHandler                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Verification

```bash
# Verify harness
steward verify 078

# Test the loop manually
python -c "
from pathlib import Path
from scripts.heartbeat import HeartbeatEngine

engine = HeartbeatEngine(Path('.'))
print('MANAS callback:', engine.manas._execution_callback)
# Should print: <function callback at ...>
"

# Full integration
python scripts/heartbeat.py
# Look for: "MANAS: Execution callback wired (IntentRouter)"
```

---

## What This Unlocks

With the execution loop closed:

| Before OPUS-078 | After OPUS-078 |
|-----------------|----------------|
| Intents logged, never run | Intents route to handlers |
| "circuit_queued" placeholder | Actual circuit execution |
| Memory never updates | Success/failure recorded |
| System observes, doesn't act | System observes AND acts |

---

## Design Decisions

**Why not hardcode handlers in heartbeat?**
- The `IntentRouter` already exists with full handler registry
- Factory pattern keeps heartbeat dumb (as it should be)
- Adding handlers = modify router, not heartbeat

**Why use the existing factory?**
- `create_execution_callback()` was designed for this
- It creates the router and returns a clean callback
- Single responsibility: heartbeat carries, router executes

**Is this spaghetti?**
- No. This is Inversion of Control (IoC)
- MANAS defines WHAT (intents)
- Router defines HOW (handlers)
- Heartbeat defines WHEN (schedule)
- Clean separation of concerns

---

*"The loop was always there. We just forgot to plug it in."*
