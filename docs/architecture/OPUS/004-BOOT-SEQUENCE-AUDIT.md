# OPUS-004: Boot Sequence Audit

> **Status**: COMPLETE
> **Created**: 2025-12-08
> **Scope**: Document kernel boot sequence, plugin order, coupling analysis

---

## Executive Summary

The Steward Protocol kernel uses a **plugin-first architecture** where most functionality is provided by plugins, not hardcoded in the kernel. The boot sequence is:

1. **Kernel `__init__`**: Initialize core subsystems (ledger, scheduler, etc.)
2. **Plugin Discovery**: `PluginLoader.discover()` finds all plugins
3. **Plugin Boot**: Each plugin's `on_boot()` is called in priority order
4. **Kernel `boot()`**: Register manifests, start scheduler

This is **clean architecture** but has some **hidden coupling** worth documenting.

---

## Boot Sequence Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RealVibeKernel.__init__()                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. Initialize ledger (SQLite or InMemory)                       │
│ 2. Create scheduler (InMemoryScheduler)                         │
│ 3. Create manifest registry                                     │
│ 4. Initialize auditor (if available)                            │
│ 5. Initialize ProcessManager                                    │
│ 6. Initialize ResourceManager                                   │
│ 7. Initialize NetworkProxy                                      │
│ 8. Initialize LineageChain (Parampara)                          │
│ 9. Initialize CapabilityRegistry                                │
│ 10. Initialize KernelIOService                                  │
│ 11. Initialize Narasimha (kill-switch)                          │
│ 12. Initialize EventBus                                         │
│ 13. Initialize PlaybookRouter                                   │
│ 14. ══════ PLUGIN DISCOVERY + BOOT ══════                       │
│     PluginLoader.discover() → sorted by priority                │
│     for plugin in plugins: plugin.on_boot(kernel)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RealVibeKernel.boot()                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Set status = BOOTING                                         │
│ 2. Record KERNEL_BOOT in Parampara                              │
│ 3. Register agent manifests                                     │
│ 4. Set status = RUNNING                                         │
│ 5. Write initial PULSE snapshot                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Plugin Boot Order

Plugins are sorted by `priority` (lower = earlier):

| Priority | Plugin ID            | Key Responsibility |
|----------|----------------------|---------------------|
| 1        | crypto               | Cryptographic primitives |
| 1        | test_mode            | Test environment detection |
| 5        | sarga_cycle          | Cosmic gate (day/night) |
| 5        | steward_protocol     | Constitutional enforcement |
| 5        | tools                | Tool registry initialization |
| 10       | vedic_governance     | Varna/Ashrama system |
| 15       | envoy                | Circuit routing + execution |
| 50       | test_orchestration   | Test fixtures |
| 100      | interface            | ENVOY.md / UI rendering |
| 999      | plugin_template      | Example template |

### Critical Boot Dependencies

```
Priority 5: tools      → Sets kernel.tool_registry
Priority 5: steward    → Sets kernel.steward
Priority 10: vedic     → Sets kernel.governance
Priority 15: envoy     → Sets kernel.envoy
                        → Registers EnvoyCartridge agent
                        → Initializes UnifiedRouter
                        → Initializes LayeredRouter
Priority 100: interface → Discovers renderers
                        → Renders initial UI
```

**Key Insight**: Envoy (15) registers the agent, Interface (100) renders the UI. Envoy MUST boot before Interface for ENVOY.md to work.

---

## Plugin `on_boot()` Actions

### ToolsPlugin (priority=5)
```python
# Creates tool registry with capability checker
kernel.tool_registry = ToolRegistry(...)
# Discovers agent tools and core tools
```

### StewardProtocol (priority=5)
```python
kernel.steward = self
self._restore_from_ledger()
self._connect_infrastructure()  # Uses kernel.lineage
```

### VedicGovernance (priority=10)
```python
kernel.governance = self
self._restore_from_ledger()  # Loads varna assignments
```

### EnvoyPlugin (priority=15)
```python
kernel.envoy = self
self._load_config()
self._discover_circuits()      # Loads YAML circuits
self._discover_playbooks()     # Loads playbook files
self._router = UnifiedRouter(kernel)
self._router.inject_kernel(kernel)  # Injects circuits into LayeredRouter
self._executor = UnifiedExecutor(kernel)
# Register EnvoyCartridge as agent
cartridge = EnvoyCartridge(system=kernel)
kernel.register_agent(cartridge)
```

### InterfacePlugin (priority=100)
```python
self._load_interface_config()  # From config/interface.yaml
self._load_renderers()         # Discovers renderer classes
self.render_all()              # Initial render of all UIs
```

---

## Coupling Analysis

### Clean Dependencies (Good)

| Component | Depends On | Reason |
|-----------|------------|--------|
| EnvoyPlugin | kernel.envoy | Sets itself as provider |
| VedicGovernance | kernel.ledger | Persistence |
| InterfacePlugin | kernel (read-only) | Renders state |
| ToolsPlugin | kernel._auditor | Optional security |

### Hidden Coupling (Watch List)

| Component | Hidden Dependency | Issue |
|-----------|-------------------|-------|
| EnvoyPlugin | kernel.envoy._circuits | Must be populated before router init |
| UnifiedRouter | kernel.envoy | Reads circuits via `kernel.envoy._circuits` |
| LayeredRouter | Circuit YAML structure | Expects `circuit.semantic_grounding` (not sibling) |
| InterfacePlugin | ENVOY.md file | Renders even if Envoy not registered |
| DeterministicExecutor | Ephemeral storage | Optional but affects behavior |

