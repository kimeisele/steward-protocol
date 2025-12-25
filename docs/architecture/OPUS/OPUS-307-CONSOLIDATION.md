# OPUS-307-CONSOLIDATION: Registry Unification

## Problem

Drei Registries für Cartridges:

| Registry | Location | Purpose | Used By |
|----------|----------|---------|---------|
| `ManifestRegistry` | `loaders/manifest_registry.py` | Scans YAML manifests | Boot, Discovery |
| `CartridgeRegistry` | `cartridges/registry.py` | Loads cartridge classes | Kernel |
| `LazyCartridgeRegistry` | `cli/cartridge_bridge.py` | CLI tool discovery | CLI only |

**Violation:** GAD-000 says ONE service per concern, accessed via DI.

## Current Flow (Fragmented)

```
Boot:
  ManifestRegistry.scan_all() → finds YAMLs
  CartridgeRegistry._auto_discover() → loads classes

CLI:
  LazyCartridgeRegistry.scan_manifests() → separate scan
  CartridgeBridgeCLI → wraps cartridges for CLI

Kernel:
  kernel.register_agent() → receives already-loaded agents
```

Three separate scans. Three separate caches. Inconsistent.

## Target Flow (Unified)

```
Boot:
  CartridgeService.initialize() → single scan, single cache

CLI:
  ServiceRegistry.get(CartridgeProtocol) → same service

Kernel:
  ServiceRegistry.get(CartridgeProtocol) → same service
```

## Implementation Plan

### Phase 1: Protocol Definition

```python
# vibe_core/protocols/cartridge.py
class CartridgeProtocol(Protocol):
    def scan(self) -> int: ...
    def get(self, cartridge_id: str) -> CartridgeInfo: ...
    def list(self) -> List[CartridgeInfo]: ...
    def load_tool(self, cartridge_id: str, tool_id: str) -> Tool: ...
```

### Phase 2: Unified Service

```python
# vibe_core/services/cartridge_service.py
class CartridgeService(CartridgeProtocol):
    """Single source of truth for cartridges."""

    def __init__(self):
        self._manifests: Dict[str, ManifestEntry] = {}
        self._classes: Dict[str, Type] = {}
        self._tools: Dict[str, ToolStub] = {}
```

### Phase 3: DI Registration

```python
# vibe_core/di.py or boot
ServiceRegistry.register(CartridgeProtocol, CartridgeService())
```

### Phase 4: Migration

1. `CartridgeRegistry` → delegates to `CartridgeService`
2. `LazyCartridgeRegistry` → delegates to `CartridgeService`
3. `ManifestRegistry` → kept for generic manifest scanning, cartridge-specific logic moves out

### Phase 5: Cleanup

- Remove duplicate scanning logic
- Remove duplicate caches
- Single source of truth

## Files Affected

| File | Change |
|------|--------|
| `vibe_core/protocols/cartridge.py` | NEW - Protocol definition |
| `vibe_core/services/cartridge_service.py` | NEW - Unified service |
| `vibe_core/cartridges/registry.py` | MODIFY - Delegate to service |
| `vibe_core/cli/cartridge_bridge.py` | MODIFY - Use service |
| `vibe_core/loaders/manifest_registry.py` | MODIFY - Remove cartridge-specific |
| `vibe_core/di.py` | MODIFY - Register service |

## Success Criteria

1. `ServiceRegistry.get(CartridgeProtocol)` works everywhere
2. Single scan at boot, single cache
3. CLI and Kernel use same data
4. No duplicate code

## Status

- [x] Phase 1: Protocol (`vibe_core/protocols/cartridge.py`)
- [x] Phase 2: Service (`vibe_core/cartridge_service.py`)
- [x] Phase 3: DI Registration (`boot_orchestrator.py`)
- [x] Phase 4: Migration (CartridgeRegistry, LazyCartridgeRegistry delegate to CartridgeService)
- [x] Phase 5: Cleanup (ManifestRegistry kept for generic scanning)

---

*"Drei Registries sind zwei zu viel."*
