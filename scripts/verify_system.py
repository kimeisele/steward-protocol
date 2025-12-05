#!/usr/bin/env python3
"""
SYSTEM VERIFICATION SCRIPT - CI Fast Lane

This script boots the kernel, runs the Universal Test Orchestration,
and exits with appropriate code for CI/CD pipelines.

EXIT CODES:
    0 = All tests passed
    1 = Critical tests failed (blocks deployment)
    2 = Non-critical tests failed (warning only)
    3 = System boot failed (fatal error)

USAGE:
    python scripts/verify_system.py           # Run all tests
    python scripts/verify_system.py --fast    # Only critical tests
    python scripts/verify_system.py --report  # Generate JSON report

CI INTEGRATION:
    # GitHub Actions example:
    - name: Fast Lane Verification
      run: python scripts/verify_system.py --fast
      timeout-minutes: 1
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_system(fast_mode: bool = False, generate_report: bool = False) -> int:
    """
    Boot kernel and run verification tests.

    Args:
        fast_mode: Only run critical tests
        generate_report: Generate JSON report file

    Returns:
        Exit code (0=success, 1=critical fail, 2=warning, 3=boot fail)
    """
    start_time = time.time()
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "fast" if fast_mode else "full",
        "status": "unknown",
        "duration_ms": 0,
        "summary": {},
        "failures": [],
    }

    print("=" * 60)
    print("STEWARD PROTOCOL - SYSTEM VERIFICATION")
    print("=" * 60)
    print(f"Mode: {'FAST (critical only)' if fast_mode else 'FULL'}")
    print()

    # =========================================================================
    # PHASE 1: Boot Kernel
    # =========================================================================
    print("[1/3] Booting kernel...")

    try:
        from vibe_core.kernel_impl import RealVibeKernel
        from vibe_core.plugins.test_orchestration import TestOrchestrationPlugin
        from vibe_core.protocols.testable import TestableType

        kernel = RealVibeKernel(ledger_path=":memory:")
        print("      Kernel booted successfully")

    except Exception as e:
        print(f"      FATAL: Kernel boot failed: {e}")
        report["status"] = "boot_failed"
        report["error"] = str(e)
        _save_report(report, generate_report)
        return 3

    # =========================================================================
    # PHASE 2: Get Test Orchestration Plugin
    # =========================================================================
    print("[2/3] Initializing test orchestration...")

    test_plugin = None
    for plugin in kernel._plugins:
        if plugin.plugin_id == "test_orchestration":
            test_plugin = plugin
            break

    if not test_plugin:
        # Register it manually
        test_plugin = TestOrchestrationPlugin()
        kernel.register_plugin(test_plugin)
        test_plugin.on_boot(kernel)

    discovery = test_plugin._registry.get_summary()
    print(f"      Discovered: {discovery['total_testables']} components")
    print(f"      Total tests: {discovery['total_tests']}")

    # =========================================================================
    # PHASE 3: Run Tests
    # =========================================================================
    print("[3/3] Running verification tests...")

    if fast_mode:
        # Only run critical infrastructure tests
        critical_types = [
            TestableType.LEDGER,
            TestableType.SCHEDULER,
            TestableType.EVENT_BUS,
            TestableType.PLUGIN,
        ]
        results = []
        for t_type in critical_types:
            results.extend(test_plugin.run_tests_by_type(t_type))
    else:
        # Run all tests
        results = test_plugin.run_all_tests()

    # =========================================================================
    # PHASE 4: Analyze Results
    # =========================================================================
    duration_ms = (time.time() - start_time) * 1000

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    pass_rate = passed / len(results) if results else 0

    print()
    print("-" * 60)
    print("RESULTS")
    print("-" * 60)
    print(f"Total:     {len(results)}")
    print(f"Passed:    {passed}")
    print(f"Failed:    {failed}")
    print(f"Pass Rate: {pass_rate:.1%}")
    print(f"Duration:  {duration_ms:.2f}ms")

    # Categorize failures
    critical_failures = []
    non_critical_failures = []

    CRITICAL_TYPES = {"ledger", "scheduler", "event_bus", "plugin", "security", "governance"}

    for result in results:
        if not result.passed:
            if result.testable_type in CRITICAL_TYPES:
                critical_failures.append(result)
            else:
                non_critical_failures.append(result)

    # Print failures
    if critical_failures:
        print()
        print("CRITICAL FAILURES (blocks deployment):")
        for f in critical_failures[:10]:
            print(f"  - {f.test_id}")
            if f.error:
                print(f"    {f.error[:60]}")

    if non_critical_failures:
        print()
        print("NON-CRITICAL FAILURES (warnings):")
        for f in non_critical_failures[:5]:
            print(f"  - {f.test_id}")

    # Build report
    report["duration_ms"] = duration_ms
    report["summary"] = {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "critical_failures": len(critical_failures),
        "non_critical_failures": len(non_critical_failures),
    }
    report["failures"] = [
        {"test_id": r.test_id, "type": r.testable_type, "error": r.error}
        for r in (critical_failures + non_critical_failures)[:20]
    ]

    # Determine exit code
    if critical_failures:
        report["status"] = "critical_failure"
        exit_code = 1
    elif non_critical_failures:
        report["status"] = "warning"
        exit_code = 2
    else:
        report["status"] = "success"
        exit_code = 0

    print()
    print("=" * 60)
    print(f"STATUS: {report['status'].upper()}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)

    _save_report(report, generate_report)
    return exit_code


def _save_report(report: dict, generate_report: bool) -> None:
    """Save JSON report if requested."""
    if generate_report:
        report_path = Path("verification_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify STEWARD Protocol system integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Only run critical infrastructure tests (< 1 second)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate JSON report file",
    )

    args = parser.parse_args()
    exit_code = verify_system(fast_mode=args.fast, generate_report=args.report)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
