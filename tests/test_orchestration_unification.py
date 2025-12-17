"""
OPUS-095: Orchestration Unification - Test Harness

This harness verifies that the CognitiveCycle abstraction is correctly implemented
and properly integrated with UnifiedTrace, EventBus, and the Holon architecture.

These tests are designed to FAIL initially (when classes don't inherit yet)
and then PASS after each phase of migration (CognitiveKernel, PranaOrchestrator, etc.)

Running these tests:
    pytest tests/test_orchestration_unification.py -v
"""

import asyncio

import pytest

from vibe_core.event_bus import EventBus, EventType
from vibe_core.orchestration_cycle import (
    CognitiveCycle,
    CognitiveProcess,
    CycleContext,
    CyclePhase,
    CycleRegistry,
    RetentionPolicy,
)
from vibe_core.runtime.unified_trace import UnifiedTrace

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def unified_trace():
    """Provide UnifiedTrace instance for tests."""
    return UnifiedTrace()


@pytest.fixture
def event_bus():
    """Provide EventBus instance for tests."""
    return EventBus(max_history=100)


@pytest.fixture
def steward_context():
    """Provide minimal StewardContext for tests."""
    return {"name": "test_context"}


# ============================================================================
# TEST HARNESS - Part 1: Foundation Verification
# ============================================================================


class TestCycleContextIntegration:
    """Verify CycleContext properly wraps UnifiedTrace (not a parallel system)."""

    def test_cycle_context_has_trace_id(self):
        """CycleContext.trace_id links to UnifiedTrace."""
        context = CycleContext(
            cycle_id="test-001",
            parent_cycle_id=None,
            trace_id="trace-abc123",
            cycle_name="test_cycle",
            phase=CyclePhase.PERCEIVE,
            phase_start_time=0.0,
        )

        assert context.trace_id == "trace-abc123", "CycleContext must have trace_id for UnifiedTrace integration"

    def test_cycle_context_holon_wiring(self):
        """parent_cycle_id establishes Holon causality (why am I running?)."""
        parent = CycleContext(
            cycle_id="parent-001",
            parent_cycle_id=None,  # Parent has no parent
            trace_id="trace-parent",
            cycle_name="boot_orchestrator",
            phase=CyclePhase.ACT,
            phase_start_time=0.0,
        )

        child = CycleContext(
            cycle_id="child-001",
            parent_cycle_id="parent-001",  # HOLON WIRING
            trace_id="trace-child",
            cycle_name="plugin_pulse",
            phase=CyclePhase.PERCEIVE,
            phase_start_time=0.0,
        )

        assert parent.parent_cycle_id is None, "Parent cycle should have no parent"
        assert child.parent_cycle_id == "parent-001", "Child should know why it's running (parent ID)"

    def test_cycle_context_error_tracking(self):
        """CycleContext tracks errors per phase."""
        context = CycleContext(
            cycle_id="test-001",
            parent_cycle_id=None,
            trace_id="trace-abc",
            cycle_name="test",
            phase=CyclePhase.PERCEIVE,
            phase_start_time=0.0,
        )

        assert not context.has_errors(), "Fresh context should have no errors"

        context.add_error("perceive", "Permission denied")
        assert context.has_errors(), "Context should track errors"
        assert context.errors["perceive"] == "Permission denied"


class TestRetentionPolicyMemorySafety:
    """Verify retention policy prevents memory leaks."""

    def test_retention_policy_defaults(self):
        """Default retention policy is sensible."""
        policy = RetentionPolicy()

        assert policy.max_completed_cycles == 100, "Should keep last 100 completed cycles"
        assert policy.max_error_cycles == 500, "Should keep more errors for debugging"
        assert policy.enabled, "Retention should be enabled by default"

    def test_retention_policy_custom(self):
        """Custom retention policy values are respected."""
        policy = RetentionPolicy(
            max_completed_cycles=50,
            max_error_cycles=200,
            enabled=True,
        )

        assert policy.max_completed_cycles == 50
        assert policy.max_error_cycles == 200
        assert policy.enabled


