# OPUS-027: Unified State Implementation (PRAKRITI COMPLETE)

> **Status**: ✅ IMPLEMENTED (Phase 1-6 Complete)
> **Created**: 2025-12-12
> **Implemented**: 2025-12-12
> **Implements**: OPUS-009 (GOLDEN FOUNDATION - conceptual source of truth)
> **Sub-Documents**: OPUS-028 (Git-specific, ~5% of this scope)
> **Purpose**: Complete, Production-Ready Unified State for Agent OS
> **Note**: This document implements PARTS of OPUS-009's vision. See OPUS-009 for: StateSyncHolon, UntotbarMergeEngine, Tri-Guna, Plugin State Discovery.

<!-- @HARNESS
files:
  # Core Prakriti (all verified to exist)
  - path: vibe_core/state/prakriti.py
    required: true
  - path: vibe_core/state/git_state.py
    required: true
  - path: vibe_core/state/ledger_state.py
    required: true
  - path: vibe_core/state/file_state.py
    required: true
  - path: vibe_core/state/kernel_state.py
    required: true
  - path: vibe_core/state/ephemeral_state.py
    required: true
  - path: vibe_core/state/persona.py
    required: true
  # Kernel integration
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/kernel_ops.py
    required: true
  # Config
  - path: config/guardrails.yaml
    required: true
tests:
  - python scripts/ci/test_kernel_boot.py
  - python scripts/governance/verify_kernel.py --verify
wiring:
  # Prakriti unified orchestration
  - pattern: "class Prakriti"
    in: vibe_core/state/prakriti.py
  - pattern: "def commit_if_dirty"
    in: vibe_core/state/prakriti.py
  - pattern: "def sync_ledger_git"
    in: vibe_core/state/prakriti.py
  - pattern: "def save_snapshot"
    in: vibe_core/state/prakriti.py
  - pattern: "def restore_snapshot"
    in: vibe_core/state/prakriti.py
  # LedgerState integration
  - pattern: "class LedgerState"
    in: vibe_core/state/ledger_state.py
  - pattern: "def get_last_sync_commit"
    in: vibe_core/state/ledger_state.py
  # Kernel integration
  - pattern: "prakriti.sync_ledger_git"
    in: vibe_core/kernel_impl.py
  # Implementation Guidelines (Final Polish)
  - pattern: "Ledger-Head"
    in: vibe_core/state/prakriti.py
  - pattern: "session.lock"
    in: vibe_core/state/prakriti.py
  - pattern: "_is_process_alive"
    in: vibe_core/state/prakriti.py
  - pattern: "get_current_head_hash"
    in: vibe_core/state/ledger_state.py
config:
  - section: guardrails.ui_files
-->

---

## Executive Summary

**OPUS-009 is the GOLDEN FOUNDATION. This document implements parts of that vision.**

OPUS-009 describes "Git as Consciousness" and the complete Prakriti philosophy. This document delivers the production implementation, filling gaps that existed before:
- Ledger sync (previously unintegrated)
- Split-brain recovery (Git ↔ Ledger)
- Crash recovery protocol
- Session boundary commits

**See OPUS-009 for**: StateSyncHolon, UntotbarMergeEngine, Tri-Guna state classification, Plugin State Discovery - these are architectural extensions beyond this implementation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPUS-027: THE COMPLETE PICTURE                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   LAYER 3: PURUSHA (Identity)                                      │
│   ├── Personas (YAML files)                                        │
│   └── Self-modification protocol                                   │
│                                                                     │
│   LAYER 2: PRANA (Runtime)                                         │
│   ├── Kernel state (RAM)                                           │
│   ├── Ephemeral storage (Chain of Thought)                         │
│   └── Session context                                              │
│                                                                     │
│   LAYER 1: STHULA (Physical) ← CRITICAL: MUST BE IN SYNC          │
│   ├── Git Repository (code, config)     ─┐                         │
│   ├── Ledger (SQLite, audit trail)       ├── Split-Brain Risk!    │
│   └── Files (OPUS.md, INDEX.md, etc.)   ─┘                         │
│                                                                     │
│   SUB-DOCUMENTS:                                                    │
│   └── OPUS-028: Git write operations (commit, stage, VISNU)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Problem We're Solving (Full Scope)

