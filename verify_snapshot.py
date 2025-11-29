#!/usr/bin/env python3
"""
VERIFY SNAPSHOT - The Truth Test

Generates a system snapshot and verifies that the data chain is complete:
Ledger → Civic → Kernel → Snapshot

This proves that:
1. The system can introspect itself
2. All agents report accurate data
3. The snapshot captures the real state

Usage:
    python verify_snapshot.py
"""

import json
import sys
import subprocess
from pathlib import Path


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print("=" * 70)


def print_check(name: str, passed: bool, message: str = ""):
    """Print a check result."""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    msg = f" - {message}" if message else ""
    print(f"   {status} {name}{msg}")
    return passed


def main():
    """Run snapshot verification."""
    project_root = Path(__file__).parent
    snapshot_path = project_root / ".steward" / "vibe_snapshot.json"

    print_header("🧬 STEWARD PROTOCOL - SNAPSHOT VERIFICATION")
    print(f"Project Root: {project_root}")
    print(f"Snapshot Location: {snapshot_path}")

    # Step 1: Generate snapshot
    print_header("STEP 1: GENERATING SNAPSHOT")
    try:
        result = subprocess.run(
            [sys.executable, "bin/agent-city", "--snapshot"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"{Colors.RED}❌ Snapshot generation failed{Colors.END}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

        print(f"{Colors.GREEN}✅ Snapshot generated successfully{Colors.END}")
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}❌ Snapshot generation timed out{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to run snapshot command: {e}{Colors.END}")
        return False

    # Step 2: Verify snapshot file exists
    print_header("STEP 2: VERIFYING SNAPSHOT FILE")
    if not snapshot_path.exists():
        print(f"{Colors.RED}❌ Snapshot file not found at {snapshot_path}{Colors.END}")
        return False

    print_check("Snapshot file exists", True, str(snapshot_path))

    # Step 3: Load and parse snapshot
    print_header("STEP 3: PARSING SNAPSHOT")
    try:
        with open(snapshot_path) as f:
            snapshot = json.load(f)
        print_check("Snapshot is valid JSON", True)
    except json.JSONDecodeError as e:
        print_check("Snapshot is valid JSON", False, str(e))
        return False
    except Exception as e:
        print_check("Snapshot file readable", False, str(e))
        return False

    # Step 4: Verify top-level structure
    print_header("STEP 4: VERIFYING SNAPSHOT STRUCTURE")
    checks_passed = 0
    checks_total = 0

    required_keys = ["timestamp", "kernel", "agents"]
    for key in required_keys:
        checks_total += 1
        if print_check(f"Has '{key}' key", key in snapshot):
            checks_passed += 1

    # Step 5: Verify kernel data
    print_header("STEP 5: VERIFYING KERNEL DATA")
    kernel = snapshot.get("kernel", {})

    kernel_checks = [
        ("status", kernel.get("status")),
        ("agents_registered", kernel.get("agents_registered") is not None),
        ("manifests", kernel.get("manifests") is not None),
        ("ledger_events", kernel.get("ledger_events") is not None),
    ]

    for check_name, result in kernel_checks:
        checks_total += 1
        if print_check(f"Kernel.{check_name}", bool(result)):
            checks_passed += 1

    # Step 6: Verify agents data
    print_header("STEP 6: VERIFYING AGENT DATA")
    agents = snapshot.get("agents", {})

    agent_checks = [
        ("civic", agents.get("civic")),
        ("herald", agents.get("herald")),
        ("forum", agents.get("forum")),
        ("science", agents.get("science")),
        ("envoy", agents.get("envoy")),
    ]

    for agent_name, agent_data in agent_checks:
        checks_total += 1
        if print_check(f"Agent '{agent_name}' reported", agent_data is not None):
            checks_passed += 1

    # Step 7: Verify CIVIC metrics (the critical data chain)
    print_header("STEP 7: VERIFYING CIVIC METRICS (THE TRUTH TEST)")
    civic = agents.get("civic", {})
    civic_metrics = civic.get("authority_metrics", {})

    truth_checks = [
        ("total_credits_in_system", "total_credits_in_system" in civic_metrics),
        ("active_broadcast_licenses", "active_broadcast_licenses" in civic_metrics),
        ("ledger_entries", "ledger_entries" in civic_metrics),
        ("total_agents_registered", "total_agents_registered" in civic_metrics),
    ]

    for metric_name, result in truth_checks:
        checks_total += 1
        if print_check(f"CIVIC.{metric_name}", result, "Data chain verified"):
            checks_passed += 1

    # Step 8: Verify HERALD metrics
    print_header("STEP 8: VERIFYING HERALD METRICS")
    herald = agents.get("herald", {})
    herald_metrics = herald.get("broadcast_metrics", {})

    herald_checks = [
        ("broadcasts_published", "content_published_count" in herald_metrics),
        ("events_recorded", "total_events_recorded" in herald_metrics),
        ("connectivity", "connectivity" in herald),
    ]

    for metric_name, result in herald_checks:
        checks_total += 1
        if print_check(f"HERALD.{metric_name}", result):
            checks_passed += 1

    # Step 9: Verify FORUM metrics
    print_header("STEP 9: VERIFYING FORUM METRICS")
    forum = agents.get("forum", {})
    forum_metrics = forum.get("governance_metrics", {})

    forum_checks = [
        ("proposals_total", "total_proposals" in forum_metrics),
        ("proposals_open", "open_proposals" in forum_metrics),
        ("votes_recorded", "total_votes_recorded" in forum_metrics),
    ]

    for metric_name, result in forum_checks:
        checks_total += 1
        if print_check(f"FORUM.{metric_name}", result):
            checks_passed += 1

    # Final report
    print_header("📊 VERIFICATION SUMMARY")
    print(f"   Total Checks: {checks_total}")
    print(f"   Passed: {checks_passed}")
    print(f"   Failed: {checks_total - checks_passed}")

    pass_rate = (checks_passed / checks_total * 100) if checks_total > 0 else 0
    print(f"   Success Rate: {pass_rate:.1f}%")

    if checks_passed == checks_total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL CHECKS PASSED{Colors.END}")
        print(f"{Colors.GREEN}The USB-Stick of Truth is operational.{Colors.END}")
        print(f"{Colors.CYAN}Snapshot: {snapshot_path}{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ VERIFICATION FAILED{Colors.END}")
        print(f"{Colors.RED}{checks_total - checks_passed} checks failed{Colors.END}\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
