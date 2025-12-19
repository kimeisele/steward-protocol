# OPUS-124: Completing the Circuit

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-122 (Task Alignment)

## Summary

"Was routet, muss auch exekutieren." - "What routes, must also execute."

OPUS-124 fixes a critical bug in TaskManagerPlugin where tasks were marked
COMPLETED immediately after routing, without actually being executed.

## The Problem

### The "Air Gap" Was Actually a Missing Step

```
BEFORE (Broken):
┌─────────────────────────────────────────────────────────────────┐
│  TaskManagerPlugin._handle_actuators()                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Get next pending task                                       │
│  2. Mark IN_PROGRESS                                            │
│  3. router.route(prompt) → ExecutionRequest                     │
│  4. MARK COMPLETED IMMEDIATELY ← BUG!                           │
│                                                                  │
│  Never called: executor.execute(request)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**The Bug**: Line 264 marked tasks as COMPLETED after routing, but routing
only determines WHERE to send a task - it doesn't actually EXECUTE it.

This meant:
- Tasks appeared "completed" in the UI
- But the actual work was never done
- No execution = no result = phantom completions

### Root Cause

The code path was:
```python
# Route (determines destination)
route_res = router.route(prompt, source="TASK_MANAGER_PLUGIN")

# Missing: executor.execute(route_res)

# Immediately mark complete (BUG!)
self.manager.update_status(next_task.id, TaskStatus.COMPLETED)
```

## The Solution

### Complete the Circuit

```
AFTER (Fixed):
┌─────────────────────────────────────────────────────────────────┐
│  TaskManagerPlugin._handle_actuators()                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Get next pending task                                       │
│  2. Mark IN_PROGRESS                                            │
│  3. router.check_gate(request) → MilkOceanGate                  │
│     ├─ BLOCK → Mark BLOCKED, return                             │
│     ├─ QUEUE → Return (queued for later)                        │
│     └─ ALLOW/CRITICAL → Continue                                │
│  4. router.route(prompt) → ExecutionRequest                     │
│  5. executor.execute(request) → ExecutionResult ← NEW!          │
│     ├─ status="completed" → Mark COMPLETED                      │
│     └─ status="failed" → Mark FAILED                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Changes

```python
# OPUS-124: Get router AND executor
router = getattr(kernel, "router", None)
executor = getattr(kernel, "executor", None)

# Route to determine execution path
route_res = router.route(prompt, source="TASK_MANAGER_PLUGIN")

# OPUS-124: ACTUALLY EXECUTE (this was missing!)
if executor:
    exec_result = await executor.execute(route_res)

    if exec_result.status == "completed":
        self.manager.update_status(next_task.id, TaskStatus.COMPLETED)
    else:
        self.manager.update_status(next_task.id, TaskStatus.FAILED)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│             OPUS-124: Complete Execution Flow                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                                                       │
│  │ StoredTask   │ JsonTaskManager (State Sovereignty)                   │
│  │ id: uuid[:8] │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────┐                                                   │
│  │ UnifiedRouter    │ Decision: WHERE to execute                        │
│  │ .route()         │ Returns: ExecutionRequest with path               │
│  └──────┬───────────┘                                                   │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────┐                                                   │
│  │ UnifiedExecutor  │ Action: ACTUALLY execute                          │
│  │ .execute()       │ Returns: ExecutionResult with status              │
│  └──────┬───────────┘                                                   │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────┐                                                   │
│  │ Update Status    │ Based on ACTUAL result                            │
│  │ COMPLETED/FAILED │ Not optimistic assumption                         │
│  └──────────────────┘                                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/plugins/task_manager/plugin_main.py` | Added executor.execute() call, proper status handling |

## Why Not Bridge to DispatchTask?

Initial analysis suggested connecting TaskManagerPlugin to the kernel's
DispatchTask/on_task_completed system. This was rejected because:

1. **Parallel Universes**: StoredTask and DispatchTask are fundamentally
   different data models for different purposes
2. **Complexity**: Bridging would require ID mapping, event translation
3. **Simplicity**: The execution path already exists - just needed completion

The fix is surgical: complete the existing flow rather than building bridges.

## OPUS-122 Integration

This fix uses the canonical TaskStatus from `vibe_core.task_types`:

```python
# OPUS-122: Import TaskStatus from SSOT
from vibe_core.task_types import TaskStatus

# Now uses SSOT, not local enum
self.manager.update_status(next_task.id, TaskStatus.COMPLETED)
self.manager.update_status(next_task.id, TaskStatus.FAILED)
self.manager.update_status(next_task.id, TaskStatus.BLOCKED)
```

## Testing

Verify with:
```bash
pytest tests/ -k "task" -v
```

The fix ensures:
1. Tasks are only marked COMPLETED after successful execution
2. Failed executions result in FAILED status
3. Gate blocks result in BLOCKED status
4. No more phantom completions

## The Campaign Against Entropy

| OPUS | Problem | Solution |
|------|---------|----------|
| **118** | Split-Brain (CircuitState) | Canonical circuit_types.py |
| **120** | Duplicate Logic (1400 lines) | Thin proxy, single engine |
| **121** | Namespace Collision (Event) | Renamed to LedgerEvent |
| **122** | Split-Brain + Collision (Task) | SSOT + DispatchTask rename |
| **124** | Incomplete Execution Flow | Complete the circuit |

## Related

- OPUS-122: Task Alignment (TaskStatus SSOT, used here)
- OPUS-118: Split-Brain Surgery (similar pattern)