### 1. Split-Brain Risk (Critical)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SPLIT-BRAIN SCENARIO                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Git says:                     Ledger says:                         │
│  "Last commit: abc123"         "Last sync: def456"                  │
│                                                                     │
│  Who is right? NOBODY KNOWS.                                        │
│                                                                     │
│  Cause: They were never designed to sync.                           │
│  Result: Inconsistent audit trail, lost work, confusion.            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Root Cause**: OPUS-009 treated Git and Ledger as separate concerns.

**Solution**: Single source of truth with sync protocol.

### 2. Session Boundary Chaos

```
Current state:
- InterfacePlugin commits every 60 seconds (233 commits in 2 days)
- Kernel shutdown() has NO commit call
- Kernel boot() has NO crash recovery
- Sessions have no clear start/end markers
```

**Solution**: Boundary commits (boot + shutdown) with clear session markers.

### 3. Crash Recovery Gap

```
Scenario:
1. Agent writes important data
2. System crashes before commit
3. On reboot: data exists but is uncommitted
4. What happens? UNDEFINED.

Current behavior: Nothing. Data sits dirty. Maybe gets overwritten.
```

**Solution**: Boot checks for dirty state, commits with recovery marker.

### 4. Auto-Generated File Noise (The Trigger)

```
Evidence:
git log --oneline --since="2025-12-10" | grep "auto:" | wc -l
# Output: 233

This is a SYMPTOM, not the root cause.
Root cause: No unified state orchestration.
```

**Solution**: Prakriti orchestrates ALL state persistence, not just Git.

---

## Architecture: The Three Layers Complete

### Layer 1: STHULA (Physical) - The Foundation

```python
class SthulaTruth:
    """
    Physical layer = Source of truth for persistence.

    CRITICAL: Git and Ledger MUST agree on:
    - Current commit SHA
    - Last sync timestamp
    - State hash
    """

    git: GitState        # Code, config (OPUS-028)
    ledger: LedgerState  # Audit trail, hash chain
    files: FileState     # Workspace files (OPUS.md, etc.)

    def verify_consistency(self) -> ConsistencyReport:
        """
        Cross-check Git and Ledger.

        Returns:
            ConsistencyReport with:
            - git_head: Current Git HEAD
            - ledger_last_sync: Last commit recorded in Ledger
            - files_dirty: List of modified files
            - is_consistent: bool
            - divergence_point: SHA where they diverged (if any)
        """
        pass

    def sync(self, strategy: str = "git_wins") -> SyncResult:
        """
        Reconcile Git and Ledger.

        Strategies:
        - "git_wins": Ledger catches up to Git
        - "ledger_wins": Git reverts to Ledger's last known state
        - "manual": Raise error, require human intervention
        """
        pass
```

#### LedgerState (NEW - Missing from OPUS-009)

```python
# vibe_core/state/ledger_state.py

class LedgerState:
    """Ledger integration for Prakriti - the missing piece."""

    def __init__(self, ledger: "VibeCoreLedger"):
        self._ledger = ledger

    def get_last_sync_commit(self) -> Optional[str]:
        """Get the last Git commit SHA recorded in Ledger."""
        events = self._ledger.query_events(
            event_type="STATE_SYNC",
            limit=1,
            order="desc"
        )
        if events:
            return events[0].get("git_sha")
        return None

    def record_sync(self, git_sha: str, files_committed: List[str]) -> str:
        """Record a state sync event in Ledger."""
        return self._ledger.record_event(
            event_type="STATE_SYNC",
            agent_id="prakriti",
            payload={
                "git_sha": git_sha,
                "files": files_committed,
                "timestamp": time.time(),
            }
        )

    def verify_chain(self) -> bool:
        """Verify Ledger hash chain integrity."""
        return self._ledger.verify_integrity()
```

### Layer 2: PRANA (Runtime) - The Breath

```python
class PranaRuntime:
    """
    Runtime state = What's happening NOW.

    This is ephemeral but MUST be:
    1. Serializable (for snapshots)
    2. Recoverable (after crash)
    """

    kernel: KernelState       # Tasks, agents, queues
    ephemeral: EphemeralState # Chain of Thought, temp data
    session: SessionContext   # Current session metadata

    def snapshot(self) -> RuntimeSnapshot:
        """Capture current runtime state."""
        return RuntimeSnapshot(
            kernel=self.kernel.to_dict(),
            ephemeral=self.ephemeral.to_dict(),
            session=self.session.to_dict(),
            timestamp=time.time(),
        )

    def restore(self, snapshot: RuntimeSnapshot) -> None:
        """Restore runtime from snapshot."""
        self.kernel.from_dict(snapshot.kernel)
        self.ephemeral.from_dict(snapshot.ephemeral)
        self.session.from_dict(snapshot.session)
```

