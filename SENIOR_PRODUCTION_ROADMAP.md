# SENIOR PRODUCTION ROADMAP
## Vimana-Class: Range Rover Robustness Level

**Created:** 2025-11-27
**Status:** CURRENT SYSTEM STATE ASSESSMENT + PRODUCTION PATH
**Quality Standard:** Range Rover (No half-measures, production-ready, resilient)
**Branch:** `claude/senior-production-roadmap-01BGAeaVRpPYYEMAQmcjQecc`

---

## 🚨 CRITICAL: CURRENT STATE ASSESSMENT

### System Health: 🔴 CRITICAL - NON-FUNCTIONAL

```
Status Metrics:
├── Server Startup:        ❌ BROKEN (ImportError in config/schema.py)
├── Protocol Layer:        ❌ BROKEN (Task not exported)
├── Tests:                 ❌ BROKEN (SystemExit in test suite)
├── try/except Patterns:   ❌ 57 REMAINING (not 0!)
├── Phoenix Engine:        ❌ DOES NOT EXIST
├── System Agents:         ⚠️  13 cartridges exist but not wired
├── Documentation:         ⚠️  Incomplete
└── Production Readiness:  ❌ 0% - CANNOT RUN
```

### BLOCKER Status Reality Check

| Blocker | Claimed | Actual | Reality |
|---------|---------|--------|---------|
| **BLOCKER #0** | ✅ Done | ⚠️ Fragile | Config distribution works BUT depends on broken system |
| **BLOCKER #1** | ✅ Done | ⚠️ Fragile | Ledger hierarchy clean BUT can't import |
| **BLOCKER #2** | ✅ Done | 🔴 **INCOMPLETE** | Layer 1 broken, Layer 2 partial, Layer 3 missing |
| **BLOCKER #3** | Not started | 🔴 **BLOCKED** | Cannot proceed - system doesn't run |

### The Brutal Truth

**What was accomplished:**
- ✅ vibe_core/protocols/ directory created
- ✅ Some protocol files written (agent.py, ledger.py, etc.)
- ✅ Intent was good

**What is broken:**
- ❌ protocols/__init__.py imports non-existent `Task`
- ❌ Server cannot start (ImportError cascade)
- ❌ Tests cannot run (missing imports + SystemExit)
- ❌ 57 try/except ImportError remain (not removed!)
- ❌ No Phoenix engine
- ❌ No phoenix.yaml
- ❌ No Layer 3 wiring
- ❌ System agents not wired
- ❌ Cannot demonstrate ANY functionality

**Risk Assessment:**
- 🔴 **CRITICAL:** System completely non-functional
- 🔴 **HIGH:** Cannot validate ANY previous work (BLOCKER #0, #1)
- 🟡 **MEDIUM:** Technical debt accumulating
- 🟢 **LOW:** Code structure exists (foundation present)

---

## 🎯 WHAT "RANGE ROVER ROBUSTNESS" MEANS

Before we proceed, let's define the quality standard:

### Range Rover Quality Pillars

1. **RELIABILITY** - System starts every time, no exceptions
2. **RESILIENCE** - Graceful degradation, never catastrophic failure
3. **TESTABILITY** - Comprehensive test coverage, automated validation
4. **MAINTAINABILITY** - Clean code, clear architecture, documented
5. **OBSERVABILITY** - Logging, metrics, tracing, debuggability
6. **DEPLOYABILITY** - CI/CD ready, containerized, configurable
7. **SECURITY** - Input validation, error handling, no secrets leakage
8. **PERFORMANCE** - Optimized, profiled, benchmarked

### What This Means in Practice

- ✅ **Zero tolerance for broken imports**
- ✅ **All tests pass before merge**
- ✅ **Comprehensive error handling (no bare except)**
- ✅ **Structured logging throughout**
- ✅ **Configuration validation (fail-fast on bad config)**
- ✅ **Graceful shutdown**
- ✅ **Health checks & readiness probes**
- ✅ **Metrics & observability**
- ✅ **Documentation at all levels**
- ✅ **Version compatibility strategy**

---

## 📋 PRODUCTION ROADMAP: 5 PHASES

This is NOT a quick fix. This is a COMPLETE productionization effort.

### Overview

```
Phase 0: Critical Fixes        (4-6h)  🔥 URGENT
Phase 1: Foundation Hardening  (6-8h)  🏗️ CORE
Phase 2: Wiring & Integration  (8-10h) 🔌 CONNECT
Phase 3: Quality & Testing     (6-8h)  ✅ VALIDATE
Phase 4: Production Readiness  (4-6h)  🚀 DEPLOY

TOTAL: 28-38 hours (realistic: 35 hours)
```

This is the HONEST timeline for production-grade work.

---

## 🔥 PHASE 0: CRITICAL FIXES (4-6h)

**Goal:** Get system to a RUNNABLE state
**Success Criteria:** Server starts, basic tests pass

### Task 0.1: Fix Protocol Layer Imports (CRITICAL)
**Priority:** P0 - BLOCKER
**Estimated:** 30min

**Problem:**
```python
# vibe_core/protocols/__init__.py tries to import:
from .agent import VibeAgent, AgentManifest, Task  # Task doesn't exist!
```

**Actions:**
1. Read vibe_core/protocols/agent.py completely
2. Identify what `Task` should be (check imports in test files)
3. Options:
   - a) Task exists elsewhere → add to agent.py
   - b) Task is AgentTask → fix export name
   - c) Task shouldn't be exported → remove from __init__.py
