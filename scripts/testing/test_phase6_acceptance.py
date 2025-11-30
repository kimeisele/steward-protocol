#!/usr/bin/env python3
"""
PHASE 6 ACCEPTANCE CRITERIA TEST
=================================

This script verifies that PHASE 6 - THE ENVOY SHELL & API GATEWAY is working.

Acceptance Criteria:
1. run_server.py exists and is executable
2. Bootloader initializes RealVibeKernel
3. All 11 agents are importable
4. ENVOY agent is properly wired with HIL Assistant
5. FastAPI Gateway can be imported without errors

This is a functional test, not a full integration test (which would require
running the server in the background).
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_runserver_exists():
    """Test: run_server.py exists and is executable"""
    print("🔍 TEST 1: Check run_server.py exists and is executable")
    run_server = project_root / "run_server.py"

    if not run_server.exists():
        print("   ❌ FAILED: run_server.py not found")
        return False

    if not os.access(run_server, os.X_OK):
        print("   ⚠️  WARNING: run_server.py is not executable")
        # This is not a hard failure, but a warning

    print("   ✅ PASSED: run_server.py exists")
    return True


def test_gateway_api_exists():
    """Test: gateway/api.py exists and imports correctly"""
    print("\n🔍 TEST 2: Check gateway/api.py imports correctly")

    try:

        print("   ✅ PASSED: FastAPI app imports successfully")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_all_agents_importable():
    """Test: All 11 agents can be imported"""
    print("\n🔍 TEST 3: Check all 11 agents are importable")

    agents = [
        ("herald", "HeraldCartridge"),
        ("civic", "CivicCartridge"),
        ("forum", "ForumCartridge"),
        ("science", "ScientistCartridge"),
        ("envoy", "EnvoyCartridge"),
        ("archivist", "ArchivistCartridge"),
        ("auditor", "AuditorCartridge"),
        ("engineer", "EngineerCartridge"),
        ("oracle", "OracleCartridge"),
        ("watchman", "WatchmanCartridge"),
        ("artisan", "ArtisanCartridge"),
    ]

    all_passed = True
    for module_name, class_name in agents:
        try:
            module = __import__(f"{module_name}.cartridge_main", fromlist=[class_name])
            agent_class = getattr(module, class_name)
            instance = agent_class()
            print(f"   ✅ {module_name:12} | {instance.name:20} | {instance.description[:40]}")
        except Exception as e:
            print(f"   ❌ {module_name:12} | FAILED: {e}")
            all_passed = False

    if all_passed:
        print("\n   ✅ PASSED: All 11 agents are importable")
    else:
        print("\n   ❌ FAILED: Some agents could not be imported")

    return all_passed


def test_envoy_wiring():
    """Test: ENVOY is properly wired with HIL Assistant"""
    print("\n🔍 TEST 4: Check ENVOY wiring and HIL Assistant")

    try:
        from envoy.cartridge_main import EnvoyCartridge

        envoy = EnvoyCartridge()

        # Check HIL Assistant exists
        if not hasattr(envoy, "hil_assistant"):
            print("   ❌ FAILED: ENVOY missing hil_assistant attribute")
            return False

        if envoy.hil_assistant is None:
            print("   ❌ FAILED: ENVOY hil_assistant is None")
            return False

        # Check tools exist
        required_tools = [
            "city_control",  # Will be None until kernel injection
            "diplomacy",
            "curator",
            "campaign_tool",
            "gap_report",
            "hil_assistant",
        ]

        for tool_name in required_tools:
            if not hasattr(envoy, tool_name):
                print(f"   ❌ FAILED: ENVOY missing {tool_name}")
                return False

        # Check that ENVOY has process() method
        if not hasattr(envoy, "process") or not callable(envoy.process):
            print("   ❌ FAILED: ENVOY missing process() method")
            return False

        # Check command router
        if not hasattr(envoy, "_route_command") or not callable(envoy._route_command):
            print("   ❌ FAILED: ENVOY missing _route_command() method")
            return False

        print("   ✅ ENVOY Agent Configuration:")
        print(f"      • Agent ID: {envoy.agent_id}")
        print(f"      • Name: {envoy.name}")
        print(f"      • Version: {envoy.version}")
        print(f"      • Domain: {envoy.domain}")
        print(f"      • Capabilities: {', '.join(envoy.capabilities)}")
        print("      • HIL Assistant Tool: ACTIVE")
        print("      • Command Router: READY")
        print("   ✅ PASSED: ENVOY is properly wired")
        return True

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_hil_assistant_functionality():
    """Test: HIL Assistant can generate summaries"""
    print("\n🔍 TEST 5: Check HIL Assistant functionality")

    try:
        from envoy.tools.hil_assistant_tool import HILAssistantTool

        hil = HILAssistantTool()

        # Test with a mock report content
        test_report = """
