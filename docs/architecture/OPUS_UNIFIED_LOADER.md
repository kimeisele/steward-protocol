# OPUS: Unified Loader Alignment

> **Status:** IN PROGRESS
> **Started:** 2025-12-05
> **Goal:** ONE UnifiedLoader base class, ALL loaders inherit from it

---

## 1. THE PROBLEM

We have **7 different loaders** all implementing the SAME VEDA-4 pattern DIFFERENTLY:

| Loader | Location | Pattern |
|--------|----------|---------|
| PluginLoader | `vibe_core/plugin_loader.py` | scan → find class → instantiate |
| SectionLoader | `vibe_core/phoenix/section_loader.py` | scan → find class → instantiate |
| SettingsSectionLoader | `vibe_core/settings/loader.py` | scan → find class → instantiate |
| AgentLoader | `vibe_core/steward/loader.py` | scan → find manifest → load class |
| KnowledgeLoader | `vibe_core/knowledge/loader.py` | scan → load YAML |
| WorkflowLoader | `vibe_core/playbook/loader.py` | scan → load YAML → validate |
| ContextLoader | `vibe_core/runtime/context_loader.py` | load JSON files |

**This is NOT fraktal. This is chaos.**

---

## 2. THE SOLUTION

**ONE base class, ALL inherit:**

```python
# vibe_core/loaders/base_loader.py (ALREADY EXISTS!)
class UnifiedLoader(ABC):
    item_type: str           # "plugin", "agent", "section"
    scan_paths: List[Path]   # Where to look
    manifest_filenames: List[str]  # ["manifest.json"]
    entry_suffix: str        # "_main.py"

    @classmethod
    def discover_and_load() -> Tuple[ItemRegistry, ItemMetadata]
```

**Each loader becomes MINIMAL:**

```python
# vibe_core/steward/loader.py (AFTER)
from vibe_core.loaders import UnifiedLoader

class AgentLoader(UnifiedLoader):
    item_type = "agent"
    scan_paths = [Path("steward/system_agents"), Path("agent_city/registry")]
    manifest_filenames = ["manifest.json", "steward.json"]  # backward compat
    entry_suffix = "_main.py"
    # DONE - everything else inherited!
```

---

## 3. MIGRATION PLAN

### Phase 1: AgentLoader (Proof of Concept) ✅ COMPLETE
- [x] Make AgentLoader inherit from UnifiedLoader
- [x] Keep backward compat (steward.json alias, AgentMeta alias)
- [x] Support both old format (identity.agent_id) and new format (id)
- [x] All 29 unified loader tests pass
- [x] 27 agents load successfully

### Phase 2: PluginLoader ✅ COMPLETE
- [x] Make PluginLoader inherit from UnifiedLoader
- [x] Support both old .py files AND new folders (manifest.json)
- [x] Backward compat: static `discover()` method still works
- [x] All 29 unified loader tests pass
- [x] 8 plugins loaded (5 new-style, 3 old-style)

### Phase 3: SectionLoader + Config Pattern ✅ COMPLETE
- [x] Design the manifest/config split pattern
- [x] Make SectionLoader inherit from UnifiedLoader
- [x] Migrate 4 sections to folder structure (city, kernel, quality, steward)
- [x] All 29 unified loader tests pass
- [x] Kernel boots correctly with all sections

### Phase 4: Cleanup
- [ ] Remove duplicate code from old loaders
- [ ] Update documentation
- [ ] Final test run

---

## 4. SUCCESS CRITERIA

| Criterion | Metric |
|-----------|--------|
| ONE base class | All loaders inherit UnifiedLoader |
| NO duplicate code | VEDA-4 logic only in base_loader.py |
| Backward compat | All existing tests pass |
| New items | Use manifest.json pattern |

---

## 5. WORK LOG

### 2025-12-05: Setup
- [x] Created UnifiedLoader base class
- [x] Created manifest_schema.json
- [x] Created schema.py for validation
- [x] 29 tests passing

### 2025-12-05: Phase 1 Complete
- [x] AgentLoader now inherits from UnifiedLoader
- [x] Added AgentMeta = ItemMeta alias for backward compat
- [x] _validate_manifest() supports both old/new formats
- [x] 27 agents loading successfully
- [x] Tests pass (50 integration, 29 unified loader)