4. Fix import
5. Validate: `python -c "from vibe_core.protocols import *"`

**Validation:**
```bash
python -c "from vibe_core.protocols import VibeAgent, AgentManifest, Task; print('✅ OK')"
# Expected: ✅ OK
```

---

### Task 0.2: Fix Config Schema Import Chain
**Priority:** P0 - BLOCKER
**Estimated:** 1h

**Problem:**
```
Traceback in run_server.py → boot_orchestrator.py → config/schema.py
Server cannot start due to import cascade failure
```

**Actions:**
1. Trace import chain:
   ```bash
   python -c "from vibe_core.config import CityConfig" 2>&1 | tee import_trace.txt
   ```
2. Identify exact failure point
3. Check circular dependencies
4. Fix imports (use protocols if needed)
5. Validate config loads

**Validation:**
```bash
python -c "from vibe_core.config import CityConfig, load_config; print('✅ Config OK')"
python run_server.py --help  # Should not crash
```

---

### Task 0.3: Fix Test Suite Imports
**Priority:** P0 - BLOCKER
**Estimated:** 1-2h

**Problem:**
```python
# tests/test_cartridge_vibeagent_compatibility.py
from civic.cartridge_main import CivicCartridge  # Wrong path? Missing?
sys.exit(1)  # Exits entire test run!
```

**Actions:**
1. Audit test file:
   ```bash
   find tests/ -name "*.py" -exec python -m py_compile {} \; 2>&1 | tee test_syntax.log
   ```
2. Fix imports in test files:
   - Correct paths (steward.system_agents.civic vs civic)
   - Add missing __init__.py if needed
   - Use protocols for type checking
3. Remove sys.exit(1) - use pytest.skip() or pytest.fail()
4. Run test collection:
   ```bash
   pytest tests/ --collect-only
   ```

**Validation:**
```bash
pytest tests/ --collect-only  # Should collect all tests, no errors
```

---

### Task 0.4: Basic Smoke Test - Server Startup
**Priority:** P0 - VALIDATION
**Estimated:** 30min

**Actions:**
1. Create minimal config for testing:
   ```yaml
   # config/test_minimal.yaml
   governance:
     voting_threshold: 0.5

   system_agents: []  # Empty for now
   ```

2. Attempt server startup:
   ```bash
   python run_server.py --config config/test_minimal.yaml --dry-run
   ```

3. Fix any remaining import errors
4. Validate server reaches "listening" state

**Validation:**
```bash
timeout 5 python run_server.py --config config/test_minimal.yaml 2>&1 | grep -i "listening\\|ready\\|started"
# Expected: Some success message before timeout
```

---

### Task 0.5: Document Critical Fixes
**Priority:** P1
**Estimated:** 30min

**Actions:**
1. Create `PHASE0_CRITICAL_FIXES.md`:
   - What was broken
   - What was fixed
   - How to verify
   - What remains

**Validation:**
- [ ] Document exists
- [ ] Lists all fixes
- [ ] Includes validation commands

---

### Phase 0 Exit Criteria

**MUST be true before Phase 1:**
- [ ] `from vibe_core.protocols import *` works
- [ ] `from vibe_core.config import CityConfig` works
- [ ] `pytest tests/ --collect-only` succeeds
- [ ] `python run_server.py --help` succeeds (no crash)
- [ ] Basic server starts with minimal config
- [ ] Git commit: "fix: Phase 0 - Critical system fixes"

**If ANY criterion fails, DO NOT proceed to Phase 1.**

---

## 🏗️ PHASE 1: FOUNDATION HARDENING (6-8h)

**Goal:** Complete Layer 1 & Layer 2 properly
**Success Criteria:** Zero try/except ImportError, clean architecture

### Task 1.1: Complete Protocol Layer (Layer 1)
**Priority:** P0
**Estimated:** 2-3h

**Actions:**
1. Audit ALL protocols needed:
   ```bash
   grep -r "from abc import ABC" vibe_core/ steward/ --include="*.py" > abc_inventory.txt
   ```

