# OPUS-112: Synaptic Bridge Architecture

**Status**: IMPLEMENTED - Phase 1 Complete
**Author**: Claude/Gemini Synthesis
**Date**: 2025-12-19
**Depends On**: OPUS-089, OPUS-101, OPUS-106

---

## 1. The Question

How do MANAS (Mind) and ENVOY (Hand) connect without touching the Kernel (Spine)?

**Constraints:**
- Kernel is VISNU-protected - NO modifications
- No point-to-point fragile wiring
- New agents (ENGINEER, CHRONICLE, FUTURE_X) must integrate automatically
- Clear separation of concerns

---

## 2. Current State Analysis

### 2.1 ENVOY - The Semantic Shell

```
vibe_core/cartridges/system/envoy/
├── cartridge_main.py     → EnvoyCartridge (ContextAwareAgent)
├── provider.py           → UnifiedProvider + SemanticRouter
├── action_handlers.py    → ActionHandlerRegistry (internal)
├── deterministic_executor.py → DeterministicExecutor
└── tools/                → envoy.* tools (auto-discovered)
```

**Role:**
- USER ENTRY POINT - receives commands from CLI/UI
- Semantic understanding via SemanticRouter (PROJECT JNANA)
- Routes to flash/science/lazy execution paths
- Executes via `self.system.execute_tool()` (kernel-managed)
- Owns: CityControlTool, CuratorTool, DiplomacyTool, etc.

**Key Method:**
```python
# cartridge_main.py:362
result = self.system.execute_tool("envoy.city_control", {"action": "get_city_status"})
```

### 2.2 MANAS - The Cognitive Oracle

```
vibe_core/plugins/opus_assistant/manas/
├── api.py                → ManasOracle (clean entry point)
├── cognitive_kernel.py   → CognitiveKernel (the brain)
├── intent_generator.py   → IntentGenerator
├── intent_router.py      → IntentRouter + ActionLoader
├── cortex/               → Domain handlers (sutra, shell, dharma...)
└── analyzers/            → Context analyzers
```

**Role:**
- COGNITIVE ORACLE - other components CONSULT MANAS
- Generates Intents based on context analysis
- Routes intents to cortex handlers
- Maintains memory/karma for learning
- API: `ManasOracle.consult(context) → AnalysisResult`

**Key Interface:**
```python
# api.py - Clean separation
from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

oracle = ManasOracle()
result = oracle.consult({"task": "deploy", "risk": "high"})
```

### 2.3 Kernel Infrastructure (EXISTS - DO NOT TOUCH)

```
kernel.tool_registry        → ToolRegistry (all agent tools)
kernel._capability_registry → CapabilityRegistry (permissions)
ToolsPlugin                 → Auto-discovers cartridge tools
```

**What's already wired:**
```
ToolsPlugin.on_boot()
    → ToolDiscovery.discover_all_tools()
    → Scans: cartridges/system/*/tools/*.py
    → Registers in kernel.tool_registry
    → envoy.*, chronicle.*, engineer.* ALL HERE
```

---

## 3. The Gap

### Current Flow (Broken)

```
USER INPUT
    ↓
ENVOY (receives, routes)
    ↓
DeterministicExecutor OR delegate to agent
    ↓
??? How does MANAS Intent reach ENVOY's execution ???

MANAS (generates Intent)
    ↓
IntentRouter._try_action_loader()
    ↓
ActionLoader (scans cortex/*_action.py ONLY)
    ↓
CANNOT reach kernel.tool_registry!
```

### The Missing Link

MANAS's `IntentRouter` uses `ActionLoader` which only scans its own cortex:
```python
# cognitive_kernel.py:257
self._tool_loader = ToolLoader(scope="opus_private", ...)
#                                     ^^^^^^^^^^^^^^
#                                     PRIVATE SCOPE = BLIND TO ENVOY
```

---

## 4. Architecture Options

### Option A: MANAS Dispatches Directly

```
MANAS Intent → kernel.tool_registry.execute() → Tool
```

