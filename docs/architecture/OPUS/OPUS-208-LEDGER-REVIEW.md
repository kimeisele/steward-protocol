# OPUS-208: Holistic Ledger Architecture Review

**Status**: DRAFT
**Date**: 2025-12-22
**Author**: Claude Opus (Senior Architecture Review)
**Supersedes**: ADR-205 (partial)
**Related**: GAD-000, OPUS-206, OPUS-207, ADR-204

---

<!-- @HARNESS
intent: "Verify critical ledger components and configuration"

files:
  - path: vibe_core/ledger.py
    required: true
  - path: vibe_core/state/ledger_state.py
    required: true
  - path: vibe_core/kernel_ops.py
    required: true
  - path: docs/architecture/OPUS/ADR-205-LEDGER-ROTATION.md
    required: true

semantic:
  - type: file_contains
    name: check_wal_mode
    path: vibe_core/ledger.py
    pattern: "PRAGMA journal_mode=WAL"
    rationale: "WAL mode is required for concurrency"

  - type: file_contains
    name: check_incremental_health
    path: vibe_core/kernel_ops.py
    pattern: "get_events_since"
    rationale: "Health checks must be incremental"
-->

## Executive Summary

The current Ledger architecture has **critical performance and reliability flaws** that will cause exponential degradation and potential data loss. This is not just a "76MB problem" - it's a **fundamental architectural issue** involving algorithmic complexity, concurrency locking, and crash safety.

**Core Finding**: `check_system_health()` performs O(n) full scans, and the default SQLite locking model causes readers to block writers. Furthermore, the proposed rotation mechanism lacks atomicity, creating a risk of broken hash chains.

---

## 1. Current Architecture Analysis

### 1.1 The Two Ledgers

The system has **two separate ledger subsystems** that operate independently:

| Component | File | Table | Purpose |
|-----------|------|-------|---------|
| **SQLiteLedger** | `vibe_core/ledger.py` | `ledger_events` | Main event store with hash chain |
| **LedgerState** | `vibe_core/state/ledger_state.py` | `prakriti_sync_events` | Git-Ledger sync binding |

**Problem**: These are not properly unified. Git commits write to LedgerState, but auditing uses SQLiteLedger.

### 1.2 Hash Chain Design (GAD-000 Compliant)

```
Event[0]  → hash(data + "0"*64)           = H₀
Event[1]  → hash(data + H₀)               = H₁
Event[n]  → hash(data + Hₙ₋₁)             = Hₙ
```

**Status**: ✅ Hash chain is correctly implemented in isolation.

### 1.3 The Schema & Indexing Gaps

**Critical Missing Indexes**:
- `event_type` - For filtering by event type (task_start, task_completed, etc.)
- `agent_id` - For per-agent queries
- `task_id` - For task lookups
- `timestamp` - For time-range queries

---

## 2. Critical Bottlenecks & Reliability Gaps

### 2.1 🔴 CRITICAL: The O(n) "Death Spiral"

**File**: `kernel_ops.py:22-69`
`check_system_health()` is called after EVERY task and performs a **full table scan**.
At 100k events, this creates **10,000+ full scans per session**. This is O(events × tasks).

### 2.2 🔴 CRITICAL: SQLite Concurrency (Locking)

**Problem**: The plan uses default SQLite settings (Rollback Journal).
When `check_system_health` (a Reader) runs, it acquires a shared lock. If an Agent tries to write (e.g., `task_completed`) during a long audit, it gets blocked (`SQLITE_BUSY`).
**Impact**: The UI freezes, and agents time out waiting for the DB lock.

### 2.3 🔴 CRITICAL: The "Samsara Gap" (Crash Safety)

The original rotation plan (ADR-205) proposed:
1. `shutil.move(db, archive)`
2. `_initialize_db()`
3. `_record_genesis()`

**Risk**: If power fails *after* step 1 but *before* step 3, the `vibe_ledger.db` is missing, and the system initializes a NEW, empty chain on restart. The cryptographic link to history is **permanently lost**.

### 2.4 🟡 MEDIUM: Signature Verification Overhead

**Problem**: If `verify_ledger` checks RSA/Ed25519 signatures synchronously in the main thread, a batch of 100 events can block the kernel for 50-100ms.

---

## 3. Call Sites Analysis

(Unchanged from original analysis - see Section 3 in previous draft)

---

## 4. Holistic Solution: Ledger 2.0

### 4.1 Philosophy

> "The Ledger should be WRITE-HEAVY, READ-LIGHT. Auditing should be INCREMENTAL. Rotation should be ATOMIC."

### 4.2 Architectural Changes

#### Phase 1: Immediate Performance & Concurrency Fixes (P0)

**1.1 Enable WAL Mode (Concurrency)**
To prevent Readers from blocking Writers, we **must** enable Write-Ahead Logging.
```python
# vibe_core/ledger.py -> _initialize_db
self.cursor.execute("PRAGMA journal_mode=WAL;")
self.cursor.execute("PRAGMA synchronous=NORMAL;")  # Balance safety/speed
```

