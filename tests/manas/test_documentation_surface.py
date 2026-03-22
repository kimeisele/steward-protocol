from pathlib import Path
from types import SimpleNamespace

from vibe_core.plugins.opus_assistant.manas.cortex.adapters.documentation_adapter import DocumentationCortexAdapter
from vibe_core.plugins.opus_assistant.manas.cortex.documentation_surface import DocumentationSurfaceBuilder


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_documentation_surface_builder_gathers_projection_context():
    builder = DocumentationSurfaceBuilder(workspace=_repo_root())

    ctx = builder.gather_context()

    assert ctx.projection_mode in {"local", "agent_internet"}
    assert ctx.repo_python_files >= 1
    assert ctx.node_count >= 0


def test_documentation_adapter_redirects_sync_requests_to_projection_boundary():
    adapter = DocumentationCortexAdapter(workspace=_repo_root())

    result = adapter.execute(SimpleNamespace(title="sync wiki", intent_type="update_opus_documentation", params={}))

    assert result["success"] is False
    assert result["action"] == "public_wiki_removed"
    assert "agent-internet" in result["error"]


def test_documentation_adapter_reports_documentation_surface_without_authority_export_path():
    adapter = DocumentationCortexAdapter(workspace=_repo_root())

    result = adapter.execute(SimpleNamespace(title="update readme", intent_type="update_readme", params={}))

    assert result["success"] is True
    assert result["action"] == "documentation_surface_ready"
    assert result["document_count"] == 8