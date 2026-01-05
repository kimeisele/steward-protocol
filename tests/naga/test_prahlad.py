"""
Tests for PRAHLAD Service - The Resilience & Hardening Agent.

Mythology: Prahlad Maharaj was tortured by his demon father Hiranyakashipu
with fire, snakes, poison, elephants - but survived everything because
he was anchored in absolute truth (Narayana).

Purpose: Make the system ANTIFRAGILE. Every failure makes it stronger.
- Error → Regression Test (learn from suffering)
- Chaos Probing (actively seek weakness)
- Dharma Audit (verify integrity)

"What doesn't kill me makes me stronger" - but vedic:
"Because I am anchored in truth, nothing can kill me."
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest


class TestPrahladBasics:
    """Test basic Prahlad initialization and status."""

    def test_initialization(self):
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        assert prahlad._tests_generated == 0
        assert prahlad._chaos_probes == 0
        assert prahlad._dharma_audits == 0
        assert len(prahlad._hardening_suite) == 0

    def test_get_status(self):
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()
        status = prahlad.get_status()

        assert status.naga_type.value == "prahlad"
        assert status.healthy is True
        assert status.events_processed == 0


class TestErrorToTest:
    """Test error observation and test generation."""

    def test_on_error_generates_test(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        error = ErrorEvent(
            error_type="ValueError",
            message="Invalid input: negative number",
            component_id="math_service",
            context={"input": -5, "function": "sqrt"},
        )

        test_case = prahlad.on_error(error)

        assert test_case is not None
        assert test_case.target_component == "math_service"
        assert test_case.error_type == "ValueError"
        assert prahlad._tests_generated == 1

    def test_generated_test_is_reproducible(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        error = ErrorEvent(
            error_type="KeyError",
            message="'missing_key'",
            component_id="config_service",
            context={"attempted_key": "missing_key", "available_keys": ["a", "b"]},
        )

        test_case = prahlad.on_error(error)

        # Test case should contain enough info to reproduce
        assert test_case.reproduction_context is not None
        assert "missing_key" in str(test_case.reproduction_context)

    def test_on_error_adds_to_hardening_suite(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        error = ErrorEvent(
            error_type="RuntimeError",
            message="Connection lost",
            component_id="network_service",
            context={},
        )

        prahlad.on_error(error)

        assert len(prahlad._hardening_suite) == 1
        assert prahlad._hardening_suite[0].target_component == "network_service"

    def test_duplicate_errors_not_duplicated(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        error = ErrorEvent(
            error_type="ValueError",
            message="same error",
            component_id="same_component",
            context={"same": "context"},
        )

        prahlad.on_error(error)
        prahlad.on_error(error)  # Same error again

        # Should deduplicate
        assert len(prahlad._hardening_suite) == 1
        assert prahlad._tests_generated == 1  # Only counted once


class TestChaosProbing:
    """Test chaos engineering / active resilience testing."""

    def test_chaos_probe_returns_result(self):
        from vibe_core.naga.services.prahlad import PrahladService, ProbeResult

        prahlad = PrahladService()

        result = prahlad.chaos_probe("test_component")

        assert isinstance(result, ProbeResult)
        assert result.target == "test_component"
        assert prahlad._chaos_probes == 1

    def test_chaos_probe_with_scenarios(self):
        from vibe_core.naga.services.prahlad import ChaosScenario, PrahladService

        prahlad = PrahladService()

        scenarios = [
            ChaosScenario.NULL_INPUT,
            ChaosScenario.TIMEOUT,
            ChaosScenario.MALFORMED_DATA,
        ]

        result = prahlad.chaos_probe("target_service", scenarios=scenarios)

        assert result.scenarios_tested == 3

    def test_chaos_probe_reports_failures(self):
        from vibe_core.naga.services.prahlad import ChaosScenario, PrahladService

        prahlad = PrahladService()

        # Mock a component that fails on NULL_INPUT
        mock_component = MagicMock()
        mock_component.handle.side_effect = ValueError("null not allowed")

        prahlad.register_component("fragile", mock_component)

        result = prahlad.chaos_probe("fragile", scenarios=[ChaosScenario.NULL_INPUT])

        assert result.failures > 0
        assert "null_input" in [f.scenario for f in result.failure_details]

    def test_chaos_probe_generates_tests_for_failures(self):
        from vibe_core.naga.services.prahlad import ChaosScenario, PrahladService

        prahlad = PrahladService()

        # Simulate a probe that finds weakness
        mock_component = MagicMock()
        mock_component.handle.side_effect = Exception("crash")

        prahlad.register_component("weak", mock_component)
        prahlad.chaos_probe("weak")

        # Prahlad should auto-generate a test for this weakness
        assert len(prahlad._hardening_suite) >= 1


class TestDharmaAudit:
    """Test Dharma compliance auditing."""

    def test_dharma_audit_returns_score(self):
        from vibe_core.naga.services.prahlad import DharmaScore, PrahladService

        prahlad = PrahladService()

        score = prahlad.dharma_audit()

        assert isinstance(score, DharmaScore)
        assert 0 <= score.total_score <= 100
        assert prahlad._dharma_audits == 1

    def test_dharma_audit_checks_signatures(self):
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        # Mock a ledger with signed and unsigned decisions
        mock_ledger = MagicMock()
        mock_ledger.get_recent_decisions.return_value = [
            {"id": "1", "signature": b"valid"},
            {"id": "2", "signature": None},  # Unsigned! Adharma!
            {"id": "3", "signature": b"valid"},
        ]

        prahlad.set_ledger(mock_ledger)
        score = prahlad.dharma_audit()

        assert score.unsigned_decisions == 1
        assert score.signature_compliance < 100

    def test_dharma_audit_checks_ledger_integrity(self):
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        mock_ledger = MagicMock()
        mock_ledger.verify_chain.return_value = False  # Corrupted!
        mock_ledger.get_recent_decisions.return_value = []

        prahlad.set_ledger(mock_ledger)
        score = prahlad.dharma_audit()

        assert score.ledger_intact is False
        assert score.total_score < 70  # Ledger corruption is 40% of score

    def test_dharma_audit_checks_identity_coverage(self):
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        # Some agents have identity, some don't
        prahlad.register_agent("agent_1", has_identity=True)
        prahlad.register_agent("agent_2", has_identity=False)  # No identity!
        prahlad.register_agent("agent_3", has_identity=True)

        score = prahlad.dharma_audit()

        assert score.agents_without_identity == 1
        assert score.identity_coverage < 100


class TestHardeningSuite:
    """Test the generated test suite management."""

    def test_export_hardening_suite(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        # Generate some tests
        prahlad.on_error(ErrorEvent("Error1", "msg1", "comp1", {}))
        prahlad.on_error(ErrorEvent("Error2", "msg2", "comp2", {}))

        suite = prahlad.export_hardening_suite()

        assert len(suite) == 2
        assert all(tc.test_code is not None for tc in suite)

    def test_export_as_pytest(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        prahlad.on_error(
            ErrorEvent(
                error_type="ValueError",
                message="negative not allowed",
                component_id="math_service",
                context={"input": -1},
            )
        )

        pytest_code = prahlad.export_as_pytest()

        assert "def test_" in pytest_code
        assert "math_service" in pytest_code
        assert "negative not allowed" in pytest_code  # Message preserved

    def test_clear_hardening_suite(self):
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        prahlad.on_error(ErrorEvent("E", "m", "c", {}))
        assert len(prahlad._hardening_suite) == 1

        prahlad.clear_hardening_suite()

        assert len(prahlad._hardening_suite) == 0


class TestPhoenixGuarantee:
    """Test crash-restart-resume verification."""

    def test_verify_phoenix_guarantee(self):
        from vibe_core.naga.services.prahlad import PhoenixResult, PrahladService

        prahlad = PrahladService()

        # Mock a component with state
        mock_component = MagicMock()
        mock_component.get_state.return_value = {"counter": 5}
        mock_component.shutdown.return_value = None
        mock_component.restart.return_value = None

        prahlad.register_component("stateful", mock_component)

        result = prahlad.verify_phoenix_guarantee("stateful")

        assert isinstance(result, PhoenixResult)
        assert result.target == "stateful"

    def test_phoenix_detects_state_loss(self):
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        mock_component = MagicMock()
        mock_component.get_state.side_effect = [
            {"counter": 5},  # Before crash
            {"counter": 0},  # After restart - STATE LOST!
        ]

        prahlad.register_component("leaky", mock_component)

        result = prahlad.verify_phoenix_guarantee("leaky")

        assert result.state_preserved is False
        assert result.passed is False


class TestCortexIntegration:
    """Test integration with NagaCortex."""

    def test_report_to_cortex_on_weakness_found(self):
        from vibe_core.naga.services.prahlad import ChaosScenario, PrahladService

        mock_cortex = MagicMock()
        prahlad = PrahladService(cortex=mock_cortex)

        # Simulate finding a weakness
        mock_component = MagicMock()
        mock_component.handle.side_effect = Exception("weakness")
        prahlad.register_component("weak", mock_component)

        prahlad.chaos_probe("weak")

        mock_cortex.receive_prahlad_finding.assert_called()

    def test_report_dharma_violations(self):
        from vibe_core.naga.services.prahlad import PrahladService

        mock_cortex = MagicMock()
        prahlad = PrahladService(cortex=mock_cortex)

        # Create Dharma violation
        mock_ledger = MagicMock()
        mock_ledger.get_recent_decisions.return_value = [
            {"id": "1", "signature": None},  # Violation!
        ]
        prahlad.set_ledger(mock_ledger)

        prahlad.dharma_audit()

        mock_cortex.receive_prahlad_finding.assert_called()


class TestSignedFindings:
    """Test that findings are signed (37th Principle)."""

    def test_test_case_is_signed(self):
        from vibe_core.naga.identity import NagaIdentity
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        identity = NagaIdentity.generate(agent_id="prahlad_test")
        prahlad = PrahladService(identity=identity)

        test_case = prahlad.on_error(ErrorEvent("E", "m", "c", {}))

        assert test_case.generator_id == "prahlad_test"
        assert test_case.signature is not None

    def test_dharma_score_is_signed(self):
        from vibe_core.naga.identity import NagaIdentity
        from vibe_core.naga.services.prahlad import PrahladService

        identity = NagaIdentity.generate(agent_id="prahlad_auditor")
        prahlad = PrahladService(identity=identity)

        score = prahlad.dharma_audit()

        assert score.auditor_id == "prahlad_auditor"
        assert score.signature is not None


class TestAntifragility:
    """Test the core antifragility loop."""

    def test_antifragile_loop(self):
        """
        The core Prahlad loop:
        Error → Test → System Stronger
        """
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        initial_tests = len(prahlad._hardening_suite)

        # System experiences error
        error = ErrorEvent(
            error_type="OutOfMemoryError",
            message="heap exhausted",
            component_id="heavy_processor",
            context={"memory_mb": 1024, "threshold_mb": 512},
        )

        # Prahlad learns from it
        prahlad.on_error(error)

        # System is now stronger (has a test)
        assert len(prahlad._hardening_suite) > initial_tests

        # The test captures the conditions
        test = prahlad._hardening_suite[-1]
        assert "memory" in str(test.reproduction_context).lower()


class TestCoverageIntelligence:
    """Test NAGA's eyes - Coverage Intelligence via TestableRegistry."""

    def test_get_coverage_intelligence_returns_structure(self):
        """Coverage intelligence returns expected structure."""
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()
        intel = prahlad.get_coverage_intelligence()

        # Should have prahlad_stats at minimum
        assert "prahlad_stats" in intel
        assert "tests_generated" in intel["prahlad_stats"]
        assert "chaos_probes" in intel["prahlad_stats"]

    def test_get_coverage_intelligence_includes_self_stats(self):
        """Coverage intelligence includes Prahlad's own stats."""
        from vibe_core.naga.services.prahlad import ErrorEvent, PrahladService

        prahlad = PrahladService()

        # Generate some activity
        prahlad.on_error(ErrorEvent("E", "m", "c", {}))
        prahlad.dharma_audit()

        intel = prahlad.get_coverage_intelligence()

        assert intel["prahlad_stats"]["tests_generated"] >= 1
        assert intel["prahlad_stats"]["dharma_audits"] >= 1

    def test_list_available_remedies(self):
        """Can list available Shuddhi remedies."""
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        # May be empty if Shuddhi not registered, but shouldn't fail
        remedies = prahlad.list_available_remedies()
        assert isinstance(remedies, list)

    def test_request_shuddhi_heal_graceful_without_service(self):
        """Shuddhi heal request fails gracefully if service unavailable."""
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        result = prahlad.request_shuddhi_heal(
            file_path="/nonexistent/file.py",
            rule_id="test_rule",
        )

        # Should return error, not raise
        assert "error" in result or "status" in result


class TestAgencyIntegration:
    """Test NAGA as agency - using existing APIs."""

    def test_prahlad_uses_existing_infrastructure(self):
        """
        Prahlad uses TestableRegistry and Shuddhi, not rebuilding.
        'Jeder Dienst stellt auch Dienst zur Verfügung.'
        """
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        # Has coverage intelligence (uses TestableRegistry)
        assert hasattr(prahlad, "get_coverage_intelligence")

        # Has Shuddhi integration (uses Shuddhi API)
        assert hasattr(prahlad, "request_shuddhi_heal")
        assert hasattr(prahlad, "list_available_remedies")


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
