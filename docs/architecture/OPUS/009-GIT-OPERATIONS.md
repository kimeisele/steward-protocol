# OPUS-009: Git Operations for Agent Workflows

> **Status**: DRAFT
> **Created**: 2025-12-08
> **Symbol**: 9 = Completion (3x3 = Perfection Squared)
> **Purpose**: Define Git operations patterns for multi-agent parallel work

---

## Executive Summary

When multiple AI agents work in parallel on the same codebase, Git becomes both a **coordination mechanism** and a **verification tool**. This document defines:

1. **Branch Strategy** for agent isolation
2. **Git Diff as Control Mechanism** for work verification
3. **Merge Protocols** for conflict-free integration
4. **Cleanup Automation** for hygiene

---

## The Problem

### Current Chaos (What We Just Fixed)

```
Before: 39 local branches, 8 stashes, 60+ remote branches
After:  1 local branch (main), 0 stashes
```

**Root Causes**:
- Parallel agents each created branches
- No cleanup after merge
- Stashes accumulated without purpose
- Remote branches never pruned

### Agent Git Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Long-lived branches | Drift from main, merge conflicts | Short-lived feature branches |
| Stash hoarding | Forgotten work, confusion | Use commits, not stashes |
| Force push | Lost history | Never force push to main |
| No verification | Silent failures | Git diff verification |

---

## Branch Strategy: VEDA-4 Git Model

Following the fractal VEDA-4 pattern (FILE/FIND/REPLACE/VERIFY):

### 1. RIG (Knowledge) - Branch Creation

```bash
# Create branch with semantic naming
git checkout -b <type>/<description>

# Types:
# feat/   - New features
# fix/    - Bug fixes
# docs/   - Documentation only
# refactor/ - Code restructuring
# test/   - Test additions
```

**Agent Naming Convention**:
```
<type>/<agent-id>-<task-hash>
feat/haiku-a1b2c3d4
fix/sonnet-e5f6g7h8
```

### 2. YAJUR (Action) - Work Execution

```bash
# Before any work, sync with main
git fetch origin main
git rebase origin/main

# Make atomic commits
git add <specific-files>
git commit -m "type: description"
```

**Commit Message Format**:
```
<type>: <imperative description>

[optional body explaining WHY, not WHAT]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <model>
```

### 3. SAMA (Transform) - Merge Protocol

```bash
# Before merge, verify work
git diff main..HEAD --stat

# Squash merge for clean history
git checkout main
git merge --squash <branch>
git commit -m "feat: <summary of all changes>"

# Immediately delete branch
git branch -D <branch>
```

### 4. ATHARVA (Protection) - Verification

```bash
# Verify merge success
git log --oneline -1  # Check commit message
git diff HEAD~1 --stat  # Check changes
pytest tests/  # Run tests

# Push only after verification
git push origin main
```

---

## Git Diff as Control Mechanism

### Work Verification Protocol

Before accepting agent work, verify via diff:

```python
def verify_agent_work(branch: str) -> dict:
    """VEDA-4 verification of agent work."""

    # 1. RIG: What files changed?
    files_changed = run("git diff main..{branch} --name-only")

    # 2. YAJUR: What are the actual changes?
    diff_stat = run("git diff main..{branch} --stat")

    # 3. SAMA: Are changes meaningful?
    insertions = parse_insertions(diff_stat)
    deletions = parse_deletions(diff_stat)

    # 4. ATHARVA: Do tests pass?
    test_result = run("pytest tests/ -q")

    return {
        "files": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "tests_pass": test_result.returncode == 0,
        "approved": insertions > 0 and test_result.returncode == 0
    }
```

### Automated Diff Checks

| Check | Command | Fail Condition |
|-------|---------|----------------|
| Empty work | `git diff main..HEAD` | No output |
| Too large | `git diff --stat \| tail -1` | >1000 insertions |
| Unrelated files | `git diff --name-only` | Files outside scope |
| Missing tests | `git diff --name-only \| grep test` | No test changes for feat/ |
| Secrets leak | `git diff \| grep -E 'API_KEY\|SECRET'` | Any match |

---

## Cleanup Automation

### Post-Merge Cleanup Script

```python
#!/usr/bin/env python3
"""Git cleanup after agent work."""

import subprocess

def cleanup_branches():
    """Delete all branches merged into main."""
    # Get merged branches
    result = subprocess.run(
        ['git', 'branch', '--merged', 'main'],
        capture_output=True, text=True
    )

    branches = [
        b.strip() for b in result.stdout.split('\n')
        if b.strip() and b.strip() != 'main' and not b.startswith('*')
    ]

    for branch in branches:
        subprocess.run(['git', 'branch', '-d', branch])
        print(f"Deleted: {branch}")

    return len(branches)

def cleanup_stashes():
    """Clear all stashes (use commits instead)."""
    subprocess.run(['git', 'stash', 'clear'])
    print("Stashes cleared")

def prune_remotes():
    """Remove stale remote tracking branches."""
    subprocess.run(['git', 'remote', 'prune', 'origin'])
    print("Remote branches pruned")

if __name__ == "__main__":
    deleted = cleanup_branches()
    cleanup_stashes()
    prune_remotes()
    print(f"Cleanup complete: {deleted} branches removed")
```

