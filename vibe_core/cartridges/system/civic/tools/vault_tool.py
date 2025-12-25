"""
CIVIC VAULT TOOL - Secure Asset Management (Tool Protocol)

Kernel-managed vault for encrypted secret storage and leasing.
Implements graceful degradation - if cryptography fails, system continues.

Philosophy:
"API Keys are not owned by Agents. They are ASSETS of the collective.
Agents must LEASE them using Credits. Every access is logged.
This is radical transparency without radical exposure."

Rust Panic Protection:
The cryptography library uses Rust (via PyO3). If it panics, we catch it
with BaseException and return ToolResult(success=False). The system continues.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

# Lazy import for cryptography to prevent import-time crashes
Fernet = None
InvalidToken = None
_cryptography_checked = False
_cryptography_works = False

logger = logging.getLogger("CIVIC_VAULT_TOOL")


def _check_cryptography_available() -> bool:
    """
    Pre-check if cryptography library ACTUALLY works.

    This catches Rust panics BEFORE they crash the system.
    A well-designed program doesn't crash - it degrades gracefully.

    Returns:
        True if cryptography works, False otherwise
    """
    global Fernet, InvalidToken, _cryptography_checked, _cryptography_works

    if _cryptography_checked:
        return _cryptography_works

    _cryptography_checked = True

    try:
        from cryptography.fernet import Fernet as F
        from cryptography.fernet import InvalidToken as IT

        # Actually TEST it - import alone isn't enough!
        key = F.generate_key()
        cipher = F(key)
        encrypted = cipher.encrypt(b"test")
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == b"test"

        # It works! Set globals
        Fernet = F
        InvalidToken = IT
        _cryptography_works = True
        logger.debug("✅ cryptography library verified working")
        return True

    except BaseException as e:
        # Catches: ImportError, Exception, AND pyo3_runtime.PanicException
        logger.warning(f"⚠️  cryptography unavailable ({type(e).__name__}): {e}")
        _cryptography_works = False
        return False


class VaultTool(Tool):
    """
    CIVIC VAULT - Secure Asset Management Tool.

    Agents do not own API Keys. They LEASE them from the collective vault.
    Every lease costs Credits and is logged immutably.

    Actions:
    - store_secret: Store encrypted secret
    - lease_secret: Lease secret to agent (requires credits)
    - rotate_secret: Update existing secret
    - list_assets: List all stored keys (names only, not values)
    - lease_history: Get audit trail of leases
    """

    # OPUS-025: Template reference - actual path resolved from config or fallback
    _MASTER_KEY_PATH_DEFAULT = "data/security/master.key"
    MASTER_KEY_PATH = None  # Set dynamically in _ensure_master_key
    LEASE_COST = 5  # Credits per lease

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """Initialize Vault Tool (kernel-managed)."""
        super().__init__(services)
        self._bank_conn = None  # Will be injected by setter if needed
        self._crypto_available = None  # Lazy check

    @property
    def name(self) -> str:
        return "civic.vault"

    @property
    def description(self) -> str:
        return "Secure vault for encrypted API key storage and leasing"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'store_secret', 'lease_secret', 'rotate_secret', 'list_assets', 'lease_history'",
            },
            "key_name": {"type": "string", "required": False, "description": "Secret identifier (e.g., 'tavily_api')"},
            "value": {"type": "string", "required": False, "description": "Secret value (for store/rotate)"},
            "agent_id": {"type": "string", "required": False, "description": "Agent requesting lease"},
            "bank_connection": {
                "type": "object",
                "required": False,
                "description": "SQLite connection (for vault tables)",
            },
            "limit": {"type": "number", "required": False, "description": "Limit for lease_history"},
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        action = parameters.get("action")
        if not action:
            raise ValueError("Missing required parameter: action")

        valid_actions = ["store_secret", "lease_secret", "rotate_secret", "list_assets", "lease_history"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action '{action}'. Must be one of: {valid_actions}")

        # Action-specific validation
        if action in ["store_secret", "rotate_secret"]:
            if "key_name" not in parameters or "value" not in parameters:
                raise ValueError(f"Action '{action}' requires 'key_name' and 'value'")

        if action == "lease_secret":
            if "key_name" not in parameters or "agent_id" not in parameters:
                raise ValueError("Action 'lease_secret' requires 'key_name' and 'agent_id'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute vault operation with Rust panic protection.

        ALL cryptography operations are wrapped in try/except BaseException.
        If Rust panics, we return success=False instead of crashing.
        """
        action = parameters["action"]

        # Pre-check cryptography availability
        if self._crypto_available is None:
            self._crypto_available = _check_cryptography_available()

        if not self._crypto_available:
            return ToolResult(
                success=False,
                error="Vault unavailable: cryptography library not functional. "
                "System continues without encryption features.",
            )

        # Set bank connection if provided
        if "bank_connection" in parameters:
            self._bank_conn = parameters["bank_connection"]

        # Ensure schema exists (idempotent)
        try:
            self._init_schema()
        except BaseException as e:
            logger.error(f"❌ Vault schema init failed: {e}")
            return ToolResult(success=False, error=f"Vault schema initialization failed: {e}")

        # Route to action handlers
        try:
            if action == "store_secret":
                result = self._store_secret(parameters["key_name"], parameters["value"])
                return ToolResult(success=True, output=result)

            elif action == "lease_secret":
                secret = self._lease_secret(
                    agent_id=parameters["agent_id"],
                    key_name=parameters["key_name"],
                    bank=parameters.get("bank"),
                )
                return ToolResult(success=True, output={"secret": secret})

            elif action == "rotate_secret":
                result = self._rotate_secret(parameters["key_name"], parameters["value"])
                return ToolResult(success=True, output=result)

            elif action == "list_assets":
                assets = self._list_assets()
                return ToolResult(success=True, output={"assets": assets})

            elif action == "lease_history":
                history = self._lease_history(
                    agent_id=parameters.get("agent_id"),
                    limit=parameters.get("limit", 10),
                )
                return ToolResult(success=True, output={"history": history})

        except BaseException as e:
            # CRITICAL: Catch Rust panics and any other crashes
            logger.error(f"❌ Vault operation '{action}' failed: {type(e).__name__}: {e}")
            return ToolResult(success=False, error=f"Vault operation failed: {type(e).__name__}: {e}")

    def _ensure_master_key(self) -> bytes:
        """
        Ensure a Master Key exists. If not, generate one.

        Returns:
            Master Key (bytes, base64-encoded)
        """
        try:
            # OPUS-025: Resolve path from config if not set
            if self.MASTER_KEY_PATH is None:
                try:
                    from vibe_core.phoenix import get_config

                    config = get_config()
                    if config and hasattr(config, "paths"):
                        self.MASTER_KEY_PATH = config.paths.data.resolve("security_master_key")
                    else:
                        self.MASTER_KEY_PATH = Path(self._MASTER_KEY_PATH_DEFAULT)
                except Exception:
                    self.MASTER_KEY_PATH = Path(self._MASTER_KEY_PATH_DEFAULT)

            self.MASTER_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

            if self.MASTER_KEY_PATH.exists():
                with open(self.MASTER_KEY_PATH, "rb") as f:
                    master_key = f.read()
                logger.debug("✅ Master Key loaded from disk")
                return master_key
            else:
                # Generate new Master Key
                master_key = Fernet.generate_key()
                with open(self.MASTER_KEY_PATH, "wb") as f:
                    f.write(master_key)
                # Restrict permissions (Unix)
                os.chmod(self.MASTER_KEY_PATH, 0o600)
                logger.info(f"🔑 New Master Key generated at {self.MASTER_KEY_PATH}")
                return master_key

        except BaseException as e:
            logger.error(f"❌ Master key generation failed: {e}")
            raise

    def _get_cipher(self):
        """Get Fernet cipher using Master Key."""
        try:
            with open(self.MASTER_KEY_PATH, "rb") as f:
                master_key = f.read()
            return Fernet(master_key)
        except BaseException as e:
            logger.error(f"❌ Cipher init failed: {e}")
            raise

    def _init_schema(self):
        """Initialize vault tables in SQLite (idempotent)."""
        if not self._bank_conn:
            logger.warning("⚠️  No bank connection - vault schema init skipped")
            return

        try:
            cur = self._bank_conn.cursor()

            # 1. VAULT_ASSETS (The Encrypted Safe)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vault_assets (
                    key_name TEXT PRIMARY KEY,
                    encrypted_value BLOB NOT NULL,
                    created_at DATETIME,
                    rotated_at DATETIME
                )
            """
            )

            # 2. VAULT_LEASES (The Access Log)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vault_leases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    key_name TEXT,
                    lease_time DATETIME,
                    credits_charged INTEGER,
                    tx_id TEXT,
                    FOREIGN KEY(key_name) REFERENCES vault_assets(key_name)
                )
            """
            )

            self._bank_conn.commit()
            logger.debug("✅ Vault schema initialized")

        except BaseException as e:
            logger.error(f"❌ Vault schema init failed: {e}")
            raise

    def _store_secret(self, key_name: str, raw_value: str) -> dict:
        """
        Store a secret in the vault (encrypted).

        Raises on failure (caught by execute()).
        """
        try:
            # Ensure master key exists
            self._ensure_master_key()

            cipher = self._get_cipher()
            encrypted = cipher.encrypt(raw_value.encode("utf-8"))

            cur = self._bank_conn.cursor()
            now = datetime.now().isoformat()

            cur.execute(
                """
                INSERT OR REPLACE INTO vault_assets
                (key_name, encrypted_value, created_at, rotated_at)
                VALUES (?, ?, ?, ?)
            """,
                (key_name, encrypted, now, now),
            )

            self._bank_conn.commit()
            logger.info(f"✅ Secret stored in vault: {key_name}")

            return {"key_name": key_name, "status": "stored", "timestamp": now}

        except BaseException as e:
            logger.error(f"❌ Failed to store secret '{key_name}': {e}")
            raise

    def _get_secret(self, key_name: str) -> str:
        """
        Retrieve a secret from the vault (decrypted).

        This is a LOW-LEVEL method used only by _lease_secret.
        Agents should NEVER call this directly.
        """
        try:
            cur = self._bank_conn.cursor()
            cur.execute("SELECT encrypted_value FROM vault_assets WHERE key_name = ?", (key_name,))
            row = cur.fetchone()

            if not row:
                raise ValueError(f"Secret not found: {key_name}")

            encrypted_value = row[0]
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(encrypted_value).decode("utf-8")

            return decrypted

        except InvalidToken:
            raise ValueError(f"Decryption failed for '{key_name}' (corrupted or wrong key)")
        except BaseException as e:
            logger.error(f"❌ Failed to retrieve secret '{key_name}': {e}")
            raise

    def _lease_secret(self, agent_id: str, key_name: str, bank=None) -> str:
        """
        Lease a secret to an Agent (requires Credits).

        This is the PRIMARY interface for Agents. They must have sufficient
        Credits to lease a secret. Every lease is logged.

        Args:
            agent_id: Agent requesting the secret
            key_name: Identifier of the secret
            bank: CivicBank instance for credit deduction (optional)

        Returns:
            Decrypted secret value (temporary use only)

        Raises on failure (caught by execute()).
        """
        try:
            # 1. Check if secret exists
            secret = self._get_secret(key_name)

            # 2. If bank is provided, charge the Agent
            if bank is not None:
                try:
                    # Deduct lease cost
                    tx_id = bank.transfer(
                        sender=agent_id,
                        receiver="VAULT",
                        amount=self.LEASE_COST,
                        reason=f"LEASE_SECRET_{key_name}",
                        service_type="lease",
                    )
                except Exception as bank_error:
                    # Check if it's an insufficient funds error
                    if "insufficient" in str(bank_error).lower():
                        raise ValueError(
                            f"Agent '{agent_id}' lacks {self.LEASE_COST} Credits to lease secret '{key_name}'"
                        )
                    raise ValueError(f"Bank transaction failed: {bank_error}")
            else:
                tx_id = "MOCK_TX"  # For testing without bank

            # 3. Log the lease access
            cur = self._bank_conn.cursor()
            now = datetime.now().isoformat()
            cur.execute(
                """
                INSERT INTO vault_leases
                (agent_id, key_name, lease_time, credits_charged, tx_id)
                VALUES (?, ?, ?, ?, ?)
            """,
                (agent_id, key_name, now, self.LEASE_COST, tx_id),
            )
            self._bank_conn.commit()

            logger.info(f"🔓 Secret leased: {agent_id} <- {key_name} ({self.LEASE_COST} Credits via {tx_id})")

            return secret

        except BaseException as e:
            logger.error(f"❌ Lease failed: {e}")
            raise

    def _lease_history(self, agent_id: str = None, limit: int = 10) -> list:
        """
        Get lease access history (audit trail).

        Args:
            agent_id: Filter by agent (None = all agents)
            limit: Max records to return

        Returns:
            List of lease records
        """
        try:
            cur = self._bank_conn.cursor()

            if agent_id:
                cur.execute(
                    """
                    SELECT agent_id, key_name, lease_time, credits_charged, tx_id
                    FROM vault_leases
                    WHERE agent_id = ?
                    ORDER BY lease_time DESC
                    LIMIT ?
                """,
                    (agent_id, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT agent_id, key_name, lease_time, credits_charged, tx_id
                    FROM vault_leases
                    ORDER BY lease_time DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            rows = cur.fetchall()
            return [
                {
                    "agent_id": row[0],
                    "key_name": row[1],
                    "lease_time": row[2],
                    "credits_charged": row[3],
                    "tx_id": row[4],
                }
                for row in rows
            ]

        except BaseException as e:
            logger.error(f"❌ Lease history failed: {e}")
            raise

    def _rotate_secret(self, key_name: str, new_value: str) -> dict:
        """
        Rotate (update) a secret.

        Args:
            key_name: Identifier
            new_value: New secret value
        """
        try:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(new_value.encode("utf-8"))

            cur = self._bank_conn.cursor()
            now = datetime.now().isoformat()

            cur.execute(
                """
                UPDATE vault_assets
                SET encrypted_value = ?, rotated_at = ?
                WHERE key_name = ?
            """,
                (encrypted, now, key_name),
            )

            self._bank_conn.commit()
            logger.info(f"✅ Secret rotated: {key_name}")

            return {"key_name": key_name, "status": "rotated", "timestamp": now}

        except BaseException as e:
            logger.error(f"❌ Failed to rotate secret '{key_name}': {e}")
            raise

    def _list_assets(self) -> list:
        """
        List all asset names (NOT values) in the vault.

        Returns:
            List of key names with metadata
        """
        try:
            cur = self._bank_conn.cursor()
            cur.execute("SELECT key_name, created_at, rotated_at FROM vault_assets")
            rows = cur.fetchall()

            return [{"key_name": row[0], "created_at": row[1], "rotated_at": row[2]} for row in rows]

        except BaseException as e:
            logger.error(f"❌ List assets failed: {e}")
            raise
