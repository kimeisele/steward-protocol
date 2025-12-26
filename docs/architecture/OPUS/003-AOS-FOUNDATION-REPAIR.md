# 003: AOS Foundation Repair - ENVOY.md Data Flow Analysis

> **Created**: 2025-12-07 by Opus 4.5
> **Status**: COMPLETE
> **Problem**: ENVOY.md commands execute but output never appears
> **Scope**: 7 critical wiring breaks + Knowledge system test fix

<!-- @HARNESS
# OPUS-313: Updated - removed references to deleted legacy renderers
# The EnvoyRenderer was replaced by ManifestationService (OPUS-308)
files:
  - path: vibe_core/cartridges/system/envoy/cartridge_main.py
    required: true
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/plugins/interface/plugin_main.py
    required: true
  - path: vibe_core/services/manifestation_service.py
    required: true
wiring:
  - pattern: "EnvoyCartridge"
    in: vibe_core/cartridges/system/envoy/cartridge_main.py
  - pattern: "ManifestationService"
    in: vibe_core/services/manifestation_service.py
config:
  - section: interface
-->

---

## Executive Summary

The Steward Protocol AOS has solid architecture:
- InterfacePlugin (KING pattern for UI writes)
- UnifiedRouter (single routing authority)
- Phoenix Config (config-driven behavior)
- 16 working renderers

But **7 critical breaks** in the ENVOY.md data flow prevent user commands from producing visible output. The circuit executes successfully, but the rendered output is lost in translation.

---

## Data Flow Diagram: "status" Command

```
USER WRITES "status" IN ENVOY.md
           |
           v
    +---------------------------------+
    | EnvoyRenderer._sync_from_file() |
    | (interface/renderers/envoy.py)  |
    +---------------------------------+
           |
           v
    +---------------------------------+
    | EnvoySync.parse_requests()      |
    | Extracts: ["status"]            |
    +---------------------------------+
           |
           v
    +---------------------------------------+
    | BREAK 1: Dual Routing                 |
    | PATH A: kernel.envoy.route()          |
    | PATH B: kernel._playbook_router       |
    | (Legacy fallback still exists)        |
    +---------------------------------------+
           |
           v
    +---------------------------------+
    | EnvoySync.dispatch_request()    |
    | Creates Task object             |
    | scheduler.submit_task(task)     |
    +---------------------------------+
           |
           v
    +---------------------------------+
    | BREAK 2: Render BEFORE Execute  |
    | InterfacePlugin.on_tick_pre()   |
    | renders ENVOY.md with stale     |
    | data (task not executed yet)    |
    +---------------------------------+
           |
           v
    +---------------------------------+
    | Kernel.tick()                   |
    | scheduler.next_task()           |
    | agent.process(task)             |
    +---------------------------------+
           |
           v
    +-------------------------------------------+
    | EnvoyCartridge.process(task)              |
    | _route_command("status")                  |
    | kernel.envoy.execute_circuit(             |
    |   "SYSTEM_STATUS_V2",                     |
    |   params={"user_input": "status"}         |
    | )                                         |
    +-------------------------------------------+
           |
           v
    +-------------------------------------------+
    | BREAK 4: Result Path Mismatch             |
    |                                           |
    | Circuit returns:                          |
    | {                                         |
    |   "status": "COMPLETED",                  |
    |   "phases_executed": [{                   |
    |     "phase_id": "render_output",          |
    |     "result": {"rendered": "...output..."} |
    |   }]                                      |
    | }                                         |
    |                                           |
    | But code extracts:                        |
    | details.get("rendered", {})               |
    |        .get("rendered", "")               |
    | = EMPTY STRING                            |
    +-------------------------------------------+
           |
           v
    +-------------------------------------------+
    | BREAK 5: No on_task_completed() Hook      |
    |                                           |
    | Kernel calls: plugin.on_task_completed()  |
    | InterfacePlugin: METHOD NOT DEFINED       |
    | Result: No immediate UI update            |
    +-------------------------------------------+
           |
           v
    +-------------------------------------------+
    | BREAK 6: Interval-Based Rendering         |
    |                                           |
    | EnvoyRenderer only renders every 2+ sec   |
    | Not triggered by task completion          |
    +-------------------------------------------+
           |
           v
    +-------------------------------------------+
    | BREAK 7: Result Format Conversion         |
    |                                           |
    | EnvoySync extracts:                       |
    | result.get("message")                     |
    | or result.get("summary")                  |
    | or result.get("response")                 |
    | or "Done"                                 |
    |                                           |
    | None match, returns "Done"                |
    | Actual output LOST                        |
    +-------------------------------------------+
           |
           v
    +---------------------------------+
    | ENVOY.md shows:                 |
    | - Request cleared: OK           |
    | - Status: COMPLETED             |
    | - Response: "Done" (WRONG!)     |
    | - Actual output: MISSING        |
    +---------------------------------+

---

## Status

| Aspect | Status | Evidence |
|--------|--------|----------|
| P3 Foundation | ✅ | `setup/setup_project.py` |
| Dependencies | ✅ | `pyproject.toml` |

## Implementation

The `setup` directory contains all foundation repair scripts. `pyproject.toml` has been standardized to use `project.scripts` for CLI entry points.

---

## The 7 Breaks

### BREAK 1: Dual Routing System

**Location**: `vibe_core/plugins/interface/renderers/envoy.py:125-129`

**Problem**: Two routing paths exist - UnifiedRouter and legacy PlaybookRouter fallback.

```python
# Current (envoy.py:125-129)
if hasattr(self.kernel, "envoy"):
    router_callback = self._envoy_route_adapter
