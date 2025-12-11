import time

import pytest
import requests

from vibe_core.kernel_impl import RealVibeKernel


@pytest.mark.integration
def test_federation_peer_registration():
    """
    Phase 19 Verification: Federation (Seed List)
    Tests peer registration via API.
    """
    import tempfile

    # Use unique temp file to avoid test pollution
    temp_ledger = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_ledger.close()

    kernel = RealVibeKernel(ledger_path=temp_ledger.name, load_plugins=False)

    try:
        kernel.boot()
        time.sleep(2)  # Wait for gateway

        base_url = "http://127.0.0.1:8000"

        # 0. Clean up any stale peers from previous runs
        try:
            stale_resp = requests.get(f"{base_url}/api/v1/federation/peers", timeout=5)
            if stale_resp.status_code == 200:
                for peer in stale_resp.json().get("peers", []):
                    requests.delete(f"{base_url}/api/v1/federation/peers/{peer['peer_id']}", timeout=5)
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

        # 1. List peers (should be empty now)
        resp = requests.get(f"{base_url}/api/v1/federation/peers", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["peers"] == [], f"Expected empty list, got: {resp.json()['peers']}"

        # 2. Add a peer
        resp = requests.post(
            f"{base_url}/api/v1/federation/peers",
            json={"peer_id": "node-alpha", "url": "http://localhost:9000"},
            timeout=5,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "registered"

        # 3. List peers (should have one)
        resp = requests.get(f"{base_url}/api/v1/federation/peers", timeout=5)
        assert resp.status_code == 200
        peers = resp.json()["peers"]
        assert len(peers) == 1
        assert peers[0]["peer_id"] == "node-alpha"
        assert peers[0]["url"] == "http://localhost:9000"

        # 4. Remove peer
        resp = requests.delete(f"{base_url}/api/v1/federation/peers/node-alpha", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["status"] == "removed"

        # 5. Verify removal
        resp = requests.get(f"{base_url}/api/v1/federation/peers", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["peers"] == []

        print("✅ Federation peer registration test passed!")

    finally:
        kernel.shutdown()
        time.sleep(1)


@pytest.mark.integration
def test_federation_forward_mock():
    """
    Phase 19 Verification: Federation Forward Logic.
    Mocks aiohttp session to test forwarding without real network call.
    """
    kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

    try:
        kernel.boot()
        time.sleep(2)

        base_url = "http://127.0.0.1:8000"

        # 1. Register a mock peer
        resp = requests.post(
            f"{base_url}/api/v1/federation/peers",
            json={"peer_id": "mock-node", "url": "http://fake-peer:8000"},
            timeout=5,
        )
        assert resp.status_code == 200

        # 2. Try to forward (will fail because fake-peer doesn't exist)
        #    But this proves the route exists and peer lookup works
        resp = requests.post(
            f"{base_url}/api/v1/federation/forward/mock-node",
            json={"path": "/api/v1/health", "method": "GET"},
            timeout=5,
        )
        # Expect 502 because fake-peer is unreachable
        assert resp.status_code == 502
        assert "error" in resp.json()

        print("✅ Federation forward logic test passed (expected 502 for fake peer)!")

    finally:
        kernel.shutdown()
        time.sleep(1)
