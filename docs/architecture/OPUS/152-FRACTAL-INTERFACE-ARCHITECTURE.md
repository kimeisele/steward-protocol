# OPUS-152: Fractal Interface Architecture

> **Status**: IMPLEMENTED
> **Created**: 2025-12-20
> **Prereqs**: OPUS-014, OPUS-023, OPUS-151, Phoenix Config System
> **HARNESS**: @SAMSKARA → @AKSHARA → @DOJO → @MANTRA → @SIDDHI

<!-- @HARNESS
# OPUS-313: Updated - envoy.py/settings.py deleted, replaced by ManifestationService
intent: "Teach render_sections() pattern for config-driven renderers"
files:
  - path: vibe_core/plugins/interface/renderers/base.py
    required: true
  - path: vibe_core/plugins/interface/renderers/state.py
    required: true
  - path: vibe_core/plugins/interface/renderers/economy.py
    required: true
  - path: vibe_core/services/manifestation_service.py
    required: true
  - path: config/interface.yaml
    required: true
wiring:
  - pattern: "def render_sections"
    in: vibe_core/plugins/interface/renderers/base.py
  - pattern: "register_custom_renderer"
    in: vibe_core/plugins/interface/plugin_main.py
  - pattern: "ManifestationService"
    in: vibe_core/services/manifestation_service.py
-->

---

## @SAMSKARA: What We Learned

### The Fractal Config Pattern

Phoenix Config uses **deep_merge** with priority ordering:

```
┌─────────────────────────────────────────────────────────────┐
│                    config/interface.yaml                     │
│                    (ROOT - System Renderers)                 │
│                                                             │
│  renderers:                                                 │
│    envoy: { enabled: true, output: ENVOY.md }              │
│    settings: { enabled: true, output: SETTINGS.md }        │
│    ...                                                      │
│                                                             │
│  custom_renderers: {}  ← FRACTAL EXTENSION POINT            │
└─────────────────────────────────────────────────────────────┘
                              ↓
                         deep_merge
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Plugin.on_boot() Registration                   │
│                                                             │
│  interface_plugin.register_custom_renderer(                 │
│      name="state",                                          │
│      renderer=StateRenderer(kernel),                        │
│      interval=10,                                           │
│      output="STATE.md"                                      │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Files Discovered

| File | Purpose |
|------|---------|
| `vibe_core/phoenix/config.py` | PhoenixConfig with `__getattr__` for sections |
| `vibe_core/phoenix/section_loader.py` | Auto-discovers sections via manifest.json |
| `vibe_core/phoenix/sections/interface/section_main.py` | InterfaceConfig with `custom_renderers` |
| `vibe_core/plugins/interface/plugin_main.py:404` | `register_custom_renderer()` API |
| `vibe_core/plugins/opus_assistant/core/config_loader.py` | `deep_merge()` pattern |

### The Mistake I Made

**WRONG**: Modified root `config/interface.yaml` to add STATE/ECONOMY
**RIGHT**: Use `register_custom_renderer()` API from plugin on_boot

---

## @AKSHARA: The Basis Vectors

### Three Types of Renderers

```
┌─────────────────────────────────────────────────────────────┐
│ TYPE 1: SYSTEM RENDERERS (in root config/interface.yaml)    │
├─────────────────────────────────────────────────────────────┤
│ - envoy     → ENVOY.md (bidirectional, EnvoySync)          │
│ - settings  → SETTINGS.md (bidirectional, SettingsSync)    │
│ - readme, index, help, agents, etc.                         │
│                                                             │
│ These are CORE - always available, defined in root config.  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TYPE 2: PLUGIN RENDERERS (registered via API)               │
├─────────────────────────────────────────────────────────────┤
│ Plugins register their own renderers in on_boot():          │
│                                                             │
│   interface_plugin.register_custom_renderer(                │
│       "myfeature", MyRenderer(kernel), interval=60          │
│   )                                                         │
│                                                             │
│ Examples: opus_assistant's dashboard, broker's prices       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TYPE 3: STATE RENDERERS (special - Prakriti visibility)     │
├─────────────────────────────────────────────────────────────┤
│ - STATE.md   → Prakriti 3-layer state inspector            │
│ - ECONOMY.md → Resource meters, token usage                │
│                                                             │
│ QUESTION: Should these be in root config or registered?     │
│ ANSWER: Root config is OK for CORE state visibility.        │
│         They ARE system renderers, not plugin renderers.    │
└─────────────────────────────────────────────────────────────┘
```

### The Rendering Pattern (render_sections vs generate_content)

```python
# WRONG: Hardcoded generate_content()
def generate_content(self) -> str:
    lines = []
    lines.append("# HARDCODED")
    lines.append("| col1 | col2 |")
    return "\n".join(lines)

# RIGHT: Config-driven render_sections()
def render(self) -> None:
    config = self.get_config()
    if config and config.sections:
        content = self.render_sections()  # Uses interface.yaml sections
        self.merge_and_write(content)
