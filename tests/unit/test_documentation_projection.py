def test_gather_projection_context_prefers_agent_internet_snapshot(monkeypatch, tmp_path):
    from vibe_core.plugins.opus_assistant.manas.cortex import documentation_surface

    monkeypatch.setenv("AGENT_INTERNET_LOTUS_BASE_URL", "https://lotus.example.test")
    monkeypatch.setenv("AGENT_INTERNET_LOTUS_TOKEN", "token-123")
    monkeypatch.setenv("AGENT_INTERNET_PROJECTION_ROOT", "/srv/steward-protocol")

    calls = []

    def fake_fetch(config, path, *, query=None):
        calls.append((path, dict(query or {}), dict(config)))
        if path == "/v1/lotus/agent-web-manifest":
            return {
                "agent_web_manifest": {
                    "documents": [{"document_id": "home"}],
                    "entrypoints": {"default": "Home.md"},
                    "stats": {"service_count": 2, "route_count": 4},
                }
            }
        if path == "/v1/lotus/agent-web-graph":
            return {"agent_web_graph": {"stats": {"node_count": 6, "edge_count": 9}}}
        if path == "/v1/lotus/agent-web-repo-graph":
            return {"agent_web_repo_graph": {"summary": {"node_count": 33, "edge_count": 44, "constraint_count": 5}}}
        if path == "/v1/lotus/agent-web-index":
            return {"agent_web_index": {"stats": {"record_count": 12}}}
        raise AssertionError(path)

    monkeypatch.setattr(documentation_surface, "_fetch_agent_internet_json", fake_fetch)

    builder = documentation_surface.DocumentationSurfaceBuilder(workspace=tmp_path)
    ctx = documentation_surface.DocumentationContext(node_count=1, edge_count=2, constraint_count=3)

    builder._gather_projection_context(ctx)

    assert ctx.projection_mode == "agent_internet"
    assert ctx.projection_base_url == "https://lotus.example.test"
    assert ctx.projection_root == "/srv/steward-protocol"
    assert ctx.node_count == 33
    assert ctx.edge_count == 44
    assert ctx.constraint_count == 5
    assert [call[0] for call in calls] == [
        "/v1/lotus/agent-web-manifest",
        "/v1/lotus/agent-web-graph",
        "/v1/lotus/agent-web-repo-graph",
        "/v1/lotus/agent-web-index",
    ]


def test_render_projection_section_reports_local_fallback():
    from vibe_core.plugins.opus_assistant.manas.cortex.documentation_surface import (
        DocumentationContext,
        render_projection_status_section,
    )

    assert "Local fallback active" in render_projection_status_section(DocumentationContext())
