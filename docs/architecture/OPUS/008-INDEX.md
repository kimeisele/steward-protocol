# OPUS-008: Architecture Index

> **Status**: ACTIVE
> **Created**: 2025-12-08
> **Last Updated**: 2025-12-09 (Full overhaul)
> **Symbol**: 8 = Infinity Rotated = Krishna's Number
> **Purpose**: Master index of all OPUS architecture documents

---

## Document Registry (VERIFIED 2025-12-09)

| # | Document | Status | Notes |
|---|----------|--------|-------|
| 001 | [Kernel Extraction](001-KERNEL-EXTRACTION.md) | 🔄 IN PROGRESS | 1409 LOC (target: 1008) |
| 002 | [Phoenix Config](002-PHOENIX-CONFIG.md) | 📋 PLANNED | Config caching optimization |
| 003 | [AOS Foundation Repair](003-AOS-FOUNDATION-REPAIR.md) | ✅ COMPLETE | 7 breaks fixed |
| 004 | [Boot Sequence Audit](004-BOOT-SEQUENCE-AUDIT.md) | ✅ COMPLETE | Documented, depends_on TODO |
| 005 | [Unification Roadmap](005-UNIFICATION-ROADMAP.md) | 🔄 MOSTLY DONE | 5/7 phases complete |
| 006 | [GAD-000 Compliance](006-GAD000-COMPLIANCE-AUDIT.md) | ✅ COMPLETE | 5/6 tests pass |
| 007 | [UI Rendering Hardening](007-UNIFIED-UI-RENDERING.md) | ✅ IMPLEMENTED | Three Laws in code |
| 008 | **This Index** | 📍 ACTIVE | You are here |
| 009 | [Unified State (PRAKRITI)](009-UNIFIED-STATE-PRAKRITI.md) | ✅ IMPLEMENTED | state/prakriti.py |
| 010 | [Verification Protocol](010-VERIFICATION-PROTOCOL.md) | ✅ VERIFIED | Trust Score 100% |
| 011 | [Layered Router](011-LAYERED-ROUTER.md) | ✅ IMPLEMENTED | layered_router.py |
| 012 | [System Agents](012-SYSTEM-AGENTS.md) | 📋 PLANNING | BRAHMIN Architecture |
| 014 | [Unified UI Transparency](014-UNIFIED-UI-TRANSPARENCY.md) | 📋 DRAFT | STATE.md, ECONOMY.md |

---

## ✅ What's DONE (Verified Implementations)

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

---

## 🔧 Technical Debt (TODO)

### Priority 1: Kernel Reduction (OPUS-001)
- **Current**: 1409 LOC
- **Target**: 1008 LOC
- **Delta**: -401 LOC to extract
- **Next**: Extract EconomyPlugin, HealthPlugin, ProcessPlugin

### Priority 2: OPUS-005 Remaining Phases
- [ ] PlaybookRouter cleanup (exists in 2 locations)
- [ ] Remaining Loaders migration (5 loaders)
- [ ] CircuitExecutor split (1394-line monolith)
- [ ] Legacy code burn (@deprecated but not deleted)
- [ ] Manifest depends_on validation

### Priority 3: New Features (OPUS-014)
- [ ] STATE.md renderer (Prakriti inspector)
- [ ] ECONOMY.md renderer (token/credit meter)
- [ ] MATRIX.md renderer (routing visualization)

### Priority 4: Test Coverage
- [ ] Test gaps from OPUS-010 (DailyRitual, UniversalProvider)
- [ ] Agent capability test harness

---

## 🚀 For Next Agent

1. **Read this index first**
2. Pick from Technical Debt above
3. Check related OPUS doc for details
4. Make changes on a feature branch
5. Run `pytest tests/ -v` after changes
6. Commit with conventional commit format

---

## Foundational Laws

### GAD-000: Operator Inversion
All 5/6 tests pass. Test 6 (Identity) deferred to GAD-1000.

### Three Laws of Rendering (OPUS-007)
All 3 implemented in BaseRenderer/InterfacePlugin.

---

**Last Verified**: 2025-12-09
**Next Priority**: OPUS-001 Kernel reduction OR OPUS-005 cleanup
