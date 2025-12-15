"""
PRATYAYA ANALYZER TESTS - Self-Falsification Integration.

OPUS-077: Verifies the Reflex loop works correctly.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestPratyayaAnalyzer:
    """Test the PratyayaAnalyzer reflex loop."""

    def test_analyzer_exists_and_has_required_properties(self):
        """Verify analyzer has required BaseAnalyzer interface."""
        from vibe_core.plugins.opus_assistant.manas.analyzers import PratyayaAnalyzer

        analyzer = PratyayaAnalyzer()

        assert analyzer.name == "pratyaya"
        assert analyzer.is_enabled is True
        assert hasattr(analyzer, "analyze")

    def test_analyzer_skips_without_trigger(self):
        """Analyzer should not run without pratyaya_trigger in context."""
        from vibe_core.plugins.opus_assistant.manas.analyzers import PratyayaAnalyzer

        analyzer = PratyayaAnalyzer()

        # No trigger flag
        result = analyzer.analyze({})
        assert result == []

        # Explicit False
        result = analyzer.analyze({"pratyaya_trigger": False})
        assert result == []

    def test_analyzer_runs_with_trigger(self):
        """Analyzer runs Red Team when triggered."""
        from vibe_core.plugins.opus_assistant.manas.analyzers import PratyayaAnalyzer

        analyzer = PratyayaAnalyzer()

        # Mock run_red_team at the import location inside analyze()
        mock_result = {
            "vulnerabilities": 0,
            "secure": 7,
            "results": {},
        }

        with patch(
            "tests.hardening.test_red_team_attacks.run_red_team",
            return_value=mock_result,
        ):
            result = analyzer.analyze({"pratyaya_trigger": True})

        # Should return empty list when all attacks blocked
        assert isinstance(result, list)
        assert len(result) == 0  # No vulnerabilities = no intents

    def test_analyzer_generates_intent_on_vulnerability(self):
        """Analyzer creates CRITICAL intent when vulnerability detected."""
        from vibe_core.plugins.opus_assistant.manas.analyzers import PratyayaAnalyzer

        analyzer = PratyayaAnalyzer()

        # Create mock AttackResult
        mock_attack_result = MagicMock()
        mock_attack_result.exploited = True
        mock_attack_result.message = "IDENTITY SPOOFING POSSIBLE"
        mock_attack_result.details = {"recommendation": "Ledger must verify agent_id"}

        mock_result = {
            "vulnerabilities": 1,
            "secure": 6,
            "results": {"MESSAGE_SPOOFING": mock_attack_result},
        }

        with patch(
            "tests.hardening.test_red_team_attacks.run_red_team",
            return_value=mock_result,
        ):
            result = analyzer.analyze({"pratyaya_trigger": True})

        # Should generate one CRITICAL intent
        assert len(result) == 1
        intent = result[0]
        assert "pratyaya_message_spoofing" in intent.id
        assert intent.intent_type == "SECURITY_PATCH_NEEDED"
        assert intent.priority.value == "critical"
        assert "IDENTITY SPOOFING" in intent.description

    def test_analyzer_registered_in_intent_generator(self):
        """Verify PratyayaAnalyzer is wired into IntentGenerator."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentGenerator

        generator = IntentGenerator()

        analyzer_names = [a.name for a in generator._modular_analyzers]
        assert "pratyaya" in analyzer_names


@pytest.mark.hardening
class TestPratyayaIntegration:
    """Integration tests with actual Red Team (uses isolated TestKernel)."""

    def test_full_dream_session(self):
        """
        Run a full dream session with REAL Red Team attacks.

        This is the INTEGRATION TEST - if this fails, the system is broken.
        Uses TestKernel.minimal() which is ISOLATED - safe to run.
        """
        from vibe_core.plugins.opus_assistant.manas.analyzers import PratyayaAnalyzer

        analyzer = PratyayaAnalyzer()
        result = analyzer.analyze({"pratyaya_trigger": True})

        # This test documents the CURRENT security state
        # If vulnerabilities exist, this test will show them (RED is honest!)
        # If all attacks blocked, it passes (GREEN means actually secure)

        if len(result) > 0:
            vuln_names = [i.title for i in result]
            pytest.fail(
                f"VULNERABILITIES DETECTED (this is honest, not a test failure):\n"
                f"{vuln_names}\n"
                f"Fix these or acknowledge them in the harness."
            )
