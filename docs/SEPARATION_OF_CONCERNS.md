# Separation of Concerns: Store vs Ledger

**Document Purpose:** Clarify the architectural distinction between two core persistence systems in VibeOS.

**Status:** Phase 3 consolidation documentation
**Date:** 2025-11-27

---

## Executive Summary

VibeOS has two separate persistence systems that serve fundamentally different purposes:

1. **Store** (`vibe_core/store/`) - Mutable state for CRUD operations
2. **Ledger** (`vibe_core/ledger.py`) - Immutable audit trail with tamper detection

This is intentional by design. Both systems coexist and should NOT be consolidated or merged.

---

## System 1: Store (MUTABLE)

**Location:** `vibe_core/store/sqlite_store.py`
**Alias:** `ArtifactStore` (for Phase 2 compatibility)

### Purpose
Store operational data that needs to be queried, updated, and managed throughout an agent's lifecycle.

### Design Characteristics
- **CRUD Operations:** Full Create, Read, Update, Delete
- **Mutable:** Data can be changed, deleted, modified
- **Query-Rich:** Multiple ways to retrieve data (by ID, UUID, owner, status, etc.)
- **Relationship Management:** Foreign keys, cascade deletes, normalization
- **Thread-Safe:** RLock for concurrent access, WAL mode for better concurrency

### What It Stores
- **Missions** - Project metadata, budget, status, phases
- **Tool Calls** - Audit trail of tool executions (args, results, duration)
- **Decisions** - Agent decisions with rationale and context
- **Agent Memory** - Key-value storage with TTL support
- **Playbook Runs** - Workflow execution metrics
- **Tasks** - Hierarchical task tracking (ARCH-006)
- **Artifacts** - SDLC artifacts (planning, code, tests, deployments)
- **Quality Gates** - Compliance check results
- **Domain Concepts/Concerns** - Business domain tracking
- **Trajectory** - Mission phase progression
- **Roadmaps** - Project roadmaps and milestones
- **Session Narrative** - Session-by-session project memory

### Example Usage
```python
from vibe_core.store import SQLiteStore

# Open store (persistent)
store = SQLiteStore(".vibe/state/vibe_agency.db")

# Create mission
mission_id = store.create_mission(
    mission_uuid="proj-123",
    phase="PLANNING",
    status="in_progress"
)

# Update mission
store.update_mission_status(mission_id, "completed")

# Query mission
mission = store.get_mission(mission_id)

store.close()
```

---

## System 2: Ledger (IMMUTABLE)

**Location:** `vibe_core/ledger.py`

### Purpose
Maintain an immutable, tamper-proof record of all significant events for compliance, auditing, and forensics.

### Design Characteristics
- **Append-Only:** New events added, old events never modified
- **Immutable:** No updates, no deletes (only reads from history)
- **Hash-Chained:** Each event includes SHA256 hash of previous event (Merkle chain)
- **Tamper Detection:** `verify_chain_integrity()` detects any data tampering
- **Event-Sourced:** Complete history of all agent activities
- **No Foreign Keys:** Independent from Store schema

### What It Records
- **Task Events:**
  - `task_start` - When a task begins
  - `task_completed` - When a task finishes successfully
  - `task_failed` - When a task encounters an error
- **Generic Events:**
  - Custom event types for governance actions
  - Agent ID, timestamp, details (JSON)
