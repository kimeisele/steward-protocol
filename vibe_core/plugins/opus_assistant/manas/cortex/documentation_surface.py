"""Documentation surface context utilities.

This module replaces the legacy local SUTRA wiki compiler path.
Source-authority export stays in neutral top-level modules; public projection and
publication belong to `agent-internet`.
"""

from __future__ import annotations

import json
import logging
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger("MANAS.Cortex.DocumentationSurface")


@dataclass
class DocumentationContext:
    """Context data for documentation-surface inspection."""

    system_name: str = "STEWARD Protocol"
    version: str = "1.0.0"
    timestamp: str = ""
    agents: list[dict[str, Any]] = field(default_factory=list)
    capabilities: dict[str, list[str]] = field(default_factory=dict)
    domains: dict[str, list[str]] = field(default_factory=dict)
    node_count: int = 0
    edge_count: int = 0
    constraint_count: int = 0
    knowledge_summary: str = ""
    constitution_articles: list[str] = field(default_factory=list)
    governance_rules: list[str] = field(default_factory=list)
    modules: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, str]] = field(default_factory=list)
    repo_python_files: int = 0
    repo_markdown_files: int = 0
    node_manifest_count: int = 0
    repo_areas: list[dict[str, Any]] = field(default_factory=list)
    cartridge_families: list[dict[str, Any]] = field(default_factory=list)
    projection_mode: str = "local"
    projection_base_url: str = ""
    projection_root: str = ""
    projection_manifest: dict[str, Any] = field(default_factory=dict)
    projection_public_graph: dict[str, Any] = field(default_factory=dict)
    projection_repo_graph: dict[str, Any] = field(default_factory=dict)
    projection_search_index: dict[str, Any] = field(default_factory=dict)


def render_projection_status_section(ctx: DocumentationContext) -> str:
    """Render agent-internet projection status for documentation surfaces."""
    if ctx.projection_mode != "agent_internet":
        return "- Local fallback active - agent-internet projection surfaces not configured."

    manifest = dict(ctx.projection_manifest)
    public_graph = dict(ctx.projection_public_graph)
    repo_graph = dict(ctx.projection_repo_graph)
    search_index = dict(ctx.projection_search_index)
    manifest_stats = _projection_stats({"agent_web_manifest": manifest}, "agent_web_manifest")
    graph_stats = _projection_stats({"agent_web_graph": public_graph}, "agent_web_graph")
    repo_summary = _projection_summary({"agent_web_repo_graph": repo_graph}, "agent_web_repo_graph")
    index_stats = _projection_stats({"agent_web_index": search_index}, "agent_web_index")
    entrypoints = sorted(str(name) for name in dict(manifest.get("entrypoints", {})).keys())
    return "\n".join(
        [
            "| Projection Surface | Snapshot |",
            "|--------------------|----------|",
            f"| `agent-web-manifest` | {len(manifest.get('documents', []))} docs / {len(entrypoints)} entrypoints / {manifest_stats.get('service_count', 0)} services / {manifest_stats.get('route_count', 0)} routes |",
            f"| `agent-web-graph` | {graph_stats.get('node_count', 0)} public nodes / {graph_stats.get('edge_count', 0)} public edges |",
            f"| `agent-web-repo-graph` | {repo_summary.get('node_count', 0)} repo nodes / {repo_summary.get('edge_count', 0)} repo edges / {repo_summary.get('constraint_count', 0)} constraints |",
            f"| `agent-web-index` | {index_stats.get('record_count', 0)} searchable records |",
            "",
            f"Projection source: `{ctx.projection_base_url}`",
            f"Projection root: `{ctx.projection_root}`",
            f"Entrypoints: {', '.join(f'`{name}`' for name in entrypoints[:8]) if entrypoints else '_none published_'}",
        ]
    )