else:
    router_callback = self.kernel._playbook_router.route  # LEGACY
```

**Severity**: MEDIUM - UnifiedRouter is always available, but legacy code remains.

**Fix**: Remove legacy fallback.

---

### BREAK 2: Render Before Execute

**Location**: `vibe_core/kernel_impl.py:776`

**Problem**: `on_tick_pre()` renders ENVOY.md BEFORE task executes in same tick.

```
Tick Order:
1. on_tick_pre() → InterfacePlugin._render_scheduled() → writes ENVOY.md
2. scheduler.next_task() → Execute task
```

**Severity**: HIGH - User sees stale status.

**Fix**: Addressed by BREAK 5 fix (event-driven rendering).

---

### BREAK 3: Agent Registration Dependency

**Location**: `vibe_core/plugins/envoy/plugin_main.py:612-637`

**Problem**: If EnvoyCartridge fails to register, tasks queue but can't execute.

**Severity**: MEDIUM - Currently working, but fragile.

**Fix**: None needed (works correctly now).

---

### BREAK 4: Result Path Mismatch (CRITICAL)

**Location**: `vibe_core/cartridges/system/envoy/cartridge_main.py:329-346`

**Problem**: Circuit returns different structure than code expects.

**Circuit returns**:
```python
{
    "status": "COMPLETED",
    "phases_executed": [
        {
            "phase_id": "render_output",
            "result": {
                "rendered": "# System Status\n..."
            }
        }
    ]
}
```

**Code extracts** (WRONG):
```python
details = circuit_result.get("details", {})
rendered = details.get("rendered", {}).get("rendered", "")
```

**Severity**: CRITICAL - Main cause of missing output.

**Fix**: Extract from `phases_executed[].result.rendered`:
```python
rendered = ""
phases = circuit_result.get("phases_executed", [])
for phase in phases:
    if phase.get("phase_id") == "render_output":
        rendered = phase.get("result", {}).get("rendered", "")
        break
```

---

### BREAK 5: Missing Task Completion Hook (CRITICAL)

**Location**: `vibe_core/plugins/interface/plugin_main.py` (missing method)

**Problem**: InterfacePlugin doesn't implement `on_task_completed()`, so ENVOY.md isn't updated when tasks finish.

```python
# kernel_impl.py:837-838
for plugin in self._plugins:
    plugin.on_task_completed(self, task.task_id, result)
