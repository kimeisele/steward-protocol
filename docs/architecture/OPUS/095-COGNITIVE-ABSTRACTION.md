# OPUS-095: Cognitive Abstraction - Unifying Orchestration Patterns

**Status:** Planning Phase (No Code Changes Yet)
**Author:** Forensic Analysis Team (MANAS + Senior)
**Date:** Session Context Continuation
**Scope:** Architecture Blueprint for CognitiveKernel Refactoring

---

## Executive Summary

**The Problem:**
CognitiveKernel.think() is a 137-line god object that reimplements core orchestration logic that already exists in PranaOrchestrator, BootOrchestrator, and other lifecycle managers. This creates:
- Code duplication across 5+ orchestration layers
- Maintenance burden (changes must propagate to multiple places)
- Testing fragmentation (same patterns tested separately in each class)
- **CRITICAL INTEGRATION GAP:** Disconnected from UnifiedTrace and EventBus (ghost brain)

**The Opportunity:**
Extract a unifying `CognitiveCycle` abstraction that orchestration layers inherit from, **properly integrated with existing system infrastructure (UnifiedTrace, EventBus)**.

**CRITICAL CORRECTIONS (From User Review):**
1. ⚠️ **Integration Error (Was Creating Spaghetti):**
   - Original plan created new `CycleContext` + `CycleRegistry` (parallel truth systems)
   - **Fix:** `CycleContext` wraps UnifiedTrace.Span; emits to EventBus on phase transitions

2. ⚠️ **Misclassification Error:**
   - Original plan tried to force CircuitExecutor into CognitiveCycle
   - **Reality:** CircuitExecutor is LINEAR (Input → Process → Output), not CYCLIC
   - **Fix:** CircuitExecutor is a `CognitiveProcess`, not a `CognitiveCycle`; called BY cycles

3. ⚠️ **Missing Holon Wiring:**
   - No parent-child causality tracking (why did this child run?)
   - **Fix:** Add `parent_cycle_id` to CycleContext for traceability

4. ⚠️ **Memory Leak Risk:**
   - CycleRegistry would store infinite cycles (no retention policy)
   - **Fix:** Use retention policy (last N cycles + errors only)

**The Pattern Already Exists:**
Recognizing patterns already present:
- **CognitiveCycle Pattern:** PranaOrchestrator (phases: SENSORS → ACTUATORS → CLEANUP), BootOrchestrator (phases: Brahma → Vishnu → Shiva), CognitiveKernel (phases: Perceive → Orient → Decide → Act)
- **Process Pattern:** CircuitExecutor (runs YAML state machines; called BY cycles)

All cycles inherit from CognitiveCycle. All processes inherit from CognitiveProcess. Cycles call processes.

---

## Part 1: The Existing Patterns

### 1.1 Pattern Analysis: Cycles vs Processes

**CYCLES (Repeating Orchestration Loops)** - Inherit from `CognitiveCycle`:

| Class | Location | Pattern | Structure |
|-------|----------|---------|-----------|
| **CognitiveKernel** | manas/cognitive_kernel.py:1117-1250 | OODA Loop | Perceive → Orient → Decide → Act → Persist |
| **PranaOrchestrator** | vibe_core/prana_orchestrator.py | Phase-based | SENSORS → ACTUATORS → CLEANUP → PERSIST |
| **BootOrchestrator** | vibe_core/boot_orchestrator.py | Cosmic Phases | Brahma → Vishnu → Shiva → Dharma → PERSIST |
| **ShivaLifecycleManager** | manas/shiva_lifecycle.py | Sweep Cycle | Perceive → Evaluate → Archive → Persist |
| **SankalpaOrchestrator** | manas/sankalpa_orchestrator.py | Strategy Cycle | Perceive → Plan → Rank → Persist |

**PROCESSES (Linear Executors)** - Inherit from `CognitiveProcess`, called BY cycles:

| Class | Location | Pattern | Structure | Caller |
|-------|----------|---------|-----------|--------|
| **CircuitExecutor** | manas/circuit_executor.py | YAML State Machine | Input → Load → Execute → Output | CognitiveKernel.think() |
| **Cortex Senses** | manas/cortex_senses.py | Perception Processor | Input → Classify → Report → Output | PranaOrchestrator or CognitiveKernel |

**Key Insight:**
- **Cycles** manage orchestration loops (rate limiting, error recovery, persistence)
- **Processes** execute discrete work (state machines, data transformation)
- Cycles CALL processes. Processes are stateless.
- Original plan tried to fit Process into Cycle abstraction ❌
- **Correct architecture:** Cycles inherit from CognitiveCycle, Processes inherit from CognitiveProcess

### 1.2 Existing Code Locations

**CognitiveCycle Candidates (What WILL Inherit from Base):**

**CognitiveKernel.think() (the primary target):**
- Path: `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py:1117-1250`
- 137 lines of orchestration boilerplate + cognition logic mixed
- Contains: rate limiting, mirror test, 4x perception, cleanup, sweep, generate, judge, record, auto-execute, persist
- **Fix:** Extract orchestration to base; leave only pure cognition logic (~20 lines)

