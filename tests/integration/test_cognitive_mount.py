import json

from scripts.pack_vibe import build_container
from vibe_core.loaders.base_loader import UnifiedLoader


class CognitiveLoader(UnifiedLoader):
    """Minimal loader to test cognitive pack loading."""

    item_type = "cognitive_pack"


def test_cognitive_mount_no_execution(tmp_path):
    """
    Verify that a cognitive pack is:
    1. Mounted successfully
    2. Loaded with success flag
    3. NOT added to sys.path (implicit check via no code exec)
    """
    # 1. Create Cognitive Pack
    source_dir = tmp_path / "brain"
    source_dir.mkdir()
    manifest = {"id": "test_brain", "type": "cognitive_pack", "version": "1.0.0", "exports": {"data": "./data"}}
    (source_dir / "manifest.json").write_text(json.dumps(manifest))
    (source_dir / "tests").mkdir()  # Compliance
    (source_dir / "tests" / "test.py").write_text("# pass")
    (source_dir / "data").mkdir()
    (source_dir / "data" / "memory.txt").write_text("Recall")

    container_path = tmp_path / "brain.vibe"
    build_container(source_dir, container_path)

    # 2. Process with Loader
    # We use UnifiedLoader helper _process_container directly or via subclass
    meta = CognitiveLoader._process_container(container_path)

    # 3. Assertions
    assert meta is not None
    assert meta.loaded_successfully is True
    assert meta.item_id == "test_brain"
    # Ensure entry class is None
    assert meta.entry_class is None
    # Ensure mount point exists and contains data
    assert meta.entry_path.exists()
    assert (meta.entry_path / "content/data/memory.txt").exists()
