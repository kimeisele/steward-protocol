"""
Tests for Prahlad Hardening (Phase IV).
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.services.prahlad import PrahladService
from vibe_core.naga.testing import NagaTestHarness


class TestPrahladHardening:
    @pytest.fixture
    def prahlad(self):
        return PrahladService()

    @patch("subprocess.run")
    def test_verify_self_integrity_uses_subprocess(self, mock_run, prahlad):
        """Should use subprocess.run with timeout."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

        # Patch os.path.exists to return True for test_dir
        with patch("os.path.exists", return_value=True):
            result = prahlad.verify_self_integrity(quiet=True)

        assert result is True
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "pytest" in args[0]
        assert kwargs["timeout"] == 120

    @patch("subprocess.run")
    def test_verify_self_integrity_handles_timeout(self, mock_run, prahlad):
        """Should handle subprocess.TimeoutExpired gracefully (Fail-Closed)."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["pytest"], timeout=120)

        with patch("os.path.exists", return_value=True):
            with patch("sys.stderr.write") as mock_stderr:
                result = prahlad.verify_self_integrity()

        assert result is False
        mock_stderr.assert_called_with("!!! PRAHLAD CRITICAL: Integrity check TIMED OUT (120s). Chain compromised?\n")

    def test_record_integrity_event_reports_failure(self, prahlad):
        """Should report recording failures to sys.stderr instead of passing silently."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.naga import SeshaProtocol

        # Mock Sesha to fail
        mock_sesha = MagicMock()
        mock_sesha.record_event.side_effect = Exception("Sesha Down")

        with NagaTestHarness() as harness:
            # Register our broken mock
            ServiceRegistry.register(SeshaProtocol, mock_sesha)

            with patch("sys.stderr.write") as mock_stderr:
                prahlad._record_integrity_event(passed=True)

        # Should have logged to stderr
        assert any("!!! PRAHLAD: Failed to record integrity event" in str(call) for call in mock_stderr.call_args_list)

    def test_dharma_audit_reports_ledger_failure(self, prahlad):
        """Should report ledger failures to sys.stderr."""
        mock_ledger = MagicMock()
        mock_ledger.get_recent_decisions.side_effect = Exception("Ledger Error")
        prahlad.set_ledger(mock_ledger)

        with patch("sys.stderr.write") as mock_stderr:
            score = prahlad.dharma_audit()

        assert score.ledger_intact is False
        assert any("!!! PRAHLAD: Audit ledger check failed" in str(call) for call in mock_stderr.call_args_list)