2. For each ABC, ensure it's in vibe_core/protocols/:
   - VibeAgent ✅
   - VibeLedger ✅
   - VibeStore ⚠️ (verify)
   - Playbook ⚠️ (verify)
   - VibeScheduler ⚠️ (verify)
   - ManifestRegistry ⚠️ (verify)
   - OathProtocol ❌ (need to create if missing)
   - Task/AgentTask ❌ (from 0.1)
   - Any others found in audit

3. Validate EACH protocol file:
   - Only ABC definitions
   - No implementations
   - No imports from Layer 2
   - Proper docstrings
   - Type hints complete

4. Update protocols/__init__.py:
   ```python
   # Export ALL protocols
   __all__ = [...]  # Complete list
   ```

**Validation:**
```bash
# Test each protocol independently
for proto in VibeAgent VibeLedger VibeStore Playbook VibeScheduler ManifestRegistry; do
  python -c "from vibe_core.protocols import $proto; print('✅ $proto')" || echo "❌ $proto FAILED"
done

# Verify no Layer 2/3 imports
grep -r "from vibe_core\\.(?!protocols)" vibe_core/protocols/ --include="*.py" && echo "❌ Invalid imports" || echo "✅ Clean"
```

---

### Task 1.2: Systematic try/except Removal (Layer 2)
**Priority:** P0
**Estimated:** 3-4h

**Problem:** 57 try/except ImportError patterns remain

**Strategy: Categorize → Fix → Validate**

**Step 1: Categorize (30min)**
```bash
grep -r "except ImportError" vibe_core/ steward/ provider/ --include="*.py" -B 3 -A 1 > tryexcept_full.txt
```

Categorize into:
1. **Protocol imports** (should use `from vibe_core.protocols import X`)
2. **Optional dependencies** (anthropic, google libs - keep these!)
3. **Circular dependency hacks** (MUST FIX)
4. **Lazy imports** (refactor to top-level)

**Step 2: Fix Protocol Imports (1h)**

For each protocol import:
```python
# BEFORE:
try:
    from steward.agent import VibeAgent
except ImportError:
    VibeAgent = None

# AFTER:
from vibe_core.protocols import VibeAgent
```

**Step 3: Fix Circular Dependencies (1-2h)**

Pattern:
```python
# BEFORE (circular):
try:
    from vibe_core.kernel import VibeLedger
except ImportError:
    pass

# AFTER (use protocol):
from vibe_core.protocols import VibeLedger
```

**Step 4: Keep Valid Optional Dependencies**

These are OKAY to keep:
```python
try:
    import anthropic
except ImportError:
    anthropic = None  # Optional dependency, OK!
```

**Step 5: Refactor Lazy Imports**

```python
# BEFORE (lazy):
def some_function():
    try:
        from vibe_core.foo import Bar
    except ImportError:
        Bar = None

# AFTER (top-level):
from vibe_core.foo import Bar  # Or use protocol!
```

**Tracking:**
Create `migration/tryexcept_removal_phase1.log`:
```
[1/57] vibe_core/runtime/providers/google.py:42 - KEEP (optional dep: google.generativeai)
[2/57] vibe_core/kernel_impl.py:15 - FIXED (protocol import)
[3/57] vibe_core/playbook/executor.py:23 - FIXED (refactored to Layer 3)
...
```

**Validation:**
```bash
# Count remaining
grep -r "except ImportError" vibe_core/ steward/ provider/ --include="*.py" | wc -l
# Target: <10 (only optional external deps)

# All protocol imports work
python -c "
from vibe_core.protocols import *
print('✅ All protocols OK')
"

# Run syntax check on all modified files
find vibe_core/ steward/ -name '*.py' -exec python -m py_compile {} \; 2>&1 | tee syntax_check.log
```

---

### Task 1.3: Fix All System Agent Imports
**Priority:** P0
**Estimated:** 1-2h

**Actions:**
1. Audit all 13 system agent cartridge_main.py files:
   ```bash
   find steward/system_agents -name "cartridge_main.py" | while read f; do
     echo "=== $f ===" >> agent_imports.txt
     grep "^import\\|^from" "$f" >> agent_imports.txt
   done
   ```

2. Ensure all agents import from protocols:
   ```python
   # In each cartridge_main.py
   from vibe_core.protocols import VibeAgent, AgentManifest

   class MyCartridge(VibeAgent):
       ...
   ```

3. Fix broken imports in tools/ subdirectories

4. Validate each agent can be imported:
   ```bash
   for agent in civic herald forum science auditor supreme_court oracle envoy watchman engineer discovery scribe archivist; do
     python -c "from steward.system_agents.$agent.cartridge_main import *; print('✅ $agent')" || echo "❌ $agent FAILED"
   done
   ```

**Validation:**
- [ ] All 13 agents import successfully
- [ ] All agents inherit from VibeAgent (protocol)
- [ ] No circular import errors

---

### Task 1.4: Runtime Module Cleanup
**Priority:** P1
**Estimated:** 1h

