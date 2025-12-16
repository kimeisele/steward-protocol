"""
OPUS-085: BHAKTI GRACE INTEGRATION TEST
========================================

Tests that:
1. Agent with high Bhakti is SPARED from demotion (grace granted)
2. Grace COSTS Bhakti (not free)
3. Agent with low Bhakti is DEMOTED (no grace)
4. Bhakti accumulates from devotional practices
"""

import logging

import pytest

from vibe_core.plugins.test_orchestration.fixtures import TestAgents, TestKernel
from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

logger = logging.getLogger("TEST_BHAKTI")


@pytest.fixture
def test_env():
    """Setup isolated test environment with Vedic Governance."""
    kernel = TestKernel.minimal()
    governance = VedicGovernancePlugin()
    governance.on_boot(kernel)
    kernel._plugins.append(governance)

    from vibe_core.protocols import KernelStatus

    kernel._status = KernelStatus.RUNNING

    return kernel, governance


class TestBhaktiGrace:
    """Test suite for OPUS-085 Bhakti Grace enforcement."""

    def test_get_bhakti_balance_default_zero(self, test_env):
        """New agents start with 0 Bhakti."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="new_agent")
        kernel.register_agent(agent, spawn_process=False)

        balance = governance.get_bhakti_balance("new_agent")
        assert balance == 0, "New agents should have 0 Bhakti"

    def test_add_bhakti(self, test_env):
        """Bhakti can be added to an agent."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="devoted_agent")
        kernel.register_agent(agent, spawn_process=False)

        # Add Bhakti (simulating surrender practice)
        success = governance.add_bhakti("devoted_agent", 10, reason="Surrender")
        assert success
        assert governance.get_bhakti_balance("devoted_agent") == 10

        # Add more (simulating TDD dharma)
        governance.add_bhakti("devoted_agent", 5, reason="TDD Dharma")
        assert governance.get_bhakti_balance("devoted_agent") == 15

    def test_consume_bhakti(self, test_env):
        """Bhakti can be consumed (cost of grace)."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="spending_agent")
        kernel.register_agent(agent, spawn_process=False)

        governance.add_bhakti("spending_agent", 50, reason="Past service")
        assert governance.get_bhakti_balance("spending_agent") == 50

        # Consume Bhakti
        success = governance.consume_bhakti("spending_agent", 30, reason="Grace cost")
        assert success
        assert governance.get_bhakti_balance("spending_agent") == 20

    def test_consume_bhakti_fails_if_insufficient(self, test_env):
        """Cannot consume more Bhakti than available."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="poor_agent")
        kernel.register_agent(agent, spawn_process=False)

        governance.add_bhakti("poor_agent", 10, reason="Little service")

        # Try to consume more than available
        success = governance.consume_bhakti("poor_agent", 50, reason="Too expensive")
        assert not success
        assert governance.get_bhakti_balance("poor_agent") == 10  # Unchanged

    def test_grace_granted_with_sufficient_bhakti(self, test_env):
        """Agent with enough Bhakti gets grace (and pays the cost)."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="loyal_agent")
        kernel.register_agent(agent, spawn_process=False)

        # Build up Bhakti (60 needed for demotion-level grace)
        governance.add_bhakti("loyal_agent", 70, reason="Long service")
        assert governance.get_bhakti_balance("loyal_agent") == 70

        # Check grace for demotion offense (severity 2)
        result = governance.should_grant_grace("loyal_agent", offense_severity=2)

        assert result["granted"] is True
        assert result["cost"] == 50  # Demotion grace costs 50
        assert result["bhakti_balance"] == 20  # 70 - 50

        # Verify Bhakti was consumed
        assert governance.get_bhakti_balance("loyal_agent") == 20

    def test_grace_denied_with_insufficient_bhakti(self, test_env):
        """Agent without enough Bhakti gets NO grace."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="disloyal_agent")
        kernel.register_agent(agent, spawn_process=False)

        # Low Bhakti
        governance.add_bhakti("disloyal_agent", 30, reason="Minimal service")

        # Check grace for demotion offense (needs 60, has 30)
        result = governance.should_grant_grace("disloyal_agent", offense_severity=2)

        assert result["granted"] is False
        assert result["required"] == 60
        assert "Insufficient" in result["reason"]

        # Bhakti NOT consumed (grace not granted)
        assert governance.get_bhakti_balance("disloyal_agent") == 30

    def test_bhakti_decay(self, test_env):
        """Bhakti decays over time (entropy)."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="decaying_agent")
        kernel.register_agent(agent, spawn_process=False)

        governance.add_bhakti("decaying_agent", 100, reason="Past glory")
        assert governance.get_bhakti_balance("decaying_agent") == 100

        # Apply 10% decay
        governance.decay_bhakti(decay_percent=10.0)
        assert governance.get_bhakti_balance("decaying_agent") == 90

    def test_bhakti_capped_at_200(self, test_env):
        """Bhakti cannot exceed 200 (hero mode limit)."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="hero_agent")
        kernel.register_agent(agent, spawn_process=False)

        governance.add_bhakti("hero_agent", 150, reason="Major service")
        governance.add_bhakti("hero_agent", 100, reason="More service")  # Would be 250

        assert governance.get_bhakti_balance("hero_agent") == 200  # Capped


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
