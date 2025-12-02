# SOLID HARDENING PLAN
**Version:** 1.0
**Status:** APPROVED FOR EXECUTION
**Created:** 2025-11-30
**Philosophy:** VIMANA RANGE ROVER - Runs everywhere, on everything.

---

## Executive Summary

This plan addresses **security vulnerabilities**, **credibility gaps**, and **completeness issues** identified through deep code analysis. The goal is to make Steward Protocol **SOLID** - not just functional, but trustworthy and professional.

**Key Principle:** All changes must preserve the VIMANA guarantee: "Clone. Run. Done." No lock files, no vendor-specific tooling, no breaking universal compatibility.

---

## TIER 0: CRITICAL SECURITY (P0)

These are **exploitable vulnerabilities** that must be fixed before any deployment.

### 0.1 Remove "genesis_hash" Bypass

**File:** `steward/constitutional_oath.py:127-131`

**Current Code (VULNERABLE):**
```python
if stored_hash == "genesis_hash":
    logger.warning("⚠️ Allowing GENESIS_HASH bypass for bootstrapping")
    return True, "Genesis Bootstrap Authorized"
```

**Problem:** Any agent can bypass oath verification by using the literal string `"genesis_hash"` as their constitution_hash. This completely undermines the Constitutional Oath system.

**Who Uses This Bypass:**
- `steward/system_agents/discoverer/agent.py:49-54` - Discoverer agent
- `steward/system_agents/discoverer/agent.py:221-228` - GenericAgent placeholder

**Fix Options:**
1. **Remove entirely** - Force all agents to swear real oaths
2. **Environment-gated** - Only allow in `STEWARD_DEV_MODE=true`
3. **Time-limited** - Bootstrap period expires after first real oath

**Recommended:** Option 2 (Environment-gated) for development flexibility while securing production.

**Effort:** 30 minutes

---

### 0.2 Implement Actual Signature Verification

**File:** `steward/constitutional_oath.py:93-142`

**Current Code (BROKEN):**
```python
def verify_oath(oath_event: Dict[str, Any], identity_tool: Any) -> Tuple[bool, str]:
    # ... hash verification happens ...
    # BUT identity_tool is NEVER USED
    # Signatures are NEVER VERIFIED
    return True, "Oath is valid"  # Just trusts the hash match
```

**Problem:** The `identity_tool` parameter is accepted but never called. Signatures in oath events are completely ignored. Anyone can forge an oath.

**Fix:**
```python
# After hash verification passes:
if identity_tool and hasattr(identity_tool, 'verify_signature'):
    signature = oath_event.get("signature_full") or oath_event.get("signature")
    message = stored_hash  # The constitution hash that was signed

    if not identity_tool.verify_signature(message, signature):
        return False, "❌ Signature verification failed"
```

**Effort:** 1 hour

---

### 0.3 Make Oath Enforcement Mandatory

**File:** `vibe_core/kernel_impl.py:63-71`

**Current Code (SILENT FAILURE):**
```python
try:
    from vibe_core.bridge import ConstitutionalOath
    OATH_ENFORCEMENT_AVAILABLE = True
except ImportError:
    OATH_ENFORCEMENT_AVAILABLE = False
    logger_setup.warning("⚠️  Constitutional Oath not available - governance gate disabled")
```

**Problem:** If the import fails (missing file, syntax error, etc.), oath enforcement is **silently disabled**. The system continues running without security.

**Fix:**
```python
try:
    from vibe_core.bridge import ConstitutionalOath
    OATH_ENFORCEMENT_AVAILABLE = True
except ImportError as e:
    # In production, this should be fatal
    if os.environ.get("STEWARD_REQUIRE_OATH", "true").lower() == "true":
        raise RuntimeError(f"CRITICAL: Constitutional Oath module required but failed to load: {e}")
    else:
        OATH_ENFORCEMENT_AVAILABLE = False
        logger_setup.warning("⚠️  Constitutional Oath disabled (STEWARD_REQUIRE_OATH=false)")
```

**Effort:** 15 minutes

---

## TIER 1: CREDIBILITY (P1)

These issues don't break security but **destroy trust** with contributors and users.

### 1.1 Add Virtual Environment Support to boot.py

**File:** `boot.py`

**Current State:** Installs system-wide with `--system` flag (uv) or directly (pip).

**Problem:**
- Pollutes system Python
- Can conflict with other projects
- Scares away experienced Python developers
- Unprofessional for a serious project

**Fix:** Add `--venv` flag (OPTIONAL, not default to preserve VIMANA):
```python
def ensure_venv():
    """Create and activate venv if --venv flag passed."""
    venv_path = PROJECT_ROOT / ".venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    # Return the venv's Python executable
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"
```

