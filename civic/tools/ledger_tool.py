#!/usr/bin/env python3
"""
CIVIC Ledger Tool - Agent Bank & Credit System

The Treasury of Agent City. This tool manages:
1. Credit Allocation (Starting capital for agents)
2. Credit Deduction (Cost of actions like broadcasts)
3. Credit Ledger (Immutable record of all transactions)
4. Agent Wealth (Current balance, history, defaults)

Philosophy:
"No action is free. Every broadcast costs 1 credit. When credits are gone,
the broadcast license is revoked. This forces agents to be economically rational."
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger("CIVIC_LEDGER")


@dataclass
class LedgerEntry:
    """
    An immutable ledger entry (transaction record).

    Every credit operation is recorded here. Combined with event sourcing,
    this creates an immutable audit trail.
    """
    timestamp: str  # ISO 8601
    agent_name: str
    operation: str  # "allocate", "deduct", "refill", "freeze"
    amount: int
    reason: str
    balance_after: int
    tx_hash: str  # Hash of this transaction
    previous_hash: str  # Hash of previous transaction (blockchain-like)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class LedgerTool:
    """
    CIVIC's Ledger Management Tool.

    Maintains the immutable credit ledger for all agents.
    This is the "ledger of accounts" that no agent can fake.

    Design:
    - Ledger is append-only (immutable)
    - Each transaction references the previous one (hash chain)
    - Credits can only be modified through official methods
    - Deductions are automatic when actions cost credits
    """

    def __init__(self, ledger_path: str = "data/registry/ledger.jsonl"):
        """
        Initialize the Ledger Tool.

        Args:
            ledger_path: Path to the immutable ledger file
        """
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing ledger
        self.entries: List[LedgerEntry] = self._load_ledger()
        self.last_hash = self._get_last_hash()

        logger.info(f"💰 Ledger loaded: {len(self.entries)} transactions")

    def allocate_credits(self, agent_name: str, amount: int, reason: str = "initial_allocation") -> LedgerEntry:
        """
        Allocate credits to an agent (admin operation).

        This is how agents get their starting capital (e.g., 100 credits).

        Args:
            agent_name: Agent receiving credits
            amount: Number of credits to allocate
            reason: Reason for allocation

        Returns:
            The ledger entry that was recorded
        """
        # Get current balance
        current_balance = self.get_agent_balance(agent_name)
        new_balance = current_balance + amount

        # Create ledger entry
        entry = self._create_entry(
            agent_name=agent_name,
            operation="allocate",
            amount=amount,
            reason=reason,
            balance_after=new_balance
        )

        # Append to ledger
        self._append_entry(entry)

        logger.info(f"💰 Allocated {amount} credits to {agent_name}")
        logger.info(f"   Balance: {current_balance} → {new_balance}")

        return entry

    def deduct_credits(self, agent_name: str, amount: int = 1, reason: str = "broadcast") -> LedgerEntry:
        """
        Deduct credits from an agent (automatic on action).

        Called when an agent performs an action that costs credits
        (e.g., publishing a tweet costs 1 credit).

        Args:
            agent_name: Agent to charge
            amount: Credits to deduct (default: 1)
            reason: What the cost was for

        Returns:
            The ledger entry, or None if insufficient funds
        """
        current_balance = self.get_agent_balance(agent_name)

        if current_balance < amount:
            logger.warning(f"❌ {agent_name} has insufficient credits")
            logger.warning(f"   Needed: {amount}, Available: {current_balance}")
            return None

        new_balance = current_balance - amount

        entry = self._create_entry(
            agent_name=agent_name,
            operation="deduct",
            amount=amount,
            reason=reason,
            balance_after=new_balance
        )

        self._append_entry(entry)

        logger.info(f"💸 Deducted {amount} credits from {agent_name} ({reason})")
        logger.info(f"   Balance: {current_balance} → {new_balance}")

        return entry

    def refill_credits(self, agent_name: str, amount: int = 100, admin_key: Optional[str] = None) -> LedgerEntry:
        """
        Refill an agent's credits (admin operation).

        When an agent runs out of credits, an admin can refill them.
        This is logged in the ledger for auditing.

        Args:
            agent_name: Agent to refill
            amount: Credits to add
            admin_key: Admin authorization (future: check against signature)

        Returns:
            The ledger entry
        """
        current_balance = self.get_agent_balance(agent_name)
        new_balance = current_balance + amount

        entry = self._create_entry(
            agent_name=agent_name,
            operation="refill",
            amount=amount,
            reason="admin_refill",
            balance_after=new_balance
        )

        self._append_entry(entry)

        logger.info(f"💰 Refilled {amount} credits for {agent_name}")
        logger.info(f"   Balance: {current_balance} → {new_balance}")

        return entry

    def freeze_credits(self, agent_name: str, reason: str = "violation") -> LedgerEntry:
        """
        Freeze an agent's credits (punitive measure).

        If an agent violates rules, we can freeze their credits
        to prevent any further action.

        Args:
            agent_name: Agent to freeze
            reason: Why credits are frozen

        Returns:
            The ledger entry
        """
        current_balance = self.get_agent_balance(agent_name)

        entry = self._create_entry(
            agent_name=agent_name,
            operation="freeze",
            amount=0,
            reason=reason,
            balance_after=current_balance
        )

        self._append_entry(entry)

        logger.warning(f"🔒 Credits frozen for {agent_name}: {reason}")
        logger.warning(f"   Balance locked at: {current_balance}")

        return entry

    def get_agent_balance(self, agent_name: str) -> int:
        """
        Get the current credit balance for an agent.

        Returns the balance after the last transaction for this agent.

        Args:
            agent_name: Agent to check

        Returns:
            Current credit balance (or 0 if no entries)
        """
        # Find the last entry for this agent
        for entry in reversed(self.entries):
            if entry.agent_name == agent_name:
                return entry.balance_after

        # No entries for this agent yet (not allocated)
        return 0

    def get_agent_history(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transaction history for an agent.

        Args:
            agent_name: Agent to get history for
            limit: Maximum number of entries to return

        Returns:
            List of ledger entries (most recent first)
        """
        history = [
            entry.to_dict()
            for entry in reversed(self.entries)
            if entry.agent_name == agent_name
        ]

        return history[:limit]

    def get_ledger_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire ledger.

        Returns:
            Summary with total transactions, agents, etc.
        """
        agents = set(entry.agent_name for entry in self.entries)
        total_allocated = sum(
            entry.amount for entry in self.entries
            if entry.operation == "allocate"
        )
        total_deducted = sum(
            entry.amount for entry in self.entries
            if entry.operation == "deduct"
        )

        return {
            "total_transactions": len(self.entries),
            "unique_agents": len(agents),
            "total_allocated": total_allocated,
            "total_deducted": total_deducted,
            "last_transaction": self.entries[-1].to_dict() if self.entries else None,
        }

    # ========== Private Helper Methods ==========

    def _create_entry(
        self,
        agent_name: str,
        operation: str,
        amount: int,
        reason: str,
        balance_after: int
    ) -> LedgerEntry:
        """Create a new ledger entry."""
        timestamp = datetime.now(timezone.utc).isoformat()
        tx_hash = self._compute_hash(
            f"{timestamp}{agent_name}{operation}{amount}{reason}{balance_after}"
        )

        entry = LedgerEntry(
            timestamp=timestamp,
            agent_name=agent_name,
            operation=operation,
            amount=amount,
            reason=reason,
            balance_after=balance_after,
            tx_hash=tx_hash,
            previous_hash=self.last_hash
        )

        return entry

    def _append_entry(self, entry: LedgerEntry) -> None:
        """
        Append an entry to the ledger (append-only).

        Writes to the immutable ledger file.
        """
        self.entries.append(entry)
        self.last_hash = entry.tx_hash

        # Append to ledger file (JSONL format - one entry per line)
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def _load_ledger(self) -> List[LedgerEntry]:
        """Load ledger from disk."""
        if not self.ledger_path.exists():
            return []

        entries = []
        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = LedgerEntry(**data)
                        entries.append(entry)
        except Exception as e:
            logger.error(f"Error loading ledger: {e}")

        return entries

    def _get_last_hash(self) -> str:
        """Get the hash of the last transaction (or empty string if ledger is empty)."""
        if self.entries:
            return self.entries[-1].tx_hash
        return "genesis"

    def _compute_hash(self, data: str) -> str:
        """Compute SHA256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]  # First 16 chars


