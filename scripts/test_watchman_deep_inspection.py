#!/usr/bin/env python3
"""
Test Watchman Deep Inspection (Phase 3.2)
==========================================

Tests that Watchman can perform AST-based deep analysis to detect
architectural violations that simple grep cannot catch.

Tests:
1. Watchman boots with StandardsInspectionTool
2. Deep inspection runs without errors
3. Report is generated with proper structure
4. Violations are detected and categorized
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.watchman.cartridge_main import WatchmanCartridge
from vibe_core.scheduling.task import Task


def test_watchman_deep_inspection():
    """Test Watchman deep inspection mechanism (Phase 3.2)."""

    print("🧪 Watchman Deep Inspection Test (Phase 3.2)")
    print("=" * 70)

    # Step 1: Create Kernel
    print("\n1️⃣  Creating kernel...")
    try:
        kernel = RealVibeKernel(ledger_path=":memory:")
        print("   ✅ Kernel created")
    except Exception as e:
        print(f"   ❌ Kernel creation failed: {e}")
        return False

    # Step 2: Create and register Watchman
    print("\n2️⃣  Registering Watchman...")
    try:
        watchman = WatchmanCartridge()
        kernel.register_agent(watchman)
        print("   ✅ Watchman registered")
    except Exception as e:
        print(f"   ❌ Watchman registration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 3: Verify StandardsInspectionTool is initialized
    print("\n3️⃣  Verifying StandardsInspectionTool...")
    if hasattr(watchman, "standards_tool"):
        print(f"   ✅ StandardsInspectionTool initialized")
    else:
        print(f"   ❌ StandardsInspectionTool NOT found")
        return False

    # Step 4: Run deep inspection
    print("\n4️⃣  Running deep inspection...")
    try:
        task = Task(
            task_id="test_deep_inspection",
            agent_id="watchman",
            priority=1,
            payload={"action": "deep_inspection"},
        )

        result = watchman.process(task)

        if result.get("status") in [
            "COMPLIANT",
            "WARNINGS_DETECTED",
            "VIOLATIONS_DETECTED",
        ]:
            print(f"   ✅ Deep inspection completed")
            print(f"   Status: {result.get('status')}")
            print(f"   Total violations: {result.get('total_violations', 0)}")
            print(f"   Critical count: {result.get('critical_count', 0)}")
        else:
            print(f"   ❌ Deep inspection failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"   ❌ Deep inspection crashed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 5: Verify report structure
    print("\n5️⃣  Verifying report structure...")
    if "report" in result:
        report = result["report"]
        required_keys = [
            "total_violations",
            "by_severity",
            "by_agent",
            "should_fail_build",
        ]

        missing_keys = [k for k in required_keys if k not in report]
        if missing_keys:
            print(f"   ❌ Report missing keys: {missing_keys}")
            return False

        print(f"   ✅ Report structure valid")
        print(f"   📊 By severity: {report['by_severity']}")
        print(f"   📊 By agent: {report['by_agent']}")
    else:
        print(f"   ❌ No report in result")
        return False

    # Step 6: Display violations (if any)
    if result.get("total_violations", 0) > 0:
        print("\n6️⃣  Violations found:")
        violations = result.get("violations", [])

        # Group by agent
        by_agent = {}
        for v in violations:
            agent_id = v["agent_id"]
            if agent_id not in by_agent:
                by_agent[agent_id] = []
            by_agent[agent_id].append(v)

        for agent_id, agent_violations in by_agent.items():
            print(f"\n   Agent: {agent_id} ({len(agent_violations)} violation(s))")
            for v in agent_violations[:3]:  # Show first 3
                print(f"     • [{v['severity']}] {v['message']}")
                print(f"       File: {v['file_path']}:{v['line_number']}")
    else:
        print("\n6️⃣  ✅ No violations found - System compliant!")

    print("\n" + "=" * 70)
    print("✅ Phase 3.2 Watchman Deep Inspection: ALL TESTS PASSED")
    print("=" * 70)
    print("\n📋 Summary:")
    print("   • Watchman boots with StandardsInspectionTool")
    print("   • Deep inspection runs successfully")
    print("   • Report structure is valid")
    print("   • Violations are properly categorized")
    print(f"   • Status: {result.get('status')}")

    return True


if __name__ == "__main__":
    success = test_watchman_deep_inspection()
    sys.exit(0 if success else 1)
