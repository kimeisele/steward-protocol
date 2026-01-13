"""
VASUKI PROTOCOL - The Binding Rope (Layer 0.8)

"Vasuki" - The Serpent Rope used in Samudra Manthan.
He binds the data (Encryption/Hashing) so it can be churned.

Responsibilities:
1. HASH: Reduce arbitrary data to a digest (Poison).
2. SIGN: Bind identity to data.
3. VERIFY: Detect corruption (Venom).

INHERITANCE:
- Inherits from NagaBase (Devotee).
- Protected by Balarama (Shield).

STATUS: DEVOTEE / ACTIVE BINDER
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x1a990609"  # GenesisByte: parampara % 37 == 0

import hashlib
import hmac
import json
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Union, TypedDict

from vibe_core.protocols.naga.base import NagaBase

# Re-export types
from vibe_core.protocols.naga.types import NagaStatus, NagaType

# Vasuki Capabilities
VASUKI_CAPS = ("hash", "sign", "verify")


class NodeAddress(TypedDict):
    """Network address of a node."""
    host: str
    port: int
    protocol: str
    node_id: str


class SendStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class SendResult(TypedDict):
    """Result of a send operation."""
    status: SendStatus
    message_id: str
    timestamp: str
    error: Optional[str]


class SignedEnvelope(TypedDict):
    """A signed message envelope."""
    payload: str  # Serialized data
    signature: str
    hash: str
    signer_id: str
    timestamp: str


class IntegrityError(Exception):
    """Vasuki bites: The data is corrupted or unsigned."""

    pass


class Vasuki(NagaBase):
    """
    The Vasuki Service (Cryptographer).

    A Devotee Naga that:
    - Hashes (Reduces to Essence).
    - Signs (Binds to Identity).
    - Verifies (Rejects Corruption).
    """

    def __init__(self, secret_key: str = "sovereign_mock_key"):
        super().__init__(name="vasuki", capabilities=VASUKI_CAPS)
        self._secret_key = secret_key.encode("utf-8")

    # =========================================================================
    # GENERIC SERVICE (SEVA)
    # =========================================================================

    def serve(self, request: Any) -> Any:
        """
        Generic entry point.
        """
        if not isinstance(request, dict):
            return "UNKNOWN REQUEST"

        action = request.get("action")
        data = request.get("data")
        signature = request.get("signature")

        if action == "hash":
            return self.hash_data(data)
        elif action == "sign":
            return self.sign_data(data)
        elif action == "verify":
            # Might raise IntegrityError
            self.verify_data(data, signature)
            return "VERIFIED"

        return "UNKNOWN ACTION"

    # =========================================================================
    # CAPABILITY 1: HASH (THE POISON)
    # =========================================================================

    def hash_data(self, data: Any) -> str:
        """
        Reduce data to SHA-256 digest.
        """
        serialized = self._serialize(data)
        return hashlib.sha256(serialized).hexdigest()

    # =========================================================================
    # CAPABILITY 2: SIGN (THE BIND)
    # =========================================================================

    def sign_data(self, data: Any) -> str:
        """
        Sign data using HMAC-SHA256 (Mock Key).

        This represents binding the data to the Sovereign Identity.
        """
        serialized = self._serialize(data)
        signature = hmac.new(self._secret_key, serialized, hashlib.sha256).hexdigest()
        return signature

    # =========================================================================
    # CAPABILITY 3: VERIFY (THE VENOM)
    # =========================================================================

    def verify_data(self, data: Any, signature: str) -> bool:
        """
        Verify data integrity.

        If invalid, Vasuki BITES (Raises IntegrityError).
        He does not tolerate corruption.
        """
        if not signature:
            raise IntegrityError("NO SIGNATURE: Data is unbound.")

        expected = self.sign_data(data)

        # Constant time comparison to avoid timing attacks
        if not hmac.compare_digest(expected, signature):
            raise IntegrityError("INVALID SIGNATURE: Data is corrupted.")

        return True

    # =========================================================================
    # HELPER
    # =========================================================================

    def _serialize(self, data: Any) -> bytes:
        """Canonical serialization."""
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode("utf-8")

        # JSON canonical sort keys
        return json.dumps(data, sort_keys=True).encode("utf-8")


# =============================================================================
# NULL IMPLEMENTATION (The Loose Rope)
# =============================================================================


class NullVasuki:
    """
    The Loose Rope.
    Returns defaults, binds nothing.
    Used for testing without crypto requirements.
    """

    def hash_data(self, data: Any) -> str:
        return "0x00_NULL_HASH"

    def sign_data(self, data: Any) -> str:
        return "0x00_NULL_SIGNATURE"

    def verify_data(self, data: Any, signature: str) -> bool:
        return True  # Accept everything

    def serve(self, request: Any) -> Any:
        return "NULL_VASUKI_RESPONSE"


# PROTOCOL ALIAS (For strict typing compliance)
VasukiProtocol = Vasuki

