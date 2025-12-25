# OPUS-307-CONSOLIDATION: System-Wide Registry Unification

## Problem

Multiple fragmented registries/loaders for the same concerns:

| Module Type | Fragmentation | Status |
|-------------|---------------|--------|
| Cartridges | 3 registries (ManifestRegistry, CartridgeRegistry, LazyCartridgeRegistry) | ✅ FIXED |
| Plugins | PluginLoader + ManifestRegistry direct usage | ✅ FIXED |
| Circuits | CircuitEngine direct ManifestRegistry | ✅ FIXED |
| Tools | ToolDiscovery → CartridgeService | ✅ FIXED |
| Sections | SectionLoader → SectionService | ✅ FIXED |
| Prompts | PromptRegistry (already unified) | ✅ VERIFIED |
| CLI Bridges | Full coverage for all services | ✅ COMPLETE |

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

## Phase C: Circuits [COMPLETE]

### Before
```
CircuitEngine:
  ManifestRegistry.get_enabled("circuit") → direct
  No DI registration
```

### After
```
Boot:
  CircuitService.scan() → single scan
  ServiceRegistry.register(CircuitServiceProtocol, circuit_svc)

Kernel + CLI:
  ServiceRegistry.get(CircuitServiceProtocol)
```

### Files
- `vibe_core/protocols/circuit.py` - Protocol definition
- `vibe_core/circuit_service.py` - Unified service (24 circuits)
- `vibe_core/boot_orchestrator.py` - DI registration

---

## Phase D: Tools [COMPLETE]

### Before
```
ToolDiscovery:
  Direct cartridge scanning
  Duplicate of CartridgeService.scan()
```

### After
```
ToolDiscovery:
  Uses CartridgeService.get_instance()
  No duplicate scanning
```

### Files
- `vibe_core/tool_discovery.py` - Modified to use CartridgeService

---

## Phase E: Sections (Phoenix) [COMPLETE]

### Before
```
SectionLoader:
  ManifestRegistry.get_enabled("section")
  No DI registration
```

### After
```
Boot:
  SectionService.scan() → single scan
  ServiceRegistry.register(SectionServiceProtocol, section_svc)

Kernel + CLI:
  ServiceRegistry.get(SectionServiceProtocol)
```

### Files
- `vibe_core/protocols/section.py` - Protocol definition
- `vibe_core/section_service.py` - Unified service (18 sections)
- `vibe_core/boot_orchestrator.py` - DI registration

---

## Phase F: Prompts [VERIFIED]

### Status
- `PromptRegistry` in `vibe_core/runtime/prompt_registry.py`
- Already unified - single registry, single cache
- 7 prompts across 2 namespaces (genesis, research)

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
- [x] Phase G: CLI Bridges (complete coverage)

---

## Phase G: CLI Bridges [COMPLETE]

### CLI Coverage

| Command | Service | Subcommands |
|---------|---------|-------------|
| `steward config` | config/ YAML | list, show, validate |
| `steward prompts` | PromptRegistry | list, get, info |
| `steward sections` | SectionService | list, info |
| `steward plugins` | PluginService | list, info, status |
| `steward circuit` | CircuitService | list, run, info |
| `steward tool` | CartridgeService | list, run, info |

### Files
- `vibe_core/cli/config_cli.py` - Config YAML management
- `vibe_core/cli/prompts_cli.py` - Prompt registry access
- `vibe_core/cli/sections_cli.py` - Phoenix sections
- `vibe_core/cli/plugins_cli.py` - Plugin registry
- `vibe_core/cli/unified_cli.py` - Help section for OPUS-307

### Verification
```bash
# All OPUS-307 CLIs
steward config list           # 26 configs
steward config validate       # All valid
steward prompts list          # 7 prompts, 2 namespaces
steward prompts info          # Registry status
steward sections list         # 18 sections
steward plugins list          # 25 plugins
steward plugins status        # Boot order summary
```

---

*"Ein System, ein Service, ein Cache."*
