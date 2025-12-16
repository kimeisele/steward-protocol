import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

# Define paths for temporary test plugins
TEST_ROOT = Path("tests/temp_fractal")
PARENT_DIR = TEST_ROOT / "parent_plugin"
CHILD_DIR = TEST_ROOT / "child_plugin"
DIST_DIR = TEST_ROOT / "dist"


def setup_plugin(path, plugin_id, dependencies=None):
    """Helper to create a minimal valid plugin."""
    path.mkdir(parents=True, exist_ok=True)

    # Manifest
    manifest = {
        "id": plugin_id,
        "name": f"Test {plugin_id}",
        "version": "0.1.0",
        "type": "plugin",
        "entry_point": "plugin_main.py",
        "description": f"Fractal test {plugin_id}",
    }
    if dependencies:
        manifest["dependencies"] = dependencies

    with open(path / "manifest.json", "w") as f:
        json.dump(manifest, f)

    # Main Code
    with open(path / "plugin_main.py", "w") as f:
        f.write(f"""
from vibe_core.plugin_protocol import KernelPlugin

class {plugin_id.capitalize()}Plugin(KernelPlugin):
    @property
    def plugin_id(self):
        return "{plugin_id}"

    def on_boot(self, kernel):
        print(f"BOOT: {{self.plugin_id}}")
""")

    # Tests dir (required)
    (path / "tests").mkdir(exist_ok=True)
    with open(path / "tests" / "test_dummy.py", "w") as f:
        f.write("def test_dummy(): pass")


@pytest.fixture
def fractal_env():
    """Setup and Teardown for fractal test environment."""
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir()
    DIST_DIR.mkdir()

    yield

    # Cleanup
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)


@pytest.mark.asyncio
async def test_fractal_vibe_loading(fractal_env):
    """
    Test the 'Matrjoschka' scenario:
    1. Build Child Plugin -> child.vibe
    2. Embed Child in Parent/hollows/
    3. Build Parent Plugin -> parent.vibe
    4. Boot Kernel with Parent (ensure Child loads recursively)
    """

    # 1. Create Child Source
    setup_plugin(CHILD_DIR, "fractal_child")

    # 2. Pack Child
    child_vibe = DIST_DIR / "fractal_child.vibe"
    subprocess.run(
        ["python3", "scripts/pack_vibe.py", str(CHILD_DIR), "-o", str(child_vibe)], check=True, capture_output=True
    )
    assert child_vibe.exists()

    # 3. Create Parent Source
    setup_plugin(PARENT_DIR, "fractal_parent")

    # 4. Embed Child in Parent's 'hollows' directory
    # 'hollows' is the standard directory for internal/vendor dependencies in a Holon
    hollows_dir = PARENT_DIR / "hollows"
    hollows_dir.mkdir()
    shutil.copy(child_vibe, hollows_dir / "fractal_child.vibe")

    # 5. Pack Parent
    parent_vibe = DIST_DIR / "fractal_parent.vibe"
    subprocess.run(
        ["python3", "scripts/pack_vibe.py", str(PARENT_DIR), "-o", str(parent_vibe)], check=True, capture_output=True
    )
    assert parent_vibe.exists()

    # 6. Verify Structure (Static Analysis)
    with zipfile.ZipFile(parent_vibe, "r") as z:
        files = z.namelist()
        print(f"Parent Content: {files}")
        assert "hollows/fractal_child.vibe" in files, "Child not properly embedded in Parent"

    # 7. Boot Verification
    # We need to tell the kernel to load this specific plugin.
    # Currently RealVibeKernel scans 'vibe_core/plugins' and 'knowledge'.
    # We can fake it by putting parent.vibe in 'vibe_core/plugins' temporarily
    # OR we can instantiate PluginLoader directly to test the discovery logic.

    # Let's try mounting it manually first to test the loader logic
    # This simulates what the Kernel would do if it found it.

    from vibe_core.plugin_loader import PluginLoader

    # We need to trick the discovery to find our parent.vibe
    # So we move it to a location the loader scans, or we pass the specific path
    # PluginLoader.discover_and_load takes 'scan_paths'.

    # scan_paths expects directories containing potential plugins.
    # We will point it to DIST_DIR which contains parent.vibe (and child.vibe, but we prefer parent)

    # Note: DIST_DIR has both parent.vibe and child.vibe (the loose one).
    # To be strict, we should remove the loose child.vibe so we only load it via parent.
    os.remove(child_vibe)

    # Now DIST_DIR only has 'fractal_parent.vibe'.
    # Inside 'fractal_parent.vibe' is 'hollows/fractal_child.vibe'.

    print(f"Scanning {DIST_DIR} for plugins...")
    plugins_map, metadata = PluginLoader.discover_and_load(scan_paths=[DIST_DIR])

    print(f"Discovered Plugins: {list(plugins_map.keys())}")

    assert "fractal_parent" in plugins_map, "Parent plugin not discovered"

    # CRITICAL: Did the child load?
    # This depends on if PluginLoader recursively scans 'hollows' inside mounted containers.
    # If this fails, we need to implement that logic.
    if "fractal_child" not in plugins_map:
        print("⚠️ Child plugin MISSING. Recursive loading not implemented?")

        # Inspection for debugging
        parent_meta = metadata["fractal_parent"]
        print(f"Parent Mount Path: {parent_meta.entry_path}")
        if parent_meta.entry_path:
            embedded_child = parent_meta.entry_path / "hollows" / "fractal_child.vibe"
            print(f"Scanning for child at: {embedded_child}")
            print(f"Exists: {embedded_child.exists()}")

    assert "fractal_child" in plugins_map, "Child plugin (Fractal Depth) failed to load recursively"

    print("✅ Fractal Build Test Passed: Parent loaded Child from hollows/")
