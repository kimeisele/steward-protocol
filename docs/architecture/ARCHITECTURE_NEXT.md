# ARCHITECTURE NEXT - Fraktal Plugin System

> **Purpose:** This document describes the NEXT phase of system architecture.
> **Previous:** OPUS_WORKING_DOC.md (STEWARD Protocol - COMPLETE)
> **Status:** PLANNING

---

## 0. VEDA-4 COGNITIVE PATTERN (Das Fundament)

> "The infinite fractal rotating swastika zoom - it is so clear.
> Everywhere hang these 'bushes' - the fractal pattern."

### The Sacred Loop - Überall Gleich

```
SHABDA (शब्द)    → Capture Intent     "Was wurde gesagt/angefragt?"
ARTHA (अर्थ)     → Validate Meaning   "Was bedeutet das wirklich?"
PRATYAYA (प्रत्यय) → Verify Conditions  "Sind die Bedingungen erfüllt?"
KARMA (कर्म)     → Execute Action     "Führe aus"
```

Dieses Pattern ist **NICHT** nur für Circuits. Es ist für **ALLES**:

### VEDA-4 Applied to Plugin System

```
Plugin Boot:
    SHABDA    → Read config YAML (Was will der User?)
    ARTHA     → Parse/validate config (Was bedeutet das?)
    PRATYAYA  → Check dependencies met (Kann ich booten?)
    KARMA     → Execute on_boot() (Tu es)

Plugin Hook Call:
    SHABDA    → Receive hook event (Was ist passiert?)
    ARTHA     → Extract meaning (Welcher Agent? Welche Action?)
    PRATYAYA  → Check permissions (Darf das passieren?)
    KARMA     → Return decision (Allow/Veto/None)

Guard Check:
    SHABDA    → Read file content (Was steht da?)
    ARTHA     → Pattern match (Ist das ein Violation?)
    PRATYAYA  → Check severity (Ist das kritisch?)
    KARMA     → Report violation (Melde es)
```

### Fraktal Self-Similarity

```
Universe:    Brahman → Vishnu → Avatars
Kernel:      KernelProtocol → RealVibeKernel → Hooks
Plugin:      KernelPlugin → BasePlugin → ConfigurablePlugin → ConcretePlugin
Agent:       VibeAgent → OathMixin → GenericAgent → HeraldAgent
Circuit:     CircuitProtocol → SHABDA → ARTHA → PRATYAYA → KARMA
Guard:       GuardProtocol → BaseGuard → PatternGuard → ConcreteGuard
Config:      PhoenixConfig → Section → Field → Value
```

Jede Ebene folgt dem gleichen Pattern. Wenn es anders ist, ist es **falsch**.

---

## 1. CURRENT STATE (What we have)

### Kernel Hooks (COMPLETE - Never change again)

| Category | Hook | Status |
|----------|------|--------|
| Lifecycle | on_boot, on_tick_pre/post, on_shutdown | ✅ |
| Agent | on_agent_registered, on_agent_unregistered | ✅ |
| Task | on_task_submit, on_task_pre_assign, on_task_completed/failed | ✅ |
| Capability | on_capability_check | ✅ |
| Tool | on_tool_execute, on_tool_executed | ✅ |

### Current Plugins (10)

```
vibe_core/plugins/
├── __init__.py
├── sarga_cycle.py        # Cosmic Day/Night
├── vedic_governance.py   # Varna/Ashrama
├── steward_protocol.py   # Protocol Enforcement
├── envoy_ui.py           # ENVOY.md Interface
├── ephemeral_ui.py       # EPHEMERAL.md Interface
├── settings_ui.py        # SETTINGS.md Interface
├── git_history.py        # Git Analytics
├── test_mode.py          # Test Mode
└── test_orchestration.py # Test Discovery
```

---

## 2. THE FRAKTAL GAP (What's Different)

### 2.1 Agent Structure (4 Files - Golden Cartridge)

```
steward/system_agents/herald/
├── steward.json        ← Protocol Identity (MANIFEST)
├── cartridge.yaml      ← Config
├── cartridge_main.py   ← Entry Point (class *Cartridge)
├── STEWARD.md          ← Documentation
└── tools/              ← Optional
```

**Discovery:** `AgentLoader.discover_and_load()`
- Scans: `steward/system_agents/`, `agent_city/registry/`
- Looks for: `steward.json` or `manifest.json`
- Loads: `cartridge_main.py` → `*Cartridge` class
- Runtime: `Discoverer` agent does continuous monitoring

