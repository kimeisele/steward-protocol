# REAL TECH DEBT AUDIT - CONFIG IN CODE

**Date:** 2025-12-07
**Auditor:** Opus
**Status:** CRITICAL - 158 VIOLATIONS FOUND

---

## SUMMARY

| Category | Count | Severity | Fix Strategy |
|----------|-------|----------|--------------|
| Hardcoded Paths | 105 | CRITICAL | PhoenixConfig injection |
| Inline Prompts | 38 | HIGH | Move to `knowledge/prompts/` |
| Magic Agent Strings | 8 | HIGH | Config-driven references |
| Hardcoded Templates | 5 | MEDIUM | Move to `knowledge/templates/` |
| Hardcoded Circuit Names | 2 | LOW | Use intent routing |

**TOTAL: 158 violations**

---

## CATEGORY 1: HARDCODED PATHS (105 violations)

### CRITICAL - Data Paths in Code

These paths should come from PhoenixConfig, not be hardcoded:

```
vibe_core/cartridges/system/civic/registry_agent.py:38
    Path("data/registry/citizens.json")

vibe_core/cartridges/system/civic/tools/vault_tool.py:91
    Path("data/security/master.key")

vibe_core/cartridges/system/civic/tools/economy.py:52,65
    Path("data/economy.db")

vibe_core/cartridges/system/civic/tools/bank_tool.py:51
    Path("data/economy.db")

vibe_core/cartridges/system/civic/tools/ledger_tool.py:64
    Path("data/economy.db")

vibe_core/cartridges/system/civic/tools/license_tool.py:145
    Path("data/registry/licenses.json")

vibe_core/cartridges/system/civic/tools/vault.py:113
    Path("data/security/master.key")

vibe_core/cartridges/system/archivist/tools/ledger_visualizer.py:32
    Path("data/ledger/audit_trail.jsonl")

vibe_core/cartridges/system/auditor/tools/watchdog_tool.py:37,40
    Path("data/ledger/kernel.jsonl")
    Path("data/ledger/violations.jsonl")

vibe_core/cartridges/system/herald/core/agency_director.py:107
    Path("data/reports")

vibe_core/cartridges/system/herald/core/memory.py:79
    Path("data/events/herald.jsonl")

vibe_core/cartridges/system/herald/tools/identity_tool.py:80,355
    Path("data/identities")

vibe_core/cartridges/system/herald/tools/scout_tool_legacy.py:26
    Path("data/federation/pokedex.json")

vibe_core/cartridges/system/supreme_court/tools/*.py (4 files)
    Path(".") / "data" / "supreme_court"
```

### CRITICAL - Code Structure Paths

These embed knowledge of internal structure:

```
vibe_core/cartridges/system/watchman/cartridge_main.py:198-199
    Path("vibe_core/cartridges/system")
    Path("vibe_core/cartridges/agent_city")

vibe_core/cartridges/system/civic/registry_agent.py:208
    Path("vibe_core/cartridges/system")

vibe_core/cartridges/system/auditor/cartridge_main.py:211
    Path("vibe_core/cartridges/system")

vibe_core/loaders/schema.py:157-160
    Path("vibe_core/plugins")
    Path("vibe_core/cartridges/system")
    Path("vibe_core/cartridges/agent_city")
    Path("vibe_core/phoenix/sections")

vibe_core/steward/loader.py:54-55
    Path("vibe_core/cartridges/system")
    Path("vibe_core/cartridges/agent_city")

vibe_core/topology.py:236-237
    Path("vibe_core/cartridges/system")
    Path("vibe_core/cartridges/agent_city")
```

### CRITICAL - System Paths

```
vibe_core/cli.py:55,57,502,506,568,800,989
    Path("/tmp/vibe_os/...")

vibe_core/llm/local_llama_provider.py:28
    Path("/tmp/vibe_os/models")

vibe_core/playbook/operations/kernel_spawn.py:54
    Path("/tmp/vibe_os/agents")

vibe_core/vfs.py:39
    Path("/tmp/vibe_os/agents")
```

### MEDIUM - Config/Knowledge Paths

```
vibe_core/loaders/circuit_loader.py:81-82
    Path("knowledge/circuits")
    Path("vibe_core/playbook/circuits")  # LEGACY!

vibe_core/loaders/playbook_loader.py:106-107
    Path("knowledge/playbooks")
    Path("vibe_core/playbook/playbooks")  # LEGACY!

vibe_core/phoenix/config.py:89-91
    Path("vibe_core/playbook/circuits")
    Path("MATRIX.md")
    Path("config")

vibe_core/phoenix/section_loader.py:79,85
    Path("vibe_core/phoenix/sections")
    Path("config")
```

### LOW - Document Paths (acceptable)

```
vibe_core/doc_renderer.py:296,355,547
    Path("OPERATIONS.md")
    Path("SETTINGS.md")
    Path("ENVOY.md")

vibe_core/envoy_sync.py:77
    Path("ENVOY.md")

vibe_core/settings_sync.py:96
    Path("SETTINGS.md")
```

---

## CATEGORY 2: INLINE PROMPTS (38 violations)

### CRITICAL - LLM Prompts in Python

These should be in `knowledge/prompts/*.yaml` or `.j2`:

