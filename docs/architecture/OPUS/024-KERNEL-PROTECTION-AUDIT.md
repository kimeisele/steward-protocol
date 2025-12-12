# OPUS-024: Kernel Protection Audit

> **Status**: ✅ IMPLEMENTED: Option B + Security Hardening
> **Date**: 2025-12-11
> **Author**: Claude Opus (Audit by secondary agent)
> **Depends On**: 001-KERNEL-EXTRACTION, 022-KERNEL-SCALING

---

<!-- @HARNESS
files:
  # Security Ring 0 - Core Orchestration
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/kernel_ops.py
    required: true
  # Security Ring 0 - Plugin System
  - path: vibe_core/plugin_protocol.py
    required: true
  - path: vibe_core/plugin_loader.py
    required: true
  # Security Ring 0 - Security (Sword, Shield, Gate)
  - path: vibe_core/narasimha.py
    required: true
  - path: vibe_core/capability_registry.py
    required: true
  - path: vibe_core/bridge.py
    required: true
  # Governance Scripts
  - path: scripts/governance/restore_kernel.sh
    required: true
  - path: scripts/governance/verify_kernel.py
    required: true
  - path: scripts/governance/kernel_hashes.json
    required: true
  # Pre-commit Hook Config
  - path: .pre-commit-config.yaml
    required: true
  # Native Git Hook
  - path: .githooks/pre-commit
    required: true
  # Claude Code SessionStart Hook
  - path: .claude/hooks/session-start.sh
    required: true
tests:
  - python scripts/governance/verify_kernel.py --verify
wiring:
  - pattern: "kernel-is-eternal"
    in: .pre-commit-config.yaml
  - pattern: "PROTECTED_FILES="
    in: scripts/governance/restore_kernel.sh
  - pattern: "kernel-integrity:"
    in: .github/workflows/steward-ci.yml
  - pattern: "core.hooksPath"
    in: .claude/hooks/session-start.sh
absent:
  - pattern: "TODO.*kernel.*protection"
    in: scripts/governance/restore_kernel.sh
  - pattern: "FIXME.*VISNU"
    in: vibe_core/kernel_impl.py
-->

## Executive Summary

Kernel protection is **THEATER**. Detection exists but is never called. Pre-commit only guards 1 of 3 files.

---

## 1. Critical Gaps Found

| # | Gap | Evidence | Severity | Status |
|---|-----|----------|----------|--------|
| 1 | `verify_kernel.py` NOT IN CI | `steward-ci.yml` has no hash verification step | 🔴 CRITICAL | ✅ FIXED |
| 2 | Pre-commit only protects 1/3 files | `.pre-commit-config.yaml:88` only guards `kernel_impl.py` | 🔴 CRITICAL | ✅ FIXED |
| 3 | `InterfacePlugin` uses `--no-verify` | `plugin_main.py:556` bypasses hooks for auto-commits | 🟡 MEDIUM | Documented |
| 4 | Doc/Reality LOC mismatch | `001-KERNEL-EXTRACTION.md` says 1410, actual is 1505 | 🟡 MEDIUM | ✅ FIXED |
| 5 | Hash check is dead code | `verify_kernel.py --verify` works but nothing calls it | 🔴 CRITICAL | ✅ FIXED |
| 6 | `TECHNICAL_DEBT.md` acknowledges bypass | Lines 186-204 describe `--no-verify` as "PLANNED" fix | 🟡 MEDIUM | Documented |
| 7 | `kernel_ops.py` NOT protected | Kill-Switch + Immunsystem unguarded | 🔴 CRITICAL | ✅ FIXED |
| 8 | `kernel_hashes.json` mutable | Hash + kernel can be modified in same PR | 🔴 CRITICAL | ✅ FIXED |

---

## 2. Current Attack Surface

```
Agent modifies plugin_loader.py
    ↓
Pre-commit: ✅ PASS (only checks kernel_impl.py!)
    ↓
CI: ✅ PASS (verify_kernel.py never called!)
    ↓
Merged to main with corrupted loader 💀
```

**Same attack works for**: `plugin_protocol.py`

---

## 3. Files That SHOULD Be Protected