class TestCycleRegistryMemorySafety:
    """Verify CycleRegistry prevents unbounded memory growth."""

    def test_cycle_registry_retention_enforcement(self):
        """CycleRegistry applies retention policy."""
        policy = RetentionPolicy(max_completed_cycles=5, max_error_cycles=10, enabled=True)
        registry = CycleRegistry(retention_policy=policy)

        # Add more than max_completed_cycles
        for i in range(10):
            context = CycleContext(
                cycle_id=f"test-{i}",
                parent_cycle_id=None,
                trace_id=f"trace-{i}",
                cycle_name="test",
                phase=CyclePhase.PERCEIVE,
                phase_start_time=0.0,
            )
            registry.complete_cycle(context)

        # Should only keep 5 completed cycles (not 10)
        completed = registry.get_completed_cycles()
        assert len(completed) <= 5, f"Should have ≤5 completed cycles, got {len(completed)}"

    def test_cycle_registry_tracks_active_cycles(self):
        """CycleRegistry tracks currently running cycles."""
        registry = CycleRegistry()

        context1 = CycleContext(
            cycle_id="test-1",
            parent_cycle_id=None,
            trace_id="trace-1",
            cycle_name="cycle1",
            phase=CyclePhase.PERCEIVE,
            phase_start_time=0.0,
        )

        registry.register_cycle(context1)
        active = registry.get_active_cycles()
        assert len(active) == 1, "Should track 1 active cycle"
        assert active[0].cycle_id == "test-1"

    def test_cycle_registry_tracks_errors(self):
        """CycleRegistry keeps more errors than successes (for debugging)."""
        registry = CycleRegistry()

        # Mark some cycles as errors
        for i in range(3):
            context = CycleContext(
                cycle_id=f"error-{i}",
                parent_cycle_id=None,
                trace_id=f"trace-{i}",
                cycle_name="test",
                phase=CyclePhase.PERCEIVE,
                phase_start_time=0.0,
            )
            context.add_error("perceive", f"Error {i}")
            registry.error_cycle(context)

        errors = registry.get_error_cycles()
        assert len(errors) == 3, "Should track all 3 error cycles"


