# 🔧 PHASE 4: STRUCTURAL REFACTORING - THE REAL PLAN

**Status:** 🔴 NOT YET STARTED
**Priority:** 🚨 CRITICAL - Blocks all agent development
**Scope:** Fix fundamental architecture problems before ANY production deployment
**Timeline:** 1-2 weeks of focused work
**Risk if not done:** System will collapse during agent integration

---

## SITUATION ANALYSIS

**The Real Problem:**
- Tests pass but code is in **Compatibility Mode**
- Phase 2 was **Copy-Paste Merge**, not Integration
- **PHOENIX CONFIG PORTED BUT NOT INTEGRATED** ← THE ROOT CAUSE
- Agents never receive loaded config, run blind with legacy patterns
- 79 files have Circular Import Workarounds (band-aids)
- 11 Ledger classes exist (no single source of truth)
- Agents initialized with **MockAgent** (never wired up)
- Two Playbook systems run in parallel (unintegrated)
- Phase 2 aliases still in production code
- Specialists are empty stubs

**Why This Must Be Fixed Now:**
1. ❌ **Phoenix Config loaded at startup, then DROPPED - never reaches agents** (ROOT CAUSE)
2. ❌ Agents run with hardcoded defaults + legacy patterns instead of unified config
3. ❌ Can't add real agent features while MockAgent defaults exist
4. ❌ Can't consolidate systems while circular imports are band-aided
5. ❌ Can't debug when 79 files hide import problems
6. ❌ Can't scale when 11 Ledger variants exist
7. ❌ Can't proceed to Production (none exists) with this foundation

**Commitment:** This is NOT another documentation phase. This is REAL CODE CHANGES.

---

## CRITICAL PATH: TOP 4 BLOCKERS (PRIORITY ORDER)

### BLOCKER #0: Phoenix Config Integration (THE ROOT CAUSE) ⭐ START HERE
**Current State:**
- ✅ `vibe_core/config/schema.py` - Complete CityConfig with 15 model classes
- ✅ `vibe_core/config/loader.py` - ConfigLoader implementation
- ✅ `run_server.py` - Loads config at startup
- ❌ `BootOrchestrator.__init__()` - NO config parameter
- ❌ `Discoverer.discover_agents()` - NO config passed to agents
- ❌ All agents - Instantiated without config injection
- Result: **Config loaded once, then ABANDONED. Agents run blind.**

**Proof of Disconnection:**
```python
# run_server.py lines 92-93: Config loaded here
loader = ConfigLoader(self.config_path)
self.config = loader.load()

# run_server.py line 149: But NEVER passed here!
self.orchestrator.boot()  # ❌ NO config parameter!

# BootOrchestrator line 82-87: Kernel created without config
kernel = RealVibeKernel(ledger_path=...)  # ❌ NO config
discoverer = Discoverer(kernel=...)        # ❌ NO config
```

**Impact:**
- Herald reads from hardcoded paths, not CityConfig.agents.herald
- Forum (not implemented) would never read from CityConfig.agents.forum
- Civic reads from citizens.json, not CityConfig.agents.civic
- Each agent has legacy config patterns instead of unified approach
- Changing config/matrix.yaml does NOT affect agent behavior

**The Fix:**
1. **Create config parameter chain:**
   ```python
   # 1. StewardBootLoader passes config
   def boot_kernel(self):
       self.orchestrator = BootOrchestrator(config=self.config)

   # 2. BootOrchestrator stores and passes config
   def __init__(self, config: CityConfig):
       self.config = config
       self.discoverer = Discoverer(kernel=kernel, config=config)

   # 3. Discoverer passes config to agents
   def discover_agents(self):
       agent = self._load_agent_from_manifest(
           manifest_path, agent_id,
           config=self.config.agents.get(agent_id)  # ✅ Config injection
       )
   ```

2. **Update each agent to accept config:**
   ```python
   # Herald example
   class HeraldCartridge(VibeAgent):
       def __init__(self, agent_id: str, config: Optional[HeraldConfig] = None):
           self.config = config or HeraldConfig()  # Use passed or default
           self.posting_frequency = self.config.posting_frequency_hours
           self.content_style = self.config.content_style
   ```

3. **Remove legacy config patterns:**
   - Replace hardcoded paths with config.paths.data
   - Replace os.getenv() with config.integrations.twitter.bearer_token
   - Replace dict-based config with CityConfig access

4. **Add validation:**
   - Agents assert they received proper config
   - Tests verify agents use CityConfig values

**Time Estimate:** 2-3 hours (simpler than it looks - mostly parameter passing)
**Risk:** MEDIUM (config flow is clear, but touches boot sequence)
**Test Impact:** Tests will verify agents receive and use config
**PRIORITY:** 🔴 DO THIS FIRST - Everything else depends on this

---