**Usage:**
- `python boot.py` - Works as before (VIMANA mode)
- `python boot.py --venv` - Creates/uses .venv (Professional mode)

**Effort:** 1 hour

---

### 1.2 Delete Orphan requirements.txt Files

**Files to DELETE:**
```
agent_city/registry/ambassador/requirements.txt
agent_city/registry/lens/requirements.txt
agent_city/registry/pulse/requirements.txt
examples/herald/requirements.txt
```

**Problem:** These files are WRONG. The project uses `pyproject.toml` as single source of truth. Orphan requirements.txt files:
- Confuse contributors
- May have outdated/conflicting versions
- Violate the project's own architecture

**Fix:** Delete them. If sub-modules need dependencies, they should be in pyproject.toml `[project.optional-dependencies]`.

**Effort:** 5 minutes

---

### 1.3 Fix Herald's False "strategy" Capability

**Files:**
- `steward/system_agents/herald/steward.json:16-18`
- `steward/system_agents/herald/cartridge_main.py:92`

**Current (LIE):**
```json
{
  "name": "strategy",
  "description": "strategy operation"
}
```

**Problem:** Herald declares it can do "strategy" but there is:
- No strategy capability module in `herald/capabilities/`
- No strategy tool in `herald/tools/`
- No code implementing strategy operations

This is a **false advertisement** that breaks trust.

**Fix:** Remove "strategy" from capabilities list.

**Effort:** 15 minutes

---

### 1.4 Fix Chronicle's False Capabilities

**Files:**
- `steward/system_agents/chronicle/steward.json:8-15`
- `steward/system_agents/chronicle/cartridge_main.py:81-85`

**Current (LIES):**
```json
{
  "name": "ledger",
  "description": "ledger operation"
},
{
  "name": "orchestration",
  "description": "orchestration operation"
}
```

**Problem:** Chronicle declares "ledger" and "orchestration" capabilities but:
- The only tool is `chronicle.git` (Git operations)
- No ledger tool exists
- No orchestration tool exists
- Comments say "Records to immutable ledger" but the code doesn't do this

**Fix:** Remove "ledger" and "orchestration" from capabilities. Keep only "content_generation" (which maps to git commit operations).

**Effort:** 15 minutes

---

## TIER 2: COMPLETENESS (P2)

These expose the architecture's power to users.

### 2.1 Add `--agent` Flag to CLI Task Command

**File:** `bin/agent-city`

**Current:**
```bash
agent-city task add "description" -p 50 -r roadmap
```

**Problem:** Fractal routing is fully implemented in code (`TaskManager.add_task(assigned_agent=...)`) but CLI doesn't expose it. Users can't assign tasks to specific agents.

**Fix:** Add `--agent` / `-a` flag:
```python
task_add.add_argument("-a", "--agent",
    help="Assign to specific agent (e.g., herald, civic, science)")
```

Update `cmd_task_add`:
```python
task = tm.add_task(
    title=args.description,
    priority=args.priority,
    roadmap_id=roadmap_id,
    assigned_agent=getattr(args, 'agent', None)
)
```

**Effort:** 30 minutes

---

### 2.2 Add `agent list` Command to CLI

**File:** `bin/agent-city`

**Problem:** Users can't see available agents without reading code.

**Fix:** Add new command:
```python
def cmd_agent_list(args):
    """List available agents from topology."""
    from vibe_core.topology import get_topology

    topology = get_topology()
    print("Available Agents:\n")

    for varsha in topology.varshas:
        for agent in varsha.agents:
            authority = 10 - varsha.ring_number  # Higher ring = lower authority
            print(f"  {agent.id:12} | Authority {authority} | {agent.domain}")

    return 0
```

Add to parser:
```python
agent_parser = subparsers.add_parser("agent")
agent_subparsers = agent_parser.add_subparsers(dest="agent_command")
agent_list = agent_subparsers.add_parser("list")
agent_list.set_defaults(func=cmd_agent_list)
```

**Effort:** 30 minutes

---

### 2.3 Improve Task List Output

**File:** `bin/agent-city:42-68`

**Current Output:**
```
⏳ P50: Fix the bug
```

**Problem:** Doesn't show which agent a task is assigned to, even though the data exists.

**Fix:**
```python
for task in tasks[:10]:
    status_icon = {...}
    agent_str = f" → {task.assigned_agent}" if getattr(task, 'assigned_agent', None) else ""
    routing_str = f" [{task.routing_priority}]" if getattr(task, 'routing_priority', None) else ""
    print(f"  {status_icon} P{task.priority}: {task.title}{agent_str}{routing_str}")
```