**Pros:**
- Direct path
- MANAS already has `inject_kernel()`

**Cons:**
- MANAS becomes a dispatcher (not its role)
- Violates: "Mind thinks, Hand acts"

### Option B: ENVOY Dispatches for MANAS

```
MANAS Intent → ENVOY → kernel.tool_registry.execute() → Tool
```

**Pros:**
- Separation of concerns (MANAS thinks, ENVOY acts)
- ENVOY already has execution wiring
- Single dispatch path for all execution

**Cons:**
- Extra hop
- Need to define Intent → ENVOY protocol

### Option C: Unified Capability Broker (New Layer)

```
                ┌────────────────────────────────────┐
                │    CAPABILITY BROKER (new)         │
                │    - Aggregates all agent tools    │
                │    - Single query interface        │
                └────────────────────────────────────┘
                      ↑                ↓
                   MANAS            ENVOY
                (queries)        (dispatches)
```

**Pros:**
- Clean abstraction
- Future-proof

**Cons:**
- New component to maintain
- May duplicate kernel.tool_registry

### Option D: Use kernel.tool_registry AS the Broker

```
kernel.tool_registry (ALREADY EXISTS)
        ↑
    ToolsPlugin auto-discovers ALL cartridge tools
        ↑
    ENVOY tools ARE ALREADY REGISTERED
    CHRONICLE tools ARE ALREADY REGISTERED
    ENGINEER tools ARE ALREADY REGISTERED
        ↓
    MANAS just needs access!
```

**This is the answer.**

The infrastructure EXISTS. The wiring is MISSING.

---

## 5. Proposed Solution: Minimal Wiring

### 5.1 MANAS → kernel.tool_registry Access

**File:** `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`

```python
def inject_kernel(self, kernel: "RealVibeKernel") -> None:
    self._vibe_kernel = kernel
    # ADD: Store reference to kernel's tool registry
    self._global_tool_registry = kernel.tool_registry
    logger.info("⚡ VAJRA: Kernel injected - tool_registry bound")
```

### 5.2 IntentRouter Uses Global Registry

**File:** `vibe_core/plugins/opus_assistant/manas/intent_router.py`

```python
def _try_tool_dispatch(self, intent: Intent) -> Optional[RouteResult]:
    """
    OPUS-112: Try to dispatch via kernel.tool_registry.

    If intent.action_id matches a registered tool, execute it.
    """
    if self._kernel is None or not hasattr(self._kernel, 'tool_registry'):
        return None

    tool = self._kernel.tool_registry.get(intent.action_id)
    if tool is None:
        return None

    # Execute via registry
    call = ToolCall(
        tool_name=intent.action_id,
        parameters=intent.params,
        caller_agent_id="manas"
    )
    result = self._kernel.tool_registry.execute(call)

    return RouteResult(
        success=result.success,
        handler=f"tool_registry/{intent.action_id}",
        result=result.output
    )
```

### 5.3 Update route() to Try Tool Dispatch

```python
def route(self, intent: Intent) -> RouteResult:
    # 1. Gate check (unchanged)
    gate_result = self.gate(intent)
    ...

    # 2. OPUS-112: Try kernel.tool_registry first
    tool_result = self._try_tool_dispatch(intent)
    if tool_result is not None:
        return tool_result

    # 3. Try ActionLoader (existing)
    action_result = self._try_action_loader(intent)
    if action_result is not None:
        return action_result

    # 4. Legacy handlers (existing)
    ...
```

---

## 6. What About ENVOY as Entry Point?

ENVOY remains the USER-FACING entry point:

```
USER → ENVOY.process() → UnifiedRouter → Execution

But for INTERNAL cognitive operations:

MANAS Intent → kernel.tool_registry → Tool
```

**Key Insight:**
- ENVOY handles USER commands (imperative)
- MANAS handles SYSTEM cognition (declarative intents)
- Both use kernel.tool_registry as the execution substrate

---