| Category | File | LOC | Pre-commit | CI Hash | Status |
|----------|------|-----|------------|---------|--------|
| Core | `vibe_core/kernel_impl.py` | 1505 | ✅ | ✅ | PROTECTED |
| Core | `vibe_core/kernel_ops.py` | 326 | ✅ | ✅ | PROTECTED |
| Plugins | `vibe_core/plugin_protocol.py` | 402 | ✅ | ✅ | PROTECTED |
| Plugins | `vibe_core/plugin_loader.py` | 381 | ✅ | ✅ | PROTECTED |
| Security | `vibe_core/narasimha.py` | 414 | ✅ | ✅ | PROTECTED |
| Security | `vibe_core/capability_registry.py` | 343 | ✅ | ✅ | PROTECTED |
| Security | `vibe_core/bridge.py` | 28 | ✅ | ✅ | PROTECTED |
| **TOTAL** | | **3399** | | | |

---

## 4. Protection Options

### Option A: Wire Existing Tools (Minimal)

**Effort**: 1 hour
**Effect**: Detection only (CI fails on change)

Changes:
1. Add `verify_kernel.py --verify` step to `steward-ci.yml`
2. Extend pre-commit regex to cover all 3 files

```yaml
# .pre-commit-config.yaml
files: ^vibe_core/(kernel_impl|plugin_protocol|plugin_loader)\.py$
```

```yaml
# steward-ci.yml
- name: Verify Kernel Integrity
  run: python scripts/governance/verify_kernel.py --verify
```

**Limitation**: Still only DETECTS. Agent's PR fails but damage exists in branch.

---

### Option B: Auto-Restore (Prevention)

**Effort**: 2-3 hours
**Effect**: Changes automatically reverted

Pre-commit hook that RESTORES instead of just failing:

```bash
#!/bin/bash
# restore_kernel.sh
for file in kernel_impl.py plugin_protocol.py plugin_loader.py; do
    git checkout HEAD -- "vibe_core/$file" 2>/dev/null || true
done
```

**Benefit**: Agent's changes literally disappear on commit attempt.
**Limitation**: Doesn't help if agent uses `--no-verify`.

---

### Option C: Golden Copy Repository (Maximum Protection)

**Effort**: 4-6 hours
**Effect**: Single source of truth, cryptographic verification

Structure:
```
scripts/governance/
├── kernel_golden/
│   ├── kernel_impl.py.golden
│   ├── plugin_protocol.py.golden
│   └── plugin_loader.py.golden
├── kernel_hashes.json
└── verify_kernel.py  (enhanced)
```

CI workflow:
1. Compare runtime files against golden copies
2. If mismatch → auto-restore from golden → commit → continue
3. Hash verification as secondary check

**Benefit**: Even `--no-verify` can't persist changes (CI restores).
**Complexity**: Need to manage golden copy updates.

---

## 5. The `--no-verify` Problem

### Current Usage in Codebase

```python
# vibe_core/plugins/interface/plugin_main.py:556
subprocess.run(["git", "commit", "--no-verify", "-m", message])
```

This is used by `InterfacePlugin` for auto-committing UI changes.

### Question

Is this intentional for UI files only, or a vulnerability?

If intentional: Document as exception.
If vulnerability: Audit all `--no-verify` usage.

---

## 6. Decision: Option B

| Option | Detection | Prevention | Effort | Decision |
|--------|-----------|------------|--------|----------|
| A: Wire Existing | ✅ | ❌ | 1h | ❌ Half-measure |
| B: Auto-Restore | ✅ | ✅ (partial) | 2-3h | ✅ **SELECTED** |
| C: Golden Copy | ✅ | ✅ (full) | 4-6h | Overkill for now |

**Rationale**: Option A only detects - that's theater. Option B actually PREVENTS changes by auto-restoring. Option C adds complexity we don't need yet.

---

## 7. Immediate Fixes (Regardless of Option)

These should be done NOW:

1. **Update LOC in docs**: `001-KERNEL-EXTRACTION.md` says 1410, actual is 1505
2. **Extend pre-commit**: Add `plugin_protocol.py` and `plugin_loader.py`
3. **Wire CI**: Add `verify_kernel.py --verify` to `steward-ci.yml`