**Actions:**
1. Audit vibe_core/runtime/ imports
2. Fix any try/except ImportError
3. Ensure clean imports
4. Add proper error handling (not bare except)

**Validation:**
```bash
python -c "from vibe_core.runtime import *; print('✅ Runtime OK')"
```

---

### Phase 1 Exit Criteria

**MUST be true before Phase 2:**
- [ ] All protocols in vibe_core/protocols/ complete
- [ ] protocols/__init__.py exports all protocols
- [ ] try/except ImportError count < 10 (only external deps)
- [ ] All 13 system agents import successfully
- [ ] All agents inherit from VibeAgent protocol
- [ ] Zero circular import errors
- [ ] Syntax check passes on all .py files
- [ ] Git commit: "feat: Phase 1 - Foundation hardening complete"

---

## 🔌 PHASE 2: WIRING & INTEGRATION (8-10h)

**Goal:** Implement Layer 3 (Phoenix), wire all agents
**Success Criteria:** Dynamic agent loading works

### Task 2.1: Design Phoenix Architecture
**Priority:** P0
**Estimated:** 1h

**Actions:**
1. Create design document: `docs/PHOENIX_ARCHITECTURE.md`

2. Define Phoenix responsibilities:
   - Load configuration (phoenix.yaml)
   - Import agents dynamically
   - Wire dependencies
   - Enforce import order
   - Provide agent registry
   - Health checks

3. Define interface:
   ```python
   class PhoenixConfigEngine:
       def __init__(self, config_path: str)
       def enforce_import_order() -> None
       def wire_agents() -> Dict[str, Type[VibeAgent]]
       def wire_kernel() -> Dict[str, Any]
       def get_agent(agent_id: str) -> Type[VibeAgent]
       def health_check() -> Dict[str, Any]
   ```

**Validation:**
- [ ] Architecture document complete
- [ ] Interface defined
- [ ] Reviewed for completeness

---

### Task 2.2: Create phoenix.yaml Schema
**Priority:** P0
**Estimated:** 2h

**Actions:**
1. Define complete schema:
   ```yaml
   # config/phoenix.yaml

   version: "1.0"

   # Import order (Layer 1 → Layer 2 → Layer 3)
   imports:
     order:
       - vibe_core.protocols
       - vibe_core.kernel
       - vibe_core.ledger
       - vibe_core.runtime
       - steward.system_agents

   # System components
   system:
     kernel:
       class: "vibe_core.kernel_impl:VibeKernel"
     ledger:
       class: "vibe_core.ledger:VibeCoreLedger"
     store:
       class: "vibe_core.store:DefaultStore"

   # System agents (all 13)
   agents:
     system_agents:
       - id: "civic_cartridge"
         name: "Civic Licensing Agent"
         class: "steward.system_agents.civic.cartridge_main:CivicCartridge"
         enabled: true

       - id: "herald_cartridge"
         name: "Herald Broadcasting Agent"
         class: "steward.system_agents.herald.cartridge_main:HeraldCartridge"
         enabled: true

       # ... all 13 agents

   # Playbook configuration
   playbook:
     executor_agent: "steward.system_agents.envoy.cartridge_main:EnvoyCartridge"
     fallback_agent: null  # No mock fallback!

   # Provider configuration
   providers:
     llm:
       default: "anthropic"
       anthropic:
         model: "claude-sonnet-4"
       google:
         model: "gemini-2.0-flash-exp"
   ```

2. Create schema validation with Pydantic:
   ```python
   # vibe_core/phoenix_schema.py
   from pydantic import BaseModel

   class PhoenixConfig(BaseModel):
       version: str
       imports: ImportConfig
       system: SystemConfig
       agents: AgentsConfig
       playbook: PlaybookConfig
       providers: ProvidersConfig
   ```

**Validation:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/phoenix.yaml'))"

