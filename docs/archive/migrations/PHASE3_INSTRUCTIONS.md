# 🔧 PHOENIX PROTOCOL - PHASE 3 INSTRUCTIONS

**For:** Next Implementation Agent
**Date:** 2025-11-27
**Priority:** P2 - MEDIUM
**Estimated Time:** 2-3 days

---

## 🎯 MISSION

Clean up temporary aliases from Phase 2, consolidate duplicate systems, optimize imports, and prepare the unified VibeOS 1.5 for production use.

**NO NEW FEATURES. CONSOLIDATE & OPTIMIZE.**

---

## 📋 PREREQUISITE

Phase 2 must be complete:
- ✅ All 9 modules ported and working
- ✅ 22/22 integration tests passing
- ✅ HERALD & FORUM agents operational
- ✅ PHASE2_INTEGRATION_REPORT.md exists

**Current branch:** `claude/process-task-list-01Dpmm3aumM3DeWdcQ195xQF`
**Status:** ✅ Ready for Phase 3

---

## ✅ TASK 1: Audit & Document Temporary Aliases

**Files to review:**
1. `vibe_core/playbook/__init__.py` - PlaybookEngine alias
2. `vibe_core/config/__init__.py` - get_config alias
3. `vibe_core/specialists/__init__.py` - Specialist classes
4. `vibe_core/agent_protocol.py` - AgentResponse class

**Action Items:**
- [ ] Create CHANGELOG.md entry for alias deprecation timeline
- [ ] Mark aliases with `# TODO: Remove in v2.0` comments
- [ ] Document why each alias exists
- [ ] Keep aliases - they provide backward compatibility

**Success Criteria:**
- ✅ All aliases documented
- ✅ Deprecation timeline clear
- ✅ No removal of aliases (only documentation)

---

## ✅ TASK 2: Consolidate Store Systems

**Systems to analyze:**
- `vibe_core/store/` (artifact_store, manifest_store, sqlite_store)
- `vibe_core/ledger.py` (immutable audit trail)

**Design Principle:**
These serve different purposes and should coexist:
- **store/** = Mutable data (artifacts, manifests, caching)
- **ledger.py** = Immutable events (audit trail, compliance)

**Action Items:**
- [ ] Create SEPARATION_OF_CONCERNS.md document
- [ ] Clarify in docstrings the distinction
- [ ] Ensure no circular imports between store/ and ledger
- [ ] Test that both systems work together

**Success Criteria:**
- ✅ Documentation explains both systems
- ✅ No circular imports
- ✅ Both systems functional

---

## ✅ TASK 3: Consolidate Config Systems

**Systems to check:**
1. `vibe_core/config/` (loader.py, schema.py)
2. `config/` directory (if separate)
3. Configuration files:
   - agent_city.yaml
   - steward.yaml
   - .env example

**Action Items:**
- [ ] Audit all config sources
- [ ] Ensure single source of truth
- [ ] Document config hierarchy (env vars > config files > defaults)
- [ ] Add environment variable support if missing

**Success Criteria:**
- ✅ Single config entry point
- ✅ Clear hierarchy documented
- ✅ Tests verify config loading

---

## ✅ TASK 4: Optimize Imports

**Potential issues to check:**
1. Circular imports between:
   - runtime → llm → providers
   - playbook → specialists → agents
   - agents → agent_protocol

2. Missing lazy loading:
   - Heavy imports in __init__.py files
   - Could delay startup

**Action Items:**
- [ ] Run circular import check: `python -m py_compile vibe_core/**/*.py`
- [ ] Identify unused imports
- [ ] Move heavy imports to lazy loading where appropriate
- [ ] Update __init__.py files with explicit exports only

**Success Criteria:**
- ✅ Zero circular imports
- ✅ Fast startup time
- ✅ All tests still passing

**Command to verify:**
```bash
python << 'EOF'
import sys
sys.path.insert(0, '.')
for i in range(10):  # Try 10 times
    import importlib
    importlib.invalidate_caches()
    from vibe_core.runtime import KernelOracle
    from vibe_core.playbook import PlaybookEngine
    from vibe_core.specialists import PlanningSpecialist
