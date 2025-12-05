# Technical Debt Registry

> "Know thy debt, or it shall consume thee" - Srimad Debugging Purana

This document tracks all technical debt in the Steward Protocol codebase.
Each item is prioritized by **SEVERITY** (P0 = fix NOW, P1 = soon, P2 = when possible).

---

## P0: CRITICAL - Test Suite Performance Crisis

**Status**: ✅ RESOLVED (Phase 1)
**Impact**: Tests take 4+ minutes, causing development slowdown
**Root Cause**: No kernel isolation, real initialization in every test

### Solution Implemented (2025-12-05)

**Universal Testable Protocol** - Self-testing components:

```
┌─────────────────────────────────────────────────────────────┐
│ IMPLEMENTED TEST ECOSYSTEM                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ LAYER 1: AUTO-GENERATED (Testable Protocol)                 │
│ ├── 65 components auto-discovered                           │
│ ├── 366 structural tests generated                          │
│ ├── Execution: < 2 seconds                                  │
│ └── Files: vibe_core/protocols/testable.py                  │
│           vibe_core/protocols/testable_registry.py          │
│           vibe_core/plugins/test_orchestration.py           │
│                                                             │
│ LAYER 2: LEGACY SUITE (tests/ - organisch)                  │
│ ├── Behavioral tests (edge cases, ACID, integration)        │
│ ├── Bleibt als Sicherheitsnetz                              │
│ └── Wächst organisch weiter                                 │
│                                                             │
│ CI SCRIPT: scripts/verify_system.py                         │
│ ├── --fast: Critical tests only                             │
│ ├── --lint: Lint/format check                               │
│ └── Exit codes: 0=OK, 1=Critical, 2=Warning, 3=Boot, 4=Lint │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Remaining Action Items
- [x] Create `LightweightTestKernel` (tests/fractal_test_framework.py)
- [x] Create Universal Testable Protocol
- [x] Create CI Fast Lane script
- [ ] Add `@pytest.mark.slow` to stress tests
- [ ] Move legacy tests to tests/legacy_integration/

---

## P1: Kernel Plugin Extraction Incomplete

**Status**: IN PROGRESS
**Impact**: Some domain logic still hardcoded in kernel

### Completed Extractions
- [x] VedicGovernancePlugin (Varna/Ashrama/Paused agents)
- [x] SargaCyclePlugin (DAY/NIGHT_OF_BRAHMA)
- [x] SettingsUIPlugin (SETTINGS.md sync)
- [x] EnvoyUIPlugin (ENVOY.md sync)

### Remaining Candidates
| Component | Lines in kernel | Priority | Notes |
|-----------|-----------------|----------|-------|
| Economic Substrate (Bank/Vault) | 464-496 | P2 | Lazy-loaded, works fine |
| Immune System (Auditor) | 1249-1286 | P2 | Health checks |
| Pulse/Heartbeat | 1681-1723 | P2 | Observation only |
| Tool Discovery | 629-688 | P2 | Boot-time only |

**Decision**: Lower priority - these don't affect kernel stability.

---

## P2: Herald Agent Config Access Pattern

**Status**: FIXED
**Fix Date**: 2025-12-05

Herald agent was accessing `CityConfig.posting_frequency_hours` but config structure changed to nested `herald` section.

**Fix**: Detect nested config and extract herald-specific settings.

---

## P2: Duplicate Class Definitions ("Treibsand")

**Status**: DOCUMENTED
**Impact**: Confusing codebase, potential import conflicts

Multiple locations define similar classes:
- `VibeAgent` defined in multiple places
- `AgentManifest` has overlapping definitions

**Solution**: Use canonical imports from `vibe_core.protocols`.

---

## P2: Boot.py Errors

**Status**: PARTIALLY FIXED
**Impact**: Boot sequence may fail silently

Some agents fail to import during boot. Need better error handling and fallback.

---

## Architecture Notes

### Kernel Stability
The kernel is now structured as:
- **CORE**: Scheduler (pure FIFO), Registry, Ledger, Lineage
- **SECURITY**: Narasimha, CapabilityRegistry (MUST stay in kernel)
- **PLUGINS**: All domain logic (governance, cycles, UI)

### Plugin Hook Order
```
1. on_boot (kernel init)
2. on_task_submit (COSMIC GATE - Sarga)
3. on_task_pre_assign (GOVERNANCE GATE - Varna/Ashrama)
4. on_tick_pre/post (UI sync)
5. on_task_completed/failed (lifecycle)
6. on_shutdown (cleanup)
```

---

## P0 NEW: Kernel-Enforced Integrity (VISION)

**Status**: PLANNED
**Impact**: External agents (e.g., Claude Code CLI) can bypass lint/test scripts via `--no-verify`
**Root Cause**: Integrity checks are external to kernel, not enforced at boot

### The Problem

```
┌─────────────────────────────────────────────────────────────┐
│ CURRENT (VULNERABLE)                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [External Agent] ──git commit --no-verify──> [Repo]        │
│        │                                         │          │
│        └── BYPASSES ─┐                           │          │
│                      ▼                           │          │
│              scripts/verify_system.py            │          │
│              (runs lint, tests)                  │          │
│                                                             │
│  Result: Corrupted code enters codebase                     │
└─────────────────────────────────────────────────────────────┘
```

### The Vision: CodeIntegrityPlugin

```
┌─────────────────────────────────────────────────────────────┐
│ FUTURE (KERNEL-ENFORCED)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RealVibeKernel                                             │
│  ├── CodeIntegrityPlugin (priority: -100, runs FIRST)       │
│  │   ├── on_boot(): Verify codebase integrity               │
│  │   │   ├── Check lint (critical errors only)              │
│  │   │   ├── Check format (ruff format --check)             │
│  │   │   ├── Run fast structural tests                      │
│  │   │   └── REFUSE TO BOOT if integrity violated           │
│  │   │                                                      │
│  │   ├── on_task_submit(): Gate code-modifying tasks        │
│  │   │   └── Re-verify after code changes                   │
│  │   │                                                      │
│  │   └── Hooks into: Narasimha (security), Auditor          │
│  │                                                          │
│  └── [All other plugins...]                                 │
│                                                             │
│  Result: No corrupted code can execute in kernel            │
└─────────────────────────────────────────────────────────────┘
```

### Tests as Living City Architecture

The test system should be like a **city** - we build infrastructure (protocols, adapters),
but the tests grow organically on top:

```
┌─────────────────────────────────────────────────────────────┐
│ LIVING TEST CITY                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ INFRASTRUCTURE LAYER (we build once)                        │
│ ├── Testable Protocol (interfaces)                          │
│ ├── TestableRegistry (discovery)                            │
│ ├── TestOrchestrationPlugin (execution)                     │
│ └── Adapters (Agent, Plugin, Tool, Ledger, etc.)            │
│                                                             │
│ ORGANIC GROWTH LAYER (adapts automatically)                 │
│ ├── When interface changes → Tests adapt                    │
│ ├── When component added → Auto-discovered                  │
│ ├── When test becomes stale → Detected by Circuit/Playbook  │
│ └── No manual test maintenance for structural checks        │
│                                                             │
│ BEHAVIORAL LAYER (human-written, grows organically)         │
│ ├── tests/legacy_integration/ (safety net)                  │
│ ├── Edge cases, ACID tests, integration scenarios           │
│ └── Grows as developers add complex behaviors               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Roadmap

