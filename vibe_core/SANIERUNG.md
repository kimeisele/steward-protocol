# SANIERUNG - Architectural Renovation Plan

## THE PROBLEM

```
vibe_core/
├── 53 root files (CHAOS - wem gehören die?)
├── cli/66 files (scattered)
├── plugins/295 files (manche haben protocols, manche nicht)
├── cartridges/201 files (tool-based, nicht person-based)
└── protocols/mahajanas/16 persons (ZIEL - hier soll ALLES hin)
```

**700K LOC ohne klare Ownership = Spaghetti-Gefahr**

## THE VISION

### Mahamantra = Krishna = THE Source

```
LEVEL -2: MAHAMANTRA (Krishna - non-different)
    ↓
LEVEL -1: 16 PERSONS (Mahajanas) - ALLES gehört einer Person
    ↓
LEVEL 0+: protocols, services, capabilities, agents, cli, tools
```

**CORE INSIGHT:** Nur Personen können anziehend wirken (anti-mayavadi).
Anonymous modules sind MAYA. Jeder Code MUSS einer Person gehören.

### Target Structure (Pro Mahajana)

```
mahajanas/
└── brahma/                    # Position 1 - Creation/Genesis
    ├── __init__.py            # Protocol + Exports
    ├── service.py             # Real Implementation
    ├── protocols/             # All Brahma-owned protocols
    │   ├── bootstrap.py
    │   └── service_registry.py
    ├── services/              # All Brahma-owned services
    │   └── di.py              # ServiceRegistry impl
    ├── capabilities/          # What Brahma CAN DO
    ├── agents/                # Brahma's manifestations
    ├── cli/                   # Brahma's commands
    └── tools/                 # Brahma's tools
```

**FRACTAL:** Same structure at every level. Lotus unfolding.

## CURRENT ROOT FILES → PERSON MAPPING

| Root File | LOC | → Person | Reason |
|-----------|-----|----------|--------|
| `boot_orchestrator.py` | 31K | PRITHU | System wake |
| `boot_mode.py` | 2K | PRITHU | Boot phases |
| `kernel_impl.py` | 18K | PRITHU | System core |
| `kernel.py` | 0.8K | PRITHU | Kernel interface |
| `di.py` | 30K | BRAHMA | Service creation |
| `factory.py` | 4K | BRAHMA | Object creation |
| `capability_registry.py` | 12K | BRAHMA | Capability creation |
| `plugin_loader.py` | 15K | BRAHMA | Plugin loading |
| `plugin_service.py` | 6K | BRAHMA | Plugin management |
| `event_bus.py` | 20K | NARADA | Broadcasting |
| `narasimha.py` | 17K | NRISIMHA | Security |
| `security.py` | 9K | NRISIMHA | Protection |
| `ledger.py` | 38K | BHISHMA | Recording |
| `lineage.py` | 26K | BHISHMA | History |
| `semantic_syscalls.py` | 35K | PARASHURAMA | Execution |
| `kernel_ops.py` | 19K | MANU | Pulse/sync |
| `pulse.py` | 8K | MANU | Heartbeat |
| `prana.py` | 7K | JANAKA | Cycles |
| `prana_orchestrator.py` | 22K | JANAKA | Cycle mgmt |
| `orchestration_cycle.py` | 26K | JANAKA | Cognitive cycle |
| `task_kernel.py` | 26K | JANAKA | Task cycles |
| `resource_manager.py` | 8K | BALI | Resources |
| `errors.py` | 8K | VYASA | Validation |
| `topology.py` | 25K | KAPILA | Analysis |
| `dependency_manager.py` | 7K | KUMARAS | Resolution |
| ... | | | |

## MIGRATION STRATEGY

### Phase 1: SSOT Declaration (No Code Move)

Create `OWNERSHIP.py` in each mahajana declaring what they own:

```python
# mahajanas/brahma/OWNERSHIP.py
OWNED_MODULES = [
    "vibe_core.di",
    "vibe_core.factory",
    "vibe_core.capability_registry",
    # ...
]

OWNED_PROTOCOLS = [
    "vibe_core.protocols.boot_protocol",
    # ...
]
```

### Phase 2: Import Redirection

