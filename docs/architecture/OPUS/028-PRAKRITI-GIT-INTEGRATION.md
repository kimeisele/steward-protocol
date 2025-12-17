# OPUS-028: Prakriti Git Integration

> **Status**: ✅ IMPLEMENTED (Phase 1-4 Complete, Phase 5-6 Pending)
> **Created**: 2025-12-12
> **Implemented**: 2025-12-12
> **Depends On**: OPUS-027 (Master Plan), OPUS-009 (Concept), OPUS-024 (VISNU Protection)
> **Purpose**: Complete GitState write operations and kernel integration
> **Problem**: 233 auto-commits in 2 days, InterfacePlugin bypasses Prakriti
> **Scope**: Git operations ONLY (5% of unified state - see OPUS-027 for full picture)
> **Remaining**: Phase 5 (Config Extension) and Phase 6 (Tests)

<!-- @HARNESS
files:
  # Core implementation (all verified to exist)
  - path: vibe_core/state/git_state.py
    required: true
  - path: vibe_core/state/prakriti.py
    required: true
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/plugins/interface/plugin_main.py
    required: true
  # Config
  - path: config/guardrails.yaml
    required: true
tests:
  - python scripts/ci/test_kernel_boot.py
  - python scripts/governance/verify_kernel.py --verify
wiring:
  # GitState write operations
  - pattern: "def commit\\("
    in: vibe_core/state/git_state.py
  - pattern: "def stage\\("
    in: vibe_core/state/git_state.py
  - pattern: "VISNU_PROTECTED"
    in: vibe_core/state/git_state.py
  - pattern: "_commit_lock"
    in: vibe_core/state/git_state.py
  # Prakriti orchestration
  - pattern: "def commit_if_dirty"
    in: vibe_core/state/prakriti.py
  # Kernel handles commits at session boundaries (not InterfacePlugin)
  - pattern: "prakriti.sync_ledger_git"
    in: vibe_core/kernel_impl.py
absent:
  # These should be REMOVED (verified 2025-12-12)
  - pattern: "_auto_commit_ui_files"
    in: vibe_core/plugins/interface/plugin_main.py
  - pattern: "_last_auto_commit"
    in: vibe_core/plugins/interface/plugin_main.py
  - pattern: "_auto_commit_interval"
    in: vibe_core/plugins/interface/plugin_main.py
config:
  - section: guardrails.ui_files
-->

---

## Executive Summary

OPUS-009 describes "Git as Consciousness" but only READ operations exist.
InterfacePlugin makes its own subprocess calls every 60 seconds, bypassing Prakriti entirely.
Result: 233 "dumb" commits in 2 days, polluted git history.

**This document implements the WRITE operations and wires them correctly.**

---

## Problem Statement

### Current Architecture (Broken)

```
┌─────────────────────────────────────────────────────────────┐
│  InterfacePlugin                                            │
│       │                                                     │
│       └──→ _auto_commit_ui_files() [every 60s]             │
│                 │                                           │
│                 └──→ subprocess.run(["git", "commit"...])  │
│                            │                                │
│                            └──→ --no-verify (bypasses ALL) │
│                                                             │
│  Prakriti (exists but disconnected)                        │
│       │                                                     │
│       └──→ GitState (READ-ONLY, no commit())               │
│                                                             │
│  Kernel shutdown()                                          │
│       │                                                     │
│       └──→ NO prakriti.commit() call                       │
└─────────────────────────────────────────────────────────────┘
```

### Evidence

```bash
# 233 auto-commits in 2 days
git log --oneline --since="2025-12-10" | grep "auto:" | wc -l
# Output: 233

# prakriti.git is NEVER used for commits
grep -r "prakriti\.git\.commit" vibe_core/*.py
# Output: (nothing)

# InterfacePlugin uses raw subprocess
grep -n "subprocess.run.*git.*commit" vibe_core/plugins/interface/plugin_main.py
# Output: Line 556
```

### Target Architecture (Correct)

```
┌─────────────────────────────────────────────────────────────┐
│  InterfacePlugin                                            │
│       │                                                     │
│       └──→ render() ──→ files written                      │
│                                                             │
│  Kernel                                                     │
│       │                                                     │
│       ├──→ boot()                                          │
│       │       └──→ prakriti.commit_if_dirty() [crash recovery]
│       │                                                     │
│       └──→ shutdown()                                      │
│               └──→ prakriti.commit_if_dirty() [final state]│
│                         │                                   │
│                         └──→ GitState.commit()             │
│                                   │                         │
│                                   ├──→ VISNU check         │
│                                   ├──→ Concurrency lock    │
│                                   └──→ git commit          │
└─────────────────────────────────────────────────────────────┘

Result: 2 commits per session (boot + shutdown) instead of 233
```