```

**The 13 renderers using generate_content() need refactoring.**

### Bidirectional Interface Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    ENVOY.md / SETTINGS.md                    │
│                                                             │
│  ┌─────────────┐           ┌─────────────┐                 │
│  │   INPUT     │           │   OUTPUT    │                 │
│  │ (User writes│    ←→     │  (System    │                 │
│  │  commands)  │           │   renders)  │                 │
│  └─────────────┘           └─────────────┘                 │
│        ↓                          ↑                         │
│  EnvoySync.parse_requests()  render_sections()              │
│  SettingsSync.parse_commands()                              │
│        ↓                          ↑                         │
│  Submit to Scheduler         Data Sources                   │
│        ↓                          ↑                         │
│  Execute Task              register_data_source()           │
└─────────────────────────────────────────────────────────────┘
```

---

## @DOJO: The Meditation

### Question 1: Where Should STATE/ECONOMY Renderers Live?

**Option A**: Root config (current approach)
- Pro: They ARE core system visibility
- Con: Mixed with plugin-specific renderers

**Option B**: InterfacePlugin registers them internally
- Pro: Clean separation
- Con: Still in interface plugin, not truly fractal

**Option C**: New "observability" plugin that registers them
- Pro: Truly fractal, self-contained holon
- Con: More complexity

**DECISION**: Option A is correct. STATE.md and ECONOMY.md are CORE system
visibility, not plugin features. They belong in root config.

But I should NOT have disabled other renderers. Each serves a purpose.

### Question 2: How to Refactor generate_content() Renderers?

**Current State**:
- 13 renderers use hardcoded `generate_content()`
- Only `architecture/renderer.py` uses `render_sections()` properly
- Config sections in interface.yaml are IGNORED by most renderers

**Refactoring Strategy**:
1. For each renderer with sections in config:
   - Add `_register_data_sources()` in `__init__()`
   - Change `render()` to use `render_sections()` pattern
   - Keep `generate_content()` as fallback only

2. Priority order:
   - ENVOY.md (bidirectional, critical)
   - SETTINGS.md (bidirectional, critical)
   - STATE.md (already correct)
   - ECONOMY.md (already correct)
   - Others can follow later

### Question 3: What About Plugin-Specific Configs?

Plugins should have their OWN config structure:

```
vibe_core/plugins/my_plugin/
├── config/
│   └── interface.yaml    ← Plugin's OWN interface config
├── templates/            ← Plugin's OWN templates
├── renderers/            ← Plugin's OWN renderers
└── manifest.json         ← Declares capabilities
```

The plugin registers via API, but can have its own config for structure.

---

## @MANTRA: The Implementation Steps

### Phase 1: Fix My Mistake
- [x] Revert interface.yaml changes (done)
- [ ] Keep STATE/ECONOMY sections in interface.yaml (they ARE core)
- [ ] Re-add state/economy sections properly (not disabling others)

### Phase 2: Refactor ENVOY.md Renderer
```python
class EnvoyRenderer(BaseRenderer):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = EnvoySync()
        self.state = EnvoySyncState()
        self._register_data_sources()  # NEW

    def _register_data_sources(self):
        self.register_data_source("envoy.pending_tasks",
            lambda: self.state.pending_tasks)
        self.register_data_source("envoy.history",
            lambda: self.state.request_history[-5:])
        self.register_data_source("envoy.routes",
            lambda: self._get_routes())

    def render(self) -> None:
        # INPUT: Process user commands FIRST
        self._sync_from_file()
        self._process_completed_tasks()

        # OUTPUT: Use config-driven sections
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            # Fallback to hardcoded
            content = self._generate_content()
            self.merge_and_write(content)
```

### Phase 3: Refactor SETTINGS.md Renderer
Same pattern as ENVOY - register data sources, use render_sections().

### Phase 4: Verify STATE/ECONOMY
Already use the correct pattern. Just ensure they're in config.

### Phase 5: Document the Pattern
Create template/guide for other renderers to follow.

---

## @SIDDHI: The Optimal State

When complete:

1. **Root config/interface.yaml** contains:
   - System renderers (envoy, settings, readme, etc.)
   - State visibility renderers (state, economy)
   - `custom_renderers: {}` for plugin extensions

2. **All renderers** use:
   - `render_sections()` for output (config-driven)
   - `register_data_source()` for live data
   - `merge_and_write()` for bidirectional preservation

3. **Plugins** register via:
   - `interface_plugin.register_custom_renderer()` API
   - Their own config/templates in plugin directory

4. **Tests** verify:
   - Config sections are not ignored
   - Bidirectional flow works (input → process → output)
   - Fractal extension works (plugin registers → renders)

---

## Implementation Checklist

- [ ] Re-add STATE/ECONOMY sections to interface.yaml (properly)
- [ ] Refactor EnvoyRenderer to render_sections()
- [ ] Refactor SettingsRenderer to render_sections()
- [ ] Test bidirectional flow
- [ ] Document pattern for other renderers
- [ ] Update OPUS-150 audit with resolution

---

**Next Step**: Re-add STATE/ECONOMY to interface.yaml without touching other renderers.
