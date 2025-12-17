# OPUS-095: Cognitive Abstraction - Unifying Orchestration Patterns

**Status:** Planning Phase (No Code Changes Yet)
**Author:** Forensic Analysis Team (MANAS + Senior)
**Date:** Session Context Continuation
**Scope:** Architecture Blueprint for CognitiveKernel Refactoring

---

## Executive Summary

**The Problem:**
CognitiveKernel.think() is a 137-line god object that reimplements core orchestration logic that already exists in CircuitExecutor, PranaOrchestrator, BootOrchestrator, and MetaCircuitManager. This creates:
- Code duplication across 8+ orchestration layers
- Maintenance burden (changes must propagate to multiple places)
- Testing fragmentation (same patterns tested separately in each class)
- Architectural blindness (patterns hidden, difficult to refactor globally)

**The Opportunity:**
Extract a unifying `CognitiveCycle` abstraction that ALL orchestration layers inherit from. This reduces CognitiveKernel from 137 lines to ~20 lines of pure cognition logic, while standardizing the orchestration loop across the entire system.

**The Pattern Already Exists:**
This is not inventing new architecture—it's recognizing patterns that are already present:
- CircuitExecutor uses state machines with invariant checking
- PranaOrchestrator uses phase-based plugin lifecycle (SENSORS → ACTUATORS → CLEANUP)
- BootOrchestrator uses sarga phases for cosmic creation metaphor
- think() uses observe-orient-decide-act (OODA)

All are orchestration loops. All should inherit from a common abstraction.

---

## Part 1: The Existing Patterns

### 1.1 Pattern Analysis Summary

| Class | Location | Loop Type | Structure | Reusability |
|-------|----------|-----------|-----------|-------------|
| **CircuitExecutor** | vibe_core/circuit_executor.py | State Machine | enter → invariant → body → exit | YES - used by all circuits |
| **PranaOrchestrator** | vibe_core/prana_orchestrator.py | Phase-based | SENSORS → ACTUATORS → CLEANUP | YES - used by plugin pulse |
| **BootOrchestrator** | vibe_core/boot_orchestrator.py | Sarga Phases | Brahma → Vishnu → Shiva → Dharma | YES - used for boot |
| **MetaCircuitManager** | vibe_core/circuit_executor.py | Task Tracking | execute → track → callback → recover | YES - used for error handling |
| **CognitiveKernel.think()** | manas/cognitive_kernel.py:1117-1250 | OODA Loop | Observe → Orient → Decide → Act | NO - reimplements instead of reuses |
| **ShivaLifecycleManager** | manas/shiva_lifecycle.py | Sweep Cycle | scan → evaluate → archive → cleanup | Implicit pattern, not abstracted |
| **SankalpaOrchestrator** | manas/sankalpa_orchestrator.py | Strategy Loop | evaluate → plan → rank → suggest | Implicit pattern, not abstracted |
| **Cortex Senses** | manas/cortex_senses.py | Perception | perceive → classify → report → update | Implicit pattern, not abstracted |

**Key Insight:** Every orchestration class is implementing the same loop pattern independently. If we extract this, we get:
- Unified testing (one harness for all)
- Unified monitoring (one observability layer)
- Unified error handling (one recovery mechanism)
- Unified rate limiting (one throttle strategy)
- Code reduction of ~60% for orchestration layers

### 1.2 Existing Code Locations

**CircuitExecutor (the best abstraction so far):**
- Path: `vibe_core/circuit_executor.py`
- State machine pattern with generic execute() framework
- Invariant checking on entry/exit
- Callback system for error recovery
- **Missing:** explicit OODA loop; perception layer separate

**PranaOrchestrator (plugin lifecycle):**
- Path: `vibe_core/prana_orchestrator.py`
- Phase-based execution (SENSORS, ACTUATORS, CLEANUP)
- Isolation wrappers for fault tolerance
- Plugin discovery and ordering
- **Missing:** explicit decision/filtering layer; no inherent rate limiting

**BootOrchestrator (cosmic creation):**
- Path: `vibe_core/boot_orchestrator.py`
- Sarga phases: Brahma (creation) → Vishnu (maintenance) → Shiva (destruction) → Dharma (rules)
- Supports FULL/HEADLESS/MINIMAL modes
- **Missing:** observation and orientation; treats boot as one-time, not continuous

**MetaCircuitManager (error recovery):**
- Path: `vibe_core/circuit_executor.py` (same file as CircuitExecutor)
- Task tracking with callbacks
- Error recovery with exponential backoff
- **Missing:** larger orchestration context; sees only execution errors

**CognitiveKernel.think() (the problem):**
- Path: `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py:1117-1250`
- 137 lines mixing orchestration boilerplate with pure cognition logic
- Contains: rate limiting, mirror test, 4x perception, cleanup, sweep, generate, judge, record, auto-execute, persist
- **Problem:** Reimplements all of this instead of inheriting from base

---

## Part 2: The Abstraction Blueprint

### 2.1 The CognitiveCycle Interface

