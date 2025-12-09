# VISNU KERNEL EXTRACTION PLAN

**Status:** IN PROGRESS (Phase 2 COMPLETE)
**Last Updated:** 2025-12-09
**Priority:** P0
**Goal:** Reduce kernel_impl.py from 1705 LOC to EXACTLY 1008 LOC
**Current:** 1409 LOC (Phase 1+2 complete, -296 from start)


> **1008** - The sacred number of Visnu's names. The kernel is Visnu.
> Everything else is an Avatar (Plugin).

## Current State Analysis (REAL)

### What's ALREADY a Plugin:
```
vibe_core/plugins/
├── interface/           # UI rendering (DONE)
├── vedic_governance/    # Varna/Ashrama (DONE)
├── steward_protocol/    # Constitutional Oath (DONE)
├── sarga_cycle/         # Cosmic cycle (DONE)
├── test_orchestration/  # PANOPTICON+ (DONE)
├── test_mode/           # Test mode (DONE)
├── crypto/              # Crypto plugin (DONE)
└── tools/               # ToolRegistry + Discovery (EXTRACTED 2025-12-06)
```

### What's HARDCODED in Kernel `__init__`:
```python
# Line 232 - Should be ProcessPlugin
self.process_manager = ProcessManager()

# Line 235 - Should be ResourcePlugin
self.resource_manager = ResourceManager()

# Line 243 - Should be NetworkPlugin
self.network = KernelNetworkProxy(kernel=self)

# Line 247 - Should be LineagePlugin
self.lineage = LineageChain(db_path=lineage_path)

# Line 283-289 - Should be ToolPlugin
self.tool_registry = ToolRegistry(...)
self._register_core_tools()
self._discover_agent_tools()

# Line 294-296 - Should be NarasimhaPlugin
self._narasimha = get_narasimha()
self._narasimha.register_destruction_handler(...)

# Line 301 - Should be EventPlugin (or keep - it's fundamental)
self._event_bus = get_event_bus()

# Line 305 - Should be PlaybookPlugin
self._playbook_router = PlaybookRouter()
```

### DEAD CODE in Kernel (Wrapper Methods):
Lines 1254-1289 are pure delegation to `self.governance`:
```python
def get_agent_varna(self, agent_id):
    return self.governance.get_agent_varna(agent_id)  # JUST DELEGATION!

def get_agent_ashrama(self, agent_id):
    return self.governance.get_agent_ashrama(agent_id)  # JUST DELEGATION!
```
These should be REMOVED. Callers use `kernel.governance.get_varna()` directly.

## Extraction Targets

### REMOVE (Dead Code) - ~40 LOC
- `get_agent_varna()` wrapper
- `get_agent_ashrama()` wrapper
- `get_agent_permissions()` wrapper
- `check_agent_permission()` wrapper
- `transition_agent_ashrama()` wrapper
- `get_governance_status()` wrapper

### EXTRACT TO PLUGINS - ~600 LOC

| Component | Current LOC | Target Plugin |
|-----------|-------------|---------------|
| ProcessManager init + methods | ~50 | ProcessPlugin |
| ResourceManager init + methods | ~40 | ResourcePlugin |
| ToolRegistry + discovery | ~100 | ToolPlugin |
| Narasimha wiring | ~80 | SecurityPlugin |
| Network proxy | ~30 | NetworkPlugin |
| Lineage chain | ~30 | LineagePlugin |
| Playbook router | ~60 | PlaybookPlugin |
| Economy (Bank/Vault) | ~50 | EconomyPlugin |
| Health checks | ~40 | HealthPlugin |
| IPC event processing | ~40 | IPCPlugin |
| Quota syncing | ~40 | QuotaPlugin |
| Repo access grants | ~30 | SandboxPlugin |

**Total extractable: ~600 LOC**
**Current: 1705 LOC**
**Target: 1008 LOC**
**Deficit: 97 LOC** - will hit it with cleanup!

## What STAYS in Kernel (Core 1008)

```python
class RealVibeKernel:
    # CORE STATE (~100 LOC)
    _agent_registry: Dict[str, VibeAgent]
    _scheduler: InMemoryScheduler
    _ledger: VibeLedger
    _manifest_registry: ManifestRegistry
    _status: KernelStatus
    _plugins: List[KernelPlugin]
    _capability_registry: CapabilityRegistry
    io: KernelIOService

    # CORE METHODS (~400 LOC)
    __init__()           # Boot only - loads plugins, they init their stuff
    boot()               # Start kernel
    tick()               # Main loop
    shutdown()           # Graceful stop
    register_agent()     # Agent registration
    submit_task()        # Task submission

    # PLUGIN API (~200 LOC)
    api(plugin_id)       # Get plugin API
    _call_hooks()        # Call plugin hooks

    # PROPERTIES (~100 LOC)
    agent_registry
    scheduler
    ledger
    manifest_registry
    status
    config

    # UTILITY (~200 LOC)
    _pulse()             # Heartbeat
    get_status()         # Status report
    record_verified_event()
    find_agents_by_capability()
```

## Extraction Order

### Phase 1: Remove Dead Code (TODAY)
1. Delete governance wrapper methods
2. Update callers to use `kernel.governance.X()` directly
3. Test suite passes

### Phase 2: Low-Risk Extractions (THIS WEEK)
1. **ToolPlugin** - ToolRegistry is already isolated
2. **EconomyPlugin** - Bank/Vault are already lazy-loaded
3. **HealthPlugin** - `_check_system_health()` is self-contained

### Phase 3: Medium-Risk Extractions
4. **ProcessPlugin** - ProcessManager is isolated
5. **ResourcePlugin** - ResourceManager is isolated
6. **LineagePlugin** - LineageChain is isolated

### Phase 4: High-Risk Extractions
7. **SecurityPlugin** - Narasimha is critical
8. **NetworkPlugin** - Network proxy
9. **PlaybookPlugin** - Playbook router

## Safety Features (Senior Review - Gemini)

Already implemented in `plugin_protocol.py`:
- `dependencies` property (topological sort)
- `on_boot(kernel, config)` (config injection)
- `HookResult` (error boundaries)
- `get_api()` (plugin API registration)

## Success Criteria

1. `kernel_impl.py` = EXACTLY 1008 LOC (Visnu's names)
2. Tests pass without loading all managers
3. Each plugin independently testable
4. Boot time < 1 second (currently 4-5s)
5. `kernel.governance` accessed directly, not via wrappers

## LOC Tracking

```
START:     1705 LOC
Phase 1:   -43 LOC  (wrapper removal) = 1662 LOC ✅ DONE 2025-12-06
Phase 2:  -109 LOC  (ToolPlugin extraction) = 1553 LOC ✅ DONE 2025-12-06
Phase 3:  -??? LOC  (Economy+Health) = ???? LOC
Phase 4:  -??? LOC  (Process+Resource+Lineage) = ???? LOC
Phase 5:  -??? LOC  (Security+Network+Playbook) = ???? LOC
Target:   1008 LOC (remaining: 545 LOC to extract)
```

### Extraction Log

| Date | Phase | Component | LOC Removed | New LOC |
|------|-------|-----------|-------------|---------|
| 2025-12-06 | 1 | Governance wrappers | -43 | 1662 |
| 2025-12-06 | 2 | ToolsPlugin | -109 | 1553 |
