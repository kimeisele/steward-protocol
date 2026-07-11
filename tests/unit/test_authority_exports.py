from pathlib import Path

from vibe_core.authority_exports import export_authority_bundle, export_authority_surface_metadata


def test_export_authority_surface_metadata_marks_public_federation_defaults():
    root = Path(__file__).resolve().parents[2]

    payload = export_authority_surface_metadata(workspace=root, source_sha="abc123")

    assert payload["kind"] == "surface_metadata"
    assert payload["repo_id"] == "steward-protocol"
    assert payload["federation_surface"]["surface_role"] == "canonical_public_source_authority"
    assert payload["federation_surface"]["canonical_for_public_federation"] is True
    assert "authority_feed_manifest" in payload["federation_surface"]["public_channels"]


def test_export_authority_bundle_uses_neutral_exporter_contract():
    root = Path(__file__).resolve().parents[2]

    bundle = export_authority_bundle(workspace=root, source_sha="feed-abc123")

    assert bundle["kind"] == "source_authority_bundle"
    assert bundle["repo_role"]["repo_id"] == "steward-protocol"
    assert bundle["artifacts"][".authority-exports/source-surface-registry.json"]["document_count"] == 8
    assert (
        bundle["artifacts"][".authority-exports/surface-metadata.json"]["federation_surface"]["publication_model"]
        == "github_authority_feed_plus_projected_wiki"
    )
