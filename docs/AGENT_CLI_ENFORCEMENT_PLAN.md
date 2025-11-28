# AGENT CLI ENFORCEMENT PLAN

**Status:** In Progress - Phase 2.2 COMPLETE
**Goal:** Stop agents from hallucinating requirements.txt and direct filesystem access
**Strategy:** Bridge Kernel capabilities to Agents via System Interface

---

## PROBLEM

Agents bypass Kernel isolation:
- Herald creates `requirements.txt` (ignores pyproject.toml)
- 11/13 agents use direct `Path("data/...")` (bypass VFS)
- No standardized way to add dependencies or access config

**Root Cause:** Kernel has all tools (VFS, Config, Isolation) but no Agent-facing API.

---

## SOLUTION: 3-Phase Architecture Bridge

### Phase 1: KERNEL EXTENSION
**1.1 Dependency Manager** (`vibe_core/dependency_manager.py`)
- Read/Write pyproject.toml via **tomlkit** (preserves comments/formatting)
- Methods: `add_dependency()`, `get_dependencies()`, `remove_dependency()`

**1.2 Agent System Interface** (`vibe_core/agent_interface.py`)
- Injected as `agent.system` in every agent
- Provides: dependency mgmt, VFS I/O, config access
- Methods: `system.add_dependency()`, `system.write_file()`, `system.get_config()`

**1.3 Kernel Injection** (Update `kernel_impl.py:register_agent`)
- Inject `agent.system = AgentSystemInterface(kernel, agent_id)`
- All agents auto-receive system interface on registration

### Phase 2: AGENT MIGRATION
**2.1 Herald** - Migrate requirements.txt → system.add_dependency()
**2.2 Forum/Civic** - Migrate Path() → system.write_file()
**2.3 All Agents** - Use system.get_config() for config access

### Phase 3: ENFORCEMENT
**3.1 Pre-Commit Hook** - Block requirements.txt and direct Path("data/")
**3.2 CI/CD Check** - Enforce agent standards (line count, API usage)
**3.3 Scribe Templates** - Move to Jinja2 (separate task)

---

## CRITICAL DECISION

✅ **Use tomlkit NOT standard toml**
Standard parsers destroy formatting/comments → repo becomes unreadable.
tomlkit preserves structure → maintainable pyproject.toml.

---

## EXECUTION ORDER

1. ✅ Build DependencyManager (Backend) - `vibe_core/dependency_manager.py`
2. ✅ Define AgentSystemInterface (The Bridge) - `vibe_core/agent_interface.py`
3. ✅ Activate Kernel Injection (The Enforcement) - `kernel_impl.py:365-375`
4. ✅ Migrate Herald (Proof of Concept) - `steward/system_agents/herald/`
   - Dependencies in pyproject.toml ✅
   - requirements.txt DELETED ✅
   - EventLog sandboxed via system.get_sandbox_path() ✅
5. ✅ Migrate high-risk agents (Phase 2.2)
   - Forum: 4 paths sandboxed (proposals, votes, executed, ledger) ✅
   - Civic: 3 paths sandboxed (registry, agents_md, state) ✅
   - Science: 2 paths sandboxed (cache, results) ✅
   - Total: 9 filesystem violations eliminated ✅
6. ⏳ Roll out to remaining 10 agents
7. ⏳ Enable enforcement hooks

**Status:** Phase 2.2 COMPLETE ✅ (4/14 agents migrated)
**Next:** Phase 2.3+ - Migrate remaining 10 agents (Engineer, Oracle, Envoy, Archivist, Auditor, Chronicle, Watchman, Supreme Court, Scribe, Discoverer)