### BLOCKER #1: The Ledger Mess (Foundation)
**Current State:**
- `vibe_core/kernel.py:46` - VibeLedger as ABC (interface)
- `vibe_core/ledger.py:26` - VibeLedger as concrete (shadows interface!)
- `steward/.../justice_ledger.py` - Domain-specific ledger
- `steward/.../ledger.py` (in archivist tools) - Agent-specific wrapper
- `steward/.../ledger_tool.py` (civic + archivist) - Tools using ledger
- Result: **11 Ledger variants, no inheritance chain**

**The Fix:**
1. Keep ONLY: `vibe_core/ledger.py` with `VibeLedger(ABC)` interface
   ```python
   class VibeLedger(ABC):
       """The ONE canonical ledger interface"""
       @abstractmethod
       def record_event(...): pass
       # ... all abstract methods ...
   ```

2. Implementations go in `vibe_core/ledger_impl.py`:
   ```python
   class InMemoryLedger(VibeLedger):
       """Testing: Volatile, fast"""

   class SQLiteLedger(VibeLedger):
       """Production: Persistent, hash-chained"""
   ```

3. Domain-specific ledgers inherit from canonical:
   ```python
   # steward/.../justice_ledger.py
   from vibe_core.ledger import VibeLedger
   class JusticeLedger(VibeLedger):
       """Domain-specific: adds vote tracking"""
   ```

