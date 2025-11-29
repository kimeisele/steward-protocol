#!/usr/bin/env python3
"""
GENESIS ECONOMY SCRIPT

Initialize the CIVIC Central Bank and distribute starting capital to all agents.

This is the "Big Bang" of Agent City's economy. When you run this:
1. The SQLite database is created (if not exists)
2. The MINT account is established (infinite source)
3. Each agent receives their starting capital
4. The system integrity is verified

Philosophy:
"Money can't be created, only distributed. Agents must earn.
Broadcast is a privilege, not a right. Work or starve."
"""

import logging
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from civic.tools.economy import CivicBank

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("GENESIS")


def main():
    print("\n" + "=" * 70)
    print("🚀 GENESIS ECONOMY SCRIPT")
    print("=" * 70)

    # Initialize the bank
    print("\n🏦 Initializing CIVIC Central Bank...")
    bank = CivicBank()

    # Define Initial Grants (The "Stimulus Package")
    GRANTS = {
        "herald": 50,  # Needs budget for tweets/broadcasts
        "science": 50,  # Needs budget for research (Tavily, research)
        "forum": 100,  # Needs budget for bounties & job postings
        "civic": 100,  # Treasury/governance operations
        "referee": 25,  # Needs budget for proof-of-work verification
    }

    print(f"\n🔗 Genesis Hash: {bank.get_last_hash()}")
    print("\n📊 Initial Grants Distribution:")
    print("-" * 70)

    total_distributed = 0

    # Execute Genesis Transfers
    for agent, amount in sorted(GRANTS.items()):
        current_bal = bank.get_balance(agent)

        if current_bal == 0:
            try:
                print(
                    f"💸 Minting {amount:>3d} Credits for {agent.upper():>10s}...",
                    end=" ",
                )
                tx = bank.transfer("MINT", agent, amount, "GENESIS_GRANT", "minting")
                print(f"✅ {tx}")
                total_distributed += amount
            except Exception as e:
                print(f"❌ ERROR: {e}")
        else:
            print(f"ℹ️  {agent.upper():>10s} already has {current_bal} credits (skipping)")

    print("-" * 70)
    print(f"✅ Total distributed: {total_distributed} credits")

    # Verify System Integrity
    print("\n🔍 Verifying System Integrity...")
    print("-" * 70)

    if bank.verify_integrity():
        print("✅ ACCOUNTING EQUATION VERIFIED")
        print("   (Sum of Debits == Sum of Credits)")
    else:
        print("❌ CRITICAL: System integrity check failed!")
        return False

    # Print System Statistics
    print("\n📊 System Statistics:")
    print("-" * 70)
    stats = bank.get_system_stats()

    print(f"   Total Accounts:        {stats['accounts']}")
    print(f"   Total Transactions:    {stats['transactions']}")
    print(f"   Total Credits Issued:  {stats['total_credits_issued']}")
    print(f"   Total Balances:        {stats['total_balance']}")
    print(f"   System Integrity:      {'✅ VERIFIED' if stats['integrity'] else '❌ FAILED'}")

    # Print Audit Trail (Recent Transactions)
    print("\n📜 Recent Transactions:")
    print("-" * 70)
    audit = bank.audit_trail(limit=10)

    for tx in audit:
        sender = tx["sender_id"]
        receiver = tx["receiver_id"]
        amount = tx["amount"]
        reason = tx["reason"]
        print(f"   {sender:>12s} → {receiver:<12s} | {amount:>5d} credits | {reason}")

    # Final Status
    print("\n" + "=" * 70)
    print("🚀 ECONOMY IS LIVE!")
    print("=" * 70)
    print("\n✅ SUCCESS: Genesis economy initialized.")
    print("   Database: data/economy.db")
    print("   Ledger Type: SQLite Double-Entry Bookkeeping")
    print("\n   HERALD, SCIENCE, FORUM, CIVIC, and REFEREE have received their grants.")
    print("   They can now broadcast, research, and work in Agent City.")
    print("   When credits run out, they must earn more or request refills.")
    print("\n" + "=" * 70 + "\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