print("✅ No circular imports detected")
EOF
```

---

## ✅ TASK 5: Update Documentation

**Files to update:**

1. **ARCHITECTURE.md**
   - Add Phase 2 completion details
   - Show new module hierarchy
   - Document layer changes

2. **PHASE2_INSTRUCTIONS.md**
   - Add "✅ COMPLETE" at top
   - Reference PHASE2_INTEGRATION_REPORT.md

3. **Create PHASE3_COMPLETION_REPORT.md**
   - List all consolidations done
   - Document cleanup decisions
   - Record any technical debt deferred

**Action Items:**
- [ ] Update ARCHITECTURE.md with Phase 2 changes
- [ ] Mark PHASE2_INSTRUCTIONS.md as complete
- [ ] Create PHASE3_COMPLETION_REPORT.md
- [ ] Verify all code examples still work

**Success Criteria:**
- ✅ Documentation current
- ✅ No broken links
- ✅ Clear transition path to Phase 4

---

## ✅ TASK 6: Final Verification

**Run full test suite:**
```bash
pytest tests/integration/ -v
```

**Verify all modules:**
```python
from vibe_core.runtime.oracle import KernelOracle
from vibe_core.playbook import PlaybookEngine
from vibe_core.specialists import PlanningSpecialist
from vibe_core.store import ArtifactStore
from vibe_core.tools import ToolRegistry
from vibe_core.llm import ChainProvider
from vibe_core.governance import InvariantChecker
from vibe_core.agents import SimpleLLMAgent
from vibe_core.config import get_config
print("✅ All modules verified")
```

**Check Agent City:**
```python
from vibe_core.cartridges.system.herald.cartridge_main import HeraldCartridge
from vibe_core.cartridges.system.forum.cartridge_main import ForumCartridge
print("✅ Agent City intact")
```

**Action Items:**
- [ ] Run full integration test suite
- [ ] Verify all 9 modules import successfully
- [ ] Check HERALD & FORUM agents still work
- [ ] Record any warnings or errors

**Success Criteria:**
- ✅ All 22 tests still passing
- ✅ All modules working
- ✅ Agents operational
- ✅ Zero new errors

---

## 🚫 IMPORTANT: WHAT NOT TO DO

- ❌ **Do NOT remove aliases** (keep for 1 release cycle)
- ❌ **Do NOT refactor working code** (only document)
- ❌ **Do NOT add new features**
- ❌ **Do NOT modify test expectations** (unless fixing legitimate bugs)
- ❌ **Do NOT delete Agent City code**

---

## ✅ WHAT TO DO

- ✅ **Document all decisions** (in code comments)
- ✅ **Create consolidation reports** (what was done & why)
- ✅ **Update architecture docs** (reflect current state)
- ✅ **Keep all tests passing** (zero regressions)
- ✅ **Prepare clean handoff** (for Phase 4)

---

## 📊 SUCCESS CRITERIA (Phase 3 Complete)

When done, verify:

```bash
# All tests still pass
pytest tests/integration/ -v

# All modules load without errors
python -c "
from vibe_core.runtime.oracle import KernelOracle
from vibe_core.playbook import PlaybookEngine
from vibe_core.specialists import PlanningSpecialist
from vibe_core.store import ArtifactStore
from vibe_core.tools import ToolRegistry
from vibe_core.llm import ChainProvider
from vibe_core.governance import InvariantChecker
from vibe_core.agents import SimpleLLMAgent
from vibe_core.config import get_config
print('✅ All modules loaded')
"

