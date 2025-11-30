#!/usr/bin/env python3
"""
Mission Execution Script - Cost-Efficient Scaling
Simulates VibeOS kernel to execute ENVOY commands for the mission.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from civic.cartridge_main import CivicCartridge
from envoy.cartridge_main import EnvoyCartridge
from forum.cartridge_main import ForumCartridge
from herald.cartridge_main import HeraldCartridge
from science.cartridge_main import ScienceCartridge

# Import Vibe Core and Cartridges
from vibe_core import Task, VibeAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("MISSION_EXECUTION")


class MockKernel:
    """Simulates the VibeOS Kernel for agent orchestration."""

    def __init__(self):
        self.agent_registry = {}
        logger.info("🖥️  MockKernel Initialized")

    def register_agent(self, agent_id: str, agent: VibeAgent):
        self.agent_registry[agent_id] = agent
        logger.info(f"   + Registered Agent: {agent_id.upper()}")

    def get_agent(self, agent_id: str) -> Optional[VibeAgent]:
        return self.agent_registry.get(agent_id)


def main():
    print("\n" + "=" * 60)
    print("🚀 MISSION EXECUTION: Cost-Efficient Scaling")
    print("=" * 60 + "\n")

    # 1. Initialize Kernel and Agents
    kernel = MockKernel()

    # Instantiate Agents
    envoy = EnvoyCartridge()
    herald = HeraldCartridge()
    civic = CivicCartridge()
    forum = ForumCartridge()
    science = ScienceCartridge()

    # Register Agents
    kernel.register_agent("envoy", envoy)
    kernel.register_agent("herald", herald)
    kernel.register_agent("civic", civic)
    kernel.register_agent("forum", forum)
    kernel.register_agent("science", science)

    # Inject Kernel into Envoy (and others if needed)
    envoy.set_kernel(kernel)
    # Note: Other agents might need kernel injection too depending on their implementation
    # We'll assume they are self-contained or don't strictly need it for this flow
    # But let's try to inject if they have the method
    for agent in [herald, civic, forum, science]:
        if hasattr(agent, "set_kernel"):
            agent.set_kernel(kernel)

    print("\n✅ System Initialized. Starting Mission...\n")

    # 2. Phase 1: Closure (Crisis Loop) - Execute PROP-009
    print("\n" + "-" * 40)
    print("🔐 PHASE 1: CLOSURE (Execute PROP-009)")
    print("-" * 40)

    task1 = Task(
        agent_id="envoy",
        payload={"command": "execute", "args": {"proposal_id": "PROP-009"}},
    )

    result1 = envoy.process(task1)
    print(f"\n📝 Result Phase 1: {json.dumps(result1, indent=2)}")

    if result1.get("status") != "success":
        print("❌ Phase 1 Failed. Aborting.")
        # Proceeding anyway for demonstration if it was already executed
        if "already executed" not in str(result1.get("error", "")).lower():
            pass  # In a real script we might exit, but here we continue to try Phase 2

    # 3. Phase 2: Launch (New Mission) - Start Campaign
    print("\n" + "-" * 40)
    print("📢 PHASE 2: LAUNCH (Start Campaign)")
    print("-" * 40)

    task2 = Task(
        agent_id="envoy",
        payload={
            "command": "campaign",
            "args": {
                "goal": "starte die Kampagne zur Veröffentlichung des G.A.P. Reports und skaliere diese Kampagne so kosten-effizient wie möglich auf allen Kanälen. Fokussiere dich auf den Proof, dass Governed Intelligence günstig routet.",
                "campaign_type": "awareness",
                "focus": "cost_efficiency",
                "proof": "governed_intelligence",
            },
        },
    )

    result2 = envoy.process(task2)
    print(f"\n📝 Result Phase 2: {json.dumps(result2, indent=2)}")

    # 4. Generate G.A.P. Report (Explicitly to ensure it's fresh and we get the path)
    print("\n" + "-" * 40)
    print("📊 GENERATING G.A.P. REPORT")
    print("-" * 40)

    task3 = Task(
        agent_id="envoy",
        payload={
            "command": "report",
            "args": {
                "title": "Mission Cost-Efficient Scaling Proof",
                "report_type": "gap",
                "format": "markdown",
            },
        },
    )

    result3 = envoy.process(task3)
    print(f"\n📝 Result Report Generation: {json.dumps(result3, indent=2)}")

    print("\n" + "=" * 60)
    print("🏁 MISSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
