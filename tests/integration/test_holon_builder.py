import json
import shutil
import zipfile

import pytest

from scripts.pack_vibe import build_container
from vibe_core.loaders.container_loader import ContainerMounter


@pytest.fixture
def mock_plugin_dir(tmp_path):
    """Creates a valid plugin directory structure."""
    plugin_dir = tmp_path / "my_plugin"
    plugin_dir.mkdir()

    # Manifest
    manifest = {"id": "my_plugin", "type": "plugin", "description": "Test Holon", "execution": {"mode": "thread"}}
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest))

    # Content
    (plugin_dir / "plugin_main.py").write_text("class MyPlugin: pass")
    (plugin_dir / "config.yaml").write_text("enabled: true")

    # Tests (Required!)
    tests_dir = plugin_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_sanity.py").write_text("# Sanity check")

    return plugin_dir


def test_pack_vibe_creates_valid_container(mock_plugin_dir, tmp_path):
    """Test that build_container creates a compliant .vibe file."""
    output_path = tmp_path / "my_plugin.vibe"

    # Run builder
    built_path = build_container(mock_plugin_dir, output_path)

    assert built_path.exists()
    assert zipfile.is_zipfile(built_path)

    with zipfile.ZipFile(built_path, "r") as z:
        namelist = z.namelist()

        # 1. GAD-000: Manifest MUST be first
        assert namelist[0] == "manifest.json", "Manifest must be first file in ZIP"

        # 2. Signature MUST exist
        assert "SIGNATURE.sig" in namelist

        # 3. Validation: Check content
        assert "content/plugin_main.py" in namelist
        assert "tests/test_sanity.py" in namelist


def test_packed_container_loads_with_mounter(mock_plugin_dir, tmp_path):
    """Test that the packed container can be loaded by ContainerMounter."""
    output_path = tmp_path / "my_plugin.vibe"
    build_container(mock_plugin_dir, output_path)

    # Test Inspection
    meta = ContainerMounter.inspect(output_path)
    assert meta["manifest"]["id"] == "my_plugin"
    assert meta["compliance"]["signed"] is True

    # Test Mounting
    mount_result = ContainerMounter.mount(output_path)
    assert mount_result.mount_point.exists()
    assert (mount_result.mount_point / "content/plugin_main.py").exists()


def test_pack_vibe_rejects_missing_tests(mock_plugin_dir):
    """Test that packer rejects plugin without tests."""
    # Remove tests dir
    shutil.rmtree(mock_plugin_dir / "tests")

    with pytest.raises(FileNotFoundError, match="Tests directory missing"):
        build_container(mock_plugin_dir)
