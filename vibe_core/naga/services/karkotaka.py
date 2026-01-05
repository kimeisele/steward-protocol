"""
KARKOTAKA SERVICE - Der Zauberer.

Karkotaka - The Naga who gave Nala a magical cloak of transformation.

From mythology: When King Nala was cursed and disfigured, Karkotaka
bit him and gave him a magical cloak that made him unrecognizable
but also protected him. This is the power of transformation/obfuscation.

PROMPT.md: "37th Principle - Sign everything."

Responsibilities:
- Centralized signing/verification API
- Encryption/decryption for secrets (AES-256-GCM)
- Secrets vault (encrypted storage)
- Key management (trust, revoke)
- Obfuscation (reversible transformation)

Integration:
- Vasuki uses Karkotaka for signing outbound
- Takshaka uses Karkotaka for verification
- All NAGAs can use for sensitive data
"""

import base64
import hashlib
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import (
    EncryptedPayload,
    KarkotakaProtocol,
    NagaStatus,
    NagaType,
    SignedContent,
)

logger = logging.getLogger("KARKOTAKA")

# Vault location
VAULT_DIR = Path(".steward/vault")
SECRETS_FILE = VAULT_DIR / "secrets.enc"
REVOKED_KEYS_FILE = VAULT_DIR / "revoked_keys.json"


