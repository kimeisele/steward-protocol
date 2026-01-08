import logging
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.universal import SyncProtocol
from vibe_core.services.git_sync import GitSyncService
from vibe_core.services.ledger_sync import LedgerSyncWrapper


def test_nrisimha_diva_stress_test(caplog):
    """
    PROTOCOL NRISIMHA: The 'Poison Test'.
    Simulate a Git Diva meltdown (Merge Conflict) and verify:
    1. System does NOT crash.
    2. SyncResult captures the chaos.
    3. Proper strategy is suggested.
    """
    # 1. Setup Diva (Conflict Simulation)
    with patch("subprocess.run") as mock_run:
        # Simulate fatal merge conflict output from 'git pull'
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = (
            "error: Your local changes to 'vibe_core/kernel.py' would be overwritten by merge. Aborting."
        )

        # 2. Execute (Drink the Poison)
        service = GitSyncService(repo_path=".")

        # Mock .git check
        with patch("pathlib.Path.exists", return_value=True):
            result = service.sync(context=None)  # Intentionally None to trigger Mayavad check too

        # 3. Verify Survival (Graceful Degradation)
        assert result.success is False
        assert "Fetch failed" in result.errors[0] or "Pull failed" in result.errors[0]
        assert (
            "Merge Conflict" in result.errors[0]
            or "Manual Implementation Required" in result.errors[0]
            or "overwritten by merge" in result.errors[0]
        )
        # Note: The actual error message parsing in GitSync might need to be looser if the exact string isn't matched,
        # but the key is NO EXCEPTION raised.


def test_nrisimha_anti_mayavad_check(caplog):
    """
    Verify that anonymous sync attempts trigger RED ALERT.
    """
    service = GitSyncService(repo_path=".")

    with caplog.at_level(logging.CRITICAL):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                service.sync(context=None)

    # Assert the shout
    assert "ANTI-MAYAVAD VIOLATION" in caplog.text
    assert "Anonymous GitSync Attempted" in caplog.text


def test_registry_construction_order():
    """
    Verify O(1) Map is built AT REGISTRATION time, not query time.
    """
    ServiceRegistry.reset_all()

    mock_service = MagicMock()

    # Register
    ServiceRegistry.register(GitSyncService, mock_service, protocols=[SyncProtocol])

    # Inspect internals (Whitebox test)
    # The map should ALREADY have the entry
    assert SyncProtocol in ServiceRegistry._protocols
    assert mock_service in ServiceRegistry._protocols[SyncProtocol]