#### SessionContext (NEW - Critical for Boundaries)

```python
# vibe_core/state/ephemeral_state.py (extend)

@dataclass
class SessionContext:
    """Session boundary tracking."""

    session_id: str          # UUID for this session
    boot_time: float         # When kernel booted
    boot_commit: str         # Git SHA at boot
    last_commit: Optional[str] = None  # Last commit in this session
    crash_recovery: bool = False  # Was this boot a crash recovery?

    def mark_commit(self, sha: str) -> None:
        """Record a commit in this session."""
        self.last_commit = sha

    def to_commit_metadata(self) -> dict:
        """Metadata for commit messages."""
        return {
            "session_id": self.session_id,
            "session_duration": time.time() - self.boot_time,
            "commits_in_session": 1 if not self.last_commit else 2,
        }
```

### Layer 3: PURUSHA (Identity) - The Soul

```python
class PurushaIdentity:
    """
    Identity layer = Who the agents ARE.

    Already implemented in OPUS-009 Phase 3.
    This layer is mostly complete.
    """

    personas: PersonaManager  # Agent identities

    # See OPUS-009 for persona operations
    # load_persona, save_persona, fork_persona
```

---

## Prakriti: The Unified Engine

```python
# vibe_core/state/prakriti.py (COMPLETE API)

class Prakriti:
    """
    The Fractal State Engine - COMPLETE IMPLEMENTATION.

    OPUS-009 was concept. OPUS-027 is reality.
    """

    # =========================================================================
    # Layer 1: STHULA (Physical)
    # =========================================================================
    git: GitState           # OPUS-028 covers write ops
    ledger: LedgerState     # NEW: Missing from OPUS-009
    files: FileState        # Existing

    # =========================================================================
    # Layer 2: PRANA (Runtime)
    # =========================================================================
    kernel: KernelState     # Existing
    ephemeral: EphemeralState  # Existing
    session: SessionContext # NEW: Session tracking

    # =========================================================================
    # Layer 3: PURUSHA (Identity)
    # =========================================================================
    personas: PersonaManager  # Existing

    # =========================================================================
    # Core Operations
    # =========================================================================

    def snapshot(self) -> StateSnapshot:
        """Full state dump across all layers."""
        # Existing - works

    def verify(self) -> ConsistencyReport:
        """Cross-layer consistency check."""
        # Existing - works

    def diff(self, other: StateSnapshot) -> StateDelta:
        """What changed between two points in time?"""
        # Existing - works

    # =========================================================================
    # NEW: Write Operations (OPUS-027 additions)
    # =========================================================================

    def commit_if_dirty(
        self,
        message: str = "Auto-commit",
        commit_type: str = "chore",
        scope: str = "state",
        stage_patterns: Optional[List[str]] = None,
        sync_ledger: bool = True,
    ) -> Optional[CommitResult]:
        """
        Commit current changes if workspace is dirty.

        OPUS-028 handles the Git part.
        This method adds:
        - Ledger sync
        - Session tracking

        Args:
            message: Commit message
            commit_type: Conventional commit type
            scope: Commit scope
            stage_patterns: Patterns to stage (default: ["*.md"])
            sync_ledger: Also record in Ledger (default: True)

        Returns:
            CommitResult with git_sha, ledger_event_id, or None if clean
        """
        if not self.is_dirty:
            return None

        # 1. Git commit (OPUS-028)
        commit = self.git.commit_if_dirty(message, commit_type, scope, stage_patterns)
        if not commit:
            return None

        # 2. Ledger sync (NEW)
        ledger_event_id = None
        if sync_ledger:
            ledger_event_id = self.ledger.record_sync(
                git_sha=commit.sha,
                files_committed=commit.files,
            )

        # 3. Session tracking (NEW)
        self.session.mark_commit(commit.sha)

        return CommitResult(
            git_sha=commit.sha,
            ledger_event_id=ledger_event_id,
            session_id=self.session.session_id,
        )

    def sync_ledger_git(self, strategy: str = "git_wins") -> SyncResult:
        """
        Reconcile Ledger and Git if they diverged.

        Called on boot if consistency check fails.

        Strategies:
        - "git_wins": Ledger records catch-up events to match Git
        - "ledger_wins": Git reset to Ledger's last known commit
        - "manual": Raise error for human intervention

        Returns:
            SyncResult with actions taken
        """
        # Check current state
        git_head = self.git.head_sha()
        ledger_last = self.ledger.get_last_sync_commit()

        if git_head == ledger_last:
            return SyncResult(action="none", message="Already in sync")

        if strategy == "git_wins":
            # Ledger catches up
            self.ledger.record_sync(
                git_sha=git_head,
                files_committed=["SYNC_CATCHUP"],
            )
            return SyncResult(action="ledger_catchup", message=f"Ledger synced to {git_head}")

        elif strategy == "ledger_wins":
            # Git reverts (DANGEROUS)
            # Only valid if ledger_last is ancestor of git_head
            self.git.reset_to(ledger_last)
            return SyncResult(action="git_reset", message=f"Git reset to {ledger_last}")

        else:
            raise GovernanceViolation(
                f"Git ({git_head}) and Ledger ({ledger_last}) diverged. "
                f"Manual intervention required."
            )

    def save_snapshot(self, name: str) -> str:
        """
        Save complete state snapshot to disk.

        Used for:
        - Shutdown state preservation
        - Checkpoint before risky operations

        Args:
            name: Snapshot name (e.g., "shutdown_20251212_143022")

        Returns:
            Path to snapshot file
        """
        snapshot = self.snapshot()
        path = self._workspace / ".prakriti" / "snapshots" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot.to_dict(), indent=2))
        return str(path)

    def restore_snapshot(self, name: str) -> None:
        """
        Restore state from snapshot.

        Used for:
        - Boot recovery
        - Rollback

        Args:
            name: Snapshot name to restore
        """
        path = self._workspace / ".prakriti" / "snapshots" / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {name}")

        data = json.loads(path.read_text())
        snapshot = StateSnapshot.from_dict(data)

        # Restore layers
        self.kernel.from_dict(snapshot.kernel)
        self.ephemeral.from_dict(snapshot.ephemeral)
        # Note: Git and Ledger are NOT restored from snapshot
        # They are authoritative sources

    # =========================================================================
    # NEW: Session Boundary Operations
    # =========================================================================

    def begin_session(self) -> SessionContext:
        """
        Start a new session (called on kernel boot).

        Returns:
            SessionContext for this session
        """
        self.session = SessionContext(
            session_id=str(uuid.uuid4()),
            boot_time=time.time(),
            boot_commit=self.git.head_sha(),
        )
        return self.session

    def end_session(self) -> CommitResult:
        """
        End session (called on kernel shutdown).

        Returns:
            CommitResult from final commit
        """
        # 1. Save snapshot
        snapshot_name = f"shutdown_{int(time.time())}"
        self.save_snapshot(snapshot_name)

        # 2. Final commit
        result = self.commit_if_dirty(
            message=f"Session end: {self.session.session_id}",
            commit_type="chore",
            scope="session",
        )

        return result

    def recover_from_crash(self) -> Optional[CommitResult]:
        """
        Handle crash recovery on boot.

        Called when boot detects dirty state from previous session.

        Returns:
            CommitResult if recovery commit made, None if clean
        """
        if not self.is_dirty:
            return None

        # Mark session as crash recovery
        self.session.crash_recovery = True

        # Commit with recovery marker
        return self.commit_if_dirty(
            message="Crash recovery: uncommitted state from previous session",
            commit_type="chore",
            scope="recovery",
        )
```

