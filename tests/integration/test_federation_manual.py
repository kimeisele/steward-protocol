"""
Phase 19 Verification: Federation (Seed List)
Tests federation API handlers directly using aiohttp TestClient.
No real ports, no time.sleep - deterministic and fast.
"""

from unittest.mock import MagicMock

import pytest
from aiohttp.test_utils import TestClient, TestServer

from vibe_core.gateway.api import NetworkGateway


@pytest.fixture
def mock_prakriti():
    """Create a mock Prakriti with federation support."""
    prakriti = MagicMock()
    prakriti.get_system_status.return_value = {"kernel": {"status": "RUNNING"}}

    # Federation state (mutable for testing)
    peers = {}

    def list_peers():
        return list(peers.values())

    def add_peer(peer_id, url, trust_level=1):
        peers[peer_id] = {"peer_id": peer_id, "url": url, "trust_level": trust_level}
        return True

    def remove_peer(peer_id):
        if peer_id in peers:
            del peers[peer_id]
            return True
        return False

    def get_peer(peer_id):
        return peers.get(peer_id)

    def update_peer_last_seen(peer_id):
        if peer_id in peers:
            peers[peer_id]["last_seen"] = "now"

    prakriti.machine.list_peers = list_peers
    prakriti.machine.add_peer = add_peer
    prakriti.machine.remove_peer = remove_peer
    prakriti.machine.get_peer = get_peer
    prakriti.machine.update_peer_last_seen = update_peer_last_seen

    return prakriti


@pytest.fixture
def gateway(mock_prakriti):
    """Create a NetworkGateway instance for testing."""
    return NetworkGateway(mock_prakriti, host="127.0.0.1", port=0)


@pytest.mark.asyncio
async def test_list_peers_empty(gateway):
    """Test listing peers when none registered."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.get("/api/v1/federation/peers")
        assert resp.status == 200
        data = await resp.json()
        assert data["peers"] == []


@pytest.mark.asyncio
async def test_add_peer(gateway):
    """Test adding a peer to the federation."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.post(
            "/api/v1/federation/peers", json={"peer_id": "node-alpha", "url": "http://peer1.example.com:8000"}
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "registered"
        assert data["peer_id"] == "node-alpha"


@pytest.mark.asyncio
async def test_add_peer_missing_fields(gateway):
    """Test adding peer with missing required fields."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.post(
            "/api/v1/federation/peers",
            json={"peer_id": "incomplete"},  # Missing url
        )
        assert resp.status == 400
        data = await resp.json()
        assert "error" in data


@pytest.mark.asyncio
async def test_peer_lifecycle(gateway):
    """Test complete peer lifecycle: add, list, remove."""
    async with TestClient(TestServer(gateway.app)) as client:
        # 1. Add peer
        resp = await client.post("/api/v1/federation/peers", json={"peer_id": "test-node", "url": "http://test:9000"})
        assert resp.status == 200

        # 2. List peers - should have one
        resp = await client.get("/api/v1/federation/peers")
        assert resp.status == 200
        peers = (await resp.json())["peers"]
        assert len(peers) == 1
        assert peers[0]["peer_id"] == "test-node"
        assert peers[0]["url"] == "http://test:9000"

        # 3. Remove peer
        resp = await client.delete("/api/v1/federation/peers/test-node")
        assert resp.status == 200
        assert (await resp.json())["status"] == "removed"

        # 4. Verify removal
        resp = await client.get("/api/v1/federation/peers")
        assert resp.status == 200
        assert (await resp.json())["peers"] == []


@pytest.mark.asyncio
async def test_forward_to_unknown_peer(gateway):
    """Test forwarding to non-existent peer returns 404."""
    async with TestClient(TestServer(gateway.app)) as client:
        resp = await client.post(
            "/api/v1/federation/forward/nonexistent", json={"path": "/api/v1/health", "method": "GET"}
        )
        assert resp.status == 404
        data = await resp.json()
        assert "not found" in data["error"].lower()