### 2025-12-05: Phase 2 Complete
- [x] PluginLoader now inherits from UnifiedLoader
- [x] Supports both new-style (folder) and old-style (.py file) plugins
- [x] 8 plugins loading (5 new-style, 3 old-style)
- [x] Backward compat `discover()` method preserved
- [x] **COMMITTED:** `1f08196` pushed to `feat/core-io-migration`

### 2025-12-05: Phase 3 Complete
- [x] SectionLoader now inherits from UnifiedLoader
- [x] 4 sections migrated to folder structure (city, kernel, quality, steward)
- [x] Each section has manifest.json + section_main.py
- [x] Config YAML stays in config/ (separation of schema vs values)
- [x] All 29 tests pass, kernel boots correctly

---

## 6. PHASE 3 DESIGN: Config Section Pattern

### The Insight

Config Sections are DIFFERENT from Plugins/Agents:
- **Plugins/Agents:** Code that DOES something (behavior)
- **Config Sections:** Data that CONFIGURES something (settings)

But they should STILL follow the fraktal pattern!

### Current State (Problem)

```
vibe_core/phoenix/sections/
  city.py           # CityConfig class with section_id = "city"
  kernel.py         # KernelConfig class
  quality.py        # etc.

config/
  city.yaml         # values for CityConfig
  kernel.yaml       # values for KernelConfig
```

**Issues:**
1. No manifest.json → no schema, no validation rules, no metadata
2. Duck typing (`section_id` attribute) instead of explicit manifest
3. Can't use UnifiedLoader pattern

### Proposed Pattern

```
vibe_core/phoenix/sections/
  city/
    manifest.json     # SCHEMA: type, id, fields, defaults, validation
    section_main.py   # CityConfig class (code)
  kernel/
    manifest.json
    section_main.py
  ...

config/                 # INSTANCE VALUES (separate!)
  city.yaml            # actual values for this deployment
  kernel.yaml
```

### manifest.json for Config Sections

```json
{
  "type": "section",
  "id": "city",
  "name": "City Configuration",
  "version": "1.0.0",

  "entry_point": "section_main.py",
  "entry_class": "CityConfig",

  "priority": 10,

  "schema": {
    "max_agents": {"type": "integer", "default": 100, "min": 1},
    "enable_federation": {"type": "boolean", "default": false},
    "api_keys": {
      "type": "object",
      "properties": {
        "openai": {"type": "string", "secret": true},
        "tavily": {"type": "string", "secret": true}
      }
    }
  },

  "config_file": "city.yaml",
  "required": false
}
```

### The Power: Scalable Config Groups

Imagine 50 API keys:

```
vibe_core/phoenix/sections/
  api_keys/
    manifest.json     # Schema for ALL API keys
    section_main.py   # APIKeysConfig class

config/
  api_keys.yaml       # The actual keys (gitignored!)
```

**manifest.json:**
```json
{
  "type": "section",
  "id": "api_keys",
  "schema": {
    "openai": {"type": "string", "secret": true, "env": "OPENAI_API_KEY"},
    "anthropic": {"type": "string", "secret": true, "env": "ANTHROPIC_API_KEY"},
    "tavily": {"type": "string", "secret": true, "env": "TAVILY_API_KEY"},
    // ... 50 more
  },
  "config_file": "api_keys.yaml",
  "env_fallback": true
}
```

### Benefits

1. **Schema validation** - manifest defines what's valid
2. **Secrets handling** - mark fields as `secret: true`
3. **Env fallback** - `env: "OPENAI_API_KEY"` means check env if yaml missing
4. **Autodiscovery** - UnifiedLoader finds all sections
5. **Fraktal** - same pattern as plugins/agents

### Migration Path

1. Create folder for each section (4 total)
2. Move class to `section_main.py`
3. Create `manifest.json` with schema
4. Update SectionLoader to inherit UnifiedLoader
5. Keep `config/*.yaml` files where they are (instance data)

### Open Questions

- [ ] Should `config/*.yaml` stay in config/ or move into section folder?
- [ ] How to handle secrets (gitignore, env vars, vault)?
- [ ] Schema validation: JSON Schema or custom?

---

*This document tracks the Unified Loader alignment work.*