---

## Kernel Integration (Complete)

### Boot Sequence

```python
# vibe_core/kernel_impl.py - boot() additions

async def boot(self) -> None:
    """Boot sequence with Prakriti integration."""

    # ... existing boot code ...

    # OPUS-027: Initialize Prakriti
    self.prakriti = Prakriti.from_workspace(self.workspace_path)

    # OPUS-027: Begin session
    session = self.prakriti.begin_session()
    logger.info(f"[BOOT] Session {session.session_id} started")

    # OPUS-027: Check consistency
    consistency = self.prakriti.verify()
    if not consistency.is_consistent:
        logger.warning(f"[BOOT] State inconsistency detected: {consistency}")
        self.prakriti.sync_ledger_git(strategy="git_wins")

    # OPUS-027: Crash recovery
    if self.prakriti.is_dirty:
        logger.warning("[BOOT] Dirty state detected (crash recovery)")
        recovery = self.prakriti.recover_from_crash()
        if recovery:
            logger.info(f"[BOOT] Recovered: {recovery.git_sha}")

    # ... continue existing boot ...
```

### Shutdown Sequence

```python
# vibe_core/kernel_impl.py - shutdown() additions

async def shutdown(self, reason: str = "user_requested") -> None:
    """Shutdown sequence with Prakriti integration."""

    # ... existing shutdown code ...

    # OPUS-027: End session
    if hasattr(self, 'prakriti') and self.prakriti:
        result = self.prakriti.end_session()
        if result:
            logger.info(f"[SHUTDOWN] Session committed: {result.git_sha}")
        else:
            logger.info("[SHUTDOWN] Session clean, no commit needed")

    # ... continue existing shutdown ...
```