```

But `InterfacePlugin` has no such method.

**Severity**: CRITICAL - Response never appears without manual render cycle.

**Fix**: Add completion hook:
```python
def on_task_completed(self, kernel, task_id: str, result: dict) -> None:
    """Trigger immediate ENVOY.md update when task completes."""
    if "envoy" in self._renderers:
        self._last_render["envoy"] = 0  # Force immediate render
```

---

### BREAK 6: Interval-Based Rendering

**Location**: `vibe_core/plugins/interface/plugin_main.py:127-160`

**Problem**: Rendering waits for interval (default 2+ seconds) even when result is ready.

```python
def _render_scheduled(self) -> None:
    now = time.time()
    for name, renderer in self._renderers.items():
        if self._should_render(name):  # TIME-BASED CHECK
            # Render only if interval elapsed
```

**Severity**: HIGH - Delays response visibility.

**Fix**: Addressed by BREAK 5 fix (reset timer on task completion).

---

### BREAK 7: Result Format Conversion

**Location**: `vibe_core/envoy_sync.py:253-267` + `renderers/envoy.py:98-109`

**Problem**: EnvoySync extracts wrong fields from result dict.

```python
# Current (WRONG)
result.get("message") or result.get("summary") or result.get("response") or "Done"
```

None of these keys exist in circuit result → returns "Done" → actual output lost.

**Severity**: HIGH - Output visible but wrong content.

**Fix**: Add proper extraction chain:
```python
def _extract_response(result: dict) -> str:
    # Try circuit result structure first
    if "phases_executed" in result:
        for phase in result["phases_executed"]:
            if phase.get("phase_id") == "render_output":
                return phase.get("result", {}).get("rendered", "")
    # Then try standard fields
    return (result.get("response") or result.get("message") or
            result.get("output") or result.get("summary") or "Done")
```

---

## Knowledge System Test Fix

**Problem**: Test fixtures point to wrong directory.

**Location**: `tests/unit/test_knowledge_graph.py:36-38`, `tests/unit/test_knowledge_resolver.py:19-21`

**Current** (WRONG):
```python
knowledge_dir = Path(__file__).parent.parent / "knowledge"
# Resolves to: tests/knowledge/ (doesn't exist)
```

**Fix**:
```python
knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
# Resolves to: knowledge/ (correct)
```

**Impact**:
- Enables 39 knowledge tests to pass
- Activates semantic routing (concept→agent mapping)
- Enables authority-based permission checking
- Protects .git and sensitive paths

---

## Plugin/Cartridge Architecture Clarification

### INTENDED DESIGN (Correct):

```
EnvoyPlugin (kernel.envoy)
  ├─ Owns: UnifiedRouter, circuit/playbook registry
  ├─ Exposes: route(), execute_circuit(), get_routes()
  ├─ Lifecycle: on_boot, on_tick, on_shutdown
  └─ Registers: EnvoyCartridge as kernel agent

EnvoyCartridge (agent_id="envoy")
  ├─ Receives: Tasks from scheduler
  ├─ Executes: Via DeterministicExecutor
  ├─ Returns: Result to ledger
  └─ Uses: Plugin's router via self.router property
