# 🔥 PHOENIX PROTOCOL - PHASE 2 INSTRUCTIONS

**For:** Haiku (Implementation Agent)
**Date:** 2025-11-27
**Priority:** P1 - HIGH
**Estimated Time:** 2-3 days

---

## 🎯 MISSION

Port remaining OS components from vibe-agency to complete the unified VibeOS 1.5 system.

**WHAT WE'RE MERGING:**
- Runtime system (providers, oracle, safety guards)
- Playbook engine (workflow execution)
- Specialists (planning, coding, testing agents)
- Store (data persistence layer)
- Tools (file ops, search, etc.)
- LLM adapters

---

## 📋 PREREQUISITE

Phase 1 must be complete:
- ✅ task_management/ ported
- ✅ identity.py ported
- ✅ CLI working
- ✅ system-boot.sh ported

**Current branch:** `claude/phoenix-integration-plan-01EfJY2MjMTnFmptKK3wKMFc`

---

## ✅ TASK 1: Port runtime/ System

**Source:** `/home/user/vibe-agency/vibe_core/runtime/`
**Target:** `/home/user/steward-protocol/vibe_core/runtime/`

**What's in runtime/:**
```
runtime/
├── providers/            # LLM provider adapters
│   ├── chain_provider.py
│   ├── google_provider.py
│   └── steward_provider.py
├── oracle.py             # Kernel introspection
├── tool_safety_guard.py  # Tool execution safety
├── prompt_context.py     # Dynamic prompt compilation
└── interface.py          # Interface manager
```

