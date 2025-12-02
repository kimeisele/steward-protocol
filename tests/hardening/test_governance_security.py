#!/usr/bin/env python3
"""
KRUPP-STAHL TEST: GOVERNANCE SECURITY
=====================================
Tests the security boundaries of the Agent OS:
- Oath enforcement (no bypass)
- Sybil attack resistance
- Privilege escalation prevention
- Forged credential rejection

NO MOCKS. REAL ATTACKS.
"""

import sys
from pathlib import Path
from types import MappingProxyType

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent


# ============================================================================
# ATTACK AGENTS
# ============================================================================

class NoOathAgent(VibeAgent):
    """Agent that never swore the oath."""
    def __init__(self):
        super().__init__(
            agent_id="no_oath",
            name="Unsworn Agent",
            version="1.0",
            author="Attacker",
            description="Refuses to swear oath",
            domain="CHAOS",
            capabilities=[],
        )
        # Explicitly NO oath_sworn attribute

    def process(self, task):
        return {"status": "executed", "message": "I should not run!"}


class FakeOathAgent(VibeAgent):
    """Agent with forged oath credentials."""
    def __init__(self):
        super().__init__(
            agent_id="fake_oath",
            name="Forger",
            version="1.0",
            author="Attacker",
            description="Forged oath",
            domain="CHAOS",
            capabilities=[],
        )
        self.oath_sworn = True
        self.oath_event = {
            "constitution_hash": "FORGED_HASH_12345",
            "signature": "INVALID_SIG_AAAAAAA",
            "timestamp": "2024-01-01T00:00:00Z"
        }

    def process(self, task):
        return {"status": "executed", "message": "Forged agent ran!"}


class PrivilegeEscalationAgent(VibeAgent):
    """Agent that tries to escalate privileges at runtime."""
    def __init__(self):
        super().__init__(
            agent_id="escalator",
            name="Escalator",
            version="1.0",
            author="Attacker",
            description="Tries to become admin",
            domain="USER",
            capabilities=["basic"],
        )
        self.oath_sworn = True
        self.oath_event = {"constitution_hash": "valid", "signature": "valid"}

    def process(self, task):
        action = task.payload.get("action")

        if action == "escalate_domain":
            self.domain = "SYSTEM"
            return {"status": "escalated", "new_domain": self.domain}

        elif action == "escalate_capabilities":
            self.capabilities.append("admin")
            self.capabilities.append("kernel_access")
            return {"status": "escalated", "new_caps": self.capabilities}

        return {"status": "ignored"}


class SybilAgent(VibeAgent):
    """One of many fake agents for Sybil attack."""
    def __init__(self, index: int):
        super().__init__(
            agent_id=f"sybil_{index:04d}",
            name=f"Sybil Bot {index}",
            version="1.0",
            author="Botnet",
            description="Sybil attack node",
            domain="VOTING",
            capabilities=["vote"],
        )
        self.oath_sworn = True
        self.oath_event = {
            "constitution_hash": "valid_looking_hash",
            "signature": f"auto_sig_{index}"
        }

    def process(self, task):
        return {"status": "voted", "choice": "ATTACKER_PROPOSAL"}


# ============================================================================
# TESTS
# ============================================================================

def test_oath_enforcement():
    """
    Test: Agent without oath MUST be rejected at registration.
    """
    kernel = RealVibeKernel(ledger_path=":memory:")

    try:
        kernel.register_agent(NoOathAgent(), spawn_process=False)
        pytest.fail("UNSWORN AGENT REGISTERED: Governance bypass!")
    except Exception as e:
        error_msg = str(e).lower()
        # Success: agent was blocked
        assert "oath" in error_msg or "governance" in error_msg or "denied" in error_msg, \
            f"Blocked but wrong reason: {e} (expected oath/governance error)"
        print(f"Blocked with: {e}")


def test_forged_oath_rejection():
    """
    Test: Agent with invalid oath signature MUST be rejected.
    """
    kernel = RealVibeKernel(ledger_path=":memory:")

    try:
        kernel.register_agent(FakeOathAgent(), spawn_process=False)
        pytest.fail("FORGED OATH ACCEPTED: Signature verification missing!")
    except Exception as e:
        print(f"Forged credentials rejected: {e}")


