import json

from scripts.pack_vibe import build_container
from vibe_core.loaders.base_loader import UnifiedLoader
from vibe_core.loaders.circuit_loader import CircuitLoader


class CognitiveLoader(UnifiedLoader):
    """Minimal loader helper."""

    item_type = "cognitive_pack"


def test_load_circuit_from_cognitive_pack(tmp_path):
    """
    Verify that CircuitLoader can read from a mounted cognitive container.
    """
    # 1. Create Cognitive Pack with Circuit
    source_dir = tmp_path / "brain_circuit"
    source_dir.mkdir()
    manifest = {
        "id": "brain_circuit_pack",
        "type": "cognitive_pack",
        "version": "1.0.0",
        "exports": {"circuits": "./circuits"},
    }
    (source_dir / "manifest.json").write_text(json.dumps(manifest))
    (source_dir / "tests").mkdir()
    (source_dir / "tests" / "test.py").write_text("# pass")

    # Create valid Circuit YAML
    (source_dir / "circuits").mkdir()
    circuit_yaml = """
circuit_id: cognitive_test_circuit
type: state_machine
description: A circuit loaded from a Holon Vibe Container
states:
  - id: start
    type: terminal
"""
    (source_dir / "circuits" / "cognitive_test.yaml").write_text(circuit_yaml)

    # 2. Build Container
    container_path = tmp_path / "brain.vibe"
    build_container(source_dir, container_path)

    # 3. Mount Container
    meta = CognitiveLoader._process_container(container_path)
    assert meta.loaded_successfully

    # 4. Extract Circuit Path (exports resolution logic simulation)
    # In a real system, a manager would read exports. Here we assume we know.
    # Export path from manifest: "./circuits" -> mount_point / "content/circuits"
    # Note: pack_vibe puts everything under 'content/' unless top-level special.
    # Check if 'circuits' is top-level special in pack_vibe?
    # pack_vibe.py:
    #                 if str(rel_path).startswith("tests"): ...
    #                 elif str(rel_path).startswith("hollows"): ...
    #                 else: arcname = f"content/{rel_path}"
    # So 'circuits' -> 'content/circuits'

    circuit_path = meta.entry_path / "content/circuits"
    assert circuit_path.exists()

    # 5. Load with CircuitLoader
    # Force refresh to ignore cache
    circuits, circuit_meta = CircuitLoader.discover_and_load(scan_paths=[circuit_path], force_refresh=True)

    # 6. Verify
    assert "cognitive_test_circuit" in circuits
    loaded_meta = circuit_meta["cognitive_test_circuit"]
    assert loaded_meta.circuit_id == "cognitive_test_circuit"
    assert str(loaded_meta.file_path).startswith(str(circuit_path))
    print(f"\\n✅ Successfully loaded circuit from Holon: {loaded_meta.file_path}")