# Validate with Pydantic
python -c "from vibe_core.phoenix_schema import PhoenixConfig; import yaml; PhoenixConfig(**yaml.safe_load(open('config/phoenix.yaml')))"
```

---

### Task 2.3: Implement PhoenixConfigEngine
**Priority:** P0
**Estimated:** 3-4h

**Actions:**
1. Create `vibe_core/phoenix_config.py` (300-400 lines)

2. Implementation structure:
   ```python
   """Layer 3: Phoenix Dynamic Configuration Engine"""

   import importlib
   import logging
   from pathlib import Path
   from typing import Any, Dict, List, Type
   import yaml

   from vibe_core.protocols import VibeAgent, VibeLedger
   from vibe_core.phoenix_schema import PhoenixConfig

   logger = logging.getLogger(__name__)

   class PhoenixConfigEngine:
       """
       Dynamic agent and component wiring engine.

       Responsibilities:
       - Load and validate phoenix.yaml
       - Enforce import order to prevent circular deps
       - Dynamically load agent classes
       - Provide agent registry
       - Health checks
       """

       def __init__(self, config_path: str = "config/phoenix.yaml"):
           self.config_path = Path(config_path)
           self.config: PhoenixConfig = self._load_and_validate()
           self._agent_registry: Dict[str, Type[VibeAgent]] = {}
           self._initialized = False

       def _load_and_validate(self) -> PhoenixConfig:
           """Load phoenix.yaml and validate with Pydantic"""
           if not self.config_path.exists():
               raise FileNotFoundError(f"Phoenix config not found: {self.config_path}")

           with open(self.config_path) as f:
               raw_config = yaml.safe_load(f)

           return PhoenixConfig(**raw_config)

       def enforce_import_order(self) -> None:
           """Pre-import modules in correct order to avoid circular deps"""
           logger.info("🔥 Phoenix: Enforcing import order...")

           for module_name in self.config.imports.order:
               try:
                   importlib.import_module(module_name)
                   logger.info(f"  ✅ {module_name}")
               except ImportError as e:
                   logger.warning(f"  ⚠️  {module_name}: {e}")
                   # Continue - some modules may not exist yet

       def _import_class(self, class_path: str) -> Type:
           """Dynamically import a class from module:class string"""
           try:
               module_name, class_name = class_path.split(":")
               module = importlib.import_module(module_name)
               cls = getattr(module, class_name)
               return cls
           except Exception as e:
               logger.error(f"Failed to import {class_path}: {e}")
               raise ImportError(f"Cannot load {class_path}") from e

       def wire_agents(self) -> Dict[str, Type[VibeAgent]]:
           """Wire all enabled system agents"""
           if self._agent_registry:
               return self._agent_registry

           logger.info("🔥 Phoenix: Wiring agents...")

           for agent_config in self.config.agents.system_agents:
               if not agent_config.enabled:
                   logger.info(f"  ⏭️  {agent_config.id} (disabled)")
                   continue

               try:
                   agent_class = self._import_class(agent_config.class_path)

                   # Validate it's actually a VibeAgent
                   if not issubclass(agent_class, VibeAgent):
                       raise TypeError(f"{agent_class} is not a VibeAgent")

                   self._agent_registry[agent_config.id] = agent_class
                   logger.info(f"  ✅ {agent_config.id} → {agent_config.class_path}")

               except Exception as e:
                   logger.error(f"  ❌ {agent_config.id}: {e}")
                   # Continue - don't fail entire system for one agent

           logger.info(f"🔥 Phoenix: Wired {len(self._agent_registry)} agents")
           return self._agent_registry

       def get_agent(self, agent_id: str) -> Type[VibeAgent]:
           """Get agent class by ID"""
           if not self._agent_registry:
               self.wire_agents()

           if agent_id not in self._agent_registry:
               raise KeyError(f"Agent not found: {agent_id}")

           return self._agent_registry[agent_id]

       def health_check(self) -> Dict[str, Any]:
           """System health check"""
           return {
               "phoenix_initialized": self._initialized,
               "agents_wired": len(self._agent_registry),
               "config_loaded": self.config is not None,
               "agents": {
                   agent_id: "OK"
                   for agent_id in self._agent_registry.keys()
               }
           }

   # Singleton
   _phoenix: PhoenixConfigEngine | None = None

   def get_phoenix() -> PhoenixConfigEngine:
       """Get singleton Phoenix instance"""
       global _phoenix
       if _phoenix is None:
           _phoenix = PhoenixConfigEngine()
       return _phoenix
   ```

3. Add comprehensive error handling
4. Add structured logging
5. Add validation

**Validation:**
```bash
# Test import
python -c "from vibe_core.phoenix_config import get_phoenix; phoenix = get_phoenix(); print(phoenix.health_check())"

