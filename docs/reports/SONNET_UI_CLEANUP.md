# SONNET/GEMINI TASK: Markdown UI Cleanup

**Priority**: HIGH (After plugin migration)
**Effort**: 4-6 hours
**Type**: Refactoring + Cleanup

---

## The Problem

30+ markdown files in root directory. Two rendering patterns exist:

| Pattern | Files | Status |
|---------|-------|--------|
| **Direct** (GOOD) | ENVOY.md, SETTINGS.md, DASHBOARD.md | Works, sync, reliable |
| **Delegated** (BAD) | AGENTS.md, CITYMAP.md, HELP.md, INDEX.md, RAG.md | Fragile, async, fails silently |

The "Delegated" pattern submits tasks to the `scribe` agent which writes files asynchronously. This breaks when:
- Scribe agent is not running
- Scheduler is full
- Sandbox/publish logic fails

---

## The Solution

**Make ALL renderers Direct.**

```
BEFORE:
  Renderer.render() → kernel.submit_task(scribe) → [async queue] → scribe writes

AFTER:
  Renderer.render() → generate_content() → write_file() → DONE
```

---

## Files to Fix

### Renderers that need Direct conversion:

| Renderer | Current | Action |
|----------|---------|--------|
| `renderers/agents.py` | Delegated | Convert to Direct |
| `renderers/citymap.py` | Delegated | Convert to Direct |
| `renderers/help.py` | Delegated | Convert to Direct |
| `renderers/index.py` | Delegated | Convert to Direct |
| `renderers/rag.py` | Delegated | Convert to Direct |

### Renderers already Direct (verify):

| Renderer | Status |
|----------|--------|
| `renderers/envoy.py` | ✅ Direct |
| `renderers/settings.py` | Verify |
| `renderers/dashboard.py` | Verify |
| `renderers/tasks.py` | Verify |
| `renderers/ephemeral.py` | Verify |

---

## Step-by-Step for Each Renderer

### 1. Check current implementation

```bash
# If it contains "submit_task" or "scribe", it's Delegated
grep -l "submit_task\|scribe" vibe_core/plugins/interface/renderers/*.py
```

### 2. Convert to Direct pattern

```python
# BEFORE (Delegated)
def render(self):
    task = Task(agent_id="scribe", payload={"action": "render_agents"})
    self.kernel.submit_task(task)

# AFTER (Direct)
def render(self):
    content = self._generate_content()
    Path("AGENTS.md").write_text(content)

def _generate_content(self) -> str:
    lines = ["# 🤖 Agent Registry", ""]
    for agent_id, agent in self.kernel._agent_registry.items():
        lines.append(f"- **{agent_id}**: {agent.name}")
    return "\n".join(lines)
```

### 3. Move logic from scribe tools

The generation logic might be in:
```
vibe_core/cartridges/system/scribe/tools/agents_renderer.py
```

Move that logic INTO the renderer.

---

## Root Directory Cleanup

After fixing renderers, evaluate which .md files should exist:

### KEEP (UI/Interactive):
- ENVOY.md (chat terminal)
- SETTINGS.md (configuration)
- TASKS.md (task board)
- EPHEMERAL.md (ephemeral cities)

### KEEP (Documentation):
- README.md
- CONSTITUTION.md
- STEWARD.md
- INDEX.md

### MOVE to docs/:
- ARCHITECTURE.md → docs/architecture/
- AGI_MANIFESTO.md → docs/
- CARTRIDGE_SPEC.md → docs/specs/

### DELETE (stale/generated):
- AUDIT_FINDINGS.md (one-time report)
- PLAYBOOK_FIX_REPORT.md (one-time report)
- WIRING_*.md (completed tasks)
- GEMINI_ANALYSIS_REPORT.md (one-time)
- UNIVERSE_MAP_RESULTS.md (one-time)

---

## Deprecated Code to Remove

```bash
# Check if this still exists
ls vibe_core/markdown_ui_manager.py
```

If it exists, DELETE it - the InterfacePlugin replaces it.

---

## Validation

```bash
# 1. Boot kernel and check files update
python -m vibe_core.cli boot

# 2. Check all UI files have recent timestamps
ls -la ENVOY.md SETTINGS.md TASKS.md AGENTS.md

# 3. Verify no scribe dependency
grep -r "scribe" vibe_core/plugins/interface/renderers/
# Should return NOTHING
```

---

## Success Criteria

- [ ] All renderers are Direct (no scribe delegation)
- [ ] Root has < 15 markdown files
- [ ] UI files update on every kernel tick
- [ ] No deprecated MarkdownUIManager code
- [ ] Documentation moved to docs/

---

## Reference

- Analysis: `MARKDOWN_UI_ANALYSIS.md`
- InterfacePlugin: `vibe_core/plugins/interface/plugin_main.py`
- BaseRenderer: `vibe_core/plugins/interface/renderers/base.py`
- EnvoyRenderer (example): `vibe_core/plugins/interface/renderers/envoy.py`
