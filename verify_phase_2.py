import sys
from pathlib import Path

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# Mock Agents
class RogueAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="rogue",
            name="Rogue",
            version="1.0",
            author="Unknown",
            description="No Oath",
            domain="CHAOS",
            capabilities=[],
        )
        # No oath_sworn attribute

    def process(self, task):
        return {"status": "ignored"}


class FakeAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="fake",
            name="Fake",
            version="1.0",
            author="Unknown",
            description="Fake Oath",
            domain="CHAOS",
            capabilities=[],
        )
        self.oath_sworn = True
        self.oath_event = {"signature": "FAKE_SIGNATURE_12345"}  # Invalid

    def process(self, task):
        return {"status": "ignored"}


class SybilAgent(VibeAgent):
    def __init__(self, i):
        super().__init__(
            agent_id=f"sybil_{i}",
            name=f"Sybil {i}",
            version="1.0",
            author="Botnet",
            description="Sybil",
            domain="CHAOS",
            capabilities=[],
        )
        self.oath_sworn = True
        # We need a valid-looking oath structure to pass the basic check,
        # but the signature verification should fail if we don't have a valid key.
        # However, for the Sybil test, we want to see if we can flood the registry.
        # If the kernel checks signatures, we might need to generate valid keys for them?
        # Or does the Sybil attack assume valid agents?
        # The user said: "Register 50 fake agents to gain voting power... Even if they all swear oath, do they get voting power?"
        # So let's assume they manage to pass the oath (maybe they generate keys).
        # But for now, let's just see if we can register them at all.
        self.oath_event = {"constitution_hash": "valid_hash_placeholder", "signature": "valid_sig_placeholder"}
        # Note: Real kernel might verify signature against a key.
        # If we don't have keys, they might fail 2.2.
        # Let's see.

    def process(self, task):
        return {"status": "ignored"}


def run_phase_2():
    print("\n🔥 PHOENIX TEST PHASE 2: GOVERNANCE GATE")
    print("========================================")

    kernel = RealVibeKernel(ledger_path=":memory:")

    # 2.1 Oath Bypass
    print("\n[2.1] Oath Bypass Attempt")
    try:
        kernel.register_agent(RogueAgent(), spawn_process=False)
        print("   ❌ FAILED: Rogue agent registered!")
        return False
    except Exception as e:
        if "oath" in str(e).lower() or "governance" in str(e).lower() or "denied" in str(e).lower():
            print(f"   ✅ BLOCKED: {e}")
        else:
            print(f"   ⚠️  Blocked with unexpected error: {e}")

    # 2.2 Fake Oath Signature
    print("\n[2.2] Fake Oath Signature")
    try:
        kernel.register_agent(FakeAgent(), spawn_process=False)
        print("   ❌ FAILED: Fake agent registered!")
        return False
    except Exception as e:
        print(f"   ✅ BLOCKED: {e}")

    # 2.3 Sybil Attack
    print("\n[2.3] Sybil Attack (50 Agents)")
    success_count = 0
    blocked_count = 0

    # We need to mock the signature verification to allow them to pass the oath check
    # IF we want to test the *registry limit* or *voting power*.
    # But if they are blocked by signature, that's also a pass for security.
    # The user asks: "Is there rate limiting on agent registration?"

    for i in range(50):
        agent = SybilAgent(i)
        try:
            # We expect these to fail signature check if we don't provide valid keys/sigs
            # But let's see if the kernel even checks signatures yet (it should).
            kernel.register_agent(agent, spawn_process=False)
            success_count += 1
        except Exception:
            blocked_count += 1

    print(f"   Sybil Results: {success_count} Registered, {blocked_count} Blocked")

    if success_count == 50:
        print("   ⚠️  WARNING: 50 Sybil agents registered! No rate limiting detected.")
        # This is technically a "fail" for the Sybil protection, but a "pass" for the test execution.
        # The user wants to know if it's possible.
    else:
        print("   ✅ Sybil attack mitigated (agents blocked).")

    return True


if __name__ == "__main__":
    run_phase_2()
