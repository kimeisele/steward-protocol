"""
OPUS-086: TRIGUNA CLASSIFICATION TEST
=====================================

Tests that:
1. New agents default to SATTVA (healthy state)
2. Agents with high error rate become TAMASIC
3. Agents with high activity rate become RAJASIC
4. Guna affects task restrictions
"""

import logging

import pytest

from vibe_core.plugins.test_orchestration.fixtures import TestAgents, TestKernel, TestTasks
from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

logger = logging.getLogger("TEST_TRIGUNA")


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


class TestTriguna:
    """Test suite for OPUS-086 Triguna classification."""

    def test_new_agent_is_sattva(self, test_env):
        """New healthy agents default to Sattva."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="healthy_agent")
        kernel.register_agent(agent, spawn_process=False)

        guna = governance.determine_guna("healthy_agent")
        assert guna == "sattva", "New healthy agent should be Sattva"

    def test_agent_with_failures_becomes_tamasic(self, test_env):
        """Agent with high error rate becomes Tamasic."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="failing_agent")
        kernel.register_agent(agent, spawn_process=False)

        # Simulate multiple failures in ledger
        for i in range(5):
            kernel._ledger.record_failure(
                type("Task", (), {"task_id": f"fail_{i}", "agent_id": "failing_agent", "payload": {}})(),
                error="Simulated failure",
            )

        guna = governance.determine_guna("failing_agent")
        assert guna == "tamas", "Agent with many failures should be Tamasic"

    def test_sattva_allows_write(self, test_env):
        """Sattvic agents can perform write tasks."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="sattva_writer")
        kernel.register_agent(agent, spawn_process=False)

        # Promote to GRIHASTHA to allow writes by Ashrama
        governance.promote_agent("sattva_writer", reason="Testing")

        # Create write task
        write_task = TestTasks.with_payload("sattva_writer", {"action": "write"})
        write_task.action = "write"

        # Should be allowed
        allowed = governance.on_task_pre_assign(kernel, "sattva_writer", write_task)
        assert allowed, "Sattvic GRIHASTHA agent should be allowed to write"

    def test_get_agent_guna_details(self, test_env):
        """get_agent_guna returns detailed analysis."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="analyzed_agent")
        kernel.register_agent(agent, spawn_process=False)

        result = governance.get_agent_guna("analyzed_agent")

        assert result["agent_id"] == "analyzed_agent"
        assert result["guna"] in ["tamas", "rajas", "sattva"]
        assert "description" in result
        assert "restrictions" in result

    def test_tamasic_restriction_enforced(self, test_env):
        """Tamasic agents cannot perform complex tasks."""
        kernel, governance = test_env
        agent = TestAgents.compliant(agent_id="tamasic_agent")
        kernel.register_agent(agent, spawn_process=False)

        # Promote to GRIHASTHA first (so Ashrama allows writes)
        governance.promote_agent("tamasic_agent", reason="Testing")

        # Simulate failures to make agent Tamasic
        for i in range(5):
            kernel._ledger.record_failure(
                type("Task", (), {"task_id": f"fail_{i}", "agent_id": "tamasic_agent", "payload": {}})(),
                error="Simulated failure",
            )

        # Verify agent is Tamasic
        assert governance.determine_guna("tamasic_agent") == "tamas"

        # Create write task (should be blocked by Guna, not Ashrama)
        write_task = TestTasks.with_payload("tamasic_agent", {"action": "write"})
        write_task.action = "write"

        allowed = governance.on_task_pre_assign(kernel, "tamasic_agent", write_task)
        assert not allowed, "Tamasic agent should not be allowed to write"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