**Effort:** 15 minutes

---

## TIER 3: CLEANUP (P3)

Nice to have, not blocking.

### 3.1 Add More Playbooks

**Directory:** `knowledge/playbooks/`

**Current:** 4 playbooks (content_generation, governance_vote, project_scaffold, feature_implement_safe)

**Opportunity:** The deterministic executor is powerful but underutilized. More playbooks = more LLM-free operations.

**Suggested Additions:**
- `bug_fix.yaml` - Standard bug investigation workflow
- `code_review.yaml` - Review checklist execution
- `deploy.yaml` - Deployment workflow

**Effort:** 2-4 hours per playbook

---

## Execution Order

```
PHASE 1: Security (MUST DO FIRST)
├── [P0.1] Remove genesis_hash bypass
├── [P0.2] Implement signature verification
└── [P0.3] Make oath enforcement mandatory

PHASE 2: Credibility (Parallel-safe)
├── [P1.1] Add --venv support to boot.py
├── [P1.2] Delete orphan requirements.txt files
├── [P1.3] Fix herald false capabilities
└── [P1.4] Fix chronicle false capabilities

PHASE 3: Completeness (After P1)
├── [P2.1] Add --agent flag to CLI
├── [P2.2] Add agent list command
└── [P2.3] Improve task list output

PHASE 4: Polish (Optional)
└── [P3.1] Add more playbooks
```

---

## Time Estimates

| Tier | Tasks | Estimated Time |
|------|-------|----------------|
| P0 Security | 3 tasks | 1.75 hours |
| P1 Credibility | 4 tasks | 1.5 hours |
| P2 Completeness | 3 tasks | 1.25 hours |
| **Total (P0-P2)** | **10 tasks** | **4.5 hours** |

---

## Verification Checklist

After implementation, verify:

- [ ] `python boot.py --check` passes
- [ ] `python boot.py --venv --check` creates .venv and passes
- [ ] Oath verification rejects forged signatures
- [ ] Oath verification rejects "genesis_hash" in production mode
- [ ] `agent-city agent list` shows all 13 agents
- [ ] `agent-city task add "test" --agent herald` assigns to herald
- [ ] No requirements.txt files exist in project
- [ ] Herald manifest only declares: content_generation, broadcasting, research
- [ ] Chronicle manifest only declares: content_generation
- [ ] All existing tests pass: `pytest tests/`

---

## Notes

### Why No Lock Files?

Lock files (uv.lock, poetry.lock, requirements.lock) would break the **VIMANA RANGE ROVER** principle:

> "Clone. Run. Done. Works on Windows, Linux, Mac. Tries uv → pip automatically."

Lock files require specific tooling:
- `uv.lock` needs uv installed
- `poetry.lock` needs poetry installed
- `requirements.lock` needs pip-tools installed

The current approach with `>=` version specs in `pyproject.toml` ensures the project runs on ANY system with Python 3.8+ and ANY package installer.

For CI reproducibility, lock files can be generated **in CI** without being committed.

### Why Keep System-Wide Install as Default?

The `--venv` flag is optional because:
1. CI environments are ephemeral (system-wide is fine)
2. Docker containers are isolated (system-wide is fine)
3. Quick testing shouldn't require venv setup
4. VIMANA = "Clone. Run. Done." - no extra steps

Professional developers can use `--venv`. Casual users get simplicity.

---

## Appendix: Files to Modify

```
SECURITY (P0):
├── steward/constitutional_oath.py      [MODIFY: lines 127-131, 93-142]
└── vibe_core/kernel_impl.py            [MODIFY: lines 63-71]

CREDIBILITY (P1):
├── boot.py                             [MODIFY: add --venv support]
├── agent_city/registry/ambassador/requirements.txt  [DELETE]
├── agent_city/registry/lens/requirements.txt        [DELETE]
├── agent_city/registry/pulse/requirements.txt       [DELETE]
├── examples/herald/requirements.txt                 [DELETE]
├── steward/system_agents/herald/steward.json        [MODIFY: remove strategy]
├── steward/system_agents/herald/cartridge_main.py   [MODIFY: line 92]
├── steward/system_agents/chronicle/steward.json     [MODIFY: remove ledger, orchestration]
└── steward/system_agents/chronicle/cartridge_main.py [MODIFY: lines 81-85]

COMPLETENESS (P2):
└── bin/agent-city                      [MODIFY: add --agent, agent list, improve output]
```

---

*Plan created by deep code analysis. All line numbers verified against actual source.*
