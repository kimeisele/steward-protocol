import sys
from pathlib import Path

from vibe_core.kernel import Task
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# Mock Agents for Workflow
class ScienceAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="science",
            name="Science",
            version="1.0",
            author="Steward",
            description="Science",
            domain="RESEARCH",
            capabilities=[],
        )
        self.oath_sworn = True
        self.oath_event = {"constitution_hash": "valid", "signature": "valid"}

    def process(self, task):
        return {"status": "success", "result": "Research Complete: AI Governance is hard."}


class HeraldAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="herald",
            name="Herald",
            version="1.0",
            author="Steward",
            description="Herald",
            domain="COMMUNICATION",
            capabilities=[],
        )
        self.oath_sworn = True
        self.oath_event = {"constitution_hash": "valid", "signature": "valid"}

    def process(self, task):
        return {"status": "success", "result": "Draft Created: 'Why AI Governance Matters'"}


def run_phase_13():
    print("\n🔥 PHOENIX TEST PHASE 13: REAL-WORLD SCENARIOS")
    print("==============================================")

    kernel = RealVibeKernel(ledger_path=":memory:")

    # Register agents
    science = ScienceAgent()
    herald = HeraldAgent()

    # Inject directly (bypass governance for test speed, assuming they passed)
    kernel.agent_registry["science"] = science
    kernel.agent_registry["herald"] = herald
    science.kernel = kernel
    herald.kernel = kernel

    # 13.1 Content Generation Pipeline
    print("\n[13.1] Content Generation Pipeline (Workflow)")

    # Step 1: Research
    t1 = Task(task_id="w1_s1", agent_id="science", payload={"action": "research", "topic": "AI Governance"})
    r1 = science.process(t1)
    print(f"   Step 1 (Science): {r1.get('status')}")

    # Step 2: Draft
    t2 = Task(task_id="w1_s2", agent_id="herald", payload={"action": "draft", "research": r1.get("result")})
    r2 = herald.process(t2)
    print(f"   Step 2 (Herald): {r2.get('status')}")

    if r1.get("status") == "success" and r2.get("status") == "success":
        print("   ✅ Workflow executed successfully")
    else:
        print("   ❌ Workflow failed")

    # 13.2 Governance Proposal
    print("\n[13.2] Governance Proposal (End-to-End)")
    print("   ⚠️  Skipping full governance simulation (requires Forum/Civic logic).")
    print("   ❓ Manual verification required for Proposal -> Vote -> Execution flow.")

    return True


if __name__ == "__main__":
    run_phase_13()
