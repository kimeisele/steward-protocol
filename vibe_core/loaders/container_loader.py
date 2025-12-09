import hashlib
import json
import logging
import zipfile
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("CONTAINER.MOUNTER")


class ContainerMounter:
    """
    Handles the physical reality of Vibe Containers (.vibe).
    Implements Lazy Extraction and GAD-000 Inspection.
    """

    # Default cache location - should be configured in Phoenix
    CACHE_DIR = Path("/tmp/vibe_cache/containers")

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
    def _verify_signature(cls, container_path: Path) -> None:
        """
        Verify container integrity.
        Currently a strict check for development: warns if missing.
        """
        # TODO: Implement real crypto verification
        # For now, just check file existence as per TDD test
        with zipfile.ZipFile(container_path, "r") as z:
            if "SIGNATURE.sig" not in z.namelist():
                logger.warning(f"Unsigned container: {container_path}")
