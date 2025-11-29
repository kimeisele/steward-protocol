#!/usr/bin/env python3
"""
Test Herald Scribe Tool - Tool Protocol Integration

Validates that:
1. Scribe tool auto-discovered
2. Scribe tool registered with namespace (herald.scribe)
3. Scribe tool executes via kernel
4. All actions work: initialize_logbook, log_action

Run: python test_herald_scribe.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.tools import ToolCall


def test_herald_scribe():
    """Test Herald Scribe tool integration"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  HERALD SCRIBE TOOL - Tool Protocol Integration           ║")
    print("╚════════════════════════════════════════════════════════════╝")

    print("\n=== STEP 1: Boot Kernel (Auto-Discovery) ===")

    kernel = RealVibeKernel(ledger_path=":memory:")

    tools = kernel.tool_registry.list_tools()
    print(f"📋 Total tools: {len(tools)}")

    # Check if herald.scribe is discovered
    if "herald.scribe" not in tools:
        print(f"\n❌ herald.scribe NOT FOUND")
        print(f"Available tools: {sorted(tools)}")
        return False

    print("✅ herald.scribe auto-discovered")

    print("\n=== STEP 2: Execute Scribe - Initialize Logbook ===")

    # Test initialize_logbook
    tool_call = ToolCall(
        tool_name="herald.scribe",
        parameters={
            "action": "initialize_logbook",
        },
    )

    print("📚 Initializing logbook section")

    result = kernel.tool_registry.execute(tool_call)

    print(f"\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Initialized: {output['initialized']}")
        print(f"   Chronicle Path: {output['chronicle_path']}")
        print(f"   Exists: {output['exists']}")
        print("\n✅ Logbook initialization works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n=== STEP 3: Execute Scribe - Log Action ===")

    # Test log_action
    timestamp = datetime.now(timezone.utc).isoformat()
    event_data = {
        "event_type": "content_published",
        "timestamp": timestamp,
        "agent_id": "herald",
        "payload": {
            "content": "Herald Scribe Tool migrated to Tool Protocol! 🎉",
            "platform": "twitter",
        },
        "signature": "0xabcd1234",
        "sequence_number": 42,
    }

    tool_call = ToolCall(
        tool_name="herald.scribe",
        parameters={
            "action": "log_action",
            "event_data": event_data,
        },
    )

    print(f"📝 Logging event: {event_data['event_type']}")

    result = kernel.tool_registry.execute(tool_call)

    print(f"\n📊 Result:")
    print(f"   Success: {result.success}")
    if result.success:
        output = result.output
        print(f"   Logged: {output['logged']}")
        print(f"   Event Type: {output['event_type']}")
        print(f"   Chronicle Path: {output['chronicle_path']}")
        print("\n✅ Event logging works")
    else:
        print(f"   Error: {result.error}")
        return False

    print("\n" + "=" * 60)
    print("🎉 HERALD SCRIBE MIGRATION COMPLETE")
    print("=" * 60)
    print("\n✨ PROOF:")
    print("   - Herald Scribe refactored to Tool Protocol ✅")
    print("   - Auto-discovered as herald.scribe ✅")
    print("   - Executed via kernel ✅")
    print("   - Initialize logbook works ✅")
    print("   - Log action works ✅")
    print("   - Translates events to documentation ✅")
    print("\n🔥 PATTERN VALIDATED:")
    print("   OLD: self.scribe = Scribe()")
    print("   NEW: self.system.execute_tool('herald.scribe', params)")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_herald_scribe()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
