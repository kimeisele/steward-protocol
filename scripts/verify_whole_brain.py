#!/usr/bin/env python3
"""
Verify Operation Whole Brain
Checks if ENVOY and SCIENCE are correctly migrated to ContextAwareAgent
and if tools have DegradationChain injected.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.agents.context_aware_agent import ContextAwareAgent
from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge
from vibe_core.cartridges.system.science.cartridge_main import ScientistCartridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_BRAIN")


def verify_agent(agent_class, agent_name, tool_checks):
    print(f"\n🧠 Verifying {agent_name}...")

    try:
        agent = agent_class()

        # 1. Check Inheritance
        if isinstance(agent, ContextAwareAgent):
            print(f"✅ {agent_name} inherits ContextAwareAgent")
        else:
            print(f"❌ {agent_name} does NOT inherit ContextAwareAgent")
            return False

        # 2. Check DegradationChain
        chain = agent.get_degradation_chain()
        if chain:
            print(f"✅ {agent_name} has DegradationChain (Level: {chain.current_level.value})")
        else:
            print(f"❌ {agent_name} missing DegradationChain")
            return False

        # 3. Check Tool Injection
        for tool_name, tool_attr in tool_checks.items():
            tool = getattr(agent, tool_attr)
            if hasattr(tool, "chain") and tool.chain is not None:
                print(f"✅ Tool '{tool_name}' has chain injected")
            elif hasattr(tool, "_degradation_chain") and tool._degradation_chain is not None:  # For mixin
                print(f"✅ Tool '{tool_name}' has chain injected (Mixin)")
            else:
                # Check if it was assigned to self.chain in __init__ as per our changes
                if hasattr(tool, "chain") and tool.chain == chain:
                    print(f"✅ Tool '{tool_name}' has chain injected")
                else:
                    print(f"❌ Tool '{tool_name}' missing chain injection")
                    return False

        return agent

    except Exception as e:
        print(f"❌ Error verifying {agent_name}: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_science_fallback(scientist):
    print("\n🔬 Verifying SCIENCE Offline Fallback...")

    # Force offline mode
    scientist.search.mode = "offline"
    print("   Forced Search Mode: OFFLINE")

    query = "What is the capital of France?"
    print(f"   Query: '{query}'")

    results = scientist.search.search(query)

    if results and results[0].source == "local_llm":
        print("✅ Fallback successful!")
        print(f"   Source: {results[0].source}")
        print(f"   Content: {results[0].content[:100]}...")
        return True
    else:
        print("❌ Fallback failed")
        print(f"   Results: {results}")
        return False


def main():
    print("🔌 OPERATION WHOLE BRAIN - VERIFICATION")
    print("=======================================")

    # Verify ENVOY
    envoy = verify_agent(EnvoyCartridge, "ENVOY", {"Diplomacy": "diplomacy", "Curator": "curator"})
    if not envoy:
        return 1

    # Verify SCIENCE
    science = verify_agent(ScientistCartridge, "SCIENCE", {"WebSearch": "search"})
    if not science:
        return 1

    # Verify Science Fallback
    if not verify_science_fallback(science):
        return 1

    print("\n✨ ALL SYSTEMS GREEN - BRAIN IS WHOLE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
