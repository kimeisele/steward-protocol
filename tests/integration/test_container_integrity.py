"""
OPUS-017: Container Integrity Verification Test

This is THE PROOF that our container security is real, not theater.

Test Strategy:
1. Build a valid container using pack_vibe.py
2. Unzip it, tamper with plugin_main.py (inject 1 byte)
3. Rezip it (keeping the old signature)
4. Try to load it
5. MUST FAIL with SecurityError/ValueError
"""

import json
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts to path for pack_vibe import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from pack_vibe import build_container

from vibe_core.loaders.container_loader import ContainerMounter


class TestContainerIntegrity:
    """SECURITY: End-to-end container tampering detection."""

    @pytest.fixture
    def valid_holon_source(self, tmp_path):
        """Create a valid holon source directory."""
        source = tmp_path / "my_holon"
        source.mkdir()

        # Manifest
        manifest = {
            "id": "test_holon",
            "type": "plugin",
            "version": "1.0.0",
            "execution": {"mode": "thread"},
        }
        (source / "manifest.json").write_text(json.dumps(manifest, indent=2))

        # Plugin code
        (source / "plugin_main.py").write_text(
            '''"""Test plugin."""

class TestHolonPlugin:
    """A legitimate, untampered plugin."""

    def execute(self):
        return "Hello from legitimate holon"
'''
        )

        # Tests (required by pack_vibe)
        tests_dir = source / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_basic.py").write_text("""def test_placeholder(): pass""")

        return source

    def test_valid_container_loads(self, valid_holon_source, tmp_path):
        """Sanity check: Valid container should load without error."""
        # Build container
        container_path = build_container(valid_holon_source)

        # Mount should succeed
        with patch.object(
            ContainerMounter,
            "CACHE_DIR",
            new=tmp_path / "cache_valid",
        ):
            mount_point = ContainerMounter.mount(container_path)
            assert mount_point.exists()
            assert (mount_point / "manifest.json").exists()

    def test_tampered_container_rejected(self, valid_holon_source, tmp_path):
        """
        THE CRITICAL TEST: Tampered container MUST be rejected.

        This test:
        1. Builds a valid .vibe with real signature
        2. Extracts it
        3. Injects 1 byte of malware
        4. Rezips it WITH THE OLD SIGNATURE
        5. Verifies mount() raises ValueError
        """
        # === STEP 1: Build valid container ===
        container_path = build_container(valid_holon_source)
        assert container_path.exists()

        # Read the original signature for later comparison
        with zipfile.ZipFile(container_path, "r") as z:
            original_sig = z.read("SIGNATURE.sig").decode()
            assert len(original_sig) == 64  # SHA256 hex

        # === STEP 2: Extract container ===
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        with zipfile.ZipFile(container_path, "r") as z:
            z.extractall(extract_dir)

        # === STEP 3: TAMPER with plugin_main.py ===
        # Inject fake malware into the code
        plugin_path = extract_dir / "content" / "plugin_main.py"
        original_code = plugin_path.read_text()
        tampered_code = original_code + "\n# INJECTED MALWARE: os.system('rm -rf /')"
        plugin_path.write_text(tampered_code)

        # === STEP 4: Repack with OLD signature (the attack) ===
        tampered_container = tmp_path / "tampered.vibe"
        with zipfile.ZipFile(tampered_container, "w") as z:
            for file_path in extract_dir.rglob("*"):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(extract_dir))
                    z.write(file_path, arcname)

        # === STEP 5: THIS MUST FAIL ===
        with patch.object(
            ContainerMounter,
            "CACHE_DIR",
            new=tmp_path / "cache_tampered",
        ):
            with pytest.raises(ValueError, match="Container integrity check failed"):
                ContainerMounter.mount(tampered_container)

    def test_missing_signature_warns(self, tmp_path):
        """Unsigned container should warn but currently allow (dev mode)."""
        container = tmp_path / "unsigned.vibe"

        with zipfile.ZipFile(container, "w") as z:
            z.writestr("manifest.json", json.dumps({"id": "unsigned", "type": "plugin"}))
            z.writestr("tests/test.py", "# test")
            # No SIGNATURE.sig

        with patch.object(
            ContainerMounter,
            "CACHE_DIR",
            new=tmp_path / "cache_unsigned",
        ):
            # Should log warning but NOT raise (current dev behavior)
            mount_point = ContainerMounter.mount(container)
            assert mount_point.exists()

    def test_hash_determinism(self, valid_holon_source, tmp_path):
        """
        Verify that building the same source twice produces identical signatures.
        This tests the sorted(iterdir()) fix.
        """
        # Build twice
        container1 = tmp_path / "build1.vibe"
        container2 = tmp_path / "build2.vibe"

        build_container(valid_holon_source, container1)
        build_container(valid_holon_source, container2)

        # Extract and compare signatures
        with zipfile.ZipFile(container1, "r") as z1:
            sig1 = z1.read("SIGNATURE.sig").decode()

        with zipfile.ZipFile(container2, "r") as z2:
            sig2 = z2.read("SIGNATURE.sig").decode()

        assert sig1 == sig2, f"Non-deterministic hash! Build 1: {sig1[:16]}... Build 2: {sig2[:16]}..."
