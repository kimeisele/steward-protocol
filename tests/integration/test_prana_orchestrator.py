"""
OPUS-087: PRANA Orchestrator Tests
==================================

TDD-first test suite for the PRANA Pulse Architecture.

Tests cover:
- Isolation failure (one plugin crash doesn't kill others)
- Phase ordering (SENSORS → COGNITION → ACTUATORS → CLEANUP)
- Rate limiting (min 60s enforced)
- Mutation validation
- Transaction commit fail-forward
- Plugin quarantine
"""

import pytest

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult, PulsePhase
from vibe_core.prana_orchestrator import (
    ALLOWED_ACTIONS,
    PranaOrchestrator,
    PranaOrchestratorConfig,
    PulseTransaction,
    StateMutation,
)

# =============================================================================
# TEST FIXTURES: Mock Plugins
# =============================================================================


class MockSensorPlugin(KernelPlugin):
    """Mock plugin that runs in SENSORS phase."""

    def __init__(self, plugin_id: str = "mock_sensor"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.SENSORS

    def on_pulse(self, kernel, transaction) -> HookResult:
        transaction.register(
            StateMutation(
                plugin_id=self.plugin_id,
                action="log_observation",
                target="journal/sensors.log",
                payload={"collected": True},
            )
        )
        return HookResult.ok(data={"phase": "SENSORS"})


class MockCognitionPlugin(KernelPlugin):
    """Mock plugin that runs in COGNITION phase."""

    def __init__(self, plugin_id: str = "mock_cognition"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.COGNITION

    def on_pulse(self, kernel, transaction) -> HookResult:
        return HookResult.ok(data={"phase": "COGNITION"})


class MockActuatorPlugin(KernelPlugin):
    """Mock plugin that runs in ACTUATORS phase (default)."""

    def __init__(self, plugin_id: str = "mock_actuator"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    # Uses default pulse_phase = ACTUATORS

    def on_pulse(self, kernel, transaction) -> HookResult:
        return HookResult.ok(data={"phase": "ACTUATORS"})


class MockCrashingPlugin(KernelPlugin):
    """Mock plugin that crashes on pulse."""

    def __init__(self, plugin_id: str = "mock_crasher"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    def on_pulse(self, kernel, transaction) -> HookResult:
        raise RuntimeError("BOOM! This plugin crashed intentionally.")


class MockErrorPlugin(KernelPlugin):
    """Mock plugin that returns an error result."""

    def __init__(self, plugin_id: str = "mock_error"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    def on_pulse(self, kernel, transaction) -> HookResult:
        return HookResult.error("Something went wrong but not fatal")


class MockFatalPlugin(KernelPlugin):
    """Mock plugin that returns a fatal error."""

    def __init__(self, plugin_id: str = "mock_fatal"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    def on_pulse(self, kernel, transaction) -> HookResult:
        return HookResult.fatal("Critical failure - quarantine me")


# =============================================================================
# StateMutation Tests
# =============================================================================


class TestStateMutation:
    """Tests for StateMutation dataclass and validation."""

    def test_valid_mutation(self):
        """Valid mutation should pass validation."""
        mutation = StateMutation(
            plugin_id="test_plugin",
            action="update_doc",
            target="OPUS.md",
            payload={"content": "test"},
        )
        assert mutation.validate() is True

    def test_empty_plugin_id_fails(self):
        """Empty plugin_id should fail validation."""
        mutation = StateMutation(
            plugin_id="",
            action="update_doc",
            target="OPUS.md",
            payload={"content": "test"},
        )
        assert mutation.validate() is False

    def test_empty_action_fails(self):
        """Empty action should fail validation."""
        mutation = StateMutation(
            plugin_id="test_plugin",
            action="",
            target="OPUS.md",
            payload={"content": "test"},
        )
        assert mutation.validate() is False

    def test_invalid_action_fails(self):
        """Unknown action should fail validation."""
        mutation = StateMutation(
            plugin_id="test_plugin",
            action="invalid_action_not_in_allowed",
            target="OPUS.md",
            payload={"content": "test"},
        )
        assert mutation.validate() is False

    def test_empty_target_fails(self):
        """Empty target should fail validation."""
        mutation = StateMutation(
            plugin_id="test_plugin",
            action="update_doc",
            target="",
            payload={"content": "test"},
        )
        assert mutation.validate() is False

    def test_all_allowed_actions(self):
        """All defined allowed actions should pass validation."""
        for action in ALLOWED_ACTIONS:
            mutation = StateMutation(
                plugin_id="test_plugin",
                action=action,
                target="some_target",
                payload={},
            )
            assert mutation.validate() is True, f"Action '{action}' should be valid"


# =============================================================================
# PulseTransaction Tests
# =============================================================================


class TestPulseTransaction:
    """Tests for PulseTransaction with fail-forward strategy."""

    def test_register_valid_mutation(self):
        """Valid mutation should be registered successfully."""
        tx = PulseTransaction()
        mutation = StateMutation(
            plugin_id="test_plugin",
            action="update_doc",
            target="OPUS.md",
            payload={"content": "test"},
        )

        result = tx.register(mutation)

        assert result is True
        assert len(tx.mutations) == 1
        assert len(tx.validation_errors) == 0

    def test_register_invalid_mutation(self):
        """Invalid mutation should not be registered."""
        tx = PulseTransaction()
        mutation = StateMutation(
            plugin_id="",  # Invalid
            action="update_doc",
            target="OPUS.md",
            payload={"content": "test"},
        )

        result = tx.register(mutation)

        assert result is False
        assert len(tx.mutations) == 0
        assert len(tx.validation_errors) == 1

    def test_abort_clears_mutations(self):
        """Abort should clear all registered mutations."""
        tx = PulseTransaction()
        tx.register(
            StateMutation(
                plugin_id="test_plugin",
                action="update_doc",
                target="OPUS.md",
                payload={"content": "test"},
            )
        )

        tx.abort("Test abort")

        assert len(tx.mutations) == 0
        assert "ABORT: Test abort" in tx.validation_errors

    def test_commit_with_validation_errors_fails(self):
        """Commit should fail if validation errors exist."""
        tx = PulseTransaction()
        # Register invalid mutation (causes validation error)
        tx.register(
            StateMutation(
                plugin_id="",  # Invalid
                action="update_doc",
                target="OPUS.md",
                payload={},
            )
        )

        success, failure = tx.commit()

        assert success == 0
        assert failure == 0  # No mutations were registered due to validation fail

    def test_commit_without_handlers_succeeds(self):
        """Commit without handlers should succeed (mutations recorded but not applied)."""
        tx = PulseTransaction()
        tx.register(
            StateMutation(
                plugin_id="test_plugin",
                action="update_doc",
                target="OPUS.md",
                payload={"content": "test"},
            )
        )

        success, failure = tx.commit()

        # Without handlers, mutations are recorded but not "applied"
        # The commit considers them successful since no handler threw an error
        assert success == 1
        assert failure == 0
        assert tx.committed is True

    def test_commit_only_once(self):
        """Commit should only work once."""
        tx = PulseTransaction()
        tx.register(
            StateMutation(
                plugin_id="test_plugin",
                action="update_doc",
                target="OPUS.md",
                payload={},
            )
        )

        first_success, _ = tx.commit()
        second_success, second_failure = tx.commit()

        assert first_success == 1
        assert second_success == 0
        assert second_failure == 0  # Skipped, not failed

    def test_mutations_sorted_by_priority(self):
        """Mutations should be executed in priority order."""
        tx = PulseTransaction()
        executed_order = []

        def record_handler(mutation):
            executed_order.append(mutation.target)
            return True

        tx.register_handler("log_observation", record_handler)

        # Register in non-priority order
        tx.register(StateMutation("p1", "log_observation", "third", {}, priority=3))
        tx.register(StateMutation("p1", "log_observation", "first", {}, priority=1))
        tx.register(StateMutation("p1", "log_observation", "second", {}, priority=2))

        tx.commit()

        assert executed_order == ["first", "second", "third"]


# =============================================================================
# PranaOrchestrator Tests
# =============================================================================


class TestPranaOrchestrator:
    """Tests for PranaOrchestrator with isolation wrappers."""

    def test_isolation_failure_one_crash_doesnt_kill_others(self):
        """One plugin crash should not prevent other plugins from executing."""

        class MockKernel:
            _plugins = [
                MockSensorPlugin("sensor_1"),
                MockCrashingPlugin("crasher"),
                MockActuatorPlugin("actuator_1"),
            ]

        orchestrator = PranaOrchestrator(kernel=MockKernel())
        result = orchestrator.run_pulse_cycle()

        # 2 plugins succeeded, 1 crashed
        assert result["plugins_executed"] == 2
        assert result["plugins_failed"] == 1

    def test_phase_ordering_sensors_before_cognition_before_actuators(self):
        """Plugins should execute in phase order: SENSORS → COGNITION → ACTUATORS."""
        execution_order = []

        class TrackedSensor(MockSensorPlugin):
            def on_pulse(self, kernel, transaction):
                execution_order.append("SENSORS")
                return super().on_pulse(kernel, transaction)

        class TrackedCognition(MockCognitionPlugin):
            def on_pulse(self, kernel, transaction):
                execution_order.append("COGNITION")
                return super().on_pulse(kernel, transaction)

        class TrackedActuator(MockActuatorPlugin):
            def on_pulse(self, kernel, transaction):
                execution_order.append("ACTUATORS")
                return super().on_pulse(kernel, transaction)

        class MockKernel:
            _plugins = [
                TrackedActuator("act"),  # Added first but should execute last
                TrackedCognition("cog"),
                TrackedSensor("sen"),  # Added last but should execute first
            ]

        orchestrator = PranaOrchestrator(kernel=MockKernel())
        orchestrator.run_pulse_cycle()

        assert execution_order == ["SENSORS", "COGNITION", "ACTUATORS"]

    def test_rate_limiting_enforces_minimum_interval(self):
        """resolve_frequency should enforce minimum interval."""
        config = PranaOrchestratorConfig(min_pulse_interval_seconds=60)
        orchestrator = PranaOrchestrator(config=config)

        # Request faster than minimum
        result = orchestrator.resolve_frequency([10, 20, 30])

        assert result == 60  # Enforced minimum

    def test_rate_limiting_uses_conservative_vote(self):
        """resolve_frequency should use the fastest vote (but not below minimum)."""
        config = PranaOrchestratorConfig(min_pulse_interval_seconds=60)
        orchestrator = PranaOrchestrator(config=config)

        # All votes above minimum
        result = orchestrator.resolve_frequency([120, 180, 300])

        assert result == 120  # Fastest requested

    def test_rate_limiting_returns_default_on_empty_votes(self):
        """resolve_frequency should return default on empty votes."""
        config = PranaOrchestratorConfig(
            min_pulse_interval_seconds=60,
            default_interval_seconds=900,
        )
        orchestrator = PranaOrchestrator(config=config)

        result = orchestrator.resolve_frequency([])

        assert result == 900  # Default

    def test_plugin_quarantine_after_threshold(self):
        """Plugin should be quarantined after exceeding failure threshold."""
        config = PranaOrchestratorConfig(quarantine_threshold=2)

        class MockKernel:
            _plugins = [MockCrashingPlugin("crasher")]

        orchestrator = PranaOrchestrator(kernel=MockKernel(), config=config)

        # First pulse: 1 failure
        orchestrator.run_pulse_cycle()
        assert "crasher" not in orchestrator.quarantined_plugins

        # Second pulse: 2 failures, threshold reached
        orchestrator.run_pulse_cycle()
        assert "crasher" in orchestrator.quarantined_plugins

    def test_quarantined_plugin_excluded_from_next_pulse(self):
        """Quarantined plugins should not execute in subsequent pulses."""
        config = PranaOrchestratorConfig(quarantine_threshold=1)

        class MockKernel:
            _plugins = [
                MockSensorPlugin("sensor_1"),
                MockCrashingPlugin("crasher"),
            ]

        orchestrator = PranaOrchestrator(kernel=MockKernel(), config=config)

        # First pulse: crasher fails and gets quarantined
        result1 = orchestrator.run_pulse_cycle()
        assert result1["plugins_failed"] == 1
        assert "crasher" in orchestrator.quarantined_plugins

        # Second pulse: only sensor_1 should execute
        result2 = orchestrator.run_pulse_cycle()
        assert result2["plugins_executed"] == 1
        assert result2["plugins_failed"] == 0

    def test_unquarantine_plugin(self):
        """Unquarantined plugin should execute again."""
        config = PranaOrchestratorConfig(quarantine_threshold=1)

        class MockKernel:
            _plugins = [MockCrashingPlugin("crasher")]

        orchestrator = PranaOrchestrator(kernel=MockKernel(), config=config)

        # Quarantine via failure
        orchestrator.run_pulse_cycle()
        assert "crasher" in orchestrator.quarantined_plugins

        # Unquarantine
        result = orchestrator.unquarantine_plugin("crasher")
        assert result is True
        assert "crasher" not in orchestrator.quarantined_plugins

    def test_error_result_increments_failure_count(self):
        """ERROR result should increment failure count."""
        config = PranaOrchestratorConfig(quarantine_threshold=2)

        class MockKernel:
            _plugins = [MockErrorPlugin("error_plugin")]

        orchestrator = PranaOrchestrator(kernel=MockKernel(), config=config)

        # First error
        orchestrator.run_pulse_cycle()
        assert orchestrator._failure_counts.get("error_plugin") == 1
        assert "error_plugin" not in orchestrator.quarantined_plugins

        # Second error - quarantine
        orchestrator.run_pulse_cycle()
        assert "error_plugin" in orchestrator.quarantined_plugins

    def test_fatal_result_immediately_quarantines(self):
        """FATAL result should immediately quarantine the plugin."""
        config = PranaOrchestratorConfig(quarantine_threshold=10)  # High threshold

        class MockKernel:
            _plugins = [MockFatalPlugin("fatal_plugin")]

        orchestrator = PranaOrchestrator(kernel=MockKernel(), config=config)

        orchestrator.run_pulse_cycle()

        # Immediately quarantined despite high threshold
        assert "fatal_plugin" in orchestrator.quarantined_plugins

    def test_success_resets_failure_count(self):
        """Successful pulse should reset failure count."""
        config = PranaOrchestratorConfig(quarantine_threshold=3)

        call_count = 0

        class FlakeyPlugin(KernelPlugin):
            @property
            def plugin_id(self):
                return "flakey"

            def on_pulse(self, kernel, transaction):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    return HookResult.error("Temporary failure")
                return HookResult.ok()

        class MockKernel:
            _plugins = [FlakeyPlugin()]

        orchestrator = PranaOrchestrator(kernel=MockKernel(), config=config)

        # Two failures
        orchestrator.run_pulse_cycle()
        orchestrator.run_pulse_cycle()
        assert orchestrator._failure_counts.get("flakey") == 2

        # Success - should reset
        orchestrator.run_pulse_cycle()
        assert orchestrator._failure_counts.get("flakey") == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestPranaIntegration:
    """End-to-end integration tests."""

    def test_full_pulse_cycle_with_multiple_plugins(self):
        """Full pulse cycle with multiple plugins in different phases."""

        class MockKernel:
            _plugins = [
                MockSensorPlugin("sensor_1"),
                MockSensorPlugin("sensor_2"),
                MockCognitionPlugin("cognition_1"),
                MockActuatorPlugin("actuator_1"),
            ]

        orchestrator = PranaOrchestrator(kernel=MockKernel())
        result = orchestrator.run_pulse_cycle()

        assert result["status"] == "completed"
        assert result["plugins_executed"] == 4
        assert result["plugins_failed"] == 0
        assert "SENSORS" in result["phase_results"]
        assert "COGNITION" in result["phase_results"]
        assert "ACTUATORS" in result["phase_results"]

    def test_mutations_collected_across_phases(self):
        """Mutations from all phases should be collected in transaction."""

        mutations_collected = []

        class MutatingPlugin(KernelPlugin):
            def __init__(self, pid, phase):
                self._pid = pid
                self._phase = phase

            @property
            def plugin_id(self):
                return self._pid

            @property
            def pulse_phase(self):
                return self._phase

            def on_pulse(self, kernel, transaction):
                mutation = StateMutation(
                    plugin_id=self.plugin_id,
                    action="log_observation",
                    target=f"journal/{self.plugin_id}.log",
                    payload={"phase": self._phase.name},
                )
                transaction.register(mutation)
                mutations_collected.append(self.plugin_id)
                return HookResult.ok()

        class MockKernel:
            _plugins = [
                MutatingPlugin("sensor", PulsePhase.SENSORS),
                MutatingPlugin("cognition", PulsePhase.COGNITION),
                MutatingPlugin("actuator", PulsePhase.ACTUATORS),
            ]

        orchestrator = PranaOrchestrator(kernel=MockKernel())
        result = orchestrator.run_pulse_cycle()

        assert result["mutations_committed"] == 3
        assert mutations_collected == ["sensor", "cognition", "actuator"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
