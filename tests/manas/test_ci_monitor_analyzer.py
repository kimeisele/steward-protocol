"""
OPUS-041: VAK (The Voice) - CI Monitor Analyzer Tests.

These tests verify that the CIMonitorAnalyzer correctly uses
ShellCortex to check system status and generate intents.

"The system must observe itself to heal itself."
"""

from unittest.mock import patch

import pytest

from vibe_core.plugins.opus_assistant.manas.analyzers.ci_monitor_analyzer import (
    CIMonitorAnalyzer,
)
from vibe_core.plugins.opus_assistant.manas.cortex.shell import (
    CommandRisk,
    ShellCortex,
    ShellResult,
)
from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentPriority, IntentRisk

# =============================================================================
# SECTION 1: BASIC ANALYZER TESTS
# =============================================================================


class TestCIMonitorAnalyzerBasics:
    """Basic tests for CIMonitorAnalyzer."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer with temp workspace."""
        return CIMonitorAnalyzer(workspace=tmp_path)

    def test_analyzer_has_correct_name(self, analyzer):
        """Mutation killer: Name must be 'ci_monitor'."""
        assert analyzer.name == "ci_monitor"

    def test_analyzer_has_cortex(self, analyzer):
        """Mutation killer: Analyzer must have ShellCortex."""
        assert hasattr(analyzer, "_cortex")
        assert isinstance(analyzer._cortex, ShellCortex)

    def test_analyzer_is_enabled_by_default(self, analyzer):
        """Mutation killer: Analyzer should be enabled by default."""
        assert analyzer.is_enabled is True

    def test_analyze_returns_list(self, analyzer):
        """Mutation killer: analyze() must return a list."""
        result = analyzer.analyze({})
        assert isinstance(result, list)


# =============================================================================
# SECTION 2: STATUS CHECK TESTS
# =============================================================================


class TestStatusChecks:
    """Tests for system status checking."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer with temp workspace."""
        return CIMonitorAnalyzer(workspace=tmp_path)

    def test_status_check_success_no_intent(self, analyzer):
        """
        Mutation killer: Successful status should not generate intent.
        """
        # Mock successful status result
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=0,
                stdout="System is healthy",
                stderr="",
                blocked=False,
            )

            intents = analyzer.analyze({})

            # Should not generate any intent for healthy status
            status_intents = [i for i in intents if "status" in i.intent_type]
            # May still have capability check, but no status failure
            assert not any(i.intent_type == "ci_status_failure" for i in intents)

    def test_status_check_failure_generates_intent(self, analyzer):
        """
        Mutation killer: Failed status check MUST generate intent.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=1,
                stdout="",
                stderr="Connection refused",
                blocked=False,
            )

            intents = analyzer.analyze({})

            # Should generate a status failure intent
            status_intents = [i for i in intents if i.intent_type == "ci_status_failure"]
            assert len(status_intents) == 1

            intent = status_intents[0]
            assert intent.priority == IntentPriority.HIGH
            assert intent.risk == IntentRisk.SAFE  # Observation, not action
            assert intent.auto_executable is False  # Human should investigate

    def test_status_error_keywords_generate_intent(self, analyzer):
        """
        Mutation killer: Error keywords in output MUST generate intent.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=0,  # Success exit code
                stdout="Kernel status: ERROR - agent failed to respond",
                stderr="",
                blocked=False,
            )

            intents = analyzer.analyze({})

            # Should detect error in output
            error_intents = [i for i in intents if "error_detected" in i.intent_type]
            assert len(error_intents) == 1

    def test_blocked_status_command_handled(self, analyzer):
        """
        Mutation killer: Blocked status command should be handled gracefully.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=1,
                stdout="",
                stderr="",
                blocked=True,  # Command was blocked!
                error="Command blocked",
            )

            # Should not crash
            intents = analyzer.analyze({})
            # Should not generate intent for blocked command (internal error)
            assert not any(i.intent_type == "ci_status_failure" for i in intents)


# =============================================================================
# SECTION 3: CAPABILITIES CHECK TESTS
# =============================================================================


class TestCapabilitiesChecks:
    """Tests for capabilities checking."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer with temp workspace."""
        return CIMonitorAnalyzer(workspace=tmp_path)

    def test_capabilities_success_no_intent(self, analyzer):
        """
        Mutation killer: Valid capabilities should not generate intent.
        """
        import json

        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            # Return healthy status first, then valid capabilities
            mock_exec.side_effect = [
                ShellResult(
                    command=["status"],
                    exit_code=0,
                    stdout="OK",
                    stderr="",
                    blocked=False,
                ),
                ShellResult(
                    command=["capabilities"],
                    exit_code=0,
                    stdout=json.dumps({"system_commands": ["status", "stop"], "version": "2.0"}),
                    stderr="",
                    blocked=False,
                ),
            ]

            intents = analyzer.analyze({})

            # Should not generate capability intents
            cap_intents = [i for i in intents if "capabilities" in i.intent_type]
            assert len(cap_intents) == 0

    def test_capabilities_failure_generates_intent(self, analyzer):
        """
        Mutation killer: Failed capabilities MUST generate intent.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.side_effect = [
                ShellResult(command=["status"], exit_code=0, stdout="OK", stderr="", blocked=False),
                ShellResult(
                    command=["capabilities"],
                    exit_code=1,
                    stdout="",
                    stderr="Module not found",
                    blocked=False,
                ),
            ]

            intents = analyzer.analyze({})

            cap_intents = [i for i in intents if i.intent_type == "ci_capabilities_failure"]
            assert len(cap_intents) == 1
            assert cap_intents[0].priority == IntentPriority.HIGH

    def test_capabilities_invalid_json_generates_intent(self, analyzer):
        """
        Mutation killer: Invalid JSON in capabilities MUST generate intent.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.side_effect = [
                ShellResult(command=["status"], exit_code=0, stdout="OK", stderr="", blocked=False),
                ShellResult(
                    command=["capabilities"],
                    exit_code=0,
                    stdout="not valid json {{{",  # Invalid JSON!
                    stderr="",
                    blocked=False,
                ),
            ]

            intents = analyzer.analyze({})

            json_intents = [i for i in intents if "invalid_json" in i.intent_type]
            assert len(json_intents) == 1

    def test_capabilities_missing_system_commands_generates_intent(self, analyzer):
        """
        Mutation killer: Missing system_commands MUST generate intent.
        """
        import json

        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.side_effect = [
                ShellResult(command=["status"], exit_code=0, stdout="OK", stderr="", blocked=False),
                ShellResult(
                    command=["capabilities"],
                    exit_code=0,
                    stdout=json.dumps({"version": "2.0"}),  # Missing system_commands!
                    stderr="",
                    blocked=False,
                ),
            ]

            intents = analyzer.analyze({})

            incomplete_intents = [i for i in intents if "incomplete" in i.intent_type]
            assert len(incomplete_intents) == 1


