# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x276e6908"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Optional, Tuple

from vibe_core.protocols.identity import KeyStoreProtocol

logger = logging.getLogger("STEWARD.KEYSTORE")


class FileKeyStore(KeyStoreProtocol):
    """
    File-based implementation of KeyStoreProtocol.
    Manages PEM files in a directory.
    """

    def __init__(self, key_dir: str = ".steward/keys"):
        self.key_dir = Path(key_dir)
        if not self.key_dir.exists():
            self.key_dir.mkdir(parents=True, exist_ok=True)

    def load(self, identity_id: str) -> Optional[Tuple[bytes, bytes]]:
        """
        Load keys for identity.
        Returns (private_bytes, public_bytes).
        """
        priv_path = self.key_dir / f"{identity_id}.private.pem"
        pub_path = self.key_dir / f"{identity_id}.public.pem"

        # Legacy mapping for naga_federation
        if identity_id == "naga_federation" and not priv_path.exists():
            priv_path = self.key_dir / "private.pem"
            pub_path = self.key_dir / "public.pem"

        if priv_path.exists() and pub_path.exists():
            return priv_path.read_bytes(), pub_path.read_bytes()
        return None

    def save(self, identity_id: str, private: bytes, public: bytes) -> None:
        """
        Save keys for identity.
        """
        priv_path = self.key_dir / f"{identity_id}.private.pem"
        pub_path = self.key_dir / f"{identity_id}.public.pem"

        # Legacy mapping
        if identity_id == "naga_federation":
            priv_path = self.key_dir / "private.pem"
            pub_path = self.key_dir / "public.pem"

        priv_path.write_bytes(private)
        pub_path.write_bytes(public)

        try:
            priv_path.chmod(0o600)
        except Exception as e:
            logger.warning(f"Failed to chmod private key: {e}")
