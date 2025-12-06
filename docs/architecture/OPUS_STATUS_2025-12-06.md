# OPUS STATUS - 2025-12-06

> **Purpose:** Single source of truth for where we are in "Der Totale Krieg"
> **Previous:** OPUS_WORKING_DOC.md, OPUS_PANOPTICON_NANO_AGENTS.md
> **Reference:** MASTER_PLAN_V4.1_FINAL.md, ARCHITECTURE_NEXT.md

---

## EXECUTIVE SUMMARY

| Battle | Status | Notes |
|--------|--------|-------|
| **STEWARD Protocol Plugin** | ✅ COMPLETE | All hooks, trust, attestation, delegation |
| **PANOPTICON+ Nano Agents** | ✅ COMPLETE | CircuitLoader, 8 handlers, pre-commit, CI/CD |
| **PlaybookLoader/Executor** | ✅ COMPLETE | Layer 3 deterministic execution |
| **UnifiedLoader Base** | ✅ COMPLETE | VEDA-4 pattern for all loaders |
| **Plugin Folder Migration** | ❌ PENDING | 10 plugins need folder structure |
| **Cartridge Consolidation** | ❌ PENDING | steward/ + agent_city/ → vibe_core/cartridges/ |
| **CLI as Plugin** | ❓ DECISION NEEDED | See analysis below |

---

## 1. WHAT'S DONE (Don't touch!)

### 1.1 Kernel Hooks (ETERNAL - Never change again)

```
Lifecycle:  on_boot, on_tick_pre, on_tick_post, on_shutdown
Agent:      on_agent_registered, on_agent_unregistered
Task:       on_task_submit (COSMIC GATE), on_task_pre_assign (GOVERNANCE GATE)
            on_task_completed, on_task_failed
Capability: on_capability_check (CAPABILITY GATE)
Tool:       on_tool_execute (TOOL GATE), on_tool_executed
```

### 1.2 STEWARD Protocol Plugin (vibe_core/plugins/steward_protocol.py)

- ✅ Capabilities from steward.json granted on agent registration
- ✅ Trust scores tracked (completed/failed tasks)
- ✅ Attestation API (attest, has_attestation, requires_attestation)
- ✅ Delegation API (delegate, can_delegate_to)
- ✅ Strict mode API
- ✅ on_capability_check hook integration

### 1.3 PANOPTICON+ Test Validation

