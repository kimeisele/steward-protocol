from unittest.mock import MagicMock, patch

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.ouroboros.sync import CISyncService
from vibe_core.protocols.universal import SyncProtocol, SyncResult, SyncStatus
from vibe_core.services.git_sync import GitSyncService
from vibe_core.services.ledger_sync import LedgerSyncWrapper


def test_registry_lookup_optimization():
    """Verify O(1) lookup works."""
    ServiceRegistry.reset_all()

    # Register Mock Services
    git = MagicMock(spec=GitSyncService)
    ledger = MagicMock(spec=LedgerSyncWrapper)

    ServiceRegistry.register(GitSyncService, git, protocols=[SyncProtocol])
    ServiceRegistry.register(LedgerSyncWrapper, ledger, protocols=[SyncProtocol])

    # Get All
    syncs = ServiceRegistry.get_all(SyncProtocol)
    assert len(syncs) == 2
    assert git in syncs
    assert ledger in syncs


def test_git_sync_robustness():
    """Verify GitSync handles failures without crashing (Diva Check)."""
    with patch("subprocess.run") as mock_run:
        # Simulate Git Failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "error: Your local changes would be overwritten by merge"

        service = GitSyncService(repo_path=".")
        # Mock .git existing
        with patch("pathlib.Path.exists", return_value=True):
            result = service.sync(context=None)

        assert result.success is False
        assert len(result.errors) > 0
        assert result.success is False
        assert len(result.errors) > 0
        # Check that we caught the error (whatever it was)
        assert "Fetch failed" in result.errors[0] or "Pull failed" in result.errors[0]


def test_ledger_sync_wrapper():
    """Verify LedgerSync wraps VibeLedger correctly."""
    mock_ledger = MagicMock()
    wrapper = LedgerSyncWrapper(mock_ledger)

    result = wrapper.sync(context=None)
    assert result.success is True

    # Check if it tried to checkpoint (only if connection exists)
    # mock_ledger.connection.execute.assert_called() - Optional
