# OPUS-024: Kernel Protection Audit

> **Status**: AUDIT COMPLETE - AWAITING DECISION
> **Date**: 2025-12-11
> **Author**: Claude Opus (Audit by secondary agent)
> **Depends On**: 001-KERNEL-EXTRACTION, 022-KERNEL-SCALING

---

## Executive Summary

Kernel protection is **THEATER**. Detection exists but is never called. Pre-commit only guards 1 of 3 files.

---

## 1. Critical Gaps Found

| # | Gap | Evidence | Severity |
|---|-----|----------|----------|
| 1 | `verify_kernel.py` NOT IN CI | `steward-ci.yml` has no hash verification step | 🔴 CRITICAL |
| 2 | Pre-commit only protects 1/3 files | `.pre-commit-config.yaml:88` only guards `kernel_impl.py` | 🔴 CRITICAL |
| 3 | `InterfacePlugin` uses `--no-verify` | `plugin_main.py:556` bypasses hooks for auto-commits | 🟡 MEDIUM |
| 4 | Doc/Reality LOC mismatch | `001-KERNEL-EXTRACTION.md` says 1410, actual is 1505 | 🟡 MEDIUM |
| 5 | Hash check is dead code | `verify_kernel.py --verify` works but nothing calls it | 🔴 CRITICAL |
| 6 | `TECHNICAL_DEBT.md` acknowledges bypass | Lines 186-204 describe `--no-verify` as "PLANNED" fix | 🟡 MEDIUM |

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

| File | LOC | Pre-commit | CI Hash | Status |
|------|-----|------------|---------|--------|
| `vibe_core/kernel_impl.py` | 1505 | ✅ | ❌ | PARTIAL |
| `vibe_core/plugin_protocol.py` | 402 | ❌ | ❌ | UNPROTECTED |
| `vibe_core/plugin_loader.py` | 381 | ❌ | ❌ | UNPROTECTED |
| **TOTAL** | **2288** | | | |

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

## 6. Decision Required

| Option | Detection | Prevention | Effort | Recommendation |
|--------|-----------|------------|--------|----------------|
| A: Wire Existing | ✅ | ❌ | 1h | Minimum viable |
| B: Auto-Restore | ✅ | ✅ (partial) | 2-3h | Good balance |
| C: Golden Copy | ✅ | ✅ (full) | 4-6h | Maximum security |

**My recommendation**: Option A immediately (fix the dead code), then Option B or C based on how often kernel changes slip through.

---

## 7. Immediate Fixes (Regardless of Option)

These should be done NOW:

1. **Update LOC in docs**: `001-KERNEL-EXTRACTION.md` says 1410, actual is 1505
2. **Extend pre-commit**: Add `plugin_protocol.py` and `plugin_loader.py`
3. **Wire CI**: Add `verify_kernel.py --verify` to `steward-ci.yml`

---

## 8. Open Questions

1. Which protection option to implement?
2. Is `InterfacePlugin --no-verify` intentional?
3. Should we audit ALL `--no-verify` usage in codebase?
4. Who can update golden copies (if Option C)?

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

**Next Action**: AWAITING DECISION on which option to implement.
