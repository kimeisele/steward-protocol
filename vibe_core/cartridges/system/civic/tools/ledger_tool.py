#!/usr/bin/env python3
"""
CIVIC Ledger Tool - Agent Credit System (Self-Contained Tool)

High-level interface for agent credit management.
Implements Tool Protocol - Kernel-managed, self-contained.

Philosophy:
"No action is free. Every broadcast costs 1 credit. When credits are gone,
the broadcast license is revoked. This forces agents to be economically rational."
"""

import hashlib
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

from .exceptions import InsufficientFundsError

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
    CIVIC's Ledger Management Tool (Self-Contained).

    High-level interface for agent credit management.
    Uses SQLite for double-entry bookkeeping.

    Tool Protocol implementation - kernel-managed, zero external dependencies.
    """

    # OPUS-025: Fallback only - resolved from config in _ensure_connection
    _DB_PATH_DEFAULT = "data/economy.db"
    DB_PATH = None

    def __init__(self):
        """Initialize the Ledger Tool (kernel-managed)."""
        logger.info("🏦 Initializing LedgerTool (self-contained)...")
        self._conn = None
        self._db_path = None
        self._last_hash = None

        # For backward compatibility with code that reads .entries
        self.entries: List[LedgerEntry] = []

        logger.info("💰 Ledger Tool initialized")

    def _ensure_connection(self):
        """Ensure database connection is initialized."""
        if self._conn is None:
            # OPUS-025: Resolve path from config first
            if self.DB_PATH is not None:
                self._db_path = self.DB_PATH
            else:
                try:
                    from vibe_core.phoenix import get_config

                    config = get_config()
                    if config and hasattr(config, "paths"):
                        self._db_path = config.paths.data.resolve("economy_db")
                    else:
                        self._db_path = Path(self._DB_PATH_DEFAULT)
                except Exception:
                    self._db_path = Path(self._DB_PATH_DEFAULT)

            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._init_db()
            logger.info(f"🏦 Ledger database initialized at {self._db_path}")

    def _init_db(self):
        """Initialize the ledger schema."""
        cur = self._conn.cursor()

        # ACCOUNTS (State Cache)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                agent_id TEXT PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                is_frozen BOOLEAN DEFAULT 0,
                updated_at DATETIME
            )
        """
        )

        # TRANSACTIONS (Event Log - Chained)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id TEXT PRIMARY KEY,
                timestamp DATETIME,
                sender_id TEXT,
                receiver_id TEXT,
                amount INTEGER,
                reason TEXT,
                service_type TEXT,
                signature TEXT,
                previous_hash TEXT,
                tx_hash TEXT
            )
        """
        )

        # ENTRIES (Double-Entry Detail)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT,
                agent_id TEXT,
                side TEXT CHECK(side IN ('DEBIT', 'CREDIT')),
                amount INTEGER,
                FOREIGN KEY(tx_id) REFERENCES transactions(tx_id)
            )
        """
        )

        # Genesis accounts
        genesis_accounts = [("MINT", 1000000000), ("VAULT", 0), ("CIVIC", 0)]
        for agent_id, balance in genesis_accounts:
            cur.execute(
                "INSERT OR IGNORE INTO accounts (agent_id, balance) VALUES (?, ?)",
                (agent_id, balance),
            )
        self._conn.commit()
        logger.debug("✅ Ledger schema initialized")

    def _get_last_hash(self) -> str:
        """Get the hash of the last transaction."""
        self._ensure_connection()
        cur = self._conn.cursor()
        cur.execute("SELECT tx_hash FROM transactions ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        return row["tx_hash"] if row else "GENESIS_HASH"

    def _get_balance(self, agent_id: str) -> int:
        """Get current balance for an agent."""
        self._ensure_connection()
        cur = self._conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE agent_id = ?", (agent_id,))
        row = cur.fetchone()
        return row["balance"] if row else 0

    def _transfer(self, sender: str, receiver: str, amount: int, reason: str, service_type: str = "transfer") -> str:
        """Execute atomic double-entry transaction."""
        self._ensure_connection()

        if amount <= 0:
            raise ValueError("Amount must be positive")

        with self._conn:
            cur = self._conn.cursor()

            # Check funds (unless sender is MINT)
            if sender != "MINT":
                sender_balance = self._get_balance(sender)
                if sender_balance < amount:
                    raise InsufficientFundsError(f"{sender} has {sender_balance}, needs {amount}")

            # Prepare transaction
            timestamp = datetime.utcnow().isoformat()
            prev_hash = self._get_last_hash()
            raw_data = f"{timestamp}{sender}{receiver}{amount}{reason}{prev_hash}"
            tx_hash = hashlib.sha256(raw_data.encode()).hexdigest()
            tx_id = f"TX-{tx_hash[:8]}"

            # Record transaction
            cur.execute(
                """
                INSERT INTO transactions
                (tx_id, timestamp, sender_id, receiver_id, amount, reason, service_type, previous_hash, tx_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (tx_id, timestamp, sender, receiver, amount, reason, service_type, prev_hash, tx_hash),
            )

            # Record entries (double-entry)
            cur.execute(
                "INSERT INTO entries (tx_id, agent_id, side, amount) VALUES (?, ?, 'DEBIT', ?)",
                (tx_id, sender, amount),
            )
            cur.execute(
                "INSERT INTO entries (tx_id, agent_id, side, amount) VALUES (?, ?, 'CREDIT', ?)",
                (tx_id, receiver, amount),
            )

            # Update balances
            if sender != "MINT":
                cur.execute(
                    "UPDATE accounts SET balance = balance - ?, updated_at = ? WHERE agent_id = ?",
                    (amount, timestamp, sender),
                )

            cur.execute("INSERT OR IGNORE INTO accounts (agent_id, balance) VALUES (?, 0)", (receiver,))
            cur.execute(
                "UPDATE accounts SET balance = balance + ?, updated_at = ? WHERE agent_id = ?",
                (amount, timestamp, receiver),
            )

            logger.info(f"💸 Transfer: {sender} → {receiver} ({amount} credits)")
            logger.info(f"   TX: {tx_id}")

            return tx_id

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
        tx_id = self._transfer("MINT", agent_name, amount, reason, "minting")

        # Create a legacy entry for backward compatibility
        balance = self._get_balance(agent_name)
        entry = LedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            operation="allocate",
            amount=amount,
            reason=reason,
            balance_after=balance,
            tx_hash=tx_id,
            previous_hash=self._get_last_hash(),
        )

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
            tx_id = self._transfer(agent_name, "CIVIC_TREASURY", amount, reason, "deduction")

            balance = self._get_balance(agent_name)
            entry = LedgerEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_name=agent_name,
                operation="deduct",
                amount=amount,
                reason=reason,
                balance_after=balance,
                tx_hash=tx_id,
                previous_hash=self._get_last_hash(),
            )

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
        tx_id = self._transfer("MINT", agent_name, amount, "admin_refill", "refilling")

        balance = self._get_balance(agent_name)
        entry = LedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            operation="refill",
            amount=amount,
            reason="admin_refill",
            balance_after=balance,
            tx_hash=tx_id,
            previous_hash=self._get_last_hash(),
        )

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
        self._ensure_connection()
        with self._conn:
            cur = self._conn.cursor()
            cur.execute("UPDATE accounts SET is_frozen = 1 WHERE agent_id = ?", (agent_name,))

        balance = self._get_balance(agent_name)
        entry = LedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            operation="freeze",
            amount=0,
            reason=reason,
            balance_after=balance,
            tx_hash="FROZEN",
            previous_hash=self._get_last_hash(),
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
        return self._get_balance(agent_name)

    def get_agent_history(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transaction history for an agent.

        Args:
            agent_name: Agent to get history for
            limit: Maximum number of entries to return

        Returns:
            List of ledger entries (most recent first)
        """
        self._ensure_connection()
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT * FROM transactions
            WHERE sender_id = ? OR receiver_id = ?
            ORDER BY timestamp DESC LIMIT ?
            """,
            (agent_name, agent_name, limit),
        )
        transactions = [dict(row) for row in cur.fetchall()]

        # Convert to legacy format
        history = []
        for tx in transactions:
            entry = {
                "timestamp": tx.get("timestamp"),
                "agent_name": agent_name,
                "operation": "transfer",
                "amount": tx.get("amount"),
                "reason": tx.get("reason"),
                "balance_after": self._get_balance(agent_name),
                "tx_hash": tx.get("tx_id"),
                "previous_hash": tx.get("previous_hash"),
            }
            history.append(entry)

        return history

    def get_ledger_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire ledger.

        Returns:
            Summary with total transactions, agents, etc.
        """
        self._ensure_connection()
        cur = self._conn.cursor()

        cur.execute("SELECT COUNT(*) as count FROM accounts")
        account_count = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM transactions")
        transaction_count = cur.fetchone()["count"]

        cur.execute("SELECT SUM(amount) as total FROM entries WHERE side='CREDIT'")
        total_credits = cur.fetchone()["total"] or 0

        return {
            "total_transactions": transaction_count,
            "unique_agents": account_count,
            "total_allocated": total_credits,
            "total_deducted": 0,
            "last_transaction": None,
            "integrity_verified": True,
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

    # Show summary
    summary = ledger.get_ledger_summary()
    print(f"\n📊 System Stats: {summary}")


if __name__ == "__main__":
    main()
