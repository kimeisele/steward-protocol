#!/usr/bin/env python3
"""
Integration Test: Capability Revocation (REVOKE_MANDATE)
=========================================================

Tests for Phase 2 implementation of REVOKE_MANDATE syscall.

Tests that:
1. Capabilities can be revoked from agents
2. Revoked agents cannot use revoked capabilities
3. Permission model is enforced (who can revoke from whom)
4. Audit trail is maintained in ledger
5. REVOKE_MANDATE syscall works end-to-end
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.plugins.test_orchestration.fixtures import TestKernel
from vibe_core.protocols import VibeAgent
from vibe_core.scheduling import Task
from vibe_core.steward import OathMixin


class MockAgent(VibeAgent, OathMixin):
    """Mock agent for capability testing with Constitutional Oath.

    Note: Named MockAgent (not TestAgent) to avoid pytest collection conflict.
    Uses OathMixin.swear_oath_sync() - the canonical way to become compliant.
    """

    def __init__(self, agent_id: str, capabilities: list[str]):
        super().__init__(
            agent_id=agent_id,
            name=f"Mock Agent {agent_id}",
            capabilities=capabilities,
        )
        # Initialize OathMixin and swear oath properly (not manual oath_sworn=True)
        self.oath_mixin_init(agent_id)
        self.swear_oath_sync()

    def process(self, task: Task) -> dict:
        return {"status": "completed", "message": "test"}


def test_revoke_removes_capability():
    """Test that revoking a capability removes it from the agent."""
    kernel = TestKernel.minimal()

    # Register agent with capabilities
    agent = MockAgent("test_agent_1", ["can_transfer", "can_spawn"])
    kernel.register_agent(agent, spawn_process=False)

    # Verify agent has capabilities
    assert kernel._check_agent_capability("test_agent_1", "can_transfer")
    assert kernel._check_agent_capability("test_agent_1", "can_spawn")

    # Revoke one capability
    result = kernel.revoke_capability(
        agent_id="test_agent_1", capabilities=["can_transfer"], revoker_id="KERNEL", reason="Test revocation"
    )

    # Verify revocation succeeded
    assert result["success"] is True
    assert "can_transfer" in result["revoked"]
    assert result["not_found"] == []

    # Verify agent no longer has the capability
    assert not kernel._check_agent_capability("test_agent_1", "can_transfer")

    # Verify agent still has other capability
    assert kernel._check_agent_capability("test_agent_1", "can_spawn")


def test_revoked_agent_cannot_use_capability():
    """Test that revoked agent cannot use revoked capability."""
    kernel = TestKernel.minimal()

    # Register agent with tool capability
    agent = MockAgent("test_agent_2", ["execute_code", "read_file"])
    kernel.register_agent(agent, spawn_process=False)

    # Agent can use capability before revocation
    assert kernel._check_agent_capability("test_agent_2", "execute_code")

    # Revoke capability
    kernel.revoke_capability(
        agent_id="test_agent_2", capabilities=["execute_code"], revoker_id="KERNEL", reason="Security violation"
    )

    # Agent cannot use capability after revocation
    assert not kernel._check_agent_capability("test_agent_2", "execute_code")


def test_permission_model_kernel_can_revoke():
    """Test that KERNEL can revoke from any agent."""
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_3", ["can_transfer"])
    kernel.register_agent(agent, spawn_process=False)

    # KERNEL can revoke from anyone
    result = kernel.revoke_capability(
        agent_id="test_agent_3", capabilities=["can_transfer"], revoker_id="KERNEL", reason="Test"
    )

    assert result["success"] is True


def test_permission_model_civic_can_revoke():
    """Test that CIVIC can revoke from any agent (governance)."""
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_4", ["can_transfer"])
    kernel.register_agent(agent, spawn_process=False)

    # CIVIC can revoke from anyone
    result = kernel.revoke_capability(
        agent_id="test_agent_4", capabilities=["can_transfer"], revoker_id="civic", reason="Governance decision"
    )

    assert result["success"] is True


def test_permission_model_self_revocation():
    """Test that agents can revoke their own capabilities (voluntary)."""
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_5", ["can_transfer", "can_spawn"])
    kernel.register_agent(agent, spawn_process=False)

    # Agent can revoke from themselves (Principle of Least Privilege)
    result = kernel.revoke_capability(
        agent_id="test_agent_5",
        capabilities=["can_transfer"],
        revoker_id="test_agent_5",  # Self-revocation
        reason="No longer needed",
    )

    assert result["success"] is True
    assert not kernel._check_agent_capability("test_agent_5", "can_transfer")


def test_permission_model_agent_cannot_revoke_from_others():
    """Test that agents cannot revoke from other agents."""
    kernel = TestKernel.minimal()

    agent1 = MockAgent("test_agent_6a", ["can_transfer"])
    agent2 = MockAgent("test_agent_6b", ["can_transfer"])
    kernel.register_agent(agent1, spawn_process=False)
    kernel.register_agent(agent2, spawn_process=False)

    # Agent 6a tries to revoke from Agent 6b (should fail)
    result = kernel.revoke_capability(
        agent_id="test_agent_6b",
        capabilities=["can_transfer"],
        revoker_id="test_agent_6a",  # Trying to revoke from another agent
        reason="Malicious attempt",
    )

    assert result["success"] is False
    assert "Permission denied" in result["message"]

    # Agent 6b should still have capability
    assert kernel._check_agent_capability("test_agent_6b", "can_transfer")


def test_audit_trail_in_ledger():
    """Test that revocations are recorded in the audit trail."""
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_7", ["can_transfer", "can_spawn"])
    kernel.register_agent(agent, spawn_process=False)

    # Revoke capability
    kernel.revoke_capability(
        agent_id="test_agent_7", capabilities=["can_transfer"], revoker_id="civic", reason="Test audit trail"
    )

    # Check ledger for revocation event
    events = kernel.dump_ledger()

    # Find revocation event
    revocation_events = [
        e for e in events if e.get("event_type") == "capability_revoked" and e.get("agent_id") == "test_agent_7"
    ]

    assert len(revocation_events) > 0

    # Verify event details
    event = revocation_events[0]
    assert "can_transfer" in event["details"]["revoked_capabilities"]
    assert event["details"]["revoker_id"] == "civic"
    assert event["details"]["reason"] == "Test audit trail"


def test_revoke_multiple_capabilities():
    """Test revoking multiple capabilities at once."""
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_8", ["cap_a", "cap_b", "cap_c"])
    kernel.register_agent(agent, spawn_process=False)

    # Revoke multiple capabilities
    result = kernel.revoke_capability(
        agent_id="test_agent_8", capabilities=["cap_a", "cap_b"], revoker_id="KERNEL", reason="Test multiple"
    )

    assert result["success"] is True
    assert len(result["revoked"]) == 2
    assert "cap_a" in result["revoked"]
    assert "cap_b" in result["revoked"]

    # Verify both are revoked
    assert not kernel._check_agent_capability("test_agent_8", "cap_a")
    assert not kernel._check_agent_capability("test_agent_8", "cap_b")

    # Verify remaining capability still exists
    assert kernel._check_agent_capability("test_agent_8", "cap_c")


def test_revoke_nonexistent_capability():
    """Test revoking a capability the agent doesn't have."""
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_9", ["cap_a"])
    kernel.register_agent(agent, spawn_process=False)

    # Try to revoke capability agent doesn't have
    result = kernel.revoke_capability(
        agent_id="test_agent_9", capabilities=["cap_b", "cap_c"], revoker_id="KERNEL", reason="Test nonexistent"
    )

    # OPUS-075: Idempotent syscalls - goal achieved means success
    # TEST EXPECTS: success=True (agent doesn't have these caps = goal achieved)
    # FIX REQUIRED: vibe_core/capability_registry.py:194
    #   Change: return {"success": len(revoked) > 0, ...}
    #   To:     none_have = all(c not in agent_caps for c in capabilities)
    #           return {"success": none_have, ...}
    assert result["success"] is True  # CI FAILS until Ring-0 fix applied
    assert len(result["revoked"]) == 0
    assert len(result["not_found"]) == 2


