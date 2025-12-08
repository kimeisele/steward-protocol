"""
STEWARD Protocol Cryptographic Functions
Real ECDSA (Elliptic Curve Digital Signature Algorithm) implementation for identity verification
Using pure Python ECDSA library for maximum compatibility

NOTE: ecdsa imports are LAZY (inside functions) to prevent crashes when lib is missing.
"""

import base64
import hashlib
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger("STEWARD_CRYPTO")

KEY_DIR = Path(".steward/keys")
PRIVATE_KEY_PATH = KEY_DIR / "private.pem"
PUBLIC_KEY_PATH = KEY_DIR / "public.pem"


def ensure_keys_exist():
    """Ensure key directory exists."""
    if not KEY_DIR.exists():
        KEY_DIR.mkdir(parents=True, exist_ok=True)
        # Add .gitignore to keep keys safe
        gitignore = KEY_DIR / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n!.gitignore\n")


def generate_keys() -> Tuple[str, str]:
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


def load_or_generate_keys() -> Tuple[str, str]:
    """
    Load existing keys or generate new ones if missing.
    Returns (private_key_pem, public_key_pem).
    """
    ensure_keys_exist()

    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return PRIVATE_KEY_PATH.read_text(), PUBLIC_KEY_PATH.read_text()

    logger.info("Keys not found. Generating new key pair...")
    priv, pub = generate_keys()

    PRIVATE_KEY_PATH.write_text(priv)
    PUBLIC_KEY_PATH.write_text(pub)

    # Secure private key permissions (read/write for owner only)
    try:
        PRIVATE_KEY_PATH.chmod(0o600)
    except Exception:
        pass

    return priv, pub


def sign_content(content: str, private_key_pem: str) -> str:
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


def verify_signature(content: str, signature_b64: str, public_key_pem: str) -> bool:
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


def get_public_key_fingerprint(public_key_pem: str) -> str:
    """
    Get a short fingerprint (SHA256 hex) of the public key.
    """
    # Normalize by stripping whitespace
    clean_key = public_key_pem.strip().encode()
    return hashlib.sha256(clean_key).hexdigest()[:16]


def get_public_key_string() -> str:
    """
    Get the system's public key as a PEM string.

    Used by verifier_tool.py for signature verification.
    Loads or generates keys if they don't exist.
    """
    _, public_key = load_or_generate_keys()
    return public_key
