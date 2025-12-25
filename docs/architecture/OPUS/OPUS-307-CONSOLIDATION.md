# OPUS-307-CONSOLIDATION: System-Wide Registry Unification

## Problem

Multiple fragmented registries/loaders for the same concerns:

| Module Type | Fragmentation | Status |
|-------------|---------------|--------|
| Cartridges | 3 registries (ManifestRegistry, CartridgeRegistry, LazyCartridgeRegistry) | ✅ FIXED |
| Plugins | PluginLoader + ManifestRegistry direct usage | ✅ FIXED |
| Circuits | CircuitEngine direct ManifestRegistry | PENDING |
| Tools | ToolRegistry + CartridgeService.load_tool | PENDING |
| Sections | SectionLoader | PENDING |
| Prompts | PromptRegistry | TO VERIFY |

**Violation:** GAD-000 says ONE service per concern, accessed via DI.

---

## Phase A: Cartridges [COMPLETE]

### Before
```
Boot:
  ManifestRegistry.scan_all() → finds YAMLs
  CartridgeRegistry._auto_discover() → loads classes

CLI:
  LazyCartridgeRegistry.scan_manifests() → separate scan

Kernel:
  kernel.register_agent() → receives already-loaded agents
```

### After
```
Boot:
  CartridgeService.scan() → single scan, single cache
  ServiceRegistry.register(CartridgeProtocol, cartridge_svc)

CLI + Kernel:
  ServiceRegistry.get(CartridgeProtocol) → same service
```

### Files
- `vibe_core/protocols/cartridge.py` - Protocol definition
- `vibe_core/cartridge_service.py` - Unified service
- `vibe_core/cartridges/registry.py` - Delegates to CartridgeService
- `vibe_core/cli/cartridge_bridge.py` - Delegates to CartridgeService
- `vibe_core/boot_orchestrator.py` - DI registration

---

## Phase B: Plugins [COMPLETE]

### Before
```
Kernel:
  PluginLoader.discover_and_load() → direct call
  No DI registration
```

### After
```
Boot:
  PluginService.scan() → single scan
  ServiceRegistry.register(PluginServiceProtocol, plugin_svc)

Kernel + CLI:
  ServiceRegistry.get(PluginServiceProtocol)
```

### Files
- `vibe_core/protocols/plugin.py` - Protocol definition
- `vibe_core/plugin_service.py` - Unified service
- `vibe_core/boot_orchestrator.py` - DI registration

---

## Phase C: Circuits [PENDING]

### Current State
- `CircuitEngine` in `vibe_core/cortex/engines/circuit_engine.py`
- Uses ManifestRegistry directly
- No CircuitService

### Target
- `CircuitProtocol` - Protocol definition
- `CircuitService` - Unified service
- DI registration

---

## Phase D: Tools [PENDING]

### Current State
- `ToolRegistry` in `vibe_core/tools/tool_registry.py` - Governance/capability checks
- `CartridgeService.load_tool()` - Tool loading from cartridges
- Two paths to tools

### Target
- Harmonize: ToolRegistry uses CartridgeService for discovery
- Or: Unified ToolService

---

## Phase E: Sections (Phoenix) [PENDING]

### Current State
- `SectionLoader` in `vibe_core/phoenix/section_loader.py`
- Uses ManifestRegistry

### Target
- `SectionProtocol`
- `SectionService`
- DI registration

---

## Phase F: Prompts [TO VERIFY]

### Current State
- `PromptRegistry` in `vibe_core/runtime/prompt_registry.py`
- Check if truly unified

---

## Success Criteria

1. Every module type has: Protocol → Service → DI
2. Single scan at boot, single cache per type
3. CLI and Kernel use same services
4. No duplicate code paths
5. `ServiceRegistry.get(XProtocol)` works everywhere

---

## Status

- [x] Phase A: Cartridges (CartridgeService)
- [x] Phase B: Plugins (PluginService)
- [x] Phase C: Circuits (CircuitService)
- [x] Phase D: Tools (ToolDiscovery → CartridgeService)
- [x] Phase E: Sections (SectionService)
- [x] Phase F: Prompts (already unified - PromptRegistry)

---

*"Ein System, ein Service, ein Cache."*
