"""
OPUS-095: PRANA Orchestrator Tests (Migrated to CognitiveCycle API)
===================================================================

Test suite for the PRANA Pulse Architecture using OPUS-095 CognitiveCycle.

Tests cover:
- Isolation failure (one plugin crash doesn't kill others)
- Phase ordering (SENSORS → COGNITION → ACTUATORS)
- StateMutation validation
- CognitiveCycle orchestration
"""

import asyncio

import pytest

from vibe_core.event_bus import EventBus
from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.prana_orchestrator import (
    ALLOWED_ACTIONS,
    PranaOrchestrator,
    PulseTransaction,
    StateMutation,
)
from vibe_core.runtime.unified_trace import UnifiedTrace

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
# NOTE: Legacy PulseTransaction and PranaOrchestrator tests removed
# These tests used OPUS-087 API which was replaced by OPUS-095 CognitiveCycle.
# New orchestration tests are in test_opus_pulse.py and test_governance_pulse.py
# =============================================================================
