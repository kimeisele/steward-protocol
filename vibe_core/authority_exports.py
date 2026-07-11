from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vibe_core.source_authority_registry import SourceAuthorityDocumentRecord, load_source_authority_registry

STEWARD_REPO_ID = "steward-protocol"
AUTHORITY_EXPORT_CONTRACT_VERSION = 1
AUTHORITY_EXPORT_ARTIFACTS = {
    "canonical_surface": ".authority-exports/canonical-surface.json",
    "public_summary_registry": ".authority-exports/public-summary-registry.json",
    "source_surface_registry": ".authority-exports/source-surface-registry.json",
    "repo_graph": ".authority-exports/repo-graph.json",
    "surface_metadata": ".authority-exports/surface-metadata.json",
}
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _artifact_sha256(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _parse_git_origin_url(workspace: Path) -> str:
    config_path = workspace / ".git" / "config"
    if not config_path.exists():
        return ""
    in_origin = False
    origin_url = ""
    for raw_line in config_path.read_text().splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("[remote "):
            in_origin = stripped == '[remote "origin"]'
            continue
        if in_origin and stripped.startswith("url ="):
            origin_url = stripped.split("=", 1)[1].strip()
            break
    if origin_url.startswith("git@github.com:"):
        return f"https://github.com/{origin_url.removeprefix('git@github.com:').removesuffix('.git')}"
    if origin_url.startswith("https://github.com/"):
        return origin_url.removesuffix(".git")
    return ""


def _slugify_wiki_name(value: str) -> str:
    parts = [part for part in re.sub(r"[^A-Za-z0-9]+", " ", value).strip().split() if part]
    return "-".join(parts) or "Document"


def _normalize_bound_markdown(
    content: str, *, source_path: str, workspace: Path, wiki_names: dict[str, str], repo_web_url: str
) -> str:
    normalized = content.replace("-->#", "-->\n#").replace("--><", "-->\n<")
    source_file = (workspace / source_path).resolve()

    def _rewrite_link(match: re.Match[str]) -> str:
        label, target = match.groups()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        relative_target, anchor = (target.split("#", 1) + [""])[:2]
        if not relative_target:
            return match.group(0)
        anchor_suffix = f"#{anchor}" if anchor else ""
        resolved = (source_file.parent / relative_target).resolve()
        try:
            rel_path = resolved.relative_to(workspace.resolve()).as_posix()
        except ValueError:
            return match.group(0)
        if rel_path in wiki_names:
            return f"[{label}]({wiki_names[rel_path]}{anchor_suffix})"
        if repo_web_url and resolved.exists():
            return f"[{label}]({repo_web_url}/blob/main/{rel_path}{anchor_suffix})"
        return match.group(0)

    return MARKDOWN_LINK_RE.sub(_rewrite_link, normalized).strip() + "\n"


def _source_documents(workspace: Path) -> tuple[SourceAuthorityDocumentRecord, ...]:
    return load_source_authority_registry(workspace=workspace).documents


def _wiki_names(documents: tuple[SourceAuthorityDocumentRecord, ...]) -> dict[str, str]:
    return {record.source_path: _slugify_wiki_name(record.title) for record in documents}


def _repo_file_counts(workspace: Path) -> tuple[int, int, int, list[dict[str, Any]]]:
    skip_names = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "node_modules", "dist", "build"}
    python_files = 0
    markdown_files = 0
    yaml_files = 0
    repo_areas: Counter[str] = Counter()
    for path in workspace.rglob("*"):
        if not path.is_file() or any(part in skip_names for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix == ".py":
            python_files += 1
            rel_parts = path.relative_to(workspace).parts
            repo_areas[rel_parts[0] if rel_parts else workspace.name] += 1
        elif suffix == ".md":
            markdown_files += 1
        elif suffix in {".yaml", ".yml"}:
            yaml_files += 1
    areas = [{"name": name, "python_files": count} for name, count in repo_areas.most_common(10)]
    return python_files, markdown_files, yaml_files, areas


def _canonical_source_document_payload(
    workspace: Path, repo_web_url: str, wiki_names: dict[str, str], document: SourceAuthorityDocumentRecord
) -> dict[str, Any]:
    source_path = workspace / document.source_path
    if source_path.exists():
        content = _normalize_bound_markdown(
            source_path.read_text(),
            source_path=document.source_path,
            workspace=workspace,
            wiki_names=wiki_names,
            repo_web_url=repo_web_url,
        )
    else:
        content = f"# {document.title}\n\n_Source document not found: `{document.source_path}`_\n"
    payload = document.to_payload()
    payload["public_summary"] = payload.pop("public_abstract")
    payload["content"] = content
    return payload


def export_source_surface_registry(*, workspace: Path | str | None = None) -> dict[str, Any]:
    root = Path(workspace or ".").resolve()
    documents = [record.to_payload() for record in _source_documents(root)]
    return {
        "kind": "source_surface_registry",
        "version": 1,
        "repo_id": STEWARD_REPO_ID,
        "generated_at": datetime.now(timezone.utc).timestamp(),
        "document_count": len(documents),
        "documents": documents,
    }


def export_public_summary_registry(*, workspace: Path | str | None = None) -> dict[str, Any]:
    root = Path(workspace or ".").resolve()
    records = [
        {
            "document_id": record.document_id,
            "title": record.title,
            "authority": record.authority,
            "domain": record.domain,
            "source_path": record.source_path,
            "public_summary": record.public_abstract,
            "labels": dict(record.labels),
        }
        for record in _source_documents(root)
    ]
    return {
        "kind": "public_summary_registry",
        "version": 1,
        "repo_id": STEWARD_REPO_ID,
        "generated_at": datetime.now(timezone.utc).timestamp(),
        "record_count": len(records),
        "records": records,
    }


def export_canonical_surface(*, workspace: Path | str | None = None) -> dict[str, Any]:
    root = Path(workspace or ".").resolve()
    documents = _source_documents(root)
    wiki_names = _wiki_names(documents)
    repo_web_url = _parse_git_origin_url(root)
    payloads = [_canonical_source_document_payload(root, repo_web_url, wiki_names, record) for record in documents]
    return {
        "kind": "canonical_surface",
        "version": 1,
        "repo_id": STEWARD_REPO_ID,
        "generated_at": datetime.now(timezone.utc).timestamp(),
        "document_count": len(payloads),
        "documents": payloads,
    }


def export_repo_graph_snapshot(*, workspace: Path | str | None = None) -> dict[str, Any]:
    root = Path(workspace or ".").resolve()
    documents = _source_documents(root)
    repo_python_files, repo_markdown_files, node_manifest_count, repo_areas = _repo_file_counts(root)
    return {
        "kind": "repo_graph",
        "version": 1,
        "repo_id": STEWARD_REPO_ID,
        "generated_at": datetime.now(timezone.utc).timestamp(),
        "summary": {
            "agent_count": 0,
            "domain_count": len({record.domain for record in documents}),
            "capability_count": 0,
            "node_count": len(documents),
            "edge_count": 0,
            "constraint_count": 0,
            "module_count": len(repo_areas),
            "repo_python_files": repo_python_files,
            "repo_markdown_files": repo_markdown_files,
            "node_manifest_count": node_manifest_count,
        },
        "repo_areas": repo_areas,
        "cartridge_families": [],
        "knowledge_summary": f"Neutral authority export derived from {len(documents)} source authority documents.",
    }


def export_authority_surface_metadata(*, workspace: Path | str | None = None, source_sha: str = "") -> dict[str, Any]:
    root = Path(workspace or ".").resolve()
    documents = _source_documents(root)
    repo_web_url = _parse_git_origin_url(root)
    repo_python_files, repo_markdown_files, node_manifest_count, _ = _repo_file_counts(root)
    pages = [
        {
            "id": record.document_id.upper(),
            "title": record.title,
            "wiki_name": _slugify_wiki_name(record.title),
            "filename": f"{_slugify_wiki_name(record.title)}.md",
            "page_class": "canonical",
            "authority": record.authority,
            "domain": record.domain,
            "section": record.domain.replace("_", " ").title(),
            "public_summary": record.public_abstract,
            "source_path": record.source_path,
            "featured": str(record.labels.get("featured") or "").lower() == "true",
            "include_in_sidebar": str(record.labels.get("include_in_sidebar") or "").lower() == "true",
            "query_aliases": [record.document_id.replace("_", " "), Path(record.source_path).stem.replace("_", " ")],
        }
        for record in documents
    ]
    sections = list(dict.fromkeys(str(page["section"]) for page in pages if str(page["section"])))
    return {
        "kind": "surface_metadata",
        "version": 1,
        "repo_id": STEWARD_REPO_ID,
        "source_sha": source_sha,
        "public_surface": {
            "repo_label": "Steward",
            "document_prefix": "steward",
            "overview_page": {
                "document_id": "steward_authority",
                "rel": "steward_authority",
                "kind": "steward_authority",
                "title": "Steward Authority",
                "wiki_name": "Steward-Authority",
                "entrypoint": True,
            },
            "canonical_index_page": {
                "document_id": "steward_canonical_surface",
                "rel": "steward_canonical_surface",
                "kind": "steward_canonical_surface",
                "title": "Steward Canonical Surface",
                "wiki_name": "Steward-Canonical-Surface",
                "entrypoint": False,
            },
        },
        "federation_surface": {
            "surface_role": "canonical_public_source_authority",
            "canonical_for_public_federation": True,
            "publication_model": "github_authority_feed_plus_projected_wiki",
            "public_channels": ["authority_feed_manifest", "canonical_surface", "public_summary_registry"],
            "operator_companion_surfaces": ["lotus_operator_plane", "authenticated_steward_bridge"],
            "consumer_guidance": "Treat this authority feed and its projected wiki pages as public federation truth; authenticated control planes are companion operator surfaces.",
        },
        "surface_registry": {
            "kind": "wiki_surface_registry",
            "version": 2,
            "generated_at": datetime.now(timezone.utc).timestamp(),
            "repo_web_url": repo_web_url,
            "sections": sections,
            "page_count": len(pages),
            "pages": pages,
            "system_metrics": {
                "document_count": len(documents),
                "repo_python_files": repo_python_files,
                "repo_markdown_files": repo_markdown_files,
                "node_manifest_count": node_manifest_count,
            },
            "projection": {
                "mode": "source_authority_export",
                "base_url": "",
                "root": "",
                "manifest": {},
                "public_graph": {},
                "repo_graph": {},
                "search_index": {},
            },
        },
    }


def export_authority_bundle(*, workspace: Path | str | None = None, source_sha: str = "") -> dict[str, Any]:
    root = Path(workspace or ".").resolve()
    generated_at = datetime.now(timezone.utc).timestamp()
    version = source_sha or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    artifacts_by_kind = {
        "canonical_surface": export_canonical_surface(workspace=root),
        "public_summary_registry": export_public_summary_registry(workspace=root),
        "source_surface_registry": export_source_surface_registry(workspace=root),
        "repo_graph": export_repo_graph_snapshot(workspace=root),
        "surface_metadata": export_authority_surface_metadata(workspace=root, source_sha=source_sha),
    }
    artifact_payloads = {
        AUTHORITY_EXPORT_ARTIFACTS[export_kind]: payload for export_kind, payload in artifacts_by_kind.items()
    }
    authority_exports = [
        {
            "export_id": f"{STEWARD_REPO_ID}/{export_kind}",
            "repo_id": STEWARD_REPO_ID,
            "export_kind": export_kind,
            "version": version,
            "artifact_uri": AUTHORITY_EXPORT_ARTIFACTS[export_kind],
            "generated_at": generated_at,
            "contract_version": AUTHORITY_EXPORT_CONTRACT_VERSION,
            "content_sha256": _artifact_sha256(payload),
            "labels": {"source_sha": source_sha} if source_sha else {},
        }
        for export_kind, payload in artifacts_by_kind.items()
    ]
    return {
        "kind": "source_authority_bundle",
        "contract_version": AUTHORITY_EXPORT_CONTRACT_VERSION,
        "generated_at": generated_at,
        "source_sha": source_sha,
        "repo_role": {
            "repo_id": STEWARD_REPO_ID,
            "role": "normative_source",
            "owner_boundary": "normative_protocol_surface",
            "exports": [record["export_kind"] for record in authority_exports],
            "consumes": [],
            "publication_targets": ["steward-public-wiki"],
            "labels": {"public_surface_owner": "agent-internet"},
        },
        "authority_exports": authority_exports,
        "artifact_paths": {export_kind: AUTHORITY_EXPORT_ARTIFACTS[export_kind] for export_kind in artifacts_by_kind},
        "artifacts": artifact_payloads,
    }