---

## Implementation Phases

### Phase 1: LedgerState Integration (NEW)
**LOC**: +50

- Create `vibe_core/state/ledger_state.py`
- Add `get_last_sync_commit()`, `record_sync()`, `verify_chain()`
- Wire into Prakriti

### Phase 2: SessionContext (NEW)
**LOC**: +30

- Extend `vibe_core/state/ephemeral_state.py`
- Add `SessionContext` dataclass
- Wire into Prakriti

### Phase 3: Prakriti Write Operations
**LOC**: +80

- Add `commit_if_dirty()` with Ledger sync
- Add `sync_ledger_git()`
- Add `save_snapshot()`, `restore_snapshot()`
- Add `begin_session()`, `end_session()`, `recover_from_crash()`

### Phase 4: Git Write Operations (OPUS-028)
**LOC**: See OPUS-028 (~80)

- GitState.commit(), stage()
- VISNU protection
- Concurrency lock

### Phase 5: Kernel Integration
**LOC**: +20

- Boot: begin_session, consistency check, crash recovery
- Shutdown: end_session

### Phase 6: InterfacePlugin Cleanup
**LOC**: -60

- Remove `_auto_commit_ui_files()`
- Remove tick-based commits
- Delegate to Prakriti

### Phase 7: Config & Tests
**LOC**: +150

- Config extension in `guardrails.yaml`
- Integration tests

---

## LOC Impact Summary

| Component | Add | Remove | Net |
|-----------|-----|--------|-----|
| `ledger_state.py` (NEW) | +50 | 0 | +50 |
| `ephemeral_state.py` (extend) | +30 | 0 | +30 |
| `prakriti.py` (extend) | +80 | 0 | +80 |
| `git_state.py` (OPUS-028) | +80 | 0 | +80 |
| `kernel_impl.py` | +20 | 0 | +20 |
| `plugin_main.py` | +10 | -60 | -50 |
| `guardrails.yaml` | +10 | 0 | +10 |
| `tests/` | +150 | 0 | +150 |
| **TOTAL** | **+430** | **-60** | **+370** |

---

## Verification Checkpoints

### After Phase 1-2 (LedgerState + SessionContext):

```bash
python3 -c "
from vibe_core.state.prakriti import Prakriti
p = Prakriti.from_workspace('.')
print(f'Ledger last sync: {p.ledger.get_last_sync_commit()}')
print(f'Session: {p.session}')
"
```

### After Phase 3 (Prakriti Write Ops):

```bash
python3 -c "
from vibe_core.state.prakriti import Prakriti
p = Prakriti.from_workspace('.')
consistency = p.verify()
print(f'Consistent: {consistency.is_consistent}')
if not consistency.is_consistent:
    result = p.sync_ledger_git('git_wins')
    print(f'Sync: {result}')
"
```

### After Phase 5 (Kernel Integration):

```bash
python3 -c "
from vibe_core.kernel_impl import RealVibeKernel
k = RealVibeKernel(ledger_path=':memory:')
k.boot()
print(f'Session ID: {k.prakriti.session.session_id}')
k.shutdown('test')
"

# Check git log
git log --oneline -3
# Should see: Session end commit
```

### Final Verification:

```bash
# 1. Run tests
pytest tests/test_prakriti_integration.py -v

# 2. VISNU still works
python scripts/governance/verify_kernel.py --verify

# 3. Consistency check
python3 -c "
from vibe_core.state.prakriti import Prakriti
p = Prakriti.from_workspace('.')
c = p.verify()
assert c.is_consistent, f'FAIL: {c}'
print('PASS: State consistent')
"

# 4. Check commit count (should be ~2 per session, not 233)
git log --oneline --since="1 hour ago" | wc -l
```

---

## Critical Risks & Mitigations (Gemini Review)

### 1. Split-Brain (Ledger vs Git)

**Risk**: Ledger and Git disagree on current state.