class TestCognitiveCycleAbstraction:
    """Verify CognitiveCycle is a proper abstract base class."""

    def test_cognitive_cycle_requires_abstract_methods(self):
        """CognitiveCycle cannot be instantiated directly (abstract)."""
        with pytest.raises(TypeError, match="abstract"):
            # Should fail because abstract methods are not implemented
            CognitiveCycle()  # type: ignore

    def test_cognitive_cycle_concrete_implementation(self):
        """Test implementation of CognitiveCycle must provide all methods."""

        class TestCycle(CognitiveCycle):
            """Minimal concrete implementation for testing."""

            @property
            def cycle_name(self) -> str:
                return "test_cycle"

            @property
            def rate_limit_seconds(self) -> int:
                return 0  # No rate limit

            @property
            def timeout_seconds(self) -> int:
                return 0  # No timeout

            @property
            def recovery_enabled(self) -> bool:
                return True

            async def _perceive(self):
                return (["observation1"], {})

            async def _orient(self, observations):
                return (["orientation1"], {})

            async def _decide(self, orientations):
                return (["decision1"], {})

            async def _act(self, decisions):
                return ({"result": "done"}, {})

        cycle = TestCycle()
        assert cycle.cycle_name == "test_cycle"
        assert cycle.rate_limit_seconds == 0
        assert cycle.timeout_seconds == 0
        assert cycle.recovery_enabled is True

    @pytest.mark.asyncio
    async def test_cognitive_cycle_setup_required(self, unified_trace, event_bus, steward_context):
        """CognitiveCycle requires setup() before orchestrate()."""

        class TestCycle(CognitiveCycle):
            @property
            def cycle_name(self) -> str:
                return "test"

            @property
            def rate_limit_seconds(self) -> int:
                return 0

            @property
            def timeout_seconds(self) -> int:
                return 0

            @property
            def recovery_enabled(self) -> bool:
                return True

            async def _perceive(self):
                return ([], {})

            async def _orient(self, obs):
                return ([], {})

            async def _decide(self, orient):
                return ([], {})

            async def _act(self, decisions):
                return (None, {})

        cycle = TestCycle()

        # Should fail without setup()
        with pytest.raises(RuntimeError, match="setup"):
            await cycle.orchestrate()

        # Should succeed after setup()
        cycle.setup(unified_trace, event_bus, steward_context)
        context = await cycle.orchestrate()
        assert context is not None

    @pytest.mark.asyncio
    async def test_cognitive_cycle_full_orchestration(self, unified_trace, event_bus, steward_context):
        """Verify full orchestration loop runs correctly."""

        class TestCycle(CognitiveCycle):
            def __init__(self):
                super().__init__()
                self.perceive_called = False
                self.orient_called = False
                self.decide_called = False
                self.act_called = False

            @property
            def cycle_name(self) -> str:
                return "test_orchestration"

            @property
            def rate_limit_seconds(self) -> int:
                return 0

            @property
            def timeout_seconds(self) -> int:
                return 0

            @property
            def recovery_enabled(self) -> bool:
                return True

            async def _perceive(self):
                self.perceive_called = True
                return (["obs1", "obs2"], {})

            async def _orient(self, obs):
                self.orient_called = True
                assert len(obs) == 2
                return (["orient1"], {})

            async def _decide(self, orient):
                self.decide_called = True
                assert len(orient) == 1
                return (["action1", "action2"], {})

            async def _act(self, decisions):
                self.act_called = True
                assert len(decisions) == 2
                return ({"executed": 2}, {})

        cycle = TestCycle()
        cycle.setup(unified_trace, event_bus, steward_context)

        context = await cycle.orchestrate()

        # Verify all phases ran
        assert cycle.perceive_called, "PERCEIVE should be called"
        assert cycle.orient_called, "ORIENT should be called"
        assert cycle.decide_called, "DECIDE should be called"
        assert cycle.act_called, "ACT should be called"

        # Verify context was populated
        assert context is not None
        assert len(context.observations) == 2
        assert len(context.orientations) == 1
        assert len(context.decisions) == 2
        assert context.results == {"executed": 2}

        # Verify trace was created
        trace = unified_trace.get_trace(context.trace_id)
        assert len(trace) > 0, "Should have trace events"


class TestCognitiveProcessAbstraction:
    """Verify CognitiveProcess is a proper base class for linear processors."""

    def test_cognitive_process_requires_execute(self):
        """CognitiveProcess cannot be instantiated without execute() implementation."""
        with pytest.raises(TypeError, match="abstract"):
            CognitiveProcess()  # type: ignore

    def test_cognitive_process_concrete_implementation(self):
        """Test implementation of CognitiveProcess must provide execute()."""

        class TestProcess(CognitiveProcess):
            """Minimal concrete process for testing."""

            async def execute(self, inputs):
                return {
                    "success": True,
                    "output": inputs,
                    "error": None,
                }

        process = TestProcess()
        assert process is not None

        # Should be callable
        result = asyncio.run(process.execute({"test": "data"}))
        assert result["success"]
        assert result["output"] == {"test": "data"}


class TestUnifiedTraceIntegration:
    """Verify CycleContext integrates with UnifiedTrace."""

    def test_unified_trace_cycle_flow(self, unified_trace):
        """Test flow: start → emit → complete."""
        trace_id = unified_trace.start("test_component", "test_event", {"key": "value"})
        assert trace_id is not None

        unified_trace.emit(trace_id, "test_component", "step1", {"data": "a"})
        unified_trace.emit(trace_id, "test_component", "step2", {"data": "b"})

        unified_trace.complete(trace_id, {"final": "result"})

        trace = unified_trace.get_trace(trace_id)
        assert len(trace) >= 3, "Should have start, 2 emits, complete"
        assert trace[0]["event_type"] == "test_event"
        assert trace[-1]["event_type"] == "complete"