# =============================================================================
# SECTION 4: INTEGRATION TESTS
# =============================================================================


class TestCIMonitorIntegration:
    """Integration tests for CI Monitor Analyzer."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer with temp workspace."""
        return CIMonitorAnalyzer(workspace=tmp_path)

    def test_respects_max_intents_limit(self, analyzer):
        """
        Mutation killer: Analyzer should respect max_intents_per_run.
        """
        # Set a low limit
        analyzer._config.max_intents_per_run = 1

        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            # Both fail - would generate 2 intents
            mock_exec.side_effect = [
                ShellResult(command=["status"], exit_code=1, stdout="", stderr="Error", blocked=False),
                ShellResult(command=["capabilities"], exit_code=1, stdout="", stderr="Error", blocked=False),
            ]

            intents = analyzer.analyze({})

            # Should be limited to 1
            assert len(intents) <= 1

    def test_get_last_status_returns_result(self, analyzer):
        """
        Mutation killer: get_last_status should return the last result.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=0,
                stdout="Healthy",
                stderr="",
                blocked=False,
            )

            analyzer.analyze({})

            last_status = analyzer.get_last_status()
            assert last_status is not None
            assert last_status.stdout == "Healthy"

    def test_get_last_check_time_returns_datetime(self, analyzer):
        """
        Mutation killer: get_last_check_time should return datetime.
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=0,
                stdout="OK",
                stderr="",
                blocked=False,
            )

            analyzer.analyze({})

            last_time = analyzer.get_last_check_time()
            assert last_time is not None

    def test_uses_safe_commands_only(self, analyzer):
        """
        SECURITY TEST: Analyzer should only use SAFE commands.
        """
        # Verify status is SAFE
        assert analyzer._cortex.classify_risk(["status"]) == CommandRisk.SAFE
        # Verify capabilities is SAFE
        assert analyzer._cortex.classify_risk(["capabilities"]) == CommandRisk.SAFE

    def test_intents_have_safe_risk(self, analyzer):
        """
        Mutation killer: Generated intents should be SAFE risk (observation only).
        """
        with patch.object(analyzer._cortex, "execute_safe") as mock_exec:
            mock_exec.return_value = ShellResult(
                command=["status"],
                exit_code=1,
                stdout="",
                stderr="Error",
                blocked=False,
            )

            intents = analyzer.analyze({})

            for intent in intents:
                assert intent.risk == IntentRisk.SAFE  # We're just observing