## 7. Flow After Implementation

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ENVOY (Semantic Shell)                                         │
│  - Receives user commands                                       │
│  - Routes via UnifiedRouter                                     │
│  - Executes via self.system.execute_tool()                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  kernel.tool_registry (SINGLE SOURCE OF TRUTH)                  │
│  - envoy.city_control, envoy.curator, ...                       │
│  - chronicle.git_tools, chronicle.seal_history, ...             │
│  - engineer.scaffold, engineer.refactor, ...                    │
│  - (auto-discovered by ToolsPlugin)                             │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│  MANAS (Cognitive Oracle)                                       │
│  - Generates Intents from context                               │
│  - Routes via IntentRouter                                      │
│  - OPUS-112: Can now dispatch to kernel.tool_registry           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Benefits

1. **No Kernel Changes** - Only MANAS plugin modified
2. **No Point-to-Point Wiring** - Uses existing registry
3. **Auto-Discovery** - New agent tools automatically available
4. **Separation of Concerns** - ENVOY=Shell, MANAS=Mind, Kernel=Substrate
5. **Loose Coupling** - MANAS doesn't know ENVOY, ENVOY doesn't know MANAS

---

## 9. Open Questions

### Q1: Should MANAS dispatch or delegate to ENVOY?

**Current Answer:** MANAS dispatches directly to kernel.tool_registry.
ENVOY is for USER commands, MANAS is for SYSTEM cognition.

**Alternative:** MANAS creates Task for ENVOY, ENVOY dispatches.
This adds latency but maintains single execution path.

### Q2: Capability Checking

When MANAS dispatches via tool_registry, should it use `caller_agent_id="manas"`?
This affects capability enforcement.

### Q3: MANAS API vs Direct Dispatch

Should other components use `ManasOracle.consult()` or dispatch directly?
- Consult = Ask for advice (returns AnalysisResult)
- Dispatch = Execute action (uses tool_registry)

---

## 10. Implementation Checklist

- [x] Update `cognitive_kernel.py`: Store `kernel.tool_registry` reference
- [x] Add `_try_tool_dispatch()` to `intent_router.py`
- [x] Update `route()` to try tool dispatch before action loader
- [x] Add DHARMA policy: Only SAFE/LOW risk intents use direct dispatch
- [x] Add SYSTEM ACT logging to `system_journal.jsonl`
- [ ] Test: MANAS can dispatch to envoy.city_control (needs kernel boot)
- [ ] Test: MANAS can dispatch to chronicle.git_tools (needs kernel boot)
- [ ] Test: New agent tools automatically available (needs kernel boot)

---

## 11. Non-Goals

- Modifying kernel_impl.py (VISNU protected)
- Creating new capability broker (use existing tool_registry)
- Replacing ENVOY as user entry point
- Replacing ManasOracle API

---

*"The mind commands the hand, and the hand moves. But both obey the same laws."*

---

## @HARNESS

**Files**:
- `/home/user/steward-protocol/vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`
  - `inject_kernel()` - stores kernel.tool_registry reference
  - `_vibe_kernel` - kernel instance reference
  - `_global_tool_registry` - reference to kernel's tool registry
- `/home/user/steward-protocol/vibe_core/plugins/opus_assistant/manas/intent_router.py`
  - `_try_tool_dispatch()` - dispatches intents via kernel.tool_registry
  - `route()` - routing logic that tries tool dispatch first
  - `IntentRouter` class - main routing orchestrator

**Wiring Pattern**:
```python
# Kernel injection (boot time)
kernel.inject_kernel(vibe_kernel)  # Stores tool_registry reference

# Intent execution (runtime)
intent = Intent(action_id="envoy.city_control", params={...})
route_result = router.route(intent)
# → _try_tool_dispatch() checks kernel.tool_registry
# → Executes via kernel.tool_registry.execute(ToolCall(...))
# → Returns RouteResult with success/failure
```

**Integration Points**:
- MANAS generates intents → IntentRouter routes → kernel.tool_registry executes
- No direct MANAS ↔ ENVOY coupling
- kernel.tool_registry is the synaptic bridge
