# VISNU KERNEL EXTRACTION PLAN

**Status:** Draft
**Priority:** P0
**Goal:** Reduce kernel_impl.py from 1705 LOC to EXACTLY 1008 LOC

> **1008** - The sacred number of Visnu's names. The kernel is Visnu.
> Everything else is an Avatar (Plugin).

## The Problem

The "kernel" is not a kernel - it's a MONOLITH.

Current `kernel_impl.py` does:
- Event loop (tick) - KERNEL
- Plugin management - KERNEL
- Agent registry - KERNEL (minimal)
- Task scheduling - KERNEL
- Config loading - NOT KERNEL (should be plugin)
- Tool discovery - NOT KERNEL (should be plugin)
- Capability management - NOT KERNEL (should be plugin)
- Governance (Varna/Ashrama) - NOT KERNEL (should be plugin)
- Resource management - NOT KERNEL (should be plugin)
- Bank/Vault - NOT KERNEL (should be plugin)
- Narasimha (kill-switch) - NOT KERNEL (should be plugin)
- IPC events - NOT KERNEL (should be plugin)
- Health checks - NOT KERNEL (should be plugin)

**Result:** Every change breaks something. Tests take forever because they boot the whole system.

## What a REAL Kernel Should Be

```
┌─────────────────────────────────────────────┐
│                 KERNEL (~1000 LOC)          │
├─────────────────────────────────────────────┤
│  1. Boot/Shutdown                           │
│  2. Tick Loop (Event Loop)                  │
│  3. Plugin Registry (load/unload)           │
│  4. Agent Registry (register/lookup)        │
│  5. Task Queue (submit/next)                │
│  6. Event Bus (publish/subscribe)           │
│  7. I/O Service (file access)               │
│  8. Ledger (append-only log)                │
└─────────────────────────────────────────────┘
         │
         │ Plugins attach via hooks:
         │   on_boot, on_tick_pre, on_tick_post, on_shutdown
         ▼
┌─────────────────────────────────────────────┐
│                 PLUGINS                      │
├─────────────────────────────────────────────┤
│  ConfigPlugin      - Phoenix config loading │
│  GovernancePlugin  - Varna/Ashrama          │
│  CapabilityPlugin  - Capability registry    │
│  SecurityPlugin    - Narasimha, threats     │
│  ToolPlugin        - Tool discovery/registry│
│  ResourcePlugin    - Resource quotas        │
│  InterfacePlugin   - UI rendering           │
│  EconomyPlugin     - Bank/Vault             │
│  HealthPlugin      - System health checks   │
└─────────────────────────────────────────────┘
```

## Current Method Analysis

### MUST STAY IN KERNEL (Core)
```
__init__           - Boot initialization
boot()             - Start kernel
tick()             - Main event loop
shutdown()         - Clean shutdown
register_agent()   - Agent registration (basic)
scheduler property - Task queue access
ledger property    - Ledger access
agent_registry     - Agent lookup
```

### SHOULD BECOME PLUGINS

| Current Method | Target Plugin | LOC Saved |
|----------------|---------------|-----------|
| `_register_core_tools()` | ToolPlugin | ~40 |
| `_discover_agent_tools()` | ToolPlugin | ~70 |
| `get_agent_varna/ashrama/permissions` | GovernancePlugin | ~50 |
| `transition_agent_ashrama()` | GovernancePlugin | ~20 |
| `get_governance_status()` | GovernancePlugin | ~20 |
| `_check_agent_capability()` | CapabilityPlugin | ~40 |
| `revoke_capability()` | CapabilityPlugin | ~40 |
| `grant_capability()` | CapabilityPlugin | ~40 |
| `get_agent_capabilities()` | CapabilityPlugin | ~20 |
| `_narasimha_destroy_agent()` | SecurityPlugin | ~70 |
| `_check_system_health()` | HealthPlugin | ~40 |
| `_sync_resource_quotas()` | ResourcePlugin | ~40 |
| `_grant_repo_access()` | ResourcePlugin | ~30 |
| `_process_ipc_events()` | IPCPlugin | ~40 |
| `get_bank()` | EconomyPlugin | ~30 |
| `get_vault()` | EconomyPlugin | ~20 |
| `spawn_child_kernel()` | HypercubePlugin | ~50 |
| `merge_child_result()` | HypercubePlugin | ~40 |

