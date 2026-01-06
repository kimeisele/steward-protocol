"""
Tests for Ananta Hardening (Fail-Closed Loading).
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.services.ananta import AnantaService


class TestAnantaHardening:
    @pytest.fixture
    def mock_ledger(self):
        return MagicMock()

    @pytest.fixture
    def ananta(self, mock_ledger):
        return AnantaService(ledger=mock_ledger)

    def test_record_load_fails_closed(self, ananta, mock_ledger):
        """record_load should crash if ledger recording fails."""
        mock_ledger.record_event.side_effect = Exception("Ledger Full")

        with pytest.raises(RuntimeError, match="Ananta load audit failed"):
            ananta.record_load(loader_type="test", operation="load", item_type="plugin")

    def test_record_load_logs_fatal_error(self, ananta, mock_ledger):
        """record_load should log to stderr on failure."""
        mock_ledger.record_event.side_effect = Exception("Ledger Full")

        with patch("sys.stderr.write") as mock_stderr:
            try:
                ananta.record_load("test", "load", "plugin")
            except RuntimeError:
                pass

        assert any("!!! ANANTA FATAL" in str(call) for call in mock_stderr.call_args_list)
