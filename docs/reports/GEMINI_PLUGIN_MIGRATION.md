# GEMINI TASK: Plugin Folder Migration

**Priority**: Medium
**Effort**: 3-4 hours
**Type**: Repetitive refactoring

---

## Objective

Convert 9 single-file plugins to folder structure with manifest.json.

**EXAMPLE TO FOLLOW:** `vibe_core/plugins/test_orchestration/` - this is ALREADY a folder!

---

## Target Structure

```
BEFORE: vibe_core/plugins/sarga_cycle.py

AFTER:  vibe_core/plugins/sarga_cycle/
        ├── manifest.json      # Plugin identity
        ├── plugin_main.py     # The actual code (renamed from sarga_cycle.py)
        ├── config.yaml        # Optional config
        └── __init__.py        # Export the plugin class
```

---

## Plugins to Migrate (Priority Order)

| Plugin | Current File | Complexity |
|--------|--------------|------------|
| sarga_cycle | sarga_cycle.py | LOW - simple lifecycle |
| vedic_governance | vedic_governance.py | MEDIUM - core logic |
| test_mode | test_mode.py | MEDIUM - global state |
| git_history | git_history.py | LOW - analytics |
| envoy_ui | envoy_ui.py | LOW - interface |
| ephemeral_ui | ephemeral_ui.py | LOW - interface |
| settings_ui | settings_ui.py | LOW - interface |
| steward_protocol | steward_protocol.py | HIGH - complex, do last |

**SKIP:** `test_orchestration/` - already a folder!

---

## Step-by-Step for Each Plugin

### 1. Create folder structure

```bash
# Example for sarga_cycle
mkdir -p vibe_core/plugins/sarga_cycle
```

### 2. Create manifest.json

```json
{
  "$schema": "../../loaders/manifest_schema.json",
  "type": "plugin",
  "id": "sarga_cycle",
  "name": "Sarga Cycle Plugin",
  "version": "1.0.0",
  "description": "Cosmic Day/Night cycle management",
  "entry_point": "plugin_main.py",
  "entry_class": "SargaCyclePlugin",
  "priority": 10
}
```

### 3. Move and rename the code

```bash
mv vibe_core/plugins/sarga_cycle.py vibe_core/plugins/sarga_cycle/plugin_main.py
```

### 4. Create __init__.py

```python
from .plugin_main import SargaCyclePlugin

__all__ = ["SargaCyclePlugin"]
```

### 5. Update imports in other files

```bash
# Find files that import from the old location
grep -r "from vibe_core.plugins.sarga_cycle import" --include="*.py"
grep -r "from vibe_core.plugins import.*SargaCycle" --include="*.py"
```

### 6. Verify tests pass

```bash
python -m pytest tests/ -v --tb=short -x
```

---

## Validation After Each Plugin

```bash
# 1. Plugin can be imported
python3 -c "from vibe_core.plugins.sarga_cycle import SargaCyclePlugin; print('OK')"

# 2. PluginLoader discovers it
python3 -c "
from vibe_core.plugin_loader import PluginLoader
plugins = PluginLoader.discover()
print([p.__class__.__name__ for p in plugins])
"

# 3. Tests pass
python -m pytest tests/ -v --tb=short
```

---

## DO NOT TOUCH

- `test_orchestration/` - Already a folder, working perfectly
- `__init__.py` in plugins root - Just update exports

---

## Commit Strategy

One commit per plugin:

```bash
git add vibe_core/plugins/sarga_cycle/
git commit -m "refactor: Convert sarga_cycle plugin to folder structure"
```

---

## Success Criteria

- [ ] All 9 plugins converted to folders
- [ ] Each has manifest.json
- [ ] PluginLoader discovers all plugins
- [ ] All tests pass
- [ ] No import errors

---

## Reference

- Example folder: `vibe_core/plugins/test_orchestration/`
- Manifest schema: `vibe_core/loaders/manifest_schema.json`
- UnifiedLoader: `vibe_core/loaders/base_loader.py`
