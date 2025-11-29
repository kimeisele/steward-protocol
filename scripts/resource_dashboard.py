#!/usr/bin/env python3
"""
RESOURCE DASHBOARD - Real-Time Monitoring
=========================================

Displays current resource usage for all agents:
- CPU% and RAM usage
- Credit balance and quotas
- Violation alerts

Usage:
    python scripts/resource_dashboard.py
"""

import logging
import os
import sys
import time

# Ensure we can import vibe_core
sys.path.append(os.getcwd())

from vibe_core.kernel_impl import RealVibeKernel

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger("DASHBOARD")


def clear_screen():
    """Clear terminal screen"""
    os.system("clear" if os.name == "posix" else "cls")


def format_status(within_quota: bool) -> str:
    """Format status indicator"""
    return "✅" if within_quota else "⚠️ "


def display_dashboard(kernel: RealVibeKernel):
    """Display resource dashboard"""
    clear_screen()

    print("=" * 70)
    print("🖥️  RESOURCE DASHBOARD - Agent Operating System")
    print("=" * 70)
    print()

    # Get all usage stats
    usage_stats = kernel.resource_manager.get_all_usage(kernel.process_manager)

    if not usage_stats:
        print("No agents running.")
        return

    # Display each agent
    for agent_id, stats in usage_stats.items():
        if "error" in stats:
            print(f"Agent: {agent_id}")
            print(f"  ❌ Error: {stats['error']}")
            print()
            continue

        # Get credit balance
        try:
            bank = kernel.get_bank()
            credits = bank.get_balance(agent_id)
        except:
            credits = "N/A"

        print(f"Agent: {agent_id}")
        print(f"  PID:     {stats['pid']}")
        print(f"  Credits: {credits}")
        print(f"  Quota:   {stats['quota_cpu']}% CPU, {stats['quota_memory']} MB RAM")
        print(
            f"  Usage:   {stats['cpu_percent']}% CPU, {stats['memory_mb']:.1f} MB RAM"
        )

        cpu_status = format_status(stats.get("cpu_within_quota", True))
        mem_status = format_status(stats.get("memory_within_quota", True))

        print(f"  Status:  {cpu_status} CPU  {mem_status} Memory")
        print()

    # Check for violations
    violations = kernel.resource_manager.check_violations(kernel.process_manager)
    if violations:
        print("⚠️  VIOLATIONS DETECTED:")
        for v in violations:
            print(
                f"  - {v['agent_id']}: {v['type']} usage {v['usage']:.1f} exceeds quota {v['quota']}"
            )
        print()

    print("=" * 70)
    print("Press Ctrl+C to exit | Updates every 5 seconds")
    print("=" * 70)


def main():
    """Main dashboard loop"""
    print("🚀 Starting Resource Dashboard...")
    print("Initializing kernel...")

    # Initialize kernel
    kernel = RealVibeKernel(ledger_path=":memory:")

    # Note: In a real scenario, agents would be registered and running
    # For demo purposes, we'll just show the dashboard structure

    print("✅ Dashboard ready!")
    print()

    try:
        while True:
            display_dashboard(kernel)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped.")
        kernel.shutdown()


if __name__ == "__main__":
    main()
