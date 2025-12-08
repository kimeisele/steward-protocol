#!/usr/bin/env python3
"""
VERIFICATION SCRIPT: Router Cleanup (OPUS-005 Phase 2)
======================================================

Verifies that legacy routers are deprecated and replaced by UnifiedRouter.

Checks:
1. UnifiedRouter implements list_available_routes (GAD-000)
2. RealVibeKernel uses UnifiedRouter
3. BootSequence uses UnifiedRouter
4. Legacy PlaybookRouter raises DeprecationWarning
5. Legacy AgentRouter raises DeprecationWarning
"""

import sys
import unittest
import warnings
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.runtime.boot_sequence import BootSequence
from vibe_core.runtime.unified_execution import UnifiedRouter


class TestRouterCleanup(unittest.TestCase):
    def test_unified_router_capabilities(self):
        """Verify UnifiedRouter has list_available_routes"""
        print("Checking UnifiedRouter capabilities...")
        router = UnifiedRouter()
        assert hasattr(router, "list_available_routes")
        routes = router.list_available_routes()
        print(f"✅ UnifiedRouter.list_available_routes() returned {len(routes)} routes")

        # Verify specific routes if any (fast commands should serve 1.0 confidence)
        status_route = router.route("status")
        assert status_route.target_id == "SYSTEM_STATUS_V2"
        print("✅ UnifiedRouter correctly routes 'status' to SYSTEM_STATUS_V2")

    def test_kernel_uses_unified_router(self):
        """Verify RealVibeKernel uses UnifiedRouter"""
        print("\nChecking RealVibeKernel integration...")
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        assert hasattr(kernel, "_unified_router")
        assert isinstance(kernel._unified_router, UnifiedRouter)
        assert kernel._playbook_router == kernel._unified_router
        print("✅ RealVibeKernel uses UnifiedRouter (and aliases _playbook_router)")

    def test_boot_sequence_uses_unified_router(self):
        """Verify BootSequence uses UnifiedRouter"""
        print("\nChecking BootSequence integration...")
        boot = BootSequence()
        assert isinstance(boot.playbook_engine, UnifiedRouter)
        print("✅ BootSequence uses UnifiedRouter")

    def test_legacy_playbook_router_deprecation(self):
        """Verify PlaybookRouter raises DeprecationWarning"""
        print("\nChecking PlaybookRouter deprecation...")
        from vibe_core.runtime.playbook_router import PlaybookRouter

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            PlaybookRouter()
            assert len(w) > 0
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "UnifiedRouter" in str(w[-1].message)
            print("✅ PlaybookRouter raises DeprecationWarning")

    def test_legacy_agent_router_deprecation(self):
        """Verify AgentRouter raises DeprecationWarning"""
        print("\nChecking AgentRouter deprecation...")
        from vibe_core.playbook.router import AgentRouter

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            AgentRouter()
            assert len(w) > 0
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "UnifiedRouter" in str(w[-1].message)
            print("✅ AgentRouter raises DeprecationWarning")


if __name__ == "__main__":
    unittest.main()