| Phase | Timeframe | Deliverable |
|-------|-----------|-------------|
| Phase 1 | ✅ DONE | Universal Testable Protocol, 366 auto-tests |
| Phase 2 | SHORT-TERM | Add `@pytest.mark.slow`, organize legacy tests |
| Phase 3 | MEDIUM-TERM | CodeIntegrityPlugin (boot-time verification) |
| Phase 4 | LONG-TERM | Circuit/Playbook test architecture, stale test detection |

---

## Roadmap Summary

### Short-Term (Stabilization)
- [x] Universal Testable Protocol
- [x] CI Fast Lane script (verify_system.py)
- [ ] Add `@pytest.mark.slow` to stress tests
- [ ] Move legacy tests to tests/legacy_integration/
- [ ] Document all P2 items properly

### Medium-Term (Kernel Enforcement)
- [ ] CodeIntegrityPlugin (boot-time lint/test check)
- [ ] Integration with Narasimha security layer
- [ ] Refuse boot on critical integrity violations
- [ ] Hook into task submission for code changes

### Long-Term (Living Test System)
- [ ] Circuit/Playbook test architecture
- [ ] Stale test detection (test references deleted code)
- [ ] Test dependency graph
- [ ] Auto-update tests when interfaces change
- [ ] Test coverage metrics by component type

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2025-12-05 | Claude | Created document, documented test performance crisis |
| 2025-12-05 | Claude | Extracted SargaCyclePlugin from kernel |
| 2025-12-05 | Claude | Extracted VedicGovernancePlugin from kernel |
| 2025-12-05 | Claude | Implemented Universal Testable Protocol (Phase 1 complete) |
| 2025-12-05 | Claude | Added Kernel-Enforced Integrity vision (P0 NEW) |
| 2025-12-05 | Claude | Added short/medium/long term roadmap |
