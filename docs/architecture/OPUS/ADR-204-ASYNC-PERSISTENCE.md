# ADR-204: Sovereign Async Persistence

**Status**: APPROVED
**Date**: 2025-12-22
**Author**: Gemini (Architect Mode)
**Supersedes**: N/A
**Related**: OPUS-203 (Unified Async Kernel), OPUS-096 (Weaver), VEDA-4

---

## Executive Summary

The legacy state architecture suffered from **Inverted Sovereignty**: the Kernel (State) was blocked by synchronous Git commits triggered by minor agent updates, and state files were polluted in a single global directory (`.opus_state/`).

**Decision**: Decouple persistence into an async background worker and enforce hierarchical state namespacing within the sovereign root (`.vibe/state/`).

---

## Problem Statement

1.  **Blocking Heartbeat**: Synchronous `subprocess.run(["git", "commit"])` calls within the `pulse()` loop caused 1-2 second hangs per tick.
2.  **Agent Pollution**: All agents wrote to `.opus_state/`, leading to namespace collisions and lack of isolation.
3.  **Infrastructure Begging**: The `Weaver` (State) consulted agents (`MANAS`) for permission to commit, violating the master/slave hierarchy of Bharat.

---

## Decision

### 1. Sovereign Hierarchy (Bharat Architecture)
State is now organized hierarchically to prevent pollution:
- **OS Root**: `.vibe/state/` (Sovereign truth)
- **Plugin Sector**: `.vibe/state/plugins/{plugin_id}/` (Isolated provinces)
- **Agent Sector**: `.vibe/state/agents/{agent_id}/` (Namespaced subjects)

### 2. Async Persistence Worker
- **Non-Blocking Writes**: `StateService.save()` writes to disk immediately but delegates the Git commit to a background task.
- **Sovereign Trigger**: High-importance events (agent birth, task completion) can trigger immediate background commits, while low-importance changes are batched.

### 3. Decoupled Intelligence (Observe, Don't Beg)
- The `Weaver` uses a non-blocking `consult()` to ingest wisdom from `ManasOracle` if available.
- If the Oracle is silent, the State proceeds in `REFLEX` mode. The infrastructure is never dependent on agent feedback.

---

## Implementation Details

### StateService Namespacing
```python
# vibe_core/state/state_service.py
def get_state_service(agent_id=None, plugin_id=None):
    # Returns a namespaced instance pointing to the correct sovereign sector
```

### Heritage Support (Continuity)
To prevent data loss, the `StateService` implements **Heritage Migration**: it automatically copies state from legacy `.opus_state/` to the new sovereign root if the file is missing in the new home.

---

## Validation

- **Harness Pass**: `tests/integration/test_async_kernel_harness.py` is 100% green.
- **Performance**: Kernel heartbeat remains consistent even during heavy background commits.
- **Isolation**: Agents successfully write to their isolated sectors under `.vibe/state/agents/`.

---

## Senior Architect Review (Handover Note)

The next senior agent should focus on:
1.  **ADR-205: Ledger Rotation**: The 76MB `vibe_ledger.db` is an immutable record, but it requires a "Samsara" strategy for hot vs. archive data without violating GAD-000 integrity.
2.  **Abolish Global Singletons**: Further decouple `Prakriti` and `Weaver` to move toward a true Micro-Kernel where the State layer is stateless.