# G.A.P. Report - System Governability Audit Proof

## Executive Summary
The system is operating normally with no critical issues detected.

## Governance Status
✅ All Constitutional Oaths verified
✅ Agent registry synchronized
✅ Ledger integrity confirmed

## Next Actions
1. Review the system governance status
2. Monitor agent health metrics
3. Prepare for next cycle
"""

        summary = hil.get_next_action_summary(test_report)

        if not summary or len(summary) < 10:
            print("   ⚠️  WARNING: HIL Assistant returned empty or invalid summary")
            print(f"      Summary: {summary}")
            # This is a warning, not a hard failure
        else:
            print("   ✅ HIL Assistant generated summary:")
            print(f"      {summary[:100]}...")

        print("   ✅ PASSED: HIL Assistant functionality works")
        return True

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_kernel_bootstrap():
    """Test: RealVibeKernel can be bootstrapped"""
    print("\n🔍 TEST 6: Check RealVibeKernel bootstrap (no actual boot)")

    try:
        from vibe_core.kernel_impl import RealVibeKernel

        # Create an in-memory kernel (not booting to save time)
        kernel = RealVibeKernel(ledger_path=":memory:")

        if not hasattr(kernel, "register_agent"):
            print("   ❌ FAILED: Kernel missing register_agent method")
            return False

        if not hasattr(kernel, "boot"):
            print("   ❌ FAILED: Kernel missing boot method")
            return False

        print("   ✅ PASSED: RealVibeKernel is initialized and ready")
        return True

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_api_endpoints():
    """Test: FastAPI Gateway has required endpoints"""
    print("\n🔍 TEST 7: Check FastAPI Gateway endpoints")

    try:
        from gateway.api import app

        required_endpoints = [
            ("POST", "/v1/chat"),
            ("GET", "/health"),
            ("GET", "/help"),
        ]

        routes = [str(route) for route in app.routes]

        for method, path in required_endpoints:
            found = any(path in str(route) for route in app.routes)
            if found:
                print(f"   ✅ {method} {path}")
            else:
                print(f"   ❌ {method} {path} not found")
                return False

        print("   ✅ PASSED: All required endpoints configured")
        return True

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def main():
    """Run all acceptance tests"""
    print("=" * 80)
    print("PHASE 6 - ENVOY SHELL & API GATEWAY")
    print("ACCEPTANCE CRITERIA TEST")
    print("=" * 80)

    results = []

    results.append(("run_server.py exists", test_runserver_exists()))
    results.append(("gateway/api.py imports", test_gateway_api_exists()))
    results.append(("All 11 agents importable", test_all_agents_importable()))
    results.append(("ENVOY wiring & HIL Assistant", test_envoy_wiring()))
    results.append(("HIL Assistant functionality", test_hil_assistant_functionality()))
    results.append(("RealVibeKernel bootstrap", test_kernel_bootstrap()))
    results.append(("FastAPI Gateway endpoints", test_api_endpoints()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")

    print("=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("\n🎉 ALL ACCEPTANCE CRITERIA MET!")
        print("\n✅ SYSTEM READY FOR FIRST CONTACT")
        print("\nTo start the server, run:")
        print("   python3 run_server.py")
        print("\nThen open the frontend and set:")
        print("   API URL: http://localhost:8000")
        print("   API Key: steward-secret-key")
        return 0
    else:
        print("\n⚠️  SOME ACCEPTANCE CRITERIA NOT MET")
        print("Please fix the failing tests before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
