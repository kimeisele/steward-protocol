import json
import zipfile

from scripts.pack_vibe import build_container


def test_pack_cognitive_container(tmp_path):
    """Test packing a cognitive container (Data-Only)."""

    # Setup source directory
    source_dir = tmp_path / "genesis_knowledge"
    source_dir.mkdir()

    # Create manifest
    manifest = {
        "id": "genesis_knowledge",
        "type": "cognitive_pack",
        "version": "1.0.0",
        "exports": {"circuits": "./circuits"},
    }
    (source_dir / "manifest.json").write_text(json.dumps(manifest))

    # Create content
    (source_dir / "circuits").mkdir()
    (source_dir / "circuits" / "test.yaml").write_text("states: []")

    # Create required tests dir
    (source_dir / "tests").mkdir()
    (source_dir / "tests" / "test_data.py").write_text("# pass")

    # Build
    output_path = tmp_path / "genesis.vibe"
    build_container(source_dir, output_path)

    assert output_path.exists()

    # Verify contents
    with zipfile.ZipFile(output_path, "r") as z:
        namelist = z.namelist()
        assert "manifest.json" in namelist
        assert "content/circuits/test.yaml" in namelist
        # Ensure no plugin_main.py is required