4. Remove all other `VibeLedger` definitions (they're duplicates)

5. Update all imports to use canonical interface

**Time Estimate:** 3-4 hours
**Risk:** MEDIUM (many import paths change, but clear direction)
**Test Impact:** All ledger tests should pass after fix

---

### BLOCKER #2: Circular Imports (Architecture)
**Current State:**
- 79 files with try/except ImportError patterns
- Example: `vibe_core/agents/llm_agent.py` - "Import here to avoid circular dependency"
- This means: **Fundamental wiring is broken**

**Root Causes Found:**
1. `playbook/executor.py` imports `agents/llm_agent.py`
2. `agents/llm_agent.py` imports `playbook/runner.py`
3. Both try to import each other = circular
4. Workaround: Lazy imports (import inside functions)
5. Result: Fragile, hard to refactor

**The Fix:**
1. **Create Dependency Hierarchy:**
   ```
   Layer 1: Protocols (interfaces only)
   ├── agent_protocol.py (VibeAgent interface)
   ├── playbook_protocol.py (Playbook interface)
   └── ledger_protocol.py (Ledger interface)

   Layer 2: Implementations (no cross-imports)
   ├── agents/ (implements VibeAgent)
   ├── playbook/ (implements Playbook)
   └── store/ (implements persistence)

   Layer 3: Integration (only here can layers mix)
   ├── runtime/orchestrator.py (wires everything)
   └── kernel_impl.py (main kernel)
   ```

2. **Move all interfaces to `vibe_core/protocols/`:**
   - `protocols/agent.py` - VibeAgent ABC
   - `protocols/playbook.py` - Playbook ABC
   - `protocols/ledger.py` - Ledger ABC
   - `protocols/store.py` - Store ABC

3. **Update imports in Layer 2:**
   ```python
   # agents/llm_agent.py
   from vibe_core.protocols.agent import VibeAgent  # Only protocol import
   # NO imports of playbook, store, ledger

   # playbook/executor.py
   from vibe_core.protocols.playbook import Playbook
   # NO imports of agents, store, ledger
   ```

4. **Wiring happens ONLY in Layer 3:**
   ```python
   # runtime/orchestrator.py
   from vibe_core.agents.llm_agent import SimpleLLMAgent
   from vibe_core.playbook.executor import GraphExecutor
   from vibe_core.store.sqlite_store import SQLiteStore
   # All layer 2 modules imported here - NO circle possible
   ```

5. **Remove all try/except ImportError workarounds**

**Time Estimate:** 4-5 hours
**Risk:** HIGH (touching 79 files, but systematic)
**Test Impact:** Tests WILL break initially (good - they'll prove wiring works)

---

### BLOCKER #3: MockAgent Defaults (Agent Integration)
**Current State:**
- `vibe_core/playbook/executor.py:160` - `self.agent = MockAgent()` (default)
- `vibe_core/playbook/runner.py` - Doesn't actually call real agents
- `vibe_core/specialists/*` - Empty stubs with no logic
- Result: **Agent system is never exercised, just mocked**

**The Fix:**
1. **Remove MockAgent defaults:**
   ```python
   # BEFORE (broken):
   class GraphExecutor:
       def __init__(self):
           self.agent: AgentInterface = MockAgent()  # ❌ Default mock

   # AFTER (correct):
   class GraphExecutor:
       def __init__(self, agent: VibeAgent):
           self.agent = agent  # ✅ Required parameter
   ```

2. **Require real agents at instantiation:**
   ```python
   # executor = GraphExecutor()  # ❌ Will fail
   executor = GraphExecutor(
       agent=SimpleLLMAgent(...)  # ✅ Must provide real agent
   )
   ```

3. **Implement actual agent invocation:**
   ```python
   # Before: Runner just returns mock result
   # After: Runner actually calls agent.process(worklfow)
   result = await self.agent.process(
       task_type=node.task_type,
       input_data=node.input_data,
       context=execution_context
   )
   ```

4. **Implement Specialist classes with real logic:**
   ```python
   # BEFORE (empty stub):
   class PlanningSpecialist(BaseSpecialist):
       pass

   # AFTER (real implementation):
   class PlanningSpecialist(BaseSpecialist):
       """Actually creates plans, not just mocks"""

       async def process(self, task):
           # Real planning logic using LLM
           llm_result = await self.llm_client.complete(
               prompt=f"Create plan for: {task.description}"
           )
           return parse_plan(llm_result)
   ```

5. **Update all tests to use real agents (not mocks)**

**Time Estimate:** 3-4 hours
**Risk:** MEDIUM-HIGH (requires understanding agent protocol)
**Test Impact:** Tests will actually exercise real code paths

---

## EXECUTION PLAN: WEEK 1 (MONDAY-FRIDAY) + SUNDAY PREP

### Sunday (BEFORE Monday): Phoenix Config Integration Foundation
**Goal:** Wire config from load → boot orchestrator → agents
```bash
# 1. Update BootOrchestrator signature
# File: boot_orchestrator.py
# Change: __init__(self) → __init__(self, config: CityConfig)

# 2. Update Discoverer to accept config
# File: agent_city/discoverer.py
# Change: __init__(self, kernel) → __init__(self, kernel, config)

# 3. Update StewardBootLoader to pass config
# File: run_server.py line 149
# Change: self.orchestrator.boot() → self.orchestrator.boot(config=self.config)

# 4. Update each agent to accept config
# Files: herald/cartridge_main.py, civic/cartridge_main.py, etc.
# Change: def __init__(self) → def __init__(self, config=None)

# 5. Test that config flows through
pytest tests/test_config_integration.py -v

# 6. Commit
git commit -m "feat: Wire Phoenix Config through boot sequence - foundation for agent configuration"
```

**Time:** 2-3 hours
**Impact:** Config now REACHABLE by agents (fixes root cause)

### Monday: Ledger Architecture
**Goal:** One canonical Ledger interface + implementations
```bash
# 1. Create protocol layer
mv vibe_core/ledger.py vibe_core/ledger_impl.py
cat > vibe_core/ledger.py << 'EOF'
"""Canonical Ledger Interface"""
from abc import ABC, abstractmethod
# ... interface only, no implementation ...
EOF

# 2. Update kernel.py to import from ledger.py (not redefine)
# 3. Test all imports still work
pytest tests/test_ledger* -v

# 4. Update domain-specific ledgers to inherit from canonical
# 5. Commit
git add vibe_core/ledger*
git commit -m "refactor: Ledger architecture - one canonical interface"
```

### Tuesday: Dependency Layering
**Goal:** Create protocols/ layer, move all interfaces
```bash
# 1. Create protocols directory
mkdir -p vibe_core/protocols
touch vibe_core/protocols/{__init__,agent.py,playbook.py,ledger.py,store.py}

# 2. Extract interfaces from implementations
# agent_protocol.py → protocols/agent.py
# playbook protocols → protocols/playbook.py
# etc.

# 3. Update imports in Layer 2 (agents, playbook, store)
# No cross-layer imports

# 4. Test individual modules
pytest tests/test_agents* -v
pytest tests/test_playbook* -v
pytest tests/test_store* -v

# 5. Commit
git commit -m "refactor: Create protocols layer for clean dependency hierarchy"
```

### Wednesday: Remove Circular Workarounds
**Goal:** Delete all try/except ImportError patterns
```bash
# 1. Grep for workaround patterns
grep -r "except ImportError" vibe_core/ --include="*.py"
grep -r "import here to avoid" vibe_core/ --include="*.py"

# 2. Update each file to use only Layer 1 (protocols) imports
# 3. Move wiring logic to runtime/orchestrator.py
# 4. Test no circular imports
python -m py_compile vibe_core/**/*.py

# 5. Run full test suite (will be broken initially)
pytest tests/ -v

# 6. Fix wiring in orchestrator based on test failures
# 7. Commit
git commit -m "refactor: Remove circular import workarounds via protocol layer"
```

### Thursday: Agent Integration
**Goal:** Remove MockAgent defaults, implement real agent calling
```bash
# 1. Update GraphExecutor to require real agent
# 2. Update runner to actually call agent.process()
# 3. Implement PlanningSpecialist, CodingSpecialist, TestingSpecialist
# 4. Update tests to use real agents
pytest tests/test_agent_integration.py -v

# 5. Commit
git commit -m "feat: Wire real agent integration - remove MockAgent defaults"
```

### Friday: Verification & Cleanup
**Goal:** All tests pass, system actually works
```bash
# 1. Run full test suite
pytest tests/integration/ -v

# 2. Test agent-city CLI
bin/agent-city status
bin/agent-city task list

# 3. Verify no regressions
git diff HEAD~5..HEAD | wc -l  # Show scale of changes

# 4. Final commit
git commit -m "refactor: Phase 4 Complete - Fundamental Architecture Fixed

Breaking Changes:
- MockAgent removed (agents must be explicit)
- get_config/PlaybookEngine aliases removed (use canonical names)
- Specialist classes now have real implementations

New Structure:
- protocols/ layer for all interfaces
- Clean dependency hierarchy (no circular imports)
- Ledger consolidation (1 interface, 2 implementations)
- Agent integration wired (real agents, not mocks)

Testing: 22/22 integration tests passing + 100% real code paths"
```

---

## CONVERSION TABLE: Old → New Names

| Old (Phase 2) | New (Phase 4) | Location |
|---------------|---------------|----------|
| `PlaybookEngine` alias | `GraphExecutor` | `vibe_core/playbook/__init__.py` |
| `get_config` alias | `load_config` | `vibe_core/config/__init__.py` |
| `DeterministicExecutor` | Keep as-is | `steward/system_agents/envoy/` |
| `PlaybookRouter` | Keep as-is | `vibe_core/runtime/playbook_router.py` |
| `SimpleLLMAgent` | Rename to `DefaultAgent` | `vibe_core/agents/default_agent.py` |
| 11 Ledger classes | 1 interface + 2 impls | `vibe_core/ledger{,_impl}.py` |
| Specialist stubs | Real implementations | `vibe_core/specialists/{planning,coding,testing}.py` |

---

## RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Circular imports still exist after | Medium | HIGH | Automated detection, new tests |
| Tests break during refactor | High | MEDIUM | Systematic approach, one layer at time |
| Performance degrades | Low | MEDIUM | Profiling after refactor |
| Agent integration incomplete | Medium | HIGH | Clear acceptance criteria per blocker |
| Merge conflicts (git) | Medium | LOW | Small commits, frequent pushes |

---

## SUCCESS CRITERIA

When Phase 4 is done:

✅ **Ledger:**
- One canonical `VibeLedger` ABC
- Two implementations: `InMemoryLedger`, `SQLiteLedger`
- All domain-specific ledgers inherit from canonical
- Zero `VibeLedger` redefinitions

✅ **Circular Imports:**
- Zero try/except ImportError patterns
- 79 workarounds removed
- Clean dependency graph: Layer 1 → Layer 2 → Layer 3
- `python -m py_compile` passes on all files

✅ **Agent Integration:**
- No MockAgent defaults anywhere
- All agent calls go to real `SimpleLLMAgent` (or subclass)
- Specialist classes have real implementation
- Tests exercise real code paths

✅ **Consolidation:**
- Config system: Single schema in `vibe_core/config/schema.py`
- Aliases removed (Phase 2 compat not needed)
- Store vs Ledger properly separated (no confusion)

✅ **Testing:**
- 22/22 integration tests passing
- 0 new warnings in import checks
- Agent City commands work end-to-end
- Full system boots without mocks

---

## DEFINITION OF "GEWISSENHAFT" (CONSCIENTIOUS)

✅ Code reviews every change (not just PRs)
✅ Tests MUST pass before commit
✅ Clear commit messages explaining WHY
✅ No breaking changes without clear migration path
✅ Architecture decisions documented
✅ No quick fixes that create tech debt
✅ Each phase builds on previous cleanly
✅ Agent integration tested end-to-end
✅ Performance verified (not degraded)
✅ Prepared for actual deployment (even though none exists yet)

---

## DECISION POINT

**This plan requires:**
1. ✅ Clear go/no-go decision (yes, we do this)
2. ✅ Time commitment (1-2 weeks, ~40-50 hours focused work)
3. ✅ Discipline (no shortcuts, no "we'll fix it later")
4. ✅ Tests as truth (if tests pass, architecture is correct)

**If approved:**
- Start Monday on Ledger (Blocker #1)
- Each blocker depends on previous (sequential, not parallel)
- Daily commits, visible progress
- No "almost done" states - fully done or broken

**If not approved:**
- Document why (constraints, other priorities)
- Accept that production deployment will be harder
- Plan for Phase 4.5 when time opens up

---

**Status:** Ready for execution
**Author:** Claude Code (Haiku 4.5)
**Date:** 2025-11-27
**Confidence Level:** 95% - This will fix the fundamental problems