class AgentBank:
    """
    Convenience class: The Agent Bank.

    This wraps the ledger tool with a higher-level "bank" interface.
    Agents interact with the bank to check balance, etc.
    """

    def __init__(self, ledger: LedgerTool):
        """Initialize the bank with a ledger."""
        self.ledger = ledger

    def check_balance(self, agent_name: str) -> Dict[str, Any]:
        """
        Check account balance (public method).

        Args:
            agent_name: Agent to check

        Returns:
            Balance information
        """
        balance = self.ledger.get_agent_balance(agent_name)
        history = self.ledger.get_agent_history(agent_name, limit=3)

        return {
            "agent": agent_name,
            "current_balance": balance,
            "recent_transactions": history,
        }

    def can_broadcast(self, agent_name: str) -> bool:
        """
        Check if agent has credits to broadcast.

        Args:
            agent_name: Agent to check

        Returns:
            True if agent has at least 1 credit
        """
        return self.ledger.get_agent_balance(agent_name) > 0


def main():
    """Demo: Show how the ledger works."""
    ledger = LedgerTool()

    # Allocate initial credits to HERALD
    ledger.allocate_credits("herald", 100, "initial_registration")

    # Simulate some broadcasts
    for i in range(3):
        ledger.deduct_credits("herald", 1, f"broadcast_{i}")

    # Check balance
    balance = ledger.get_agent_balance("herald")
    print(f"\nHERALD's current balance: {balance} credits")

    # Show history
    history = ledger.get_agent_history("herald")
    print(f"\nTransaction history:")
    for entry in history:
        print(f"  {entry['timestamp']}: {entry['operation']} {entry['amount']} - {entry['reason']}")


if __name__ == "__main__":
    main()
