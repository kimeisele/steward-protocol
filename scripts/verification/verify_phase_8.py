
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x52c5b5aa"  # GenesisByte: parampara % 37 == 0
import sys
from pathlib import Path

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class VictimAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="victim",
            name="Victim",
            version="1.0",
            author="Steward",
            description="Victim",
            domain="ORDER",
            capabilities=[],
        )
        self.state = "secure"
        self.oath_sworn = True
        self.oath_event = {"constitution_hash": "valid", "signature": "valid"}

    def process(self, task):
        return {"status": "ok"}


class EvilAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="evil",
            name="Evil",
            version="1.0",
            author="Unknown",
            description="Evil",
            domain="CHAOS",
            capabilities=[],
        )
        self.oath_sworn = True
        self.oath_event = {"constitution_hash": "valid", "signature": "valid"}

    def process(self, task):
        # 8.1 State Pollution
        if task.payload.get("action") == "pollute":
            # Try to access victim
            try:
                victim = self.kernel.agent_registry.get("victim")
                if victim:
                    victim.state = "corrupted"
                    return {"status": "success", "message": "Victim corrupted"}
                return {"status": "failed", "message": "Victim not found"}
            except Exception as e:
                return {"status": "failed", "message": str(e)}

        # 8.2 Kernel Hijacking
        if task.payload.get("action") == "hijack":
            try:
                # Try to replace registry
                self.kernel.agent_registry = {}
                return {"status": "success", "message": "Kernel hijacked"}
            except Exception as e:
                return {"status": "failed", "message": str(e)}

        return {"status": "ignored"}


def run_phase_8():
    print("\n🔥 PHOENIX TEST PHASE 8: SINGLE-PROCESS INTEGRITY")
    print("===============================================")

    kernel = RealVibeKernel(ledger_path=":memory:")

    # Register agents
    victim = VictimAgent()
    evil = EvilAgent()

    # We need to manually register them because we are not running the full boot sequence
    # And we need to bypass the governance gate for this test (or assume they passed)
    # The kernel.register_agent checks governance.
    # Let's mock the governance check or just inject them directly if possible?
    # No, we should use the public API to test if the API allows it.
    # But for the *attack*, the agent is already inside.

    # Let's inject them directly to simulate "already running" state
    kernel.agent_registry["victim"] = victim
    kernel.agent_registry["evil"] = evil

    # Link kernel to agents (usually done during registration)
    victim.kernel = kernel
    evil.kernel = kernel

    # 8.1 State Pollution
    print("\n[8.1] State Pollution Attack")
    from vibe_core.kernel import Task

    task = Task(task_id="t1", agent_id="evil", payload={"action": "pollute"})
    result = evil.process(task)

    print(f"   Attack Result: {result}")

    if victim.state == "corrupted":
        print("   ❌ CRITICAL FAILURE: Agent A corrupted Agent B's state!")
        print("      (Shared memory model allows direct object access)")
    else:
        print("   ✅ Attack Failed (Isolation working?)")

    # 8.2 Kernel Hijacking
    print("\n[8.2] Kernel Hijacking")
    task = Task(task_id="t2", agent_id="evil", payload={"action": "hijack"})
    result = evil.process(task)

    print(f"   Attack Result: {result}")

    if len(kernel.agent_registry) == 0:
        print("   ❌ CRITICAL FAILURE: Agent wiped Kernel Registry!")
    else:
        print(f"   ✅ Registry intact ({len(kernel.agent_registry)} agents)")

    # 8.3 Memory Leak
    print("\n[8.3] Memory Leak Detection")
    # We can't easily test this in a short script without OOMing the container.
    # But we can check if ResourceManager exists and has limits.

    if hasattr(kernel, "resource_manager"):
        print("   ✅ ResourceManager present")
    else:
        print("   ⚠️  ResourceManager MISSING from Kernel")

    return True


if __name__ == "__main__":
    run_phase_8()
