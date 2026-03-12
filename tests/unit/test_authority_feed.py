import json
from pathlib import Path

from vibe_core.authority_feed import write_authority_feed


def test_write_authority_feed_materializes_manifest_and_bundle(tmp_path):
    root = Path(__file__).resolve().parents[2]

    manifest_path, manifest = write_authority_feed(workspace=root, output_dir=tmp_path, source_sha="feed-abc123")

    bundle_path = tmp_path / manifest["bundle"]["path"]
    registry_path = tmp_path / manifest["artifacts"][".authority-exports/source-surface-registry.json"]["path"]
    metadata_path = tmp_path / manifest["artifacts"][".authority-exports/surface-metadata.json"]["path"]
    persisted_manifest = json.loads(manifest_path.read_text())
    persisted_bundle = json.loads(bundle_path.read_text())

    assert manifest_path == (tmp_path / "latest-authority-manifest.json").resolve()
    assert persisted_manifest["kind"] == "source_authority_feed_manifest"
    assert persisted_manifest["source_repo_id"] == "steward-protocol"
    assert persisted_manifest["source_sha"] == "feed-abc123"
    assert persisted_bundle["source_sha"] == "feed-abc123"
    assert registry_path.exists()
    assert json.loads(registry_path.read_text())["kind"] == "source_surface_registry"
    assert json.loads(metadata_path.read_text())["federation_surface"]["canonical_for_public_federation"] is True