"""
OPUS-087 PRANA: Test opus_assistant.on_pulse implementation.

These tests MUST FAIL until Phase 5 is implemented.
TDD: Red before Green.
"""

import pytest

from vibe_core.plugin_protocol import HookResult, PluginResult, PulsePhase
from vibe_core.prana_orchestrator import PulseTransaction, StateMutation


class TestOpusAssistantPulsePhase:
    """opus_assistant must declare SENSORS phase."""

    def test_pulse_phase_is_sensors(self):
        """opus_assistant should run in SENSORS phase (first)."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        assert plugin.pulse_phase == PulsePhase.SENSORS, (
            "opus_assistant must declare SENSORS phase to collect data first"
        )


class TestOpusAssistantOnPulse:
    """opus_assistant.on_pulse must be implemented."""

    @pytest.fixture
    def plugin(self):
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        return OpusAssistantPlugin()

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

    def test_on_pulse_registers_update_doc_mutation(self, plugin, transaction):
        """on_pulse must register an update_doc mutation for OPUS.md."""
        plugin.on_pulse(kernel=None, transaction=transaction)

        # Must have at least one mutation
        assert len(transaction.mutations) >= 1, "opus_assistant.on_pulse must register at least one mutation"

        # Find the OPUS.md update
        opus_mutations = [m for m in transaction.mutations if m.action == "update_doc" and "OPUS" in m.target]
        assert len(opus_mutations) >= 1, "opus_assistant.on_pulse must register update_doc mutation for OPUS.md"

    def test_on_pulse_works_headless(self, plugin, transaction):
        """on_pulse must work when kernel is None (GitHub Actions headless)."""
        # This is the critical test - must not crash with kernel=None
        result = plugin.on_pulse(kernel=None, transaction=transaction)
        assert result.status != PluginResult.FATAL, "on_pulse must not FATAL when kernel is None (headless mode)"

    def test_on_pulse_mutation_has_content(self, plugin, transaction):
        """The registered mutation must have actual content."""
        plugin.on_pulse(kernel=None, transaction=transaction)

        opus_mutations = [m for m in transaction.mutations if m.action == "update_doc" and "OPUS" in m.target]

        if opus_mutations:
            mutation = opus_mutations[0]
            assert "content" in mutation.payload, "Mutation must have content in payload"
            assert len(mutation.payload["content"]) > 0, "Content must not be empty"


class TestOpusAssistantOnPulseErrorHandling:
    """on_pulse must handle errors gracefully."""

    def test_on_pulse_returns_error_not_raises(self):
        """on_pulse should return HookResult.error(), not raise exceptions."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        transaction = PulseTransaction()

        # Even with bad state, should not raise
        try:
            result = plugin.on_pulse(kernel=None, transaction=transaction)
            # If it raised, we wouldn't get here
            assert isinstance(result, HookResult)
        except Exception as e:
            pytest.fail(f"on_pulse raised {type(e).__name__}: {e} - should return HookResult.error() instead")