**Steps:**
1. Copy entire directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/runtime/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Check for conflicts:
   - steward-protocol might already have `runtime/` or similar
   - If exists, merge carefully (don't overwrite Agent City code)

3. Update imports:
   - Test: `python -c "from vibe_core.runtime.oracle import KernelOracle; print('✅')"`

4. Integrate with existing provider:
   - steward-protocol has `provider/universal_provider.py`
   - Keep both, make them work together

**Success Criteria:**
- ✅ runtime/ directory exists
- ✅ No import errors
- ✅ Oracle can introspect kernel

---

## ✅ TASK 2: Port playbook/ Engine

**Source:** `/home/user/vibe-agency/vibe_core/playbook/`
**Target:** `/home/user/steward-protocol/vibe_core/playbook/`

**What's in playbook/:**
```
playbook/
├── tasks/          # Task definitions
├── workflows/      # Workflow definitions
└── engine.py       # Execution engine
```

**Steps:**
1. Copy directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/playbook/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Check conflicts:
   - steward-protocol has `knowledge/playbooks/` (different!)
   - Keep both - one is system playbooks, one is knowledge playbooks

3. Test:
   ```python
   from vibe_core.playbook import PlaybookEngine
   print("✅ Playbook engine loaded")
   ```

**Success Criteria:**
- ✅ playbook/ exists
- ✅ No import errors
- ✅ Engine can load workflow definitions

---

## ✅ TASK 3: Port specialists/ Agents

**Source:** `/home/user/vibe-agency/vibe_core/specialists/`
**Target:** `/home/user/steward-protocol/vibe_core/specialists/`

**What's in specialists/:**
```
specialists/
├── planning_specialist.py   # Planning agent
├── coding_specialist.py     # Coding agent
├── testing_specialist.py    # Testing agent
└── specialist_factory.py    # Factory pattern
```

**Steps:**
1. Copy directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/specialists/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Integrate with Agent City:
   - These are SYSTEM agents (like CIVIC, HERALD)
   - They should be callable by Agent City agents
   - Keep separate from `steward/system_agents/`

3. Test:
   ```python
   from vibe_core.specialists import PlanningSpecialist
   agent = PlanningSpecialist()
   print(f"✅ Specialist: {agent.name}")
   ```

**Success Criteria:**
- ✅ specialists/ exists
- ✅ All 3 specialist agents load
- ✅ Factory can create specialists

---

## ✅ TASK 4: Port store/ Layer

**Source:** `/home/user/vibe-agency/vibe_core/store/`
**Target:** `/home/user/steward-protocol/vibe_core/store/`

**What's in store/:**
```
store/
├── artifact_store.py    # Artifact persistence
├── manifest_store.py    # Manifest storage
└── shadow_db.py         # SQLite shadow mode
```

**Steps:**
1. Copy directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/store/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Integrate with existing ledger:
   - steward-protocol has `ledger.py` (immutable audit trail)
   - store/ is for mutable data (artifacts, manifests)
   - Keep both - they serve different purposes

3. Test:
   ```python
   from vibe_core.store import ArtifactStore
   store = ArtifactStore(Path(".vibe/artifacts"))
   print("✅ Store initialized")
   ```

**Success Criteria:**
- ✅ store/ exists
- ✅ Can save/load artifacts
- ✅ Shadow DB works (SQLite fallback)

---

## ✅ TASK 5: Port tools/

**Source:** `/home/user/vibe-agency/vibe_core/tools/`
**Target:** `/home/user/steward-protocol/vibe_core/tools/`

**What's in tools/:**
```
tools/
├── read_file.py
├── write_file.py
├── search_file.py
├── list_directory.py
├── inspect_result.py
├── add_task.py       # Already have from task_management
├── list_tasks.py     # Already have
├── complete_task.py  # Already have
├── delegate.py
└── tool_registry.py
```

**Steps:**
1. Check what exists:
   ```bash
   ls -la /home/user/steward-protocol/vibe_core/tools/ 2>/dev/null
   ```

2. If doesn't exist, copy all:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/tools/ \
         /home/user/steward-protocol/vibe_core/
   ```

3. If exists, merge:
   - Keep steward-protocol tools
   - Add missing tools from vibe-agency
   - Don't duplicate task tools (already in task_management)

4. Test:
   ```python
   from vibe_core.tools import ToolRegistry, ReadFileTool
   registry = ToolRegistry()
   registry.register(ReadFileTool())
   print(f"✅ Tools: {len(registry)}")
   ```

**Success Criteria:**
- ✅ All file operation tools available
- ✅ ToolRegistry works
- ✅ No duplicates with task_management tools

---

## ✅ TASK 6: Port llm/ Adapters

**Source:** `/home/user/vibe-agency/vibe_core/llm/`
**Target:** `/home/user/steward-protocol/vibe_core/llm/`

**What's in llm/:**
```
llm/
├── chain_provider.py         # Provider chaining
├── google_adapter.py         # Google Gemini
├── smart_local_provider.py   # Offline provider
└── steward_provider.py       # Main provider
```

**Steps:**
1. Copy directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/llm/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Integrate with existing provider:
   - steward-protocol has `provider/universal_provider.py`
   - vibe-agency has `vibe_core/llm/steward_provider.py`
   - These might be the SAME thing (renamed)
   - Keep both, make them compatible

3. Test:
   ```python
   from vibe_core.llm import ChainProvider
   provider = ChainProvider()
   print("✅ LLM adapters loaded")
   ```

**Success Criteria:**
- ✅ llm/ exists
- ✅ All adapters load
- ✅ Compatible with existing universal_provider

---

## ✅ TASK 7: Port governance/ (InvariantChecker)

**Source:** `/home/user/vibe-agency/vibe_core/governance/`
**Target:** `/home/user/steward-protocol/vibe_core/governance/`

**What's in governance/:**
```
governance/
├── invariant_checker.py   # Soul governance rules
└── rules.yaml             # Rule definitions
```

**NOTE:** steward-protocol has `steward/constitutional_oath.py` (different!)

**Steps:**
1. Copy directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/governance/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Keep both governance systems:
   - InvariantChecker = Pre-flight checks (code quality, etc.)
   - Constitutional Oath = Agent identity verification
   - They complement each other

3. Test:
   ```python
   from vibe_core.governance import InvariantChecker
   soul = InvariantChecker("config/soul.yaml")
   print(f"✅ Soul: {soul.rule_count} rules")
   ```

**Success Criteria:**
- ✅ governance/ exists
- ✅ InvariantChecker works alongside Constitutional Oath
- ✅ No conflicts

---

## ✅ TASK 8: Port agents/ (Base classes)

**Source:** `/home/user/vibe-agency/vibe_core/agents/`
**Target:** `/home/user/steward-protocol/vibe_core/agents/`

**What's in agents/:**
```
agents/
├── llm_agent.py              # SimpleLLMAgent base class
├── specialist_factory.py     # Factory for specialists
└── system_maintenance.py     # Maintenance agent
```

**Steps:**
1. Copy directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/agents/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Check conflicts:
   - steward-protocol has `agent_protocol.py` (different!)
   - agent_protocol.py = Interface (VibeAgent base)
   - agents/ = Concrete implementations
   - Keep both

3. Test:
   ```python
   from vibe_core.agents import SimpleLLMAgent
   agent = SimpleLLMAgent(agent_id="test", name="Test")
   print(f"✅ Base agent: {agent.name}")
   ```

**Success Criteria:**
- ✅ agents/ exists
- ✅ SimpleLLMAgent loads
- ✅ No conflicts with agent_protocol.py

---

## ✅ TASK 9: Port config/ System

**Source:** `/home/user/vibe-agency/vibe_core/config/`
**Target:** `/home/user/steward-protocol/vibe_core/config/`

**What's in config/:**
```
config/
├── __init__.py
├── loader.py         # Config loader
└── schemas/          # Config schemas
```

**Steps:**
1. Check if exists:
   ```bash
   ls -la /home/user/steward-protocol/vibe_core/config/
   ```

2. If doesn't exist, copy:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/config/ \
         /home/user/steward-protocol/vibe_core/
   ```

3. If exists, merge carefully

4. Test:
   ```python
   from vibe_core.config import get_config
   config = get_config()
   print("✅ Config loaded")
   ```

**Success Criteria:**
- ✅ config/ exists
- ✅ Can load configuration
- ✅ No conflicts with existing config

---

## ✅ TASK 10: Update Dependencies

**File:** `/home/user/steward-protocol/pyproject.toml`

**Add missing dependencies from vibe-agency:**

Check `/home/user/vibe-agency/pyproject.toml`:
```toml
dependencies = [
    "pyyaml>=6.0.1",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "google-api-python-client>=2.100.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "psutil>=7.1.3",
    "rich>=13.0.0",
    "google-generativeai>=0.8.5",
    "jsonschema>=4.17.0",
]
```

Compare with steward-protocol pyproject.toml and add missing ones.

**Success Criteria:**
- ✅ All dependencies added
- ✅ `pip install -e .` works without errors

---

## 🚫 IMPORTANT: WHAT NOT TO DO

- ❌ **Do NOT refactor Agent City code** (keep HERALD, CIVIC, etc. as-is)
- ❌ **Do NOT modify vibe-agency code** (copy as-is)
- ❌ **Do NOT add new features**
- ❌ **Do NOT change existing functionality**
- ❌ **Do NOT delete Agent City innovations** (topology.py, narasimha.py, etc.)

---

## ✅ WHAT TO DO

- ✅ **Copy code from vibe-agency**
- ✅ **Merge with existing steward-protocol code**
- ✅ **Keep BOTH when they serve different purposes**
- ✅ **Test that everything loads**
- ✅ **Update imports as needed**

---

## 📊 SUCCESS CRITERIA (Phase 2 Complete)

When done:

```bash
# All modules load without errors
python -c "from vibe_core.runtime.oracle import KernelOracle; print('✅')"
python -c "from vibe_core.playbook import PlaybookEngine; print('✅')"
python -c "from vibe_core.specialists import PlanningSpecialist; print('✅')"
python -c "from vibe_core.store import ArtifactStore; print('✅')"
python -c "from vibe_core.tools import ToolRegistry; print('✅')"
python -c "from vibe_core.llm import ChainProvider; print('✅')"
python -c "from vibe_core.governance import InvariantChecker; print('✅')"
python -c "from vibe_core.agents import SimpleLLMAgent; print('✅')"
python -c "from vibe_core.config import get_config; print('✅')"

# CLI still works
bin/agent-city status
bin/agent-city task list

# Integration tests pass
pytest tests/integration/ -v
```

---

## 📝 COMMIT STRATEGY

**After each task, commit:**

```bash
git add vibe_core/runtime/
git commit -m "feat: Port runtime system from vibe-agency (Phase 2)"

git add vibe_core/playbook/
git commit -m "feat: Port playbook engine from vibe-agency (Phase 2)"

# etc. for each task
```

**Final commit:**
```bash
git commit -m "feat: Phoenix Protocol Phase 2 Complete - Full OS unification

Ported from vibe-agency:
- runtime/ (providers, oracle, safety guards)
- playbook/ (workflow engine)
- specialists/ (planning, coding, testing agents)
- store/ (data persistence)
- tools/ (file operations, search, etc.)
- llm/ (LLM adapters)
- governance/ (InvariantChecker)
- agents/ (base classes)
- config/ (configuration system)

All vibe-agency OS features now in steward-protocol.
Agent City innovations preserved (topology, narasimha, pulse, etc.)

Next: Phase 3 (cleanup & refactoring)"
```

---

## ⏱️ ESTIMATED TIME

- Task 1 (runtime): 3 hours
- Task 2 (playbook): 2 hours
- Task 3 (specialists): 2 hours
- Task 4 (store): 2 hours
- Task 5 (tools): 3 hours
- Task 6 (llm): 2 hours
- Task 7 (governance): 1 hour
- Task 8 (agents): 1 hour
- Task 9 (config): 1 hour
- Task 10 (dependencies): 1 hour

**Total: ~2-3 days focused work**

---

## 🆘 IF YOU GET STUCK

**Merge conflicts:**
- Keep BOTH versions if they serve different purposes
- Rename if needed (e.g., vibe_store vs city_store)

**Import errors:**
- Check sys.path includes project root
- Use absolute imports

**Duplicate functionality:**
- It's OK to have two similar things temporarily
- We'll clean up in Phase 3

---

## 🎯 DEFINITION OF DONE

Phase 2 is complete when:

1. ✅ All 10 tasks completed
2. ✅ All imports work
3. ✅ CLI still functional
4. ✅ Integration tests still pass
5. ✅ No regressions in Agent City
6. ✅ All code committed and pushed

---

**EXECUTE. Phase 2 starts now.** 🔥
