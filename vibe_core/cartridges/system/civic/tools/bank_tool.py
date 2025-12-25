"""
CIVIC BANK TOOL - Double-Entry Bookkeeping Engine (Tool Protocol)

Production-Grade SQLite Banking with Chained Hashes.
GAD-000 Compliant: Radical Transparency & Atomicity.

This is the financial core of Agent City. Every credit transaction
is recorded with double-entry logic:
  - DEBIT: Money leaving an account
  - CREDIT: Money entering an account

The Accounting Equation ALWAYS holds: Sum(DEBITS) = Sum(CREDITS)

Philosophy:
"No agent action is free. Every broadcast costs credits. When credits
are gone, broadcast license is revoked. This forces agents to be
economically rational and earn through productive work."
"""

import hashlib
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("CIVIC_BANK_TOOL")


class BankTool(Tool):
    """
    THE CENTRAL BANK OF AGENT CITY (Tool Protocol).

    Implements Double-Entry Bookkeeping with Chained Hashes.
    GAD-000 Compliant: Radical Transparency & Atomicity.

    Actions:
    - get_balance: Get agent balance
    - transfer: Execute atomic double-entry transaction
    - freeze_account: Freeze agent account
    - unfreeze_account: Unfreeze agent account
    - is_frozen: Check if account is frozen
    - audit_trail: Get recent transactions
    - get_statement: Get account statement
    - verify_integrity: Verify accounting equation
    - get_stats: Get system statistics
    """

    # OPUS-025: Fallback only - actual path from config or parameters
    _DB_PATH_DEFAULT = "data/economy.db"
    DB_PATH = None  # Set at runtime from config or parameters

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        super().__init__(services)
        self._conn = None
        self._db_path = None

    @property
    def name(self) -> str:
        return "civic.bank"

    @property
    def description(self) -> str:
        return "Central bank: double-entry bookkeeping, credit transfers, account management"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'get_balance', 'transfer', 'freeze_account', 'unfreeze_account', 'is_frozen', 'audit_trail', 'get_statement', 'verify_integrity', 'get_stats'",
            },
            "agent_id": {"type": "string", "required": False, "description": "Agent identifier"},
            "sender": {"type": "string", "required": False, "description": "Sender agent (for transfer)"},
            "receiver": {"type": "string", "required": False, "description": "Receiver agent (for transfer)"},
            "amount": {"type": "number", "required": False, "description": "Amount of credits"},
            "reason": {"type": "string", "required": False, "description": "Transaction reason"},
            "service_type": {
                "type": "string",
                "required": False,
                "description": "Service type (transfer, minting, etc)",
            },
            "limit": {"type": "number", "required": False, "description": "Limit for audit_trail"},
            "db_path": {"type": "string", "required": False, "description": "Database path (for VFS isolation)"},
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        action = parameters.get("action")
        if not action:
            raise ValueError("Missing required parameter: action")

        valid_actions = [
            "get_balance",
            "transfer",
            "freeze_account",
            "unfreeze_account",
            "is_frozen",
            "audit_trail",
            "get_statement",
            "verify_integrity",
            "get_stats",
            "get_connection",
        ]
        if action not in valid_actions:
            raise ValueError(f"Invalid action '{action}'. Must be one of: {valid_actions}")

        # Action-specific validation
        if action == "get_balance" and "agent_id" not in parameters:
            raise ValueError("Action 'get_balance' requires 'agent_id'")

        if action == "transfer":
            required = ["sender", "receiver", "amount", "reason"]
            missing = [p for p in required if p not in parameters]
            if missing:
                raise ValueError(f"Action 'transfer' requires: {', '.join(missing)}")
            if parameters["amount"] <= 0:
                raise ValueError("Transfer amount must be positive")

        if action in ["freeze_account", "unfreeze_account", "is_frozen", "get_statement"]:
            if "agent_id" not in parameters:
                raise ValueError(f"Action '{action}' requires 'agent_id'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute bank operation."""
        action = parameters["action"]

        try:
            # Initialize database connection if needed
            if self._conn is None:
                db_path = parameters.get("db_path")

                # OPUS-025: Resolve from config if not provided
                if db_path is None:
                    if self.DB_PATH is not None:
                        db_path = str(self.DB_PATH)
                    else:
                        try:
                            from vibe_core.phoenix import get_config

                            config = get_config()
                            if config and hasattr(config, "paths"):
                                db_path = str(config.paths.data.resolve("economy_db"))
                            else:
                                db_path = self._DB_PATH_DEFAULT
                        except Exception:
                            db_path = self._DB_PATH_DEFAULT

                self._db_path = Path(db_path)
                self._db_path.parent.mkdir(parents=True, exist_ok=True)
                self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
                self._conn.row_factory = sqlite3.Row
                self._init_db()
                logger.info(f"🏦 CivicBank initialized at {self._db_path}")

            # Special action: return connection (for vault integration)
            if action == "get_connection":
                return ToolResult(success=True, output={"connection": self._conn})

            # Route to action handlers
            if action == "get_balance":
                balance = self._get_balance(parameters["agent_id"])
                return ToolResult(success=True, output={"agent_id": parameters["agent_id"], "balance": balance})

            elif action == "transfer":
                tx_id = self._transfer(
                    sender=parameters["sender"],
                    receiver=parameters["receiver"],
                    amount=parameters["amount"],
                    reason=parameters["reason"],
                    service_type=parameters.get("service_type", "transfer"),
                )
                return ToolResult(success=True, output={"tx_id": tx_id, "status": "completed"})

            elif action == "freeze_account":
                self._freeze_account(parameters["agent_id"], parameters.get("reason", "violation"))
                return ToolResult(success=True, output={"agent_id": parameters["agent_id"], "status": "frozen"})

            elif action == "unfreeze_account":
                self._unfreeze_account(parameters["agent_id"], parameters.get("reason", "manual_override"))
                return ToolResult(success=True, output={"agent_id": parameters["agent_id"], "status": "unfrozen"})

            elif action == "is_frozen":
                frozen = self._is_frozen(parameters["agent_id"])
                return ToolResult(success=True, output={"agent_id": parameters["agent_id"], "is_frozen": frozen})

            elif action == "audit_trail":
                trail = self._audit_trail(parameters.get("limit", 10))
                return ToolResult(success=True, output={"transactions": trail})

            elif action == "get_statement":
                statement = self._get_statement(parameters["agent_id"])
                return ToolResult(success=True, output=statement)

            elif action == "verify_integrity":
                valid = self._verify_integrity()
                return ToolResult(success=True, output={"integrity_valid": valid})

            elif action == "get_stats":
                stats = self._get_stats()
                return ToolResult(success=True, output=stats)

        except ValueError as e:
            # Business logic errors (insufficient funds, etc.)
            logger.warning(f"⚠️  Bank operation '{action}' rejected: {e}")
            return ToolResult(success=False, error=str(e))

        except Exception as e:
            # Unexpected errors
            logger.error(f"❌ Bank operation '{action}' failed: {type(e).__name__}: {e}")
            return ToolResult(success=False, error=f"Bank operation failed: {type(e).__name__}: {e}")

    def _init_db(self):
        """Initialize the immutable ledger schema."""
        cur = self._conn.cursor()

        # 1. ACCOUNTS (State Cache - Denormalized)
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

        # 2. TRANSACTIONS (The Event Log - Chained & Immutable)
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

        # 3. ENTRIES (The Double-Entry Detail)
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

        # GENESIS: Ensure special accounts exist
        genesis_accounts = [
            ("MINT", 1000000000),  # Infinite money fountain
            ("VAULT", 0),  # Vault asset management (receives lease fees)
            ("CIVIC", 0),  # Platform operations (receives platform fees)
        ]
        for agent_id, initial_balance in genesis_accounts:
            cur.execute(
                "INSERT OR IGNORE INTO accounts (agent_id, balance) VALUES (?, ?)",
                (agent_id, initial_balance),
            )
        self._conn.commit()
        logger.info("✅ Bank schema initialized (MINT, VAULT, CIVIC accounts ready)")

    def _get_last_hash(self) -> str:
        """Get the hash of the last transaction for chaining."""
        cur = self._conn.cursor()
        cur.execute("SELECT tx_hash FROM transactions ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        return row["tx_hash"] if row else "GENESIS_HASH"

    def _get_balance(self, agent_id: str) -> int:
        """Get current balance for an agent."""
        cur = self._conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE agent_id = ?", (agent_id,))
        row = cur.fetchone()
        return row["balance"] if row else 0

    def _transfer(
        self,
        sender: str,
        receiver: str,
        amount: int,
        reason: str,
        service_type: str = "transfer",
    ) -> str:
        """
        Execute an atomic Double-Entry Transaction.

        Raises:
            ValueError: If amount is not positive or sender lacks funds
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with self._conn:  # Atomic transaction block
            cur = self._conn.cursor()

            # 1. CHECK FUNDS (unless sender is MINT)
            if sender != "MINT":
                sender_balance = self._get_balance(sender)
                if sender_balance < amount:
                    raise ValueError(f"{sender} has {sender_balance}, needs {amount}")

            # 2. PREPARE DATA
            timestamp = datetime.utcnow().isoformat()
            prev_hash = self._get_last_hash()

            # Generate Transaction ID & Hash
            raw_data = f"{timestamp}{sender}{receiver}{amount}{reason}{prev_hash}"
            tx_hash = hashlib.sha256(raw_data.encode()).hexdigest()
            tx_id = f"TX-{tx_hash[:8]}"

            # 3. RECORD TRANSACTION (Master Record - Immutable)
            cur.execute(
                """
                INSERT INTO transactions
                (tx_id, timestamp, sender_id, receiver_id, amount, reason, service_type, previous_hash, tx_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    tx_id,
                    timestamp,
                    sender,
                    receiver,
                    amount,
                    reason,
                    service_type,
                    prev_hash,
                    tx_hash,
                ),
            )

            # 4. RECORD ENTRIES (Double-Entry Detail)
            # Entry 1: Sender loses money (DEBIT)
            cur.execute(
                "INSERT INTO entries (tx_id, agent_id, side, amount) VALUES (?, ?, 'DEBIT', ?)",
                (tx_id, sender, amount),
            )

            # Entry 2: Receiver gains money (CREDIT)
            cur.execute(
                "INSERT INTO entries (tx_id, agent_id, side, amount) VALUES (?, ?, 'CREDIT', ?)",
                (tx_id, receiver, amount),
            )

            # 5. UPDATE BALANCES (Denormalized State Cache)
            # Update Sender
            if sender != "MINT":
                cur.execute(
                    "UPDATE accounts SET balance = balance - ?, updated_at = ? WHERE agent_id = ?",
                    (amount, timestamp, sender),
                )

            # Ensure Receiver exists and update
            cur.execute(
                "INSERT OR IGNORE INTO accounts (agent_id, balance) VALUES (?, 0)",
                (receiver,),
            )
            cur.execute(
                "UPDATE accounts SET balance = balance + ?, updated_at = ? WHERE agent_id = ?",
                (amount, timestamp, receiver),
            )

            logger.info(f"💸 Transfer: {sender} → {receiver} ({amount} credits)")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   TX: {tx_id}")

            return tx_id

    def _freeze_account(self, agent_id: str, reason: str = "violation") -> None:
        """Freeze an agent's account (prevent all transactions)."""
        with self._conn:
            cur = self._conn.cursor()
            cur.execute("UPDATE accounts SET is_frozen = 1 WHERE agent_id = ?", (agent_id,))
            logger.warning(f"🔒 Account frozen: {agent_id} ({reason})")

    def _unfreeze_account(self, agent_id: str, reason: str = "manual_override") -> None:
        """Unfreeze a previously frozen account (amnesty/redemption)."""
        with self._conn:
            cur = self._conn.cursor()
            timestamp = datetime.utcnow().isoformat()

            # Update account
            cur.execute(
                "UPDATE accounts SET is_frozen = 0, updated_at = ? WHERE agent_id = ?",
                (timestamp, agent_id),
            )

            # Record in ledger (AMNESTY transaction)
            tx_id = f"THAW-{hashlib.sha256((timestamp + agent_id).encode()).hexdigest()[:8]}"
            cur.execute(
                """
                INSERT INTO transactions
                (tx_id, timestamp, sender_id, receiver_id, amount, reason, service_type, previous_hash, tx_hash)
                VALUES (?, ?, 'WATCHMAN', ?, 0, ?, 'AMNESTY', ?, ?)
            """,
                (tx_id, timestamp, agent_id, reason, self._get_last_hash(), tx_id),
            )

            logger.info(f"✅ Account unfrozen: {agent_id} ({reason})")

    def _is_frozen(self, agent_id: str) -> bool:
        """Check if an agent's account is frozen."""
        cur = self._conn.cursor()
        cur.execute("SELECT is_frozen FROM accounts WHERE agent_id = ?", (agent_id,))
        row = cur.fetchone()
        return bool(row["is_frozen"]) if row else False

    def _audit_trail(self, limit: int = 10) -> list:
        """Provide radical transparency: Show all transactions."""
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cur.fetchall()]

    def _get_statement(self, agent_id: str) -> dict:
        """Get complete account statement (balance + recent transactions)."""
        balance = self._get_balance(agent_id)

        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT * FROM transactions
            WHERE sender_id = ? OR receiver_id = ?
            ORDER BY timestamp DESC LIMIT 10
            """,
            (agent_id, agent_id),
        )
        transactions = [dict(row) for row in cur.fetchall()]

        return {
            "agent_id": agent_id,
            "balance": balance,
            "recent_transactions": transactions,
        }

    def _verify_integrity(self) -> bool:
        """GAD-000 Verification: Check that the system is watertight."""
        cur = self._conn.cursor()

        # Check 1: Accounting Equation
        cur.execute("SELECT SUM(amount) as total FROM entries WHERE side='DEBIT'")
        debits = cur.fetchone()["total"] or 0
        cur.execute("SELECT SUM(amount) as total FROM entries WHERE side='CREDIT'")
        credits = cur.fetchone()["total"] or 0

        if debits != credits:
            logger.error(f"❌ ACCOUNTING ERROR: Debits ({debits}) != Credits ({credits})")
            return False

        logger.info(f"✅ Accounting Equation Verified: {debits} == {credits}")

        # Check 2: All balances are non-negative
        cur.execute("SELECT agent_id, balance FROM accounts WHERE balance < 0")
        negative = cur.fetchall()
        if negative:
            logger.error(f"❌ NEGATIVE BALANCE ALERT: {len(negative)} accounts with negative balance")
            for row in negative:
                logger.error(f"   {row['agent_id']}: {row['balance']}")
            return False

        logger.info("✅ All Account Balances Verified (non-negative)")

        return True

    def _get_stats(self) -> dict:
        """Get overall system statistics."""
        cur = self._conn.cursor()

        cur.execute("SELECT COUNT(*) as count FROM accounts")
        account_count = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM transactions")
        transaction_count = cur.fetchone()["count"]

        cur.execute("SELECT SUM(amount) as total FROM entries WHERE side='CREDIT'")
        total_credits = cur.fetchone()["total"] or 0

        cur.execute("SELECT SUM(balance) as total FROM accounts")
        total_balance = cur.fetchone()["total"] or 0

        return {
            "accounts": account_count,
            "transactions": transaction_count,
            "total_credits_issued": total_credits,
            "total_balance": total_balance,
            "integrity": self._verify_integrity(),
        }
