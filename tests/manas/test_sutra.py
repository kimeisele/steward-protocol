from pathlib import Path
from types import SimpleNamespace

from vibe_core.plugins.opus_assistant.manas.cortex.adapters.sutra_adapter import SutraCortexAdapter
from vibe_core.plugins.opus_assistant.manas.cortex.sutra import (
    SutraOrchestrator,
    get_sutra_for_chat,
    handle_sutra_query,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_export_surface_metadata():
    orch = SutraOrchestrator(workspace=_repo_root())

    payload = orch.export_surface_metadata()

    assert payload["kind"] == "wiki_surface_registry"
    assert payload["version"] == 2
    assert payload["projection"]["mode"] in {"local", "agent_internet"}
    assert payload["system_metrics"]["repo_python_files"] >= 1


def test_export_source_surface_registry_uses_neutral_source_contract():
    orch = SutraOrchestrator(workspace=_repo_root())

    payload = orch.export_source_surface_registry()

    assert payload["kind"] == "source_surface_registry"
    assert payload["repo_id"] == "steward-protocol"
    assert payload["document_count"] == 8
    assert "pages" not in payload
    assert all("renderer" not in record for record in payload["documents"])


def test_export_authority_bundle_uses_source_documents():
    orch = SutraOrchestrator(workspace=_repo_root())

    payload = orch.export_authority_bundle(source_sha="abc123")

    assert payload["kind"] == "source_authority_bundle"
    assert payload["source_sha"] == "abc123"
    assert payload["artifacts"][".authority-exports/source-surface-registry.json"]["document_count"] == 8
    assert payload["artifacts"][".authority-exports/canonical-surface.json"]["documents"][0]["document_id"] == "readme"
    assert payload["artifacts"][".authority-exports/surface-metadata.json"]["public_surface"]["overview_page"]["wiki_name"] == "Steward-Authority"
    assert payload["artifacts"][".authority-exports/surface-metadata.json"]["federation_surface"]["surface_role"] == "canonical_public_source_authority"


def test_handle_sutra_query_describes_available_exports():
    result = handle_sutra_query("show authority bundle", workspace=_repo_root())

    assert "Source Authority Export" in result
    assert "canonical_surface" in result
    assert "source_surface_registry" in result


def test_handle_sutra_query_redirects_local_wiki_publish_requests():
    result = handle_sutra_query("sync wiki", workspace=_repo_root())

    assert "agent-internet" in result
    assert "no longer publishes local wiki pages" in result


def test_get_sutra_for_chat_reports_export_boundary():
    result = get_sutra_for_chat(workspace=_repo_root())

    assert "Source Authority Export" in result
    assert "agent-internet" in result
    assert "Local wiki preview/generation/publish has been removed" in result


def test_sutra_adapter_redirects_sync_requests_to_projection_boundary():
    adapter = SutraCortexAdapter(workspace=_repo_root())

    result = adapter.execute(SimpleNamespace(title="sync wiki", intent_type="update_opus_documentation", params={}))

    assert result["success"] is False
    assert result["action"] == "public_wiki_removed"
    assert "agent-internet" in result["error"]