---

## Gap Analysis

### GitState (`vibe_core/state/git_state.py`)

| Method | OPUS-009 Spec | Implemented | Status |
|--------|---------------|-------------|--------|
| `current_branch()` | ✅ | ✅ Line 84 | OK |
| `head_sha()` | ✅ | ✅ Line 92 | OK |
| `is_dirty()` | ✅ | ✅ Line 105 | OK |
| `diff()` | ✅ | ✅ Line 133 | OK |
| `recent_commits()` | ✅ | ✅ Line 185 | OK |
| `commit()` | ✅ | ❌ | **MISSING** |
| `stage()` | ✅ | ❌ | **MISSING** |
| VISNU protection | ✅ | ❌ | **MISSING** |
| Concurrency lock | ✅ | ❌ | **MISSING** |

Note: Line 72 says `"read_only": True` - this must change to `False`.

### Prakriti (`vibe_core/state/prakriti.py`)

| Method | OPUS-009 Spec | Implemented | Status |
|--------|---------------|-------------|--------|
| `snapshot()` | ✅ | ✅ Line 158 | OK |
| `verify()` | ✅ | ✅ Line 182 | OK |
| `diff()` | ✅ | ✅ Line 219 | OK |
| `inject_kernel()` | ✅ | ✅ Line 173 | OK |
| `commit_if_dirty()` | ✅ | ❌ | **MISSING** |
| `restore()` | ✅ | ❌ | Phase 3+ |
| `sync()` | ✅ | ❌ | Phase 3+ |

### Kernel Integration (`vibe_core/kernel_impl.py`)

| Integration Point | OPUS-009 Spec | Implemented | Status |
|-------------------|---------------|-------------|--------|
| Boot: crash recovery | ✅ | ❌ | **MISSING** |
| Shutdown: final commit | ✅ | ❌ | **MISSING** |
| Prakriti injection | ✅ | ✅ Line 946 | OK |

### InterfacePlugin (`vibe_core/plugins/interface/plugin_main.py`)

| Issue | Current | Target |
|-------|---------|--------|
| `_auto_commit_ui_files()` | Line 521-582 | **REMOVE** |
| `_last_auto_commit` | Line 56 | **REMOVE** |
| `_auto_commit_interval` | Line 57 | **REMOVE** |
| Tick-based commit | Lines 203-205 | **REMOVE** |
| `on_shutdown()` | Empty (Line 316) | Delegate to Prakriti |
| `--no-verify` bypass | Line 556 | Keep for UI files |

---

## Design Decisions

### 1. Semantic Commit Format

**Decision: LATER (Phase 2)**

Rationale:
- The problem is FREQUENCY (233 commits), not FORMAT
- `chore(ui): Update` vs `auto: Update` doesn't reduce commit count
- First: reduce to 2 commits per session
- Then: add semantic format when it works

### 2. Concurrency Protection

**Decision: NOW but MINIMAL**

```python
# NOT this (overengineering):
_commit_queue: asyncio.Queue
_lock: asyncio.Lock
async def request_commit(...)
async def _process_queue(...)

# THIS (minimal, sufficient):
_commit_lock = threading.Lock()

def commit(self, ...):
    with self._commit_lock:
        # git operations
```

Rationale:
- Single-threaded kernel = no real concurrency problem now
- Simple lock prevents index.lock errors
- Fancy queue only needed for multi-agent parallel commits (Phase 3+)

### 3. VISNU Protection in Commit Path

**Decision: CHECK IN GitState.commit() ITSELF**

```python
VISNU_PROTECTED = [
    "vibe_core/kernel_impl.py",
    "vibe_core/kernel_ops.py",
    # ... all 21 files from restore_kernel.sh
]

def commit(self, ...):
    staged = self._get_staged_files()
    protected = [f for f in staged if f in VISNU_PROTECTED]
    if protected:
        raise GovernanceViolation(f"VISNU protected: {protected}")
```

Rationale:
- Defense in Depth - every layer checks itself
- Caller can forget to check
- GitState is the last defense line before git

### 4. Config Extension

**Decision: ADD `auto_commit_mode` CONFIG**

```yaml
# config/guardrails.yaml
ui_files:
  auto_commit: true
  auto_commit_mode: "boundary"  # NEW: boundary | continuous | disabled
  commit_message: "auto: Update generated UI files"
```

