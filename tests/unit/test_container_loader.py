import hashlib
import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.loaders.base_loader import UnifiedLoader
from vibe_core.loaders.container_loader import ContainerMounter
from vibe_core.plugin_loader import PluginLoader


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

    # Calculate hash same as container_loader: manifest first, then ZIP entry order
    hasher = hashlib.sha256()
    hasher.update(manifest_bytes)
    # ZIP entry order matches write order below: content/plugin_main.py, tests/test_basic.py
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


@pytest.fixture
def cognitive_pack_container(tmp_path):
    """Creates a cognitive_pack .vibe container (data-only, like genesis_knowledge)."""
    container_path = tmp_path / "genesis_knowledge.vibe"

    manifest = {
        "id": "genesis_knowledge",
        "type": "cognitive_pack",
        "version": "1.0.0",
    }
    manifest_bytes = json.dumps(manifest).encode("utf-8")

    # Cognitive packs have circuits/ directory instead of content/
    circuit_bytes = b"# Sample circuit"
    readme_bytes = b"# Genesis Knowledge Pack"

    # Calculate signature: manifest first, then files in ZIP ENTRY ORDER (not sorted!)
    # container_loader._calculate_content_hash uses z.namelist() order
    hasher = hashlib.sha256()
    hasher.update(manifest_bytes)
    # ZIP entry order matches write order below: circuits/sample.md, README.md
    hasher.update(circuit_bytes)
    hasher.update(readme_bytes)
    real_signature = hasher.hexdigest()

    with zipfile.ZipFile(container_path, "w") as z:
        z.writestr("manifest.json", manifest_bytes)
        z.writestr("circuits/sample.md", circuit_bytes)
        z.writestr("README.md", readme_bytes)
        z.writestr("SIGNATURE.sig", real_signature)

    return container_path


class TestCognitivePack:
    """
    Tests for cognitive_pack containers (data-only packs like genesis_knowledge).

    CRITICAL INVARIANT:
        manifest_path.parent MUST equal entry_path

    WHY: The kernel uses manifest_path.parent to derive genesis_path:
        kernel_impl.py:322 → self.genesis_path = genesis_meta.manifest_path.parent

    If manifest_path points to the original .vibe file instead of the mounted
    manifest.json, genesis_path will be wrong and circuits/ won't be found.

    This test was added as a regression test after fixing this bug.

    NOTE: Uses real PluginLoader because it has relaxed type validation that
    allows cognitive_pack type in manifest (unlike base UnifiedLoader).
    """

    def test_cognitive_pack_manifest_path_parent_equals_entry_path(self, cognitive_pack_container, tmp_path):
        """
        REGRESSION TEST: manifest_path.parent must equal entry_path for cognitive packs.

        Before the fix:
            manifest_path = container_path → .parent = wrong directory
        After the fix:
            manifest_path = mount_point/"manifest.json" → .parent = mount_point = entry_path
        """
        with patch(
            "vibe_core.loaders.container_loader.ContainerMounter.CACHE_DIR",
            new=tmp_path / "cache_cognitive",
        ):
            # Use real PluginLoader - it has relaxed validation for cognitive_pack type
            meta = PluginLoader._process_container(cognitive_pack_container, config=None)

            assert meta is not None, "Failed to process cognitive pack container"
            assert meta.loaded_successfully, f"Cognitive pack failed to load: {meta.error}"
            assert meta.item_type == "cognitive_pack", f"Wrong item_type: {meta.item_type}"

            # THE CRITICAL INVARIANT
            # kernel_impl.py uses: genesis_path = manifest_path.parent
            # This MUST equal entry_path (where circuits/ lives)
            assert meta.manifest_path is not None, "manifest_path should not be None"
            assert meta.entry_path is not None, "entry_path should not be None"
            assert meta.manifest_path.parent == meta.entry_path, (
                f"INVARIANT VIOLATION: manifest_path.parent != entry_path\n"
                f"  manifest_path.parent = {meta.manifest_path.parent}\n"
                f"  entry_path = {meta.entry_path}\n"
                f"This would cause kernel.genesis_path to point to the wrong directory!"
            )

    def test_cognitive_pack_circuits_accessible(self, cognitive_pack_container, tmp_path):
        """Verify circuits/ directory is accessible from manifest_path.parent."""
        with patch(
            "vibe_core.loaders.container_loader.ContainerMounter.CACHE_DIR",
            new=tmp_path / "cache_circuits",
        ):
            # Use real PluginLoader
            meta = PluginLoader._process_container(cognitive_pack_container, config=None)

            assert meta is not None and meta.loaded_successfully

            # Simulate what the kernel does
            genesis_path = meta.manifest_path.parent
            circuits_path = genesis_path / "circuits"

            assert circuits_path.exists(), (
                f"circuits/ not found at {circuits_path}\nThis means genesis_path derivation is broken!"
            )


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
