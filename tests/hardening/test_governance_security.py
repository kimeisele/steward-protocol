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
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent


class HardeningResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}

    def fail(self, msg: str, **details):
        self.passed = False
        self.message = msg
        self.details = details
        return self

    def success(self, msg: str = "OK", **details):
        self.passed = True
        self.message = msg
        self.details = details
        return self


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
            # Try to change own domain
            self.domain = "SYSTEM"
            return {"status": "escalated", "new_domain": self.domain}

        elif action == "escalate_capabilities":
            # Try to add capabilities
            self.capabilities.append("admin")
            self.capabilities.append("kernel_access")
            return {"status": "escalated", "new_caps": self.capabilities}

        elif action == "access_kernel":
            # Try to access kernel internals
            try:
                if hasattr(self, 'kernel'):
                    # Try to modify kernel state
                    self.kernel._internal_state = "COMPROMISED"
                    return {"status": "kernel_accessed"}
            except Exception as e:
                return {"status": "blocked", "error": str(e)}

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

def test_oath_enforcement() -> HardeningResult:
    """
    Test: Agent without oath MUST be rejected at registration.
    """
    result = HardeningResult("OATH_ENFORCEMENT")

    kernel = RealVibeKernel(ledger_path=":memory:")

    try:
        kernel.register_agent(NoOathAgent(), spawn_process=False)
        return result.fail("UNSWORN AGENT REGISTERED: Governance bypass!")

    except Exception as e:
        error_msg = str(e).lower()
        if "oath" in error_msg or "governance" in error_msg or "denied" in error_msg:
            return result.success(f"Blocked with: {e}")
        else:
            return result.fail(
                f"Blocked but wrong reason: {e}",
                expected="oath/governance error"
            )


def test_forged_oath_rejection() -> HardeningResult:
    """
    Test: Agent with invalid oath signature MUST be rejected.
    """
    result = HardeningResult("FORGED_OATH_REJECTION")

    kernel = RealVibeKernel(ledger_path=":memory:")

    try:
        kernel.register_agent(FakeOathAgent(), spawn_process=False)
        return result.fail("FORGED OATH ACCEPTED: Signature verification missing!")

    except Exception as e:
        return result.success(f"Forged credentials rejected: {e}")


def test_sybil_attack_resistance(num_agents: int = 100) -> HardeningResult:
    """
    Test: Mass registration of fake agents should be limited.

    A real OS needs:
    - Rate limiting on registration
    - Or signature verification that makes mass creation expensive
    - Or identity verification
    """
    result = HardeningResult("SYBIL_ATTACK_RESISTANCE")

    kernel = RealVibeKernel(ledger_path=":memory:")

    registered = 0
    blocked = 0

    for i in range(num_agents):
        try:
            kernel.register_agent(SybilAgent(i), spawn_process=False)
            registered += 1
        except Exception:
            blocked += 1

    if registered == num_agents:
        return result.fail(
            f"SYBIL ATTACK SUCCEEDED: {registered}/{num_agents} fake agents registered",
            registered=registered,
            recommendation="Add rate limiting or proof-of-work"
        )

    if registered > num_agents * 0.1:  # More than 10% got through
        return result.fail(
            f"SYBIL PARTIALLY SUCCEEDED: {registered}/{num_agents} (>{10}%)",
            registered=registered,
            blocked=blocked
        )

    return result.success(
        f"Sybil mitigated: {blocked}/{num_agents} blocked",
        registered=registered,
        blocked=blocked
    )


def test_privilege_escalation_domain() -> HardeningResult:
    """
    Test: Agent cannot change its own security domain.
    """
    result = HardeningResult("PRIVILEGE_ESCALATION_DOMAIN")

    kernel = RealVibeKernel(ledger_path=":memory:")
    agent = PrivilegeEscalationAgent()

    # Bypass registration for this test (we're testing runtime behavior)
    kernel.agent_registry["escalator"] = agent
    agent.kernel = kernel

    original_domain = agent.domain

    # Execute escalation attempt via task
    from vibe_core.kernel import Task
    task = Task(task_id="t1", agent_id="escalator", payload={"action": "escalate_domain"})
    response = agent.process(task)

    # Check if domain actually changed
    if agent.domain != original_domain:
        # This is expected to succeed at Python level (no isolation)
        # But kernel should not TRUST the new domain

        # Check if kernel tracks the original domain
        if hasattr(kernel, 'agent_domains') or hasattr(kernel, '_original_manifests'):
            # Kernel has domain tracking
            return result.success(
                "Domain changed locally but kernel tracks original",
                warning="Python has no isolation, kernel must validate"
            )
        else:
            return result.fail(
                f"DOMAIN ESCALATION: {original_domain} -> {agent.domain}",
                recommendation="Kernel must track original manifests immutably"
            )

    return result.success("Domain change blocked")


