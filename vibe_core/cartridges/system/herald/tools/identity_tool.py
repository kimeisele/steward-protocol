"""
HERALD Identity Tool - Cryptographic signing via Steward Protocol (Tool Protocol).

Provides agent identity verification and content signing capabilities.
Integrates HERALD with the Steward Protocol for cryptographic integrity.

Fallback: If Steward Protocol client is unavailable, uses steward/crypto.py ECDSA directly.
         SECURITY FIX (OPUS-018): Replaced HMAC-SHA256 with real asymmetric ECDSA.

This tool implements the Tool Protocol for kernel-managed execution.

SECURITY NOTE: Private key writes intentionally bypass the I/O Service.
              Key material should NOT be logged in the audit trail.
              Direct writes with restrictive permissions (0o600) are used instead.
              See: docs/architecture/KERNEL_IO_ARCHITECTURE.md
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

# SECURITY FIX (OPUS-018): Always import steward/crypto.py for ECDSA signing
# This replaces the insecure HMAC-SHA256 fallback
try:
    from vibe_core.steward.crypto import (
        get_public_key_fingerprint,
        load_or_generate_keys,
        sign_content,
    )

    STEWARD_CRYPTO_AVAILABLE = True
except ImportError:
    STEWARD_CRYPTO_AVAILABLE = False
    load_or_generate_keys = None
    sign_content = None
    get_public_key_fingerprint = None

try:
    from vibe_core.steward.client import StewardClient
except ImportError:
    StewardClient = None

logger = logging.getLogger("HERALD_IDENTITY")


class IdentityTool(Tool):
    """
    Cryptographic identity and signing tool for HERALD.

    Capabilities:
    - sign_artifact: Sign content with HERALD's private key
    - assert_identity: Verify that HERALD has cryptographic credentials
    - get_public_key: Retrieve HERALD's public key for verification

    Fallback: If Steward Protocol client unavailable, uses steward/crypto.py ECDSA directly.
    SECURITY: ECDSA signatures are asymmetric - verification without secret key.
    """

    def __init__(
        self,
        services: Optional["ServiceRegistry"] = None,
        identity_file: str = "herald/STEWARD.md",
        agent_id: str = "herald",
    ):
        """
        Initialize identity tool with HERALD's identity file.

        Args:
            services: ServiceRegistry for dependency injection
            identity_file: Path to HERALD's STEWARD.md identity file
            agent_id: Agent identifier for key storage
        """
        super().__init__(services)
        self.identity_file = Path(identity_file)
        self.agent_id = agent_id
        self.client = None
        self.public_key = None
        self._private_key = None
        self._use_native = False

        # Try Steward Protocol first (StewardClient for full integration)
        if StewardClient and STEWARD_CRYPTO_AVAILABLE:
            try:
                self.client = StewardClient(identity_file=str(self.identity_file))
                logger.info(f"✅ Identity: Steward client initialized with {self.identity_file}")
                return
            except Exception as e:
                logger.warning(f"⚠️  Identity: Failed to initialize Steward client: {e}")

        # Fallback to steward/crypto.py ECDSA (SECURITY FIX: replaced HMAC)
        if STEWARD_CRYPTO_AVAILABLE:
            logger.info("🔐 Identity: Using steward/crypto.py ECDSA (StewardClient unavailable)")
            self._use_native = True
            self._ensure_ecdsa_keys()
        else:
            logger.error("❌ Identity: NO CRYPTO AVAILABLE - steward/crypto.py not found!")
            self._use_native = False

    def _ensure_ecdsa_keys(self) -> None:
        """
        Load or generate ECDSA keypair using steward/crypto.py.

        SECURITY FIX (OPUS-018): Replaced HMAC-SHA256 with real ECDSA.
        Keys are stored at .steward/keys/ with proper permissions.
        """
        if not STEWARD_CRYPTO_AVAILABLE:
            logger.error("❌ Identity: steward/crypto.py not available")
            return

        try:
            # load_or_generate_keys() handles key storage at .steward/keys/
            # Returns (private_key_pem, public_key_pem)
            self._private_key, self.public_key = load_or_generate_keys()
            logger.info(
                f"🔐 Identity: ECDSA keys loaded for {self.agent_id} (fingerprint: {get_public_key_fingerprint(self.public_key)})"
            )
        except Exception as e:
            logger.error(f"❌ Identity: Failed to load/generate ECDSA keys: {e}")
            self._private_key = None
            self.public_key = None

    @property
    def name(self) -> str:
        return "herald.identity"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Cryptographic identity verification and content signing (Steward Protocol or ECDSA)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action to perform: 'assert_identity', 'sign_artifact', 'get_public_key', 'create_signed_record'",
            },
            "content": {
                "type": "string",
                "required": False,
                "description": "Content to sign (required for 'sign_artifact' and 'create_signed_record')",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate identity parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["assert_identity", "sign_artifact", "get_public_key", "create_signed_record"]:
            raise ValueError(
                f"Invalid action: {action}. Must be 'assert_identity', 'sign_artifact', 'get_public_key', or 'create_signed_record'"
            )

        # Validate action-specific parameters
        if action in ["sign_artifact", "create_signed_record"]:
            if "content" not in parameters:
                raise ValueError(f"{action} action requires 'content' parameter")
            if not isinstance(parameters["content"], str):
                raise TypeError("content must be a string")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute identity operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with operation results
        """
        try:
            action = parameters["action"]

            if action == "assert_identity":
                verified = self._assert_identity()

                return ToolResult(
                    success=True,
                    output={
                        "verified": verified,
                        "agent_id": self.agent_id,
                        "method": "native_hmac" if self._use_native else "steward_protocol",
                    },
                    metadata={
                        "action": "assert_identity",
                        "verified": verified,
                    },
                )

            elif action == "sign_artifact":
                content = parameters["content"]
                signature = self._sign_artifact(content)

                if signature:
                    return ToolResult(
                        success=True,
                        output={
                            "content": content,
                            "signature": signature,
                            "method": "native_hmac" if self._use_native else "steward_protocol",
                        },
                        metadata={
                            "action": "sign_artifact",
                            "signature_length": len(signature),
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="Failed to sign content - no signing method available",
                    )

            elif action == "get_public_key":
                public_key = self._get_public_key()

                if public_key:
                    return ToolResult(
                        success=True,
                        output={
                            "public_key": public_key,
                            "agent_id": self.agent_id,
                        },
                        metadata={
                            "action": "get_public_key",
                            "key_length": len(public_key),
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="Public key not available",
                    )

            elif action == "create_signed_record":
                content = parameters["content"]
                record = self._create_signed_record(content)

                if record:
                    return ToolResult(
                        success=True,
                        output=record,
                        metadata={
                            "action": "create_signed_record",
                            "has_public_key": "public_key" in record,
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="Failed to create signed record",
                    )

        except Exception as e:
            error_msg = f"Identity operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"IdentityTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _assert_identity(self) -> bool:
        """
        Internal method: Verify that HERALD has cryptographic credentials available.

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

    def _sign_artifact(self, content: str) -> Optional[str]:
        """
        Internal method: Cryptographically sign a text artifact (tweet, post, etc.).

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

        # Use ECDSA from steward/crypto.py (SECURITY FIX: replaced HMAC)
        if self._use_native and self._private_key and STEWARD_CRYPTO_AVAILABLE:
            try:
                # sign_content returns base64-encoded ECDSA signature
                signature = sign_content(content.strip(), self._private_key)
                logger.info(f"✅ Identity: Content signed with ECDSA ({len(signature)} char signature)")
                return signature
            except Exception as e:
                logger.error(f"❌ Identity: ECDSA signing failed: {e}")
                return None

        # Try Steward Protocol
        if self.client:
            try:
                signature = self.client.sign_artifact(content.strip())
                logger.info(f"✅ Identity: Content signed via Steward ({len(signature)} char signature)")
                return signature
            except Exception as e:
                logger.error(f"❌ Identity: Steward signing failed: {e}")
                return None

        logger.warning("⚠️  Identity: No signing method available")
        return None

    def _get_public_key(self) -> Optional[str]:
        """
        Internal method: Get HERALD's public key for verification.

        The public key is embedded in the identity file and can be used
        to verify any signature created by sign_artifact().

        Returns:
            str: Hex-encoded public key, or None if not available
        """
        if self.public_key:
            return self.public_key

        # Return cached public key if available
        # (set by _ensure_ecdsa_keys during init)

        # Use steward/crypto.py to get the public key
        if not STEWARD_CRYPTO_AVAILABLE:
            logger.warning("⚠️  Identity: steward/crypto.py not available")
            return None

        try:
            _, self.public_key = load_or_generate_keys()
            logger.debug(f"✅ Identity: Public key retrieved ({len(self.public_key)} chars)")
            return self.public_key
        except Exception as e:
            logger.warning(f"⚠️  Identity: Could not retrieve public key: {e}")
            return None

    def _create_signed_record(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Internal method: Create a complete signed record of the content.

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
        signature = self._sign_artifact(content)
        if not signature:
            return None

        record = {
            "content": content,
            "signature": signature,
        }

        public_key = self._get_public_key()
        if public_key:
            record["public_key"] = public_key

        return record


# Export for Herald use
__all__ = ["IdentityTool"]
