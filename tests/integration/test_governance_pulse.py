"""
OPUS-087 PRANA: Test vedic_governance.on_pulse implementation.

These tests MUST FAIL until Phase 6 is implemented.
TDD: Red before Green.
"""

import pytest

from vibe_core.plugin_protocol import HookResult, PluginResult, PulsePhase
from vibe_core.prana_orchestrator import PulseTransaction, StateMutation


class TestVedicGovernancePulsePhase:
    """vedic_governance must declare ACTUATORS phase."""

    def test_pulse_phase_is_actuators(self):
        """vedic_governance should run in ACTUATORS phase (after data collection)."""
        from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

        plugin = VedicGovernancePlugin()
        assert plugin.pulse_phase == PulsePhase.ACTUATORS, (
            "vedic_governance must declare ACTUATORS phase to act on collected data"
        )


class TestVedicGovernanceOnPulse:
    """vedic_governance.on_pulse must be implemented."""

    @pytest.fixture
    def plugin(self):
        from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

        return VedicGovernancePlugin()

    @pytest.fixture
    def transaction(self):
        return PulseTransaction()

    def test_on_pulse_returns_hook_result(self, plugin, transaction):
        """on_pulse must return HookResult, not raise."""
        result = plugin.on_pulse(kernel=None, transaction=transaction)
        assert isinstance(result, HookResult), "on_pulse must return HookResult"

    def test_on_pulse_returns_ok_on_success(self, plugin, transaction):
        """on_pulse should return OK status on success."""
        result = plugin.on_pulse(kernel=None, transaction=transaction)
        assert result.status == PluginResult.OK, f"Expected OK, got {result.status}: {result.error_message}"

    def test_on_pulse_can_register_decay_karma(self, plugin, transaction):
        """on_pulse should be able to register decay_karma mutations."""
        result = plugin.on_pulse(kernel=None, transaction=transaction)

        # Check that decay_karma mutations are valid if registered
        decay_mutations = [m for m in transaction.mutations if m.action == "decay_karma"]

        for mutation in decay_mutations:
            assert "agent_id" in mutation.payload, "decay_karma must have agent_id"
            assert "delta" in mutation.payload, "decay_karma must have delta"

    def test_on_pulse_works_headless(self, plugin, transaction):
        """on_pulse must work when kernel is None (GitHub Actions headless)."""
        result = plugin.on_pulse(kernel=None, transaction=transaction)
        assert result.status != PluginResult.FATAL, "on_pulse must not FATAL when kernel is None (headless mode)"

    def test_on_pulse_returns_data(self, plugin, transaction):
        """on_pulse should return data about what was processed."""
        result = plugin.on_pulse(kernel=None, transaction=transaction)

        # Should have some data about processing
        assert result.data is not None or result.status == PluginResult.OK, (
            "on_pulse should return data or at least OK status"
        )


class TestVedicGovernanceOnPulseErrorHandling:
    """on_pulse must handle errors gracefully."""

    def test_on_pulse_returns_error_not_raises(self):
        """on_pulse should return HookResult.error(), not raise exceptions."""
        from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

        plugin = VedicGovernancePlugin()
        transaction = PulseTransaction()

        try:
            result = plugin.on_pulse(kernel=None, transaction=transaction)
            assert isinstance(result, HookResult)
        except Exception as e:
            pytest.fail(f"on_pulse raised {type(e).__name__}: {e} - should return HookResult.error() instead")


class TestVedicGovernanceKarmaDecay:
    """Karma decay logic tests."""

    def test_decay_calculation_exists(self):
        """vedic_governance must have karma decay calculation method."""
        from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

        plugin = VedicGovernancePlugin()

        # Must have a method for calculating decay
        assert hasattr(plugin, "_calculate_pulse_decay") or hasattr(plugin, "calculate_karma_decay"), (
            "vedic_governance must have karma decay calculation method"
        )
