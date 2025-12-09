# OPUS-005: Unification Roadmap

> **Status**: ✅ MOSTLY COMPLETE (5/7 phases done)
> **Created**: 2025-12-08
> **Last Updated**: 2025-12-09
> **Scope**: Consolidate duplicate components into unified patterns
> **GAD-000**: All phases require GAD-000 compliance as Definition of Done

---

## Executive Summary

The Steward Protocol has made good progress on unification (UnifiedLoader, UnifiedRouter, UnifiedExecutor) but several components remain fragmented. This document tracks what IS unified, what CLAIMS to be unified, and what NEEDS unification.

---

## GAD-000 Definition of Done (DoD)

> **CRITICAL**: GAD-000 is not a phase - it's the acceptance criteria for ALL phases.
> See: OPUS-006 GAD-000 Compliance Audit for detailed requirements.

Every phase completion MUST pass these GAD-000 tests:

| Test | Requirement | Verification |
|------|-------------|--------------|
| **Parseability** | All errors are `StructuredError` with error codes | `except StructuredError as e: assert e.code` |
| **Discoverability** | Public APIs return structured capability schemas | `kernel.get_capabilities()` returns dict |
| **Composability** | All outputs are dict/dataclass, never raw strings | `isinstance(result, dict)` |

### Phase-Specific GAD-000 Requirements

| Phase | Must Pass |
|-------|-----------|
| Phase 1 (CLI) | Discoverability: `--help --json` returns capability schema |
| Phase 1 (CLI) | Parseability: CLI errors are `StructuredError` |
| Phase 2 (Routers) | Composability: `RouteResult` is dataclass, not string |
| Phase 3 (Loaders) | Parseability: Load failures return `ErrorCode.E2001_INVALID_*` |
| Phase 4 (Executors) | All 3 tests: Structured errors, capability discovery, dict output |

---

## Current State

### Unified Components (Working) - VERIFIED 2025-12-09

| Component | Location | Tests | Status |
|-----------|----------|-------|--------|
| UnifiedLoader | `loaders/base_loader.py` | 29 | ✅ COMPLETE |
| UnifiedRouter | `runtime/unified_execution.py` | 8 | ✅ COMPLETE |
| LayeredRouter | `runtime/layered_router.py` | 40 | ✅ COMPLETE |
| UnifiedExecutor | `runtime/unified_execution.py` | Yes | ✅ COMPLETE |
| **UnifiedCLI** | `cli/unified_cli.py` | Yes | ✅ COMPLETE |
| **UnifiedTrace** | `runtime/unified_trace.py` | Yes | ✅ COMPLETE |

### Remaining Work

| Component | Problem | Priority | Status |
|-----------|---------|----------|--------|
| PlaybookRouter | Exists in 2 locations | MEDIUM | TODO |
| Remaining Loaders | 5 loaders not migrated | MEDIUM | TODO |
| CircuitExecutor | 1394-line monolith | LOW | TODO |
| Legacy Code | @deprecated but not deleted | MEDIUM | TODO |
| Manifest deps | Magic priority numbers | MEDIUM | TODO |

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

## Phase 5: Unified Telemetry (Observability Infrastructure)

> **Implements GAD-000 Test 2 (Observability) infrastructure**
> Note: GAD-000 compliance is now DoD for all phases, not a separate phase

### Problem

GAD-000 Test 2 requires AI-readable system state.
Currently each component logs independently. AI cannot trace execution flow.

### Solution: UnifiedTrace

Central telemetry in `UnifiedExecutor` - the ONLY place where all execution passes through.

```python
# vibe_core/runtime/unified_trace.py
@dataclass
class TraceEvent:
    trace_id: str
    timestamp: float
    component: str  # "router", "executor", "agent"
    event_type: str  # "start", "complete", "error"
    data: Dict[str, Any]

class UnifiedTrace:
    """Central nervous system for AI observability."""

    def emit(self, event: TraceEvent) -> None:
        """Emit trace event to all registered collectors."""
        ...

    def get_trace(self, trace_id: str) -> List[TraceEvent]:
        """AI can query: what happened in this execution?"""
        ...
```

