"""
Test Execution Mode Enforcement (OPUS-015/020)

Verifies that:
1. MountResult includes execution.mode from manifest
2. Default execution mode is 'thread' when not specified
3. Invalid execution modes fall back to 'thread'
"""

import json
import zipfile
from pathlib import Path

from vibe_core.loaders.container_loader import ContainerMounter, MountResult


def create_test_container(tmp_path: Path, manifest: dict) -> Path:
    """Create a minimal .vibe container for testing."""
    container_path = tmp_path / "test.vibe"

    with zipfile.ZipFile(container_path, "w") as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr("content/plugin_main.py", "# placeholder")

    return container_path


class TestExecutionMode:
    """Tests for execution mode enforcement."""

    def test_mount_returns_mount_result(self, tmp_path):
        """Verify mount() returns MountResult instead of just Path."""
        manifest = {"id": "test_plugin", "type": "plugin"}
        container_path = create_test_container(tmp_path, manifest)

        result = ContainerMounter.mount(container_path)

        assert isinstance(result, MountResult)
        assert isinstance(result.mount_point, Path)
        assert result.mount_point.exists()

    def test_default_execution_mode_is_thread(self, tmp_path):
        """Containers without execution.mode default to 'thread'."""
        manifest = {"id": "no_mode_plugin", "type": "plugin"}
        container_path = create_test_container(tmp_path, manifest)

        result = ContainerMounter.mount(container_path)

        assert result.execution_mode == "thread"

    def test_execution_mode_thread(self, tmp_path):
        """Containers with execution.mode='thread' are correctly detected."""
        manifest = {
            "id": "thread_plugin",
            "type": "plugin",
            "execution": {"mode": "thread"},
        }
        container_path = create_test_container(tmp_path, manifest)

        result = ContainerMounter.mount(container_path)

        assert result.execution_mode == "thread"

    def test_execution_mode_process(self, tmp_path):
        """Containers with execution.mode='process' are correctly detected."""
        manifest = {
            "id": "isolated_plugin",
            "type": "plugin",
            "execution": {"mode": "process"},
        }
        container_path = create_test_container(tmp_path, manifest)

        result = ContainerMounter.mount(container_path)

        assert result.execution_mode == "process"

    def test_invalid_execution_mode_falls_back_to_thread(self, tmp_path):
        """Invalid execution.mode values fall back to 'thread'."""
        manifest = {
            "id": "invalid_mode_plugin",
            "type": "plugin",
            "execution": {"mode": "invalid_value"},
        }
        container_path = create_test_container(tmp_path, manifest)

        result = ContainerMounter.mount(container_path)

        assert result.execution_mode == "thread"

    def test_mount_result_includes_manifest(self, tmp_path):
        """MountResult includes the full manifest dict."""
        manifest = {
            "id": "full_manifest_plugin",
            "type": "plugin",
            "version": "1.0.0",
            "execution": {"mode": "process"},
        }
        container_path = create_test_container(tmp_path, manifest)

        result = ContainerMounter.mount(container_path)

        assert result.manifest["id"] == "full_manifest_plugin"
        assert result.manifest["version"] == "1.0.0"
        assert result.manifest["execution"]["mode"] == "process"


class TestItemMetaExecutionMode:
    """Tests for execution_mode propagation through ItemMeta."""

    def test_item_meta_has_execution_mode_field(self):
        """Verify ItemMeta dataclass has execution_mode field with default."""
        from pathlib import Path

        from vibe_core.loaders.base_loader import ItemMeta

        meta = ItemMeta(
            item_id="test",
            item_type="plugin",
            manifest={},
            manifest_path=Path("/fake"),
            entry_path=None,
            entry_class=None,
        )
        # Should default to "thread"
        assert meta.execution_mode == "thread"

    def test_item_meta_accepts_process_mode(self):
        """Verify ItemMeta can store process execution mode."""
        from pathlib import Path

        from vibe_core.loaders.base_loader import ItemMeta

        meta = ItemMeta(
            item_id="isolated_plugin",
            item_type="plugin",
            manifest={"execution": {"mode": "process"}},
            manifest_path=Path("/fake"),
            entry_path=None,
            entry_class=None,
            execution_mode="process",
        )
        assert meta.execution_mode == "process"
