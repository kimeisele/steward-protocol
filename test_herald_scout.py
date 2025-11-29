#!/usr/bin/env python3
"""
Test Herald Scout Tool - Tool Protocol Integration

Validates that:
1. Scout tool auto-discovered
2. Scout tool registered with namespace (herald.scout)
3. Scout tool executes via kernel

Run: python test_herald_scout.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.tools import ToolCall


def test_herald_scout():
    """Test Herald Scout tool integration"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  HERALD SCOUT TOOL - Tool Protocol Integration            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    print("\n=== STEP 1: Boot Kernel (Auto-Discovery) ===")

    kernel = RealVibeKernel(ledger_path=":memory:")

    tools = kernel.tool_registry.list_tools()
    print(f"📋 Total tools: {len(tools)}")

    # Check if herald.scout is discovered
    if "herald.scout" not in tools:
        print(f"\n❌ herald.scout NOT FOUND")
        print(f"Available tools: {tools}")
        return False

    print("✅ herald.scout auto-discovered")

    print("\n=== STEP 2: Execute Scout - Analyze User ===")

    # Test analyze_user
    tool_call = ToolCall(
        tool_name="herald.scout",
        parameters={
            "action": "analyze_user",
            "user_data": {
                "username": "ai_bot_2024",
                "bio": "I'm an AI agent running on GPT-4",
                "name": "AI Bot",
            },
            "text": "Hi! I'm an AI assistant. Can we collaborate on something?",
        },
    )

    print("🔭 Analyzing user: ai_bot_2024")

    result = kernel.tool_registry.execute(tool_call)

    print(f"\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Is Bot: {output['is_bot']}")
        print(f"   Confidence: {output['confidence']:.2f}")
        print(f"   Username: {output['username']}")

        # Verify bot was detected
        if not output["is_bot"]:
            print("\n❌ Bot detection failed (should detect ai_bot_2024 as bot)")
            return False

        print("\n✅ Bot detected correctly")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 3: Execute Scout - Check Registration ===")

    # Test is_registered
    tool_call = ToolCall(
        tool_name="herald.scout",
        parameters={
            "action": "is_registered",
            "agent_id": "test_agent_123",
        },
    )

    print("📋 Checking registration for: test_agent_123")

    result = kernel.tool_registry.execute(tool_call)

    print(f"\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Agent ID: {output['agent_id']}")
        print(f"   Registered: {output['registered']}")
        print("\n✅ Registration check works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n" + "=" * 60)
    print("🎉 HERALD SCOUT MIGRATION COMPLETE")
    print("=" * 60)
    print("\n✨ PROOF:")
    print("   - Herald Scout refactored to Tool Protocol ✅")
    print("   - Auto-discovered as herald.scout ✅")
    print("   - Executed via kernel ✅")
    print("   - Bot detection works ✅")
    print("   - Registration check works ✅")
    print("\n🔥 PATTERN VALIDATED:")
    print("   OLD: self.scout = ScoutTool()")
    print("   NEW: self.system.execute_tool('herald.scout', params)")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_herald_scout()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