### Integration Point

```python
# In UnifiedExecutor.execute():
trace_id = self._trace.start("execute", {"circuit": circuit_id})
try:
    result = await self._execute_internal(...)
    self._trace.complete(trace_id, {"result": result})
except Exception as e:
    self._trace.error(trace_id, {"error": str(e)})
```

### GAD-000 Compliance

| GAD-000 Test | Before | After |
|--------------|--------|-------|
| Observability | Logs only | Structured traces |
| Parseability | Human text | JSON events |
| AI Self-Correct | Cannot | Query trace, retry |

---

## Phase 6: Dead Code Elimination ("Burn Notice")

> **Added per Gemini review - @deprecated is not enough**

### Problem

Legacy code with `@deprecated` tends to stay forever "just in case".

### Solution

After Phase 4, run automated check:

```bash
# scripts/verify_no_legacy_imports.py
LEGACY_FILES = [
    "vibe_core/cli.py",  # Old StewardCLI
    "vibe_core/playbook/router.py",  # Old PlaybookRouter
    "vibe_core/runtime/playbook_router.py",  # Duplicate
]

for file in LEGACY_FILES:
    if imported_anywhere(file):
        fail(f"{file} still imported!")
    else:
        rm(file)  # Physical deletion
```

### Timeline

- **Phase 4 complete** → Mark @deprecated
- **2 weeks later** → Run burn script
- **If no imports** → DELETE files

---

## Phase 7: Explicit Manifest Dependencies (OPUS-004 Upgrade)

> **Already recommended in OPUS-004, promoted to roadmap**

### Problem

Plugin boot order relies on magic priority numbers (5, 10, 15).
See OPUS-004 "Issue 3: Plugin Order Not Explicit".

### Solution

Extend `manifest.json`:

```json
{
  "id": "envoy",
  "priority": 15,
  "depends_on": ["tools"],
  "provides": ["kernel.envoy"]
}
```

### UnifiedLoader Enhancement

```python
# In UnifiedLoader._sort_by_dependencies():
def _sort_by_dependencies(self, manifests):
    """Topological sort respecting depends_on."""
    graph = {m["id"]: m.get("depends_on", []) for m in manifests}
    return topological_sort(graph)
```

### Verification

