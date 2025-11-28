"""
THE CIVIC VAULT - Secure Asset Management System

Philosophy:
"API Keys are not owned by Agents. They are ASSETS of the collective.
Agents must LEASE them using Credits. Every access is logged.
This is radical transparency without radical exposure."

Implementation:
- Symmetric encryption using Fernet (cryptography library)
- Encrypted storage in SQLite (vault_assets table)
- Leasing system tied to Agent Credit balance
- Immutable audit trail of every access
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Lazy import for cryptography to prevent import-time crashes
Fernet = None
InvalidToken = None
import_error = None

logger = logging.getLogger("CIVIC_VAULT")


class VaultError(Exception):
    """Raised when vault operations fail."""
    pass


class InsufficientFundsError(Exception):
    """Raised when Agent lacks credits to lease a secret."""
    pass


class SecretNotFoundError(Exception):
    """Raised when a secret doesn't exist in the vault."""
    pass


class CivicVault:
    """
    THE CIVIC VAULT - Secure Asset Management.

    Agents do not own API Keys. They LEASE them from the collective vault.
    Every lease costs Credits and is logged immutably.

    Schema:
    - vault_assets: Encrypted secret storage
      - key_name (TEXT PRIMARY KEY): "tavily_api", "openai_api", etc.
      - encrypted_value (BLOB): Fernet-encrypted secret
      - created_at (DATETIME)
      - rotated_at (DATETIME)

    - vault_leases: Audit trail
      - id (INTEGER PRIMARY KEY)
      - agent_id (TEXT)
      - key_name (TEXT)
      - lease_time (DATETIME)
      - credits_charged (INTEGER)
      - tx_id (TEXT) -> links to CivicBank.transactions
    """

    MASTER_KEY_PATH = Path("data/security/master.key")
    LEASE_COST = 5  # Credits per lease

    def __init__(self, db_connection):
        """
        Initialize the Vault.

        Args:
            db_connection: SQLite connection from CivicBank
        """
        # Lazy load cryptography
        global Fernet, InvalidToken, import_error
        if Fernet is None:
            try:
                from cryptography.fernet import Fernet, InvalidToken
            except (ImportError, Exception) as e:
                import_error = str(e)
                raise ImportError(
                    "❌ cryptography library failed to initialize. "
                    f"Error: {import_error}"
                )

        self.conn = db_connection
        self._ensure_master_key()
        self._init_schema()
        logger.info("🔐 CIVIC VAULT initialized")

    def _ensure_master_key(self) -> str:
        """
        Ensure a Master Key exists. If not, generate one.

        Returns:
            Master Key (bytes, base64-encoded)
        """
        self.MASTER_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

        if self.MASTER_KEY_PATH.exists():
            with open(self.MASTER_KEY_PATH, 'rb') as f:
                master_key = f.read()
            logger.debug("✅ Master Key loaded from disk")
            return master_key
        else:
            # Generate new Master Key
            master_key = Fernet.generate_key()
            with open(self.MASTER_KEY_PATH, 'wb') as f:
                f.write(master_key)
            # Restrict permissions (Unix)
            os.chmod(self.MASTER_KEY_PATH, 0o600)
            logger.info(f"🔑 New Master Key generated at {self.MASTER_KEY_PATH}")
            return master_key

    def _get_cipher(self) -> Fernet:
        """Get Fernet cipher using Master Key."""
        with open(self.MASTER_KEY_PATH, 'rb') as f:
            master_key = f.read()
        return Fernet(master_key)

    def _init_schema(self):
        """Initialize vault tables in SQLite."""
        cur = self.conn.cursor()

        # 1. VAULT_ASSETS (The Encrypted Safe)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_assets (
                key_name TEXT PRIMARY KEY,
                encrypted_value BLOB NOT NULL,
                created_at DATETIME,
                rotated_at DATETIME
            )
        """)

        # 2. VAULT_LEASES (The Access Log)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_leases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                key_name TEXT,
                lease_time DATETIME,
                credits_charged INTEGER,
                tx_id TEXT,
                FOREIGN KEY(key_name) REFERENCES vault_assets(key_name)
            )
        """)

        self.conn.commit()
        logger.debug("✅ Vault schema initialized")

    def store_secret(self, key_name: str, raw_value: str) -> None:
        """
        Store a secret in the vault (encrypted).

        Args:
            key_name: Identifier (e.g., "tavily_api")
            raw_value: Plain-text secret value

        Raises:
            VaultError: If encryption fails
        """
        try:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(raw_value.encode('utf-8'))

            cur = self.conn.cursor()
            now = datetime.now().isoformat()

            cur.execute("""
                INSERT OR REPLACE INTO vault_assets
                (key_name, encrypted_value, created_at, rotated_at)
                VALUES (?, ?, ?, ?)
            """, (key_name, encrypted, now, now))

            self.conn.commit()
            logger.info(f"✅ Secret stored in vault: {key_name}")

        except Exception as e:
            raise VaultError(f"❌ Failed to store secret '{key_name}': {e}")

    def get_secret(self, key_name: str) -> str:
        """
        Retrieve a secret from the vault (decrypted).

        This is a LOW-LEVEL method used only by lease_secret.
        Agents should NEVER call this directly.

        Args:
            key_name: Identifier

        Returns:
            Decrypted secret value

        Raises:
            SecretNotFoundError: If secret doesn't exist
            VaultError: If decryption fails
        """
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT encrypted_value FROM vault_assets WHERE key_name = ?", (key_name,))
            row = cur.fetchone()

            if not row:
                raise SecretNotFoundError(f"❌ Secret not found: {key_name}")

            encrypted_value = row[0]
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(encrypted_value).decode('utf-8')

            return decrypted

        except InvalidToken:
            raise VaultError(f"❌ Decryption failed for '{key_name}' (corrupted or wrong key)")
        except Exception as e:
            raise VaultError(f"❌ Failed to retrieve secret '{key_name}': {e}")

    def lease_secret(
        self,
        agent_id: str,
        key_name: str,
        bank=None  # CivicBank instance for charging credits
    ) -> str:
        """
        Lease a secret to an Agent (requires Credits).

        This is the PRIMARY interface for Agents. They must have sufficient
        Credits to lease a secret. Every lease is logged.

        Args:
            agent_id: Agent requesting the secret
            key_name: Identifier of the secret
            bank: CivicBank instance for credit deduction

        Returns:
            Decrypted secret value (temporary use only)

        Raises:
            SecretNotFoundError: If secret doesn't exist
            InsufficientFundsError: If Agent lacks Credits
            VaultError: If anything else fails
        """
        try:
            # 1. Check if secret exists
            secret = self.get_secret(key_name)

            # 2. If bank is provided, charge the Agent
            if bank is not None:
                try:
                    # Deduct lease cost
                    tx_id = bank.transfer(
                        sender=agent_id,
                        receiver="VAULT",
                        amount=self.LEASE_COST,
                        reason=f"LEASE_SECRET_{key_name}",
                        service_type="lease"
                    )
                except Exception as bank_error:
                    # Check if it's an insufficient funds error
                    if "insufficient" in str(bank_error).lower():
                        raise InsufficientFundsError(
                            f"❌ Agent '{agent_id}' lacks {self.LEASE_COST} Credits "
                            f"to lease secret '{key_name}'"
                        )
                    raise VaultError(f"❌ Bank transaction failed: {bank_error}")
            else:
                tx_id = "MOCK_TX" # For testing without bank

            # 3. Log the lease access
            cur = self.conn.cursor()
            now = datetime.now().isoformat()
            cur.execute("""
                INSERT INTO vault_leases
                (agent_id, key_name, lease_time, credits_charged, tx_id)
                VALUES (?, ?, ?, ?, ?)
            """, (agent_id, key_name, now, self.LEASE_COST, tx_id))
            self.conn.commit()

            logger.info(
                f"🔓 Secret leased: {agent_id} <- {key_name} "
                f"({self.LEASE_COST} Credits via {tx_id})"
            )

            return secret

        except (SecretNotFoundError, InsufficientFundsError):
            raise
        except Exception as e:
            raise VaultError(f"❌ Lease failed: {e}")

    def lease_history(self, agent_id: str = None, limit: int = 10) -> list:
        """
        Get lease access history (audit trail).

        Args:
            agent_id: Filter by agent (None = all agents)
            limit: Max records to return

        Returns:
            List of lease records
        """
        cur = self.conn.cursor()

        if agent_id:
            cur.execute("""
                SELECT agent_id, key_name, lease_time, credits_charged, tx_id
                FROM vault_leases
                WHERE agent_id = ?
                ORDER BY lease_time DESC
                LIMIT ?
            """, (agent_id, limit))
        else:
            cur.execute("""
                SELECT agent_id, key_name, lease_time, credits_charged, tx_id
                FROM vault_leases
                ORDER BY lease_time DESC
                LIMIT ?
            """, (limit,))

        rows = cur.fetchall()
        return [
            {
                "agent_id": row[0],
                "key_name": row[1],
                "lease_time": row[2],
                "credits_charged": row[3],
                "tx_id": row[4]
            }
            for row in rows
        ]

    def rotate_secret(self, key_name: str, new_value: str) -> None:
        """
        Rotate (update) a secret.

        Args:
            key_name: Identifier
            new_value: New secret value
        """
        try:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(new_value.encode('utf-8'))

            cur = self.conn.cursor()
            now = datetime.now().isoformat()

            cur.execute("""
                UPDATE vault_assets
                SET encrypted_value = ?, rotated_at = ?
                WHERE key_name = ?
            """, (encrypted, now, key_name))

            self.conn.commit()
            logger.info(f"✅ Secret rotated: {key_name}")

        except Exception as e:
            raise VaultError(f"❌ Failed to rotate secret '{key_name}': {e}")

    def list_assets(self) -> list:
        """
        List all asset names (NOT values) in the vault.

        Returns:
            List of key names
        """
        cur = self.conn.cursor()
        cur.execute("SELECT key_name, created_at, rotated_at FROM vault_assets")
        rows = cur.fetchall()

        return [
            {
                "key_name": row[0],
                "created_at": row[1],
                "rotated_at": row[2]
            }
            for row in rows
        ]
