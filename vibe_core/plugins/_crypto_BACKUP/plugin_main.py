"""
Crypto Plugin - Core Cryptographic Functions.

This plugin provides ECDSA signing and verification services to the kernel.
It encapsulates the 'ecdsa' library dependency, preventing system-wide crashes
if the library is missing (until crypto functions are actually called).
"""

import base64
import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("CRYPTO_PLUGIN")


class CryptoPlugin(KernelPlugin):
    """
    Crypto Plugin - Provides ECDSA signing and verification.

    Priority: 1 (Critical infrastructure)
    """

    @property
    def plugin_id(self) -> str:
        return "crypto"

    @property
    def priority(self) -> int:
        return 1

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None
        self._key_dir: Path = Path(".steward/keys")
        self._private_key_path: Path = self._key_dir / "private.pem"
        self._public_key_path: Path = self._key_dir / "public.pem"

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Register crypto services on kernel."""
        self._kernel = kernel

        # Register as kernel.crypto
        kernel.crypto = self

        # Load config
        if hasattr(self, "config") and self.config:
            key_dir_str = self.config.get("key_dir", ".steward/keys")
            self._key_dir = Path(key_dir_str)
            self._private_key_path = self._key_dir / "private.pem"
            self._public_key_path = self._key_dir / "public.pem"

        logger.info("🔐 Crypto Plugin booted (ECDSA provider ready)")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Cleanup."""
        logger.info("🔐 Crypto Plugin shutting down")

    # =========================================================================
    # PUBLIC API (kernel.crypto.*)
    # =========================================================================

    def ensure_keys_exist(self) -> None:
        """Ensure key directory exists."""
        if not self._key_dir.exists():
            self._key_dir.mkdir(parents=True, exist_ok=True)
            # Add .gitignore to keep keys safe
            gitignore = self._key_dir / ".gitignore"
            if not gitignore.exists():
                gitignore.write_text("*\n!.gitignore\n")

    def generate_keys(self) -> Tuple[str, str]:
        """
        Generate a new ECC key pair (NIST256p).
        Returns (private_key_pem, public_key_pem).
        """
        try:
            from ecdsa import NIST256p, SigningKey
        except ImportError:
            logger.error("ecdsa library not installed. Cannot generate keys.")
            raise ImportError("ecdsa library not installed. Please run 'pip install ecdsa'")

        sk = SigningKey.generate(curve=NIST256p)
        vk = sk.verifying_key

        return sk.to_pem().decode(), vk.to_pem().decode()

    def load_or_generate_keys(self) -> Tuple[str, str]:
        """
        Load existing keys or generate new ones if missing.
        Returns (private_key_pem, public_key_pem).
        """
        self.ensure_keys_exist()

        if self._private_key_path.exists() and self._public_key_path.exists():
            return self._private_key_path.read_text(), self._public_key_path.read_text()

        logger.info("Keys not found. Generating new key pair...")
        priv, pub = self.generate_keys()

        self._private_key_path.write_text(priv)
        self._public_key_path.write_text(pub)

        # Secure private key permissions (read/write for owner only)
        try:
            self._private_key_path.chmod(0o600)
        except Exception:
            pass

        return priv, pub

    def sign_content(self, content: str, private_key_pem: str) -> str:
        """
        Sign a string content using the private key.
        Returns base64 encoded signature.
        """
        try:
            from ecdsa import SigningKey
            from ecdsa.util import sigencode_string
        except ImportError:
            logger.error("ecdsa library not installed. Cannot sign content.")
            raise ImportError("ecdsa library not installed. Please run 'pip install ecdsa'")

        sk = SigningKey.from_pem(private_key_pem)
        signature = sk.sign_deterministic(content.encode(), hashfunc=hashlib.sha256, sigencode=sigencode_string)
        return base64.b64encode(signature).decode()

    def verify_signature(self, content: str, signature_b64: str, public_key_pem: str) -> bool:
        """
        Verify a signature against content using the public key.
        """
        try:
            from ecdsa import VerifyingKey
            from ecdsa.util import sigdecode_string
        except ImportError:
            logger.error("ecdsa library not installed. Cannot verify signature.")
            raise ImportError("ecdsa library not installed. Please run 'pip install ecdsa'")

        try:
            vk = VerifyingKey.from_pem(public_key_pem)
            signature = base64.b64decode(signature_b64)
            return vk.verify(signature, content.encode(), hashfunc=hashlib.sha256, sigdecode=sigdecode_string)
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False

    def get_public_key_fingerprint(self, public_key_pem: str) -> str:
        """
        Get a short fingerprint (SHA256 hex) of the public key.
        """
        # Normalize by stripping whitespace
        clean_key = public_key_pem.strip().encode()
        return hashlib.sha256(clean_key).hexdigest()[:16]