@naga_service(
    name="Karkotaka",
    lord=NagaLord.KARKOTAKA,
    drift_source=None,  # Pure crypto, no drift handling
    priority=95,  # High priority - needed by other NAGAs
    capabilities=[NagaCapability.CRYPTO],
    protocol_class="vibe_core.protocols.naga.KarkotakaProtocol",
)
class KarkotakaService(NagaBaseService, KarkotakaProtocol):
    """
    Karkotaka - The Magic Cloak.

    Centralizes all cryptographic operations for the NAGA infrastructure.
    Wraps the existing steward.crypto module and adds encryption capabilities.


    OUROBOROS: Inherits NagaBaseService for self-monitoring."""

    def __init__(self, vault_dir: Optional[Path] = None) -> None:
        """
        Initialize Karkotaka.

        Args:
            vault_dir: Optional custom vault directory. Uses default if None.
        """
        self._vault_dir = vault_dir or VAULT_DIR
        self._secrets_file = self._vault_dir / "secrets.enc"
        self._revoked_file = self._vault_dir / "revoked_keys.json"

        self._private_key: Optional[str] = None
        self._public_key: Optional[str] = None
        self._fingerprint: str = ""
        self._encryption_key: Optional[bytes] = None

        self._operations_count = 0
        self._errors = 0
        self._last_heartbeat = datetime.now()

        self._ensure_vault()
        self._load_keys()
        self._load_encryption_key()

        logger.info("KARKOTAKA initialized - The Magic protects")

    def _ensure_vault(self) -> None:
        """Ensure vault directory exists."""
        if not self._vault_dir.exists():
            self._vault_dir.mkdir(parents=True, exist_ok=True)
            gitignore = self._vault_dir / ".gitignore"
            if not gitignore.exists():
                gitignore.write_text("*\n!.gitignore\n")

    def _load_keys(self) -> None:
        """Load signing keys from steward.crypto."""
        try:
            from vibe_core.steward.crypto import (
                get_public_key_fingerprint,
                load_or_generate_keys,
            )

            self._private_key, self._public_key = load_or_generate_keys()
            self._fingerprint = get_public_key_fingerprint(self._public_key)
            logger.debug(f"KARKOTAKA: Keys loaded (fingerprint: {self._fingerprint})")
        except Exception as e:
            logger.warning(f"KARKOTAKA: Failed to load signing keys: {e}")
            self._errors += 1

    def _load_encryption_key(self) -> None:
        """Load or generate encryption key for vault."""
        key_file = self._vault_dir / "vault.key"
        try:
            if key_file.exists():
                self._encryption_key = base64.b64decode(key_file.read_text())
            else:
                self._encryption_key = os.urandom(32)  # 256-bit key
                key_file.write_text(base64.b64encode(self._encryption_key).decode())
                key_file.chmod(0o600)
                logger.debug("KARKOTAKA: Generated new vault encryption key")
        except Exception as e:
            logger.warning(f"KARKOTAKA: Failed to load encryption key: {e}")
            self._errors += 1

    # =========================================================================
    # Signing (37th Principle)
    # =========================================================================

    def sign(self, content: str) -> SignedContent:
        """Sign content with the node's private key."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        if not self._private_key:
            logger.warning("KARKOTAKA: No private key available for signing")
            return SignedContent(
                content=content,
                signature="",
                signer_fingerprint="",
                timestamp=time.time(),
            )

        try:
            from vibe_core.steward.crypto import sign_content

            signature = sign_content(content, self._private_key)
            return SignedContent(
                content=content,
                signature=signature,
                signer_fingerprint=self._fingerprint,
                timestamp=time.time(),
            )
        except Exception as e:
            logger.error(f"KARKOTAKA: Signing failed: {e}")
            self._errors += 1
            return SignedContent(
                content=content,
                signature="",
                signer_fingerprint="",
                timestamp=time.time(),
            )

    def verify(self, signed: SignedContent) -> bool:
        """Verify a signed content - checks signature AND trust."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        if not signed.signature:
            return False

        # Check if signer is trusted
        if not self.is_key_trusted(signed.signer_fingerprint):
            logger.warning(f"KARKOTAKA: Signer {signed.signer_fingerprint} not trusted")
            return False

        # Get the public key for this fingerprint
        try:
            from vibe_core.steward.crypto import load_trusted_keys

            trusted = load_trusted_keys()
            public_key = trusted.get(signed.signer_fingerprint)
            if not public_key:
                return False

            return self.verify_with_key(signed, public_key)
        except Exception as e:
            logger.error(f"KARKOTAKA: Verification failed: {e}")
            self._errors += 1
            return False

    def verify_with_key(self, signed: SignedContent, public_key: str) -> bool:
        """Verify signature against a specific public key."""
        self._last_heartbeat = datetime.now()

        try:
            from vibe_core.steward.crypto import verify_signature

            return verify_signature(signed.content, signed.signature, public_key)
        except Exception as e:
            logger.error(f"KARKOTAKA: Verification with key failed: {e}")
            self._errors += 1
            return False

    # =========================================================================
    # Encryption (Secrets Protection)
    # =========================================================================

    def encrypt(self, plaintext: bytes, key_id: Optional[str] = None) -> EncryptedPayload:
        """Encrypt data using AES-256-GCM."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        if not self._encryption_key:
            raise ValueError("No encryption key available")

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            nonce = os.urandom(12)  # 96-bit nonce for GCM
            aesgcm = AESGCM(self._encryption_key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)

            return EncryptedPayload(
                ciphertext=ciphertext,
                nonce=nonce,
                key_id=key_id or self._fingerprint,
                algorithm="AES-256-GCM",
            )
        except ImportError:
            # Fallback: simple XOR obfuscation (NOT secure, just for testing)
            logger.warning("KARKOTAKA: cryptography not installed, using fallback")
            xored = bytes(b ^ self._encryption_key[i % 32] for i, b in enumerate(plaintext))
            return EncryptedPayload(
                ciphertext=xored,
                nonce=b"",
                key_id=key_id or self._fingerprint,
                algorithm="XOR-FALLBACK",
            )

    def decrypt(self, payload: EncryptedPayload) -> bytes:
        """Decrypt an encrypted payload."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        if not self._encryption_key:
            raise ValueError("No encryption key available")

        try:
            if payload.algorithm == "XOR-FALLBACK":
                return bytes(b ^ self._encryption_key[i % 32] for i, b in enumerate(payload.ciphertext))

            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            aesgcm = AESGCM(self._encryption_key)
            return aesgcm.decrypt(payload.nonce, payload.ciphertext, None)
        except Exception as e:
            logger.error(f"KARKOTAKA: Decryption failed: {e}")
            self._errors += 1
            raise ValueError(f"Decryption failed: {e}")

    # =========================================================================
    # Secrets Vault
    # =========================================================================

    def _load_vault(self) -> Dict[str, str]:
        """Load secrets from encrypted vault."""
        if not self._secrets_file.exists():
            return {}

        try:
            encrypted = self._secrets_file.read_bytes()
            if not encrypted:
                return {}

            payload = EncryptedPayload(
                ciphertext=encrypted[12:],
                nonce=encrypted[:12],
                key_id=self._fingerprint,
                algorithm="AES-256-GCM",
            )
            decrypted = self.decrypt(payload)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"KARKOTAKA: Failed to load vault: {e}")
            return {}

    def _save_vault(self, secrets: Dict[str, str]) -> bool:
        """Save secrets to encrypted vault."""
        try:
            plaintext = json.dumps(secrets).encode()
            payload = self.encrypt(plaintext)
            self._secrets_file.write_bytes(payload.nonce + payload.ciphertext)
            return True
        except Exception as e:
            logger.error(f"KARKOTAKA: Failed to save vault: {e}")
            self._errors += 1
            return False

    def store_secret(self, name: str, value: str) -> bool:
        """Store a secret in the encrypted vault."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        secrets = self._load_vault()
        secrets[name] = value
        return self._save_vault(secrets)

    def get_secret(self, name: str) -> Optional[str]:
        """Retrieve a secret from the vault."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        secrets = self._load_vault()
        return secrets.get(name)

    def delete_secret(self, name: str) -> bool:
        """Delete a secret from the vault."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        secrets = self._load_vault()
        if name not in secrets:
            return False

        del secrets[name]
        return self._save_vault(secrets)

    def list_secrets(self) -> List[str]:
        """List all secret names (not values)."""
        self._last_heartbeat = datetime.now()
        return list(self._load_vault().keys())

    # =========================================================================
    # Key Management
    # =========================================================================

    def get_public_key(self) -> str:
        """Get this node's public key (PEM format)."""
        return self._public_key or ""

    def get_fingerprint(self) -> str:
        """Get this node's key fingerprint."""
        return self._fingerprint

    def is_key_trusted(self, fingerprint: str) -> bool:
        """Check if a key fingerprint is in the trusted keyring."""
        # Check if revoked first
        if self._is_key_revoked(fingerprint):
            return False

        try:
            from vibe_core.steward.crypto import is_fingerprint_trusted

            return is_fingerprint_trusted(fingerprint)
        except Exception:
            return fingerprint == self._fingerprint  # Trust self

    def _is_key_revoked(self, fingerprint: str) -> bool:
        """Check if a key has been revoked."""
        if not self._revoked_file.exists():
            return False
        try:
            revoked = json.loads(self._revoked_file.read_text())
            return fingerprint in revoked
        except Exception:
            return False

    def trust_key(self, public_key: str, label: str) -> str:
        """Add a public key to the trusted keyring."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        try:
            from vibe_core.steward.crypto import (
                TRUSTED_KEYS_DIR,
                ensure_trusted_keys_dir,
                get_public_key_fingerprint,
            )

            ensure_trusted_keys_dir()
            fingerprint = get_public_key_fingerprint(public_key)

            # Save the key
            safe_label = "".join(c for c in label if c.isalnum() or c in "-_")
            key_path = TRUSTED_KEYS_DIR / f"{safe_label}_{fingerprint[:8]}.pem"
            key_path.write_text(public_key)

            logger.info(f"KARKOTAKA: Trusted key {label} ({fingerprint})")
            return fingerprint
        except Exception as e:
            logger.error(f"KARKOTAKA: Failed to trust key: {e}")
            self._errors += 1
            return ""

    def revoke_key(self, fingerprint: str) -> bool:
        """Revoke a key (remove from trusted, add to blacklist)."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        try:
            # Add to revoked list
            revoked: List[str] = []
            if self._revoked_file.exists():
                revoked = json.loads(self._revoked_file.read_text())

            if fingerprint not in revoked:
                revoked.append(fingerprint)
                self._revoked_file.write_text(json.dumps(revoked))

            # Remove from trusted keys if present
            try:
                from vibe_core.steward.crypto import TRUSTED_KEYS_DIR

                for pem_file in TRUSTED_KEYS_DIR.glob("*.pem"):
                    if fingerprint in pem_file.stem:
                        pem_file.unlink()
                        logger.info(f"KARKOTAKA: Removed trusted key {pem_file.name}")
            except Exception:
                pass

            logger.info(f"KARKOTAKA: Revoked key {fingerprint}")
            return True
        except Exception as e:
            logger.error(f"KARKOTAKA: Failed to revoke key: {e}")
            self._errors += 1
            return False

    # =========================================================================
    # Obfuscation (The Magic Cloak)
    # =========================================================================

    def obfuscate(self, data: str) -> str:
        """
        Obfuscate data to hide patterns.

        Uses simple reversible transformation - NOT encryption.
        """
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        # Simple obfuscation: base64 + byte reversal + base64
        encoded = base64.b64encode(data.encode()).decode()
        reversed_bytes = encoded[::-1]
        return base64.b64encode(reversed_bytes.encode()).decode()

    def deobfuscate(self, data: str) -> str:
        """Reverse obfuscation."""
        self._last_heartbeat = datetime.now()
        self._operations_count += 1

        try:
            decoded = base64.b64decode(data).decode()
            reversed_back = decoded[::-1]
            return base64.b64decode(reversed_back).decode()
        except Exception as e:
            logger.error(f"KARKOTAKA: Deobfuscation failed: {e}")
            return data  # Return as-is on failure

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        has_keys = bool(self._private_key and self._public_key)
        has_encryption = bool(self._encryption_key)
        secrets_count = len(self.list_secrets())

        return NagaStatus(
            naga_type=NagaType.SESHA,  # No KARKOTAKA in NagaType
            healthy=has_keys and has_encryption and self._errors < 10,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._operations_count,
            errors=self._errors,
            message=f"keys={'ok' if has_keys else 'missing'}, enc={'ok' if has_encryption else 'missing'}, secrets={secrets_count}",
        )