**Estimated LOC saved: ~700**
**Target kernel: ~1000 LOC**

## Extraction Order

### Phase 1: Low-Risk Extractions
1. **ToolPlugin** - Tool discovery is already isolated
2. **EconomyPlugin** - Bank/Vault are already isolated
3. **HealthPlugin** - Health checks are independent

### Phase 2: Medium-Risk Extractions
4. **GovernancePlugin** - Already partially extracted
5. **CapabilityPlugin** - Used by governance
6. **ResourcePlugin** - Resource management

### Phase 3: High-Risk Extractions
7. **SecurityPlugin** - Narasimha integration
8. **IPCPlugin** - Process communication
9. **HypercubePlugin** - Child kernel spawning

## Plugin Interface Contract

Each plugin implements:

```python
class KernelPlugin(Protocol):
    @property
    def plugin_id(self) -> str: ...

    @property
    def priority(self) -> int: ...  # Lower = earlier

    def on_boot(self, kernel: "VibeKernel") -> None: ...
    def on_tick_pre(self, kernel: "VibeKernel") -> None: ...
    def on_tick_post(self, kernel: "VibeKernel") -> None: ...
    def on_shutdown(self, kernel: "VibeKernel") -> None: ...
```

Plugins can expose APIs via kernel:
```python
# Plugin registers its API
kernel.register_api("governance", self)

# Other code accesses it
kernel.api("governance").get_varna(agent_id)
```

## Why Tests Are Slow

Current test flow:
```
Test starts
  → Import kernel_impl
    → Import 20+ modules
    → Load PhoenixConfig (4+ seconds!)
      → SectionLoader.discover()
        → Import ALL sections
        → Parse ALL YAML files
    → Initialize ALL managers
  → Run actual test (0.1 seconds)
```

With plugin extraction:
```
Test starts
  → Import minimal kernel
  → Mock plugins or load only needed ones
  → Run test
```

## Success Criteria

1. `kernel_impl.py` = EXACTLY 1008 LOC (Visnu's names)
2. Tests pass without loading PhoenixConfig
3. Each plugin independently testable
4. Boot time < 1 second (currently 4-5s)

## Safety Features (Senior Review - Gemini)

Based on critical architecture review, the plugin system has:

### 1. Dependencies (not magic priority integers)
```python
@property
def dependencies(self) -> Set[str]:
    return {"capability", "governance"}  # Topological sort
```

### 2. Config Injection (no global get_config)
```python
def on_boot(self, kernel, config: Dict[str, Any]) -> HookResult:
    # Plugin receives ONLY its config section
    self.timeout = config.get("timeout", 30)
```

### 3. Error Boundaries (plugins can't crash kernel)
```python
def on_tick_pre(self, kernel) -> HookResult:
    try:
        # work
        return HookResult.ok()
    except Exception as e:
        return HookResult.error(str(e))  # Logged, continue
```

### 4. State Isolation (plugins own their state)
- No writing to kernel attributes
- Communication via APIs and Events only
- `kernel.api("governance").get_varna(agent_id)`

### 5. Plugin API Registration
```python
def get_api(self) -> Optional[Any]:
    return GovernanceAPI(self)  # Other plugins call kernel.api("governance")
```

## Next Steps

1. ✅ Create plugin interface contract (done: plugin_protocol.py with Safety Features)
2. Extract ToolPlugin (lowest risk)
3. Extract EconomyPlugin
4. Extract GovernancePlugin
5. Update tests to use MockKernel/TestHarness
6. Count LOC - target EXACTLY 1008
