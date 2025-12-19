# OPUS-122: Task Alignment - Full Clarity

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-118 (Split-Brain Surgery), OPUS-121 (Semantic Clarity)

## Summary

"एकं सत्यं बहुधा वदन्ति" - "The truth is one, the wise call it by many names."

OPUS-122 addresses TWO problems:

1. **Split-Brain (TaskStatus)**: Three different TaskStatus enums with drift
2. **Namespace Collision (Task)**: Two different Task classes with same name

## The Problem

### TaskStatus Split-Brain (3 Divergent Enums)

```python
# scheduling/task.py
class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"        # ← Different name!
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"        # ← Unique state

# task_management/models.py
class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"  # ← Different name!
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"          # ← Unique state
    ARCHIVED = "ARCHIVED"        # ← Unique state

# plugins/task_manager/state_store.py
class TaskStatus(Enum):
    PENDING = "pending"          # ← LOWERCASE!
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
```

**Problems**:
- `RUNNING` vs `IN_PROGRESS` (same concept, different names)
- Casing inconsistency (UPPERCASE vs lowercase)
- State drift (TIMEOUT, ARCHIVED only in some)

### Task Namespace Collision

```python
# Which Task is this?
from vibe_core.scheduling.task import Task          # Dispatch envelope
from vibe_core.task_management.models import Task   # Project card

# Import collision - silent confusion
```

Both called `Task`, but fundamentally different:

| Aspect | Scheduling Task | Management Task |
|--------|-----------------|-----------------|
| Purpose | Agent dispatch | Project tracking |
| Fields | agent_id, payload | title, assignee, tags |
| Metaphor | "Message envelope" | "Project card" |
| Persistence | In-memory queue | TASKS.md, roadmaps |

**IMPORTANT**: Unlike OPUS-118/120, these are NOT duplicates to merge.
They are semantically different types that shared a name.

## The Solution

### 1. TaskStatus SSOT (Single Source of Truth)

Created `vibe_core/task_types.py`:

```python
class TaskStatus(str, Enum):
    """Canonical task lifecycle states (OPUS-122)."""

    # Core states (present in all systems)
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    # Extended states
    BLOCKED = "BLOCKED"     # task_management, state_store
    TIMEOUT = "TIMEOUT"     # scheduling
    ARCHIVED = "ARCHIVED"   # task_management

    @classmethod
    def from_string(cls, value: str) -> "TaskStatus":
        """Convert with alias support (RUNNING -> IN_PROGRESS)."""
        normalized = value.upper()
        if normalized == "RUNNING":
            return cls.IN_PROGRESS
        return cls(normalized)
```

### 2. Task Semantic Rename

```python
# BEFORE: Ambiguous
class Task:  # Which one?

# AFTER: Clear semantics
class DispatchTask:  # Message envelope (scheduling)
class Task:          # Project card (task_management)

# Semantic aliases for clarity
ManagedTask = Task   # When importing alongside DispatchTask
```

### Migration Paths

```python
# OLD (still works - backward compatible)
from vibe_core.scheduling.task import Task, TaskStatus
from vibe_core.task_management.models import Task, TaskStatus

# NEW (preferred - semantic clarity)
from vibe_core.task_types import TaskStatus              # SSOT
from vibe_core.scheduling.task import DispatchTask       # Dispatch unit
from vibe_core.task_management.models import ManagedTask # Project card
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│             OPUS-122: Task Alignment Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  SINGLE SOURCE OF TRUTH:                                                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  vibe_core/task_types.py                                          │  │
│  │  ─────────────────────────────────────────────────                │  │
│  │  class TaskStatus(str, Enum):                                     │  │
│  │    PENDING, IN_PROGRESS, COMPLETED, FAILED,                       │  │
│  │    BLOCKED, TIMEOUT, ARCHIVED                                     │  │
│  │                                                                    │  │
│  │  + normalize_status() for legacy format handling                  │  │
│  │  + RUNNING -> IN_PROGRESS alias                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                            ↑                                             │
│            ┌───────────────┼───────────────┐                            │
│            │               │               │                             │
│  ┌─────────┴─────────┐  ┌──┴──────────┐  ┌─┴────────────────┐          │
│  │ scheduling/task   │  │ models.py   │  │ state_store.py   │          │
│  │ ─────────────────  │  │ ──────────  │  │ ──────────────   │          │
│  │ class DispatchTask │  │ class Task  │  │ imports SSOT     │          │
│  │ (was: Task)        │  │ (ManagedTask│  │ lowercase compat │          │
│  │                    │  │  alias)     │  │ for JSON storage │          │
│  │ "Message envelope" │  │ "Project    │  │                  │          │
│  │                    │  │  card"      │  │                  │          │
│  └────────────────────┘  └─────────────┘  └──────────────────┘          │
│                                                                          │
│  SEMANTIC DISTINCTION:                                                   │
│  ─────────────────────                                                   │
│  DispatchTask = "A message sent to an agent"                            │
│  ManagedTask  = "A project item tracked in TASKS.md"                    │
│                                                                          │
│  One is a nerve impulse. One is a memory in the ledger.                 │
│  Same name was misleading. Now they speak their truth.                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/task_types.py` | **NEW** - SSOT for TaskStatus |
| `vibe_core/scheduling/task.py` | Task → DispatchTask, imports SSOT |
| `vibe_core/task_management/models.py` | Imports SSOT, adds ManagedTask alias |
| `vibe_core/plugins/task_manager/state_store.py` | Imports SSOT, lowercase compat |

