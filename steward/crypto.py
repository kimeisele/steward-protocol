import os
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

KEY_DIR = Path(".steward/keys")
PRIVATE_KEY_FILE = KEY_DIR / "private.pem"
PUBLIC_KEY_FILE = KEY_DIR / "public.pem"

def ensure_keys_exist():
    """Generates a new ECC keypair if none exists."""
    if PRIVATE_KEY_FILE.exists():
        return False

    KEY_DIR.mkdir(parents=True, exist_ok=True)

    # Generate Private Key (SECP256R1)
    private_key = ec.generate_private_key(ec.SECP256R1())

    # Save Private Key
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save Public Key
    public_key = private_key.public_key()
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Update .gitignore to secure private key
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if ".steward/keys/private.pem" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n# Steward Keys\n.steward/keys/private.pem\n")

    return True

def get_public_key_string():
    """Returns the public key as a clean base64 string for the STEWARD.md."""
    if not PUBLIC_KEY_FILE.exists():
        raise FileNotFoundError("No keys found. Run 'steward keygen' first.")

    with open(PUBLIC_KEY_FILE, "rb") as f:
        pem_data = f.read()
        # Strip PEM headers to keep markdown clean
        lines = pem_data.decode().splitlines()
        return "".join(lines[1:-1])

def sign_content(content: str) -> str:
    """Signs the content string with the private key."""
    if not PRIVATE_KEY_FILE.exists():
        raise FileNotFoundError("No private key found.")

    with open(PRIVATE_KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    signature = private_key.sign(
        content.encode('utf-8'),
        ec.ECDSA(hashes.SHA256())
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(content: str, signature_b64: str, public_key_pem_str: str) -> bool:
    """Verifies a signature against content and a public key."""
    try:
        # Reconstruct PEM format
        pem = f"-----BEGIN PUBLIC KEY-----\n{public_key_pem_str}\n-----END PUBLIC KEY-----"
        public_key = serialization.load_pem_public_key(pem.encode())

        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, content.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, Exception):
        return False
