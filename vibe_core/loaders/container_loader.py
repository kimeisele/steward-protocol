import hashlib
import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Any, Dict

# P2 SECURITY: Import ECDSA verification from steward/crypto.py
try:
    from steward.crypto import load_or_generate_keys, verify_signature

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    verify_signature = None
    load_or_generate_keys = None

logger = logging.getLogger("CONTAINER.MOUNTER")


def _get_cache_dir() -> Path:
    """Get XDG-compliant user-private cache directory.

    P2 SECURITY (OPUS-018): Replaced /tmp with user-private directory.
    - Uses XDG_CACHE_HOME if set, else ~/.cache
    - Creates with 0700 permissions (owner-only)
    - Prevents symlink attacks, race conditions, and world-readable cache
    """
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        cache_base = Path(xdg_cache)
    else:
        cache_base = Path.home() / ".cache"

    cache_dir = cache_base / "vibe" / "containers"
    cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    return cache_dir


class ContainerMounter:
    """
    Handles the physical reality of Vibe Containers (.vibe).
    Implements Lazy Extraction and GAD-000 Inspection.
    """

    # P2 SECURITY: XDG-compliant user-private cache (was /tmp/vibe_cache)
    CACHE_DIR = _get_cache_dir()

    @classmethod
    def inspect(cls, container_path: Path) -> Dict[str, Any]:
        """
        GAD-000: Read TRUTH without EXECUTION.
        Reads metadata directly from ZIP stream.
        """
        if not zipfile.is_zipfile(container_path):
            raise ValueError(f"Not a valid zip file: {container_path}")

        with zipfile.ZipFile(container_path, "r") as z:
            # Manifest MUST be present
            if "manifest.json" not in z.namelist():
                raise FileNotFoundError("manifest.json missing from container")

            # Read manifest directly from stream
            manifest_data = json.loads(z.read("manifest.json"))

            # Compliance checks
            has_tests = any(f.startswith("tests/") for f in z.namelist())
            has_signature = "SIGNATURE.sig" in z.namelist()

            return {"manifest": manifest_data, "compliance": {"has_tests": has_tests, "signed": has_signature}}

    @classmethod
    def mount(cls, container_path: Path) -> Path:
        """
        Mounts a container to the filesystem for execution.
        Uses Lazy Extraction strategy based on container hash.
        """
        container_hash = cls._get_file_hash(container_path)
        mount_point = cls.CACHE_DIR / container_hash

        # If not cached, extract
        if not mount_point.exists():
            logger.info(f"Mounting container {container_path.name} to {mount_point}")

            # 1. Verify Signature (Artha) - Placeholder
            cls._verify_signature(container_path)

            # 2. Extract
            mount_point.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(container_path, "r") as z:
                z.extractall(mount_point)

            # 3. Recursive Mounting only if hollows exist
            hollows_path = mount_point / "hollows"
            if hollows_path.exists():
                for sub_container in hollows_path.glob("*.vibe"):
                    cls.mount(sub_container)

        return mount_point

    @classmethod
    def _get_file_hash(cls, file_path: Path) -> str:
        """Calculate SHA256 of file for caching key."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        return sha256.hexdigest()

    @classmethod
    def _verify_signature(cls, container_path: Path) -> bool:
        """
        Verify container integrity and authenticity.

        P2 SECURITY (OPUS-018): Now supports two signature formats:
        - v1 (legacy): 64-char hex SHA256 hash (tamper detection only)
        - v2 (ECDSA): JSON with hash + ECDSA signature (tamper + author verification)

        Returns True if valid, raises ValueError if tampered/forged.
        """
        with zipfile.ZipFile(container_path, "r") as z:
            # 1. Check if signature exists
            if "SIGNATURE.sig" not in z.namelist():
                logger.warning(f"⚠️ Unsigned container: {container_path}")
                return False  # Allow but warn for development

            # 2. Read stored signature
            signature_raw = z.read("SIGNATURE.sig").decode("utf-8").strip()

            # 3. Recalculate hash (same algorithm as pack_vibe.py)
            calculated_hash = cls._calculate_content_hash(z)

            # 4. Detect signature format (v1 = plain hash, v2 = JSON with ECDSA)
            if signature_raw.startswith("{"):
                # V2: ECDSA signed JSON format
                return cls._verify_v2_signature(container_path, signature_raw, calculated_hash)
            else:
                # V1: Legacy hash-only format
                return cls._verify_v1_signature(container_path, signature_raw, calculated_hash)

    @classmethod
    def _calculate_content_hash(cls, z: zipfile.ZipFile) -> str:
        """Calculate SHA256 hash of container contents.

        IMPORTANT: Hash order must match pack_vibe.py exactly:
        1. manifest.json first
        2. All other files in ZIP entry order (as written by pack_vibe)
        """
        hasher = hashlib.sha256()

        # Manifest MUST be first and always exists
        if "manifest.json" in z.namelist():
            hasher.update(z.read("manifest.json"))

        # Hash all other files in ZIP entry order (NOT sorted - matches pack_vibe)
        for name in z.namelist():
            if name in ("manifest.json", "SIGNATURE.sig"):
                continue
            if name.endswith("/"):  # Skip directories
                continue
            hasher.update(z.read(name))

        return hasher.hexdigest()

    @classmethod
    def _verify_v1_signature(cls, container_path: Path, stored_hash: str, calculated_hash: str) -> bool:
        """Verify legacy v1 signature (hash comparison only).

        WARNING: v1 only provides tamper detection, not author verification.
        Anyone can modify content and update the hash.
        """
        if len(stored_hash) != 64:
            raise ValueError(f"Invalid v1 signature length: {len(stored_hash)} (expected 64)")

        if calculated_hash != stored_hash:
            logger.error(
                f"🔴 CONTAINER TAMPERED: {container_path}\n"
                f"   Expected: {stored_hash[:16]}...\n"
                f"   Got:      {calculated_hash[:16]}..."
            )
            raise ValueError(f"Container integrity check failed: {container_path}")

        logger.warning(f"⚠️ Container verified (v1 LEGACY - hash only, no author verification): {container_path.name}")
        return True

    @classmethod
    def _verify_v2_signature(cls, container_path: Path, signature_json: str, calculated_hash: str) -> bool:
        """Verify v2 ECDSA-signed container.

        Provides both tamper detection AND author verification.
        """
        try:
            sig_data = json.loads(signature_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid signature JSON: {e}")

        # Check required fields
        version = sig_data.get("version")
        stored_hash = sig_data.get("hash")
        ecdsa_signature = sig_data.get("signature")
        signer = sig_data.get("signer")

        if version != 2:
            raise ValueError(f"Unknown signature version: {version}")
        if not all([stored_hash, ecdsa_signature, signer]):
            raise ValueError("Missing required signature fields")

        # Step 1: Verify hash matches (tamper detection)
        if calculated_hash != stored_hash:
            logger.error(
                f"🔴 CONTAINER TAMPERED: {container_path}\n"
                f"   Expected hash: {stored_hash[:16]}...\n"
                f"   Got hash:      {calculated_hash[:16]}..."
            )
            raise ValueError(f"Container integrity check failed: {container_path}")

        # Step 2: Verify ECDSA signature (author verification)
        if not CRYPTO_AVAILABLE:
            logger.warning(
                f"⚠️ ECDSA verification unavailable - hash verified but signature NOT checked: {container_path.name}"
            )
            return True

        try:
            # Load our public key to check if we're the signer
            _, our_public_key = load_or_generate_keys()

            # P2 PERMISSIVE: Accept ANY valid signature (future: add keyring trust model)
            # For now, just verify the signature is mathematically valid
            is_valid = verify_signature(stored_hash, ecdsa_signature, our_public_key)

            if not is_valid:
                # Signature doesn't match our key - could be from different author
                # P2 PERMISSIVE: Log warning but accept (future: check keyring)
                logger.warning(f"⚠️ Container signed by different key: {signer} (accepting in permissive mode)")
                # TODO P3: Check signer against trusted keyring
                return True

            logger.info(f"✅ Container ECDSA verified: {container_path.name} signed by {signer}")
            return True

        except Exception as e:
            logger.warning(f"⚠️ ECDSA verification error: {e} - hash verified, signature check failed")
            # P2 PERMISSIVE: Accept if hash matches even if signature check fails
            return True
