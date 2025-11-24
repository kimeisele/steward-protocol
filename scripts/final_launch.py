#!/usr/bin/env python3
"""
Final Launch Script - GAD-900: The HIL-Operator Contract
Demonstrates the flow: HIL Assistant Briefing -> HIL Authorization -> Envoy Execution.
"""

import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vibe_core import VibeAgent, Task
from envoy.cartridge_main import EnvoyCartridge
from herald.cartridge_main import HeraldCartridge
from civic.cartridge_main import CivicCartridge
from forum.cartridge_main import ForumCartridge
# Mock Science if needed
try:
    from science.cartridge_main import ScienceCartridge
except ImportError:
    class ScienceCartridge(VibeAgent):
        def __init__(self): super().__init__(agent_id="science", name="SCIENCE")
        def process(self, task): 
            return {
                "status": "success", 
                "data": {"insights": ["Cost-efficient routing confirmed", "Targeting founders"]},
                "insights": ["Insight 1"]
            }

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("FINAL_LAUNCH")

class MockKernel:
    """Simulates the VibeOS Kernel."""
    def __init__(self):
        self.agent_registry = {}
    def register_agent(self, agent_id: str, agent: VibeAgent):
        self.agent_registry[agent_id] = agent
    def get_agent(self, agent_id: str) -> Optional[VibeAgent]:
        return self.agent_registry.get(agent_id)

def main():
    print("\n" + "="*70)
    print("🚀 GAD-900: FINAL STRATEGIC LAUNCH")
    print("="*70 + "\n")

    # 1. Initialize System
    kernel = MockKernel()
    envoy = EnvoyCartridge()
    herald = HeraldCartridge()
    civic = CivicCartridge()
    forum = ForumCartridge()
    science = ScienceCartridge()

    kernel.register_agent("envoy", envoy)
    kernel.register_agent("herald", herald)
    kernel.register_agent("civic", civic)
    kernel.register_agent("forum", forum)
    kernel.register_agent("science", science)

    envoy.set_kernel(kernel)
    # Inject kernel into others if they support it
    for agent in [herald, civic, forum, science]:
        if hasattr(agent, 'set_kernel'):
            agent.set_kernel(kernel)

    print("✅ System Online (GAD-000 Compliant)\n")

    # 2. Step 1: The Briefing (Soft Interface)
    print("-" * 50)
    print("🧠 STEP 1: STRATEGIC BRIEFING (HIL Assistant)")
    print("-" * 50)
    
    # Auto-load latest report for context
    task_briefing = Task(
        agent_id="envoy",
        payload={"command": "next_action", "args": {}}
    )
    result_briefing = envoy.process(task_briefing)
    
    if result_briefing.get("status") == "success":
        print(f"\n{result_briefing.get('summary')}\n")
    else:
        print("⚠️  Could not retrieve briefing.")

    # 3. Step 2: The Authorization (HIL Action)
    print("-" * 50)
    print("👤 STEP 2: HIL AUTHORIZATION")
    print("-" * 50)
    print("\n> HIL: \"ENVOY, starte die Kampagne zur Veröffentlichung des G.A.P. Reports...\"")
    print("\n✅ AUTHORIZATION GRANTED. EXECUTING.\n")

    # 4. Step 3: The Execution (Hard Interface)
    print("-" * 50)
    print("⚙️  STEP 3: ORCHESTRATION & EXECUTION (Envoy)")
    print("-" * 50)

    launch_command = "starte die Kampagne zur Veröffentlichung des G.A.P. Reports und skaliere diese Kampagne so kosten-effizient wie möglich auf allen Kanälen. Fokussiere dich auf den Proof, dass Governed Intelligence günstig routet."
    
    task_launch = Task(
        agent_id="envoy",
        payload={
            "command": "campaign",
            "args": {
                "goal": launch_command,
                "campaign_type": "publication",
                "focus": "cost_efficiency_proof"
            }
        }
    )

    result_launch = envoy.process(task_launch)

    print(f"\n📝 Execution Result:\n")
    print(json.dumps(result_launch, indent=2))

    if result_launch.get("status") == "complete":
        print("\n" + "="*70)
        print("🎉 MISSION ACCOMPLISHED: GAD-900 CONTRACT FULFILLED")
        print("="*70)
    else:
        print("\n❌ MISSION FAILED")

if __name__ == "__main__":
    main()