## Backward Compatibility

All existing code continues to work:

```python
# These still work (aliases in place)
from vibe_core.scheduling.task import Task        # → DispatchTask
from vibe_core.scheduling.task import TaskStatus  # → re-exported from SSOT

from vibe_core.task_management.models import Task       # → unchanged
from vibe_core.task_management.models import TaskStatus # → re-exported from SSOT
```

## Verification

```python
from vibe_core.task_types import TaskStatus, normalize_status
from vibe_core.scheduling.task import Task, DispatchTask, TaskStatus as SchedStatus
from vibe_core.task_management.models import Task as MgmtTask, ManagedTask

# All verifications pass
assert Task is DispatchTask          # ✅ Alias works
assert ManagedTask is MgmtTask       # ✅ Alias works
assert SchedStatus is TaskStatus     # ✅ Same SSOT
assert normalize_status("RUNNING") == TaskStatus.IN_PROGRESS  # ✅ Alias
assert normalize_status("pending") == TaskStatus.PENDING      # ✅ Lowercase
```

## The Split-Brain Trilogy

| OPUS | Problem | Solution |
|------|---------|----------|
| **118** | Duplicate types (CircuitState) | Canonical `circuit_types.py` |
| **120** | Duplicate logic (1400 lines) | Thin proxy, single engine |
| **121** | Namespace collision (Event) | Renamed to LedgerEvent |
| **122** | Split-Brain + Collision (Task) | SSOT + DispatchTask rename |

## Philosophical Foundation

From the Rigveda:

**"एकं सत्यं बहुधा वदन्ति"** - "The truth is one, the wise call it by many names."

Before OPUS-122, the system had multiple "truths" for task status:
- RUNNING vs IN_PROGRESS (same concept, different names)
- UPPERCASE vs lowercase (same values, different cases)

Now there is ONE truth (`vibe_core.task_types.TaskStatus`), and the wise
can call it by different aliases (`normalize_status()`, `from_string()`).

The Task/DispatchTask distinction follows the same principle: they were
never the same truth - they were different concepts forced into the same name.
Now each speaks its own truth.

## Related

- OPUS-118: Split-Brain Surgery (unified duplicate types)
- OPUS-120: Logic Fusion (unified duplicate logic)
- OPUS-121: Semantic Clarity (distinguished Event/LedgerEvent)
- OPUS-122: Task Alignment (unified TaskStatus, distinguished Task types)

## Future Considerations

- **OPUS-123**: Import Audit - Automated detection of namespace collisions
- Consider adding deprecation warnings to aliases in future versions

---

## @HARNESS

**Files**:
- `/home/user/steward-protocol/vibe_core/task_types.py`
  - `TaskStatus` enum - SSOT for all task status values
  - States: PENDING, IN_PROGRESS, COMPLETED, FAILED, BLOCKED, TIMEOUT, ARCHIVED
  - `from_string()` - alias support (RUNNING → IN_PROGRESS)
  - `normalize_status()` - handles legacy formats (lowercase, aliases)
- `/home/user/steward-protocol/vibe_core/scheduling/task.py`
  - `DispatchTask` class - message envelope for agent dispatch (renamed from Task)
  - `Task` alias - backward compatibility
  - Imports TaskStatus from task_types.py (SSOT)
- `/home/user/steward-protocol/vibe_core/task_management/models.py`
  - `Task` class - project tracking card (unchanged name)
  - `ManagedTask` alias - semantic clarity when used alongside DispatchTask
  - Imports TaskStatus from task_types.py (SSOT)
- `/home/user/steward-protocol/vibe_core/plugins/task_manager/state_store.py`
  - Imports TaskStatus from task_types.py
  - Lowercase compatibility for JSON storage

**Wiring Pattern**:
```python
# SSOT for TaskStatus (all systems import from here)
from vibe_core.task_types import TaskStatus

# Semantic distinction for Task types
from vibe_core.scheduling.task import DispatchTask  # Message envelope
from vibe_core.task_management.models import ManagedTask  # Project card

# Backward compatibility
from vibe_core.scheduling.task import Task  # Alias to DispatchTask
assert Task is DispatchTask  # True

# Status normalization
TaskStatus.from_string("RUNNING")  # → TaskStatus.IN_PROGRESS
TaskStatus.from_string("pending")  # → TaskStatus.PENDING (uppercase)
```

**Validation**:
```python
from vibe_core.task_types import TaskStatus as TS1
from vibe_core.scheduling.task import TaskStatus as TS2
from vibe_core.task_management.models import TaskStatus as TS3
assert TS1 is TS2 is TS3  # True - all import same SSOT
```