# Test agent wiring
python -c "from vibe_core.phoenix_config import get_phoenix; phoenix = get_phoenix(); phoenix.enforce_import_order(); agents = phoenix.wire_agents(); print(f'Wired: {len(agents)}')"
```

---

### Task 2.4: Integrate Phoenix into run_server.py
**Priority:** P0
**Estimated:** 1h

**Actions:**
1. Modify run_server.py to use Phoenix:
   ```python
   from vibe_core.phoenix_config import get_phoenix

   def main():
       # Initialize Phoenix
       phoenix = get_phoenix()

       # Enforce import order
       phoenix.enforce_import_order()

       # Wire agents
       agent_classes = phoenix.wire_agents()

       # Load config
       city_config = load_config()

       # Create orchestrator with wired agents
       orchestrator = BootOrchestrator(
           config=city_config,
           agent_classes=agent_classes
       )

       # Start server
       orchestrator.boot()
   ```

2. Update BootOrchestrator to accept agent_classes

**Validation:**
```bash
python run_server.py --dry-run 2>&1 | grep "Phoenix\\|Wired"
# Expected: Phoenix logs + agent count
```

---

### Task 2.5: Remove MockAgent Defaults
**Priority:** P0
**Estimated:** 1h

**Actions:**
1. Find all MockAgent usages:
   ```bash
   grep -r "MockAgent" vibe_core/ steward/ --include="*.py"
   ```

2. Replace with Phoenix-wired agents:
   ```python
   # BEFORE:
   self.agent = MockAgent()

   # AFTER:
   from vibe_core.phoenix_config import get_phoenix
   phoenix = get_phoenix()
   agent_class = phoenix.get_agent("executor_agent")
   self.agent = agent_class(config=self.config)
   ```

3. Remove mock files if no longer needed

**Validation:**
```bash
grep -r "MockAgent" vibe_core/ steward/ --include="*.py" | wc -l
# Expected: 0
```

---

### Task 2.6: Integration Testing
**Priority:** P0
**Estimated:** 2h

**Actions:**
1. Create `tests/test_phoenix_integration.py`:
   ```python
   def test_phoenix_loads_config():
       """Phoenix can load phoenix.yaml"""
       from vibe_core.phoenix_config import get_phoenix
       phoenix = get_phoenix()
       assert phoenix.config is not None

   def test_phoenix_wires_agents():
       """Phoenix wires all enabled agents"""
       from vibe_core.phoenix_config import get_phoenix
       phoenix = get_phoenix()
       agents = phoenix.wire_agents()
       assert len(agents) >= 10  # At least 10 agents

   def test_agents_are_vibeagent():
       """All wired agents are VibeAgent subclasses"""
       from vibe_core.phoenix_config import get_phoenix
       from vibe_core.protocols import VibeAgent

       phoenix = get_phoenix()
       agents = phoenix.wire_agents()

       for agent_id, agent_class in agents.items():
           assert issubclass(agent_class, VibeAgent), f"{agent_id} is not VibeAgent"

   def test_server_starts_with_phoenix():
       """Server starts successfully with Phoenix"""
       # TODO: Implement server startup test
   ```

2. Run integration tests:
   ```bash
   pytest tests/test_phoenix_integration.py -v
   ```

**Validation:**
- [ ] All Phoenix tests pass
- [ ] Agents wire successfully
- [ ] No import errors

---

### Phase 2 Exit Criteria

**MUST be true before Phase 3:**
- [ ] phoenix.yaml created and validated
- [ ] PhoenixConfigEngine implemented
- [ ] All 13 agents wire successfully
- [ ] MockAgent removed completely
- [ ] run_server.py uses Phoenix
- [ ] Integration tests pass
- [ ] Server starts with Phoenix
- [ ] Health check works
- [ ] Git commit: "feat: Phase 2 - Phoenix wiring complete"

---

## ✅ PHASE 3: QUALITY & TESTING (6-8h)

**Goal:** Comprehensive testing, quality gates
**Success Criteria:** >80% test coverage, all tests pass

### Task 3.1: Unit Test Coverage
**Priority:** P0
**Estimated:** 3-4h

**Actions:**
1. Install coverage tools:
   ```bash
   pip install pytest-cov coverage
   ```

2. Write unit tests for critical modules:
   - `tests/unit/test_protocols.py` - All protocols
   - `tests/unit/test_phoenix.py` - Phoenix engine
   - `tests/unit/test_agents.py` - Each system agent
   - `tests/unit/test_kernel.py` - Kernel
   - `tests/unit/test_ledger.py` - Ledger

3. Run with coverage:
   ```bash
   pytest tests/unit/ --cov=vibe_core --cov=steward --cov-report=html --cov-report=term
   ```

4. Target: >80% coverage

**Validation:**
```bash
coverage report --fail-under=80
```

---

### Task 3.2: Integration Test Suite
**Priority:** P0
**Estimated:** 2-3h

**Actions:**
1. Create comprehensive integration tests:
   ```python
   # tests/integration/test_full_system.py

   def test_server_startup():
       """Full server startup test"""

   def test_agent_communication():
       """Agents can communicate via kernel"""

   def test_ledger_operations():
       """Ledger operations work end-to-end"""

   def test_config_distribution():
       """Config flows to all agents"""

   def test_phoenix_agent_lifecycle():
       """Agent creation, execution, shutdown"""
   ```

2. Test error scenarios:
   ```python
   def test_invalid_config_fails_gracefully():
       """Bad config causes fail-fast, not crash"""

   def test_missing_agent_graceful_degradation():
       """System continues if one agent fails"""
   ```

**Validation:**
```bash
pytest tests/integration/ -v
```

---

### Task 3.3: Performance Benchmarking
**Priority:** P1
**Estimated:** 1-2h

**Actions:**
1. Create `tests/performance/test_benchmarks.py`:
   ```python
   import time

   def test_server_startup_time():
       """Server starts in <5 seconds"""
       start = time.time()
       # Start server
       duration = time.time() - start
       assert duration < 5.0

   def test_agent_wiring_time():
       """Phoenix wires agents in <1 second"""
       from vibe_core.phoenix_config import get_phoenix
       start = time.time()
       phoenix = get_phoenix()
       phoenix.wire_agents()
       duration = time.time() - start
       assert duration < 1.0

   def test_agent_process_latency():
       """Agent processes task in <100ms"""
       # TODO: Implement
   ```

2. Run benchmarks:
   ```bash
   pytest tests/performance/ -v --benchmark
   ```

**Validation:**
- [ ] Startup < 5s
- [ ] Wiring < 1s
- [ ] No performance regressions

---

### Task 3.4: Security Audit
**Priority:** P1
**Estimated:** 1h

**Actions:**
1. Check for security issues:
   ```bash
   # Install security tools
   pip install bandit safety

   # Run security scan
   bandit -r vibe_core/ steward/ -o security_report.txt

   # Check dependencies
   safety check --json > safety_report.json
   ```

2. Fix any HIGH/CRITICAL issues

3. Document security posture

**Validation:**
- [ ] No HIGH/CRITICAL bandit findings
- [ ] No vulnerable dependencies
- [ ] Security report documented

---

### Phase 3 Exit Criteria

**MUST be true before Phase 4:**
- [ ] Unit test coverage >80%
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance benchmarks pass
- [ ] Security audit clean
- [ ] No critical issues
- [ ] Git commit: "test: Phase 3 - Quality & testing complete"

---

## 🚀 PHASE 4: PRODUCTION READINESS (4-6h)

**Goal:** CI/CD, monitoring, docs, deployment
**Success Criteria:** Production-ready

### Task 4.1: Structured Logging
**Priority:** P0
**Estimated:** 2h

**Actions:**
1. Implement structured logging throughout:
   ```python
   import structlog

   logger = structlog.get_logger(__name__)

   logger.info("agent.started",
               agent_id=agent_id,
               config=config_summary)
   ```

2. Configure log levels (DEBUG, INFO, WARN, ERROR)

3. Add request ID tracking

4. Output JSON logs for production

**Validation:**
```bash
python run_server.py 2>&1 | jq .  # Should parse as JSON
```

---

### Task 4.2: Health & Readiness Endpoints
**Priority:** P0
**Estimated:** 1h

**Actions:**
1. Add health check endpoint:
   ```python
   @app.get("/health")
   def health():
       return {
           "status": "healthy",
           "phoenix": phoenix.health_check(),
           "agents": len(phoenix._agent_registry)
       }

   @app.get("/ready")
   def readiness():
       # Check if system is ready to serve
       return {"ready": True}
   ```

**Validation:**
```bash
curl localhost:8000/health
curl localhost:8000/ready
```

---

### Task 4.3: Metrics & Observability
**Priority:** P1
**Estimated:** 1-2h

**Actions:**
1. Add Prometheus metrics:
   ```python
   from prometheus_client import Counter, Histogram

   agent_executions = Counter("agent_executions_total", "Agent executions", ["agent_id"])
   agent_latency = Histogram("agent_latency_seconds", "Agent latency", ["agent_id"])
   ```

2. Expose /metrics endpoint

**Validation:**
```bash
curl localhost:8000/metrics | grep agent_
```

---

### Task 4.4: Documentation
**Priority:** P0
**Estimated:** 2h

**Actions:**
1. Update README.md:
   - Architecture overview
   - Quick start
   - Development setup
   - Production deployment

2. Create docs/:
   - `docs/ARCHITECTURE.md` - 3-layer architecture
   - `docs/PHOENIX.md` - Phoenix config guide
   - `docs/DEVELOPMENT.md` - Developer guide
   - `docs/PRODUCTION.md` - Production deployment
   - `docs/TROUBLESHOOTING.md` - Common issues

3. Add inline docstrings (Google style)

**Validation:**
- [ ] README complete
- [ ] All docs created
- [ ] Docstrings added

---

### Task 4.5: CI/CD Pipeline
**Priority:** P1
**Estimated:** 1-2h

**Actions:**
1. Create `.github/workflows/ci.yml`:
   ```yaml
   name: CI

   on: [push, pull_request]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: pip install -r requirements.txt
         - name: Run tests
           run: pytest tests/ --cov --cov-report=xml
         - name: Upload coverage
           uses: codecov/codecov-action@v3
   ```

2. Add quality gates:
   - Tests must pass
   - Coverage >80%
   - Security scan clean

**Validation:**
- [ ] CI pipeline runs
- [ ] Tests pass on CI
- [ ] Quality gates work

---

### Phase 4 Exit Criteria

**MUST be true:**
- [ ] Structured logging implemented
- [ ] Health/readiness endpoints work
- [ ] Metrics exposed
- [ ] Documentation complete
- [ ] CI/CD pipeline runs
- [ ] Git commit: "feat: Phase 4 - Production ready"

---

## 📊 FINAL VALIDATION & SIGN-OFF

### Production Readiness Checklist

**Architecture:**
- [ ] 3-layer architecture enforced
- [ ] Zero circular dependencies
- [ ] All protocols in Layer 1
- [ ] All implementations in Layer 2
- [ ] Phoenix in Layer 3

**Code Quality:**
- [ ] Zero try/except ImportError (except external deps)
- [ ] All agents import successfully
- [ ] No MockAgent fallbacks
- [ ] Type hints throughout
- [ ] Docstrings complete

**Testing:**
- [ ] >80% test coverage
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance benchmarks pass
- [ ] Security audit clean

**Operational:**
- [ ] Server starts reliably
- [ ] Health checks work
- [ ] Logging structured
- [ ] Metrics exposed
- [ ] Documentation complete

**Deployment:**
- [ ] CI/CD pipeline working
- [ ] Docker image builds
- [ ] Config externalized
- [ ] Secrets management

### Range Rover Quality Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Test Coverage | >80% | ___ |
| Server Startup | <5s | ___ |
| Agent Wiring | <1s | ___ |
| try/except Count | <10 | ___ |
| Import Errors | 0 | ___ |
| Circular Deps | 0 | ___ |
| Security Issues | 0 | ___ |
| Doc Pages | >5 | ___ |

---

## 🎯 WHAT SUCCESS LOOKS LIKE

When this roadmap is complete:

```
✅ Developer runs: python run_server.py
   → Server starts in 3 seconds
   → Phoenix wires 13 agents
   → Health check returns 200 OK
   → System ready for requests

