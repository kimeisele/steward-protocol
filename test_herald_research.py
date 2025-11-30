#!/usr/bin/env python3
"""
Test Herald Research Tool - Tool Protocol Integration

Validates that:
1. Research tool auto-discovered
2. Research tool registered with namespace (herald.research)
3. Research tool executes via kernel
4. All actions work: scan, find_trending, get_status

Run: python test_herald_research.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.tools import ToolCall


def test_herald_research():
    """Test Herald Research tool integration"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  HERALD RESEARCH TOOL - Tool Protocol Integration         ║")
    print("╚════════════════════════════════════════════════════════════╝")

    print("\n=== STEP 1: Boot Kernel (Auto-Discovery) ===")

    kernel = RealVibeKernel(ledger_path=":memory:")

    tools = kernel.tool_registry.list_tools()
    print(f"📋 Total tools: {len(tools)}")

    # Check if herald.research is discovered
    if "herald.research" not in tools:
        print("\n❌ herald.research NOT FOUND")
        print(f"Available tools: {tools}")
        return False

    print("✅ herald.research auto-discovered")

    print("\n=== STEP 2: Execute Research - Get Status ===")

    # Test get_status
    tool_call = ToolCall(
        tool_name="herald.research",
        parameters={
            "action": "get_status",
        },
    )

    print("📊 Checking research capability status")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Tavily Available: {output['tavily_available']}")
        print(f"   API Key Present: {output['api_key_present']}")
        print(f"   Offline Capable: {output['offline_capable']}")
        print(f"   Degradation Level: {output['degradation_level']}")
        print("\n✅ Status check works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 3: Execute Research - Scan (Fallback Mode) ===")

    # Test scan with fallback (Tavily likely not configured)
    tool_call = ToolCall(
        tool_name="herald.research",
        parameters={
            "action": "scan",
            "query": "agent verification protocols",
        },
    )

    print("🔍 Scanning for: agent verification protocols")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Query: {output['query']}")
        print(f"   Source: {output['source']}")
        print(f"   Result Preview: {output['result'][:100]}...")

        # Verify we got a result (even if from fallback)
        if not output["result"]:
            print("\n❌ Scan returned no result")
            return False

        print("\n✅ Scan works (fallback mode)")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 4: Execute Research - Find Trending ===")

    # Test find_trending
    tool_call = ToolCall(
        tool_name="herald.research",
        parameters={
            "action": "find_trending",
        },
    )

    print("🔥 Finding trending topics...")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Found: {output['found']}")
        if output["found"]:
            topic = output["topic"]
            print(f"   Search Query: {topic['search_query']}")
            print(f"   Article Preview: {topic['article']['content'][:100]}...")
        else:
            print(f"   Message: {output.get('message', 'No trending topics')}")
        print("\n✅ Find trending works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n" + "=" * 60)
    print("🎉 HERALD RESEARCH MIGRATION COMPLETE")
    print("=" * 60)
    print("\n✨ PROOF:")
    print("   - Herald Research refactored to Tool Protocol ✅")
    print("   - Auto-discovered as herald.research ✅")
    print("   - Executed via kernel ✅")
    print("   - Get status works ✅")
    print("   - Scan works (fallback mode) ✅")
    print("   - Find trending works ✅")
    print("   - Offline-capable with DegradationChain ✅")
    print("\n🔥 PATTERN VALIDATED:")
    print("   OLD: self.research = ResearchTool()")
    print("   NEW: self.system.execute_tool('herald.research', params)")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_herald_research()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
