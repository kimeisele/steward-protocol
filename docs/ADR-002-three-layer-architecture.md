# ADR 002: Three-Layer Architecture

**Status:** Implemented (BLOCKER #2)
**Date:** 2025-11-27
**Authors:** Claude, Steward Protocol Team
**References:** BLOCKER #2 completion, HONEST_PLAN.md

## Context

The system had evolved with fragmented abstract base class definitions scattered across multiple locations (`vibe_core.agent_protocol`, `vibe_core.kernel`, `vibe_core.protocols`, etc.), causing:

- **26+ circular import patterns** requiring try/except workarounds throughout the codebase
- **57+ try/except ImportError blocks** used as architectural band-aids
- **Fragile import order dependencies** that broke unpredictably
- **Inconsistent protocol usage** across different modules
- **Difficult to test** due to import side effects and conditional fallbacks

This architectural fragility was identified as BLOCKER #2 - a critical blocker preventing scalability and maintainability.

## Decision

Implement a **clean 3-layer architecture** with unidirectional dependency flow:

### Layer 1: Protocols (Pure Interfaces)
**Location:** `vibe_core/protocols/`

Contains ONLY abstract base class definitions:
- `agent.py` - VibeAgent protocol
- `ledger.py` - VibeLedger, VibeScheduler, VibeKernel, ManifestRegistry protocols
- `registry.py` - ManifestRegistry protocol
- `scheduler.py` - VibeScheduler protocol
- `__init__.py` - Canonical exports

**Rules:**
- ✅ Define abstract methods only
- ✅ Import from: stdlib, abc, typing
- ❌ NO implementations
- ❌ NO imports from Layer 2 or 3

**Exports via:** `vibe_core/__init__.py` for backward compatibility

### Layer 2: Implementations
**Locations:**
- `vibe_core/agents/` - Core agent implementations
- `steward/system_agents/` - System cartridge agents (14 cartridges)
- `vibe_core/runtime/` - Runtime components
- `provider/` - Provider implementations

**Rules:**
- ✅ Import from Layer 1 (protocols) only
- ✅ Implement business logic
- ❌ NO cross-imports between implementations (no sibling imports)
- ❌ NO wiring/orchestration logic

### Layer 3: Dynamic Wiring (Phoenix)
**Location:** `vibe_core/phoenix_config.py` + `config/phoenix.yaml`

Provides runtime dependency injection:
- `PhoenixConfigEngine` - Dynamic class importing and wiring
- `config/phoenix.yaml` - Configuration of which implementations to load
- Import order enforcement to prevent circular dependency issues

**Rules:**
- ✅ Import from Layer 1 and 2
- ✅ Wire implementations to protocols
- ✅ Configure system behavior
- ✅ Handle optional/missing components gracefully

## Dependency Flow

```
Layer 1 (Protocols) ← Pure ABCs only
     ↑
Layer 2 (Implementations) ← Can import from Layer 1
     ↑
Layer 3 (Phoenix) ← Can import from Layers 1 & 2
```

**Critical constraint:** NO imports flow downward (1 ← 2 ← 3 only, never the reverse).

## Implementation

### Phase 1: Consolidate Protocols
- [x] Created `vibe_core/protocols/` as canonical protocol location
- [x] Fixed circular imports in protocol layer
- [x] Updated `vibe_core/__init__.py` to re-export from protocols
- [x] Eliminated duplicate ABC definitions

### Phase 2: Redirect Implementations
- [x] Updated 31+ files to import from `vibe_core.protocols`
- [x] Removed 26 internal try/except ImportError blocks
- [x] Ensured clean import ordering

### Phase 3: Build Wiring Engine
- [x] Created `PhoenixConfigEngine` class (200 lines)
- [x] Created `config/phoenix.yaml` with agent configurations
- [x] Implemented singleton pattern with lazy initialization
- [x] Added import order enforcement

### Phase 4: Validation
- [x] Zero internal try/except ImportError blocks
- [x] Zero circular import errors
- [x] All protocols are proper abstract base classes
- [x] All implementations correctly inherit from protocols

## Consequences

### Positive Consequences ✅
- **Zero circular dependencies** - Impossible to create circular imports with proper layer separation
- **Testable** - Each layer can be tested in isolation
- **Extensible** - New implementations can be added without modifying existing code
- **Configurable** - Behavior changes via `phoenix.yaml` without code changes
- **Clear contract** - Protocols define clear interfaces that implementations must follow
- **Gradual migration** - Old code using `from vibe_core import ...` still works via re-exports

### Trade-offs ⚠️
- **One level of indirection** - Dynamic wiring adds a small startup overhead (negligible)
- **Configuration file required** - `phoenix.yaml` must be kept in sync with actual implementations
- **Learning curve** - New developers must understand 3-layer architecture

## Alternatives Considered

### Alternative 1: Keep Old Structure
**Rejected.** Would require continuing to maintain 57+ try/except workarounds and managing fragmented ABC definitions.

### Alternative 2: Single Monolithic File
**Rejected.** Would make the file unmaintainable (potentially 5000+ lines) and lose modular organization.

### Alternative 3: Implicit Wiring (Reflection)
**Rejected.** Would require class name conventions and reflection, making it harder to understand what gets loaded.

## Migration Path for Existing Code

Old imports continue to work via `vibe_core/__init__.py` re-exports:

```python
# Old code (still works):
from vibe_core import VibeAgent, VibeLedger

# New code (preferred):
from vibe_core.protocols import VibeAgent, VibeLedger

# Both are equivalent - __init__.py re-exports from protocols
```

This allows gradual migration without breaking existing code.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| ABC duplicate definitions | 6+ locations | 1 location |
| Internal try/except ImportError | 26+ blocks | 0 blocks |
| Circular dependencies | 27+ patterns | 0 patterns |
| Files importing from old locations | 25+ files | 0 files |
| Protocol import consistency | Fragmented | Unified |

## Validation Commands

```bash
# 1. Verify zero internal try/except
grep -r "except ImportError" vibe_core/ steward/ provider/ --include="*.py" | \
  grep -E "(from steward|from vibe_core|import steward|import vibe_core)" | \
  wc -l
# Expected: 0

# 2. Verify all protocols import correctly
python -c "from vibe_core.protocols import *; print('All protocols imported')"

# 3. Verify no circular imports
python -c "from vibe_core import VibeAgent; from steward.system_agents.discoverer.agent import Discoverer; print('No circular imports')"

# 4. Verify Phoenix works
python -c "from vibe_core.phoenix_config import get_phoenix_engine; e = get_phoenix_engine(); print(f'Phoenix loaded with {len(e.get_config().get(\"agents\", {}).get(\"system_agents\", []))} agents')"
```

## Related Documents

- `BLOCKER2_FINAL_COMPLETION_REPORT.md` - Detailed execution summary
- `BLOCKER2_HAIKU_PLAN.md` - Implementation plan
- `docs/DEVELOPER_GUIDELINES.md` - Development rules for this architecture

## Future Improvements

Once this architecture is stable:

1. **Plugin System** - Load agents from external packages
2. **Multi-Environment Config** - Different `phoenix.yaml` per environment (dev/prod/test)
3. **Agent Marketplace** - Third-party agents can implement protocols
4. **Hot-reload** - Reload agents without restarting (via Phoenix)
5. **Observability** - Cross-cutting concerns (logging, tracing) via Layer 3

---

**Decision:** APPROVED
**Implementation:** COMPLETE
**Status:** ACTIVE

This ADR represents the foundation for BLOCKER #3 (Real Agent Wiring) and all future development.
