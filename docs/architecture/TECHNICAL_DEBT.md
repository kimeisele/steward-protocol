# TECHNICAL DEBT & INTEGRATION TRACKER

> **Created:** 2025-12-05
> **Last Updated:** 2025-12-05
> **Status:** ACTIVE - 63 commits in last 24 hours

## Executive Summary

The last 24 hours saw massive architectural changes:
- Phoenix Config V2 (fractal sections)
- STEWARD Protocol Meta-Layer (vibe_core/steward/)
- Ephemeral Cities (4D Hypercube)
- Pre-commit hooks
- Agent consolidation (eliminate treibsand)

**Current System Status:**
- ✅ `boot.py`: 26 agents, 26 healthy
- ✅ Integration tests: 147 passed, 1 skipped
- ⚠️ Herald agent: Broken (config access issue)
- ⚠️ 20 files still use legacy imports

---

## CRITICAL: Half-Finished Work

### 1. STEWARD Protocol Migration (Phase 1-2 DONE, Phase 3-4 TODO)

**Completed:**
- [x] Phase 1: Created `vibe_core/steward/` with protocol, loader, constitution
- [x] Phase 2: Fixed discoverer naming (steward → discoverer), cleaned orphan dir

**Incomplete:**
- [ ] **Phase 3: Migrate 20 files** still importing from old locations
- [ ] **Phase 4: Delete legacy files** in `steward/` root

**Files with legacy imports (`from steward.constitutional_oath` or `from steward.oath_mixin`):**
```
steward/oath_mixin.py                              # Self-import - KEEP for now
docs/GENESIS_OATH_SUMMARY.md                       # Documentation only
docs/OATH_ROLLOUT_GUIDE.md                         # Documentation only
docs/archive/migrations/BLOCKER_2_ANALYSIS.md      # Archive
docs/guides/GOVERNANCE_GAPS.md                     # Documentation only
docs/reports/migrations/GOLDEN_THREAD_STATUS.md    # Report
migration/tryexcept_catalog.txt                    # Catalog
scripts/verify_database_isolation.py               # Verification script
scripts/verify_monkey_patching.py                  # Verification script
scripts/verify_process_isolation.py                # Verification script
scripts/verify_resource_limits.py                  # Verification script
starter-packs/nexus/cartridge_main.py              # NEEDS UPDATE
starter-packs/scope/cartridge_main.py              # NEEDS UPDATE
starter-packs/shield/cartridge_main.py             # NEEDS UPDATE
starter-packs/spark/cartridge_main.py              # NEEDS UPDATE
steward/system_agents/civic/tools/license_tool.py  # NEEDS UPDATE
steward/system_agents/engineer/templates/agent/cartridge_main.py  # Template - NEEDS UPDATE
vibe_core/bridge.py                                # NEEDS UPDATE
vibe_core/semantic_syscalls.py                     # NEEDS UPDATE
agent_city/registry/citizens/echo/cartridge_main.py  # NEEDS UPDATE
```

**Action Required:** Update 10 files to use `from vibe_core.steward import ...`

---

### 2. Herald Agent Broken

**Error:**
```
[STEWARD.LOADER] Cartridge init error for HeraldCartridge:
'CityConfig' object has no attribute 'posting_frequency_hours'
[DISCOVERER]   Skipping herald: Cartridge returned None
```

**Root Cause:**
- `HeraldCartridge.__init__` expects `config.posting_frequency_hours`
- But `CityConfig` has `config.agents.herald.posting_frequency_hours`
- Config path mismatch

**File:** `steward/system_agents/herald/cartridge_main.py:120`

**Fix Required:**
```python
# Line 120: Change
self.config.posting_frequency_hours
# To:
self.config.agents.herald.posting_frequency_hours if hasattr(self.config, 'agents') else self.config.posting_frequency_hours
```

---

### 3. Legacy Files in steward/ Root

**Files that should be in vibe_core/steward/ but still exist in steward/:**
- `steward/constitutional_oath.py` - Duplicates vibe_core/steward/constitution.py
- `steward/oath_mixin.py` - Duplicates vibe_core/steward/oath_mixin.py

**Migration Status:**
- New canonical locations created ✅
- Old files NOT deleted (breaking imports) ❌
- No deprecation warnings added ❌

**Action Required:**
1. Add deprecation warnings to old files
2. Update all imports
3. Delete old files

---

### 4. Treibsand (Quicksand) - Duplicate Class Definitions

**Problem:** Multiple files defined the same classes, causing `isinstance()` failures.

**Resolved (2025-12-04):**
- `vibe_core/protocols/agent.py` is now CANONICAL for:
  - `AgentManifest`
  - `VibeAgent`
  - `AgentResponse`
  - `Capability`
- `vibe_core/agent_protocol.py` now re-exports from canonical location
- `vibe_core/steward/protocol.py` re-exports AgentManifest

**Verification:**
```bash
grep -r "class AgentManifest" vibe_core/
# Should only return: vibe_core/protocols/agent.py
```

---

## Features Added (Last 24h) - Integration Status