✅ Developer runs: pytest tests/
   → 150+ tests collected
   → All tests pass
   → Coverage: 85%
   → No warnings

✅ Developer deploys to production:
   → Docker build succeeds
   → CI pipeline green
   → Health checks pass
   → Metrics flowing
   → System stable

✅ Developer adds new agent:
   → Inherit from VibeAgent (protocol)
   → Add to phoenix.yaml
   → Phoenix wires automatically
   → No code changes needed elsewhere
```

**That's Range Rover robustness.**

---

## 📅 EXECUTION TIMELINE

### Realistic Schedule (35 hours)

**Week 1:**
- Days 1-2: Phase 0 (6h) - Critical fixes
- Days 3-4: Phase 1 (8h) - Foundation hardening

**Week 2:**
- Days 1-3: Phase 2 (10h) - Phoenix wiring
- Days 4-5: Phase 3 (8h) - Testing

**Week 3:**
- Days 1-2: Phase 4 (6h) - Production readiness
- Day 3: Final validation & sign-off

**Total: 3 weeks (part-time) or 1 week (full-time)**

---

## 🚨 RISK MITIGATION

### Known Risks

1. **Import hell** - Circular dependencies resurface
   - Mitigation: Strict layer enforcement, import order validation

2. **Tests reveal deeper issues** - Breaking changes cascade
   - Mitigation: Fix incrementally, don't skip tests

3. **Phoenix complexity** - Too much indirection
   - Mitigation: Keep it simple, document well

4. **Timeline slippage** - 35h becomes 50h
   - Mitigation: Track progress, adjust scope if needed

---

## 🎓 HAIKU EXECUTION TIPS

This plan is Haiku-friendly:

1. **One phase at a time** - Complete Phase 0 before Phase 1
2. **One task at a time** - Follow sequence
3. **Validate each task** - Check criteria before proceeding
4. **Use checkboxes** - Track progress
5. **If stuck** - Review validation criteria
6. **Ask for help** - If validation fails repeatedly

**You can run tasks in parallel within a phase if they're independent.**

---

## 📚 REFERENCES

- HONEST_PLAN.md - Original brutal assessment
- BLOCKER2_HAIKU_PLAN.md - Original Haiku plan
- BLOCKER2_ANALYSIS_SUMMARY.md - Gap analysis

---

## 🏁 FINAL WORD

This is the **REAL path to production**.

No shortcuts. No half-measures. **Range Rover quality.**

When you finish this roadmap:
- ✅ System will RUN reliably
- ✅ Tests will PASS consistently
- ✅ Code will be MAINTAINABLE
- ✅ Architecture will be CLEAN
- ✅ Deployment will be AUTOMATED
- ✅ Team will be CONFIDENT

**That's worth 35 hours.**

Let's build something solid. 🏗️

---

**Created by:** Claude (Senior)
**Quality Standard:** Vimana-class Range Rover
**Status:** READY FOR EXECUTION
**Next Step:** Begin Phase 0, Task 0.1
