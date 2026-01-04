"""
Crypto Protocols - Signature Verification

GAD-000 v2.0: The 37th Principle requires signature verification.
This protocol enables hot-swap of crypto implementations.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class SignatureVerifierProtocol(Protocol):
    """
    Protocol for ECDSA signature verification.

    Replaces inline import:
        from vibe_core.steward.crypto import verify_signature

    Usage:
        verifier = ServiceRegistry.get(SignatureVerifierProtocol)
        is_valid = verifier.verify(message, signature, public_key)
    """

    def verify(self, message: str, signature: str, public_key: str) -> bool:
        """
        Verify an ECDSA signature.

        Args:
            message: The original message that was signed
            signature: Base64-encoded ECDSA signature
            public_key: Base64-encoded public key

        Returns:
            True if signature is valid, False otherwise
        """
        ...

    def sign(self, message: str, private_key: str) -> str:
        """
        Sign a message with ECDSA.

        Args:
            message: The message to sign
            private_key: Base64-encoded private key

        Returns:
            Base64-encoded signature
        """
        ...


class ECDSAVerifier:
    """
    Default implementation using vibe_core.steward.crypto.

    Registered in ServiceRegistry by steward plugin.
    """

    def verify(self, message: str, signature: str, public_key: str) -> bool:
        from vibe_core.steward.crypto import verify_signature
        return verify_signature(message, signature, public_key)

    def sign(self, message: str, private_key: str) -> str:
        from vibe_core.steward.crypto import sign_content
        return sign_content(message, private_key)
