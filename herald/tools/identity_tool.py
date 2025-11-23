"""
HERALD Identity Tool - Cryptographic signing via Steward Protocol.

Provides agent identity verification and content signing capabilities.
Integrates HERALD with the Steward Protocol for cryptographic integrity.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from steward.client import StewardClient
    from steward import crypto
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
    """

    def __init__(self, identity_file: str = "herald/STEWARD.md"):
        """
        Initialize identity tool with HERALD's identity file.

        Args:
            identity_file: Path to HERALD's STEWARD.md identity file
        """
        self.identity_file = Path(identity_file)
        self.client = None
        self.public_key = None

        if not StewardClient or not crypto:
            logger.warning("⚠️  Steward Protocol not available (not installed)")
            return

        try:
            self.client = StewardClient(identity_file=str(self.identity_file))
            logger.info(f"✅ Identity: Steward client initialized with {self.identity_file}")
        except Exception as e:
            logger.warning(f"⚠️  Identity: Failed to initialize Steward client: {e}")

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
            str: Base64-encoded signature, or None if signing failed
        """
        if not content:
            logger.error("❌ Identity: Cannot sign empty content")
            return None

        if not self.client:
            logger.warning("⚠️  Identity: Steward client not available, skipping signature")
            return None

        try:
            signature = self.client.sign_artifact(content.strip())
            logger.info(f"✅ Identity: Content signed ({len(signature)} char signature)")
            return signature
        except Exception as e:
            logger.error(f"❌ Identity: Signing failed: {e}")
            return None

    def get_public_key(self) -> Optional[str]:
        """
        Get HERALD's public key for verification.

        The public key is embedded in the identity file and can be used
        to verify any signature created by sign_artifact().

        Returns:
            str: Base64-encoded public key, or None if not available
        """
        if self.public_key:
            return self.public_key

        if not crypto:
            logger.warning("⚠️  Identity: Crypto module not available")
            return None

        try:
            self.public_key = crypto.get_public_key_string()
            logger.debug(f"✅ Identity: Public key retrieved ({len(self.public_key)} chars)")
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
