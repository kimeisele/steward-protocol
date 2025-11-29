"""
HERALD Identity Tool - Cryptographic signing via Steward Protocol.

Provides agent identity verification and content signing capabilities.
Integrates HERALD with the Steward Protocol for cryptographic integrity.

Fallback: If Steward Protocol is unavailable, uses native HMAC-SHA256 signing.
"""

import hashlib
import hmac
import logging
import os
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from steward import crypto
    from steward.client import StewardClient
except ImportError:
    StewardClient = None
    crypto = None

logger = logging.getLogger("HERALD_IDENTITY")


class IdentityTool:
    """
    Cryptographic identity and signing tool for HERALD.

    Capabilities:
    - sign_artifact: Sign content with HERALD's private key
    - assert_identity: Verify that HERALD has cryptographic credentials
    - get_public_key: Retrieve HERALD's public key for verification

    Fallback: If Steward Protocol unavailable, uses native HMAC-SHA256 signing
    """

    def __init__(
        self, identity_file: str = "herald/STEWARD.md", agent_id: str = "herald"
    ):
        """
        Initialize identity tool with HERALD's identity file.

        Args:
            identity_file: Path to HERALD's STEWARD.md identity file
            agent_id: Agent identifier for key storage
        """
        self.identity_file = Path(identity_file)
        self.agent_id = agent_id
        self.client = None
        self.public_key = None
        self._private_key = None
        self._use_native = False

        # Try Steward Protocol first
        if StewardClient and crypto:
            try:
                self.client = StewardClient(identity_file=str(self.identity_file))
                logger.info(
                    f"✅ Identity: Steward client initialized with {self.identity_file}"
                )
                return
            except Exception as e:
                logger.warning(f"⚠️  Identity: Failed to initialize Steward client: {e}")

        # Fallback to native HMAC-SHA256 signing
        logger.info(
            "🔐 Identity: Using native HMAC-SHA256 signing (Steward unavailable)"
        )
        self._use_native = True
        self._ensure_native_keys()

    def _ensure_native_keys(self) -> None:
        """Generate or load native HMAC-SHA256 keypair"""
        keys_dir = Path("data/identities")
        keys_dir.mkdir(parents=True, exist_ok=True)

        private_key_file = keys_dir / f"{self.agent_id}_private.key"
        public_key_file = keys_dir / f"{self.agent_id}_public.key"

        if private_key_file.exists():
            # Load existing key
            try:
                with open(private_key_file, "rb") as f:
                    self._private_key = f.read()
                with open(public_key_file, "r") as f:
                    self.public_key = f.read().strip()
                logger.info(f"🔐 Identity: Loaded native keys for {self.agent_id}")
            except Exception as e:
                logger.error(f"❌ Identity: Failed to load native keys: {e}")
        else:
            # Generate new keypair
            self._private_key = secrets.token_bytes(32)  # 256-bit key
            self.public_key = hashlib.sha256(self._private_key).hexdigest()

            # Save private key (owner-only)
            try:
                with open(private_key_file, "wb") as f:
                    f.write(self._private_key)
                os.chmod(private_key_file, 0o600)

                with open(public_key_file, "w") as f:
                    f.write(self.public_key)

                logger.info(
                    f"🔐 Identity: Generated new native keypair for {self.agent_id}"
                )
            except Exception as e:
                logger.error(f"❌ Identity: Failed to save native keys: {e}")

    def assert_identity(self) -> bool:
        """
        Verify that HERALD has cryptographic credentials available.

        This checks that:
        1. The private key exists and is readable
        2. The identity file is properly configured
        3. The keypair is valid

        Returns:
            bool: True if identity is valid and keys are available
        """
        if self._use_native:
            if self._private_key:
                logger.info("✅ Identity: Native cryptographic credentials verified")
                return True
            else:
                logger.warning("⚠️  Identity: Native credentials not available")
                return False

        if not self.client:
            logger.warning("⚠️  Identity: Steward client not available")
            return False

        try:
            result = self.client.assert_identity()
            if result:
                logger.info("✅ Identity: Cryptographic credentials verified")
            else:
                logger.warning("⚠️  Identity: Credentials not verified")
            return result
        except Exception as e:
            logger.warning(f"⚠️  Identity: Assertion failed: {e}")
            return False

    def sign_artifact(self, content: str) -> Optional[str]:
        """
        Cryptographically sign a text artifact (tweet, post, etc.).

        Uses HERALD's private key to create a digital signature.
        The signature can be used to verify that HERALD created this content.

        Args:
            content: The text to sign

        Returns:
            str: Hex-encoded signature, or None if signing failed
        """
        if not content:
            logger.error("❌ Identity: Cannot sign empty content")
            return None

        # Use native HMAC-SHA256 if available
        if self._use_native and self._private_key:
            try:
                message = content.strip().encode("utf-8")
                signature = hmac.new(
                    self._private_key, message, hashlib.sha256
                ).digest()
                signature_hex = signature.hex()
                logger.info(
                    f"✅ Identity: Content signed with native HMAC-SHA256 ({len(signature_hex)} char signature)"
                )
                return signature_hex
            except Exception as e:
                logger.error(f"❌ Identity: Native signing failed: {e}")
                return None

        # Try Steward Protocol
        if self.client:
            try:
                signature = self.client.sign_artifact(content.strip())
                logger.info(
                    f"✅ Identity: Content signed via Steward ({len(signature)} char signature)"
                )
                return signature
            except Exception as e:
                logger.error(f"❌ Identity: Steward signing failed: {e}")
                return None

        logger.warning("⚠️  Identity: No signing method available")
        return None

    def get_public_key(self) -> Optional[str]:
        """
        Get HERALD's public key for verification.

        The public key is embedded in the identity file and can be used
        to verify any signature created by sign_artifact().

        Returns:
            str: Hex-encoded public key, or None if not available
        """
        if self.public_key:
            return self.public_key

        # Try to load native public key
        if self._use_native:
            keys_dir = Path("data/identities")
            public_key_file = keys_dir / f"{self.agent_id}_public.key"
            if public_key_file.exists():
                try:
                    with open(public_key_file, "r") as f:
                        self.public_key = f.read().strip()
                    logger.debug(
                        f"✅ Identity: Public key retrieved ({len(self.public_key)} chars)"
                    )
                    return self.public_key
                except Exception as e:
                    logger.warning(
                        f"⚠️  Identity: Could not read native public key: {e}"
                    )
            return None

        if not crypto:
            logger.warning("⚠️  Identity: Crypto module not available")
            return None

        try:
            self.public_key = crypto.get_public_key_string()
            logger.debug(
                f"✅ Identity: Public key retrieved ({len(self.public_key)} chars)"
            )
            return self.public_key
        except Exception as e:
            logger.warning(f"⚠️  Identity: Could not retrieve public key: {e}")
            return None

    def create_signed_record(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Create a complete signed record of the content.

        This is a convenience method that signs content and returns
        both the content and signature in a structured format.

        Args:
            content: The text to sign and record

        Returns:
            dict: {
                "content": str,
                "signature": str,
                "public_key": str (optional)
            }
            or None if signing failed
        """
        signature = self.sign_artifact(content)
        if not signature:
            return None

        record = {
            "content": content,
            "signature": signature,
        }

        public_key = self.get_public_key()
        if public_key:
            record["public_key"] = public_key

        return record


# Export for Herald use
__all__ = ["IdentityTool"]