```

### CURRENT CONFUSION:

1. **Plugin has execute_circuit()** - bypasses task/scheduler flow
2. **Two DeterministicExecutor instances** - one in plugin, one in cartridge
3. **Router access unclear** - cartridge gets it via plugin

### RECOMMENDATION:

Keep current design (80% correct). The execute_circuit() in plugin is useful for direct API calls. Just fix the wiring breaks.

---

## Implementation Order

```
1. Fix 4 (result path)      → Circuit output extracted correctly
2. Fix 7 (format conversion) → Output reaches ENVOY.md
3. Fix 5 (completion hook)   → Immediate UI update
4. Knowledge test fix        → Semantic routing works
5. Fix 1 (legacy cleanup)    → Cleaner code
```

Fixes 2 and 6 are addressed by Fix 5.

---

## Files to Modify

| File | Changes |
|------|---------|
| `vibe_core/cartridges/system/envoy/cartridge_main.py` | Fix 4: result extraction |
| `vibe_core/plugins/interface/plugin_main.py` | Fix 5: add `on_task_completed()` |
| `vibe_core/envoy_sync.py` | Fix 7: result format extraction |
| `vibe_core/plugins/interface/renderers/envoy.py` | Fix 7: result format + Fix 1: remove legacy |
| `tests/unit/test_knowledge_graph.py` | Knowledge path fix |
| `tests/unit/test_knowledge_resolver.py` | Knowledge path fix |

---

## Verification Checkpoints

### After Fix 4+7:
```bash
python3 -c "
from vibe_core.kernel_impl import RealVibeKernel
k = RealVibeKernel(ledger_path=':memory:')
k.boot()
result = k.envoy.execute_circuit('SYSTEM_STATUS_V2', params={'user_input': 'status'})
print(result)
# Should contain actual status output, not empty string
"
```

### After Fix 5:
```bash
python -m pytest tests/integration/test_kernel_markdown_interfaces.py -v
```

### After Knowledge Fix:
```bash
python -m pytest tests/unit/test_knowledge_graph.py tests/unit/test_knowledge_resolver.py -v
# Should be 39 PASSED, 0 FAILED
```

---

## Success Criteria

1. `status` command in ENVOY.md produces actual status output
2. Response appears in Response History section within 1 tick
3. Knowledge tests pass (39/39)
4. No regression in existing passing tests

---

## HAIKU EXECUTION BLOCKS

> **For AI Agent Execution**: Copy-paste these blocks to implement fixes.

### TASK 1: Fix Result Path (cartridge_main.py)

```
FILE: vibe_core/cartridges/system/envoy/cartridge_main.py
FIND: details = circuit_result.get("details", {})
      rendered = details.get("rendered", {}).get("rendered", "")
REPLACE_WITH:
      # Extract rendered output from phases_executed
      rendered = ""
      phases = circuit_result.get("phases_executed", [])
      for phase in phases:
          if phase.get("phase_id") == "render_output":
              rendered = phase.get("result", {}).get("rendered", "")
              break
VERIFY: python3 -c "from vibe_core.kernel_impl import RealVibeKernel; k=RealVibeKernel(ledger_path=':memory:'); k.boot(); print(k.envoy.execute_circuit('SYSTEM_STATUS_V2', params={'user_input':'status'}))"
```

### TASK 2: Add Task Completion Hook (plugin_main.py)

```
FILE: vibe_core/plugins/interface/plugin_main.py
AFTER: def on_tick_post(self, kernel) -> None:
ADD_METHOD:
    def on_task_completed(self, kernel, task_id: str, result: dict) -> None:
        """FIX 5: Trigger immediate ENVOY.md update when task completes."""
        if "envoy" in self._renderers:
            self._last_render["envoy"] = 0  # Force next render
VERIFY: python -m pytest tests/integration/test_kernel_markdown_interfaces.py -v -k "envoy"
```

### TASK 3: Fix Result Format Extraction (envoy_sync.py)

```
FILE: vibe_core/envoy_sync.py
FIND: result.get("message") or result.get("summary") or result.get("response") or "Done"
REPLACE_WITH:
      # Extract from circuit phases first
      if "phases_executed" in result:
          for phase in result["phases_executed"]:
              if phase.get("phase_id") == "render_output":
                  return phase.get("result", {}).get("rendered", "")
      return result.get("response") or result.get("message") or result.get("output") or "Done"
VERIFY: Write "status" to ENVOY.md, run kernel ticks, check Response History has actual output
```

---

**Signed**: Opus 4.5
**Date**: 2025-12-07
**Status**: HAIKU-READY
