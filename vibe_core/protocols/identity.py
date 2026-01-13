# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xe76754c5"  # GenesisByte: parampara % 37 == 0

from typing import Optional, Protocol, Tuple, runtime_checkable


@runtime_checkable
class IdentityProtocol(Protocol):
    """
    Protocol defining a cryptographic identity.
    Decoupled from specific implementations (e.g. ECDSA, Ed25519).
    """

    @property
    def fingerprint(self) -> str:
        """The unique identifier of the identity."""
        ...

    @property
    def public_key_pem(self) -> str:
        """The public key in PEM format."""
        ...

    def sign(self, data: bytes) -> bytes:
        """Sign data with the private key."""
        ...

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify the signature of data using the public key."""
        ...


@runtime_checkable
class KeyStoreProtocol(Protocol):
    """
    Protocol for secure key storage.
    Decoupled from specific storage (e.g. File, Vault, HSM).
    """

    def load(self, identity_id: str) -> Optional[Tuple[bytes, bytes]]:
        """
        Load keys for an identity.

        Args:
            identity_id: The ID of the identity to load.

        Returns:
            Tuple[private_key, public_key] (bytes) or None if not found.
        """
        ...

    def save(self, identity_id: str, private_key: bytes, public_key: bytes) -> None:
        """
        Save keys for an identity.

        Args:
            identity_id: The ID of the identity.
            private_key: Private key bytes.
            public_key: Public key bytes.
        """
        ...