```python
# In plugin boot:
for dep in manifest.get("depends_on", []):
    if not hasattr(kernel, dep):
        raise BootError(f"{manifest['id']} requires {dep}")
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
- [ ] **GAD-000 DoD**: `--help --json` returns capability schema
- [ ] **GAD-000 DoD**: CLI errors are `StructuredError`

### Phase 2 (Routers):
- [ ] Legacy routers marked @deprecated
- [ ] UnifiedRouter handles all routing cases
- [ ] No code references legacy routers
- [ ] **GAD-000 DoD**: `RouteResult` is dataclass (already ✅)

### Phase 3 (Loaders):
- [ ] PlaybookLoader inherits UnifiedLoader
- [ ] KnowledgeLoader inherits UnifiedLoader
- [ ] ContextLoader inherits UnifiedLoader
- [ ] All loader tests pass
- [ ] **GAD-000 DoD**: Load failures return `StructuredError`

### Phase 4 (Executors):
- [ ] CircuitExecutor split into modules
- [ ] All executor tests pass
- [ ] Clear documentation
- [ ] **GAD-000 DoD**: Execution errors are `StructuredError`
- [ ] **GAD-000 DoD**: `executor.get_capabilities()` returns dict
- [ ] **GAD-000 DoD**: All outputs are dict/dataclass

### Phase 5 (Telemetry):
- [ ] UnifiedTrace class exists
- [ ] UnifiedExecutor emits trace events
- [ ] AI can query execution traces via structured API
- [ ] **GAD-000 DoD**: `kernel.get_system_status()` returns dict

### Phase 6 (Burn Notice):
- [ ] `scripts/verify_no_legacy_imports.py` exists
- [ ] Script runs in CI
- [ ] Legacy files physically deleted (not just deprecated)

### Phase 7 (Manifest Dependencies):
- [ ] `depends_on` supported in manifest.json
- [ ] UnifiedLoader performs topological sort
- [ ] Boot fails if dependency missing

---

## Success Metrics

1. **Single source of truth** for each component type
2. **No duplicate implementations** across codebase
3. **Consistent patterns** (VEDA-4 for loaders, etc.)
4. **100% test coverage** for unified components

---

## Related Documents

- **OPUS-006**: GAD-000 Compliance Audit (defines DoD tests)
- **GAD-000**: Operator Inversion Principle (foundational law)
- OPUS-001: Memory Migration
- OPUS-002: Phoenix Config Extraction
- OPUS-003: AOS Foundation Repair
- OPUS-004: Boot Sequence Audit

---

## HAIKU EXECUTION BLOCKS

> **For AI Agent Execution**: Copy-paste these blocks to implement each phase.

### TASK 1: Phase 1 - CLI Unification

```
FILE: vibe_core/cli/unified_cli.py (NEW)
CREATE:
    """UnifiedCLI - Single entry point for all CLI operations."""
    from vibe_core.cli.cli_loader import CLILoader
    from vibe_core.cli.cli_executor import CLIExecutor

    class UnifiedCLI:
        """GAD-000 compliant CLI with JSON output support."""

        def __init__(self):
            self._loader = CLILoader()
            self._executor = CLIExecutor()

        def run(self, args: list[str]) -> dict:
            """Execute CLI command, return structured result."""
            command = self._loader.parse(args)
            return self._executor.execute(command)

        def get_capabilities(self) -> dict:
            """GAD-000 Test 1: Machine-readable capability discovery."""
            return {
                "commands": self._loader.list_commands(),
                "version": "1.0",
                "json_output": True
            }

THEN:
FILE: vibe_core/cli.py
ADD_AT_TOP: import warnings
FIND: class StewardCLI:
ADD_BEFORE: @deprecated("Use UnifiedCLI instead")

VERIFY: python -c "from vibe_core.cli.unified_cli import UnifiedCLI; print(UnifiedCLI().get_capabilities())"
```

### TASK 2: Phase 2 - Legacy Router Cleanup

```
FILE: vibe_core/playbook/router.py
ADD_AT_TOP:
    import warnings
    warnings.warn("PlaybookRouter is deprecated, use UnifiedRouter", DeprecationWarning)

FILE: vibe_core/runtime/playbook_router.py
ADD_AT_TOP:
    import warnings
    warnings.warn("playbook_router is deprecated, use UnifiedRouter", DeprecationWarning)

FILE: vibe_core/plugins/interface/renderers/envoy.py
FIND: router_callback = self.kernel._playbook_router.route  # LEGACY
REPLACE_WITH:
    raise RuntimeError("Legacy PlaybookRouter no longer supported - use UnifiedRouter")

VERIFY: python -c "from vibe_core.runtime.unified_execution import UnifiedRouter; print('UnifiedRouter OK')"
```

### TASK 3: Phase 3 - Loader Migration (PlaybookLoader)

```
FILE: vibe_core/playbook/loader.py
FIND: class PlaybookLoader:
REPLACE_WITH:
    from vibe_core.loaders.base_loader import UnifiedLoader

    class PlaybookLoader(UnifiedLoader):
        """Playbook loader following VEDA-4 pattern."""

        def _find_manifest(self, path: Path) -> Optional[dict]:
            """SHABDA: Discovery - find playbook.yaml."""
            manifest_path = path / "playbook.yaml"
            if manifest_path.exists():
                return yaml.safe_load(manifest_path.read_text())
            return None

        def _validate_manifest(self, manifest: dict) -> bool:
            """ARTHA: Validation - check required fields."""
            return "id" in manifest and "steps" in manifest

