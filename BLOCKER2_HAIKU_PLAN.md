# BLOCKER #2: Haiku Execution Plan
**Optimized for: Claude Haiku**
**Created: 2025-11-27**
**Goal: Fix 92 try/except workarounds via 3-layer architecture**

---

## PREREQUISITES CHECKLIST

Before starting, verify:
- [ ] BLOCKER #0 is complete (config distribution working)
- [ ] BLOCKER #1 is complete (ledger hierarchy clean)
- [ ] Working directory: `/home/user/steward-protocol`
- [ ] Branch: `claude/analyze-haiku-content-01BGAeaVRpPYYEMAQmcjQecc`
- [ ] All tests currently passing
- [ ] Git status clean

---

## PHASE 1: PROTOCOL AUDIT (Est: 1-2h)

### Task 1.1: Identify ALL ABCs to Move
**Action:** Search codebase for abstract base classes
**Command:**
```bash
grep -r "class.*ABC" vibe_core/ steward/ provider/ --include="*.py"
grep -r "from abc import" vibe_core/ steward/ provider/ --include="*.py"
```

**Create file:** `migration/protocol_inventory.txt`
**Expected ABCs (minimum):**
- VibeAgent (from steward/agent.py)
- VibeLedger (from vibe_core/kernel.py) ✅ Already canonical
- VibeStore (if exists)
- VibePlaybook (if exists)
- OathProtocol (if exists)
- Additional ABCs found during search

**Validation:**
- [ ] All ABCs listed in protocol_inventory.txt
- [ ] Current location noted for each
- [ ] Dependencies mapped

---

### Task 1.2: Map Import Dependencies
**Action:** Find all files importing each ABC
**Command:**
```bash
# For each ABC found:
grep -r "from steward.agent import VibeAgent" --include="*.py"
grep -r "import VibeAgent" --include="*.py"
# Repeat for each ABC
```

**Create file:** `migration/import_map.txt`
**Format:**
```
VibeAgent:
  - Current location: steward/agent.py
  - Imported by:
    - file1.py (line X)
    - file2.py (line Y)
  - Dependencies: [list]
```

**Validation:**
- [ ] All import sites identified
- [ ] Circular dependencies marked
- [ ] Count matches expected files (~60)

---

### Task 1.3: Catalog try/except Patterns
**Action:** Find and categorize all try/except ImportError
**Command:**
```bash
grep -r "except ImportError" vibe_core/ steward/ provider/ -A 2 -B 2 --include="*.py" > migration/tryexcept_catalog.txt
```

**Expected count:** 92 instances

**Categorize by type:**
1. Agent imports (SimpleLLMAgent, etc.)
2. Protocol imports (VibeAgent, etc.)
3. Config imports
4. Ledger imports
5. Other

**Create file:** `migration/tryexcept_breakdown.txt`

**Validation:**
- [ ] All 92 instances found
- [ ] Categorized by import type
- [ ] Root cause identified for each

---

## PHASE 2: LAYER 1 - PROTOCOL DEFINITIONS (Est: 2-3h)

### Task 2.1: Create Protocol Directory Structure
**Action:** Set up Layer 1 structure
```bash
mkdir -p vibe_core/protocols
touch vibe_core/protocols/__init__.py
```

**Files to create:**
```
vibe_core/protocols/
├── __init__.py          # Protocol exports
├── agent.py             # VibeAgent ABC
├── ledger.py            # VibeLedger ABC (import from kernel)
├── store.py             # VibeStore ABC
├── playbook.py          # VibePlaybook ABC
├── oath.py              # OathProtocol ABC
└── [additional based on 1.1]
```

**Validation:**
- [ ] Directory created
- [ ] __init__.py exists
- [ ] No circular imports possible (protocols only import stdlib/abc)

---

### Task 2.2: Move VibeAgent to protocols/agent.py
**Action:** Create canonical VibeAgent protocol

**Read:** `steward/agent.py`
**Extract:** VibeAgent ABC definition
**Write:** `vibe_core/protocols/agent.py`

**Template:**
```python
"""Layer 1: VibeAgent Protocol Definition
NO IMPLEMENTATIONS - ONLY INTERFACE
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class VibeAgent(ABC):
    """Canonical VibeAgent protocol"""

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        pass

    # ... copy all abstract methods from steward/agent.py
```

