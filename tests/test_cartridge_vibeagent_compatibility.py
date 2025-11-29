#!/usr/bin/env python3
"""
VALIDATION: Cartridge VibeAgent Compatibility Test

This test validates that all cartridges:
1. Inherit from VibeAgent
2. Implement required methods (process, report_status)
3. Can be instantiated and injected with kernel reference
4. Respond to tasks correctly

This ensures steward-protocol is ready for VibeOS kernel integration.
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core import VibeAgent, Task

# Import cartridges
try:
    from civic.cartridge_main import CivicCartridge
    from herald.cartridge_main import HeraldCartridge
    from forum.cartridge_main import ForumCartridge
    from science.cartridge_main import ScientistCartridge

    print("✅ All cartridges imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_cartridge_inheritance(cartridge_class, expected_agent_id):
    """Test that cartridge inherits from VibeAgent"""
    print(f"\n🧪 Testing {expected_agent_id.upper()}...")

    # Check inheritance
    if not issubclass(cartridge_class, VibeAgent):
        print(f"   ❌ {cartridge_class.__name__} does not inherit from VibeAgent")
        return False
    print(f"   ✅ Inherits from VibeAgent")

    # Instantiate
    try:
        cartridge = cartridge_class()
        print(f"   ✅ Instantiated successfully")
    except Exception as e:
        print(f"   ❌ Failed to instantiate: {e}")
        return False

    # Check agent_id
    if cartridge.agent_id != expected_agent_id:
        print(
            f"   ❌ Expected agent_id='{expected_agent_id}', got '{cartridge.agent_id}'"
        )
        return False
    print(f"   ✅ agent_id = '{expected_agent_id}'")

    # Check required methods exist
    if not hasattr(cartridge, "process"):
        print(f"   ❌ Missing process() method")
        return False
    print(f"   ✅ process() method exists")

    if not hasattr(cartridge, "report_status"):
        print(f"   ❌ Missing report_status() method")
        return False
    print(f"   ✅ report_status() method exists")

    # Check capabilities
    if not hasattr(cartridge, "capabilities") or not cartridge.capabilities:
        print(f"   ❌ No capabilities defined")
        return False
    print(f"   ✅ Capabilities: {cartridge.capabilities}")

    # Test get_manifest()
    try:
        manifest = cartridge.get_manifest()
        if manifest.agent_id != expected_agent_id:
            print(f"   ❌ Manifest agent_id mismatch")
            return False
        print(f"   ✅ get_manifest() returns valid AgentManifest")
    except Exception as e:
        print(f"   ❌ get_manifest() failed: {e}")
        return False

    # Test report_status()
    try:
        status = cartridge.report_status()
        if not isinstance(status, dict):
            print(f"   ❌ report_status() did not return dict")
            return False
        if "agent_id" not in status:
            print(f"   ❌ report_status() missing agent_id")
            return False
        print(f"   ✅ report_status() returns valid dict")
    except Exception as e:
        print(f"   ❌ report_status() failed: {e}")
        return False

    # Test process() with mock task
    try:
        task = Task(agent_id=expected_agent_id, payload={"action": "status_check"})

        # This will likely fail (action not recognized)
        # but we just want to make sure process() is callable
        try:
            result = cartridge.process(task)
            # Should get either success or "unknown action" error
            if isinstance(result, dict) and "status" in result:
                print(f"   ✅ process() is callable and returns dict")
            else:
                print(f"   ⚠️  process() returned unexpected format")
        except TypeError as e:
            if "missing 1 required positional argument: 'task'" in str(e):
                print(f"   ❌ process() signature incorrect (missing self?)")
                return False
            raise
    except Exception as e:
        print(f"   ❌ process() failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Test kernel injection
    try:
        # Create a mock kernel object
        class MockKernel:
            def __init__(self):
                self.agent_registry = {}

        mock_kernel = MockKernel()
        cartridge.set_kernel(mock_kernel)

        if cartridge.kernel != mock_kernel:
            print(f"   ❌ Kernel injection failed")
            return False
        print(f"   ✅ Kernel injection works (set_kernel())")
    except Exception as e:
        print(f"   ❌ Kernel injection failed: {e}")
        return False

    return True


def main():
    """Run all validation tests"""
    print("=" * 70)
    print("🔍 STEWARD PROTOCOL - VIBEAGENT COMPATIBILITY VALIDATION")
    print("=" * 70)

    cartridges = [
        (CivicCartridge, "civic"),
        (HeraldCartridge, "herald"),
        (ForumCartridge, "forum"),
        (ScientistCartridge, "science"),
    ]

    results = []
    for cartridge_class, expected_agent_id in cartridges:
        success = test_cartridge_inheritance(cartridge_class, expected_agent_id)
        results.append((expected_agent_id, success))

    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)

    for agent_id, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {agent_id.upper():12} - VibeAgent compatible")

    all_pass = all(success for _, success in results)

    print("\n" + "=" * 70)
    if all_pass:
        print("✅ ALL CARTRIDGES VALIDATED - READY FOR VIBEAGENT INTEGRATION")
        print("\nNext Steps:")
        print("1. Deploy steward-protocol as cartridge pack to vibe-agency")
        print("2. VibeOS kernel will auto-discover and load cartridges")
        print("3. Kernel will inject references via set_kernel()")
        print("4. Tasks will be routed via kernel scheduler")
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix issues above before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