### Circular Reference Risk

```
EnvoyPlugin.on_boot():
  1. Sets kernel.envoy = self
  2. Creates UnifiedRouter(kernel)
  3. UnifiedRouter.__init__():
     - Reads kernel.envoy._circuits  ← TIMING DEPENDENT
  4. Calls router.inject_kernel(kernel)
  5. inject_kernel() rebuilds indexes
```

**Risk**: If circuits aren't loaded before step 2, router has 0 circuits.
**Mitigation**: EnvoyPlugin correctly calls `_discover_circuits()` BEFORE creating router.

---

## Agent Registration Flow

```
EnvoyPlugin.on_boot()
    │
    ├─→ EnvoyCartridge(system=kernel)
    │        │
    │        └─→ cartridge.system = kernel
    │        └─→ cartridge.agent_id = "envoy"
    │
    └─→ kernel.register_agent(cartridge)
             │
             ├─→ Plugin hook: on_agent_pre_register()
             │     StewardProtocol checks Constitutional Oath
             │
             ├─→ Store in kernel._agent_registry["envoy"]
             │
             ├─→ CapabilityRegistry.register_agent(capabilities)
             │
             ├─→ agent.inject_kernel(kernel)
             │
             └─→ Plugin hook: on_agent_registered()
```

---

## Timing Issues Found

### Issue 1: Render Before Execute (SOLVED in AOS-003)

InterfacePlugin runs `on_tick_pre()` which renders BEFORE task execution happens.

**Solution**: Task completion triggers immediate re-render via completion hook.

### Issue 2: LayeredRouter Semantic Path (SOLVED - commit 6c171b7)

LayeredRouter was looking for `circuit_data.get("semantic_grounding")` but semantic_grounding is INSIDE the circuit block.

**Solution**: Changed to `circuit_def.get("semantic_grounding")`.

### Issue 3: Plugin Order Not Explicit

Plugins rely on numeric priority but nothing enforces that tools (5) loads before envoy (15).

**Risk**: If someone creates a plugin at priority 10 that depends on kernel.envoy, it will fail.

**Recommendation**: Document explicit dependencies in manifest.json:
```json
{
  "id": "my_plugin",
  "depends_on": ["envoy", "tools"]
}
```

---

## Simplification Opportunities

### 1. Consolidate Router Initialization

Currently:
- EnvoyPlugin creates UnifiedRouter
- UnifiedRouter creates LayeredRouter
- inject_kernel() called separately

Could be:
```python
self._router = UnifiedRouter.from_kernel(kernel)  # Single factory
```

### 2. Make Plugin Dependencies Explicit

Add to manifest.json:
```json
{
  "depends_on": ["tools"],  // Must boot after tools
  "provides": ["envoy"]     // Sets kernel.envoy
}
```

### 3. Lazy Agent Registration

Currently EnvoyPlugin registers EnvoyCartridge in on_boot().
Could defer to first use (but risk: agent not available for early tasks).

---

## Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| LayeredRouter | 40 tests | ✅ PASS |
| Knowledge Resolver | 39 tests | ✅ PASS |
| Plugin Discovery | via integration | ✅ Works |
| Boot Sequence | test_kernel_boot.py | ✅ PASS |

---

## Conclusion

The boot sequence is **fundamentally sound** but relies on implicit ordering via priority numbers. The main coupling points are:

1. **EnvoyPlugin** must boot before **InterfacePlugin** (15 < 100) ✅
2. **ToolsPlugin** must boot before **EnvoyPlugin** (5 < 15) ✅
3. **Circuit discovery** must happen before router initialization ✅

The LayeredRouter fix (commit 6c171b7) resolved the last major wiring issue. The system is now fully functional.

### Future Work (Optional)

- Add explicit `depends_on` to plugin manifests
- Add boot-time validation of plugin dependencies
- Consider lazy initialization for expensive components

---

## HAIKU EXECUTION BLOCKS

> **For AI Agent Execution**: Copy-paste these blocks to implement improvements.

### TASK 1: Add depends_on to EnvoyPlugin manifest

```
FILE: vibe_core/plugins/envoy/manifest.json
FIND: "priority": 15
ADD_AFTER:
    "depends_on": ["tools"],
    "provides": ["kernel.envoy"],
VERIFY: python3 -c "import json; m=json.load(open('vibe_core/plugins/envoy/manifest.json')); print('depends_on' in m)"
```

### TASK 2: Add depends_on to InterfacePlugin manifest

```
FILE: vibe_core/plugins/interface/manifest.json
FIND: "priority": 100
ADD_AFTER:
    "depends_on": ["envoy"],
    "provides": ["kernel.interface"],
VERIFY: python3 -c "import json; m=json.load(open('vibe_core/plugins/interface/manifest.json')); print('depends_on' in m)"
```

### TASK 3: Add Boot Dependency Validation

```
FILE: vibe_core/loaders/plugin_loader.py
LOCATION: In PluginLoader._boot_plugins() or similar method
ADD_VALIDATION:
    for manifest in sorted_manifests:
        for dep in manifest.get("depends_on", []):
            if dep not in booted_plugins and not hasattr(kernel, dep):
                raise StructuredError(
                    code=ErrorCode.E3003_BOOT_FAILED,
                    message=f"Plugin '{manifest['id']}' requires '{dep}' to be loaded first",
                    context={"plugin": manifest["id"], "missing_dep": dep}
                )
VERIFY: python -m pytest tests/integration/test_kernel_boot.py -v
```

---

**Status**: COMPLETE
