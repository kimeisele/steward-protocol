import time

import pytest
import requests

from vibe_core.kernel_impl import RealVibeKernel


@pytest.mark.integration
def test_sangha_api_gateway():
    """
    Phase 18 Verification: The Network (Sangha)
    Ensures the Async Sidecar (API Gateway) starts with the kernel and responds to HTTP.
    """
    # 1. Boot Kernel
    kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

    # Force a unique port for testing (though logic supports 8000)
    # Ideally config would handle this, but for now we test default

    try:
        kernel.boot()

        # 2. Wait for Gateway to Start (Sidecar Thread)
        print("\n⏳ Waiting for Gateway Sidecar to initialize...")
        time.sleep(2)  # Give thread time to spin up

        # 3. Request Health Check
        url = "http://127.0.0.1:8000/api/v1/health"
        print(f"📡 Requesting: {url}")

        try:
            response = requests.get(url, timeout=5)
            print(f"✅ Response: {response.status_code} {response.json()}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "alive"
            assert data["phase"] == "18 (Sangha)"

        except requests.exceptions.ConnectionError:
            pytest.fail("❌ Connection refused - Gateway sidecar did not start or port is blocked.")

        # 4. Request System State
        url_state = "http://127.0.0.1:8000/api/v1/state"
        print(f"📡 Requesting: {url_state}")

        try:
            response = requests.get(url_state, timeout=5)
            print(f"✅ State Response: {response.status_code}")
            assert response.status_code == 200
            state = response.json()
            # Ensure we get kernel status
            assert "kernel" in state
            assert "status" in state["kernel"]
            assert state["kernel"]["status"] == "RUNNING"

        except requests.exceptions.ConnectionError:
            pytest.fail("❌ Connection refused for state endpoint")

    finally:
        # 5. Shutdown
        print("🛑 Shutting down kernel...")
        kernel.shutdown()
        time.sleep(1)  # Wait for thread cleanup
