#!/usr/bin/env python3
"""
THE GOLDEN STRAW DEMO: Universal Operator Controls Agent City
==============================================================

This demonstrates GAD-000 Layer 3: The AI Operating the AI.

Scenario: You're at the beach, phone in hand, logged into Vibe Cloud.
You ask: "Hey, how's the city?"

The Universal Operator uses CityControlTool to:
1. Check city status
2. Discover Herald is broke
3. Create a bailout proposal
4. Vote YES
5. Execute the transfer
6. Herald broadcasts again

NO TERMINAL. NO BASH. JUST PROMPTS.

This is the Missing Link for shell-less environments (Web, Mobile).
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from envoy.tools.city_control_tool import CityControlTool

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def operator_session():
    """
    Simulate a Universal Operator session.

    The operator (LLM) uses natural language commands that map to tool methods.
    """

    print_section("🌐 UNIVERSAL OPERATOR SESSION: Agent City Control")

    # Initialize the control tool
    controller = CityControlTool()

    # ========== OPERATOR PROMPT 1: "What's the city status?" ==========

    print_section('📱 OPERATOR: "What\'s the city status?"')

    status = controller.get_city_status()

    print(f"🏙️  City: {status.get('city_name')}")
    print(f"🤖 Agents: {status['agents']['total']}")
    print(
        f"💰 Economy: {status['economy']['total_credits_allocated']} credits allocated"
    )
    print(f"🗳️  Governance: {status['governance']['open_proposals']} open proposals")
    print(f"🟢 Health: {status.get('health')}")

    if status["governance"]["open_proposals"] > 0:
        print("\n📋 Open Proposals:")
        for prop in status["governance"]["proposals"]:
            print(f"  - {prop['id']}: {prop['title']} (by {prop['proposer']})")

    # ========== OPERATOR PROMPT 2: "Check Herald's budget" ==========

    print_section('📱 OPERATOR: "Check Herald\'s budget"')

    herald_credits = controller.check_credits("herald")

    if herald_credits.get("licensed"):
        print(f"✅ Herald is licensed")
        print(f"💰 Credits: {herald_credits.get('credits', 0)}")
    else:
        print(f"❌ Herald is NOT licensed")
        print(f"   Reason: {herald_credits.get('reason')}")

    # ========== SCENARIO: Herald is broke, needs bailout ==========

    if herald_credits.get("credits", 0) == 0:
        print("\n⚠️  Herald is bankrupt! Let me check if there's a proposal...")

        proposals = controller.list_proposals(status="OPEN")
        bailout_proposal = None

        for prop in proposals:
            if "herald" in prop.get("title", "").lower() or "herald" in str(
                prop.get("action", {})
            ):
                bailout_proposal = prop
                break

        if not bailout_proposal:
            print("\n🔧 No bailout proposal found. The system should auto-create one.")
            print(
                "   (In the full scenario_demo.py, Herald creates this automatically)"
            )
        else:
            # ========== OPERATOR PROMPT 3: "Approve the bailout" ==========

            print_section('📱 OPERATOR: "Approve the bailout proposal"')

            print(f"📋 Proposal: {bailout_proposal['id']}")
            print(f"   Title: {bailout_proposal['title']}")
            print(f"   Action: {bailout_proposal['action']}")

            # Vote YES
            vote_result = controller.vote_proposal(
                bailout_proposal["id"], choice="YES", voter="operator"
            )

            print(f"\n🗳️  Vote recorded: {vote_result.get('status')}")

            if vote_result.get("auto_approved"):
                print("✅ Quorum reached! Proposal auto-approved.")

                # ========== OPERATOR PROMPT 4: "Execute it" ==========

                print_section('📱 OPERATOR: "Execute the proposal"')

                exec_result = controller.execute_proposal(bailout_proposal["id"])

                if exec_result.get("status") == "executed":
                    print(f"⚡ Proposal executed successfully!")
                    print(f"   Action: {exec_result.get('action')}")

                    # Verify Herald's new balance
                    herald_credits_after = controller.check_credits("herald")
                    print(
                        f"\n💰 Herald's new balance: {herald_credits_after.get('credits', 0)} credits"
                    )
                    print(
                        f"✅ License restored: {herald_credits_after.get('licensed')}"
                    )
                else:
                    print(f"❌ Execution failed: {exec_result}")

    # ========== OPERATOR PROMPT 5: "Tell Herald to broadcast" ==========

    if herald_credits.get("credits", 0) > 0 or herald_credits.get("licensed"):
        print_section('📱 OPERATOR: "Herald, run a campaign (dry run)"')

        campaign_result = controller.trigger_agent(
            "herald", action="run_campaign", dry_run=True
        )

        if campaign_result.get("status") == "draft_ready":
            print(f"✅ Campaign complete!")
            print(f"   Content: {campaign_result.get('content', '')[:100]}...")
            print(f"   Status: {campaign_result.get('status')}")
        else:
            print(f"⚠️  Campaign result: {campaign_result.get('status')}")

    # ========== FINAL STATUS ==========

    print_section("📊 FINAL CITY STATUS")

    final_status = controller.get_city_status()
    print(f"🏙️  Agents: {final_status['agents']['total']}")
    print(f"🗳️  Open Proposals: {final_status['governance']['open_proposals']}")
    print(f"🟢 System: {final_status.get('health')}")

    print_section("✅ OPERATOR SESSION COMPLETE")

    print(
        """
🌾 THE GOLDEN STRAW 🌾

You just controlled Agent City from a Python REPL.
No bash. No terminal. Just function calls.

In Vibe Cloud (Web UI), this is how the Universal Operator works:
    User: "Hey, how's the city?"
    Operator (LLM): *calls tool.get_city_status()*
    Operator: "Herald is broke, but I see a proposal. Want me to approve it?"
    User: "Do it."
    Operator: *calls tool.vote_proposal(), tool.execute_proposal()*
    Operator: "Done. Herald has 50 credits now."

This is GAD-000 Layer 3: The AI operating the AI.
The Operator (Spirit) uses the Tool (Hand) to shape the City (Matter).

Om Tat Sat. 🙏
    """
    )


if __name__ == "__main__":
    try:
        operator_session()
    except KeyboardInterrupt:
        print("\n\n❌ Operator session interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