- **Hash Chain:**
  - Previous hash (cryptographic seal)
  - Current hash (this event's seal)
  - Enables tamper detection across entire history

### Implementations
- **InMemoryLedger** - Fast, volatile (testing only)
- **SQLiteLedger** - Persistent, hash-chained (production)

### Example Usage
```python
from vibe_core.ledger import SQLiteLedger

# Open ledger
ledger = SQLiteLedger("data/vibe_ledger.db")

# Record task start
ledger.record_start(task)

# Record task completion
ledger.record_completion(task, result)

# Query task result
event = ledger.get_task(task.task_id)

# Verify integrity (detects tampering)
integrity = ledger.verify_chain_integrity()
if integrity["corrupted"]:
    print("⚠️  CORRUPTION DETECTED!")

ledger.close()
```

---

## Key Differences Table

| Aspect | Store | Ledger |
|--------|-------|--------|
| **Mutability** | MUTABLE (CRUD) | IMMUTABLE (append-only) |
| **Operations** | Create, Read, Update, Delete | Create (append), Read only |
| **Primary Use** | Operational state | Audit trail |
| **Query Pattern** | Multiple rich queries | Sequential history |
| **Relationship Mgmt** | Foreign keys, cascades | Independent records |
| **Data Integrity** | Referential integrity | Cryptographic integrity |
| **Update Pattern** | Direct updates | Event-sourced (immutable) |
| **Storage Model** | Relational (normalized) | Event log (denormalized) |
| **Lifetime** | Active mission operations | Complete forensic history |

---

## When to Use Which System

### Use Store When:
- You need to query agent mission state (phase, status, budget)
- You need to update a mission's information
- You need to delete obsolete records (cascading cleanup)
- You need complex queries (by owner, status, phase, etc.)
- You're working with active agent operations

### Use Ledger When:
- You need an audit trail of what happened
- You need compliance/forensic data
- You need to detect tampering or data corruption
- You need to replay events or understand history
- You're building introspection/monitoring tools

### Use BOTH When:
- Recording a task execution (Store captures operational data, Ledger captures event for audit)
- Example: Agent completes a task
  - **Store:** Update mission status, record metrics, update budget
  - **Ledger:** Record task_completed event with hash chain

---

## Architectural Diagram

```
VibeKernel (Agent Orchestration)
         |
         ├─────────────────┬────────────────┐
         |                 |                |
         v                 v                v
    Scheduler          Scheduler       Agents
         |                 |                |
         └─────┬───────────┼────────────────┘
               |           |
        ┌──────v───────────v──────────┐
        |  Store (Operational)         |
        |  (Mutable CRUD)              |
        ├──────────────────────────────┤
        | - Missions                   |
        | - Tool Calls                 |
        | - Decisions                  |
        | - Agent Memory               |
        | - Artifacts                  |
        | - Quality Gates              |
        | - Task Tracking              |
        └──────────────────────────────┘
               |
        ┌──────v───────────────────────┐
        |  Ledger (Immutable)           |
        |  (Append-only + Hash Chain)   |
        ├──────────────────────────────┤
        | - Task Events (start/done)    |
        | - Governance Events           |
        | - Tamper Detection            |
        | - Forensic History            |
        └──────────────────────────────┘
```

---

## No Circular Dependencies

**Status:** ✅ Verified - No circular imports

- `vibe_core/store/` does NOT import from `vibe_core/ledger.py`
- `vibe_core/ledger.py` does NOT import from `vibe_core/store/`
- Both are independent systems that can be used separately

**Independence Principle:**
The Ledger records generic events without knowing about Store internals.
The Store operates independently without requiring Ledger writes.

---

## Phase 2 → Phase 3 Transition

### What Changed
- Store system was ported to Python (ARCH-001, ARCH-002, ARCH-003)
- Ledger was isolated as a separate concern
- Both systems now have independent schema and interfaces

### What Stayed the Same
- Both systems coexist in production
- No circular dependencies
- Clear separation of concerns

### What's Next (Phase 4)
- Optimize ledger queries for compliance reports
- Add ledger verification to system health checks
- Expand event types for richer forensics

---

## Docstring Guidelines

When working with Store or Ledger in code, include this distinction in docstrings:

```python
def process_task(self, task):
    """
    Process a task and record its lifecycle.

    This method demonstrates the separation of concerns:
    - Store (mutable): Update mission status, log tool calls, track decisions
    - Ledger (immutable): Record task_start and task_completed events for audit trail

    Args:
        task: Task object with task_id, agent_id, payload
    """
    # 1. Record task start in ledger (immutable audit trail)
    ledger.record_start(task)

    # 2. Update store with operational data (mutable state)
    store.update_mission_status(mission_id, "in_progress")

    try:
        # ... task execution ...
        result = execute_task(task)

        # 3. Record task completion in both systems
        ledger.record_completion(task, result)  # Immutable
        store.update_mission_status(mission_id, "completed")  # Mutable
    except Exception as e:
        # 4. Record failure in both systems
        ledger.record_failure(task, str(e))  # Immutable
        store.update_mission_status(mission_id, "failed")  # Mutable
        raise
```

---

## Verification Checklist (Phase 3)

- ✅ Store and Ledger are independent (no circular imports)
- ✅ Both systems serve distinct purposes (mutable vs immutable)
- ✅ No plans to merge or consolidate (keep separate)
- ✅ Documentation clarifies the distinction
- ✅ Code examples show proper usage of both systems
- ✅ Architectural diagrams show the relationship

---

## References

- **Store Implementation:** `vibe_core/store/sqlite_store.py`
- **Ledger Implementation:** `vibe_core/ledger.py`
- **Schema Design:** `docs/tasks/ARCH-001_schema.sql`
- **Store Architecture:** ARCH-002 (SQLiteStore CRUD)
- **Ledger Concept:** Append-only, immutable event log with cryptographic integrity

---

**Document Version:** 1.0
**Status:** ✅ Complete
**Last Updated:** 2025-11-27
**Next Review:** Phase 4 (if ledger optimization is planned)