# Agent City still works
python -c "
from vibe_core.cartridges.system.herald.cartridge_main import HeraldCartridge
from vibe_core.cartridges.system.forum.cartridge_main import ForumCartridge
h = HeraldCartridge()
f = ForumCartridge()
print(f'✅ {h.name} & {f.name} operational')
"
```

---

## 📝 COMMIT STRATEGY

**After Task 1:**
```bash
git add vibe_core/
git commit -m "docs: Audit and document Phase 2 aliases

Document temporary aliases created in Phase 2:
- PlaybookEngine (GraphExecutor)
- get_config (load_config)
- Specialist classes (PlanningSpecialist, CodingSpecialist, TestingSpecialist)
- AgentResponse (agent_protocol)

All aliases preserved for backward compatibility.
Deprecation timeline documented.
No breaking changes.
"
```

**After Task 3 (config):**
```bash
git add vibe_core/config/
git commit -m "docs: Consolidate configuration system

Document single source of truth for config:
- vibe_core/config/ is primary config loader
- Hierarchy: env vars > config files > defaults
- All config access through get_config() or load_config()
"
```

**Final commit:**
```bash
git commit -m "feat: Phoenix Protocol Phase 3 Complete - System Consolidation

Phase 3 cleanup and consolidation:
- Documented all Phase 2 temporary aliases
- Clarified store vs ledger separation (mutable vs immutable)
- Consolidated configuration system
- Optimized imports (zero circular dependencies)
- Updated architecture documentation
- All 22 integration tests still passing
- HERALD & FORUM agents verified operational

Technical Decisions:
- Aliases preserved for 1 release cycle (Phase 4: remove)
- Store (mutable) + Ledger (immutable) coexist by design
- Single config entry point established
- Import optimization complete

Status: Production Ready
Risk Level: LOW
Next Phase: Phase 4 (if needed)
"
```

---

## ⏱️ ESTIMATED TIME

- Task 1 (Alias audit): 2 hours
- Task 2 (Store consolidation): 2 hours
- Task 3 (Config consolidation): 2 hours
- Task 4 (Import optimization): 3 hours
- Task 5 (Documentation): 2 hours
- Task 6 (Final verification): 1 hour

**Total: ~2-3 days focused work**

---

## 🆘 IF YOU GET STUCK

**Circular import issues:**
- Use `python -m compileall vibe_core/` to check
- Restructure imports to avoid cycles
- Consider lazy loading in __init__.py

**Missing modules:**
- Check PHASE2_INTEGRATION_REPORT.md for module status
- All 9 modules should be present and working
- If missing, refer to PHASE2_INSTRUCTIONS.md

**Test failures:**
- Should be zero test failures from Phase 2
- If any appear, check if new code introduced regression
- Run tests in isolation: `pytest tests/integration/test_system_boot.py::TestKernelBoot`

**Documentation confusion:**
- ARCHITECTURE.md describes the 4-layer system
- PHASE2_INSTRUCTIONS.md details what was ported
- This file (PHASE3_INSTRUCTIONS.md) is for cleanup
- PHASE2_INTEGRATION_REPORT.md has verification results

---

## 🎯 DEFINITION OF DONE

Phase 3 is complete when:

1. ✅ All Phase 2 aliases documented (with deprecation path)
2. ✅ Store vs Ledger consolidation documented
3. ✅ Config system consolidated (single entry point)
4. ✅ Zero circular imports detected
5. ✅ All 22 tests still passing
6. ✅ HERALD & FORUM agents verified operational
7. ✅ Architecture documentation updated
8. ✅ Phase 3 completion report created
9. ✅ All code committed and pushed
10. ✅ Ready for Phase 4 (or production deployment)

---

## 🚀 NEXT STEPS (Phase 4)

After Phase 3 is complete:
- Remove aliases (breaking change, requires version bump)
- Expand specialist classes with real implementations
- Add advanced features (if needed)
- Performance optimization
- Production hardening

---

**EXECUTE. Phase 3 is your mission.** 🔥

Good luck, Agent!

---

**Document Version:** 1.0
**Last Updated:** 2025-11-27
**Status:** Ready for Phase 3
