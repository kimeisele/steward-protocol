from pathlib import Path

import pytest

from scripts.pack_vibe import build_container
from vibe_core.loaders.circuit_loader import CircuitLoader
from vibe_core.plugin_loader import PluginLoader


def test_golden_holon_fractal_integrity(tmp_path):
    """
    Verify the Golden Holon (Nexus Holon):
    1. Packs Code (Plugin) AND Thoughts (Circuit).
    2. Loads Plugin successfully (Process Execution -> Thread for now).
    3. Loads Circuit successfully (Cognitive Mobility).
    """
    # 1. Setup Source (Nexus Holon)
    real_nexus_path = Path("vibe_core/plugins/nexus_holon")
    if not real_nexus_path.exists():
        pytest.skip("Nexus Holon source not found")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    # We build INTO plugins_dir
    vibe_path = plugins_dir / "nexus_holon.vibe"
    build_container(real_nexus_path, vibe_path)

    assert vibe_path.exists()
    assert vibe_path.stat().st_size > 0

    # 2. Load Plugin (Code)
    registry, meta = PluginLoader.discover_and_load(scan_paths=[plugins_dir])

    assert "nexus_holon" in registry
    plugin = registry["nexus_holon"]
    assert plugin.plugin_id == "nexus_holon"
    assert plugin.on_load() is True  # Prove code execution

    # 3. Load Circuit (Thoughts)
    # Extract path from metadata
    holon_meta = meta["nexus_holon"]
    mount_point = holon_meta.entry_path

    # In manifest: "exports": {"circuits": "./content/circuits"}
    # pack_vibe puts content in 'content/' and default packing structure
    # With 'thread' mode, base_loader verifies content/ AND entry_point is found
    # So mount_point is correct.

    # Circuit path: mount_point/content/circuits
    circuit_dir = mount_point / "content/circuits"

    assert circuit_dir.exists()
    assert (circuit_dir / "golden.yaml").exists()

    # Verify CircuitLoader accepts it
    circuits, circuit_meta = CircuitLoader.discover_and_load(scan_paths=[circuit_dir], force_refresh=True)

    assert "golden_spiral" in circuits
    assert circuits["golden_spiral"]["type"] == "fractal"
    print("\n✅ Golden Holon Verified: Code and Thoughts are One.")
