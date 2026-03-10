from pathlib import Path

import pytest
import yaml

from vibe_core.source_authority_registry import load_source_authority_registry


def test_load_checked_in_source_authority_registry():
    repo_root = Path(__file__).resolve().parents[2]

    registry = load_source_authority_registry(workspace=repo_root)

    assert registry.kind == "source_authority_registry"
    assert registry.version == 1
    assert registry.repo_id == "steward-protocol"
    assert len(registry.documents) == 8
    assert {record.document_id for record in registry.documents} == {
        "readme",
        "index",
        "constitution",
        "agi_manifesto",
        "steward_operating_model",
        "protocols",
        "architecture",
        "kernel",
    }
    documents_by_id = {record.document_id: record for record in registry.documents}
    assert documents_by_id["readme"].labels["nav_label"] == "Start Here"
    assert documents_by_id["constitution"].labels["nav_label"] == "Constitution"
    assert documents_by_id["protocols"].labels["nav_label"] == "Protocols"
    assert "renderer" not in registry.to_payload()["documents"][0]
    assert "featured" not in registry.to_payload()["documents"][0]


def test_reject_projection_keys_in_source_authority_registry(tmp_path):
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "kind": "source_authority_registry",
                "version": 1,
                "repo_id": "steward-protocol",
                "documents": [
                    {
                        "document_id": "constitution",
                        "title": "Constitution",
                        "source_path": "CONSTITUTION.md",
                        "authority": "binding",
                        "domain": "governance",
                        "renderer": "canonical_doc",
                    }
                ],
            },
            sort_keys=False,
        )
    )

    with pytest.raises(ValueError, match="unsupported_source_authority_document_keys:renderer"):
        load_source_authority_registry(registry_path=registry_path)


def test_reject_duplicate_document_ids(tmp_path):
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "kind": "source_authority_registry",
                "version": 1,
                "repo_id": "steward-protocol",
                "documents": [
                    {
                        "document_id": "constitution",
                        "title": "Constitution",
                        "source_path": "CONSTITUTION.md",
                        "authority": "binding",
                        "domain": "governance",
                    },
                    {
                        "document_id": "constitution",
                        "title": "Constitution Copy",
                        "source_path": "docs/governance/CONSTITUTION_COPY.md",
                        "authority": "binding",
                        "domain": "governance",
                    },
                ],
            },
            sort_keys=False,
        )
    )

    with pytest.raises(ValueError, match="duplicate_source_authority_document_id:constitution"):
        load_source_authority_registry(registry_path=registry_path)