---

## 8. Implementation Plan (Option B)

1. **Create `scripts/governance/restore_kernel.sh`** - auto-restore script
2. **Extend pre-commit** - protect all 3 files, use restore script instead of `language: fail`
3. **Wire CI** - add `verify_kernel.py --verify` as backup check
4. **Update hashes** - regenerate `kernel_hashes.json` with current state
5. **Update docs** - fix LOC in `001-KERNEL-EXTRACTION.md`

### Remaining Questions (P2)

- `InterfacePlugin --no-verify`: Document as intentional exception for UI files
- Full `--no-verify` audit: Defer unless issues arise

---

## Appendix: File References

| File | Purpose |
|------|---------|
| `.pre-commit-config.yaml:82-88` | Current kernel protection (incomplete) |
| `scripts/governance/verify_kernel.py` | Hash verification (dead code) |
| `scripts/governance/kernel_hashes.json` | Baseline hashes |
| `.github/workflows/steward-ci.yml` | CI workflow (missing kernel check) |
| `TECHNICAL_DEBT.md:186-204` | Documents known bypass vulnerability |

---

---

## 9. Security Hardening (Post-Audit Fixes)

After initial Option B implementation, secondary audit (Gemini) found two additional critical gaps:

### 9.1 kernel_ops.py Backdoor

**Problem**: `kernel_impl.py` delegates to `kernel_ops.py` which contains:
- `narasimha_destroy_agent()` - Kill-Switch
- `check_system_health()` - Immunsystem
- `grant_repo_access()` - Security critical

**Fix**: Added `kernel_ops.py` to protected files list.

### 9.2 Hash File Manipulation

**Problem**: `kernel_hashes.json` is mutable. Attacker can:
1. Modify kernel file
2. Modify hash file to match
3. CI verifies manipulated hash against manipulated file → PASS

**Fix**: CI now blocks any PR that modifies `kernel_hashes.json`.
Hash updates require separate PR with Senior review.

---

---

## 10. Security Ring 0 (Final Definition)

After multiple audit rounds, the complete **Security Ring 0** is defined:

### Philosophy

> "We cannot freeze everything (the project dies), but we must freeze what controls **Life, Death, and Rights**."

### The Ring

| Role | File | Purpose |
|------|------|---------|
| **Brain** | `kernel_impl.py` | Orchestration |
| **Hands** | `kernel_ops.py` | Delegated operations |
| **Interface** | `plugin_protocol.py` | Plugin contracts |
| **Loader** | `plugin_loader.py` | Plugin loading |
| **Sword** | `narasimha.py` | Kill-Switch |
| **Shield** | `capability_registry.py` | Permissions |
| **Gate** | `bridge.py` | Constitution enforcement |

### Attack Scenarios Now Blocked

| Attack | Before | After |
|--------|--------|-------|
| Modify kernel_impl.py | Pre-commit blocks | ✅ Auto-restore |
| Modify narasimha.py (disable kill-switch) | ❌ UNPROTECTED | ✅ Auto-restore |
| Modify capability_registry.py (grant self rights) | ❌ UNPROTECTED | ✅ Auto-restore |
| Modify bridge.py (bypass constitution) | ❌ UNPROTECTED | ✅ Auto-restore |
| Modify kernel + hash together | CI passes | ✅ CI blocks hash changes |

### What Remains Mutable

Everything else (ledger, event_bus, filesystem, etc.) is **infrastructure**:
- If manipulated = system broken, but not "hostile takeover"
- Still monitored by CI (lint, tests, Watchman)
- Can be updated via normal PR process

---

## 11. Total War Lockdown (Final Expansion)

Secondary audit (Gemini) identified that protecting only `steward-ci.yml` left 9 other workflow files unprotected. A rascal agent could:
1. Modify `factory.yml` to inject malicious code
2. Create a new `evil-workflow.yml` with admin privileges

### Solution: Protect ALL Workflows