```python
# This is a signature, not implementation
# Location: vibe_core/orchestration_cycle.py (new file)

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

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
    """Execution context passed through the cycle."""
    cycle_id: str               # Unique ID for this execution
    phase: CyclePhase          # Current phase
    observations: List[Any]    # From PERCEIVE
    orientations: List[Any]    # From ORIENT
    decisions: List[Any]       # From DECIDE
    actions: List[Any]         # From ACT
    results: Optional[Any]     # From execution
    errors: Dict[str, str]     # Accumulated errors
    metadata: Dict[str, Any]   # Custom per-cycle data


class CognitiveCycle(ABC):
    """
    Abstract base class for ALL orchestration loops in the system.

    This replaces scattered orchestration logic with unified structure:
    - CircuitExecutor loops (state machines)
    - PranaOrchestrator loops (plugin phases)
    - BootOrchestrator loops (cosmic phases)
    - CognitiveKernel loops (MANAS thinking)
    - Any future orchestration patterns

    The Template Method: orchestrate() runs the standard cycle.
    Subclasses implement the _perceive(), _orient(), _decide(), _act() logic.
    """

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

    async def orchestrate(self, force: bool = False) -> CycleContext:
        """
        RUN THE CYCLE: This is the unified orchestration loop.

        All concrete loops (CognitiveKernel, PranaOrchestrator, etc.)
        inherit this. They only implement the phase methods above.

        Flow:
        1. Check rate limiting + cache
        2. Create cycle context
        3. PERCEIVE phase
        4. ORIENT phase
        5. DECIDE phase
        6. ACT phase
        7. PERSIST state
        8. RECOVER if errors
        9. Return context with all results

        This is the only place orchestration logic lives.
        Every cycle in the system runs through this.
        """
        pass  # Implementation provided in base class, not here


class CycleRegistry:
    """
    Track and coordinate all active CognitiveCycle instances.

    Provides:
    - Rate limit enforcement (per cycle, global throttle)
    - Cycle monitoring (current phase, runtime, errors)
    - Mirror test (detect self-triggered infinite loops)
    - Observability (which cycles are running, which are blocked)
    """
    pass  # Signature only
```

---

## Part 3: Migration Strategy

### 3.1 Phase-by-Phase Refactoring

**Phase A: Foundation**
```
1. Create vibe_core/orchestration_cycle.py with CognitiveCycle base class
2. Create CycleRegistry for unified monitoring
3. Add tests for interface + harness checks
4. → All tests should FAIL initially (classes don't inherit yet)
```

**Phase B: CognitiveKernel Migration**
```
1. Make CognitiveKernel inherit from CognitiveCycle
2. Extract _perceive() from think() (lines 1127-1170 → ~30 lines)
3. Extract _orient() from think() (lines 1171-1195 → ~20 lines)
4. Extract _decide() from think() (lines 1196-1215 → ~20 lines)
5. Extract _act() from think() (lines 1216-1240 → ~20 lines)
6. Extract _persist() from think() (lines 1241-1250 → ~10 lines)
7. Rewrite think() to call orchestrate() (~5 lines)
8. Run harness checks → Should PASS
9. Verify no regression in tests
```

**Phase C: PranaOrchestrator Migration**
```
1. Make PranaOrchestrator inherit from CognitiveCycle
2. Extract _perceive() (load plugin registry)
3. Extract _orient() (sort plugins by phase: SENSORS → ACTUATORS → CLEANUP)
4. Extract _decide() (select which plugins to run)
5. Extract _act() (run plugins with isolation wrappers)
6. Rewrite pulse() to call orchestrate()
7. Run harness checks → Should PASS
```

**Phase D: BootOrchestrator Migration**
```
1. Make BootOrchestrator inherit from CognitiveCycle
2. Extract _perceive() (check environment)
3. Extract _orient() (determine boot mode)
4. Extract _decide() (select boot tasks)
5. Extract _act() (run boot sequence)
6. Rewrite boot() to call orchestrate()
7. Run harness checks → Should PASS
```

**Phase E: CircuitExecutor Migration**
```
1. Make CircuitExecutor inherit from CognitiveCycle
2. Extract _perceive() (load circuit + invariants)
3. Extract _orient() (classify state)
4. Extract _decide() (apply guards)
5. Extract _act() (run circuit body)
6. Rewrite execute() to call orchestrate()
7. Run harness checks → Should PASS
```

**Phase F: Integration + Monitoring**
```
1. Update OPUS.md to show all active cycles (via CycleRegistry)
2. Add cycle monitoring to dashboard
3. Verify unified error recovery works across all cycle types
4. Verify unified rate limiting works
5. Update architecture docs to reflect new pattern
```

### 3.2 Code Reduction Expected

| Class | Before | After | Reduction |
|-------|--------|-------|-----------|
| CognitiveKernel | 137 lines | ~20 lines | 85% |
| PranaOrchestrator | ~80 lines | ~25 lines | 69% |
| BootOrchestrator | ~100 lines | ~30 lines | 70% |
| CircuitExecutor | ~60 lines | ~20 lines | 67% |
| **Total Orchestration** | ~377 lines | ~95 lines | **75%** |
| **CognitiveCycle base** | — | ~150 lines | (new abstraction) |
| **Net savings** | — | ~232 lines | **61% reduction** |

**Non-code benefits:**
- Single source of truth for orchestration logic
- Unified testing strategy (one harness, applied to all cycles)
- Unified monitoring (CycleRegistry for all cycles)
- Unified error recovery (one _recover() strategy)
- Future cycles inherit correctly automatically

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

    def test_circuit_executor_is_cycle(self):
        """CircuitExecutor properly inherits from CognitiveCycle."""
        from vibe_core.orchestration_cycle import CognitiveCycle
        from vibe_core.circuit_executor import CognitiveCircuitExecutor

        assert issubclass(CognitiveCircuitExecutor, CognitiveCycle)

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
    # CHECK 8: No Spaghetti Code
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
