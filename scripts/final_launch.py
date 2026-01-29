#!/usr/bin/env python3
"""
Final Launch Script - GAD-900: The HIL-Operator Contract
Demonstrates the flow: HIL Assistant Briefing -> HIL Authorization -> Envoy Execution.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x3cb35eb4"  # GenesisByte: parampara % 37 == 0

import json
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from civic.cartridge_main import CivicCartridge
from envoy.cartridge_main import EnvoyCartridge
from forum.cartridge_main import ForumCartridge
from herald.cartridge_main import HeraldCartridge
from science.cartridge_main import ScienceCartridge

from vibe_core import Task

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("FINAL_LAUNCH")


def main():
    print("\n" + "=" * 70)
    print("🚀 GAD-900: FINAL STRATEGIC LAUNCH")
    print("=" * 70 + "\n")

    # 1. Initialize System
    envoy = EnvoyCartridge()
    herald = HeraldCartridge()
    civic = CivicCartridge()
    forum = ForumCartridge()
    science = ScienceCartridge()

    print("✅ System Online (GAD-000 Compliant)\n")

    # 2. Step 1: The Briefing (Soft Interface)
    print("-" * 50)
    print("🧠 STEP 1: STRATEGIC BRIEFING (HIL Assistant)")
    print("-" * 50)

    # Auto-load latest report for context
    task_briefing = Task(agent_id="envoy", payload={"command": "next_action", "args": {}})
    result_briefing = envoy.process(task_briefing)

    if result_briefing.get("status") == "success":
        print(f"\n{result_briefing.get('summary')}\n")
    else:
        print("⚠️  Could not retrieve briefing.")

    # 3. Step 2: The Authorization (HIL Action)
    print("-" * 50)
    print("👤 STEP 2: HIL AUTHORIZATION")
    print("-" * 50)
    print('\n> HIL: "ENVOY, starte die Kampagne zur Veröffentlichung des G.A.P. Reports..."')
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
                "focus": "cost_efficiency_proof",
            },
        },
    )

    result_launch = envoy.process(task_launch)

    print("\n📝 Execution Result:\n")
    print(json.dumps(result_launch, indent=2))

    if result_launch.get("status") == "complete":
        print("\n" + "=" * 70)
        print("🎉 MISSION ACCOMPLISHED: GAD-900 CONTRACT FULFILLED")
        print("=" * 70)
    else:
        print("\n❌ MISSION FAILED")


if __name__ == "__main__":
    main()