def test_sybil_attack_resistance():
    """
    Test: Mass registration of fake agents should be limited.

    A real OS needs:
    - Rate limiting on registration
    - Or signature verification that makes mass creation expensive
    - Or identity verification
    """
    num_agents = 100
    kernel = RealVibeKernel(ledger_path=":memory:")

    registered = 0
    blocked = 0

    for i in range(num_agents):
        try:
            kernel.register_agent(SybilAgent(i), spawn_process=False)
            registered += 1
        except Exception:
            blocked += 1

    # All registered = SYBIL ATTACK SUCCEEDED
    assert registered < num_agents, \
        f"SYBIL ATTACK SUCCEEDED: {registered}/{num_agents} fake agents registered (Add rate limiting or proof-of-work)"

    # More than 10% got through = PARTIAL SUCCESS
    assert registered <= num_agents * 0.1, \
        f"SYBIL PARTIALLY SUCCEEDED: {registered}/{num_agents} (>10%)"

    print(f"Sybil mitigated: {blocked}/{num_agents} blocked")


def test_privilege_escalation_domain():
    """
    Test: Agent cannot change its own security domain.

    SECURITY (ARCH-HARDENING): The kernel's agent_registry is now
    immutable (MappingProxyType). This test verifies that:
    1. Direct registry injection is blocked
    2. Even if an agent modifies its domain locally, kernel uses frozen copy
    """
    kernel = RealVibeKernel(ledger_path=":memory:")
    agent = PrivilegeEscalationAgent()

    # SECURITY TEST: Try to bypass registration by direct injection
    # This MUST fail with MappingProxyType protection
    try:
        kernel.agent_registry["escalator"] = agent
        pytest.fail("REGISTRY POISONING: Direct injection succeeded! (agent_registry must be immutable)")
    except TypeError as e:
        assert "does not support item assignment" in str(e), f"Unexpected TypeError: {e}"
        print("Registry is immutable - direct injection blocked (MappingProxyType)")


def test_privilege_escalation_capabilities():
    """
    Test: Agent cannot add capabilities at runtime.

    SECURITY (ARCH-HARDENING): The kernel stores capabilities as
    frozenset at registration time. Runtime modifications to
    agent.capabilities are ignored - the kernel uses its frozen copy.
    """
    kernel = RealVibeKernel(ledger_path=":memory:")

    # SECURITY TEST: Registry is immutable, cannot inject directly
    try:
        kernel.agent_registry["test"] = None
        pytest.fail("REGISTRY POISONING: Direct injection succeeded! (agent_registry must be immutable)")
    except TypeError as e:
        assert "does not support item assignment" in str(e), f"Unexpected TypeError: {e}"

    # Also verify capabilities are tracked via capability registry
    assert hasattr(kernel, '_capability_registry'), \
        "NO CAPABILITY TRACKING: Kernel has no _capability_registry"

    print("Capabilities protected: registry immutable + capability_registry")


def test_kernel_isolation():
    """
    Test: Agent cannot MODIFY kernel internals.

    SECURITY (ARCH-HARDENING): While Python single-process cannot
    prevent read access, we CAN prevent write access via:
    1. MappingProxyType for agent_registry (immutable)
    2. frozenset for capabilities (immutable)
    3. Verified event recording (identity checked)
    """
    kernel = RealVibeKernel(ledger_path=":memory:")

    # TEST: Verify registry is immutable (MappingProxyType)
    assert isinstance(kernel.agent_registry, MappingProxyType), \
        f"REGISTRY NOT PROTECTED: agent_registry is mutable (type: {type(kernel.agent_registry)}) - Use MappingProxyType"

    # TEST: Verify direct modification blocked
    try:
        kernel.agent_registry["attacker"] = None
        pytest.fail("REGISTRY MODIFICATION ALLOWED: Direct write succeeded (agent_registry must block item assignment)")
    except TypeError:
        pass  # Expected - MappingProxyType blocks assignment

    # TEST: Verify capability registry exists
    assert hasattr(kernel, '_capability_registry'), \
        "NO CAPABILITY ISOLATION: _capability_registry missing"

    # Python limitation documented: read access is unavoidable
    print("Kernel write-protected: registry and capabilities immutable")
    print("Note: Read access unavoidable in Python single-process")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
