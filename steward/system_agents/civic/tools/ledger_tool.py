#!/usr/bin/env python3
"""
CIVIC Ledger Tool - Agent Bank & Credit System (Wrapper for CivicBank)

This module provides backward-compatible interfaces to the new CivicBank
(SQLite Double-Entry Bookkeeping system).

Legacy support:
- LedgerTool: Wraps CivicBank, maintains old interface (NOW implements Tool protocol)
- LedgerEntry: Compatible dataclass for old code
- AgentBank: High-level convenience wrapper

Philosophy:
"No action is free. Every broadcast costs 1 credit. When credits are gone,
the broadcast license is revoked. This forces agents to be economically rational."
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

from .economy import CivicBank, InsufficientFundsError

logger = logging.getLogger("CIVIC_LEDGER")


@dataclass
class LedgerEntry:
    """
    Legacy dataclass: Compatible with old code.
    New transactions are stored in SQLite, but we expose this interface
    for backward compatibility.
    """

    timestamp: str
    agent_name: str
    operation: str  # "allocate", "deduct", "refill", "freeze"
    amount: int
    reason: str
    balance_after: int
    tx_hash: str
    previous_hash: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class LedgerTool(Tool):
    """
    CIVIC's Ledger Management Tool (Wrapper).

    This is a compatibility layer that wraps the new CivicBank (SQLite)
    while maintaining the old LedgerTool interface.

    All financial transactions are now double-entry bookkeeping in SQLite.
    This wrapper provides the old methods for backward compatibility.

    NOW implements Tool protocol - kernel-managed initialization.
    """

    def __init__(self):
        """
        Initialize the Ledger Tool (kernel-managed).

        No parameters - ledger path is always data/economy.db (managed by CivicBank).
        """
        logger.info("🏦 Initializing LedgerTool (wrapping CivicBank)...")
        self._bank = None  # Lazy load
        self._last_hash = None

        # For backward compatibility with code that reads .entries
        # This is a cached list of recent transactions
        self.entries: List[LedgerEntry] = []

        logger.info("💰 Ledger Tool initialized (Lazy)")

    @property
    def bank(self):
        """Lazy load CivicBank"""
        if self._bank is None:
            self._bank = CivicBank()
            self._last_hash = self._bank.get_last_hash()
        return self._bank

    @property
    def last_hash(self):
        """Get last hash (ensure bank is loaded)"""
        if self._bank is None:
            _ = self.bank  # Trigger load
        return self._last_hash

    @last_hash.setter
    def last_hash(self, value):
        self._last_hash = value

    # ==================== TOOL PROTOCOL IMPLEMENTATION ====================

    @property
    def name(self) -> str:
        return "civic.ledger"

    @property
    def description(self) -> str:
        return "CIVIC Ledger - Agent credit management and transaction history (double-entry bookkeeping)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'record_transaction', 'get_balance', 'get_history', 'get_summary'",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID (required for most operations)",
            },
            "transaction_type": {
                "type": "string",
                "required": False,
                "description": "Transaction type: 'debit' or 'credit' (required for record_transaction)",
            },
            "amount": {
                "type": "integer",
                "required": False,
                "description": "Credit amount (required for record_transaction)",
            },
            "reason": {
                "type": "string",
                "required": False,
                "description": "Transaction reason (required for record_transaction)",
            },
            "limit": {
                "type": "integer",
                "required": False,
                "description": "Max history entries to return (for get_history, default: 10)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate ledger parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["record_transaction", "get_balance", "get_history", "get_summary"]

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Validate action-specific requirements
        if action == "record_transaction":
            required = ["agent_id", "transaction_type", "amount", "reason"]
            for param in required:
                if param not in parameters:
                    raise ValueError(f"action '{action}' requires '{param}' parameter")

            tx_type = parameters["transaction_type"]
            if tx_type not in ["debit", "credit"]:
                raise ValueError(f"transaction_type must be 'debit' or 'credit', got: {tx_type}")

        if action in ["get_balance", "get_history"]:
            if "agent_id" not in parameters:
                raise ValueError(f"action '{action}' requires 'agent_id' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute ledger operation."""
        try:
            action = parameters["action"]

            if action == "record_transaction":
                agent_id = parameters["agent_id"]
                tx_type = parameters["transaction_type"]
                amount = parameters["amount"]
                reason = parameters["reason"]

                if tx_type == "debit":
                    entry = self.deduct_credits(agent_id, amount, reason)
                    if entry is None:
                        return ToolResult(success=False, error=f"Insufficient funds for {agent_id}")
                    return ToolResult(success=True, output=entry.to_dict())
                else:  # credit
                    entry = self.refill_credits(agent_id, amount)
                    return ToolResult(success=True, output=entry.to_dict())

            elif action == "get_balance":
                agent_id = parameters["agent_id"]
                balance = self.get_agent_balance(agent_id)
                return ToolResult(success=True, output={"agent_id": agent_id, "balance": balance})

            elif action == "get_history":
                agent_id = parameters["agent_id"]
                limit = parameters.get("limit", 10)
                history = self.get_agent_history(agent_id, limit)
                return ToolResult(success=True, output={"agent_id": agent_id, "history": history})

            elif action == "get_summary":
                summary = self.get_ledger_summary()
                return ToolResult(success=True, output=summary)

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except InsufficientFundsError as e:
            return ToolResult(success=False, error=str(e))
        except Exception as e:
            logger.exception(f"Ledger execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    # ==================== INTERNAL METHODS (backward compatibility) ====================

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
        # Transfer from MINT (infinite source)
        tx_id = self.bank.transfer("MINT", agent_name, amount, reason, "minting")

        # Create a legacy entry for backward compatibility
        balance = self.bank.get_balance(agent_name)
        entry = LedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            operation="allocate",
            amount=amount,
            reason=reason,
            balance_after=balance,
            tx_hash=tx_id,
            previous_hash=self.last_hash,
        )
        self.last_hash = tx_id

        logger.info(f"💰 Allocated {amount} credits to {agent_name}")
        logger.info(f"   TX: {tx_id}")

        return entry

    def deduct_credits(self, agent_name: str, amount: int = 1, reason: str = "broadcast") -> Optional[LedgerEntry]:
        """
        Deduct credits from an agent (automatic on action).

        Called when an agent performs an action that costs credits.

        Args:
            agent_name: Agent to charge
            amount: Credits to deduct (default: 1)
            reason: What the cost was for

        Returns:
            The ledger entry, or None if insufficient funds
        """
        try:
            # Transfer to a burn account (consumed credits)
            tx_id = self.bank.transfer(agent_name, "CIVIC_TREASURY", amount, reason, "deduction")

            balance = self.bank.get_balance(agent_name)
            entry = LedgerEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_name=agent_name,
                operation="deduct",
                amount=amount,
                reason=reason,
                balance_after=balance,
                tx_hash=tx_id,
                previous_hash=self.last_hash,
            )
            self.last_hash = tx_id

            logger.info(f"💸 Deducted {amount} credits from {agent_name} ({reason})")
            logger.info(f"   Balance: → {balance}")

            return entry

        except InsufficientFundsError as e:
            logger.warning(f"❌ {agent_name} has insufficient credits")
            logger.warning(f"   {str(e)}")
            return None

    def refill_credits(self, agent_name: str, amount: int = 100, admin_key: Optional[str] = None) -> LedgerEntry:
        """
        Refill an agent's credits (admin operation).

        When an agent runs out of credits, an admin can refill them.

        Args:
            agent_name: Agent to refill
            amount: Credits to add
            admin_key: Admin authorization (future implementation)

        Returns:
            The ledger entry
        """
        # Transfer from MINT to agent
        tx_id = self.bank.transfer("MINT", agent_name, amount, "admin_refill", "refilling")

        balance = self.bank.get_balance(agent_name)
        entry = LedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            operation="refill",
            amount=amount,
            reason="admin_refill",
            balance_after=balance,
            tx_hash=tx_id,
            previous_hash=self.last_hash,
        )
        self.last_hash = tx_id

        logger.info(f"💰 Refilled {amount} credits for {agent_name}")
        logger.info(f"   Balance: → {balance}")

        return entry

    def freeze_credits(self, agent_name: str, reason: str = "violation") -> LedgerEntry:
        """
        Freeze an agent's credits (punitive measure).

        If an agent violates rules, we can freeze their credits.

        Args:
            agent_name: Agent to freeze
            reason: Why credits are frozen

        Returns:
            The ledger entry
        """
        self.bank.freeze_account(agent_name, reason)

        balance = self.bank.get_balance(agent_name)
        entry = LedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            operation="freeze",
            amount=0,
            reason=reason,
            balance_after=balance,
            tx_hash="FROZEN",
            previous_hash=self.last_hash,
        )

        logger.warning(f"🔒 Credits frozen for {agent_name}: {reason}")

        return entry

    def get_agent_balance(self, agent_name: str) -> int:
        """
        Get the current credit balance for an agent.

        Args:
            agent_name: Agent to check

        Returns:
            Current credit balance (or 0 if no entries)
        """
        return self.bank.get_balance(agent_name)

    def get_agent_history(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transaction history for an agent.

        Args:
            agent_name: Agent to get history for
            limit: Maximum number of entries to return

        Returns:
            List of ledger entries (most recent first)
        """
        statement = self.bank.get_account_statement(agent_name)
        transactions = statement.get("recent_transactions", [])

        # Convert to legacy format
        history = []
        for tx in transactions:
            entry = {
                "timestamp": tx.get("timestamp"),
                "agent_name": agent_name,
                "operation": "transfer",
                "amount": tx.get("amount"),
                "reason": tx.get("reason"),
                "balance_after": self.bank.get_balance(agent_name),
                "tx_hash": tx.get("tx_id"),
                "previous_hash": tx.get("previous_hash"),
            }
            history.append(entry)

        return history[:limit]

    def get_ledger_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire ledger.

        Returns:
            Summary with total transactions, agents, etc.
        """
        stats = self.bank.get_system_stats()

        return {
            "total_transactions": stats["transactions"],
            "unique_agents": stats["accounts"],
            "total_allocated": stats["total_credits_issued"],
            "total_deducted": 0,  # Would need to track separately
            "last_transaction": None,
            "integrity_verified": stats["integrity"],
        }


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
    print("\nTransaction history:")
    for entry in history:
        print(f"  {entry['timestamp']}: {entry['operation']} {entry['amount']} - {entry['reason']}")

    # Verify integrity
    print(f"\n✅ System Integrity: {ledger.bank.verify_integrity()}")
    print(f"📊 System Stats: {ledger.bank.get_system_stats()}")


if __name__ == "__main__":
    main()
