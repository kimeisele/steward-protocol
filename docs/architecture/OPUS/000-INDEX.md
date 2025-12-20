# OPUS-000: Architecture Index

> **Status**: ACTIVE
> **Created**: 2025-12-08
> **Last Updated**: 2025-12-12 (Moved from OPUS-008)
> **Symbol**: 0 = Origin = The Seed from which all OPUS grows
> **Purpose**: Master index of all OPUS architecture documents

---

## Document Registry (VERIFIED 2025-12-12)

| # | Document | Status | Notes |
|---|----------|--------|-------|
| 001 | [Kernel Extraction](001-KERNEL-EXTRACTION.md) | 🔒 LOCKED | 1410 LOC ETERNAL |
| 002 | [Phoenix Config](002-PHOENIX-CONFIG.md) | 📋 PLANNED | Config caching optimization |
| 003 | [AOS Foundation Repair](003-AOS-FOUNDATION-REPAIR.md) | ✅ COMPLETE | 7 breaks fixed |
| 004 | [Boot Sequence Audit](004-BOOT-SEQUENCE-AUDIT.md) | ✅ COMPLETE | Documented |
| 005 | [Unification Roadmap](005-UNIFICATION-ROADMAP.md) | ✅ MOSTLY DONE | 5/7 phases complete |
| 006 | [GAD-000 Compliance](006-GAD000-COMPLIANCE-AUDIT.md) | ✅ VERIFIED | 5/6 tests pass |
| 000 | **This Index** | 📍 ACTIVE | You are here |
| 008 | [Prakriti Prototype](008-PRAKRITI-PROTOTYPE.md) | 🚧 IN_PROGRESS | Internal state workflow |
| 009 | [Unified State (PRAKRITI)](009-UNIFIED-STATE-PRAKRITI.md) | ✅ IMPLEMENTED | state/prakriti.py (concept) |
| 010 | [Verification Protocol](010-VERIFICATION-PROTOCOL.md) | ✅ VERIFIED | Trust Score 100% |
| 011 | [Layered Router](011-LAYERED-ROUTER.md) | ✅ IMPLEMENTED | layered_router.py |
| 012 | [System Agents](012-SYSTEM-AGENTS.md) | 📋 PLANNING | BRAHMIN Architecture |
| 014 | [Unified UI Transparency](014-UNIFIED-UI-TRANSPARENCY.md) | 📋 DRAFT | STATE.md, ECONOMY.md |
| 020 | [Container Migration](020-CONTAINER-MIGRATION-READY.md) | 📋 READY | Not tested |
| 024 | [Kernel Protection (VISNU)](024-KERNEL-PROTECTION-AUDIT.md) | ✅ IMPLEMENTED | 21 files protected |
| 025 | [PATH Lobotomy Crisis](025-PATH-LOBOTOMY-CRISIS.md) | 🔴 CRITICAL | 75% remaining |
| 027 | [Unified State Implementation](027-UNIFIED-STATE-IMPLEMENTATION.md) | ✅ IMPLEMENTED | Master plan for state |
| 028 | [Prakriti Git Integration](028-PRAKRITI-GIT-INTEGRATION.md) | ✅ IMPLEMENTED | Phases 1-4 complete |
| 150 | [Unified Interface Audit](150-UNIFIED-INTERFACE-AUDIT.md) | 🚧 IN_PROGRESS | Architecture clarification |
| 151 | [Markdown Reality](151-MARKDOWN-REALITY.md) | ✅ PARADIGM | GAD-000 Operator Inversion |

---

## ✅ Verified Implementations

| Component | Location | Verified |
|-----------|----------|----------|
| `StructuredError` | `errors.py:90` | ✅ |
| `get_capabilities()` | `kernel_impl.py:638` | ✅ |
| `get_system_status()` | `kernel_impl.py:586` | ✅ |
| `UnifiedTrace` | `runtime/unified_trace.py:37` | ✅ |
| `UnifiedCLI` | `cli/unified_cli.py:24` | ✅ |
| `LayeredRouter` | `runtime/layered_router.py` | ✅ |
| `Prakriti` | `state/prakriti.py:48` | ✅ |
| `_create_backup` (Law 1) | `renderers/base.py:503` | ✅ |
| `_render_error_placeholder` (Law 2) | `plugin_main.py:178` | ✅ |
| `_last_content_hash` (Law 3) | `renderers/base.py:52` | ✅ |
| Idempotency keys | `scheduling/in_memory.py:47` | ✅ |
| `LedgerState` | `state/ledger_state.py` | ✅ |
| `GitState.commit()` | `state/git_state.py:313` | ✅ |
| `VISNU_PROTECTED` | `state/git_state.py:25` | ✅ |
| `Prakriti.begin_session()` | `state/prakriti.py` | ✅ |
| `Prakriti.end_session()` | `state/prakriti.py` | ✅ |
| `StateRenderer` | `plugins/interface/renderers/state.py` | ✅ |
| `EconomyRenderer` | `plugins/interface/renderers/economy.py` | ✅ |

---

## 🔒 Kernel Protection

The kernel is now **ETERNAL** (1410 LOC, locked via pre-commit hook).

**All new features must be plugins.** See OPUS-001 for details.

---

## 🔧 Remaining Technical Debt

### 🔴 CRITICAL: OPUS-025 PATH Lobotomy
- [ ] 75% of path migrations still pending
- [ ] Hardcoded paths need config/dynamic resolution
- See docs/architecture/OPUS/025-PATH-LOBOTOMY-CRISIS.md

### OPUS-005: Remaining Phases
- [ ] PlaybookRouter cleanup
- [ ] CircuitExecutor split
- [ ] Legacy code burn

### OPUS-014: New Renderers
- [ ] STATE.md, ECONOMY.md, MATRIX.md

### OPUS-027/028: Final Phases
- [ ] Config extension (auto_commit_mode)
- [ ] Test suite for state write ops

---

## 🚀 For Next Agent

1. Read this index first
2. Check related OPUS doc
3. Create feature branch
4. Run `pytest tests/ -v`
5. Push and create PR

---

**Last Verified**: 2025-12-12
**Kernel**: 🔒 LOCKED (1410 LOC ETERNAL)
**State Management**: ✅ OPUS-027/028 Implemented