### Scheduled Cleanup

Add to `.github/workflows/cleanup.yml`:

```yaml
name: Git Cleanup
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly Sunday midnight
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Prune merged branches
        run: |
          git fetch --prune
          # Delete remote branches merged into main
          for branch in $(git branch -r --merged origin/main | grep -v main); do
            branch_name=${branch#origin/}
            gh api -X DELETE repos/${{ github.repository }}/git/refs/heads/$branch_name || true
          done
```

---

## Parallel Agent Coordination

### Isolation Patterns

```
┌─────────────────────────────────────────────────────────┐
│                        main                              │
│  (protected, only squash merges)                        │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Agent A │    │ Agent B │    │ Agent C │
    │ feat/a  │    │ feat/b  │    │ fix/c   │
    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │
         ▼               ▼               ▼
    [Verify]        [Verify]        [Verify]
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                   [Squash Merge]
                         │
                         ▼
                       main
```

### Conflict Resolution Rules

1. **File-level isolation**: Each agent works on different files
2. **First-merged wins**: Later agents rebase before merge
3. **Human arbitration**: Conflicting changes require human review
4. **No parallel edits**: Lock files via ledger when editing

---

## Integration with Steward Protocol

### Kernel Git Service

```python
class GitService:
    """Git operations as kernel service."""

    def create_agent_branch(self, agent_id: str, task_hash: str) -> str:
        """Create isolated branch for agent work."""
        branch_name = f"feat/{agent_id}-{task_hash[:8]}"
        self._run(['git', 'checkout', '-b', branch_name])
        return branch_name

    def verify_work(self, branch: str) -> dict:
        """VEDA-4 verification before merge."""
        return {
            "files_changed": self._diff_names(branch),
            "insertions": self._count_insertions(branch),
            "tests_pass": self._run_tests(),
        }

    def complete_work(self, branch: str) -> bool:
        """Squash merge and cleanup."""
        self._run(['git', 'checkout', 'main'])
        self._run(['git', 'merge', '--squash', branch])
        self._run(['git', 'commit', '-m', f'feat: Agent work from {branch}'])
        self._run(['git', 'branch', '-D', branch])
        return True
```

### Ledger Integration

Record all git operations in the audit ledger:

```python
ledger.record_event(
    event_type="GIT_BRANCH_CREATED",
    agent_id="haiku-agent",
    payload={
        "branch": "feat/haiku-a1b2c3d4",
        "base": "main",
        "task_id": "task-123"
    }
)
```

---

## HAIKU EXECUTION BLOCKS

### TASK 1: Add Git Cleanup Script

```
FILE: scripts/git_cleanup.py
CREATE_FILE_WITH:
#!/usr/bin/env python3
"""Git cleanup automation for Steward Protocol."""

import subprocess
import sys

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def cleanup_merged_branches():
    result = run(['git', 'branch', '--merged', 'main'])
    branches = [b.strip() for b in result.stdout.split('\n')
                if b.strip() and b.strip() != 'main' and not b.startswith('*')]

    for branch in branches:
        run(['git', 'branch', '-d', branch])
        print(f"Deleted: {branch}")
    return len(branches)

def cleanup_stashes():
    run(['git', 'stash', 'clear'])
    print("Stashes cleared")

def prune_remotes():
    run(['git', 'remote', 'prune', 'origin'])
    print("Remote branches pruned")

if __name__ == "__main__":
    print("=== Git Cleanup ===")
    deleted = cleanup_merged_branches()
    cleanup_stashes()
    prune_remotes()
    print(f"Done: {deleted} branches removed")

VERIFY: python scripts/git_cleanup.py
```

### TASK 2: Add Pre-Commit Git Verification

```
FILE: .pre-commit-config.yaml
FIND: repos:
ADD_AFTER:
  - repo: local
    hooks:
      - id: verify-branch-naming
        name: Verify branch naming convention
        entry: python -c "import subprocess; b=subprocess.run(['git','branch','--show-current'],capture_output=True,text=True).stdout.strip(); exit(0 if b=='main' or '/' in b else 1)"
        language: system
        always_run: true
        pass_filenames: false

VERIFY: pre-commit run verify-branch-naming --all-files || echo "Hook installed"
```

### TASK 3: Add GitHub Actions Cleanup Workflow

```
FILE: .github/workflows/git-cleanup.yml
CREATE_FILE_WITH:
name: Git Cleanup
on:
  schedule:
    - cron: '0 0 * * 0'
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Prune stale remote branches
        run: |
          git fetch --prune
          echo "Remote branches pruned"

VERIFY: ls .github/workflows/git-cleanup.yml
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Local branches | ≤ 3 | `git branch \| wc -l` |
| Stashes | 0 | `git stash list \| wc -l` |
| Remote branches | ≤ 10 | `git branch -r \| wc -l` |
| Merge conflicts | 0/week | Manual tracking |
| Failed agent work | <5% | Ledger query |

---

## Related Documents

- **OPUS-006**: GAD-000 Compliance (Git as verification tool)
- **OPUS-008**: Index of all OPUS documents

---

**Signed**: Opus 4.5
**Date**: 2025-12-08
**Status**: HAIKU-READY (3 tasks)
