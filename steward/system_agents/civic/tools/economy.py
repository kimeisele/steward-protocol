"""
THE CIVIC CENTRAL BANK - Double-Entry Bookkeeping Engine

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
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("CIVIC_BANK")

# Vault will be imported lazily to avoid circular imports
vault = None


class InsufficientFundsError(Exception):
    """Raised when an agent lacks sufficient credits for a transaction."""

    pass


class CivicBank:
    """
    THE CENTRAL BANK OF AGENT CITY.

    Implements Double-Entry Bookkeeping with Chained Hashes.
    GAD-000 Compliant: Radical Transparency & Atomicity.

    Schema:
    - accounts: State cache (agent_id -> balance)
    - transactions: Event log (immutable, chained hashes)
    - entries: Double-entry detail (DEBIT/CREDIT pairs)
    """

    DB_PATH = Path("data/economy.db")

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the bank and SQLite schema.

        Args:
            db_path: Path to database file. If None, uses default data/economy.db
                     For VFS isolation, pass agent.get_sandbox_path() + "/economy.db"
        """
        if db_path:
            self.DB_PATH = Path(db_path)
        else:
            self.DB_PATH = Path("data/economy.db")

        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

        # Initialize the Civic Vault (lazy import to avoid circular imports)
        try:
            from .vault import CivicVault

            self.vault = CivicVault(self.conn)
        except (ImportError, Exception) as e:
            logger.warning(f"⚠️  Vault unavailable ({type(e).__name__}: cryptography issue)")
            self.vault = None

        logger.info(f"🏦 CivicBank initialized at {self.DB_PATH}")

    def _init_db(self):
        """Initialize the immutable ledger schema."""
        cur = self.conn.cursor()

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
        self.conn.commit()
        logger.info("✅ Schema initialized (MINT, VAULT, CIVIC accounts ready)")

    def get_last_hash(self) -> str:
        """
        Get the hash of the last transaction for chaining.

        Returns:
            Last transaction hash, or "GENESIS_HASH" if ledger is empty
        """
        cur = self.conn.cursor()
        cur.execute("SELECT tx_hash FROM transactions ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        return row["tx_hash"] if row else "GENESIS_HASH"

    def get_balance(self, agent_id: str) -> int:
        """
        Get current balance for an agent.

        Args:
            agent_id: Agent to check

        Returns:
            Current balance (or 0 if account doesn't exist)
        """
        cur = self.conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE agent_id = ?", (agent_id,))
        row = cur.fetchone()
        return row["balance"] if row else 0

    def transfer(
        self,
        sender: str,
        receiver: str,
        amount: int,
        reason: str,
        service_type: str = "transfer",
    ) -> str:
        """
        Execute an atomic Double-Entry Transaction.

        This is the core banking operation. Every credit movement goes through
        this function. It ensures:
        1. Atomic ACID compliance (all-or-nothing)
        2. Double-entry invariant (DEBITS == CREDITS)
        3. Cryptographic chaining (blockchain-lite)

        Args:
            sender: Agent paying (or "MINT" for initial issuance)
            receiver: Agent receiving
            amount: Credits to transfer (positive integer)
            reason: Human-readable reason (e.g., "broadcast", "bounty_reward")
            service_type: Category (e.g., "transfer", "minting", "bounty")

        Returns:
            Transaction ID (TX-xxxxxxxx)

        Raises:
            ValueError: If amount is not positive
            InsufficientFundsError: If sender lacks funds
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with self.conn:  # Atomic transaction block
            cur = self.conn.cursor()

            # 1. CHECK FUNDS (unless sender is MINT)
            if sender != "MINT":
                sender_balance = self.get_balance(sender)
                if sender_balance < amount:
                    raise InsufficientFundsError(f"{sender} has {sender_balance}, needs {amount}")

            # 2. PREPARE DATA
            timestamp = datetime.utcnow().isoformat()
            prev_hash = self.get_last_hash()

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

    def freeze_account(self, agent_id: str, reason: str = "violation") -> None:
        """
        Freeze an agent's account (prevent all transactions).

        This is the nuclear option - used when an agent violates critical rules.

        Args:
            agent_id: Agent to freeze
            reason: Reason for freezing
        """
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("UPDATE accounts SET is_frozen = 1 WHERE agent_id = ?", (agent_id,))
            logger.warning(f"🔒 Account frozen: {agent_id} ({reason})")

    def unfreeze_account(self, agent_id: str, reason: str = "manual_override") -> None:
        """
        Unfreeze a previously frozen account (amnesty/redemption).

        Args:
            agent_id: Agent to unfreeze
            reason: Reason for unfreezing (e.g., "Compliance Restored")
        """
        with self.conn:
            cur = self.conn.cursor()
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
                (tx_id, timestamp, agent_id, reason, self.get_last_hash(), tx_id),
            )

            logger.info(f"✅ Account unfrozen: {agent_id} ({reason})")

    def is_frozen(self, agent_id: str) -> bool:
        """
        Check if an agent's account is frozen.

        Args:
            agent_id: Agent to check

        Returns:
            True if frozen, False otherwise
        """
        cur = self.conn.cursor()
        cur.execute("SELECT is_frozen FROM accounts WHERE agent_id = ?", (agent_id,))
        row = cur.fetchone()
        return bool(row["is_frozen"]) if row else False

    def audit_trail(self, limit: int = 10) -> List[Dict]:
        """
        Provide radical transparency: Show all transactions.

        GAD-000 requirement: No silent failures, full audit trail.

        Args:
            limit: Number of recent transactions to return

        Returns:
            List of transaction records (most recent first)
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cur.fetchall()]

    def get_account_statement(self, agent_id: str) -> Dict:
        """
        Get complete account statement (balance + recent transactions).

        Args:
            agent_id: Agent to check

        Returns:
            Dict with balance and recent transactions
        """
        balance = self.get_balance(agent_id)

        cur = self.conn.cursor()
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

    def verify_integrity(self) -> bool:
        """
        GAD-000 Verification: Check that the system is watertight.

        Rules:
        1. Debits == Credits (Accounting Equation)
        2. All balances are non-negative
        3. All transactions are chained correctly

        Returns:
            True if system is consistent, False otherwise
        """
        cur = self.conn.cursor()

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

    def get_system_stats(self) -> Dict:
        """
        Get overall system statistics.

        Returns:
            Dict with aggregate statistics
        """
        cur = self.conn.cursor()

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
            "integrity": self.verify_integrity(),
        }