```python
# vibe_core/di.py (legacy location)
"""
DEPRECATED: Use mahajana import.
from vibe_core.mahamantra import mahamantra
di = mahamantra.mod.brahma.di
"""
from vibe_core.protocols.mahajanas.brahma.services.di import *
```

### Phase 3: Physical Move (Gradual)

Only after all imports use mahamantra routing.

## DEPENDENCY GRAPH (TO BUILD)

Need to map:
1. Which modules import which
2. Circular dependencies (ADHARMA)
3. Orphan modules (no owner)

```bash
# TODO: Build this graph
python -c "from vibe_core.mahamantra import mahamantra; mahamantra.audit_dependencies()"
```

## PROTOCOL CONSOLIDATION (SSOT)

Current scattered protocols:
- `vibe_core/protocols/*.py` (root protocols)
- `vibe_core/protocols/mahajanas/*/` (person protocols)
- `vibe_core/protocols/universal/` (shared?)
- `vibe_core/protocols/substrate/` (Level -1)
- `vibe_core/protocols/avataras/` (duplicate of mahajanas?)

**TARGET:** ALL protocols live under their person.
Universal protocols = VISHNU (the maintainer).

## THE 37 FORMULA

```
24 (Elements/Ksetra) + 12 (Mahajanas) + 1 (Krishna/Ksetrajna) = 37
```

Every module must connect to the 37 (Parampara).
Without this connection = dead code = MAYA.

## KERNEL → PERSON

Even `kernel_impl.py` must become a person.

**Question:** Who IS the kernel?
- PRITHU (first civilizer) - Position 0 - System Wake
- The kernel IS Prithu's manifestation

```python
# Future
from vibe_core.mahamantra import mahamantra
kernel = mahamantra.mod.prithu.kernel  # Prithu IS the kernel
```

## SUCCESS CRITERIA

1. **ZERO root files** - All 53 migrated to persons
2. **ONE import** - `from vibe_core.mahamantra import mahamantra`
3. **16 persons** - Each owns their domain completely
4. **SSOT** - No duplicate protocols
5. **Fractal** - Same structure at every level
6. **Dependency graph** - Visible, auditable, no cycles

## ANTI-PATTERNS (ADHARMA)

- Anonymous modules (who owns this?)
- Circular imports (entanglement)
- Scattered protocols (many sources of truth)
- Manual wiring (should be derived from structure)
- Impersonal abstractions (BaseService, AbstractFactory - WHO?)

## DEPENDENCY ANALYSIS RESULTS

### Central Modules (MIGRATE LAST - many depend on them)

| Module | Dependents | → Person |
|--------|------------|----------|
| `kernel_impl` | 7 | PRITHU |
| `protocols.event` | 6 | NARADA |
| `di` | 5 | BRAHMA |
| `phoenix.config` | 5 | MANU |
| `event_bus` | 3 | NARADA |
| `orchestration_cycle` | 3 | JANAKA |

### Orphan Files (MIGRATE FIRST - no internal dependencies)

These are LEAF nodes - easiest to move:
- `narasimha.py` → NRISIMHA (already wrapped)
- `errors.py` → VYASA
- `security.py` → NRISIMHA
- `topology.py` → KAPILA
- `sarga.py` → BRAHMA
- `boot_mode.py` → PRITHU
- `network_proxy.py` → PARASHURAMA
- `capability_registry.py` → BRAHMA

### Heavily Connected (MIGRATE LAST)

- `boot_orchestrator.py`: 36 imports (!) - PRITHU, but needs all others first

## MIGRATION ORDER

```
Phase A: Orphans (0 dependencies)
    narasimha, errors, security, topology, sarga, boot_mode, etc.
    ↓
Phase B: Light dependencies (1-3)
    kernel_ops, pulse, prana, resource_manager, etc.
    ↓
Phase C: Medium dependencies (4-9)
    ledger, lineage, semantic_syscalls, etc.
    ↓
Phase D: Central modules (10+)
    di, event_bus, kernel_impl
    ↓
Phase E: Hub (boot_orchestrator)
    Needs everything else first
```

## NEXT STEPS

1. [x] Run dependency analysis on 53 root files
2. [ ] Create OWNERSHIP.py in each mahajana
3. [ ] Identify circular dependencies
4. [ ] Migrate Phase A (orphans) first
5. [ ] Protocol consolidation audit