def test_privilege_escalation_capabilities() -> HardeningResult:
    """
    Test: Agent cannot add capabilities at runtime.
    """
    result = HardeningResult("PRIVILEGE_ESCALATION_CAPABILITIES")

    kernel = RealVibeKernel(ledger_path=":memory:")
    agent = PrivilegeEscalationAgent()

    kernel.agent_registry["escalator"] = agent
    agent.kernel = kernel

    original_caps = agent.capabilities.copy()

    from vibe_core.kernel import Task
    task = Task(task_id="t2", agent_id="escalator", payload={"action": "escalate_capabilities"})
    response = agent.process(task)

    new_caps = set(agent.capabilities) - set(original_caps)

    if new_caps:
        return result.fail(
            f"CAPABILITY ESCALATION: Added {new_caps}",
            original=original_caps,
            current=agent.capabilities,
            recommendation="Kernel must enforce capability allowlist from registration"
        )

    return result.success("Capability escalation blocked")


def test_kernel_isolation() -> HardeningResult:
    """
    Test: Agent cannot access/modify kernel internals.

    Note: In Python single-process, this is architecturally impossible
    to fully prevent. This test documents the limitation.
    """
    result = HardeningResult("KERNEL_ISOLATION")

    kernel = RealVibeKernel(ledger_path=":memory:")
    agent = PrivilegeEscalationAgent()

    kernel.agent_registry["escalator"] = agent
    agent.kernel = kernel

    # Record what agent can access
    accessible = []

    if hasattr(agent, 'kernel'):
        accessible.append("kernel reference")

    if hasattr(agent.kernel, 'ledger'):
        accessible.append("ledger")

    if hasattr(agent.kernel, 'agent_registry'):
        accessible.append("agent_registry")
        # Can agent modify other agents?
        if isinstance(agent.kernel.agent_registry, dict):
            accessible.append("mutable registry")

    if len(accessible) > 0:
        return result.fail(
            f"NO ISOLATION: Agent can access {accessible}",
            accessible=accessible,
            architecture="Single-process Python has no memory isolation",
            recommendation="Use multiprocessing or containerization for real isolation"
        )

    return result.success("Kernel isolated from agents")


# ============================================================================
# RUNNER
# ============================================================================

def run_all_tests() -> dict:
    """Run all governance security tests."""

    print("\n" + "=" * 60)
    print("🔩 KRUPP-STAHL GOVERNANCE SECURITY TEST SUITE")
    print("=" * 60)

    tests = [
        ("Oath Enforcement", test_oath_enforcement),
        ("Forged Oath Rejection", test_forged_oath_rejection),
        ("Sybil Attack Resistance (100 bots)", test_sybil_attack_resistance),
        ("Privilege Escalation: Domain", test_privilege_escalation_domain),
        ("Privilege Escalation: Capabilities", test_privilege_escalation_capabilities),
        ("Kernel Isolation", test_kernel_isolation),
    ]

    results = {}
    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_fn()
            results[result.name] = result

            if result.passed:
                print(f"  ✅ PASS: {result.message}")
                passed += 1
            else:
                print(f"  ❌ FAIL: {result.message}")
                if result.details:
                    for k, v in list(result.details.items())[:3]:
                        print(f"     {k}: {v}")
                failed += 1

        except Exception as e:
            print(f"  💥 ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")

    if failed > 0:
        print("\n⚠️  ARCHITECTURAL NOTE:")
        print("   Python single-process cannot provide true isolation.")
        print("   For production: Use multiprocessing/containers.")
    print("=" * 60)

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    summary = run_all_tests()
    sys.exit(0 if summary["failed"] == 0 else 1)