### 2.2 Plugin Structure (1 File - No Template)

```
vibe_core/plugins/
├── steward_protocol.py   ← Everything in ONE file
├── vedic_governance.py
├── envoy_ui.py
└── ...
```

**Discovery:** `PluginLoader.discover()`
- Scans: `vibe_core/plugins/`
- Looks for: ANY .py file with `KernelPlugin` subclass
- NO manifest file
- NO config file
- NO documentation template

### 2.3 The Gap

| Aspect | Agents | Plugins |
|--------|--------|---------|
| Manifest | steward.json | ❌ NONE |
| Config | cartridge.yaml | ❌ hardcoded |
| Discovery | AgentLoader + Discoverer | PluginLoader only |
| Hot-reload | ❌ No | ❌ No |
| Documentation | STEWARD.md | ❌ NONE |
| Structure | 4 files | 1 file |

### 2.4 Why This Matters

Agents can be:
- Discovered at runtime
- Configured via YAML
- Documented consistently
- Extended without changing core

Plugins are:
- Hardcoded Python
- No external config
- No discovery agent
- Changes require code edits

---

## 3. THE FRAKTAL SOLUTION

### 3.1 Plugin Cartridge Structure (Like Agents)

```
vibe_core/plugins/
├── steward_protocol/
│   ├── plugin.json       ← Manifest (like steward.json)
│   ├── plugin_main.py    ← Entry (like cartridge_main.py)
│   ├── config.yaml       ← Config (like cartridge.yaml)
│   └── PLUGIN.md         ← Docs (like STEWARD.md)
│
├── vedic_governance/
│   ├── plugin.json
│   ├── plugin_main.py
│   ├── config.yaml
│   └── PLUGIN.md
│
└── ... (other plugins)
```

### 3.2 PluginLoader Enhancement

```python
# vibe_core/plugin_loader.py - FRAKTAL VERSION
class PluginLoader:
    """
    Mirrors AgentLoader pattern:
    - Scans for plugin.json manifests
    - Loads plugin_main.py → *Plugin class
    - Reads config.yaml
    """

    SCAN_PATHS = [Path("vibe_core/plugins")]
    MANIFEST_FILENAMES = ["plugin.json", "manifest.json"]

    @classmethod
    def discover_and_load(cls) -> List[KernelPlugin]:
        # Same pattern as AgentLoader.discover_and_load()
        pass
```

### 3.3 PluginDiscoverer Agent (Optional)

Like Discoverer for agents, a PluginDiscoverer could:
- Monitor `vibe_core/plugins/` for new plugin.json files
- Hot-reload plugins at runtime
- Register/unregister plugins dynamically

**BUT:** This may be overkill. Plugins are more stable than agents.

### 3.4 Migration Strategy

**Option A: Keep 1-file plugins, add manifest**
- Add plugin.json next to each .py file
- PluginLoader reads both

**Option B: Full cartridge structure**
- Convert each plugin to folder with 4 files
- Maximum fraktal consistency

**Decision needed:** Which option?

---

## 4. IMPLEMENTATION PLAN

### Phase 1: Plugin Foundation (1-2 days)
- [ ] Create `vibe_core/plugins/base.py` with BasePlugin
- [ ] Create `vibe_core/plugins/configurable.py` with ConfigurablePlugin
- [ ] Create `config/plugins.yaml` schema
- [ ] Add Phoenix section for plugins

### Phase 2: Migrate Existing Plugins (2-3 days)
- [ ] Migrate sarga_cycle.py to ConfigurablePlugin
- [ ] Migrate vedic_governance.py to ConfigurablePlugin
- [ ] Migrate steward_protocol.py to ConfigurablePlugin
- [ ] Migrate UI plugins (envoy, ephemeral, settings)

### Phase 3: Module → Plugin Wrappers (3-5 days)
- [ ] Create CapabilityPlugin wrapper
- [ ] Create EventBusPlugin wrapper
- [ ] Create LineagePlugin wrapper
- [ ] Add new hooks: on_capability_granted, on_event_emitted, etc.

### Phase 4: Documentation & Testing (1-2 days)
- [ ] Update plugin documentation
- [ ] Create plugin development guide
- [ ] Add plugin integration tests

---

## 5. SUCCESS CRITERIA

