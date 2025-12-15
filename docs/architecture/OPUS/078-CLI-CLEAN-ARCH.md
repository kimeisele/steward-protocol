# OPUS-078: Clean CLI & Envoy Delegation (The Clean Cut)

**Status:** DRAFT
**Author:** AntiGravity (via Senior User Guidance)
**Date:** 2025-12-15
**Scope:** Architecture Refactoring (CLI -> Plugin -> Envoy -> Execution)

---

## 1. The "Clean Cut" Philosophy

We are moving from a "Spaghetti" architecture (CLI knowing about Brains) to a "Lasagna" architecture (Layered & Decoupled).

- **Layer 1 (Kernel/CLI):** Dumb & Robust. "I execute what plugins tell me."
- **Layer 2 (Plugin):** Specific. "I provide `approve`, `karma` commands."
- **Layer 3 (Envoy):** Execution. "I am the Hand. I execute what the Brain (MANAS) decides."

## 2. The Harness (Verification Contract)

This document serves as the **Harness** for the refactoring. Without passing these checks, the documentation is irrelevant and the code is dead matter.

### @HARNESS: CLI-CLEANLINESS
> **Goal:** Ensure `UnifiedCLI` knows NOTHING about MANAS.

- [ ] **Input:** Scan `vibe_core/cli/unified_cli.py` source code.
- [ ] **Constraint:** `import .*manas.*` MUST NOT exist.
- [ ] **Constraint:** `IntentRouter` MUST NOT be referenced.
- [ ] **Constraint:** Hardcoded commands (`approve`, `karma`) MUST NOT exist in `__init__`.

### @HARNESS: ENVOY-DELEGATION
> **Goal:** Ensure `IntentRouter` (MANAS) delegates to Envoy (Hand).

- [ ] **Input:** Trigger `steward approve <id>`.
- [ ] **Constraint:** `IntentRouter.approve_intent` MUST call `envoy.execute_mission(intent)`.
- [ ] **Constraint:** `IntentRouter` MUST NOT call `handler(intent)` directly for execution.
- [ ] **Output:** Execution log MUST show "Envoy accepting mission".

## 3. Implementation Details

### Envoy's "Twist"
Envoy is not just a pass-through. It is a **Diplomat and Protocol Officer**.

```python
def execute_mission(self, intent):
    # 1. Log Acceptance
    logging.info(f"🕵️ ENVOY: Accepting mission {id}")
    # 2. Safety Check (optional)
    # 3. Execution & Signing
    result = self.execute(...)
    result['signed_by'] = 'Envoy'
    return result
```