| Mode | Behavior |
|------|----------|
| `boundary` | Commit on boot + shutdown only (DEFAULT) |
| `continuous` | Commit every N seconds (old behavior, not recommended) |
| `disabled` | Never auto-commit |

---

## Implementation Plan

### Phase 1: GitState Write Operations

**File:** `vibe_core/state/git_state.py`
**LOC:** +80

```python
import threading
from typing import List, Optional

# After line 20 (imports)
VISNU_PROTECTED = [
    "vibe_core/kernel_impl.py",
    "vibe_core/kernel_ops.py",
    "vibe_core/plugin_protocol.py",
    "vibe_core/plugin_loader.py",
    "vibe_core/narasimha.py",
    "vibe_core/capability_registry.py",
    "vibe_core/bridge.py",
    "scripts/governance/restore_kernel.sh",
    "scripts/governance/verify_kernel.py",
    "scripts/governance/kernel_hashes.json",
    ".github/workflows/attest.yml",
    ".github/workflows/container-build.yml",
    ".github/workflows/deploy.yml",
    ".github/workflows/factory.yml",
    ".github/workflows/heartbeat.yml",
    ".github/workflows/integration-tests.yml",
    ".github/workflows/scheduled-agents.yml",
    ".github/workflows/scribe-docs.yml",
    ".github/workflows/steward-ci.yml",
    ".github/workflows/system-cycle.yml",
    ".pre-commit-config.yaml",
]

# In GitState class, after __init__
_commit_lock = threading.Lock()

# After line 220 (after _get_main_branch)
# =========================================================================
# Write Operations (OPUS-028)
# =========================================================================

def stage(self, patterns: List[str]) -> int:
    """Stage files matching patterns.

    Args:
        patterns: File patterns to stage (e.g., ["*.md"])

    Returns:
        Number of files staged
    """
    if not self.is_git_repo():
        return 0

    total = 0
    for pattern in patterns:
        result = self._run_git(["add", pattern])
        if result is not None:
            total += 1
    return total

def commit(
    self,
    message: str,
    commit_type: str = "chore",
    scope: str = "auto",
    no_verify: bool = True,
) -> Optional[GitCommit]:
    """Create a commit.

    VISNU Guard: Refuses to commit protected files.
    Thread-safe via _commit_lock.

    Args:
        message: Commit message
        commit_type: Conventional commit type (chore, feat, fix, etc.)
        scope: Commit scope
        no_verify: Skip pre-commit hooks (True for UI auto-commits)

    Returns:
        GitCommit if successful, None if nothing to commit

    Raises:
        GovernanceViolation: If VISNU protected files are staged
    """
    if not self.is_git_repo():
        return None

    with self._commit_lock:
        # 1. Check if anything to commit
        if not self.is_dirty():
            return None

        # 2. VISNU protection check
        staged = self._get_staged_files()
        protected = [f for f in staged if f in VISNU_PROTECTED]
        if protected:
            from vibe_core.exceptions import GovernanceViolation
            raise GovernanceViolation(
                f"Cannot commit VISNU protected files via Prakriti: {protected}. "
                f"See docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md"
            )

        # 3. Format message
        formatted_msg = f"{commit_type}({scope}): {message}"

        # 4. Create commit
        cmd = ["commit", "-m", formatted_msg]
        if no_verify:
            cmd.insert(1, "--no-verify")

        result = self._run_git(cmd)
        if result is None:
            return None

        # 5. Return commit info
        return GitCommit(
            sha=self.head_sha(),
            short_sha=self.short_sha(),
            author="system",
            message=formatted_msg,
            timestamp=str(time.time()),
        )

def _get_staged_files(self) -> List[str]:
    """Get list of staged files."""
    result = self._run_git(["diff", "--cached", "--name-only"])
    if not result:
        return []
    return [f.strip() for f in result.strip().split("\n") if f.strip()]
```

**Also update `get_capabilities()`:**

```python
def get_capabilities(self) -> Dict[str, Any]:
    return {
        "operations": [
            "current_branch",
            "head_sha",
            "is_dirty",
            "diff",
            "recent_commits",
            "stage",      # NEW
            "commit",     # NEW
        ],
        "read_only": False,  # CHANGED from True
        "visnu_protected_count": len(VISNU_PROTECTED),
        "workspace": str(self._workspace),
    }
```

### Phase 2: Prakriti Commit Orchestration

**File:** `vibe_core/state/prakriti.py`
**LOC:** +25