class TestEventBusIntegration:
    """Verify EventBus is ready for phase transition events."""

    @pytest.mark.asyncio
    async def test_event_bus_receives_events(self, event_bus):
        """EventBus can receive and emit events."""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_bus.subscribe(handler, EventType.THOUGHT)

        # Simulate a phase event
        from vibe_core.event_bus import Event

        event = Event(
            event_type=EventType.THOUGHT,
            agent_id="test_cycle",
            message="Testing",
            details={"phase": "perceive"},
        )

        await event_bus.emit(event)

        assert len(received_events) == 1
        assert received_events[0].agent_id == "test_cycle"


# ============================================================================
# TEST HARNESS - Part 2: Post-Migration Checks (for Phase B, C, D, E)
# ============================================================================


class TestCognitiveKernelMigration:
    """These tests FAIL before Phase B, PASS after Phase B migration."""

    def test_cognitive_kernel_is_cycle(self):
        """CognitiveKernel properly inherits from CognitiveCycle."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

        assert issubclass(CognitiveKernel, CognitiveCycle)

    def test_cognitive_kernel_think_is_thin(self):
        """think() method is thin wrapper, not full orchestration."""
        import inspect

        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

        source = inspect.getsource(CognitiveKernel.think)
        lines = [l.strip() for l in source.split("\n") if l.strip() and not l.strip().startswith("#")]

        assert len(lines) < 30, f"think() is still {len(lines)} lines - should be <30 (delegate to orchestrate())"


class TestPranaOrchestratorMigration:
    """These tests FAIL before Phase C, PASS after Phase C migration."""

    def test_prana_orchestrator_is_cycle(self):
        """PranaOrchestrator properly inherits from CognitiveCycle."""
        from vibe_core.prana_orchestrator import PranaOrchestrator

        assert issubclass(PranaOrchestrator, CognitiveCycle)

    def test_prana_orchestrator_pulse_is_thin(self):
        """pulse() method is thin wrapper delegating to orchestrate()."""
        import inspect

        from vibe_core.prana_orchestrator import PranaOrchestrator

        source = inspect.getsource(PranaOrchestrator.pulse)
        lines = [l.strip() for l in source.split("\n") if l.strip() and not l.strip().startswith("#")]

        assert len(lines) < 15, f"pulse() is {len(lines)} lines - should be <15 (thin wrapper)"


class TestBootOrchestratorMigration:
    """These tests FAIL before Phase D, PASS after Phase D migration."""

    def test_boot_orchestrator_is_cycle(self):
        """BootOrchestrator properly inherits from CognitiveCycle."""
        from vibe_core.boot_orchestrator import BootOrchestrator

        assert issubclass(BootOrchestrator, CognitiveCycle)

    def test_boot_orchestrator_boot_is_thin(self):
        """boot() method is thin wrapper delegating to orchestrate()."""
        import inspect

        from vibe_core.boot_orchestrator import BootOrchestrator

        source = inspect.getsource(BootOrchestrator.boot)
        lines = [l.strip() for l in source.split("\n") if l.strip() and not l.strip().startswith("#")]

        assert len(lines) < 15, f"boot() is {len(lines)} lines - should be <15 (thin wrapper)"


class TestCircuitExecutorCorrection:
    """Test CRITICAL CORRECTION: CircuitExecutor is CognitiveProcess, NOT CognitiveCycle."""

    def test_circuit_executor_is_process_not_cycle(self):
        """CircuitExecutor inherits from CognitiveProcess, NOT CognitiveCycle."""
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import CognitiveCircuitExecutor

        # Should inherit from CognitiveProcess
        assert issubclass(CognitiveCircuitExecutor, CognitiveProcess)

        # Should NOT inherit from CognitiveCycle
        assert not issubclass(CognitiveCircuitExecutor, CognitiveCycle)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