| Category | Files | Count |
|----------|-------|-------|
| Kernel Code | kernel_impl, kernel_ops, plugin_protocol, plugin_loader, narasimha, capability_registry, bridge | 7 |
| Governance | restore_kernel.sh, verify_kernel.py, kernel_hashes.json | 3 |
| Workflows | attest, container-build, deploy, factory, heartbeat, integration-tests, scheduled-agents, scribe-docs, steward-ci, system-cycle | 10 |
| Config | .pre-commit-config.yaml | 1 |
| **TOTAL** | | **21** |

### New Attack Blocked: Unauthorized Workflow Creation

```
Agent creates .github/workflows/evil-backdoor.yml
    ↓
Pre-commit: 🚨 DETECTED (matches .github/workflows/*.yml)
    ↓
restore_kernel.sh: 💀 DESTROYED (not in origin/main)
    ↓
CI: 🚫 BLOCKED (file not in blessed list)
```

### Protection Mechanisms

1. **Pre-commit hook**: Triggers on ANY .yml/.yaml in .github/workflows/
2. **restore_kernel.sh**: Auto-restores existing files + DESTROYS new unauthorized files
3. **CI Nuclear Verification**: Checks all 21 files + detects new workflow files

---

**Status**: ✅ TOTAL WAR LOCKDOWN COMPLETE - 21 files protected + new workflow block.

---

## 12. Native Git Hooks Integration (Claude Code Web Fix)

**Date**: 2025-12-11

### Problem Discovered

The `kernel-is-eternal` hook in `.pre-commit-config.yaml` requires `pre-commit install` to be active.
In Claude Code Web containers, `postCreateCommand` from `devcontainer.json` is NOT executed.
Result: AI agents could commit to kernel files without any local blocking.

### Solution: GUARD 6 in `.githooks/pre-commit`

Added native git hook guard that calls `restore_kernel.sh` directly:

```bash
# .githooks/pre-commit - GUARD 6
RESTORE_SCRIPT="$REPO_ROOT/scripts/governance/restore_kernel.sh"
if [ -x "$RESTORE_SCRIPT" ]; then
    OUTPUT=$("$RESTORE_SCRIPT" 2>&1)
    # Auto-restores protected files from origin/main
fi
```

### Activation Requirement

The native hook ONLY works if `core.hooksPath` is set:

```bash
git config --local core.hooksPath .githooks
```

This must be set via:
1. **Devcontainer**: `postCreateCommand` in `devcontainer.json` (existing)
2. **Claude Code Web**: SessionStart hook in `.claude/settings.json` ✅ IMPLEMENTED
3. **Manual**: Developer runs the command

### Defense Layers Now

| Layer | Mechanism | Blocks Commit | Blocks Merge |
|-------|-----------|---------------|--------------|
| 0 | `.githooks/pre-commit` GUARD 6 | ✅ (if hooksPath set) | N/A |
| 1 | `.pre-commit-config.yaml` kernel-is-eternal | ✅ (if pre-commit installed) | N/A |
| 2 | CI VISNU kernel-integrity job | N/A | ✅ |

**Claude Code Web**: Kernel protection is AUTOMATIC via `.claude/settings.json` SessionStart hook.
No manual steps required - every session auto-configures git hooks.

### SessionStart Hook Implementation

Created `.claude/hooks/session-start.sh` registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"
      }]
    }]
  }
}
```

**What it does:**
1. Installs dependencies (`uv pip install -e .[dev]`)
2. Enables git hooks (`git config --local core.hooksPath .githooks`)

**GAD-000 Compliance:**
- JSON output for AI parseability
- Clear status codes (ok, configured, skip, error)
- Solution guidance in structured format

**GUARD 6 GAD-000 Output:**
```json
{
  "guard": "VISNU_KERNEL_PROTECTION",
  "status": "RESTORED",
  "action": "auto_reverted_to_origin_main",
  "protected_files_count": 21,
  "restored_files": ["vibe_core/kernel_impl.py"],
  "reason": "Security Ring 0 files are immutable",
  "solution": "Create a plugin in vibe_core/plugins/your_feature/ instead",
  "documentation": "docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md"
}
```

This ensures AI agents understand WHY they are "rascals" and HOW to do it correctly.