```python
# After line 260 (after is_dirty property)

# =========================================================================
# Write Operations (OPUS-028)
# =========================================================================

def commit_if_dirty(
    self,
    message: str = "Auto-commit",
    commit_type: str = "chore",
    scope: str = "state",
    stage_patterns: Optional[List[str]] = None,
) -> Optional[GitCommit]:
    """Commit current changes if workspace is dirty.

    Idempotent - safe to call multiple times.

    Args:
        message: Commit message
        commit_type: Conventional commit type
        scope: Commit scope
        stage_patterns: Patterns to stage (default: ["*.md"])

    Returns:
        GitCommit if committed, None if nothing to commit
    """
    if not self.is_dirty:
        logger.debug("[PRAKRITI] Nothing to commit (clean state)")
        return None

    # Stage files
    patterns = stage_patterns or ["*.md"]
    self.git.stage(patterns)

    # Commit
    commit = self.git.commit(message, commit_type, scope)
    if commit:
        logger.info(f"[PRAKRITI] Committed: {commit.short_sha} - {message}")

    return commit
```

### Phase 3: Kernel Integration

**File:** `vibe_core/kernel_impl.py`
**LOC:** +15

```python
# In boot(), after line 946 (after prakriti.inject_kernel):

# OPUS-027: Crash Recovery - commit any dirty state from previous session
if self.prakriti.is_dirty:
    logger.warning("⚠️ Dirty state from previous session detected (crash recovery)")
    commit = self.prakriti.commit_if_dirty(
        message="Crash recovery: uncommitted state from previous session",
        commit_type="chore",
        scope="recovery"
    )
    if commit:
        logger.info(f"[BOOT] Recovered state: {commit.short_sha}")


# In shutdown(), after line 1173 (after plugin.on_shutdown loop):

# OPUS-027: Final state commit
if hasattr(self, 'prakriti') and self.prakriti:
    commit = self.prakriti.commit_if_dirty(
        message="Kernel shutdown state",
        commit_type="chore",
        scope="kernel"
    )
    if commit:
        logger.info(f"[SHUTDOWN] State committed: {commit.short_sha}")
```

### Phase 4: InterfacePlugin Cleanup

**File:** `vibe_core/plugins/interface/plugin_main.py`
**LOC:** -60, +10

**REMOVE these lines:**
- Line 56: `self._last_auto_commit: float = 0`
- Line 57: `self._auto_commit_interval: int = 60`
- Lines 203-205: Tick-based auto-commit trigger
- Lines 521-582: `_auto_commit_ui_files()` method

**MODIFY `on_shutdown()` (Line 316):**

```python
def on_shutdown(self, kernel: "RealVibeKernel") -> None:
    """Clean up and commit UI state via Prakriti."""
    logger.info("InterfacePlugin shutting down")

    # Delegate to Prakriti (not direct subprocess)
    if hasattr(kernel, 'prakriti') and kernel.prakriti:
        commit = kernel.prakriti.commit_if_dirty(
            message="UI files on shutdown",
            commit_type="chore",
            scope="ui"
        )
        if commit:
            logger.info(f"[INTERFACE] UI state committed: {commit.short_sha}")
```

### Phase 5: Config Extension

**File:** `config/guardrails.yaml`
**LOC:** +3

```yaml
ui_files:
  auto_commit: true
  auto_commit_mode: "boundary"  # NEW: boundary | continuous | disabled
  commit_message: "auto: Update generated UI files"
  commit_on_boot: true   # NEW: commit dirty state on boot (crash recovery)
  commit_on_shutdown: true  # NEW: commit state on shutdown
```

### Phase 6: Tests

**File:** `tests/test_state_write_ops.py` (NEW)
**LOC:** +120

```python
"""
Tests for OPUS-028: Prakriti Git Integration

Verifies:
1. GitState.commit() creates real commits
2. GitState.commit() rejects VISNU protected files
3. Prakriti.commit_if_dirty() is idempotent
4. Kernel boot/shutdown commits work
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from vibe_core.state.git_state import GitState, VISNU_PROTECTED
from vibe_core.state.prakriti import Prakriti
from vibe_core.exceptions import GovernanceViolation


class TestGitStateCommit:
    """Tests for GitState.commit()"""

    def test_commit_creates_commit(self, tmp_path):
        """GitState.commit() creates a real git commit."""
        # Setup: init git repo, create file, stage it
        ...

    def test_commit_visnu_protected_raises(self, tmp_path):
        """GitState.commit() refuses to commit VISNU protected files."""
        git_state = GitState(tmp_path)

        with patch.object(git_state, '_get_staged_files') as mock:
            mock.return_value = ["vibe_core/kernel_impl.py"]

            with pytest.raises(GovernanceViolation) as exc:
                git_state.commit("test")

            assert "VISNU protected" in str(exc.value)

    def test_commit_empty_returns_none(self, tmp_path):
        """GitState.commit() returns None if nothing to commit."""
        ...

    def test_commit_thread_safe(self, tmp_path):
        """GitState.commit() is thread-safe."""
        ...


class TestPrakritiCommitIfDirty:
    """Tests for Prakriti.commit_if_dirty()"""

    def test_commit_if_dirty_when_dirty(self, tmp_path):
        """commit_if_dirty() commits when dirty."""
        ...

    def test_commit_if_dirty_when_clean(self, tmp_path):
        """commit_if_dirty() returns None when clean."""
        ...

    def test_commit_if_dirty_idempotent(self, tmp_path):
        """Multiple calls don't create duplicate commits."""
        ...


class TestKernelIntegration:
    """Tests for kernel boot/shutdown integration."""

    def test_kernel_shutdown_commits_state(self):
        """Kernel shutdown commits dirty state via Prakriti."""
        ...

    def test_kernel_boot_crash_recovery(self):
        """Kernel boot commits dirty state (crash recovery)."""
        ...
```

