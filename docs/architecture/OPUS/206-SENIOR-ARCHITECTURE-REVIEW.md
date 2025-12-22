# OPUS-206: Senior Architecture Review (Post-ADR-204)

**Status**: CRITICAL REVIEW
**Date**: 2025-12-22
**Author**: Senior Architect (Opus 4.5)
**Context**: Review of ADR-204 implementation and identification of architectural debt

---

## Executive Summary

The previous Senior Agent implemented significant architectural improvements (ADR-204, OPUS-203), but left behind **critical structural issues** that must be addressed before further development. This document is a brutal, honest assessment.

**Good work done:**
- Hierarchical state namespacing (`.vibe/state/`)
- Async kernel migration (OPUS-203)
- IntegrityGuard boot-time validation

**Critical issues discovered:**
1. **Circular Dependency Hell** in StateService
2. **Multi-Path Git Commits** (3+ different code paths)
3. **Dead Oracle Code** (never executed)
4. **Environment Variable Backdoors** (inconsistent)
5. **Singleton Chaos** (new instances created instead of using singletons)

---

## Critical Issue #1: Circular Dependency in StateService

### Location
`vibe_core/state/state_service.py:651-663`

### The Problem

```python
def _commit_via_weaver(self) -> bool:
    """Try to commit via StateSyncWeaver."""
    try:
        from .prakriti import Prakriti          # CREATES NEW INSTANCE!
        from .weaver import get_state_sync_weaver

        prakriti = Prakriti(self.workspace)     # NOT THE SINGLETON!
        weaver = get_state_sync_weaver(prakriti)
        result = weaver.pulse()

        return result.success if hasattr(result, "success") else bool(result)
    except Exception:
        return False
```

This creates a **NEW Prakriti instance** every time, which:
1. Wastes memory
2. Breaks session tracking (new session each call)
3. Creates circular imports at runtime
4. Ignores any existing Prakriti state

### The Fix Required

Use proper singleton access or inject dependency:

```python
def _commit_via_weaver(self) -> bool:
    """Try to commit via StateSyncWeaver."""
    try:
        from .weaver import get_state_sync_weaver
        weaver = get_state_sync_weaver()  # Use existing singleton!
        if weaver is None:
            return False  # Weaver not initialized
        result = weaver.pulse()
        return result.success if hasattr(result, "success") else bool(result)
    except Exception:
        return False
```

---

## Critical Issue #2: Multi-Path Git Commits

### The Problem

There are **3+ independent code paths** for Git commits:

| Path | Location | Hook Bypass | Notes |
|------|----------|-------------|-------|
| `StateService._commit_via_git()` | state_service.py:665-705 | `--no-verify` | Bypasses ALL hooks! |
| `StateService._commit_via_weaver()` | state_service.py:651-663 | Normal | Creates new Prakriti |
| `Prakriti.commit_if_dirty()` | prakriti.py:346-419 | Normal | The "official" way |
| `Weaver.pulse()` | weaver.py:162-188 | Check env | Calls Prakriti |
| `Weaver.weave()` | weaver.py:209-223 | Check env | Also calls Prakriti |
| `Weaver.on_session_end()` | weaver.py:190-207 | Force | Yet another path |

### Why This Is Dangerous

1. **Hook Bypass**: `StateService._commit_via_git()` uses `--no-verify`, which:
   - Bypasses pre-commit hooks
   - Bypasses GPG signing hooks
   - Bypasses VISNU kernel protection

2. **Inconsistent Behavior**: Some paths check `VIBE_NO_GIT_COMMIT`, others don't

3. **Race Conditions**: Each path has its own locking (or none)

### The Fix Required

**Single Commit Authority**: ALL commits must go through ONE method:

```python
# In prakriti.py or a dedicated CommitManager
class CommitAuthority:
    """THE ONLY way to commit. Period."""

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def commit(cls, files: List[Path], message: str, no_verify: bool = False) -> bool:
        """Single commit entry point."""
        with cls._lock:
            if os.environ.get("VIBE_NO_GIT_COMMIT") == "1":
                return False
            # ... single implementation
```

---

## Critical Issue #3: Dead Oracle Code

### Location
`vibe_core/state/weaver.py:229-260`

### The Problem

```python
def _consult_oracle(self, classified: ClassifiedState) -> WeavingAdvice:
    """Phase 3: CONSULT - Non-blocking intelligence ingestion."""
    advice = WeavingAdvice(mode=WeaverMode.REFLEX)

    if not self.manas_oracle:  # ALWAYS NONE!
        return advice

    try:
        # This code NEVER executes because manas_oracle is never set
        oracle_context = {...}
        result = self.manas_oracle.consult(oracle_context)
        # ...
```

`self.manas_oracle` is **never set**. Looking at all usages:

```python
# weaver.py:141-151
def __init__(
    self,
    prakriti: "Prakriti",
    sync_holon: Optional["StateSyncHolon"] = None,
    manas_oracle: Optional[Any] = None,  # NEVER PASSED!
):
    self.manas_oracle = manas_oracle  # Always None
```

And `get_state_sync_weaver()`:

```python
# weaver.py:437-444
def get_state_sync_weaver(prakriti: Optional["Prakriti"] = None) -> Optional[StateSyncWeaver]:
    global _global_weaver
    if _global_weaver is None and prakriti is not None:
        _global_weaver = StateSyncWeaver(prakriti)  # NO manas_oracle!
    return _global_weaver
```

### The Fix Required

Either:
1. **Remove dead code** (preferable - YAGNI)
2. **Actually wire MANAS Oracle** if needed

---

## Critical Issue #4: Environment Variable Backdoors

### The Problem

Multiple environment variables disable security:

