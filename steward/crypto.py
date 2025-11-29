"""
STEWARD Protocol Cryptographic Functions
Real ECDSA (Elliptic Curve Digital Signature Algorithm) implementation for identity verification
Using pure Python ECDSA library for maximum compatibility
"""

import base64
import hashlib
import os
from pathlib import Path

from ecdsa import NIST256p, SigningKey, VerifyingKey
from ecdsa.util import sigdecode_string, sigencode_string

# Key storage location
KEYS_DIR = Path(".steward/keys")
PRIVATE_KEY_PATH = KEYS_DIR / "private.pem"
PUBLIC_KEY_PATH = KEYS_DIR / "public.pem"


def ensure_keys_exist():
    """
    Ensures that key pair exists. Creates one if it doesn't.

    Returns:
        bool: True if new keys were created, False if they already existed
    """
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return False

    # Create directory
    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate new keypair using NIST P-256 curve
    private_key = SigningKey.generate(curve=NIST256p, hashfunc=hashlib.sha256)
    public_key = private_key.get_verifying_key()

    # Save private key (PEM format)
    private_pem = private_key.to_pem().decode("utf-8")
    PRIVATE_KEY_PATH.write_text(private_pem)
    PRIVATE_KEY_PATH.chmod(0o600)  # Restrict to owner only

    # Save public key (PEM format)
    public_pem = public_key.to_pem().decode("utf-8")
    PUBLIC_KEY_PATH.write_text(public_pem)

    # Add private.pem to .gitignore
    gitignore_path = Path(".gitignore")
    gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""
    if ".steward/keys/private.pem" not in gitignore_content:
        with open(gitignore_path, "a") as f:
            if gitignore_content and not gitignore_content.endswith("\n"):
                f.write("\n")
            f.write(".steward/keys/private.pem\n")

    return True


def get_public_key_string():
    """
    Returns the public key as a base64 string (without PEM markers).
    Suitable for embedding in STEWARD.md files.

    Returns:
        str: Public key in base64 format (without BEGIN/END markers)
    """
    ensure_keys_exist()
    public_pem = PUBLIC_KEY_PATH.read_text()
    # Extract just the base64 content (without BEGIN/END lines)
    lines = public_pem.split("\n")
    content = "".join([line for line in lines if line and not line.startswith("-----")])
    return content


def _load_private_key():
    """Load private key from file."""
    if not PRIVATE_KEY_PATH.exists():
        raise FileNotFoundError(f"Private key not found at {PRIVATE_KEY_PATH}")

    private_pem = PRIVATE_KEY_PATH.read_text()
    private_key = SigningKey.from_pem(private_pem)
    return private_key


def _load_public_key(public_key_b64_str):
    """Load public key from base64 string (without PEM markers)."""
    # Reconstruct PEM format with BEGIN/END markers
    pem_str = f"""-----BEGIN PUBLIC KEY-----
{public_key_b64_str}
-----END PUBLIC KEY-----"""

    public_key = VerifyingKey.from_pem(pem_str)
    return public_key


def sign_content(content: str) -> str:
    """
    Sign the given content with the private key.

    Args:
        content (str): The content to sign

    Returns:
        str: The signature in base64 format
    """
    private_key = _load_private_key()

    # Sign the content using SHA256 hash
    content_bytes = content.encode("utf-8")
    signature_bytes = private_key.sign(content_bytes, hashfunc=hashlib.sha256, sigencode=sigencode_string)

    # Encode as base64
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")
    return signature_b64


def verify_signature(content: str, signature_b64: str, public_key_b64: str) -> bool:
    """
    Verify a signature against content using the public key.

    Args:
        content (str): The original content that was signed
        signature_b64 (str): The signature in base64 format
        public_key_b64 (str): The public key (base64 content without BEGIN/END markers)

    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        public_key = _load_public_key(public_key_b64)

        # Decode signature from base64
        signature_bytes = base64.b64decode(signature_b64)

        # Verify the signature
        content_bytes = content.encode("utf-8")
        public_key.verify(
            signature_bytes,
            content_bytes,
            hashfunc=hashlib.sha256,
            sigdecode=sigdecode_string,
        )
        return True
    except Exception:
        # Any exception means verification failed
        return False
