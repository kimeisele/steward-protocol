# OPUS-090: DUAL CORE ARCHITECTURE (ENVOY & MANAS)

**Scope:** Architectural separation between Reactive Router (ENVOY) and Proactive Cognition (MANAS)
**Philosophy:** Two minds, one body. ENVOY speaks to users. MANAS thinks in silence. Neither bypasses the other.
**Goal:** Prevent architectural erosion where MANAS becomes a "shadow router" that bypasses ENVOY.

---

## The Grand Separation

The Steward Protocol operates on a **bicameral architecture**:

```
                    ┌─────────────────────────────────────────┐
                    │              STEWARD KERNEL             │
                    │                                         │
    USER INPUT ────▶│  ┌─────────┐         ┌─────────┐       │
                    │  │  ENVOY  │         │  MANAS  │       │
                    │  │(Reaktiv)│         │(Proaktiv)│      │
                    │  └────┬────┘         └────┬────┘       │
                    │       │                   │             │
                    │       ▼                   ▼             │
                    │  ┌─────────┐         ┌─────────┐       │
                    │  │ AGENT   │         │ CORTEX  │       │
                    │  │  CITY   │         │ MODULES │       │
                    │  └─────────┘         └─────────┘       │
                    │                                         │
                    │       ▲                   ▲             │
                    │       └───────┬───────────┘             │
                    │               │                         │
                    │         ┌─────┴─────┐                   │
                    │         │  DHARMA   │  ◀── Bridge       │
                    │         │ (Avatar)  │                   │
                    │         └───────────┘                   │
                    └─────────────────────────────────────────┘
```

## Core Components

### ENVOY (The Grand Router)
- **Role:** Reactive execution of User Commands
- **Trigger:** Explicit input (CLI, API, Chat)
- **Scope:** High-level orchestration of Agent City
- **Files:** `vibe_core/cartridges/system/envoy/`
- **Law:** The User is King

### MANAS (The Cognitive Kernel)
- **Role:** Proactive system maintenance and optimization
- **Trigger:** Heartbeat (15min) or Event (Idle threshold)
- **Scope:** Internal consistency, self-healing via Cortex
- **Files:** `vibe_core/plugins/opus_assistant/manas/`
- **Law:** The Dharma (Config) is King

### DHARMA (The Bridge)
- **Role:** Avatar pattern connecting kernel-level (MANAS) to city-level (Agents)
- **Location:** `vibe_core/cartridges/agent_city/dharma/`
- **Services:** seek_guidance, bless_action, check_karma, mediate

---

## Wiring Rules

### FORBIDDEN Patterns
- MANAS MUST NOT bypass ENVOY to execute user-facing actions
- MANAS MUST NOT directly call Agent City cartridges (except via Dharma)
- MANAS Cortex handlers MUST NOT import from `vibe_core.cartridges.system.envoy.provider`

### ALLOWED Patterns
- MANAS MAY use DeterministicExecutor for internal task execution
- MANAS MAY request Agent City services via Dharma bridge
- ENVOY MAY query MANAS for insights (Analysis, Context)
- Heartbeat MAY call both ENVOY tasks and MANAS.think()

---

## The Harness

<!-- @HARNESS
files:
  # === ENVOY (Grand Router) ===
  - path: vibe_core/cartridges/system/envoy/cartridge_main.py
    required: true
  - path: vibe_core/cartridges/system/envoy/provider.py
    required: true
  - path: vibe_core/cartridges/system/envoy/deterministic_executor.py
    required: true

  # === MANAS (Cognitive Kernel) ===
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true

  # === DHARMA (Bridge) ===
  - path: vibe_core/cartridges/agent_city/dharma/cartridge_main.py
    required: true
  - path: vibe_core/cartridges/agent_city/dharma/observer.py
    required: true

  # === AGENT CITY (13 Cartridges) ===
  - path: vibe_core/plugins/agent_city/plugin_main.py
    required: true

wiring:
  # === LEGITIMATE BRIDGE ===
  # kernel_tick MAY use DeterministicExecutor (this is the sanctioned path)
  - pattern: "DeterministicExecutor"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py

  # === DHARMA OPUS CONNECTION ===
  # Dharma reaches UP to opus_assistant (Avatar pattern)
  - pattern: "_get_opus_plugin"
    in: vibe_core/cartridges/agent_city/dharma/cartridge_main.py

  # === MANAS EXECUTION CALLBACK ===
  # Heartbeat wires execution callback (gives MANAS hands)
  - pattern: "set_execution_callback"
    in: scripts/heartbeat.py

  # === ENVOY KERNEL INTEGRATION ===
  # Envoy is a ContextAwareAgent (proper kernel citizen)
  - pattern: "ContextAwareAgent"
    in: vibe_core/cartridges/system/envoy/cartridge_main.py

violations:
  # === FORBIDDEN: Direct Envoy Provider import in MANAS ===
  # If found, MANAS is bypassing the Grand Router
  - pattern: "from vibe_core.cartridges.system.envoy.provider import"
    in: vibe_core/plugins/opus_assistant/manas/*.py
    expected: 0
    message: "MANAS must not directly import Envoy provider - use Dharma bridge"

  # === FORBIDDEN: Direct Agent City calls from Cortex ===
  - pattern: "from vibe_core.cartridges.agent_city"
    in: vibe_core/plugins/opus_assistant/manas/cortex/*.py
    expected: 0
    message: "Cortex modules must not directly call Agent City - use IntentRouter"
-->

---

## Verification Commands

```bash
# Check for illegal ENVOY imports in MANAS
grep -r "from vibe_core.cartridges.system.envoy.provider" vibe_core/plugins/opus_assistant/manas/

# Check for illegal Agent City imports in Cortex
grep -r "from vibe_core.cartridges.agent_city" vibe_core/plugins/opus_assistant/manas/cortex/

# Verify legitimate DeterministicExecutor usage (should be in kernel_tick only)
grep -r "DeterministicExecutor" vibe_core/plugins/opus_assistant/
```

---

## Future Integration Path (Phase 2)

When MANAS needs to coordinate with Agent City:

1. MANAS generates Intent (e.g., `delegate_to_analyst`)
2. Intent routes to `_handle_dharma` in IntentRouter
3. Dharma validates via `bless_action`
4. If blessed, Dharma calls Agent City service
5. Result flows back through Dharma to MANAS

This preserves the separation while enabling cooperation.

---

*"Two minds, one purpose. The router speaks. The cognition thinks. Neither rules alone."*
