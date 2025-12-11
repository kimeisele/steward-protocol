"""
Phase 18 Verification: The Network (Sangha)
Tests the Gateway API handlers directly using aiohttp TestClient.
No real ports, no time.sleep - deterministic and fast.
"""

from unittest.mock import MagicMock

import pytest
from aiohttp.test_utils import TestClient, TestServer

from vibe_core.gateway.api import NetworkGateway


@pytest.fixture
def mock_prakriti():
    """Create a mock Prakriti (state engine) for testing."""
    prakriti = MagicMock()
    prakriti.get_system_status.return_value = {
        "kernel": {"status": "RUNNING", "agents_registered": 0},
        "ledger": {"total_events": 0},
    }
    prakriti.machine.list_peers.return_value = []
    prakriti.machine.add_peer.return_value = True
    prakriti.machine.remove_peer.return_value = True
    prakriti.machine.get_peer.return_value = None
    return prakriti


@pytest.fixture
def gateway(mock_prakriti):
    """Create a NetworkGateway instance for testing."""
    return NetworkGateway(mock_prakriti, host="127.0.0.1", port=0)


@pytest.mark.asyncio
async def test_health_endpoint(gateway):
    """Test /api/v1/health returns correct response."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.get("/api/v1/health")
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "alive"
        assert data["phase"] == "18 (Sangha)"
        assert data["system"] == "VibeOS"


@pytest.mark.asyncio
async def test_state_endpoint(gateway, mock_prakriti):
    """Test /api/v1/state returns kernel status."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.get("/api/v1/state")
        assert resp.status == 200
        data = await resp.json()
        assert "kernel" in data
        assert data["kernel"]["status"] == "RUNNING"
        # Verify prakriti was called
        mock_prakriti.get_system_status.assert_called_once()


@pytest.mark.asyncio
async def test_index_without_static(gateway):
    """Test / returns fallback when no static files."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.get("/")
        # Either 200 with fallback text or FileResponse
        assert resp.status == 200
        text = await resp.text()
        assert "VibeOS" in text or "index" in text.lower()
