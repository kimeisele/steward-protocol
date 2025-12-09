"""
GAJENDRA MOKSHA TEST SUITE (Refactored for OPUS Unified Architecture)
=====================================================================

Tests for the Emergency Interrupt Protocol (Canto 8 - Gajendra Protocol)
using the modern `UnifiedRouter` instead of legacy `MilkOceanRouter`.

Technical Test Scenarios:
1. Security Block (The Watchman)
2. CRITICAL Request Identification (The Lotus Flower)
3. Normal Flow (Default)
"""

import logging

import pytest

from vibe_core.runtime.unified_execution import ExecutionRequest, MilkOceanGate, UnifiedRouter

logger = logging.getLogger("GAJENDRA_TEST")


class TestGajendraProtocolUnified:
    """Test suite for Gajendra Moksha using UnifiedRouter"""

    @pytest.fixture
    def router(self):
        return UnifiedRouter()

    def test_security_block(self, router):
        """Test that Watchman still blocks malicious input."""
        req = ExecutionRequest(user_input="DROP TABLE users; --", source="hacker")
        decision = router.check_gate(req)

        assert decision == MilkOceanGate.BLOCK
        assert req.gate_decision == MilkOceanGate.BLOCK
        logger.info("✅ Security intact: Watchman blocked SQL injection")

    def test_critical_recognition(self, router):
        """Test that CRITICAL requests are identified."""
        req = ExecutionRequest(user_input="CRITICAL: System Failure!", source="admin")
        decision = router.check_gate(req)

        assert decision == MilkOceanGate.CRITICAL
        assert req.gate_decision == MilkOceanGate.CRITICAL
        logger.info("✅ Gajendra Protocol: CRITICAL request identified")

    def test_normal_flow(self, router):
        """Test normal request flow."""
        req = ExecutionRequest(user_input="Schedule report", source="user")
        decision = router.check_gate(req)

        assert decision == MilkOceanGate.ALLOW
        logger.info("✅ Normal flow: Request allowed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
