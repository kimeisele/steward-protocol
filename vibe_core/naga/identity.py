"""
NAGA Identity - Sovereign cryptographic identity for NAGA services.

GAD-000 37th Principle: "No operation in the 36 fields is valid without
being signed by the 37th entity (Sovereign Identity)."

Each NAGA (Sesha, Vasuki, Takshaka, Cortex) has a sovereign identity
that signs its decisions. This enables:
- Verification of who made a decision
- Non-repudiation of NAGA actions
- Audit trail with cryptographic proof
"""

import base64
import hashlib
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("NAGA.IDENTITY")


@dataclass
class NagaIdentity:
    """
    Sovereign identity for a NAGA service (GAD-000 37th Principle).

    Each NAGA has an ECDSA P-256 keypair that signs its decisions.
    The fingerprint is the SHA256 of the public key.
    """

    agent_id: str
    public_key: str  # PEM format
    private_key: str  # PEM format
    fingerprint: str  # SHA256 of public key

    @classmethod
    def generate(cls, agent_id: str) -> "NagaIdentity":
        """
        Generate a new NAGA identity with ECDSA P-256 keypair.

        Args:
            agent_id: Identifier for this NAGA (e.g., "naga_cortex")

        Returns:
            NagaIdentity with generated keys
        """
        try:
            from ecdsa import NIST256p, SigningKey
        except ImportError:
            logger.error("ecdsa library not installed")
            raise ImportError("ecdsa library required: pip install ecdsa")

        sk = SigningKey.generate(curve=NIST256p)
        vk = sk.get_verifying_key()

        private_key = sk.to_pem().decode()
        public_key = vk.to_pem().decode()
        fingerprint = hashlib.sha256(public_key.encode()).hexdigest()[:16]

        logger.info(f"🐍 NAGA Identity generated: {agent_id} ({fingerprint})")

        return cls(
            agent_id=agent_id,
            public_key=public_key,
            private_key=private_key,
            fingerprint=fingerprint,
        )

    @classmethod
    def from_keys(cls, agent_id: str, private_key: str, public_key: str) -> "NagaIdentity":
        """Load identity from existing keys."""
        fingerprint = hashlib.sha256(public_key.encode()).hexdigest()[:16]
        return cls(
            agent_id=agent_id,
            public_key=public_key,
            private_key=private_key,
            fingerprint=fingerprint,
        )

    def sign(self, payload: bytes) -> bytes:
        """
        Sign a payload with this NAGA's private key.

        Args:
            payload: Bytes to sign

        Returns:
            Signature as bytes
        """
        try:
            from ecdsa import SigningKey
            from ecdsa.util import sigencode_string
        except ImportError:
            raise ImportError("ecdsa library required")

        sk = SigningKey.from_pem(self.private_key)
        signature = sk.sign_deterministic(
            payload,
            hashfunc=hashlib.sha256,
            sigencode=sigencode_string,
        )
        return signature

    def verify(self, payload: bytes, signature: bytes) -> bool:
        """
        Verify a signature against this NAGA's public key.

        Args:
            payload: Original bytes that were signed
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        try:
            from ecdsa import BadSignatureError, VerifyingKey
            from ecdsa.util import sigdecode_string
        except ImportError:
            return False

        try:
            vk = VerifyingKey.from_pem(self.public_key)
            vk.verify(
                signature,
                payload,
                hashfunc=hashlib.sha256,
                sigdecode=sigdecode_string,
            )
            return True
        except BadSignatureError:
            return False
        except Exception as e:
            logger.warning(f"Signature verification failed: {type(e).__name__}: {e}")
            return False

    def sign_b64(self, payload: bytes) -> str:
        """Sign and return base64-encoded signature."""
        sig = self.sign(payload)
        return base64.b64encode(sig).decode()

    def verify_b64(self, payload: bytes, signature_b64: str) -> bool:
        """Verify a base64-encoded signature."""
        try:
            sig = base64.b64decode(signature_b64)
            return self.verify(payload, sig)
        except Exception:
            return False

    def get_status(self) -> dict:
        """Get identity status for observability."""
        return {
            "agent_id": self.agent_id,
            "fingerprint": self.fingerprint,
            "has_private_key": bool(self.private_key),
            "has_public_key": bool(self.public_key),
        }


# =============================================================================
# NAGA FEDERATION IDENTITY
# =============================================================================


class NagaFederationIdentity:
    """
    Shared identity for the entire NAGA Federation.

    All NAGAs in a federation share the same signing key.
    This simplifies verification while maintaining sovereignty.
    """

    _instance: Optional["NagaFederationIdentity"] = None

    def __init__(self, identity: NagaIdentity):
        self._identity = identity

    @classmethod
    def initialize(cls, identity: Optional[NagaIdentity] = None) -> "NagaFederationIdentity":
        """Initialize the federation identity (singleton)."""
        if cls._instance is None:
            if identity is None:
                identity = NagaIdentity.generate("naga_federation")
            cls._instance = cls(identity)
            logger.info(f"🐍 NAGA Federation Identity: {identity.fingerprint}")
        return cls._instance

    @classmethod
    def get(cls) -> Optional["NagaFederationIdentity"]:
        """Get the federation identity if initialized."""
        return cls._instance

    @property
    def identity(self) -> NagaIdentity:
        """Get the underlying identity."""
        return self._identity

    def sign(self, payload: bytes) -> bytes:
        """Sign with federation identity."""
        return self._identity.sign(payload)

    def verify(self, payload: bytes, signature: bytes) -> bool:
        """Verify with federation identity."""
        return self._identity.verify(payload, signature)