1. **All plugins extend BasePlugin** - Common functionality
2. **All plugins configurable via YAML** - No hardcoded values
3. **Plugin discovery is automatic** - Drop .py file, it works
4. **Modules wrapped as plugins** - CapabilityRegistry, EventBus, etc.
5. **Tests pass** - 374+ tests still green

---

## 6. FRAKTAL GUARD SYSTEM

### 6.1 The Problem

Pre-commit guards are **hardcoded bash** in `.githooks/pre-commit`:
```bash
# HARDCODED - Not fraktal!
if echo "$STAGED_FILES" | grep -q "requirements.txt"; then
    exit 1
fi
```

This violates the fraktal principle - guards should come from **plugins**.

### 6.2 The Solution: GuardProtocol

```python
# vibe_core/guards/protocol.py
class Guard(Protocol):
    """A single guard check"""

    @property
    def guard_id(self) -> str:
        """Unique identifier"""
        ...

    @property
    def description(self) -> str:
        """Human-readable description"""
        ...

    @property
    def severity(self) -> Literal["error", "warning", "info"]:
        """How severe is a violation"""
        ...

    def check_file(self, file_path: Path, content: str) -> Optional[GuardViolation]:
        """Check a single file. Return violation or None."""
        ...

    def check_pattern(self, file_path: Path) -> bool:
        """Should this guard apply to this file?"""
        ...
```

### 6.3 Plugin-Defined Guards

```python
# vibe_core/plugins/steward_protocol.py
class StewardProtocolPlugin(ConfigurablePlugin):

    def get_guards(self) -> List[Guard]:
        """Return guards this plugin wants to enforce"""
        return [
            RequirementsTxtGuard(),      # No requirements.txt in agent dirs
            DirectPathGuard(),           # No Path("data/...")
            HardcodedInitGuard(),        # No paths in __init__
            CapabilityBypassGuard(),     # No anonymous tool calls
        ]
```

### 6.4 Dynamic Pre-Commit Hook

```bash
#!/bin/bash
# .githooks/pre-commit - Now DYNAMIC!

# Let Python handle the logic - fraktal!
python -m vibe_core.guards.precommit "$@"
```

```python
# vibe_core/guards/precommit.py
def main():
    """Dynamic pre-commit that discovers guards from plugins"""

    # Get staged files
    staged_files = get_staged_files()

    # Discover all guards from all plugins
    guards = discover_guards_from_plugins()

    # Run each guard
    violations = []
    for guard in guards:
        for file_path in staged_files:
            if guard.check_pattern(file_path):
                content = read_file(file_path)
                violation = guard.check_file(file_path, content)
                if violation:
                    violations.append(violation)

    # Report results
    report_violations(violations)

    # Exit based on severity
    if any(v.severity == "error" for v in violations):
        sys.exit(1)
```

### 6.5 Guard Configuration

```yaml
# config/guards.yaml
guards:
  # Global settings
  enabled: true
  fail_on_warning: false

  # Per-guard configuration
  requirements_txt:
    enabled: true
    severity: error
    paths: ["steward/system_agents/*"]

  direct_path:
    enabled: true
    severity: error
    patterns: ["Path([\"']data/"]

  hardcoded_init:
    enabled: true
    severity: warning  # Just warn, don't block

  # New guards added by plugins automatically discovered
```

### 6.6 The Fraktal Beauty

Now we have:
```
Runtime                      Commit-Time
────────                     ───────────
on_capability_check    ←→    CapabilityBypassGuard
on_tool_execute        ←→    ToolPatternGuard
on_agent_registered    ←→    AgentStructureGuard
on_task_submit         ←→    TaskValidationGuard
```

**Same logic, different enforcement points.**

Plugins define guards ONCE, they work:
1. At commit time (pre-commit hook)
2. At runtime (kernel hooks)
3. In CI/CD (test suite)
4. In monitoring (dashboards)

---

## 7. QUESTIONS TO RESOLVE

1. Should plugins have their own config files or share plugins.yaml?
2. Should plugin state be persisted automatically?
3. How to handle plugin dependencies (Plugin A needs Plugin B)?
4. Should there be a plugin marketplace/registry?
5. **NEW:** Should guards be separate from plugins or part of them?
6. **NEW:** How to handle guard ordering/priority?

---

*Created: 2025-12-05*
*Status: PLANNING - Awaiting approval to proceed*
