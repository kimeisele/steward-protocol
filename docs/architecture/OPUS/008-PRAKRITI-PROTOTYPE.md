# OPUS-008: Prakriti Prototype

> **Status**: 🚧 IN_PROGRESS
> **Created**: 2025-12-12
> **Author**: Claude Opus 4
> **Depends On**: OPUS-009 (Concept), OPUS-027 (Implementation), OPUS-028 (Git Integration)
> **Purpose**: Test PROMPT/OPUS workflow with real Prakriti state integration
> **Scope**: Add Prakriti state panel to OPUS.md, verify @HARNESS accuracy

<!-- @HARNESS
files:
  # Core Prakriti files (must exist)
  - path: vibe_core/state/prakriti.py
    required: true
  - path: vibe_core/state/git_state.py
    required: true
  - path: vibe_core/state/ledger_state.py
    required: true
  - path: vibe_core/state/__init__.py
    required: true
  # OpusDashboardRenderer (will be modified)
  - path: vibe_core/plugins/opus_assistant/render/opus_dashboard_renderer.py
    required: true
tests:
  - scripts/ci/test_kernel_boot.py
wiring:
  # Prakriti session management
  - pattern: "def begin_session"
    in: vibe_core/state/prakriti.py
  - pattern: "def end_session"
    in: vibe_core/state/prakriti.py
  - pattern: "class KernelSessionContext"
    in: vibe_core/state/prakriti.py
  # GitState write operations
  - pattern: "def commit\\("
    in: vibe_core/state/git_state.py
  - pattern: "VISNU_PROTECTED"
    in: vibe_core/state/git_state.py
  # LedgerState
  - pattern: "class LedgerState"
    in: vibe_core/state/ledger_state.py
  - pattern: "def record_sync"
    in: vibe_core/state/ledger_state.py
absent:
  # InterfacePlugin should NOT have auto-commit anymore
  - pattern: "_auto_commit_ui_files"
    in: vibe_core/plugins/interface/plugin_main.py
config:
  - section: guardrails.ui_files
-->

---

## Executive Summary

This document serves two purposes:

1. **Workflow Test**: Validate the PROMPT.md + OPUS.md + @HARNESS workflow
2. **Feature Spec**: Add Prakriti state panel to OPUS.md renderer

The @HARNESS above is the **contract**. If verification fails, this doc is RED.

---

## Problem Statement

OPUS.md currently shows:
- OPUS-027: **35%** verified
- OPUS-028: **25%** verified

But I claimed these were "IMPLEMENTED". This is exactly the problem:
- Claims without @HARNESS verification = FICTION
- The workflow broke because I wrote status before ensuring @HARNESS matches code

---

## Success Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| @HARNESS files exist | ❓ | Run verification |
| @HARNESS wiring patterns match | ❓ | Run verification |
| @HARNESS absent patterns verified | ❓ | Run verification |
| OPUS.md shows Prakriti panel | ❌ | Not implemented yet |
| Kernel boot test passes | ❓ | Run test |

---

## Implementation Plan

### Phase 1: Fix @HARNESS in OPUS-027/028

The @HARNESS sections in those docs have patterns that don't match the actual code.

**Action**: Update @HARNESS to match reality, not aspiration.

### Phase 2: Add Prakriti Panel to OpusRenderer

**File**: `vibe_core/plugins/interface/renderers/opus/opus_renderer.py`

Add a new panel that shows:
```
## Prakriti State

| Layer | Status | Last Sync |
|-------|--------|-----------|
| STHULA (Git) | dirty/clean | commit sha |
| PRANA (Ledger) | entries | head hash |
| PURUSHA (Session) | active/none | session_id |
```

### Phase 3: Verify Full Workflow

1. Run kernel boot test
2. Check OPUS.md verification score
3. Confirm this doc shows ✅ not ❌

---

## Design Decisions

### 1. @HARNESS First, Claims Second

**Rule**: Never mark status as "IMPLEMENTED" until @HARNESS verification passes.

**Enforcement**: PROMPT.md guardian protocol.

### 2. Prakriti Panel is Informational

The panel shows current state, not claims. It reads from Prakriti at render time.

---

## Verification Protocol

After implementation, run:

```bash
# 1. Kernel boot (triggers OPUS.md render)
python scripts/ci/test_kernel_boot.py

# 2. Check verification score
grep "008-PRAKRITI-PROTOTYPE" OPUS.md

# 3. Should show 100% or list specific failures
```

---

## Related Documents

- **OPUS-000**: Master Index
- **OPUS-009**: Unified State concept
- **OPUS-027**: Unified State implementation (master plan)
- **OPUS-028**: Prakriti Git integration

---

**Author**: Claude Opus 4
**Date**: 2025-12-12
**Status**: 🚧 IN_PROGRESS - This doc is a live test of the workflow
