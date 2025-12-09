import json
import shutil

import pytest

from scripts.pack_vibe import build_container
from vibe_core.plugin_loader import PluginLoader


@pytest.fixture
def temp_plugins_dir(tmp_path):
    p = tmp_path / "plugins"
    p.mkdir()
    return p


def test_container_shadows_folder(temp_plugins_dir):
    """
    Verify precedence: Container > Folder (when IDs collide)
    """
    plugin_id = "shadow_target"

    # 1. Create FOLDER plugin
    folder_dir = temp_plugins_dir / "shadow_target"
    folder_dir.mkdir()
    (folder_dir / "manifest.json").write_text(
        json.dumps({"id": plugin_id, "type": "plugin", "description": "I AM THE FOLDER"})
    )
    (folder_dir / "plugin_main.py").write_text(f"""
from vibe_core.plugin_protocol import KernelPlugin
class ShadowPlugin(KernelPlugin):
    @property
    def plugin_id(self): return "{plugin_id}"
    def resolve_origin(self): return "FOLDER"
""")

    # 2. Create CONTAINER plugin (same ID)
    container_src = temp_plugins_dir / "shadow_src"
    container_src.mkdir()
    (container_src / "manifest.json").write_text(
        json.dumps({"id": plugin_id, "type": "plugin", "description": "I AM THE CONTAINER"})
    )
    (container_src / "plugin_main.py").write_text(f"""
from vibe_core.plugin_protocol import KernelPlugin
class ShadowPlugin(KernelPlugin):
    @property
    def plugin_id(self): return "{plugin_id}"
    def resolve_origin(self): return "CONTAINER"
""")
    (container_src / "tests").mkdir()
    (container_src / "tests/test.py").write_text("pass")

    vibe_path = temp_plugins_dir / "shadow_target.vibe"
    build_container(container_src, vibe_path)

    # Clean up src so only vibe and folder remain in plugins dir
    shutil.rmtree(container_src)

    # 3. Load
    registry, meta = PluginLoader.discover_and_load(scan_paths=[temp_plugins_dir])

    # 4. Verify
    assert plugin_id in registry
    plugin = registry[plugin_id]

    # Check origin
    origin = plugin.resolve_origin()
    print(f"\\nResolved Origin: {origin}")

    assert origin == "CONTAINER"
    assert str(meta[plugin_id].manifest_path).endswith(".vibe")