**1.2 Add Indexes**
Add indexes on `event_type`, `agent_id`, `task_id`, `timestamp`.

**1.3 Incremental Health Check with Trust Anchor (Persistent)**
We cannot just store `last_checked_id` in RAM. We need the *hash* to verify the chain link, and it must survive restarts.
```python
# kernel_ops.py - PROPOSED FIX
def check_system_health(kernel: "RealVibeKernel") -> None:
    # 1. Load anchor from DB meta-table (avoids full scan on restart)
    # Tuple: (last_id, last_trusted_hash)
    anchor = kernel._ledger.get_meta('health_anchor') or (0, GENESIS_HASH)
    
    # 2. Query ONLY new events
    new_events = kernel._ledger.get_events_since(anchor[0])

    if new_events:
        # 3. Verify chain continuity using the anchor hash
        report, new_tail_hash = kernel._auditor.verify_incremental(new_events, start_hash=anchor[1])
        
        # 4. Persist new anchor atomically
        kernel._ledger.set_meta('health_anchor', (new_events[-1]['id'], new_tail_hash))
```

#### Phase 2: Crash-Safe Samsara Rotation (P1)

**2.1 The "Manifest" Protocol (Atomic Rotation)**
Instead of a naked `move`, we use a two-phase commit via a manifest file.

1. **Prepare**: Write `rotation_state.json` containing:
   ```json
   {
     "state": "rotating",
     "target_archive": "data/ledger/archive/2025-12-22.db",
     "genesis_hash": "a1b2c3..." 
   }
   ```
2. **Execute**: Move `vibe_ledger.db` to target.
3. **Re-Initialize**: Create new DB, insert Genesis event linking to `genesis_hash`.
4. **Finalize**: Delete `rotation_state.json`.

**Recovery**: On boot, if `rotation_state.json` exists, the system knows a rotation was interrupted and can repair the state.

**2.2 UnifiedLedgerReader (Accessing "Dark Data")**
To solve the "Write-Only Archive" problem, we implement a reader that can attach archives.

> **⚠️ WARNING**: SQLite has a hard limit on attached databases (default `SQLITE_MAX_ATTACHED = 10`). The Reader must NOT attach all archives. It must implement a **dynamic mount strategy** (mount/unmount) based on the requested time range.

```sql
-- Dynamic SQL generation in UnifiedLedgerReader
ATTACH DATABASE 'data/ledger/archive/2025-12-22.db' AS archive_1;
SELECT * FROM archive_1.ledger_events WHERE ...;
DETACH DATABASE archive_1; -- Cleanup to respect limits
```

#### Phase 3: Unified Ledger Layer

**3.1 Merge SQLiteLedger + LedgerState**
(See previous draft for UnifiedLedger class structure)

---

## 5. Implementation Priority

| Phase | Task | Effort | Impact | Priority |
|-------|------|--------|--------|----------|
| P0-1 | **Enable WAL Mode** | 15min | High | 🔴 CRITICAL |
| P0-2 | Add Indexes | 30min | High | 🔴 CRITICAL |
| P0-3 | **Fix Incremental Check (Trust Anchor)** | 2h | High | 🔴 CRITICAL |
| P1-1 | **Implement Atomic Rotation (Manifest)** | 4h | High | 🟡 HIGH |
| P1-2 | Implement UnifiedLedgerReader | 4h | Medium | 🟡 HIGH |
| P2-1 | Unify SQLiteLedger + LedgerState | 6h | Medium | 🟢 MEDIUM |
| P2-2 | Async Signature Verification | 4h | Low | 🟢 LOW |

---

## 6. Risk Analysis

### 6.1 Breaking Changes & Data Integrity

| Risk | Mitigation |
|------|------------|
| **Rotation Crash** | **Manifest Protocol** ensures we never lose the chain link. |
| **Lock Contention** | **WAL Mode** isolates readers from writers. |
| **Broken Chain** | **Trust Anchor** ensures incremental checks are mathematically sound. |

### 6.2 Verification Strategy

**Hash Chain Invariant**: The hash chain MUST remain unbroken across:
1. Individual events
2. Archive boundaries (Samsara rotation)
3. Git-Ledger syncs

---

## 7. Metrics & Observability

### 7.1 Health Metrics (Revised)

```json
{
    "ledger": {
        "mode": "WAL",
        "hot_events": 4532,
        "archive_count": 28,
        "rotation_state": "idle",
        "last_anchor": "id:4500 hash:a1b2..."
    }
}
```

---

## Appendix A: File References

| File | Lines | Purpose |
|------|-------|---------|
| `vibe_core/ledger.py` | 1-559 | SQLiteLedger implementation |
| `vibe_core/state/ledger_state.py` | 1-366 | LedgerState wrapper |
| `vibe_core/kernel_ops.py` | 22-69 | check_system_health() |

---

**Author Notes**:
This review has been updated to address critical concurrency and safety concerns. The "Samsara Gap" and "WAL Mode" are non-negotiable requirements for a production-grade system.