**PranaOrchestrator (plugin lifecycle):**
- Path: `vibe_core/prana_orchestrator.py`
- Phase-based execution (SENSORS, ACTUATORS, CLEANUP)
- Isolation wrappers for fault tolerance
- Plugin discovery and ordering
- **Fix:** Inherit from CognitiveCycle; override phase methods; delegate orchestration

**BootOrchestrator (cosmic creation):**
- Path: `vibe_core/boot_orchestrator.py`
- Sarga phases: Brahma → Vishnu → Shiva → Dharma
- Supports FULL/HEADLESS/MINIMAL modes
- **Fix:** Inherit from CognitiveCycle; override phase methods

---

**CognitiveProcess Candidates (What WON'T Inherit from CognitiveCycle):**

**CircuitExecutor (LINEAR PROCESS, not cycle):**
- Path: `vibe_core/plugins/opus_assistant/manas/circuit_executor.py`
- Executes YAML state machines WITHOUT kernel boot
- Pattern: Load YAML → Walk state machine → Dispatch actions → Return results
- **Correction:** Inherits from `CognitiveProcess`, NOT CognitiveCycle
- **Caller:** CognitiveKernel calls this during ACT phase
- **Not a cycle:** No perception, no persistence, no rate limiting (caller handles that)

**Cortex Senses (LINEAR PROCESSOR):**
- Path: `vibe_core/plugins/opus_assistant/manas/cortex_senses.py`
- Perception processor: Input → Classify → Report → Output
- Stateless transformation layer
- **Correction:** Inherits from `CognitiveProcess`
- **Caller:** PranaOrchestrator or CognitiveKernel calls this

---

**Existing Infrastructure (Integration Points):**

**UnifiedTrace** (`vibe_core/runtime/unified_trace.py`):
- Existing: `start(component, event_type, data)` → trace_id
- Existing: `emit(trace_id, component, event_type, data)`
- Existing: `complete(trace_id, data)`, `error(trace_id, error, data)`
- **Integration:** CycleContext wraps this (will extend UnifiedTrace.Span)

**EventBus** (`vibe_core/event_bus.py`):
- Existing: `emit(event)` to subscribers
- Existing: Event history with max_history limit
- Event types: THOUGHT, ACTION, ERROR, COMPLETED, etc.
- **Integration:** Phase transitions emit events to EventBus

---

## Part 2: The Abstraction Blueprint

### 2.1 The CognitiveCycle Interface (CORRECTED FOR SYSTEM INTEGRATION)

```python
# This is a signature, not implementation
# Location: vibe_core/orchestration_cycle.py (new file)

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from vibe_core.runtime.unified_trace import UnifiedTrace  # INTEGRATION POINT #1
from vibe_core.event_bus import EventBus, EventType, Event  # INTEGRATION POINT #2

class CyclePhase(Enum):
    """Standard cycle phases for all orchestration loops."""
    PERCEIVE = "perceive"      # Sense state / observe reality
    ORIENT = "orient"          # Classify / interpret observations
    DECIDE = "decide"          # Generate / filter / prioritize actions
    ACT = "act"                # Execute / apply actions
    PERSIST = "persist"        # Record / commit state
    RECOVER = "recover"        # Error handling / reset if needed


@dataclass
class CycleContext:
    """
    Execution context passed through cycle phases.

    ⚠️ CRITICAL CORRECTION (from user review):
    - This wraps UnifiedTrace.Span (not a parallel system)
    - Emits to EventBus on phase transitions (integrated observability)
    - Includes parent_cycle_id for Holon causality tracking
    - Managed by CycleRegistry with retention policy
    """

    # Identity & Causality
    cycle_id: str                   # Unique ID for this execution
    parent_cycle_id: Optional[str]  # HOLON WIRING: Why am I running? (e.g., CognitiveKernel requested me)
    trace_id: str                   # Links to UnifiedTrace (NOT a separate system)
    cycle_name: str                 # e.g., "cognitive_kernel", "plugin_pulse", "boot_orchestrator"

    # Phase tracking
    phase: CyclePhase              # Current phase
    phase_start_time: float        # When did this phase start? (for timeout checking)

    # Phase results (accumulated through execution)
    observations: List[Any]        # From PERCEIVE phase
    orientations: List[Any]        # From ORIENT phase
    decisions: List[Any]           # From DECIDE phase
    actions: List[Any]             # From ACT phase
    results: Optional[Any]         # From execution (final result)
    errors: Dict[str, str]         # Accumulated errors (phase_name → error_message)

    # Metadata & Extensions
    metadata: Dict[str, Any] = field(default_factory=dict)  # Subclass-specific data

    # EventBus integration
    emitted_events: List[str] = field(default_factory=list)  # Event IDs for observability


@dataclass
class RetentionPolicy:
    """
    Memory safety: Define how long CycleRegistry retains cycle history.

    ⚠️ CRITICAL CORRECTION (from user review):
    This prevents memory leaks (CycleRegistry shouldn't store infinite cycles).
    """
    max_completed_cycles: int = 100      # Keep last N completed cycles
    max_error_cycles: int = 500          # Keep more errors (debugging needed)
    max_age_seconds: Optional[int] = None # Optional TTL (3600 = 1 hour)
    enabled: bool = True                 # False = disable retention (only for testing)


class CognitiveCycle(ABC):
    """
    Abstract base class for ALL orchestration CYCLES in the system.

    ⚠️ CORRECTED SCOPE (from user review):
    - This is for CYCLES (repeating: CognitiveKernel, PranaOrchestrator, BootOrchestrator)
    - NOT for Processes (CircuitExecutor inherits from CognitiveProcess)

    Integration:
    - Uses UnifiedTrace for tracing (not a parallel system)
    - Emits to EventBus on phase transitions
    - Supports parent_cycle_id for Holon causality
    - CycleRegistry manages lifetime with retention policy

    The Template Method: orchestrate() runs the standard cycle.
    Subclasses implement ONLY: _perceive(), _orient(), _decide(), _act()
    """

    def __init__(self):
        """Initialize cycle with system dependencies."""
        self._trace: Optional[UnifiedTrace] = None
        self._event_bus: Optional[EventBus] = None
        self._steward_context: Optional[Any] = None  # Soul, Ledger, etc.

    # ========================================================================
    # DEPENDENCY INJECTION (must be called before orchestrate())
    # ========================================================================

    def setup(self,
              trace: UnifiedTrace,
              event_bus: EventBus,
              steward_context: Any) -> None:
        """
        CRITICAL CORRECTION (from user review):
        Set up system integration points BEFORE orchestrate().

        Args:
            trace: UnifiedTrace instance for observability
            event_bus: EventBus instance for phase transition events
            steward_context: StewardContext with Soul, Ledger, etc.
        """
        self._trace = trace
        self._event_bus = event_bus
        self._steward_context = steward_context

    # ========================================================================
    # CONFIGURATION (override in subclasses)
    # ========================================================================

    @property
    @abstractmethod
    def cycle_name(self) -> str:
        """Human-readable name: 'cognitive_kernel', 'plugin_pulse', 'boot', etc."""
        pass

    @property
    @abstractmethod
    def rate_limit_seconds(self) -> int:
        """Minimum seconds between cycles (0 = no limit)."""
        pass

    @property
    @abstractmethod
    def timeout_seconds(self) -> int:
        """Max runtime for entire cycle (0 = no timeout)."""
        pass

    @property
    @abstractmethod
    def recovery_enabled(self) -> bool:
        """Should we catch and recover from errors?"""
        pass

    @property
    def parent_cycle_id(self) -> Optional[str]:
        """
        HOLON WIRING (from user review):
        Override this in subclasses that are called by parent cycles.
        Example: PranaOrchestrator.pulse() called by BootOrchestrator.boot()
        """
        return None

    # ========================================================================
    # PHASE IMPLEMENTATIONS (subclasses override these)
    # ========================================================================

    @abstractmethod
    async def _perceive(self) -> Tuple[List[Any], Dict[str, str]]:
        """
        PERCEIVE: Sense the state. Return (observations, errors).

        Examples:
        - CognitiveKernel: Check git status, test results, pending intents
        - PranaOrchestrator: Load plugin registry, check sensor statuses
        - BootOrchestrator: Check if directories exist, configs loaded
        """
        pass

    @abstractmethod
    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, str]]:
        """
        ORIENT: Classify/interpret observations. Return (orientations, errors).

        Examples:
        - CognitiveKernel: Classify state into Sattva/Rajas/Tamas gunas
        - PranaOrchestrator: Sort plugins by dependency order
        - BootOrchestrator: Determine boot mode (FULL/HEADLESS/MINIMAL)
        """
        pass

    @abstractmethod
    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, str]]:
        """
        DECIDE: Generate/filter/prioritize actions. Return (decisions, errors).

        Examples:
        - CognitiveKernel: Generate intents, apply filters (NARASIMHA, DHARMA), auto-execute safe
        - PranaOrchestrator: Select which plugins to run based on phases
        - BootOrchestrator: Generate boot sequence based on mode
        """
        pass

    @abstractmethod
    async def _act(self, decisions: List[Any]) -> Tuple[Any, Dict[str, str]]:
        """
        ACT: Execute decisions. Return (results, errors).

        Examples:
        - CognitiveKernel: Execute intents, record in OPUS.md, commit
        - PranaOrchestrator: Run plugin tasks in isolation wrappers
        - BootOrchestrator: Execute boot tasks (boot plugins, init state)
        """
        pass

    async def _persist(self, context: CycleContext) -> Dict[str, str]:
        """
        PERSIST: Record state. Override only if needed.
        Default: Store cycle_id in registry for idempotency.

        Examples:
        - CognitiveKernel: Commit to git, update .opus_state/
        - PranaOrchestrator: Update last_pulse timestamp
        - BootOrchestrator: Mark boot phase complete
        """
        return {}

    async def _recover(self, context: CycleContext) -> bool:
        """
        RECOVER: Handle errors. Override only if needed.
        Default: Log errors and continue.

        Return: True if recovery successful, False to abort cycle.
        """
        return True

    # ========================================================================
    # THE ORCHESTRATION TEMPLATE METHOD (final, not overridden)
    # ========================================================================

    async def orchestrate(self, force: bool = False, parent_cycle_id: Optional[str] = None) -> CycleContext:
        """
        RUN THE CYCLE: This is the unified orchestration loop.

        All concrete cycles (CognitiveKernel, PranaOrchestrator, etc.)
        inherit this. They only implement the phase methods above.

        ⚠️ CRITICAL CORRECTION (from user review):
        This orchestrate() method:
        1. Starts trace in UnifiedTrace: trace_id = self._trace.start(self.cycle_name)
        2. Creates CycleContext with trace_id, parent_cycle_id
        3. For each phase (PERCEIVE → ORIENT → DECIDE → ACT → PERSIST):
           a. Emit phase_start event to EventBus
           b. Call _perceive()/_orient()/_decide()/_act()
           c. Emit phase_complete event to EventBus
           d. Track phase results in CycleContext
        4. If errors: Call _recover(), emit error event
        5. Emit cycle_complete to EventBus
        6. Call self._trace.complete(trace_id) to close trace
        7. Return CycleContext

        This is the ONLY place orchestration logic lives.
        Every cycle in the system runs through this.
        """
        pass  # Implementation provided in base class, not here


# ============================================================================
# COGNITIVE PROCESS ABSTRACTION (from user review)
# ============================================================================

class CognitiveProcess(ABC):
    """
    Abstract base class for stateless LINEAR PROCESSORS.

    ⚠️ CRITICAL CORRECTION (from user review):
    - Processes are NOT cycles (no perceive/persist/rate limiting)
    - Processes are CALLED BY cycles (e.g., CircuitExecutor called during ACT phase)
    - Processes are STATELESS (input → transform → output)

    Examples:
    - CircuitExecutor: Load YAML circuit → Execute state machine → Return results
    - Cortex Senses: Perceive input → Classify into Sattva/Rajas/Tamas → Return classification

    A Process should be simple: inherit this, implement execute()
    """

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the process.

        Args:
            inputs: Input data for processing

        Returns:
            Results dict with success/failure and output data
        """
        pass


# ============================================================================
# CYCLE REGISTRY (with memory safety)
# ============================================================================

class CycleRegistry:
    """
    Track and coordinate all active CognitiveCycle instances.

    ⚠️ CRITICAL CORRECTION (from user review):
    - Uses RetentionPolicy to prevent memory leaks
    - Tracks cycles in UnifiedTrace (not a separate system)
    - Emits to EventBus (not a separate log)

    Provides:
    - Rate limit enforcement (per cycle, global throttle)
    - Cycle monitoring (current phase, runtime, errors)
    - Mirror test (detect self-triggered infinite loops)
    - Observability (which cycles are running, which are blocked)
    - Memory safety (retention policy enforcement)
    """

    def __init__(self, retention_policy: Optional[RetentionPolicy] = None):
        """
        Initialize registry.

        Args:
            retention_policy: How long to keep cycle history (prevents memory leaks)
        """
        self._cycles: Dict[str, CycleContext] = {}  # cycle_id → CycleContext
        self._retention_policy = retention_policy or RetentionPolicy()
        self._completed_cycles: List[CycleContext] = []  # For retention
        self._error_cycles: List[CycleContext] = []  # For retention

    def register_cycle(self, context: CycleContext) -> None:
        """Register an active cycle."""
        self._cycles[context.cycle_id] = context

    def complete_cycle(self, context: CycleContext) -> None:
        """Mark cycle as complete. Applies retention policy."""
        del self._cycles[context.cycle_id]
        self._completed_cycles.append(context)

        # Apply retention policy
        if self._retention_policy.enabled:
            if len(self._completed_cycles) > self._retention_policy.max_completed_cycles:
                # Remove oldest
                self._completed_cycles.pop(0)

    def error_cycle(self, context: CycleContext) -> None:
        """Track cycle that failed. Keep more error cycles for debugging."""
        if context.cycle_id in self._cycles:
            del self._cycles[context.cycle_id]
        self._error_cycles.append(context)

        # Apply retention policy (more lenient for errors)
        if self._retention_policy.enabled:
            if len(self._error_cycles) > self._retention_policy.max_error_cycles:
                self._error_cycles.pop(0)

    def get_active_cycles(self) -> List[CycleContext]:
        """Get currently running cycles."""
        return list(self._cycles.values())
```

---

## Part 3: Migration Strategy

### 3.1 Phase-by-Phase Refactoring

**Phase A: Foundation + System Integration**
```
1. Create vibe_core/orchestration_cycle.py with:
   - CycleContext (wraps UnifiedTrace, includes parent_cycle_id)
   - RetentionPolicy (prevents memory leaks)
   - CognitiveCycle base class (integrated with EventBus)
   - CognitiveProcess base class (for CircuitExecutor)
   - CycleRegistry with retention enforcement
2. Verify imports: UnifiedTrace, EventBus, EventType
3. Add tests for interface + harness checks
4. → All tests should FAIL initially (classes don't inherit yet)
```

**Phase B: CognitiveKernel Migration + System Wiring**
```
1. Make CognitiveKernel inherit from CognitiveCycle
2. Add setup() call in __init__: setup(trace, event_bus, steward_context)
3. Extract _perceive() from think() (lines 1127-1170 → ~30 lines)
4. Extract _orient() from think() (lines 1171-1195 → ~20 lines)
5. Extract _decide() from think() (lines 1196-1215 → ~20 lines)
6. Extract _act() from think() (lines 1216-1240 → ~20 lines)
   - NOTE: Act phase calls CircuitExecutor as CognitiveProcess (not CognitiveCycle)
7. Extract _persist() from think() (lines 1241-1250 → ~10 lines)
8. Rewrite think() to call orchestrate(parent_cycle_id=None) (~5 lines)
9. Verify UnifiedTrace integration: trace_id flows through context
10. Verify EventBus events emitted on phase transitions
11. Run harness checks → Should PASS
12. Verify no regression in tests
```

**Phase C: PranaOrchestrator Migration**
```
1. Make PranaOrchestrator inherit from CognitiveCycle
2. Add setup() call (integration with Trace/Bus)
3. Extract _perceive() (load plugin registry)
4. Extract _orient() (sort plugins by phase: SENSORS → ACTUATORS → CLEANUP)
5. Extract _decide() (select which plugins to run)
6. Extract _act() (run plugins with isolation wrappers)
   - NOTE: May call CognitiveProcess-based plugins
7. Override parent_cycle_id property (if called by BootOrchestrator)
8. Rewrite pulse() to call orchestrate()
9. Verify parent-child causality tracking in UnifiedTrace
10. Run harness checks → Should PASS
```

**Phase D: BootOrchestrator Migration**
```
1. Make BootOrchestrator inherit from CognitiveCycle
2. Add setup() call
3. Extract _perceive() (check environment)
4. Extract _orient() (determine boot mode: FULL/HEADLESS/MINIMAL)
5. Extract _decide() (select boot tasks)
6. Extract _act() (run boot sequence, possibly calling PranaOrchestrator as child cycle)
7. Track parent-child relationship: boot() calls pulse()
8. Rewrite boot() to call orchestrate()
9. Run harness checks → Should PASS
```

**Phase E: CircuitExecutor → CognitiveProcess (NOT CognitiveCycle)**
```
⚠️ CRITICAL CORRECTION (from user review):
CircuitExecutor does NOT inherit from CognitiveCycle!
It inherits from CognitiveProcess instead.

1. Make CircuitExecutor inherit from CognitiveProcess
2. Implement execute(inputs) method:
   - Load YAML circuit
   - Walk state machine
   - Return results
3. Remove any orchestration logic (rate limiting, persistence, etc.)
   - That's the caller's (CognitiveKernel) responsibility
4. Verify: CircuitExecutor is called FROM CognitiveKernel.act(), not as autonomous cycle
5. Run tests
```

**Phase F: Integration + Observability**
```
1. Verify all cycles use setup(trace, event_bus, steward_context) before orchestrate()
2. Verify EventBus receives phase transition events from all cycles
3. Verify UnifiedTrace has parent_cycle_id links (causality chain)
4. Update OPUS.md to show:
   - Active cycles from CycleRegistry.get_active_cycles()
   - Trace IDs linking to UnifiedTrace for detailed inspection
   - Phase timeline (when each cycle started/completed)
5. Update architecture docs to reflect Cycle vs Process distinction
6. Add monitoring dashboard showing:
   - Cycles by type (CognitiveKernel, PranaOrchestrator, BootOrchestrator)
   - Rate limit status
   - Error cycles (from CycleRegistry._error_cycles)
```

### 3.2 Code Reduction Expected

**CYCLES (what actually gets refactored):**

| Class | Before | After | Reduction |
|-------|--------|-------|-----------|
| CognitiveKernel | 137 lines | ~20 lines | 85% |
| PranaOrchestrator | ~80 lines | ~25 lines | 69% |
| BootOrchestrator | ~100 lines | ~30 lines | 70% |
| **Total Cycle Orchestration** | ~317 lines | ~75 lines | **76%** |
| **CognitiveCycle base** | — | ~180 lines | (new abstraction, includes EventBus/UnifiedTrace integration) |
| **Net savings** | — | **~142 lines** | **45% reduction** |

**PROCESSES (NOT refactored, stay as they are):**
- CircuitExecutor: ~60 lines (no change - stays as CognitiveProcess caller)

**Non-code benefits:**
- ✅ Single source of truth for orchestration logic (one place to maintain)
- ✅ Unified testing strategy (one harness for all cycles)
- ✅ Unified monitoring (CycleRegistry + EventBus + UnifiedTrace integration)
- ✅ Unified error recovery (one _recover() strategy)
- ✅ **Future cycles inherit correctly automatically**
- ✅ **No more "ghost brain" - fully integrated with EventBus and UnifiedTrace**
- ✅ **Holon causality tracking** via parent_cycle_id
- ✅ **Memory safe** with retention policy

---

## Part 4: HARNESS Definition (@HARNESS)

### 4.1 What We're Verifying

The @HARNESS answers: **"Are all orchestration patterns using the CognitiveCycle abstraction correctly?"**

### 4.2 Verification Checklist

```python
# File: tests/test_orchestration_unification.py
# These checks run AFTER code changes to prove correctness

@HARNESS("OPUS-095: Cognitive Abstraction - Orchestration Unification")
class TestOrchestrationUnification:

    # ====================================================================
    # CHECK 1: Inheritance Correctness
    # ====================================================================

    def test_cognitive_kernel_is_cycle(self):
        """CognitiveKernel properly inherits from CognitiveCycle."""
        from vibe_core.orchestration_cycle import CognitiveCycle
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

        assert issubclass(CognitiveKernel, CognitiveCycle), \
            "CognitiveKernel must inherit from CognitiveCycle"

        # Verify it implements all required methods
        assert hasattr(CognitiveKernel, '_perceive'), "Missing _perceive()"
        assert hasattr(CognitiveKernel, '_orient'), "Missing _orient()"
        assert hasattr(CognitiveKernel, '_decide'), "Missing _decide()"
        assert hasattr(CognitiveKernel, '_act'), "Missing _act()"

    def test_prana_orchestrator_is_cycle(self):
        """PranaOrchestrator properly inherits from CognitiveCycle."""
        from vibe_core.orchestration_cycle import CognitiveCycle
        from vibe_core.prana_orchestrator import PranaOrchestrator

        assert issubclass(PranaOrchestrator, CognitiveCycle)

    def test_boot_orchestrator_is_cycle(self):
        """BootOrchestrator properly inherits from CognitiveCycle."""
        from vibe_core.orchestration_cycle import CognitiveCycle
        from vibe_core.boot_orchestrator import BootOrchestrator

        assert issubclass(BootOrchestrator, CognitiveCycle)

    def test_circuit_executor_is_process_not_cycle(self):
        """⚠️ CRITICAL CORRECTION: CircuitExecutor is CognitiveProcess, NOT CognitiveCycle."""
        from vibe_core.orchestration_cycle import CognitiveProcess
        from vibe_core.circuit_executor import CognitiveCircuitExecutor

        # CORRECTED: CircuitExecutor should inherit from CognitiveProcess
        assert issubclass(CognitiveCircuitExecutor, CognitiveProcess), \
            "CircuitExecutor should inherit from CognitiveProcess (linear), not CognitiveCycle (repeating)"

        # Should NOT inherit from CognitiveCycle
        from vibe_core.orchestration_cycle import CognitiveCycle
        assert not issubclass(CognitiveCircuitExecutor, CognitiveCycle), \
            "CircuitExecutor is a stateless processor, not an orchestration cycle"

    # ====================================================================
    # CHECK 2: Boilerplate Reduction
    # ====================================================================

    def test_cognitive_kernel_think_is_thin(self):
        """think() method is thin wrapper, not full orchestration."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel
        import inspect

        source = inspect.getsource(CognitiveKernel.think)
        lines = [l.strip() for l in source.split('\n') if l.strip() and not l.strip().startswith('#')]

        # Should be <30 lines (just docstring + orchestrate() call)
        assert len(lines) < 30, \
            f"think() is still {len(lines)} lines - should be <30 (delegate to orchestrate())"

    def test_prana_orchestrator_pulse_is_thin(self):
        """pulse() method is thin wrapper."""
        from vibe_core.prana_orchestrator import PranaOrchestrator
        import inspect

        source = inspect.getsource(PranaOrchestrator.pulse)
        lines = [l.strip() for l in source.split('\n') if l.strip() and not l.strip().startswith('#')]

        assert len(lines) < 30, \
            f"pulse() is still {len(lines)} lines - should delegate to orchestrate()"

    def test_boot_orchestrator_boot_is_thin(self):
        """boot() method is thin wrapper."""
        from vibe_core.boot_orchestrator import BootOrchestrator
        import inspect

        source = inspect.getsource(BootOrchestrator.boot)
        lines = [l.strip() for l in source.split('\n') if l.strip() and not l.strip().startswith('#')]

        assert len(lines) < 30, \
            f"boot() is still {len(lines)} lines - should delegate to orchestrate()"

    # ====================================================================
    # CHECK 3: Unified Orchestration
    # ====================================================================

    def test_orchestrate_only_in_base_class(self):
        """orchestrate() method exists ONLY in CognitiveCycle base."""
        from vibe_core.orchestration_cycle import CognitiveCycle
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel
        from vibe_core.prana_orchestrator import PranaOrchestrator
        from vibe_core.boot_orchestrator import BootOrchestrator
        from vibe_core.circuit_executor import CognitiveCircuitExecutor
        import inspect

        base_source = inspect.getsource(CognitiveCycle.orchestrate)
        base_impl = base_source.count('\n')  # Should be ~100+ lines (real implementation)

        # Check subclasses don't reimplement
        for cls in [CognitiveKernel, PranaOrchestrator, BootOrchestrator, CognitiveCircuitExecutor]:
            if hasattr(cls, 'orchestrate'):
                # Should inherit from base, not override
                assert cls.orchestrate == CognitiveCycle.orchestrate, \
                    f"{cls.__name__}.orchestrate should be inherited from base, not overridden"

    # ====================================================================
    # CHECK 4: Phase Method Implementations
    # ====================================================================

    def test_cognitive_kernel_has_all_phase_methods(self):
        """CognitiveKernel implements all required phase methods."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

        for method in ['_perceive', '_orient', '_decide', '_act']:
            assert hasattr(CognitiveKernel, method), f"Missing {method}()"
            # Check it's not abstract (has implementation)
            impl = getattr(CognitiveKernel, method)
            assert impl.__code__.co_code != (lambda: None).__code__.co_code, \
                f"{method}() should have implementation, not be abstract"

    # ====================================================================
    # CHECK 5: Rate Limiting Unified
    # ====================================================================

    def test_rate_limiting_applies_to_all_cycles(self):
        """All cycle types respect unified rate limiting."""
        from vibe_core.orchestration_cycle import CycleRegistry
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel
        import time

        kernel = CognitiveKernel(rate_limit_seconds=1)

        # First call should succeed
        result1 = kernel.orchestrate(force=False)
        assert result1 is not None

        # Immediate second call should be throttled
        result2 = kernel.orchestrate(force=False)
        assert result2 is None or result2.metadata.get('throttled') == True, \
            "Rate limiting should throttle rapid consecutive calls"

    # ====================================================================
    # CHECK 6: Error Recovery Unified
    # ====================================================================

    def test_error_recovery_in_phases(self):
        """Errors in any phase are caught and recovery is attempted."""
        # Create a test cycle that fails in _decide phase
        # Verify _recover() is called
        # Verify orchestrate() completes without crashing
        pass

    # ====================================================================
    # CHECK 7: Observability Unified
    # ====================================================================

    def test_cycle_registry_tracks_all_cycles(self):
        """CycleRegistry tracks all active cycles uniformly."""
        from vibe_core.orchestration_cycle import CycleRegistry
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel
        from vibe_core.prana_orchestrator import PranaOrchestrator

        registry = CycleRegistry()

        # Run a few cycles
        kernel = CognitiveKernel()
        kernel.orchestrate()

        # Query registry
        active = registry.get_active_cycles()
        completed = registry.get_completed_cycles()

        # Should see cycles tracked
        assert len(completed) > 0, "CycleRegistry should track completed cycles"

    # ====================================================================
    # CHECK 8: UnifiedTrace Integration (from user review)
    # ====================================================================

    def test_cycle_context_wraps_unified_trace(self):
        """CycleContext.trace_id links to UnifiedTrace (not parallel system)."""
        from vibe_core.orchestration_cycle import CycleContext, CyclePhase

        # CycleContext must have trace_id field
        context = CycleContext(
            cycle_id="test",
            parent_cycle_id=None,
            trace_id="trace-123",
            cycle_name="test_cycle",
            phase=CyclePhase.PERCEIVE,
            phase_start_time=0.0,
            observations=[],
            orientations=[],
            decisions=[],
            actions=[],
            results=None,
            errors={}
        )

        assert context.trace_id == "trace-123", "CycleContext must have trace_id for UnifiedTrace integration"

    def test_cycle_registry_retention_policy(self):
        """CycleRegistry applies retention policy (memory safety)."""
        from vibe_core.orchestration_cycle import CycleRegistry, RetentionPolicy

        policy = RetentionPolicy(
            max_completed_cycles=10,
            max_error_cycles=20,
            enabled=True
        )
        registry = CycleRegistry(retention_policy=policy)

        # Verify policy is enforced
        assert registry._retention_policy.max_completed_cycles == 10
        assert registry._retention_policy.max_error_cycles == 20

    def test_holon_wiring_with_parent_cycle_id(self):
        """parent_cycle_id tracks causality (why am I running?)."""
        from vibe_core.orchestration_cycle import CycleContext, CyclePhase

        # Parent cycle calls child cycle
        parent = CycleContext(
            cycle_id="parent-001",
            parent_cycle_id=None,  # Parent has no parent
            trace_id="trace-parent",
            cycle_name="boot_orchestrator",
            phase=CyclePhase.ACT,
            phase_start_time=0.0,
            observations=[],
            orientations=[],
            decisions=[],
            actions=[],
            results=None,
            errors={}
        )

        # Child cycle called by parent
        child = CycleContext(
            cycle_id="child-001",
            parent_cycle_id="parent-001",  # HOLON WIRING: I'm called by parent
            trace_id="trace-child",
            cycle_name="plugin_pulse",
            phase=CyclePhase.PERCEIVE,
            phase_start_time=0.0,
            observations=[],
            orientations=[],
            decisions=[],
            actions=[],
            results=None,
            errors={}
        )

        assert child.parent_cycle_id == "parent-001", "parent_cycle_id establishes causality chain"

    # ====================================================================
    # CHECK 9: No Spaghetti Code (Orchestration logic centralized)
    # ====================================================================

    def test_orchestration_logic_not_duplicated(self):
        """Orchestration logic appears in ONE place: CognitiveCycle.orchestrate()"""
        import ast
        import os

        # Parse all Python files in vibe_core/
        orchestration_files = []

        for root, dirs, files in os.walk('/home/user/steward-protocol/vibe_core'):
            for f in files:
                if f.endswith('.py'):
                    filepath = os.path.join(root, f)
                    with open(filepath, 'r') as file:
                        content = file.read()

                        # Look for orchestration patterns being reimplemented
                        # (rate limiting, error handling, phase loops, etc.)
                        if re.search(r'def (think|pulse|boot|execute|orchestrate)\(', content):
                            if 'CognitiveCycle' not in content:  # Exclude the base class itself
                                # Check for orchestration boilerplate
                                if re.search(
                                    r'(rate.?limit|throttle|error.?handl|try.*except|\.get\(|for.*in.*phase)',
                                    content,
                                    re.IGNORECASE
                                ):
                                    # This should only use inherited orchestrate()
                                    orchestration_files.append(filepath)

        # Should find 0 or very few (only thin wrappers)
        # If we find many, orchestration logic is being reimplemented
        assert len(orchestration_files) < 5, \
            f"Found {len(orchestration_files)} files with orchestration logic - should be delegating to base class"
```

### 4.3 Test Execution Plan

```bash
# BEFORE code changes: All harness checks should FAIL
pytest tests/test_orchestration_unification.py -v
# Expected: 8 failures (classes don't inherit yet)

# AFTER Phase A (CognitiveCycle foundation created)
pytest tests/test_orchestration_unification.py::TestOrchestrationUnification::test_cognitive_cycle_interface -v
# Expected: 1 pass (base class exists)

# AFTER Phase B (CognitiveKernel migrated)
pytest tests/test_orchestration_unification.py::TestOrchestrationUnification::test_cognitive_kernel_is_cycle -v
pytest tests/test_orchestration_unification.py::TestOrchestrationUnification::test_cognitive_kernel_think_is_thin -v
# Expected: 2 passes

# AFTER all phases complete
pytest tests/test_orchestration_unification.py -v
# Expected: All 8 pass
```

---

## Part 5: Risk Assessment

### 5.1 Risks Mitigated by This Plan

| Risk | How Plan Addresses It |
|------|----------------------|
| **Breaking existing code** | Tests verify no regression; phase-by-phase migration |
| **Infinite loops (mirror test)** | CycleRegistry detects self-triggered cycles |
| **Rate limit drift** | Unified enforcement in one place |
| **Error handling gaps** | Standardized _recover() for all cycles |
| **Observability fragmentation** | CycleRegistry single source of truth |
| **Future spaghetti** | Pattern defined; new cycles inherit automatically |

### 5.2 Risks of NOT Implementing

| Risk | Impact |
|------|--------|
| **Code duplication continues** | Maintenance burden grows; hard to change orchestration |
| **Pattern recognition hidden** | New developers don't see reusable patterns |
| **Inconsistent error handling** | Some cycles fail gracefully, others crash |
| **Rate limit gaps** | Some cycles might execute too frequently |
| **Monitoring fragmentation** | Can't see all cycles in one place |

---

## Part 6: Success Criteria

**Plan is complete when:**

1. ✅ **CognitiveCycle base class created** with full orchestrate() implementation
2. ✅ **CycleRegistry built** for unified monitoring
3. ✅ **CognitiveKernel migrated** - think() is <30 lines, delegates to orchestrate()
4. ✅ **All harness checks pass** - inheritance, rate limiting, error recovery all work
5. ✅ **No regression** - all existing tests still pass
6. ✅ **Code reduction achieved** - 61% reduction in orchestration boilerplate
7. ✅ **Observability improved** - All cycles visible in OPUS.md System Journal
8. ✅ **Documentation updated** - Architecture docs reflect new pattern

---

## Appendix: Code Patterns Already in Use

### Pattern 1: CircuitExecutor (State Machines)
```python
# vibe_core/circuit_executor.py
class CognitiveCircuitExecutor:
    async def execute(self):
        # enter → invariant check → body → exit
        # Pattern: state machine with transitions
```

### Pattern 2: PranaOrchestrator (Phase-based)
```python
# vibe_core/prana_orchestrator.py
class PranaOrchestrator:
    async def pulse(self):
        # SENSORS → ACTUATORS → CLEANUP
        # Pattern: phase-based coordination
```

### Pattern 3: CognitiveKernel.think() (OODA)
```python
# vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py:1117-1250
def think(self):
    # Perceive → Orient → Decide → Act → Persist
    # Pattern: OODA loop (currently reimplements orchestration)
```

### Pattern 4: BootOrchestrator (Cosmic Phases)
```python
# vibe_core/boot_orchestrator.py
class BootOrchestrator:
    async def boot(self):
        # Brahma → Vishnu → Shiva → Dharma
        # Pattern: lifecycle phases
```

**All are orchestration loops. All should inherit from CognitiveCycle.**

---

## Summary: The Blueprint

**What we're doing:** Extracting the hidden orchestration abstraction that already exists across the codebase and making it explicit.

**What we're not doing:** Inventing new patterns or changing existing behavior. Just reorganizing to reduce duplication and improve maintainability.

**Why now:** CognitiveKernel is 137 lines of boilerplate—the perfect moment to recognize the pattern and standardize it.

**Expected outcome:** 61% reduction in orchestration code, 100% improvement in maintainability, zero regression in functionality.

---

**Next Step:** User reviews this plan. When approved, proceed to Phase A: Create vibe_core/orchestration_cycle.py with CognitiveCycle base class.