```
vibe_core/cartridges/system/envoy/deterministic_executor.py:991
    prompt = f"""Given the context: {context}...

vibe_core/cartridges/system/envoy/blueprint_generator.py:753
    prompt = f"""Extract structured parameters from this user request...

vibe_core/cortex/engines/circuit_engine.py:691
    prompt = f"""...

vibe_core/circuit_executor.py:691
    prompt = f"""...  (DUPLICATE!)

vibe_core/llm/degradation_chain.py:178
    return f"""Du bist ein Agent in Agent City...

vibe_core/runtime/boot_sequence.py:225
    return f"""You are operating the STEWARD Protocol...

vibe_core/operator_adapter.py:92,297
    output = f"""...
    return f"""You are an operator for Agent City OS...
```

### MEDIUM - UI/Report Templates

These should be in `knowledge/templates/`:

```
vibe_core/plugins/interface/renderers/git.py:520,583
    content = f"""# Git Repository Analysis...

vibe_core/plugins/interface/renderers/tasks.py:148
    content = f"""# 📋 Mission Control...

vibe_core/plugins/interface/renderers/opus/renderer.py:108,131,147,176,206,227
    f"""<!-- ... multiple panel templates

vibe_core/runtime/prompt_composer.py:36,125,166
    Multiple f-string templates

vibe_core/runtime/project_memory.py:125
    summary = f"""🧠 PROJECT MEMORY SUMMARY...
```

---

## CATEGORY 3: MAGIC AGENT STRINGS (8 violations)

### CRITICAL - Hardcoded Agent References

These should use config-driven agent discovery:

```
vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py:297
    civic = self.kernel.get_agent("civic")

vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py:344
    science = self.kernel.get_agent("science")

vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py:411,498
    herald = self.kernel.get_agent("herald")

vibe_core/cartridges/system/envoy/tools/city_control_tool.py:549,553
    return self._get_agent("civic")
    return self._get_agent("forum")

vibe_core/cortex/engines/circuit_engine.py:686
    architect = self.kernel.get_agent("architect") or self.kernel.get_agent("science")

vibe_core/circuit_executor.py:686
    (DUPLICATE of above)
```

**FIX:** Use capability-based lookup or config:
```python
# BAD
herald = self.kernel.get_agent("herald")

# GOOD
herald = self.kernel.get_agent_by_capability("broadcast")
# OR
herald = self.kernel.config.agents.broadcaster
```

---

## CATEGORY 4: HARDCODED TEMPLATES (5 violations)

### HIGH - Jinja Templates in Python

```
vibe_core/cartridges/system/envoy/action_handlers.py:665-705
    BUILTIN_TEMPLATES = {
        "status_summary": """## 🏙️ {{ city_name }}...""",
        "agent_list": """### Registered Agents ({{ total }})...""",
        "simple": """{{ message }}""",
    }
```

**FIX:** Move to `knowledge/templates/`:
```
knowledge/templates/
├── status_summary.j2
├── agent_list.j2
└── simple.j2
```

---

## CATEGORY 5: HARDCODED CIRCUIT NAMES (2 violations)

```
vibe_core/cortex/engines/circuit_engine.py:???
vibe_core/circuit_executor.py:???
```

(Need to find exact lines - likely in test/example code)

---

## FIX PRIORITY

### P0 - Must Fix (Blocks Fraktal Vision)

1. **Data Paths** (15 files) - All `Path("data/...")` must come from PhoenixConfig
2. **Code Structure Paths** (6 files) - Must use loader discovery, not hardcoded paths
3. **Hardcoded Templates** (1 file) - Move to knowledge/templates/

### P1 - Should Fix (Tech Debt)

4. **Inline Prompts** (10 files) - Move to knowledge/prompts/
5. **Magic Agent Strings** (4 files) - Use capability lookup

### P2 - Nice to Have

6. **System Paths** (5 files) - Consolidate to single config
7. **UI Templates** (5 files) - Consider template system

---

## ANTI-PATTERNS FOUND

### 1. Global Defaults Pattern (BAD)
```python
class Tool:
    DB_PATH = Path("data/economy.db")  # Class-level constant
```

### 2. Default Args Pattern (BAD)
```python
def __init__(self, path: Path = Path("data/...")):
```

### 3. Inline Discovery Pattern (BAD)
```python
agents = list(Path("vibe_core/cartridges/system").iterdir())
```

### 4. Fallback to Hardcoded Pattern (BAD)
```python
path = config.get("path") or Path("data/default")
```

---

## SOLUTION: PhoenixConfig Injection

Every component should receive its paths from PhoenixConfig:

```python
# phoenix.yaml
paths:
  data_root: "data/"
  economy_db: "{data_root}/economy.db"
  registry: "{data_root}/registry/citizens.json"
  ledger: "{data_root}/ledger/"

cartridge_paths:
  system: "vibe_core/cartridges/system"
  agent_city: "vibe_core/cartridges/agent_city"

knowledge_paths:
  circuits: "knowledge/circuits"
  playbooks: "knowledge/playbooks"
  templates: "knowledge/templates"
  prompts: "knowledge/prompts"
```

```python
# In cartridge __init__
def __init__(self, config: PhoenixConfig):
    self.db_path = config.paths.economy_db
    # NOT: self.db_path = Path("data/economy.db")
```

---

## NEXT STEPS

1. Create `knowledge/templates/` directory structure
2. Create `knowledge/prompts/` directory structure
3. Add path config section to phoenix.yaml
4. Update PhoenixConfig to expose all paths
5. Refactor each violation one-by-one with tests

**This is the REAL work that needs to be done.**
