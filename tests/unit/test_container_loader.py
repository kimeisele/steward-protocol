import hashlib
import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.loaders.base_loader import UnifiedLoader
from vibe_core.loaders.container_loader import ContainerMounter


# Mock class for testing UnifiedLoader with containers
class MockPluginLoader(UnifiedLoader):
    item_type = "plugin"
    scan_paths = []
    entry_suffix = "_main.py"


@pytest.fixture
def sample_vibe_container(tmp_path):
    """Creates a valid .vibe container with REAL signature."""
    container_path = tmp_path / "test_agent.vibe"

    manifest = {"id": "test_agent", "type": "plugin", "execution": {"mode": "thread"}}
    manifest_bytes = json.dumps(manifest).encode("utf-8")
    content_bytes = b"class TestPlugin: pass"
    test_bytes = b"# test"

    # Calculate hash same as container_loader: manifest first, then sorted files
    hasher = hashlib.sha256()
    hasher.update(manifest_bytes)
    # Sorted order: content/plugin_main.py, tests/test_basic.py
    hasher.update(content_bytes)
    hasher.update(test_bytes)
    real_signature = hasher.hexdigest()

    with zipfile.ZipFile(container_path, "w") as z:
        z.writestr("manifest.json", manifest_bytes)
        z.writestr("content/plugin_main.py", content_bytes)
        z.writestr("tests/test_basic.py", test_bytes)
        z.writestr("SIGNATURE.sig", real_signature)

    return container_path


class TestContainerMounter:
    def test_gad000_inspect_manifest(self, sample_vibe_container):
        """Test GAD-000 compliant zero-touch manifest reading."""
        # Should read manifest without extracting
        meta = ContainerMounter.inspect(sample_vibe_container)

        assert meta["manifest"]["id"] == "test_agent"
        assert meta["compliance"]["has_tests"] is True
        assert meta["compliance"]["signed"] is True

    def test_lazy_extraction_mount(self, sample_vibe_container):
        """Test lazy extraction creates cache directory."""
        with patch(
            "vibe_core.loaders.container_loader.ContainerMounter.CACHE_DIR", new=sample_vibe_container.parent / "cache"
        ):
            mount_result = ContainerMounter.mount(sample_vibe_container)
            mount_path = mount_result.mount_point

            assert Path(mount_path).exists()
            assert (Path(mount_path) / "manifest.json").exists()
            assert (Path(mount_path) / "content" / "plugin_main.py").exists()

    def test_signature_verification_mock(self, sample_vibe_container):
        """Test that mount trigger signature verification."""
        with patch("vibe_core.loaders.container_loader.ContainerMounter._verify_signature") as mock_verify:
            with patch(
                "vibe_core.loaders.container_loader.ContainerMounter.CACHE_DIR",
                new=sample_vibe_container.parent / "cache_sig",
            ):
                ContainerMounter.mount(sample_vibe_container)
                mock_verify.assert_called_once_with(sample_vibe_container)

    def test_tampered_container_rejected(self, tmp_path):
        """SECURITY: Tampered container MUST be rejected."""
        container_path = tmp_path / "tampered.vibe"

        manifest_bytes = json.dumps({"id": "evil", "type": "plugin"}).encode()
        evil_code = b"import os; os.system('rm -rf /')"  # Malicious payload

        # Create container with WRONG signature (simulating tampering)
        with zipfile.ZipFile(container_path, "w") as z:
            z.writestr("manifest.json", manifest_bytes)
            z.writestr("content/plugin_main.py", evil_code)
            z.writestr("tests/test_basic.py", b"# test")
            # 64 hex chars = valid v1 format but wrong hash → triggers "integrity check failed"
            z.writestr("SIGNATURE.sig", "0" * 64)  # Valid v1 format, wrong hash

        with patch(
            "vibe_core.loaders.container_loader.ContainerMounter.CACHE_DIR",
            new=tmp_path / "cache_tamper",
        ):
            with pytest.raises(ValueError, match="Container integrity check failed"):
                ContainerMounter.mount(container_path)


class TestUnifiedLoaderContainerSupport:
    def test_loader_detects_zip(self, sample_vibe_container, tmp_path):
        """Test that UnifiedLoader finds .vibe file."""
        loader = MockPluginLoader()

        # We want to verify that discover_and_load calls _process_container
        # Since we modified the BASE class, the MockPluginLoader (subclass) inherits the behavior

        with patch.object(MockPluginLoader, "_process_container") as mock_process:
            # Setup mock to return something valid so discovery counts it
            mock_process.return_value.loaded_successfully = True
            mock_process.return_value.entry_class = True  # Just simple generic true
            mock_process.return_value.item_id = "test_agent"

            instances, meta = loader.discover_and_load(scan_paths=[tmp_path])

            mock_process.assert_called_once()