def test_revoke_from_unregistered_agent():
    """Test revoking from an agent that doesn't exist."""
    kernel = TestKernel.minimal()

    # Try to revoke from non-existent agent
    result = kernel.revoke_capability(
        agent_id="nonexistent_agent", capabilities=["some_cap"], revoker_id="KERNEL", reason="Test nonexistent agent"
    )

    assert result["success"] is False
    assert "not registered" in result["message"].lower()


def test_narasimha_revokes_all_capabilities():
    """Test that Narasimha kill-switch revokes all capabilities."""
    import pytest
    pytest.skip("Requires full brahma bootstrap: production narasimha_destroy_agent uses "
                "brahma._capability_registry.revoke_all, which TestKernel.minimal() does not set up. "
                "Re-enable when the minimal harness bootstraps the capability registry.")
    kernel = TestKernel.minimal()

    agent = MockAgent("test_agent_10", ["cap_a", "cap_b", "cap_c"])
    kernel.register_agent(agent, spawn_process=False)

    # Verify agent has capabilities
    assert kernel._check_agent_capability("test_agent_10", "cap_a")
    assert kernel._check_agent_capability("test_agent_10", "cap_b")

    # Simulate Narasimha revoke-all
    success = kernel._capability_registry.revoke_all(
        agent_id="test_agent_10", revoker_id="NARASIMHA", reason="Kill-switch activated"
    )

    assert success is True

    # Verify all capabilities are revoked
    assert not kernel._check_agent_capability("test_agent_10", "cap_a")
    assert not kernel._check_agent_capability("test_agent_10", "cap_b")
    assert not kernel._check_agent_capability("test_agent_10", "cap_c")


