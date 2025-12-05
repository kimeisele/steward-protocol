# ARCHITECTURE NEXT - Fraktal Plugin System

> **Purpose:** This document describes the NEXT phase of system architecture.
> **Previous:** OPUS_WORKING_DOC.md (STEWARD Protocol - COMPLETE)
> **Status:** PLANNING

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

## 2. THE PROBLEM (What we need)

### 2.1 No Plugin Inheritance Pattern

**Agents have:**
```
VibeAgent (Protocol)
    → OathMixin (Capabilities)
    → GenericAgent (Base Implementation)
    → HeraldAgent (Specific Agent)
```

**Plugins have:**
```
KernelPlugin (Protocol)
    → ??? (Nothing!)
    → StewardProtocolPlugin (Direct Implementation)
```

**Missing:**
- `BasePlugin` - Common functionality (logging, config, state)
- `ConfigurablePlugin` - YAML-driven plugins
- `Plugin Templates` - Like Golden Cartridge for agents

### 2.2 Modules That Should Be Plugins

| Module | Location | Why Plugin? |
|--------|----------|-------------|
| CapabilityRegistry | capability_registry.py | on_capability_granted/revoked hooks |
| EventBus | event_bus.py | on_event_emitted hook |
| Lineage/Parampara | lineage.py | Audit Trail as plugin |
| Narasimha | narasimha.py | Kill-Switch as plugin |
| ResourceManager | resource_manager.py | Quotas as plugin |

### 2.3 No Plugin Configuration

Plugins hardcode their config. Should be:
```yaml
# config/plugins.yaml
plugins:
  sarga_cycle:
    enabled: true
    day_duration: 86400
    night_duration: 3600

  steward_protocol:
    enabled: true
    strict_mode: false
    sensitive_capabilities:
      - write_file
      - delete_file
```

---

## 3. THE SOLUTION (Fraktal Plugin Architecture)

### 3.1 Plugin Class Hierarchy

```python
# vibe_core/plugin_protocol.py (EXISTS)
class KernelPlugin(ABC):
    """Protocol - defines the interface"""
    pass

# vibe_core/plugins/base.py (NEW)
class BasePlugin(KernelPlugin):
    """Common functionality for all plugins"""

    def __init__(self):
        self._kernel = None
        self._config = {}
        self._state = {}
        self._logger = logging.getLogger(self.plugin_id)

    def load_config(self, config_path: Path) -> None:
        """Load plugin-specific YAML config"""
        pass

    def save_state(self) -> None:
        """Persist plugin state"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Standard status for all plugins"""
        return {
            "plugin_id": self.plugin_id,
            "priority": self.priority,
            "config": self._config,
            "state_keys": list(self._state.keys()),
        }

# vibe_core/plugins/configurable.py (NEW)
class ConfigurablePlugin(BasePlugin):
    """Plugins driven by YAML configuration"""

    @property
    @abstractmethod
    def config_section(self) -> str:
        """Name of config section in plugins.yaml"""
        pass

    def on_boot(self, kernel):
        super().on_boot(kernel)
        self._load_from_phoenix()
```

### 3.2 Plugin Configuration (Phoenix Integration)

```yaml
# config/plugins.yaml (NEW)
plugins:
  # Each plugin gets its own section
  sarga_cycle:
    enabled: true
    settings:
      day_duration_seconds: 86400
      night_duration_seconds: 3600
      maintenance_tasks_only_at_night: true

  vedic_governance:
    enabled: true
    settings:
      auto_graduate_threshold: 3
      brahmachari_actions: [read, observe, listen, learn]

  steward_protocol:
    enabled: true
    settings:
      strict_mode: false
      trust_threshold_warn: 0.3
      trust_threshold_block: 0.2
      sensitive_capabilities:
        - write_file
        - delete_file
        - execute_command
        - network_request
        - credential_access
```

### 3.3 Plugin Discovery Enhancement

```python
# vibe_core/plugin_loader.py (ENHANCE)
class PluginLoader:
    @staticmethod
    def discover() -> List[KernelPlugin]:
        """Discover and instantiate plugins from vibe_core/plugins/"""
        plugins = []

        # Load config first
        config = load_plugin_config()

        for plugin_class in discover_plugin_classes():
            plugin_id = plugin_class.plugin_id

            # Check if enabled in config
            if not config.get(plugin_id, {}).get("enabled", True):
                logger.info(f"Plugin '{plugin_id}' disabled in config")
                continue

            # Instantiate with config
            plugin = plugin_class()
            if isinstance(plugin, ConfigurablePlugin):
                plugin.load_config(config.get(plugin_id, {}))

            plugins.append(plugin)

        return sorted(plugins, key=lambda p: p.priority)
```

### 3.4 Modules → Plugins Migration Path

**Phase 1: Keep as modules, add plugin wrappers**
```python
# vibe_core/plugins/capability_plugin.py
class CapabilityPlugin(BasePlugin):
    """Plugin wrapper for CapabilityRegistry"""

    def on_boot(self, kernel):
        # Use existing registry, just add hooks
        self._registry = kernel._capability_registry

    def on_capability_granted(self, agent_id, capability, granter):
        # New hook - audit trail
        pass
```

**Phase 2: Gradually move logic into plugins**
- CapabilityRegistry → CapabilityPlugin
- EventBus → EventBusPlugin
- Lineage → LineagePlugin

**Phase 3: Remove standalone modules**
- Only plugin versions remain
- Config-driven behavior

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

## 6. QUESTIONS TO RESOLVE

1. Should plugins have their own config files or share plugins.yaml?
2. Should plugin state be persisted automatically?
3. How to handle plugin dependencies (Plugin A needs Plugin B)?
4. Should there be a plugin marketplace/registry?

---

*Created: 2025-12-05*
*Status: PLANNING - Awaiting approval to proceed*