- ✅ CircuitLoader (knowledge/circuits/*.yaml)
- ✅ TestValidationCircuitExecutor
- ✅ 8 Nano Agent handlers (ast_parse, pattern_match, etc.)
- ✅ TestValidationTool (for Watchman agent)
- ✅ Pre-commit Guard 5
- ✅ GitHub Actions CI/CD (Layer 4)
- ✅ Miniaturwunderland fixtures (TestAgents, TestKernel)

### 1.4 PlaybookLoader & DeterministicPlaybookExecutor

- ✅ PlaybookLoader in vibe_core/loaders/
- ✅ DeterministicPlaybookExecutor in test_orchestration
- ✅ Topological sort for DAG execution
- ✅ Handler registry for deterministic actions
- ✅ Loop support for enhancement iterations

---

## 2. WHAT'S IN PROGRESS

### 2.1 Test Fixture Migration (Gemini doing this)

**Task File:** `docs/reports/GEMINI_TEST_MIGRATION.md`

```
Current State:
  BLOCKED: 0
  WARNED: 33  ← Tech debt, Gemini migrating these
  PASSED: 39
```

### 2.2 Unmerged Branches (14 remain)

```
origin/claude/agent-veda4-integration-*
origin/claude/architecture-cleanup-*
origin/claude/fix-workflow-*
... etc
```

**Decision needed:** Review and delete or salvage.

---

## 3. WHAT'S PENDING (The Grand Vision)

### 3.1 Plugin Folder Migration (ARCHITECTURE_NEXT.md Phase 2)

**Current:** 10 plugins as single .py files
**Target:** Each plugin as folder with manifest.json + plugin_main.py + config.yaml

| Plugin | Priority | Complexity |
|--------|----------|------------|
| steward_protocol | 🔴 CRITICAL | Already complex, HIGH |
| vedic_governance | 🟡 MEDIUM | Core logic |
| sarga_cycle | 🟡 MEDIUM | Scheduler gating |
| test_mode | 🟡 MEDIUM | Global state issues |
| test_orchestration | 🟢 LOW | Already folder structure! |
| envoy_ui | 🟢 LOW | Interface only |
| ephemeral_ui | 🟢 LOW | Interface only |
| settings_ui | 🟢 LOW | Interface only |
| git_history | 🟢 LOW | Analytics only |

**NOTE:** test_orchestration is ALREADY a folder! It's the example to follow.

### 3.2 Cartridge Consolidation (MASTER_PLAN_V4.1_FINAL.md)

**The Big Move:**
```
steward/system_agents/    → vibe_core/cartridges/system/
agent_city/registry/      → vibe_core/cartridges/agent_city/
```

**Why:** CODE lives in vibe_core/, not scattered around root.

**Blockers:**
- AgentLoader hardcodes scan paths
- Many imports reference old paths
- Need to update steward.json discovery

### 3.3 CLI Question

**User asked:** "should we also get the cli as plugin?"

**Analysis:**

| Approach | Pros | Cons |
|----------|------|------|
| CLI as Entry Point (current) | Simple, works | Not pluggable |
| CLI as Plugin | Pluggable commands | Chicken/egg: who loads the plugin loader? |
| CLI calls Plugins | Commands delegate to plugins | Best of both worlds |

**Recommendation:** Keep CLI as entry point (`vibe_core/cli.py`), but have commands delegate to plugins for actual work.

```python
# vibe_core/cli.py
@click.command()
def verify():
    # Delegate to steward_protocol plugin
    kernel.steward.verify_all()

@click.command()
def validate_tests():
    # Delegate to test_orchestration plugin
    from vibe_core.plugins.test_orchestration import validate_test_files
    validate_test_files(...)
```

---

## 4. TECH DEBT INVENTORY

### 4.1 Critical (Blocks Progress)

| Issue | Location | Impact |
|-------|----------|--------|
| 33 tests use old patterns | tests/**/*.py | WARNED but not blocked |
| PlaybookExecutor handlers are stubs | playbook_executor.py | No real pytest integration |

### 4.2 High (Should Fix Soon)

| Issue | Location | Impact |
|-------|----------|--------|
| Plugins are single files | vibe_core/plugins/*.py | No manifest, no config |
| AgentLoader hardcoded paths | vibe_core/steward/loader.py | Blocks cartridge move |
| 14 unmerged branches | origin/claude/* | Clutter, possible lost work |

### 4.3 Medium (Nice to Have)

| Issue | Location | Impact |
|-------|----------|--------|
| SectionLoader not using UnifiedLoader | phoenix/section_loader.py | Inconsistent pattern |
| No hot-reload for plugins | PluginLoader | Dev experience |
| TestGuardian has __init__ | test_guardian.py:104 | pytest warning |

---

## 5. DECISION LOG

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-05 | Kernel hooks are ETERNAL | Vishnu is immutable |
| 2025-12-05 | UnifiedLoader is the pattern | Fraktal consistency |
| 2025-12-06 | CLI stays as entry point | Simplicity, no chicken/egg |
| 2025-12-06 | test_orchestration is the folder example | Already structured |

---

## 6. NEXT ACTIONS (Priority Order)

### For OPUS (Deep Architecture)

1. **Review unmerged branches** - Decide delete vs salvage
2. **Plan cartridge consolidation** - Update AgentLoader scan paths
3. **Phoenix fraktal alignment** - Sections as folders?

### For GEMINI (Bulk Work)

1. **Finish 33 test migrations** - In progress
2. **Plugin folder migration** - Convert .py → folders
   - Start with sarga_cycle (simple)
   - Then vedic_governance
   - Then UI plugins (envoy, ephemeral, settings, git_history)

### For SONNET (Repetitive Tasks)

1. **Update imports after cartridge move** - Mechanical
2. **Add manifest.json to each plugin folder** - Template copy

---

## 7. THE FRAKTAL VISION (Where We're Going)

```
steward-protocol/
├── vibe_core/                  # ══════ CODE ══════
│   ├── kernel_impl.py          # Vishnu (immutable)
│   ├── loaders/                # UnifiedLoader pattern
│   ├── plugins/                # ALL plugins as folders
│   │   ├── steward_protocol/
│   │   ├── vedic_governance/
│   │   ├── test_orchestration/ ✅ DONE
│   │   └── ...
│   ├── cartridges/             # ALL agents
│   │   ├── system/             # ex steward/system_agents/
│   │   └── agent_city/         # ex agent_city/registry/
│   └── runtime/                # ex services/
│
├── knowledge/                  # ══════ CONFIG ══════
│   ├── circuits/               ✅ DONE
│   ├── playbooks/              ✅ DONE
│   ├── concepts/
│   └── intents/
│
└── data/                       # ══════ RUNTIME ══════ (gitignored)
    ├── ledger/
    ├── cache/
    └── models/
```

---

## 8. METRICS

| Metric | Current | Target |
|--------|---------|--------|
| Tests passing | ~374 | 374+ |
| Tests BLOCKED | 0 | 0 |
| Tests WARNED | 33 | 0 |
| Plugins as folders | 1 | 10 |
| Loaders using UnifiedLoader | 2 | 5 |
| Root-level directories | ~20 | 6 |

---

*Last updated: 2025-12-06*
*Next review: After Gemini completes test migration*