---

## LOC Impact

| File | Add | Remove | Net |
|------|-----|--------|-----|
| `vibe_core/state/git_state.py` | +80 | 0 | +80 |
| `vibe_core/state/prakriti.py` | +25 | 0 | +25 |
| `vibe_core/kernel_impl.py` | +15 | 0 | +15 |
| `vibe_core/plugins/interface/plugin_main.py` | +10 | -60 | -50 |
| `config/guardrails.yaml` | +3 | 0 | +3 |
| `tests/test_state_write_ops.py` | +120 | 0 | +120 |
| **TOTAL** | **+253** | **-60** | **+193** |

---

## Verification Checkpoints

### After Phase 1-2 (GitState + Prakriti):

```bash
python3 -c "
from vibe_core.state.prakriti import Prakriti
p = Prakriti.from_workspace('.')
print(f'Capabilities: {p.git.get_capabilities()}')
print(f'read_only should be False: {p.git.get_capabilities()[\"read_only\"]}')
"
```

### After Phase 3 (Kernel Integration):

```bash
python3 -c "
from vibe_core.kernel_impl import RealVibeKernel
k = RealVibeKernel(ledger_path=':memory:')
k.boot()
# Should see: crash recovery message if dirty, or clean boot
k.shutdown('test')
# Should see: state committed message
"

# Check git log
git log --oneline -5
# Should see: 1-2 new commits (recovery + shutdown)
```

### After Phase 4 (InterfacePlugin):

```bash
# Verify _auto_commit_ui_files is GONE
grep -n "_auto_commit_ui_files" vibe_core/plugins/interface/plugin_main.py
# Should output: nothing

# Verify on_shutdown delegates to Prakriti
grep -A5 "def on_shutdown" vibe_core/plugins/interface/plugin_main.py
# Should show: kernel.prakriti.commit_if_dirty
```

### Final Verification:

```bash
# 1. Run tests
pytest tests/test_state_write_ops.py -v

# 2. VISNU still works
python scripts/governance/verify_kernel.py --verify

# 3. Full kernel cycle
python -m vibe_core.cli boot
sleep 5
python -m vibe_core.cli stop

# 4. Check commit count
git log --oneline --since="1 hour ago" | grep -E "chore\(|auto:" | wc -l
# Should be: 2 (boot recovery + shutdown), not 60+
```

---

## Success Criteria

- [x] `prakriti.git.commit()` works
- [x] VISNU protected files are rejected
- [x] Kernel boot commits dirty state (crash recovery)
- [x] Kernel shutdown commits final state
- [x] InterfacePlugin no longer has `_auto_commit_ui_files()`
- [ ] Git history is clean (~2 commits per session)
- [x] All existing tests pass
- [ ] New tests pass (Phase 6)

---

## Rollback Plan

If issues arise:

1. Revert InterfacePlugin changes (restore `_auto_commit_ui_files`)
2. Remove kernel integration (boot/shutdown commits)
3. Keep GitState write ops (they don't break anything if unused)

---

## Related Documents

- **OPUS-027**: Unified State Implementation (master plan - this is a sub-document)
- **OPUS-009**: GOLDEN FOUNDATION - conceptual source of truth for all Prakriti
- **OPUS-024**: Kernel Protection Audit (VISNU)
- **GAD-000**: Operator Inversion (API design principles)

---

**Author**: Claude Opus 4
**Date**: 2025-12-12
**Status**: ✅ IMPLEMENTED (Phase 1-4) - Git operations only (see OPUS-027 for full scope)
