"""
INTEGRATION TEST - The Balarama Proof
=====================================

"Proof of Strength"

This test verifies that the Mahamantra Router correctly:
1. Loads legacy services.
2. Wraps them in MahamantraProxy (Balarama).
3. Makes them Pancha Tattva compliant.

This proves the "One Import" promise:
    from vibe_core.mahamantra import mahamantra
    service = mahamantra.mod.some_legacy_service
    assert service.__tattva__  # Magic!
"""

import pytest

from vibe_core.mahamantra import mahamantra
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol
from vibe_core.mahamantra.substrate.proxy import MahamantraProxy

# We use a known legacy module for testing (e.g. from protocols.mahajanas)
# OR we can mock one if we want pure isolation.
# But "Integration" means testing with real components.


@pytest.mark.skip(reason="LEGACY: mahamantra.mod API removed. New API: mahamantra.genesis.brahma")
def test_router_access_core_service():
    """Test accessing a core service via mahamantra router."""
    # LEGACY TEST: mahamantra.mod.* API no longer exists
    # NEW API: mahamantra.genesis.brahma, mahamantra.shadow, etc.
    pass


@pytest.mark.skip(reason="LEGACY: mahamantra.mod API removed. Proxy wrapping architecture changed")
def test_router_wraps_legacy_module():
    """
    Test that a legacy module (if any exist) gets wrapped.
    LEGACY TEST: No longer applicable with new Lotus architecture.
    """
    pass


@pytest.mark.skip(reason="LEGACY: Rewrite needed for Lotus API (mahamantra.genesis.*, etc.)")
def test_one_import_promise():
    """Test the sacred promise: one import gives access to everything."""
    # LEGACY TEST: Needs rewrite for new Lotus-based navigation
    # NEW: mahamantra.genesis.brahma, mahamantra.shadow.spawn(), etc.
    pass


def test_proxy_transparency():
    """Test that the proxy forwards calls correctly."""

    class LegacyTool:
        def run(self):
            return "legacy run"

    # Wrap it manually to test the proxy mechanism
    proxy = MahamantraProxy(LegacyTool(), position=0, guardian="test")

    # It should have tattva
    assert proxy.__tattva__["srivasa"] == "Guarded by test"

    # It should behave like the tool
    assert proxy.run() == "legacy run"


if __name__ == "__main__":
    pytest.main([__file__])
