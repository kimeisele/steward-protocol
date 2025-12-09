from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.cli.unified_cli import UnifiedCLI


@pytest.mark.integration
def test_telepathy_download_and_install():
    """
    Verify Phase 17 Telepathy:
    1. Resolve @steward/mock_telepathy alias.
    2. Download from mocked URL.
    3. Install to library/.
    """

    # Setup
    cli = UnifiedCLI()
    mock_content = b"FAKE_VIBE_CONTAINER_CONTENT"
    mock_url = "https://github.com/steward-protocol/registry/releases/download/v1.0/mock_telepathy.vibe"

    # Mock requests.get to return a mock response with content
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": str(len(mock_content))}
    mock_response.iter_content = MagicMock(return_value=[mock_content])
    mock_response.raise_for_status = MagicMock()

    # MOCK THE NETWORK
    with patch("requests.get", return_value=mock_response) as mock_get:
        # EXECUTE
        # usage: steward install @steward/mock_telepathy
        exit_code = cli.cmd_install(["@steward/mock_telepathy"])

        # VERIFY
        assert exit_code == 0

        # Check alias resolution happened (mock_get called with correct URL)
        mock_get.assert_called_once()
        args, _ = mock_get.call_args
        assert args[0] == mock_url

        # Check file installation
        target_path = Path("library/mock_telepathy.vibe")
        assert target_path.exists()
        assert target_path.read_bytes() == mock_content

        # Cleanup
        if target_path.exists():
            target_path.unlink()