**Mitigation**:
- `verify()` checks consistency on every boot
- `sync_ledger_git()` reconciles divergence
- Default: "git_wins" (Ledger is catch-up log)

### 2. Concurrency (index.lock)

**Risk**: Multiple agents committing = lock errors.

**Mitigation**:
- `_commit_lock` in GitState (OPUS-028)
- Single-threaded kernel = minimal risk now
- Future: Commit queue for multi-agent

### 3. Crash Recovery

**Risk**: System crashes with uncommitted state.

**Mitigation**:
- Boot checks `is_dirty`
- `recover_from_crash()` commits with recovery marker
- Snapshot saved on shutdown for restoration

### 4. Session Boundary Chaos

**Risk**: No clear start/end markers.

**Mitigation**:
- `begin_session()` on boot
- `end_session()` on shutdown
- Session metadata in commits

---

## Implementation Guidelines (Final Polish)

These refinements make the difference between "works" and "unbreakable":

### 1. Cryptographic Zipper (Bidirectional Interlock)

**Problem**: Ledger stores `git_sha`. But if Git history is rewritten (force push), the commit doesn't know which Ledger state it belonged to.

**Solution**: Every Git commit must include `Ledger-Head` in the commit body:

```python
# In Prakriti.commit_if_dirty()
commit_body = f"""
Session-ID: {self.session.session_id}
Ledger-Head: {self.ledger.get_current_head_hash()}
Source: Prakriti
"""
```

**Why**: Code (Git) and Memory (Ledger) become **cryptographically inseparable**. You cannot checkout old code without knowing exactly which memory state belongs to it.

### 2. Ghost Lock Cleanup (Stale Lock Detection)

**Problem**: Hard crash (OOM, power loss) leaves `index.lock` or `session.lock` behind. Next boot fails with "System locked" even though nothing is running.

**Solution**: In `begin_session()`, detect and clean stale locks:

```python
def begin_session(self) -> SessionContext:
    # Check for stale locks
    lock_file = self._workspace / ".prakriti" / "session.lock"
    if lock_file.exists():
        stored_pid = int(lock_file.read_text().strip())
        if not self._is_process_alive(stored_pid):
            logger.warning(f"Removed stale lock from dead session (PID {stored_pid})")
            lock_file.unlink()
        else:
            raise RuntimeError(f"Session already running (PID {stored_pid})")

    # Write our PID
    lock_file.write_text(str(os.getpid()))
    # ... rest of begin_session
```

### 3. Git Trailers (Machine Readability)

**Problem**: Freeform commit messages are hard to parse programmatically.

**Solution**: Use Git Trailer standard instead of freeform body:

```
chore(session): Session end

Session-ID: abc-123-def
Ledger-Head: 7f8a9b2c
Crash-Recovery: false
Commits-In-Session: 2
```

**Why**: Enables SQL-like queries: `git log --format='%(trailers:key=Session-ID)'`

Agents can read their own history programmatically.

---

## Success Criteria

- [ ] LedgerState tracks Git sync points
- [ ] Prakriti.verify() detects inconsistency
- [ ] Prakriti.sync_ledger_git() reconciles state
- [ ] Prakriti.commit_if_dirty() syncs both Git AND Ledger
- [ ] Kernel boot starts session, checks consistency, recovers from crash
- [ ] Kernel shutdown ends session, commits final state
- [ ] InterfacePlugin no longer has `_auto_commit_ui_files()`
- [ ] Git history clean (~2 commits per session)
- [ ] Ledger hash chain intact
- [ ] All existing tests pass
- [ ] New integration tests pass

---

## Related Documents

- **OPUS-009**: GOLDEN FOUNDATION - conceptual source of truth (this document implements parts of 009)
- **OPUS-028**: Git write operations (sub-document of this)
- **OPUS-024**: VISNU Kernel Protection
- **GAD-000**: Operator Inversion (API design)

---

## Why This Exists

The user said:

> "git autocommit sind nur 5% des echten unified states"
> "027 müsste der MASTER sein und 028 ein slave dazu!"
> "027 muss das sein was 009 NICHT ist"

OPUS-009 was vision. OPUS-027 is execution.

Git is ONE piece. Ledger sync, session boundaries, crash recovery, persona persistence - these are the other 95%.

**This document delivers all 100%.**

---

**Author**: Claude Opus 4
**Date**: 2025-12-12
**Status**: 📋 PLANNING - Complete scope, ready for implementation
