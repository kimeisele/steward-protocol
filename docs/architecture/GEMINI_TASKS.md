# GEMINI TASKS - Bulk Migration Work

> **For:** Gemini (Bulk Worker)
> **From:** Opus (Architect)
> **Date:** 2025-12-05

---

## Context

UnifiedLoader pattern is COMPLETE for core loaders:
- AgentLoader ✅
- PluginLoader ✅
- SectionLoader ✅

PR #308 is open for review.

---

## Remaining Loaders to Migrate

These loaders still use their own patterns and should be migrated to UnifiedLoader:

### 1. WorkflowLoader
**Location:** `vibe_core/playbook/loader.py`
**Priority:** MEDIUM
**Pattern:** Loads YAML workflow definitions

```python
# Current
class WorkflowLoader:
    def load_workflows(self, path: Path) -> Dict[str, Workflow]

# Target
class WorkflowLoader(UnifiedLoader):
    item_type = "workflow"
    scan_paths = [Path("workflows/")]
    manifest_filenames = ["workflow.yaml", "manifest.json"]
```

### 2. PlaybookLoader
**Location:** `vibe_core/playbook/runner.py`
**Priority:** MEDIUM
**Pattern:** Similar to WorkflowLoader, may be duplicate

### 3. KnowledgeLoader
**Location:** `vibe_core/knowledge/loader.py`
**Priority:** LOW
**Pattern:** Loads knowledge base files

### 4. ContextLoader
**Location:** `vibe_core/runtime/context_loader.py`
**Priority:** LOW
**Pattern:** Loads JSON context files

---

## Migration Pattern

For each loader:

1. **Create folder structure:**
```
vibe_core/{type}/items/
  item_name/
    manifest.json
    {type}_main.py (or .yaml for data items)
```

2. **Update loader to inherit UnifiedLoader:**
```python
from vibe_core.loaders import UnifiedLoader, LoaderRegistry

class {Type}Loader(UnifiedLoader):
    item_type = "{type}"
    scan_paths = [Path("...")]
    # Override methods as needed

LoaderRegistry.register("{type}", {Type}Loader)
```

3. **Run tests, verify backward compat**

---

## Test Commands

```bash
# Verify loader works
python -c "from vibe_core.{module} import {Type}Loader; items, meta = {Type}Loader.discover(); print(f'{len(items)} items')"

# Run related tests
python -m pytest tests/ -k "{type}" -v
```

---

## Notes

- Keep backward compatibility for existing code
- Each loader can be migrated independently
- Lower priority items can wait until core is stable

---

*Created by Opus for Gemini handoff*
