# =============================================================================
# Public API Tests (Hardened) — stub tests pending implementation
# =============================================================================

import pytest


@pytest.mark.skip(reason="Stub tests — sesha/mock_ledger fixtures not yet wired")
class TestPublicAPI:
    """Test YAMARAJA compliant public API (Fail-Closed)."""

    def test_get_recent_events_raises_on_failure(self, sesha, mock_ledger):
        """Should raise RuntimeError when read fails."""
        pass

    def test_get_events_by_type_raises_on_failure(self, sesha, mock_ledger):
        """Should raise RuntimeError when read fails."""
        pass
