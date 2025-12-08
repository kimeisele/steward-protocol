# OPUS-005: Unification Roadmap

> **Status**: IN PROGRESS
> **Created**: 2025-12-08
> **Scope**: Consolidate duplicate components into unified patterns

---

## Executive Summary

The Steward Protocol has made good progress on unification (UnifiedLoader, UnifiedRouter, UnifiedExecutor) but several components remain fragmented. This document tracks what IS unified, what CLAIMS to be unified, and what NEEDS unification.

---

## Current State

### Unified Components (Working)

| Component | Location | Tests | Status |
|-----------|----------|-------|--------|
| UnifiedLoader | `loaders/base_loader.py` | 29 | COMPLETE |
| UnifiedRouter | `runtime/unified_execution.py` | 8 | COMPLETE |
| LayeredRouter | `runtime/layered_router.py` | 40 | COMPLETE |
| UnifiedExecutor | `runtime/unified_execution.py` | Yes | COMPLETE |

### Fragmented Components (Need Unification)

| Component | Problem | Priority |
|-----------|---------|----------|
| CLI System | Two separate implementations | HIGH |
| PlaybookRouter | Exists in 2 locations | MEDIUM |
| Remaining Loaders | 5 loaders not migrated | MEDIUM |
| CircuitExecutor | 1394-line monolith | LOW |

---

## Phase 1: CLI Unification (HIGH PRIORITY)

### Problem

Two CLI systems exist:

1. **StewardCLI** (`vibe_core/cli.py`)
   - Traditional class-based CLI
   - Direct subprocess spawning
   - No plugin integration

2. **Fractal CLI** (`vibe_core/cli/`)
   - Plugin-based command discovery
   - CLILoader + CLIExecutor + CLIRenderer
   - Execution modes (OFFLINE, RPC, BOOT, HYBRID)

### Solution

Create `UnifiedCLI` that:
- Uses Fractal CLI's plugin-based discovery
- Supports StewardCLI's traditional commands
- Single entry point for all CLI operations

### Files to Modify

```
vibe_core/cli/unified_cli.py      # NEW - Single entry point
vibe_core/cli.py                  # DEPRECATE - Mark legacy
vibe_core/cli/__init__.py         # Export UnifiedCLI
```

### Verification

```bash
# Both should work identically:
python -m vibe_core.cli status
python -m vibe_core.cli.unified_cli status
```

---

## Phase 2: Legacy Router Cleanup (MEDIUM PRIORITY)

### Problem

PlaybookRouter exists in TWO locations:
- `vibe_core/playbook/router.py`
- `vibe_core/runtime/playbook_router.py`

UnifiedRouter was designed to replace these, but they weren't removed.

### Solution

1. Verify UnifiedRouter handles all cases
2. Mark legacy routers as `@deprecated`
3. Remove after confirmation period

### Files to Modify

```
vibe_core/playbook/router.py         # ADD @deprecated
vibe_core/runtime/playbook_router.py # ADD @deprecated or DELETE
```

---

## Phase 3: Loader Migration (MEDIUM PRIORITY)

### Problem

UnifiedLoader exists but 5 loaders haven't migrated:

| Loader | Location | Status |
|--------|----------|--------|
| PlaybookLoader | `playbook/loader.py` | NOT MIGRATED |
| KnowledgeLoader | `knowledge/loader.py` | NOT MIGRATED |
| ContextLoader | `runtime/context_loader.py` | NOT MIGRATED |
| TemplateLoader | `loaders/template_loader.py` | NOT MIGRATED |
| CircuitLoader | `loaders/circuit_loader.py` | NOT MIGRATED |

### Solution

Migrate each loader to inherit from UnifiedLoader:

```python
# Before:
class PlaybookLoader:
    def load(self, path): ...

# After:
class PlaybookLoader(UnifiedLoader):
    def _find_manifest(self, path): ...
    def _validate_manifest(self, manifest): ...
    def _load_entry_class(self, manifest): ...
```

### VEDA-4 Pattern (From UnifiedLoader)

```
SHABDA   → _find_manifest()      # Discovery
ARTHA    → _validate_manifest()  # Validation
PRATYAYA → _load_config()        # Configuration
KARMA    → _load_entry_class()   # Instantiation
```

---

## Phase 4: CircuitExecutor Refactor (LOW PRIORITY)

### Problem

`circuit_executor.py` is 1394 lines containing:
- CognitiveCircuitExecutor
- GraphExecutor
- Meta-circuit management
- Multiple inner classes

### Solution

Split into focused modules:
```
vibe_core/runtime/executors/
├── __init__.py
├── cognitive.py      # CognitiveCircuitExecutor
├── graph.py          # GraphExecutor
└── deterministic.py  # DeterministicExecutor (already separate)
```

---

## Non-Goals (Out of Scope)

- Changing plugin architecture (backward compatibility)
- Adding new CLI commands
- Performance optimization

---

## Verification Checklist

### Phase 1 (CLI):
- [ ] UnifiedCLI class exists
- [ ] `python -m vibe_core.cli` uses UnifiedCLI
- [ ] All existing CLI tests pass
- [ ] StewardCLI marked @deprecated

### Phase 2 (Routers):
- [ ] Legacy routers marked @deprecated
- [ ] UnifiedRouter handles all routing cases
- [ ] No code references legacy routers

### Phase 3 (Loaders):
- [ ] PlaybookLoader inherits UnifiedLoader
- [ ] KnowledgeLoader inherits UnifiedLoader
- [ ] ContextLoader inherits UnifiedLoader
- [ ] All loader tests pass

### Phase 4 (Executors):
- [ ] CircuitExecutor split into modules
- [ ] All executor tests pass
- [ ] Clear documentation

---

## Success Metrics

1. **Single source of truth** for each component type
2. **No duplicate implementations** across codebase
3. **Consistent patterns** (VEDA-4 for loaders, etc.)
4. **100% test coverage** for unified components

---

## Related Documents

- OPUS-001: Memory Migration
- OPUS-002: Phoenix Config Extraction
- OPUS-003: AOS Foundation Repair
- OPUS-004: Boot Sequence Audit
