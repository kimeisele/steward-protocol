#!/usr/bin/env python3
"""
WATCHMAN PATROL SCRIPT

Execute the first system integrity check.
Freeze violating agents.
Report violations to ledger.

"The guardian stands watch. Justice is swift."
"""

import sys
import json
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchman.cartridge_main import WatchmanCartridge
from civic.tools.economy import CivicBank

def main():
    print("\n" + "=" * 80)
    print("🔐 SYSTEM INTEGRITY AUDIT - WATCHMAN PATROL")
    print("=" * 80)

    # Initialize
    watchman = WatchmanCartridge()
    bank = CivicBank()

    # Run Patrol
    report = watchman.run_patrol()

    # Print Report
    print("\n📋 PATROL REPORT:")
    print("-" * 80)
    print(f"Status: {report['status']}")
    print(f"Violations Found: {report['violations_found']}")
    print(f"Agents Frozen: {len(report['agents_frozen'])}")

    if report['violations_found'] > 0:
        print("\n🚨 VIOLATIONS DETAIL:")
        for v in report['details']:
            print(f"\n   Agent: {v['agent_id'].upper()}")
            print(f"   File: {v['file']}:{v['line']}")
            print(f"   Type: {v['pattern']}")
            print(f"   Code: {v['code']}")
            print(f"   Reason: {v['reason']}")

    if report['agents_frozen']:
        print(f"\n❄️ FROZEN AGENTS:")
        for agent in report['agents_frozen']:
            print(f"   - {agent.upper()}")
            balance = bank.get_balance(agent)
            print(f"     Balance: {balance} credits (LOCKED)")

    # System Status
    print("\n📊 SYSTEM STATUS:")
    print("-" * 80)
    stats = bank.get_system_stats()
    print(f"Total Accounts: {stats['accounts']}")
    print(f"Total Transactions: {stats['transactions']}")
    print(f"System Integrity: {'✅ VERIFIED' if stats['integrity'] else '❌ FAILED'}")

    # Audit Trail
    print("\n📜 RECENT LEDGER ENTRIES:")
    audit = bank.audit_trail(limit=5)
    for tx in audit:
        sender = tx['sender_id']
        receiver = tx['receiver_id']
        amount = tx['amount']
        reason = tx['reason']
        print(f"   {sender:>12s} → {receiver:<12s} | {amount:>5d} | {reason}")

    print("\n" + "=" * 80)
    if report['agents_frozen']:
        print(f"⚠️ CRITICAL: {len(report['agents_frozen'])} agents FROZEN for violations")
        print("These agents cannot execute until violations are resolved.")
    else:
        print("✅ GREEN LIGHT: System is clean. All agents operational.")
    print("=" * 80 + "\n")

    return 0 if report['status'] == 'clean' else 1

if __name__ == "__main__":
    sys.exit(main())
