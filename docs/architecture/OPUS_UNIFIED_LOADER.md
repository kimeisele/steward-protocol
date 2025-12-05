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

### Phase 3: SectionLoader
- [ ] Make SectionLoader inherit from UnifiedLoader
- [ ] Add manifest.json to sections
- [ ] All section tests still pass

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
- [ ] **NEXT:** SectionLoader alignment

---

*This document tracks the Unified Loader alignment work.*