class DocumentationSurfaceBuilder:
    """Build neutral documentation-surface context without local wiki publishing."""

    def __init__(self, workspace: Path | None = None):
        self._workspace = workspace or Path.cwd()

    def gather_context(self) -> DocumentationContext:
        ctx = DocumentationContext(timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
        self._gather_mandala_context(ctx)
        self._gather_akasha_context(ctx)
        self._gather_constitution_context(ctx)
        self._gather_module_context(ctx)
        self._gather_projection_context(ctx)
        return ctx

    def _gather_mandala_context(self, ctx: DocumentationContext) -> None:
        try:
            from .mandala import ConfigWeaver

            weaver = ConfigWeaver(workspace=self._workspace)
            weaver.weave()
            cartridges_root = self._workspace / "vibe_core" / "cartridges"
            runtime_families: Counter[str] = Counter()
            for agent_id, manifest in weaver.manifests.items():
                ctx.agents.append({
                    "id": agent_id,
                    "name": manifest.name,
                    "domain": manifest.domain,
                    "version": manifest.version,
                    "capabilities": list(manifest.capabilities.keys()),
                    "tier": manifest.tier,
                })
                family = str(getattr(manifest, "tier", "agent") or "agent").lower()
                source_path = getattr(manifest, "source_path", None)
                if isinstance(source_path, Path):
                    try:
                        rel = source_path.relative_to(cartridges_root)
                        if rel.parts:
                            family = rel.parts[0]
                    except ValueError:
                        pass
                runtime_families[family] += 1
                ctx.domains.setdefault(manifest.domain, []).append(agent_id)
                ctx.capabilities[agent_id] = list(manifest.capabilities.keys())
            ctx.node_manifest_count = len(weaver.manifests)
            ctx.cartridge_families = [{"name": name, "agents": count} for name, count in runtime_families.most_common(10)]
        except Exception as exc:
            logger.warning("DocumentationSurface: could not gather MANDALA context: %s", exc)

    def _gather_akasha_context(self, ctx: DocumentationContext) -> None:
        try:
            from .akasha import AkashaPort, AkashaQuery

            port = AkashaPort(self._workspace)
            ctx.node_count = port.get_node_count()
            ctx.edge_count = port.get_edge_count()
            if port.graph:
                ctx.constraint_count = len(port.graph.constraints)
            ctx.knowledge_summary = AkashaQuery(port).graph_summary().raw_context
        except Exception as exc:
            logger.warning("DocumentationSurface: could not gather AKASHA context: %s", exc)

    def _gather_constitution_context(self, ctx: DocumentationContext) -> None:
        try:
            for _level, heading in _extract_markdown_outline(self._workspace / "CONSTITUTION.md"):
                ctx.constitution_articles.append(heading)
            governance_path = self._workspace / "vibe_core" / "governance"
            if governance_path.exists():
                for rule_file in governance_path.glob("*.py"):
                    if rule_file.name != "__init__.py":
                        ctx.governance_rules.append(rule_file.stem)
        except Exception as exc:
            logger.warning("DocumentationSurface: could not gather constitution context: %s", exc)

    def _gather_module_context(self, ctx: DocumentationContext) -> None:
        try:
            vibe_core = self._workspace / "vibe_core"
            if not vibe_core.exists():
                return
            repo_areas: Counter[str] = Counter()
            for module_dir in vibe_core.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("_"):
                    py_files = list(module_dir.glob("**/*.py"))
                    if py_files:
                        repo_areas[module_dir.name] = len(py_files)
                        ctx.modules.append({
                            "name": module_dir.name,
                            "files": len(py_files),
                            "path": str(module_dir.relative_to(self._workspace)),
                        })
            ctx.repo_python_files = len(list(vibe_core.rglob("*.py")))
            ctx.repo_markdown_files = len(list(self._workspace.rglob("*.md")))
            ctx.repo_areas = [{"name": name, "python_files": count} for name, count in repo_areas.most_common(10)]
        except Exception as exc:
            logger.warning("DocumentationSurface: could not gather module context: %s", exc)

    def _gather_projection_context(self, ctx: DocumentationContext) -> None:
        config = _resolve_agent_internet_projection_config(self._workspace)
        if not config:
            return
        try:
            query = {"root": config["root"]}
            manifest_payload = _fetch_agent_internet_json(config, "/v1/lotus/agent-web-manifest", query=query)
            public_graph_payload = _fetch_agent_internet_json(config, "/v1/lotus/agent-web-graph", query=query)
            repo_graph_payload = _fetch_agent_internet_json(config, "/v1/lotus/agent-web-repo-graph", query={**query, "limit": 25})
            search_index_payload = _fetch_agent_internet_json(config, "/v1/lotus/agent-web-index", query=query)
            ctx.projection_mode = "agent_internet"
            ctx.projection_base_url = str(config["base_url"])
            ctx.projection_root = str(config["root"])
            ctx.projection_manifest = dict(manifest_payload.get("agent_web_manifest", {}))
            ctx.projection_public_graph = dict(public_graph_payload.get("agent_web_graph", {}))
            ctx.projection_repo_graph = dict(repo_graph_payload.get("agent_web_repo_graph", {}))
            ctx.projection_search_index = dict(search_index_payload.get("agent_web_index", {}))
            repo_summary = dict(ctx.projection_repo_graph.get("summary", {}))
            if repo_summary:
                ctx.node_count = int(repo_summary.get("node_count", ctx.node_count) or ctx.node_count)
                ctx.edge_count = int(repo_summary.get("edge_count", ctx.edge_count) or ctx.edge_count)
                ctx.constraint_count = int(repo_summary.get("constraint_count", ctx.constraint_count) or ctx.constraint_count)
        except Exception as exc:
            logger.warning("DocumentationSurface: could not gather agent-internet projection surfaces: %s", exc)


def _extract_markdown_outline(path: Path) -> list[tuple[int, str]]:
    outline: list[tuple[int, str]] = []
    if not path.exists():
        return outline
    for raw_line in path.read_text().splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("### "):
            outline.append((3, stripped[4:].strip()))
        elif stripped.startswith("## "):
            outline.append((2, stripped[3:].strip()))
    return outline


def _resolve_agent_internet_projection_config(workspace: Path) -> dict[str, Any]:
    base_url = str(os.environ.get("AGENT_INTERNET_LOTUS_BASE_URL", "")).rstrip("/")
    bearer_token = str(os.environ.get("AGENT_INTERNET_LOTUS_TOKEN", ""))
    timeout_s = int(str(os.environ.get("AGENT_INTERNET_LOTUS_TIMEOUT_S", "20") or "20"))
    root = str(
        os.environ.get("AGENT_INTERNET_PROJECTION_ROOT")
        or os.environ.get("SUTRA_AGENT_INTERNET_ROOT")
        or workspace.resolve()
    )
    if not base_url or not bearer_token:
        return {}
    return {"base_url": base_url, "bearer_token": bearer_token, "timeout_s": timeout_s, "root": root}


def _fetch_agent_internet_json(config: dict[str, Any], path: str, *, query: dict[str, Any] | None = None) -> dict[str, Any]:
    encoded = urlencode({str(key): str(value) for key, value in dict(query or {}).items() if value not in (None, "")}, doseq=True)
    suffix = f"?{encoded}" if encoded else ""
    request = Request(f"{config['base_url']}{path}{suffix}", method="GET")
    request.add_header("Authorization", f"Bearer {config['bearer_token']}")
    request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=int(config["timeout_s"])) as response:
        return json.loads(response.read().decode("utf-8"))


def _projection_stats(payload: dict[str, Any], key: str) -> dict[str, Any]:
    return dict(dict(payload).get(key, {}).get("stats", {}))


def _projection_summary(payload: dict[str, Any], key: str) -> dict[str, Any]:
    return dict(dict(payload).get(key, {}).get("summary", {}))