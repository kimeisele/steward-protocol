#!/usr/bin/env python3
"""
KRUPP-STAHL HARDENING TEST SUITE
================================
Master runner for all OS hardening tests.

Run all tests:
    python tests/hardening/run_hardening_suite.py

Run specific suite:
    python tests/hardening/run_hardening_suite.py --suite acid
    python tests/hardening/run_hardening_suite.py --suite governance
    python tests/hardening/run_hardening_suite.py --suite constitutional
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def run_suite(name: str, module_name: str) -> dict:
    """Import and run a test suite."""
    print(f"\n{'#' * 70}")
    print(f"# SUITE: {name}")
    print(f"{'#' * 70}")

    try:
        module = __import__(module_name, fromlist=['run_all_tests'])
        return module.run_all_tests()
    except ImportError as e:
        print(f"  💥 IMPORT ERROR: {e}")
        return {"passed": 0, "failed": 1, "error": str(e)}
    except Exception as e:
        print(f"  💥 RUNTIME ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"passed": 0, "failed": 1, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Krupp-Stahl Hardening Test Suite")
    parser.add_argument(
        "--suite",
        choices=["acid", "governance", "constitutional", "all"],
        default="all",
        help="Which test suite to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    suites = {
        "acid": ("LEDGER ACID PROPERTIES", "test_ledger_acid"),
        "governance": ("GOVERNANCE SECURITY", "test_governance_security"),
        "constitutional": ("CONSTITUTIONAL ENFORCEMENT", "test_constitutional_enforcement"),
    }

    if args.suite == "all":
        to_run = list(suites.keys())
    else:
        to_run = [args.suite]

    print("=" * 70)
    print("🔩 KRUPP-STAHL HARDENING TEST SUITE")
    print("=" * 70)
    print(f"Suites to run: {', '.join(to_run)}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    total_passed = 0
    total_failed = 0
    suite_results = {}

    start_time = time.time()

    for suite_key in to_run:
        name, module = suites[suite_key]
        result = run_suite(name, module)
        suite_results[suite_key] = result
        total_passed += result.get("passed", 0)
        total_failed += result.get("failed", 0)

    duration = time.time() - start_time

    # Final Summary
    print("\n")
    print("=" * 70)
    print("🏁 FINAL SUMMARY")
    print("=" * 70)

    for suite_key, result in suite_results.items():
        name = suites[suite_key][0]
        p = result.get("passed", 0)
        f = result.get("failed", 0)
        status = "✅" if f == 0 else "❌"
        print(f"  {status} {name}: {p} passed, {f} failed")

    print("-" * 70)
    print(f"  TOTAL: {total_passed} passed, {total_failed} failed")
    print(f"  TIME:  {duration:.2f}s")
    print("=" * 70)

    if total_failed > 0:
        print("\n⚠️  SYSTEM NOT HARDENED - FIX FAILURES BEFORE PRODUCTION")
        return 1
    else:
        print("\n✅ ALL HARDENING TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