**Validation:**
- [ ] File created
- [ ] Only ABC, no implementations
- [ ] All abstract methods present
- [ ] No imports from vibe_core/steward (except typing/abc)
- [ ] Docstrings clear

---

### Task 2.3: Create protocols/ledger.py (Reference)
**Action:** Reference existing canonical VibeLedger

**Content:**
```python
"""Layer 1: VibeLedger Protocol
Canonical definition is in vibe_core.kernel
This is a reference/re-export for Layer 1 clarity
"""
from vibe_core.kernel import VibeLedger

__all__ = ["VibeLedger"]
```

**Validation:**
- [ ] File created
- [ ] Imports from kernel (already canonical from BLOCKER #1)
- [ ] No circular dependency

---

### Task 2.4: Create Remaining Protocol Files
**Action:** For each ABC from Task 1.1, create protocol file

**Process:**
1. Read source file
2. Extract ABC definition
3. Create new file in protocols/
4. Copy ABC (interface only)
5. Remove any implementation details
6. Add clear docstring

**Validation per file:**
- [ ] Only ABC definition
- [ ] No implementation code
- [ ] No Layer 2/3 imports
- [ ] Docstring explains purpose

---

### Task 2.5: Create protocols/__init__.py Exports
**Action:** Central export point for all protocols

**Content:**
```python
"""Layer 1: Protocol Definitions
All abstract base classes (ABCs) for the vibe system.
NO IMPLEMENTATIONS ALLOWED IN THIS LAYER.
"""

from vibe_core.protocols.agent import VibeAgent
from vibe_core.protocols.ledger import VibeLedger
from vibe_core.protocols.store import VibeStore
from vibe_core.protocols.playbook import VibePlaybook
from vibe_core.protocols.oath import OathProtocol
# ... add all protocols

__all__ = [
    "VibeAgent",
    "VibeLedger",
    "VibeStore",
    "VibePlaybook",
    "OathProtocol",
    # ... list all
]
```

**Validation:**
- [ ] All protocols exported
- [ ] No circular imports
- [ ] Import test passes: `python -c "from vibe_core.protocols import *"`

---

## PHASE 3: LAYER 2 - UPDATE IMPLEMENTATIONS (Est: 4-6h)

### Task 3.1: Update Agent Implementations
**Action:** Change imports in all agent files

**Files to update (from Task 1.2 import_map.txt):**
- steward/system_agents/*.py (13 files)
- vibe_core/agents/*.py
- Any other agent implementations

**Change pattern:**
```python
# OLD:
from steward.agent import VibeAgent

# NEW:
from vibe_core.protocols import VibeAgent
```

**Process:**
1. For each file in import_map.txt
2. Read file
3. Replace import statement
4. Verify implementation still inherits correctly
5. Save file
6. Run quick syntax check: `python -m py_compile <file>`

**Validation:**
- [ ] All agent files updated
- [ ] All agents still inherit from VibeAgent
- [ ] Syntax check passes for each file
- [ ] No broken imports

---

### Task 3.2: Update Ledger Implementations
**Action:** Verify ledger implementations use canonical import

**Files:**
- vibe_core/ledger.py (should already import from kernel - BLOCKER #1)
- justice/ledger.py
- audit/ledger.py

**Expected pattern (should already be correct from BLOCKER #1):**
```python
from vibe_core.protocols import VibeLedger
# OR
from vibe_core.kernel import VibeLedger  # Also valid
```

**Validation:**
- [ ] All ledger implementations checked
- [ ] Imports are canonical
- [ ] No duplicate VibeLedger definitions

---

### Task 3.3: Update Store Implementations
**Action:** Change imports in store-related files

**Files to update:**
- vibe_core/store/*.py
- Any files importing store protocols

**Change pattern:**
```python
# OLD:
from vibe_core.store import VibeStore

# NEW:
from vibe_core.protocols import VibeStore
```

**Validation:**
- [ ] All store files updated
- [ ] Implementations inherit from protocol
- [ ] Syntax valid

---

### Task 3.4: Update Playbook Implementations
**Action:** Change imports in playbook files

**Files:**
- vibe_core/playbook/*.py
- executor.py (critical - has MockAgent)

**Change pattern:**
```python
# OLD:
try:
    from vibe_core.agents.llm_agent import SimpleLLMAgent
except ImportError:
    SimpleLLMAgent = None

# NEW:
from vibe_core.protocols import VibeAgent
# Implementation wiring happens in Layer 3, not here
```

**Validation:**
- [ ] Imports updated
- [ ] try/except removed (track count)
- [ ] No broken references

---

### Task 3.5: Update Provider Implementations
**Action:** Update imports in provider/ modules

**Files:**
- provider/**/*.py

**Change pattern:**
```python
# OLD:
from steward.agent import VibeAgent

# NEW:
from vibe_core.protocols import VibeAgent
```

**Validation:**
- [ ] All provider files updated
- [ ] Syntax valid
- [ ] Provider tests still pass (if they exist)

---

### Task 3.6: Systematic try/except Removal
**Action:** Remove all try/except ImportError blocks identified in Task 1.3

**Process:**
For each of 92 instances in `tryexcept_breakdown.txt`:

1. Open file
2. Locate try/except block
3. Determine replacement strategy:
   - If importing protocol → use `from vibe_core.protocols import X`
   - If importing implementation → defer to Layer 3 (PhoenixConfig)
   - If defensive/unknown → mark for review
4. Remove try/except
5. Update import
6. Test syntax

**Tracking:**
Create `migration/tryexcept_removal_log.txt`:
```
[1/92] file.py:line - REMOVED - replaced with protocol import
[2/92] file.py:line - REMOVED - deferred to Layer 3
[3/92] file.py:line - NEEDS REVIEW - unclear intent
...
```

**Validation:**
- [ ] All 92 instances reviewed
- [ ] Removal strategy applied
- [ ] Count: 0 try/except ImportError remaining
- [ ] All files syntax-valid

---

## PHASE 4: LAYER 3 - PHOENIX CONFIG ENGINE (Est: 2-3h)

### Task 4.1: Define phoenix.yaml Schema
**Action:** Create configuration file for agent wiring

**Create:** `config/phoenix.yaml`

**Schema:**
```yaml
# Phoenix Configuration - Layer 3 Dynamic Wiring
# This file defines HOW implementations are wired to protocols

system:
  kernel:
    ledger: "vibe_core.ledger:VibeLedger"
    store: "vibe_core.store:VibeStore"

agents:
  system_agents:
    - name: "DiscoveryAgent"
      class: "steward.system_agents.discovery:DiscoveryAgent"
      protocol: "VibeAgent"
      enabled: true

    - name: "SimpleLLMAgent"
      class: "vibe_core.agents.llm_agent:SimpleLLMAgent"
      protocol: "VibeAgent"
      enabled: true

    # ... all 13 system agents

  custom_agents: []

playbook:
  executor_agent: "vibe_core.agents.llm_agent:SimpleLLMAgent"
  default_fallback: "vibe_core.agents.mock:MockAgent"

providers:
  llm_provider: "provider.llm:DefaultLLMProvider"

imports:
  # Explicit import order to avoid circular dependencies
  order:
    - "vibe_core.protocols"
    - "vibe_core.kernel"
    - "vibe_core.ledger"
    - "vibe_core.store"
    - "vibe_core.agents"
    - "steward.system_agents"
    - "vibe_core.playbook"
```

**Validation:**
- [ ] Valid YAML syntax
- [ ] All 13 system agents listed
- [ ] Import order respects layer architecture
- [ ] No circular dependencies in order

---

### Task 4.2: Create PhoenixConfigEngine
**Action:** Build dynamic wiring engine

**Create:** `vibe_core/phoenix_config.py`

**Structure:**
```python
"""Layer 3: Phoenix Configuration Engine
Dynamic wiring of implementations to protocols.
"""

import importlib
from typing import Any, Dict, Type
from pathlib import Path
import yaml

from vibe_core.protocols import VibeAgent, VibeLedger, VibeStore

class PhoenixConfigEngine:
    """Dynamically wires implementations based on phoenix.yaml"""

    def __init__(self, config_path: str = "config/phoenix.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._registry: Dict[str, Type] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load phoenix.yaml"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _import_class(self, class_path: str) -> Type:
        """Import class from module:class string"""
        module_name, class_name = class_path.split(":")
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def wire_agents(self) -> Dict[str, VibeAgent]:
        """Wire all agent implementations"""
        agents = {}
        for agent_config in self.config['agents']['system_agents']:
            if agent_config['enabled']:
                agent_class = self._import_class(agent_config['class'])
                agents[agent_config['name']] = agent_class
        return agents

    def wire_kernel(self) -> Dict[str, Type]:
        """Wire kernel components"""
        kernel = {}
        for component, class_path in self.config['system']['kernel'].items():
            kernel[component] = self._import_class(class_path)
        return kernel

    def get_playbook_executor_agent(self) -> Type[VibeAgent]:
        """Get configured executor agent class"""
        class_path = self.config['playbook']['executor_agent']
        return self._import_class(class_path)

    def enforce_import_order(self):
        """Pre-import modules in correct order to avoid circular deps"""
        for module_name in self.config['imports']['order']:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                # Log but continue - some modules may not exist yet
                print(f"Warning: Could not pre-import {module_name}: {e}")

# Singleton instance
_engine: PhoenixConfigEngine | None = None

def get_phoenix_engine() -> PhoenixConfigEngine:
    """Get singleton Phoenix engine instance"""
    global _engine
    if _engine is None:
        _engine = PhoenixConfigEngine()
    return _engine
```

**Validation:**
- [ ] File created
- [ ] Can load phoenix.yaml
- [ ] Can import classes dynamically
- [ ] Singleton pattern works
- [ ] Test: `python -c "from vibe_core.phoenix_config import get_phoenix_engine; get_phoenix_engine()"`

---

### Task 4.3: Update run_server.py to Use Phoenix
**Action:** Wire PhoenixConfigEngine into server startup

**Read:** `run_server.py`
**Modify:** Add Phoenix engine initialization

**Changes:**
```python
# Add near top:
from vibe_core.phoenix_config import get_phoenix_engine

# In main() or startup:
def main():
    # Load config (existing code)
    config = load_config()

    # NEW: Initialize Phoenix engine
    phoenix = get_phoenix_engine()
    phoenix.enforce_import_order()

    # NEW: Wire agents
    agent_classes = phoenix.wire_agents()

    # Use wired agents instead of hardcoded imports
    boot_orchestrator = BootOrchestrator(
        config=config,
        agent_classes=agent_classes  # NEW: pass wired classes
    )

    # ... rest of existing code
```

**Validation:**
- [ ] Phoenix engine imported
- [ ] Import order enforced
- [ ] Agents wired dynamically
- [ ] Server still starts
- [ ] No hardcoded agent imports in run_server.py

---

### Task 4.4: Update BootOrchestrator to Accept Wired Agents
**Action:** Modify orchestrator to use dynamically wired agents

**Read:** `steward/boot_orchestrator.py`
**Modify:** Accept agent_classes parameter

**Changes:**
```python
class BootOrchestrator:
    def __init__(
        self,
        config: CityConfig,
        agent_classes: Dict[str, Type[VibeAgent]] | None = None  # NEW
    ):
        self.config = config
        self.agent_classes = agent_classes or {}  # NEW
        # ... existing code

    def _discover_agents(self):
        """Use wired agents instead of hardcoded imports"""
        # OLD: hardcoded imports
        # NEW: use self.agent_classes
        for agent_name, agent_class in self.agent_classes.items():
            # Instantiate agent
            agent = agent_class(config=self.config)
            # ... rest of logic
```

**Validation:**
- [ ] BootOrchestrator updated
- [ ] Accepts agent_classes parameter
- [ ] Uses dynamic agents instead of imports
- [ ] Backward compatible (default to {} if not provided)

---

### Task 4.5: Update Playbook Executor to Use Phoenix
**Action:** Remove MockAgent default, use Phoenix-wired agent

**Read:** `vibe_core/playbook/executor.py`
**Modify:** Use Phoenix to get executor agent

**Changes:**
```python
# Remove:
# try:
#     from vibe_core.agents.llm_agent import SimpleLLMAgent
# except ImportError:
#     SimpleLLMAgent = None

# Add:
from vibe_core.phoenix_config import get_phoenix_engine

class PlaybookExecutor:
    def __init__(self, config: dict | None = None):
        self.config = config

        # NEW: Get agent from Phoenix
        phoenix = get_phoenix_engine()
        agent_class = phoenix.get_playbook_executor_agent()
        self.agent = agent_class(config=config)

        # OLD was:
        # self.agent = MockAgent()
```

**Validation:**
- [ ] MockAgent default removed
- [ ] Phoenix-wired agent used
- [ ] try/except removed
- [ ] Executor works with real agent

---

## PHASE 5: VALIDATION & TESTING (Est: 2-3h)

### Task 5.1: Verify Zero try/except ImportError
**Action:** Confirm all workarounds removed

**Command:**
```bash
grep -r "except ImportError" vibe_core/ steward/ provider/ --include="*.py" | wc -l
```

**Expected:** 0

**If not 0:**
- Review remaining instances
- Determine if legitimate or missed
- Remove or document reason

**Validation:**
- [ ] Count is 0
- [ ] All 92 from Task 1.3 accounted for

---

### Task 5.2: Test Import Order (No Circular Deps)
**Action:** Verify imports don't create cycles

**Create test:** `tests/test_import_order.py`
```python
"""Test that import order doesn't create circular dependencies"""

def test_layer1_imports():
    """Layer 1 protocols should import cleanly"""
    from vibe_core.protocols import (
        VibeAgent, VibeLedger, VibeStore, VibePlaybook, OathProtocol
    )
    assert VibeAgent is not None
    assert VibeLedger is not None
    # ... all protocols

def test_layer2_imports():
    """Layer 2 implementations should import cleanly"""
    from vibe_core.ledger import VibeLedger as ImplLedger
    from steward.system_agents.discovery import DiscoveryAgent
    # ... all implementations

def test_layer3_phoenix():
    """Layer 3 Phoenix should wire everything"""
    from vibe_core.phoenix_config import get_phoenix_engine
    phoenix = get_phoenix_engine()
    phoenix.enforce_import_order()
    agents = phoenix.wire_agents()
    assert len(agents) == 13  # All system agents
```

**Run:**
```bash
pytest tests/test_import_order.py -v
```

**Validation:**
- [ ] All import tests pass
- [ ] No circular dependency errors
- [ ] Phoenix wires all 13 agents

---

### Task 5.3: Run Existing Test Suite
**Action:** Ensure nothing broke

**Command:**
```bash
pytest tests/ -v
```

**Expected:**
- All tests that passed before still pass
- No new import errors
- No new failures

**If failures:**
- Investigate each failure
- Determine if due to migration
- Fix or document

**Validation:**
- [ ] Test suite runs
- [ ] No regressions
- [ ] Import-related tests pass

---

### Task 5.4: Integration Test - Start Server
**Action:** Verify server starts with new architecture

**Command:**
```bash
python run_server.py
```

**Expected:**
- Phoenix engine initializes
- Import order enforced
- 13 agents wired
- Server starts successfully
- No import errors in logs

**Monitor logs for:**
- "Phoenix engine initialized"
- "Agents wired: 13"
- No "ImportError" messages
- No "ModuleNotFoundError" messages

**Validation:**
- [ ] Server starts
- [ ] Phoenix engine works
- [ ] All agents loaded
- [ ] No import errors

---

### Task 5.5: Smoke Test - Agent Operations
**Action:** Test that agents actually work

**Test cases:**
1. Create an agent instance
2. Call agent.process()
3. Verify response
4. Check ledger operations
5. Verify config distribution

**Create:** `tests/test_blocker2_smoke.py`
```python
"""Smoke tests for BLOCKER #2 completion"""

def test_agent_creation():
    """Can create agents through Phoenix"""
    from vibe_core.phoenix_config import get_phoenix_engine
    phoenix = get_phoenix_engine()
    agents = phoenix.wire_agents()

    # Test one agent
    DiscoveryAgent = agents['DiscoveryAgent']
    agent = DiscoveryAgent(config={})
    assert agent is not None

def test_agent_operation():
    """Can call agent methods"""
    # ... test agent.process() works

def test_ledger_hierarchy():
    """Ledger hierarchy still works (BLOCKER #1)"""
    from vibe_core.protocols import VibeLedger
    from vibe_core.ledger import VibeLedger as ImplLedger
    assert issubclass(ImplLedger, VibeLedger)

def test_config_distribution():
    """Config distribution still works (BLOCKER #0)"""
    # ... test config flows through
```

**Run:**
```bash
pytest tests/test_blocker2_smoke.py -v
```

**Validation:**
- [ ] All smoke tests pass
- [ ] Agents operational
- [ ] BLOCKER #0 still works
- [ ] BLOCKER #1 still works

---

### Task 5.6: Performance Check
**Action:** Verify no major performance regression

**Benchmark:**
1. Server startup time
2. Agent creation time
3. Agent operation latency

**Before BLOCKER #2 (baseline):**
- (Record if known)

**After BLOCKER #2:**
- Server startup: ___ seconds
- Agent creation: ___ ms
- Agent operation: ___ ms

**Acceptable:**
- Startup < 5 seconds
- Creation < 100ms
- Operation < previous baseline + 10%

**Validation:**
- [ ] No significant regression
- [ ] Performance acceptable
- [ ] If regression > 10%, investigate

---

## PHASE 6: DOCUMENTATION & CLEANUP (Est: 1-2h)

### Task 6.1: Create Architecture Decision Record
**Action:** Document the migration

**Create:** `docs/ADR-002-three-layer-architecture.md`

**Content:**
```markdown
# ADR 002: Three-Layer Architecture

## Status
Implemented (BLOCKER #2)

## Context
We had 92 try/except ImportError workarounds due to circular dependencies.
System was fragile and couldn't scale.

## Decision
Implement 3-layer architecture:
- Layer 1: Protocol definitions (vibe_core/protocols/)
- Layer 2: Implementations
- Layer 3: Dynamic wiring (PhoenixConfigEngine + phoenix.yaml)

## Consequences
- ✅ Zero circular dependencies
- ✅ Clean separation of concerns
- ✅ Easy to test
- ✅ Easy to extend
- ⚠️ More indirection (acceptable trade-off)

## Implementation
See BLOCKER2_HAIKU_PLAN.md for details.
```

**Validation:**
- [ ] ADR created
- [ ] Decision documented
- [ ] Context clear
- [ ] Consequences listed

---

### Task 6.2: Update Developer Guidelines
**Action:** Add layer architecture rules

**Create/Update:** `docs/DEVELOPER_GUIDELINES.md`

**Add section:**
```markdown
## Layer Architecture Rules

### Layer 1: Protocols (vibe_core/protocols/)
- ✅ Abstract base classes only
- ✅ Can import: stdlib, abc, typing
- ❌ NEVER import from Layer 2 or 3
- ❌ NO implementations

### Layer 2: Implementations
- ✅ Import protocols from Layer 1
- ✅ Implement business logic
- ❌ NO cross-imports between implementations
- ❌ NO wiring logic

### Layer 3: Wiring (phoenix_config.py + phoenix.yaml)
- ✅ Import from Layer 1 and 2
- ✅ Wire implementations to protocols
- ✅ Configure system

### Rule: If you add try/except ImportError, you're doing it wrong.
### Rule: If you have circular imports, you violated layer separation.
```

**Validation:**
- [ ] Guidelines updated
- [ ] Rules clear
- [ ] Examples provided
- [ ] Consequences explained

---

### Task 6.3: Update README
**Action:** Note architectural change

**Update:** `README.md`

**Add section:**
```markdown
## Architecture

This project uses a 3-layer architecture:

1. **Layer 1: Protocols** (`vibe_core/protocols/`)
   - Abstract interfaces (ABCs)
   - No implementations

2. **Layer 2: Implementations**
   - Business logic
   - Agent implementations
   - Ledger implementations

3. **Layer 3: Wiring** (`vibe_core/phoenix_config.py`)
   - Dynamic configuration
   - Dependency injection
   - See `config/phoenix.yaml`

This eliminates circular dependencies and enables clean testing.
```

**Validation:**
- [ ] README updated
- [ ] Architecture explained
- [ ] Easy for new developers to understand

---

### Task 6.4: Clean Up Migration Artifacts
**Action:** Remove temporary migration files

**Files to keep:**
```
migration/
├── protocol_inventory.txt      # Historical record
├── import_map.txt              # Reference
├── tryexcept_breakdown.txt     # What we fixed
└── tryexcept_removal_log.txt   # How we fixed it
```

**Files to archive (move to docs/migration_history/):**
- All grep outputs
- Temporary notes

**Validation:**
- [ ] Migration files organized
- [ ] Historical record preserved
- [ ] Clutter removed

---

### Task 6.5: Update HONEST_PLAN.md Status
**Action:** Mark BLOCKER #2 complete

**Edit:** `HONEST_PLAN.md`

**Change:**
```markdown
### BLOCKER #2 ✅ - COMPLETE
- ✅ Layer 1 protocols created
- ✅ Layer 2 reorganized
- ✅ Layer 3 PhoenixConfigEngine written
- ✅ phoenix.yaml created
- ✅ 92 try/except ImportError workarounds REMOVED
- ✅ Circular imports fixed
```

**Validation:**
- [ ] Status updated
- [ ] Accurate reflection of completion
- [ ] Ready for BLOCKER #3

---

## SUCCESS CRITERIA

BLOCKER #2 is complete when ALL of the following are true:

### Code Quality
- [ ] Zero try/except ImportError in codebase
- [ ] Zero circular import errors
- [ ] All protocols in vibe_core/protocols/
- [ ] All implementations import from Layer 1
- [ ] Phoenix engine works

### Testing
- [ ] All existing tests still pass
- [ ] Import order tests pass
- [ ] Smoke tests pass
- [ ] Server starts successfully
- [ ] Agents operational

### Documentation
- [ ] ADR created
- [ ] Developer guidelines updated
- [ ] README updated
- [ ] Migration artifacts organized

### Validation Commands
```bash
# 1. Zero try/except
grep -r "except ImportError" vibe_core/ steward/ provider/ --include="*.py" | wc -l
# Expected: 0

# 2. Tests pass
pytest tests/ -v
# Expected: All pass

# 3. Server starts
python run_server.py
# Expected: No errors

# 4. Phoenix works
python -c "from vibe_core.phoenix_config import get_phoenix_engine; e = get_phoenix_engine(); print(len(e.wire_agents()))"
# Expected: 13
```

---

## ROLLBACK PLAN

If something goes catastrophically wrong:

### Emergency Rollback
```bash
git stash
git checkout main
git checkout -b blocker2-rollback
git cherry-pick <last-known-good-commit>
```

### Partial Rollback
If only some files are broken:
```bash
git checkout HEAD~1 -- path/to/broken/file.py
```

### Recovery Strategy
1. Identify what broke
2. Check migration logs
3. Revert specific changes
4. Test incrementally
5. Re-apply carefully

---

## ESTIMATED TIMELINE

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1 | Protocol Audit | 1-2h |
| Phase 2 | Layer 1 Creation | 2-3h |
| Phase 3 | Layer 2 Updates | 4-6h |
| Phase 4 | Layer 3 Phoenix | 2-3h |
| Phase 5 | Validation | 2-3h |
| Phase 6 | Documentation | 1-2h |
| **TOTAL** | | **12-19h** |

Realistic estimate: **15 hours**

---

## NEXT STEPS AFTER BLOCKER #2

Once complete, you can proceed to:

**BLOCKER #3: Real Agent Wiring**
- Replace MockAgent defaults
- Wire real agents throughout system
- Full integration testing

Estimated effort: 4-6 hours
Prerequisites: ✅ BLOCKER #2 complete

---

## HAIKU-SPECIFIC TIPS

This plan is optimized for Claude Haiku execution:

1. **One task at a time** - Don't jump ahead
2. **Validate each step** - Check before proceeding
3. **Track progress** - Use checkboxes
4. **If stuck** - Check validation criteria
5. **Ask for help** - If validation fails

**Parallel execution is OK for:**
- Phase 1 tasks (all can run together)
- Phase 2.2-2.4 (protocol file creation)
- Phase 3.1-3.5 (file updates, track count)

**Sequential execution required for:**
- Phase 2 → Phase 3 (need protocols before updating imports)
- Phase 3 → Phase 4 (need clean imports before Phoenix)
- Phase 4 → Phase 5 (need Phoenix before testing)

---

**END OF PLAN**
