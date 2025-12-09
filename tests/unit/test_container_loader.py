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
    """Creates a valid .vibe container."""
    container_path = tmp_path / "test_agent.vibe"

    manifest = {"id": "test_agent", "type": "plugin", "execution": {"mode": "thread"}}

    with zipfile.ZipFile(container_path, "w") as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr("content/plugin_main.py", "class TestPlugin: pass")
        z.writestr("tests/test_basic.py", "# test")
        z.writestr("SIGNATURE.sig", "mock_signature")

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
            mount_path = ContainerMounter.mount(sample_vibe_container)

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
