"""
Tests for Sesha Hardening (Fail-Closed Read).
"""

from unittest.mock import MagicMock

import pytest

from vibe_core.naga.services.sesha import SeshaService


class TestSeshaHardening:
    @pytest.fixture
    def mock_ledger(self):
        m = MagicMock()
        # Setup successful boot check
        m.get_top_hash.return_value = "0" * 64
        return m

    @pytest.fixture
    def sesha(self, mock_ledger):
        return SeshaService(ledger=mock_ledger)

    def test_get_recent_events_raises_on_failure(self, sesha, mock_ledger):
        """get_recent_events should raise RuntimeError if ledger fails."""
        mock_ledger.get_events.side_effect = Exception("DB Fire")

        with pytest.raises(RuntimeError, match="Sesha read failure"):
            sesha.get_recent_events()

    def test_get_events_by_type_raises_on_failure(self, sesha, mock_ledger):
        """get_events_by_type should raise RuntimeError if ledger fails."""
        mock_ledger.get_events.side_effect = Exception("DB Explosion")

        with pytest.raises(RuntimeError, match="Sesha read failure"):
            sesha.get_events_by_type("TEST")

    def test_boot_integrity_check_passes(self, mock_ledger):
        """Should verify integrity at boot."""
        mock_ledger.get_top_hash.return_value = "hash123"
        sesha = SeshaService(ledger=mock_ledger)
        assert sesha.get_top_hash() == "hash123"

    def test_boot_integrity_check_fails_closed(self, mock_ledger):
        """Should crash at boot if integrity check fails."""
        mock_ledger.get_top_hash.side_effect = Exception("Corrupt")

        with pytest.raises(RuntimeError, match="Sesha boot failed"):
            SeshaService(ledger=mock_ledger)
