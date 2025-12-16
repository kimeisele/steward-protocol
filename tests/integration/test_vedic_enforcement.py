"""
OPUS-084: VEDIC ENFORCEMENT INTEGRATION TEST
=============================================

Tests that:
1. Agents start as BRAHMACHARI (Student)
2. BRAHMACHARI agents are VETOED from 'write' tasks
3. Promoted agents (GRIHASTHA) are ALLOWED 'write' tasks
4. Demoted agents lose rights again

Note: Kernel "hard fail" was reverted by VISNU protection.
This test verifies the VETO mechanism (on_task_pre_assign returns False).
"""

import logging

import pytest

from vibe_core.plugins.test_orchestration.fixtures import TestAgents, TestKernel, TestTasks
from vibe_core.plugins.vedic_governance.ashrama import Ashrama
from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

logger = logging.getLogger("TEST_VEDIC")


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


def test_new_agent_starts_as_brahmachari(test_env):
    """New agents start as BRAHMACHARI (Student)."""
    kernel, governance = test_env
    agent = TestAgents.compliant(agent_id="new_student")
    kernel.register_agent(agent, spawn_process=False)

    ashrama = governance.get_agent_ashrama("new_student")
    assert ashrama.current_ashrama == Ashrama.BRAHMACHARI


def test_brahmachari_vetoed_from_write(test_env):
    """BRAHMACHARI agents are VETOED from write tasks."""
    kernel, governance = test_env
    agent = TestAgents.compliant(agent_id="test_student")
    kernel.register_agent(agent, spawn_process=False)

    # Verify initial state
    ashrama = governance.get_agent_ashrama("test_student")
    assert ashrama.current_ashrama == Ashrama.BRAHMACHARI

    # Try to perform a WRITE task
    write_task = TestTasks.with_payload("test_student", {"action": "write"})
    write_task.action = "write"

    # Check veto directly (this is what matters)
    allowed = governance.on_task_pre_assign(kernel, "test_student", write_task)
    assert not allowed, "BRAHMACHARI agent should be VETOED from write tasks"


def test_brahmachari_allowed_read(test_env):
    """BRAHMACHARI agents CAN perform read tasks."""
    kernel, governance = test_env
    agent = TestAgents.compliant(agent_id="reader")
    kernel.register_agent(agent, spawn_process=False)

    read_task = TestTasks.with_payload("reader", {"action": "read"})
    read_task.action = "read"

    allowed = governance.on_task_pre_assign(kernel, "reader", read_task)
    assert allowed, "BRAHMACHARI agent should be allowed read tasks"


def test_promote_agent(test_env):
    """Promoted agents (GRIHASTHA) are ALLOWED write tasks."""
    kernel, governance = test_env
    agent = TestAgents.compliant(agent_id="promoted_agent")
    kernel.register_agent(agent, spawn_process=False)

    # Promote to GRIHASTHA
    success = governance.promote_agent("promoted_agent", reason="Testing")
    assert success
    assert governance.get_agent_ashrama("promoted_agent").current_ashrama == Ashrama.GRIHASTHA

    # Verify write is now allowed
    write_task = TestTasks.with_payload("promoted_agent", {"action": "write"})
    write_task.action = "write"

    allowed = governance.on_task_pre_assign(kernel, "promoted_agent", write_task)
    assert allowed, "GRIHASTHA agent should be allowed write tasks"


def test_demote_agent(test_env):
    """Demoted agents lose write rights."""
    kernel, governance = test_env
    agent = TestAgents.compliant(agent_id="demoted_agent")
    kernel.register_agent(agent, spawn_process=False)

    # Promote then demote
    governance.promote_agent("demoted_agent", reason="Testing")
    assert governance.get_agent_ashrama("demoted_agent").current_ashrama == Ashrama.GRIHASTHA

    governance.demote_agent("demoted_agent", reason="Testing Demotion")
    assert governance.get_agent_ashrama("demoted_agent").current_ashrama == Ashrama.BRAHMACHARI

    # Verify write is forbidden again
    write_task = TestTasks.with_payload("demoted_agent", {"action": "write"})
    write_task.action = "write"

    allowed = governance.on_task_pre_assign(kernel, "demoted_agent", write_task)
    assert not allowed, "Demoted agent should be VETOED from write tasks"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
