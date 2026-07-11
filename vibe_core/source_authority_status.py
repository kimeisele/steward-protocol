from __future__ import annotations

from pathlib import Path

from vibe_core.authority_exports import export_authority_bundle
from vibe_core.source_authority_registry import load_source_authority_registry


def handle_source_authority_query(content: str, workspace: Path | None = None) -> str:
    root = workspace or Path.cwd()
    content_lower = content.lower()
    registry = load_source_authority_registry(workspace=root)
    bundle = export_authority_bundle(workspace=root)
    export_lines = [
        f"- `{record['export_kind']}` → `{record['artifact_uri']}`" for record in bundle["authority_exports"]
    ]

    if any(word in content_lower for word in ["authority", "bundle", "registry", "summary", "canonical", "export"]):
        return (
            "📜 **Source Authority Export**\n\n"
            f"Repo: `{registry.repo_id}`\n"
            f"Document count: {bundle['artifacts']['.authority-exports/source-surface-registry.json']['document_count']}\n\n"
            "**Available exports**\n"
            f"{chr(10).join(export_lines)}"
        )

    if any(
        word in content_lower
        for word in [
            "preview",
            "show",
            "display",
            "generate",
            "create",
            "build",
            "update",
            "sync",
            "push",
            "deploy",
            "publish",
        ]
    ):
        return (
            "📜 **Source Authority Export** no longer publishes local wiki pages.\n\n"
            "Public membrane rendering and publication belong to `agent-internet`.\n"
            "Use the neutral authority export path here only for the authority bundle, source surface registry, public summary registry, and canonical surface."
        )

    return get_source_authority_for_chat(workspace)


def get_source_authority_for_chat(workspace: Path | None = None) -> str:
    root = workspace or Path.cwd()
    registry = load_source_authority_registry(workspace=root)
    bundle = export_authority_bundle(workspace=root)
    export_kinds = [record["export_kind"] for record in bundle["authority_exports"]]

    return f"""📜 **Source Authority Export**
├─ Repo: {registry.repo_id}
├─ Documents: {len(registry.documents)}
└─ Export Kinds: {", ".join(export_kinds)}

**Commands:**
- "show authority bundle" - Describe exported authority artifacts
- "show source registry" - Review canonical source-document coverage
- "sync wiki" - explains that publication moved to agent-internet

**Boundary:**
- The authority export path is neutral and no longer runs through the legacy local wiki compiler.
- Public membrane rendering and publication belong to `agent-internet`.
"""