| Variable | Location | What It Bypasses |
|----------|----------|------------------|
| `VIBE_NO_LOCK` | prakriti.py:490-497 | Session locking |
| `VIBE_NO_GIT_COMMIT` | weaver.py:167-169, state_service.py:607-609 | All Git commits |
| `test_mode` parameter | kernel_impl.py, integrity_guard | IntegrityGuard checks |

### Why This Is Dangerous

1. **Inconsistent Checking**: Some places check, others don't
2. **Production Risk**: If accidentally set in production, security is disabled
3. **No Audit Trail**: No logging when bypasses are used

### The Fix Required

Consolidate into a single, well-documented bypass mechanism:

```python
# vibe_core/test_mode.py
class TestMode:
    """Centralized test mode control."""

    _enabled: bool = False

    @classmethod
    def is_enabled(cls) -> bool:
        if cls._enabled:
            return True
        return os.environ.get("VIBE_TEST_MODE") == "1"

    @classmethod
    def log_bypass(cls, component: str, operation: str) -> None:
        if cls.is_enabled():
            logger.warning(f"[TEST_MODE] {component} bypassed {operation}")
```

---

## Critical Issue #5: Singleton Chaos

### The Problem

Multiple singleton patterns, each implemented differently:

| Component | Pattern | Location |
|-----------|---------|----------|
| StateService | Dict registry `_instances` | state_service.py:713 |
| Weaver | Global variable `_global_weaver` | weaver.py:434 |
| SynapseStore | Class dict `_instances` | synapse_store.py:350 |
| CycleRegistry | Global variable `_global_cycle_registry` | orchestration_cycle.py:56 |
| EventBus | Multiple patterns | event_bus.py |

### Why This Is Dangerous

1. **Memory Leaks**: Each pattern handles cleanup differently
2. **Testing Nightmares**: Hard to reset between tests
3. **Race Conditions**: Each has different locking

### The Fix Required

Use a consistent DI container or registry:

```python
# vibe_core/di.py
class ServiceRegistry:
    """Centralized dependency injection."""

    _services: Dict[str, Any] = {}
    _lock = threading.Lock()

    @classmethod
    def get(cls, service_type: Type[T]) -> T:
        with cls._lock:
            return cls._services.get(service_type.__name__)

    @classmethod
    def reset(cls) -> None:
        """For testing only."""
        with cls._lock:
            cls._services.clear()
```

---

## Issue #6: Prakriti God Object

### The Problem

`Prakriti` has too many responsibilities:

```python
class Prakriti:
    # Layer 1: Physical
    self.git = GitState(...)         # Git operations
    self.files = FileState(...)      # File operations
    self.ledger = LedgerState(...)   # Ledger operations
    self.machine = MachineState(...) # Machine state

    # Layer 2: Runtime
    self.kernel = KernelState()      # Kernel state
    self.ephemeral = EphemeralState() # Ephemeral state

    # Layer 3: Identity
    self.personas = PersonaManager(...) # Personas

    # Session
    self.session: KernelSessionContext  # Session tracking

    # Methods
    def commit_if_dirty(...)   # Git commits
    def sync_ledger_git(...)   # Ledger sync
    def begin_session(...)     # Session management
    def end_session(...)       # Session management
    def recover_from_crash(...)# Crash recovery
    def save_snapshot(...)     # Snapshots
    def restore_snapshot(...)  # Snapshots
```

This is a **God Object** anti-pattern.

### The Fix Required

Split into focused managers:

```
Prakriti (Facade)
  ├── GitManager (git operations)
  ├── FileManager (file operations)
  ├── LedgerManager (ledger operations)
  ├── SessionManager (session lifecycle)
  └── SnapshotManager (snapshots)
```

---

## Immediate Action Items

### Priority 1 (Fix Now - Breaking Issues)

1. **Fix StateService circular dependency** (Issue #1)
   - Remove `Prakriti()` instantiation in `_commit_via_weaver()`
   - Use existing singleton or remove method

2. **Remove or fix dead Oracle code** (Issue #3)
   - Either wire MANAS or remove `_consult_oracle()`

### Priority 2 (Fix Soon - Technical Debt)

3. **Consolidate commit paths** (Issue #2)
   - Create single `CommitAuthority`
   - Remove `--no-verify` bypass in `_commit_via_git()`

4. **Consolidate test mode** (Issue #4)
   - Single `TestMode` class
   - Audit all bypass locations

### Priority 3 (Refactor - Long Term)

5. **Unify singleton patterns** (Issue #5)
   - Evaluate DI container
   - Consistent reset mechanism

6. **Split Prakriti** (Issue #6)
   - Extract managers
   - Keep Prakriti as facade

---

## Validation

After fixes, run:

```bash
# Fast integrity check
pytest -m fast --maxfail=3

# Full test suite
pytest tests/ -v --tb=short

# Lint
ruff check vibe_core/ --select F,E9
```

---

## Handover Notes

To the next Senior Agent:

> **The Vibe Core is architecturally sound in CONCEPT but has implementation debt.** The ADR-204 namespacing is correct. The OPUS-203 async migration is correct. But the EXECUTION has circular dependencies, dead code, and too many commit paths.
>
> Fix Issues #1-4 before ANY new feature work. The foundation must be solid before we build higher.
>
> **DO NOT add more abstraction layers.** The system already has too many. Simplify, don't complexify.

---

## Approval

- [x] Identified: Circular dependency in StateService
- [x] Identified: Multi-path git commits
- [x] Identified: Dead Oracle code
- [x] Identified: Environment variable chaos
- [x] Identified: Singleton inconsistencies
- [x] Identified: Prakriti god object
- [ ] Fixed: Priority 1 items
- [ ] Fixed: Priority 2 items
- [ ] Refactored: Priority 3 items

**Status: REVIEW COMPLETE. FIXES PENDING.**