def test_syscall_revoke_mandate_success():
    """Test REVOKE_MANDATE syscall end-to-end."""
    from vibe_core.semantic_syscalls import SemanticSyscallHandler, SyscallRequest, SyscallType

    kernel = TestKernel.minimal()
    handler = SemanticSyscallHandler(kernel)

    # Register test agent
    agent = MockAgent("test_agent_11", ["can_transfer", "can_spawn"])
    kernel.register_agent(agent, spawn_process=False)

    # Create REVOKE_MANDATE syscall request
    request = SyscallRequest(
        syscall_type=SyscallType.REVOKE_MANDATE,
        requester_id="civic",
        params={"agent_id": "test_agent_11", "capabilities": ["can_transfer"], "reason": "Test syscall"},
    )

    # Execute syscall
    result = handler.handle(request)

    # Verify syscall succeeded
    assert result.success is True
    assert "can_transfer" in result.output["revoked"]

    # Verify capability was actually revoked
    assert not kernel._check_agent_capability("test_agent_11", "can_transfer")


def test_syscall_revoke_mandate_permission_denied():
    """Test REVOKE_MANDATE syscall with insufficient permissions."""
    from vibe_core.semantic_syscalls import SemanticSyscallHandler, SyscallRequest, SyscallType

    kernel = TestKernel.minimal()
    handler = SemanticSyscallHandler(kernel)

    # Register two test agents
    agent1 = MockAgent("test_agent_12a", ["can_transfer"])
    agent2 = MockAgent("test_agent_12b", ["can_transfer"])
    kernel.register_agent(agent1, spawn_process=False)
    kernel.register_agent(agent2, spawn_process=False)

    # Agent 12a tries to revoke from Agent 12b (should fail)
    request = SyscallRequest(
        syscall_type=SyscallType.REVOKE_MANDATE,
        requester_id="test_agent_12a",
        params={"agent_id": "test_agent_12b", "capabilities": ["can_transfer"], "reason": "Malicious"},
    )

    # Execute syscall
    result = handler.handle(request)

    # Verify syscall failed with permission error
    assert result.success is False
    assert "Permission denied" in result.error

    # Verify capability was NOT revoked
    assert kernel._check_agent_capability("test_agent_12b", "can_transfer")


def test_core_capabilities_not_revocable():
    """Test that core capabilities (read_file, write_file, etc.) work even if not explicitly granted."""
    kernel = TestKernel.minimal()

    # Register agent with NO capabilities
    agent = MockAgent("test_agent_13", [])
    kernel.register_agent(agent, spawn_process=False)

    # Core capabilities should still work
    assert kernel._check_agent_capability("test_agent_13", "read_file")
    assert kernel._check_agent_capability("test_agent_13", "write_file")
    assert kernel._check_agent_capability("test_agent_13", "list_tasks")


def test_grant_already_had_is_idempotent():
    """
    OPUS-075: Test that granting capabilities agent already has is idempotent SUCCESS.

    Idempotent operations should return success if the desired end state is achieved,
    regardless of whether any action was taken. This fixes GRANT_MANDATE 0/153 metric.
    """
    kernel = TestKernel.minimal()

    # Register agent with some capabilities
    agent = MockAgent("test_agent_14", ["cap_a", "cap_b"])
    kernel.register_agent(agent, spawn_process=False)

    # Try to grant capabilities agent already has
    result = kernel.grant_capability(
        agent_id="test_agent_14",
        capabilities=["cap_a", "cap_b"],  # Already has these
        granter_id="KERNEL",
        reason="Test idempotent grant",
    )

    # OPUS-075: Idempotent success - goal achieved (agent has all requested caps)
    # TEST EXPECTS: success=True (even though nothing new was granted)
    # FIX REQUIRED: vibe_core/capability_registry.py:261
    #   Change: return {"success": len(granted) > 0, ...}
    #   To:     all_have = all(c in agent_caps for c in capabilities)
    #           return {"success": all_have, ...}
    assert result["success"] is True  # CI FAILS until Ring-0 fix applied
    assert len(result["granted"]) == 0
    assert len(result["already_had"]) == 2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