| Feature | Commit | Status | Verified? |
|---------|--------|--------|-----------|
| Phoenix Config V2 | b88f202 | ✅ Complete | Yes - 147 tests pass |
| Ephemeral Cities (4D Hypercube) | db9cc9f | ✅ Complete | Partial - basic spawn works |
| Pre-commit hooks | 838b98c | ✅ Complete | Yes - runs on commit |
| EphemeralCityPlugin | de68fc1 | ✅ Complete | Partial - needs CLI integration |
| Airlock pattern | da5ff05 | ⚠️ Partial | No - artifact harvesting untested |
| STEWARD Protocol | 39b9838-d87c976 | ⚠️ Phase 2/4 | Partial - discoverer works |
| QualityConfig | 09691dd | ✅ Complete | Yes - ruff/pytest configs used |
| Test profiles | c9521de | ✅ Complete | Yes - --profile flag works |
| Fractal section auto-discovery | 22f9f69 | ✅ Complete | Yes - sections load |
| Boot.py error fixes | d088a70, 518edde | ✅ Complete | Yes - boot runs clean |

---

## Separation of Concerns Issues

### 1. Config Access Patterns (Inconsistent)

**Problem:** Agents access config in different ways:
```python
# Some agents expect flat config:
self.config.posting_frequency_hours

# Some expect nested Phoenix config:
self.config.city.herald.posting_frequency_hours

# Some expect agents subsection:
self.config.agents.herald.posting_frequency_hours
```

**Fix:** Standardize on `PhoenixConfig` with typed sections. Agents should receive their specific config slice:
```python
# In AgentLoader, when loading herald:
herald_config = phoenix_config.city.agents.herald
cartridge = HeraldCartridge(config=herald_config)
```

### 2. OathMixin vs ConstitutionalOath

**Two patterns coexist:**
1. `OathMixin` - Mixin class for agents
2. `ConstitutionalOath` - Static utility class

**Where they live:**
- OLD: `steward/oath_mixin.py`, `steward/constitutional_oath.py`
- NEW: `vibe_core/steward/oath_mixin.py`, `vibe_core/steward/constitution.py`

**Fix:** Consolidate into single pattern, delete legacy locations.

### 3. VibeAgent Base Class Sprawl

**Multiple base classes for agents:**
- `VibeAgent` (vibe_core/protocols/agent.py) - ABC interface
- `ContextAwareAgent` (vibe_core/agent_interface.py) - Adds context
- `ManagedAgent` (?) - Process management
- `GenericAgent` (steward/system_agents/discoverer/agent.py) - Manifest-only

**Fix:** Document inheritance hierarchy clearly. VibeAgent is base ABC.

---

## Verification Checklist

### Core System
- [x] `boot.py` starts without errors
- [x] 26 agents registered
- [x] 147 integration tests pass
- [ ] Herald agent loads successfully
- [ ] All agents can process basic tasks

### STEWARD Protocol
- [x] `vibe_core/steward/` exists with core modules
- [x] `AgentLoader.discover_and_load()` finds 27 agents
- [x] Discoverer uses AgentLoader (not hardcoded)
- [ ] All agents use `vibe_core.steward` imports
- [ ] Legacy files deleted

### Phoenix Config
- [x] Sections auto-discovered
- [x] `PhoenixConfig.load()` works
- [x] `CityConfig` has all subsections
- [ ] All agents receive correct config slice

### Governance
- [x] ConstitutionalOath computes hash
- [x] Agents can swear oath
- [ ] Oath verification works end-to-end

### Ephemeral Cities
- [x] `spawn_city` command exists
- [x] Basic kernel spawning works
- [ ] Airlock harvesting tested
- [ ] Plugin integration complete

---

## Priority Order for Fixes

1. **P0 - Herald Agent** (broken, affects system health)
   - Fix config access pattern
   - 1 file change

2. **P1 - Legacy Import Migration** (technical debt)
   - Update 10 files to use vibe_core.steward
   - Add deprecation warnings to old files

3. **P2 - Delete Legacy Files** (cleanup)
   - Remove steward/constitutional_oath.py
   - Remove steward/oath_mixin.py
   - After all imports updated

4. **P3 - Config Standardization** (architecture)
   - Document expected config shapes per agent
   - Update AgentLoader to pass correct slices

5. **P4 - Full Integration Tests** (confidence)
   - Add tests for agent task processing
   - Add tests for governance flow
   - Add tests for ephemeral city lifecycle

---

## Architecture Debt Summary

| Category | Count | Effort |
|----------|-------|--------|
| Broken agents | 1 | Low |
| Legacy imports | 10 | Medium |
| Duplicate files | 2 | Low |
| Missing tests | ~10 | High |
| Config inconsistencies | ~5 agents | Medium |

**Total Estimated Cleanup:** 2-3 focused sessions

---

## Notes

- STEWARD_PROTOCOL.md is still marked DRAFT - finalize after Phase 4
- Consider renaming `steward/` directory to `agents/` or `citizens/` (breaking change)
- manifest.schema.json exists but schema validation not enforced yet