VERIFY: python -c "from vibe_core.playbook.loader import PlaybookLoader; print('PlaybookLoader migrated')"
```

### TASK 4: Phase 5 - UnifiedTrace for Observability

```
FILE: vibe_core/runtime/unified_trace.py (NEW)
CREATE:
    \"\"\"UnifiedTrace - GAD-000 Test 2: AI-readable execution traces.\"\"\"
    from dataclasses import dataclass, field
    from typing import Dict, Any, List
    import time
    import uuid

    @dataclass
    class TraceEvent:
        trace_id: str
        timestamp: float
        component: str
        event_type: str
        data: Dict[str, Any]

    class UnifiedTrace:
        \"\"\"Central nervous system for AI observability.\"\"\"

        def __init__(self):
            self._traces: Dict[str, List[TraceEvent]] = {}

        def start(self, component: str, data: Dict[str, Any]) -> str:
            trace_id = str(uuid.uuid4())[:8]
            event = TraceEvent(
                trace_id=trace_id,
                timestamp=time.time(),
                component=component,
                event_type="start",
                data=data
            )
            self._traces[trace_id] = [event]
            return trace_id

        def complete(self, trace_id: str, data: Dict[str, Any]) -> None:
            if trace_id in self._traces:
                self._traces[trace_id].append(TraceEvent(
                    trace_id=trace_id,
                    timestamp=time.time(),
                    component="",
                    event_type="complete",
                    data=data
                ))

        def get_trace(self, trace_id: str) -> List[dict]:
            events = self._traces.get(trace_id, [])
            return [{"timestamp": e.timestamp, "type": e.event_type, "data": e.data} for e in events]

VERIFY: python -c "from vibe_core.runtime.unified_trace import UnifiedTrace; t=UnifiedTrace(); id=t.start('test',{}); t.complete(id,{'ok':True}); print(t.get_trace(id))"
```

### TASK 5: Phase 6 - Burn Notice Script

```
FILE: scripts/verify_no_legacy_imports.py (NEW)
CREATE:
    #!/usr/bin/env python3
    \"\"\"Verify no legacy imports remain before deletion.\"\"\"
    import subprocess
    import sys

    LEGACY_FILES = [
        "vibe_core/cli.py",  # Old StewardCLI
        "vibe_core/playbook/router.py",  # Old PlaybookRouter
        "vibe_core/runtime/playbook_router.py",  # Duplicate
    ]

    def check_imports(file_path: str) -> bool:
        \"\"\"Check if file is imported anywhere.\"\"\"
        module = file_path.replace("/", ".").replace(".py", "")
        result = subprocess.run(
            ["grep", "-r", f"from {module}", "vibe_core/", "tests/"],
            capture_output=True, text=True
        )
        return len(result.stdout.strip()) > 0

    def main():
        for f in LEGACY_FILES:
            if check_imports(f):
                print(f"ERROR: {f} still imported!")
                sys.exit(1)
            else:
                print(f"OK: {f} can be deleted")
        print("All legacy files ready for deletion")

    if __name__ == "__main__":
        main()

VERIFY: python scripts/verify_no_legacy_imports.py
```

### TASK 6: Phase 7 - Manifest Dependencies

```
FILE: vibe_core/loaders/plugin_loader.py
FIND: def _sort_by_priority(self, manifests):
REPLACE_WITH:
    def _sort_by_dependencies(self, manifests: List[dict]) -> List[dict]:
        \"\"\"Topological sort respecting depends_on + priority fallback.\"\"\"
        # Build dependency graph
        graph = {m["id"]: set(m.get("depends_on", [])) for m in manifests}
        result = []
        visited = set()

        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in graph.get(node_id, []):
                visit(dep)
            manifest = next((m for m in manifests if m["id"] == node_id), None)
            if manifest:
                result.append(manifest)

        # Sort by priority first, then resolve dependencies
        for m in sorted(manifests, key=lambda x: x.get("priority", 999)):
            visit(m["id"])

        return result

VERIFY: python -m pytest tests/integration/test_kernel_boot.py -v
```

---

**Status**: HAIKU-READY
