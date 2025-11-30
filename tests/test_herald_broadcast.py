#!/usr/bin/env python3
"""
Test Herald Broadcast Tool - Tool Protocol Integration

Validates that:
1. Broadcast tool auto-discovered
2. Broadcast tool registered with namespace (herald.broadcast)
3. Broadcast tool executes via kernel
4. All actions work: publish, scan_mentions, reply, verify_credentials

Run: python test_herald_broadcast.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.tools import ToolCall


def test_herald_broadcast():
    """Test Herald Broadcast tool integration"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  HERALD BROADCAST TOOL - Tool Protocol Integration        ║")
    print("╚════════════════════════════════════════════════════════════╝")

    print("\n=== STEP 1: Boot Kernel (Auto-Discovery) ===")

    kernel = RealVibeKernel(ledger_path=":memory:")

    tools = kernel.tool_registry.list_tools()
    print(f"📋 Total tools: {len(tools)}")

    # Check if herald.broadcast is discovered
    if "herald.broadcast" not in tools:
        print("\n❌ herald.broadcast NOT FOUND")
        print(f"Available tools: {tools}")
        return False

    print("✅ herald.broadcast auto-discovered")

    print("\n=== STEP 2: Execute Broadcast - Verify Credentials ===")

    # Test verify_credentials
    tool_call = ToolCall(
        tool_name="herald.broadcast",
        parameters={
            "action": "verify_credentials",
            "platform": "twitter",
        },
    )

    print("🔐 Verifying Twitter credentials")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Platform: {output['platform']}")
        print(f"   Verified: {output['verified']}")
        print(f"   Status: {output['status']}")
        print("\n✅ Credential verification works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 3: Execute Broadcast - Publish (Simulation) ===")

    # Test publish
    tool_call = ToolCall(
        tool_name="herald.broadcast",
        parameters={
            "action": "publish",
            "content": "🎉 Herald Broadcast Tool migrated to Tool Protocol! Auto-discovery FTW! 🚀",
            "platform": "twitter",
        },
    )

    print("📢 Publishing test tweet (simulation mode)")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Published: {output['published']}")
        print(f"   Platform: {output['platform']}")
        print(f"   Preview: {output['content_preview']}")

        # Verify it succeeded (even in simulation)
        if not output["published"]:
            print("\n❌ Publish failed")
            return False

        print("\n✅ Publish works (simulation)")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 4: Execute Broadcast - Scan Mentions ===")

    # Test scan_mentions
    tool_call = ToolCall(
        tool_name="herald.broadcast",
        parameters={
            "action": "scan_mentions",
            "platform": "twitter",
        },
    )

    print("🔍 Scanning for mentions")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Platform: {output['platform']}")
        print(f"   Mention Count: {output['count']}")
        print(f"   Mentions: {output['mentions']}")
        print("\n✅ Scan mentions works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 5: Execute Broadcast - Reply (Simulation) ===")

    # Test reply
    tool_call = ToolCall(
        tool_name="herald.broadcast",
        parameters={
            "action": "reply",
            "tweet_id": "123456789",
            "content": "Thanks for reaching out! 🤖",
        },
    )

    print("💬 Replying to tweet (simulation mode)")

    result = kernel.tool_registry.execute(tool_call)

    print("\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Replied: {output['replied']}")
        print(f"   Tweet ID: {output['tweet_id']}")
        print(f"   Preview: {output['content_preview']}")

        # Verify it succeeded (even in simulation)
        if not output["replied"]:
            print("\n❌ Reply failed")
            return False

        print("\n✅ Reply works (simulation)")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n" + "=" * 60)
    print("🎉 HERALD BROADCAST MIGRATION COMPLETE")
    print("=" * 60)
    print("\n✨ PROOF:")
    print("   - Herald Broadcast refactored to Tool Protocol ✅")
    print("   - Auto-discovered as herald.broadcast ✅")
    print("   - Executed via kernel ✅")
    print("   - Verify credentials works ✅")
    print("   - Publish works (simulation) ✅")
    print("   - Scan mentions works ✅")
    print("   - Reply works (simulation) ✅")
    print("\n🔥 PATTERN VALIDATED:")
    print("   OLD: self.broadcast = BroadcastTool()")
    print("   NEW: self.system.execute_tool('herald.broadcast', params)")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_herald_broadcast()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
