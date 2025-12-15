"""
ARCHIVIST Verifier Tool
========================

REAL CRYPTOGRAPHIC VERIFICATION IMPLEMENTED.

This tool performs actual ECDSA P-256 signature verification using the
steward.crypto module. Signatures are verified against stored public keys.

Implementation:
1. Uses ECDSA NIST P-256 for signing/verification
2. Public keys loaded from agent registry (in-memory for MVP)
3. Signatures verified cryptographically - invalid signatures are rejected
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Tuple

logger = logging.getLogger("ARCHIVIST_VERIFIER")

# Import real crypto functions
try:
    from vibe_core.steward.crypto import get_public_key_string
    from vibe_core.steward.crypto import verify_signature as crypto_verify_signature

    CRYPTO_AVAILABLE = True
except ImportError:
    logger.error("❌ steward.crypto not available - verification will fail")
    CRYPTO_AVAILABLE = False

# Feature flag - ENABLED for real crypto
CRYPTO_ENABLED = True


class VerifierTool:
    """
    Content verification tool for the Chain of Trust.

    REAL CRYPTOGRAPHIC VERIFICATION ENABLED.
    Signatures are verified using ECDSA P-256 against agent public keys.

    VAJRA Wiring:
    - inject_kernel() for kernel binding
    - _get_ledger() for ledger access
    """

    # VAJRA: Kernel binding slot
    _vibe_kernel = None

    def __init__(self):
        self.logger = logger
        self.simulation_mode = not (CRYPTO_ENABLED and CRYPTO_AVAILABLE)

        if self.simulation_mode:
            self.logger.warning("Verifier Tool running in SIMULATION MODE - crypto module unavailable")
        else:
            self.logger.info("Verifier Tool initialized with REAL CRYPTO VERIFICATION")

        # Agent Public Key Registry (MVP: in-memory, hardcoded)
        # In production: Load from vibe_core.steward.json files or central registry
        self._load_agent_public_keys()

    def inject_kernel(self, kernel) -> None:
        """VAJRA: Inject kernel for ledger access."""
        self._vibe_kernel = kernel
        self.logger.info("VerifierTool: Kernel injected")

    def _get_ledger(self):
        """VAJRA: Get ledger from kernel (safe access)."""
        if self._vibe_kernel is None:
            return None
        return self._vibe_kernel.ledger

    def _load_agent_public_keys(self):
        """
        Load agent public keys from registry.

        MVP: Uses the system's public key for all known agents.
        Production: Load individual keys from agent steward.json files.
        """
        self.agent_public_keys = {}

        # Try to load system public key as default
        if CRYPTO_AVAILABLE:
            try:
                system_public_key = get_public_key_string()
                # For MVP: Use system key for all known agents
                # In production: Each agent would have their own key
                known_agents = ["HERALD_Agent", "ENVOY_Agent", "CIVIC_Agent", "ARCHIVIST_Agent"]
                for agent in known_agents:
                    self.agent_public_keys[agent] = system_public_key
                self.logger.info(f"✅ Loaded public keys for {len(known_agents)} agents")
            except Exception as e:
                self.logger.error(f"❌ Failed to load public keys: {e}")
                self.agent_public_keys = {}
        else:
            self.logger.warning("⚠️  Crypto unavailable - no public keys loaded")

    def verify_signature(self, content: str, signature: str, signer: str) -> Tuple[bool, str]:
        """
        Verify signature of content using REAL CRYPTOGRAPHIC VERIFICATION.

        Args:
            content: The original content that was signed
            signature: The signature to verify (base64)
            signer: The identity of the signer

        Returns:
            Tuple of (is_valid, verification_details)
        """
        self.logger.info(f"🔐 Verification request from: {signer}")

        # Check if signer is known
        if signer not in self.agent_public_keys:
            return False, f"❌ Unknown signer: {signer} (not in registry)"

        # Fallback to simulation mode if crypto unavailable
        if self.simulation_mode:
            if signature and len(signature) > 0:
                self.logger.warning(
                    f"⚠️  SIMULATION: Accepting signature from {signer} WITHOUT VERIFICATION (crypto unavailable)"
                )
                return True, f"[SIMULATION] Signature accepted from {signer} (NOT VERIFIED)"
            else:
                return False, f"❌ Empty signature from {signer}"

        # REAL CRYPTOGRAPHIC VERIFICATION
        try:
            public_key = self.agent_public_keys[signer]

            # Verify using steward.crypto module
            is_valid = crypto_verify_signature(content, signature, public_key)

            if is_valid:
                self.logger.info(f"✅ Signature VERIFIED for {signer} (ECDSA P-256)")
                return True, f"✅ Signature cryptographically verified from {signer}"
            else:
                self.logger.warning(f"❌ Signature INVALID for {signer}")
                return False, "❌ Signature verification FAILED - signature is invalid or tampered"

        except Exception as e:
            self.logger.error(f"❌ Verification error for {signer}: {e}")
            return False, f"❌ Verification error: {e}"

    def compute_content_hash(self, content: str) -> str:
        """
        Compute SHA-256 hash of content.
        This IS real - it's just hashing, not crypto verification.
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def create_verification_proof(self, verified_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create proof of verification attempt.

        Args:
            verified_content: The content that was verified

        Returns:
            Proof object with verification metadata

        NOTE: The 'verification_status' reflects whether cryptographic
        verification was performed (VERIFIED) or simulated.
        """
        self.logger.info("📜 Creating verification proof")

        proof = {
            "content_hash": self.compute_content_hash(str(verified_content)),
            "verifier_id": "ARCHIVIST_Agent",
            "verification_timestamp": datetime.now().isoformat(),
            "verification_status": "SIMULATED" if self.simulation_mode else "CRYPTOGRAPHICALLY_VERIFIED",
            "crypto_enabled": CRYPTO_ENABLED,
            "crypto_available": CRYPTO_AVAILABLE,
            "algorithm": "ECDSA-P256-SHA256" if not self.simulation_mode else None,
            "chain_of_trust_link": {
                "from_agent": verified_content.get("author", "unknown"),
                "to_agent": "ARCHIVIST_Agent",
                "relay_count": 1,
            },
            "warning": ("Signature verification was SIMULATED (crypto unavailable)" if self.simulation_mode else None),
        }

        return proof
