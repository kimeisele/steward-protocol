"""
OPUS-054: SUTRA (The Thread) - Wiki Documentation Weaver.

Sanskrit: Sutra = Thread, String, Aphorism.
    "The sutras are threads that weave knowledge into wisdom."

SUTRA enables MANAS to write its own documentation to GitHub Wiki.
It extracts knowledge from AKASHA (the knowledge graph) and MANDALA
(the configuration), then weaves it into wiki pages.

Architecture:
    ┌───────────────────────────────────────────────────────────────┐
    │                    SUTRA (The Thread)                          │
    │                                                                │
    │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │
    │   │ SutraWeaver │──▶│ WikiPages   │──▶│ WikiSync    │        │
    │   │ (Generate)  │   │ (Templates) │   │ (Git Push)  │        │
    │   └─────────────┘   └─────────────┘   └─────────────┘        │
    │          │                                    │                │
    │          ▼                                    ▼                │
    │   ┌─────────────────────────────────────────────────────┐    │
    │   │  AKASHA (Knowledge) + MANDALA (Configuration)       │    │
    │   └─────────────────────────────────────────────────────┘    │
    └───────────────────────────────────────────────────────────────┘

Wiki Pages Generated:
    - manifest-declared canonical bindings, derived atlases, and navigation pages
    - federation registry and topology views derived from runtime/document sources

"The wiki is the visible thread - what MANAS thinks, the wiki reflects."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xb98e092c"  # GenesisByte: parampara % 37 == 0

import logging
import re
import yaml

# subprocess removed
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from vibe_core.protocols.system_shell import ShellProtocol, SystemShell, ShellResult

logger = logging.getLogger("MANAS.Cortex.Sutra")


# =============================================================================
# SECTION 1: DATA MODELS
# =============================================================================


class WikiPageType(Enum):
    """Types of wiki pages SUTRA can generate."""

    HOME = "Home"  # Main wiki page
    START_HERE = "Start-Here"  # Canonical README binding
    INDEX = "Index"  # Canonical documentation index binding
    CONSTITUTION = "Constitution"  # Canonical constitution binding
    LAW = "Constitution"  # Legacy alias for constitution preview/generation
    GOVERNANCE_INDEX = "Governance-Index"  # Governance navigation/index page
    GOVERNANCE_ATLAS = "Governance-Atlas"  # Deeper governance reference atlas
    AGI_MANIFESTO = "AGI-Manifesto"  # Canonical manifesto binding
    STEWARDSHIP = "Stewardship"  # Canonical steward protocol binding
    PROTOCOLS = "Protocols"  # Canonical protocol registry binding
    ARCHITECTURE = "Architecture"  # Canonical architecture binding
    KERNEL = "Kernel"  # Canonical kernel planning/battle document binding
    CANONICAL_ATLAS = "Canonical-Atlas"  # Canonical source registry atlas
    PROTOCOL_ATLAS = "Protocol-Atlas"  # Protocol and architecture reference atlas
    FEDERATION_REGISTRY = "Federation-Registry"  # Agent registry
    PANTHEON = "Federation-Registry"  # Legacy alias for federation registry preview/generation
    MAP = "Map"  # Architecture overview
    SIDEBAR = "_Sidebar"  # Navigation sidebar
    FOOTER = "_Footer"  # Common footer


@dataclass
class WikiPage:
    """A generated wiki page."""

    page_type: WikiPageType
    title: str
    content: str
    wiki_name: Optional[str] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_entities: List[str] = field(default_factory=list)

    @property
    def filename(self) -> str:
        """Get the filename for this page."""
        return f"{(self.wiki_name or self.page_type.value)}.md"


@dataclass(frozen=True)
class WikiSurfacePageSpec:
    """Manifest-backed page specification for the public wiki surface."""

    page_type: WikiPageType
    title: str
    wiki_name: str
    page_class: str
    authority: str
    domain: str
    section: str
    nav_label: str = ""
    description: str = ""
    public_summary: str = ""
    renderer: str = ""
    source_path: Optional[str] = None
    featured: bool = False
    include_in_sidebar: bool = True
    query_aliases: tuple[str, ...] = ()
    render_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WikiContext:
    """Context data for wiki generation."""

    # System info
    system_name: str = "STEWARD Protocol"
    version: str = "1.0.0"
    timestamp: str = ""

    # From MANDALA
    agents: List[Dict[str, Any]] = field(default_factory=list)
    capabilities: Dict[str, List[str]] = field(default_factory=dict)
    domains: Dict[str, List[str]] = field(default_factory=dict)

    # From AKASHA
    node_count: int = 0
    edge_count: int = 0
    constraint_count: int = 0
    knowledge_summary: str = ""

    # From Constitution
    constitution_articles: List[str] = field(default_factory=list)
    governance_rules: List[str] = field(default_factory=list)

    # Architecture
    modules: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[Dict[str, str]] = field(default_factory=list)
    repo_python_files: int = 0
    repo_markdown_files: int = 0
    node_manifest_count: int = 0
    repo_areas: List[Dict[str, Any]] = field(default_factory=list)
    cartridge_families: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SutraResult:
    """Result of wiki generation."""

    success: bool
    pages_generated: List[WikiPage] = field(default_factory=list)
    pages_synced: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    wiki_url: Optional[str] = None

    def to_chat_response(self) -> str:
        """Format for chat display."""
        if not self.success:
            return "❌ Wiki generation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)

        lines = [
            "📜 **SUTRA** - Wiki Generation Complete",
            "",
            f"**Pages Generated:** {len(self.pages_generated)}",
        ]

        for page in self.pages_generated:
            lines.append(f"  ✅ {page.filename} ({len(page.content)} chars)")

        if self.pages_synced:
            lines.append(f"\n**Synced to Wiki:** {len(self.pages_synced)} pages")
            if self.wiki_url:
                lines.append(f"  🔗 {self.wiki_url}")

        return "\n".join(lines)


# =============================================================================
# SECTION 2: WIKI TEMPLATES (Inline Jinja2-style)
# =============================================================================


# Templates are defined as Python format strings with Jinja2-like syntax
# This avoids external file dependencies while maintaining flexibility

WIKI_SURFACE_MANIFEST = Path("wiki-src/manifest.yaml")


TEMPLATE_HOME = """# {system_name}

> *Public documentation surface derived from repository sources and runtime discovery.*

## System Overview

| Metric | Value |
|--------|-------|
| **Version** | {version} |
| **Agents** | {agent_count} registered |
| **Knowledge Nodes** | {node_count} |
| **Last Updated** | {timestamp} |

## Quick Links

{quick_links}

## Status

{status_section}

---

*Generated by SUTRA from repository and runtime metadata*
"""

TEMPLATE_PANTHEON = """# {title}

> *{intro}*

## Registry Overview

**Total Agents:** {agent_count}
**Domains:** {domain_count}
**Capabilities:** {capability_count}

## Agents by Domain

{domain_sections}

## Capability Matrix

{capability_matrix}

---

*Generated by SUTRA from MANDALA configuration*
"""

TEMPLATE_GOVERNANCE_INDEX = """# {title}

> *The canonical constitution, governance neighbors, and enforcement sources.*

## Canonical Governance Pages

{canonical_pages}

## Constitutional Structure

{constitution_section}

## Governance Source Modules

{governance_section}

## Enforcement Posture

- **Change policy:** verification-backed changes only
- **Source basis:** constitutional headings plus governance modules
- **Assurance level:** conservative and test-first

---

*Derived by SUTRA from constitutional and governance sources*
"""

TEMPLATE_MAP = """# {title}

> *{intro}*

## Repository Snapshot

| Metric | Value |
|--------|-------|
| **Python files** | {repo_python_files} |
| **Markdown sources** | {repo_markdown_files} |
| **Agent manifests** | {node_manifest_count} |

## Knowledge Graph

| Dimension | Count |
|-----------|-------|
| **Nodes** (Ontology) | {node_count} |
| **Edges** (Topology) | {edge_count} |
| **Constraints** (Rules) | {constraint_count} |

## Major Subsystems

{subsystem_section}

## Runtime Surface

{runtime_section}

## Module Structure

{module_section}

## Relationship Summary

{dependency_section}

---

*Derived by SUTRA from repository structure, agent manifests, and graph metadata*
"""

TEMPLATE_ATLAS = """# {title}

> *{intro}*

## Published Surface Coverage

| Page | Class | Authority | Domain | Public Summary | Source |
|------|-------|-----------|--------|----------------|--------|
{surface_rows}

## Related Repository Sources

{source_section}

## Derivation Contract

- **Registry documents matched:** {surface_count}
- **Repository sources discovered:** {source_count}
- **Renderer:** `atlas`

---

*Derived by SUTRA from the document registry and repository source trees*
"""

TEMPLATE_SIDEBAR = """**{system_name}**

{navigation_sections}

---

*v{version}*
"""

TEMPLATE_FOOTER = """---
*Generated by [SUTRA](https://github.com/kimeisele/steward-protocol) | {timestamp}*
"""


def _humanize_symbol_name(value: str) -> str:
    """Convert snake/caps identifiers into a human-readable label."""
    return value.replace("_", " ").replace("-", " ").strip().title()


MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _parse_git_origin_url(workspace: Path) -> str:
    """Read the origin remote from .git/config and convert it to a web URL."""
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
        repo = origin_url.removeprefix("git@github.com:").removesuffix(".git")
        return f"https://github.com/{repo}"
    if origin_url.startswith("https://github.com/"):
        return origin_url.removesuffix(".git")
    return ""


def _normalize_bound_markdown(
    content: str,
    *,
    source_path: Optional[str] = None,
    workspace: Optional[Path] = None,
    source_page_specs: Optional[dict[str, "WikiSurfacePageSpec"]] = None,
    repo_web_url: str = "",
) -> str:
    """Apply minimal formatting fixes and rewrite repo-relative markdown links when possible."""
    normalized = content.replace("-->#", "-->\n#").replace("--><", "-->\n<")
    if source_path and workspace:
        source_file = (workspace / source_path).resolve()

        def _rewrite_link(match: re.Match[str]) -> str:
            label, target = match.groups()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                return match.group(0)
            relative_target, anchor = (target.split("#", 1) + [""])[:2]
            anchor_suffix = f"#{anchor}" if anchor else ""
            if not relative_target:
                return match.group(0)
            resolved = (source_file.parent / relative_target).resolve()
            basename = Path(relative_target).name
            try:
                rel_path = resolved.relative_to(workspace.resolve()).as_posix()
            except ValueError:
                return match.group(0)
            if source_page_specs and rel_path in source_page_specs:
                return f"[{label}]({source_page_specs[rel_path].wiki_name}{anchor_suffix})"
            if source_page_specs and basename:
                basename_matches = {
                    candidate_spec.wiki_name: candidate_spec
                    for candidate_path, candidate_spec in source_page_specs.items()
                    if Path(candidate_path).name == basename
                }
                if len(basename_matches) == 1:
                    matched_spec = next(iter(basename_matches.values()))
                    return f"[{label}]({matched_spec.wiki_name}{anchor_suffix})"
            if repo_web_url and resolved.exists():
                return f"[{label}]({repo_web_url}/blob/main/{rel_path}{anchor_suffix})"
            return match.group(0)

        normalized = MARKDOWN_LINK_RE.sub(_rewrite_link, normalized)
    return normalized.strip() + "\n"


def _extract_markdown_summary(path: Path) -> tuple[str, str]:
    """Extract a human title and first paragraph summary from markdown content."""
    if not path.exists():
        return "", ""
    heading = ""
    paragraph_lines: list[str] = []
    started_paragraph = False
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            if started_paragraph:
                break
            continue
        if line.startswith("#") and not heading:
            heading = line.lstrip("#").strip()
            continue
        if line.startswith((">", "*", "-", "|", "```")):
            continue
        paragraph_lines.append(line)
        started_paragraph = True
    return heading, " ".join(paragraph_lines).strip()


def _slugify_wiki_name(label: str) -> str:
    """Convert a label into a wiki-friendly page slug."""
    slug = re.sub(r"[^A-Za-z0-9]+", "-", label).strip("-")
    return slug or "Page"


def _build_surface_spec(workspace: Path, payload: dict[str, Any], *, defaults: Optional[dict[str, Any]] = None) -> WikiSurfacePageSpec:
    """Build a surface page spec from manifest or discovery payload."""
    merged = {**(defaults or {}), **payload}
    source_path = str(merged.get("source_path") or "") or None
    _source_title, source_summary = _extract_markdown_summary(workspace / source_path) if source_path else ("", "")
    title = str(merged.get("title") or _humanize_symbol_name(Path(source_path or merged["id"]).stem))
    wiki_name = str(merged.get("wiki_name") or _slugify_wiki_name(title))
    nav_label = str(merged.get("nav_label") or title)
    description = str(merged.get("description") or (source_summary if str(merged.get("page_class") or "derived") != "canonical" else ""))
    public_summary = str(merged.get("public_summary") or merged.get("summary") or description)
    aliases = [str(value).lower() for value in merged.get("query_aliases", [])]
    if source_path:
        aliases.append(Path(source_path).stem.lower().replace("_", " "))
    return WikiSurfacePageSpec(
        page_type=WikiPageType[str(merged["id"])],
        title=title,
        wiki_name=wiki_name,
        page_class=str(merged.get("page_class") or "derived"),
        authority=str(merged.get("authority") or "derived"),
        domain=str(merged.get("domain") or merged.get("section") or "reference"),
        section=str(merged.get("section") or "reference"),
        nav_label=nav_label,
        description=description,
        public_summary=public_summary,
        renderer=str(merged.get("renderer") or ""),
        source_path=source_path,
        featured=bool(merged.get("featured", False)),
        include_in_sidebar=bool(merged.get("include_in_sidebar", True)),
        query_aliases=tuple(dict.fromkeys(alias for alias in aliases if alias)),
        render_config=dict(merged.get("render_config") or {}),
    )


def _surface_public_summary(spec: WikiSurfacePageSpec, fallback: str = "") -> str:
    """Return the public-safe summary for a surface page."""
    return str(spec.public_summary or spec.description or fallback).strip()


def _match_discovery_rule(path: str, rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Find the first discovery rule matching a source path."""
    for rule in rules:
        if str(rule.get("match_path") or "") == path:
            return rule
        pattern = str(rule.get("match_regex") or "")
        if pattern and re.fullmatch(pattern, path):
            return rule
    return {}


def _load_surface_model(workspace: Path) -> tuple[list[dict[str, str]], list[WikiSurfacePageSpec]]:
    """Load the canonical wiki surface declaration from disk."""
    manifest_path = workspace / WIKI_SURFACE_MANIFEST
    if not manifest_path.exists():
        for parent in Path(__file__).resolve().parents:
            candidate = parent / WIKI_SURFACE_MANIFEST
            if candidate.exists():
                manifest_path = candidate
                break
    payload = yaml.safe_load(manifest_path.read_text()) or {}
    sections = list(payload.get("sections", []))
    specs: list[WikiSurfacePageSpec] = []
    if payload.get("canonical_discovery") or payload.get("derived_pages"):
        canonical_discovery = dict(payload.get("canonical_discovery") or {})
        discovery_defaults = dict(canonical_discovery.get("defaults") or {})
        discovery_rules = list(canonical_discovery.get("rules") or [])
        discovered_paths = list(dict.fromkeys(str(path) for path in canonical_discovery.get("include_paths", [])))
        for source_path in discovered_paths:
            rule = _match_discovery_rule(source_path, discovery_rules)
            if not rule:
                continue
            specs.append(_build_surface_spec(workspace, {**rule, "source_path": source_path}, defaults=discovery_defaults))
        for page_payload in payload.get("derived_pages", []):
            specs.append(_build_surface_spec(workspace, dict(page_payload)))
    else:
        for page_payload in payload.get("pages", []):
            specs.append(_build_surface_spec(workspace, dict(page_payload)))
    return sections, specs


def _extract_markdown_outline(path: Path) -> list[tuple[int, str]]:
    """Extract ordered markdown headings for index/report generation."""
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


def _format_surface_link(spec: WikiSurfacePageSpec) -> str:
    """Render a wiki link for a declared surface page."""
    label = spec.nav_label or spec.title
    if label == spec.wiki_name:
        return f"[[{spec.wiki_name}]]"
    return f"[[{spec.wiki_name}|{label}]]"


def _format_surface_markdown_link(spec: WikiSurfacePageSpec) -> str:
    """Render a standard markdown link for contexts where wiki links are poorly supported."""
    label = spec.nav_label or spec.title
    return f"[{label}]({spec.wiki_name})"


def _render_repo_source_reference(path: str, repo_web_url: str) -> str:
    """Render a repository source reference as a markdown link when possible."""
    if repo_web_url:
        return f"[`{path}`]({repo_web_url}/blob/main/{path})"
    return f"`{path}`"


def _match_registry_filters(spec: WikiSurfacePageSpec, filters: Dict[str, Any]) -> bool:
    """Determine whether a surface page matches atlas registry filters."""
    if spec.page_class == "navigation":
        return False
    include_page_classes = set(filters.get("include_page_classes", []))
    include_authorities = set(filters.get("include_authorities", []))
    include_domains = set(filters.get("include_domains", []))
    exclude_page_types = {WikiPageType[name] for name in filters.get("exclude_page_types", [])}
    if include_page_classes and spec.page_class not in include_page_classes:
        return False
    if include_authorities and spec.authority not in include_authorities:
        return False
    if include_domains and spec.domain not in include_domains:
        return False
    if exclude_page_types and spec.page_type in exclude_page_types:
        return False
    return True


def _discover_source_paths(workspace: Path, config: Dict[str, Any]) -> list[str]:
    """Discover source files for atlas/reference pages from configured roots and paths."""
    discovered: set[str] = set()
    suffixes = tuple(config.get("source_suffixes", [".md"]))
    for raw_path in config.get("source_paths", []):
        candidate = workspace / str(raw_path)
        if candidate.exists() and candidate.is_file() and candidate.suffix in suffixes:
            discovered.add(candidate.relative_to(workspace).as_posix())
    for raw_root in config.get("source_roots", []):
        root = workspace / str(raw_root)
        if not root.exists():
            continue
        for candidate in root.rglob("*"):
            if candidate.is_file() and candidate.suffix in suffixes:
                discovered.add(candidate.relative_to(workspace).as_posix())
    for raw_path in config.get("exclude_source_paths", []):
        discovered.discard(str(raw_path))
    return sorted(discovered)


# =============================================================================
# SECTION 3: SUTRA WEAVER - Wiki Generator
# =============================================================================


class SutraWeaver:
    """
    Weaves wiki pages from knowledge sources.

    "The weaver takes the threads of knowledge and creates the tapestry of documentation."
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize the weaver.

        Args:
            workspace: Workspace path for knowledge loading
        """
        self._workspace = workspace or Path.cwd()
        surface_sections, surface_specs = _load_surface_model(self._workspace)
        self._surface_sections = surface_sections
        self._surface_spec_list = surface_specs
        self._surface_specs = {spec.page_type: spec for spec in surface_specs}
        self._source_specs = {str(spec.source_path): spec for spec in surface_specs if spec.source_path}
        self._repo_web_url = _parse_git_origin_url(self._workspace)

    def gather_context(self) -> WikiContext:
        """
        Gather context from AKASHA and MANDALA.

        Returns:
            WikiContext with all gathered data
        """
        ctx = WikiContext(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )

        # Gather from MANDALA
        self._gather_mandala_context(ctx)

        # Gather from AKASHA
        self._gather_akasha_context(ctx)

        # Gather from Constitution
        self._gather_constitution_context(ctx)

        # Gather module structure
        self._gather_module_context(ctx)

        return ctx

    def _gather_mandala_context(self, ctx: WikiContext) -> None:
        """Gather agent and capability info from MANDALA."""
        try:
            from .mandala import ConfigWeaver

            weaver = ConfigWeaver(workspace=self._workspace)
            weaver.weave()
            cartridges_root = self._workspace / "vibe_core" / "cartridges"
            runtime_families: Counter[str] = Counter()

            # Extract agents
            for agent_id, manifest in weaver.manifests.items():
                agent_info = {
                    "id": agent_id,
                    "name": manifest.name,
                    "domain": manifest.domain,
                    "version": manifest.version,
                    "capabilities": list(manifest.capabilities.keys()),
                    "tier": manifest.tier,
                }
                ctx.agents.append(agent_info)

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

                # Group by domain
                if manifest.domain not in ctx.domains:
                    ctx.domains[manifest.domain] = []
                ctx.domains[manifest.domain].append(agent_id)

                # Group capabilities by agent
                ctx.capabilities[agent_id] = list(manifest.capabilities.keys())

            ctx.node_manifest_count = len(weaver.manifests)
            ctx.cartridge_families = [{"name": name, "agents": count} for name, count in runtime_families.most_common(10)]

            logger.debug(f"SUTRA: Gathered {len(ctx.agents)} agents from MANDALA")

        except Exception as e:
            logger.warning(f"SUTRA: Could not gather MANDALA context: {e}")

    def _gather_akasha_context(self, ctx: WikiContext) -> None:
        """Gather knowledge graph info from AKASHA."""
        try:
            from .akasha import AkashaPort, AkashaQuery

            port = AkashaPort(self._workspace)
            ctx.node_count = port.get_node_count()
            ctx.edge_count = port.get_edge_count()

            if port.graph:
                ctx.constraint_count = len(port.graph.constraints)

            query = AkashaQuery(port)
            summary = query.graph_summary()
            ctx.knowledge_summary = summary.raw_context

            logger.debug(f"SUTRA: Gathered {ctx.node_count} nodes from AKASHA")

        except Exception as e:
            logger.warning(f"SUTRA: Could not gather AKASHA context: {e}")

    def _gather_constitution_context(self, ctx: WikiContext) -> None:
        """Gather governance info from constitution files."""
        try:
            constitution_path = self._workspace / "CONSTITUTION.md"
            for _level, heading in _extract_markdown_outline(constitution_path):
                ctx.constitution_articles.append(heading)

            # Governance rules from config
            governance_path = self._workspace / "vibe_core" / "governance"
            if governance_path.exists():
                for rule_file in governance_path.glob("*.py"):
                    if rule_file.name == "__init__.py":
                        continue
                    ctx.governance_rules.append(rule_file.stem)

            logger.debug(f"SUTRA: Gathered {len(ctx.constitution_articles)} articles")

        except Exception as e:
            logger.warning(f"SUTRA: Could not gather constitution context: {e}")

    def _gather_module_context(self, ctx: WikiContext) -> None:
        """Gather module structure from vibe_core."""
        try:
            vibe_core = self._workspace / "vibe_core"
            if vibe_core.exists():
                repo_areas: Counter[str] = Counter()
                for module_dir in vibe_core.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith("_"):
                        py_files = list(module_dir.glob("**/*.py"))
                        if py_files:
                            repo_areas[module_dir.name] = len(py_files)
                            ctx.modules.append(
                                {
                                    "name": module_dir.name,
                                    "files": len(py_files),
                                    "path": str(module_dir.relative_to(self._workspace)),
                                }
                            )

                ctx.repo_python_files = len(list(vibe_core.rglob("*.py")))
                ctx.repo_markdown_files = len(list(self._workspace.rglob("*.md")))
                ctx.repo_areas = [
                    {"name": name, "python_files": count}
                    for name, count in repo_areas.most_common(10)
                ]

            logger.debug(f"SUTRA: Gathered {len(ctx.modules)} modules")

        except Exception as e:
            logger.warning(f"SUTRA: Could not gather module context: {e}")

    def weave_page(self, page_type: WikiPageType, ctx: WikiContext) -> WikiPage:
        """
        Weave a single wiki page.

        Args:
            page_type: Type of page to generate
            ctx: Context data for generation

        Returns:
            WikiPage with generated content
        """
        spec = self._surface_specs.get(page_type)
        if spec is None:
            raise ValueError(f"Unknown page type: {page_type}")

        if spec.renderer == "home":
            return self._weave_home(ctx, spec)
        if spec.renderer == "pantheon":
            return self._weave_pantheon(ctx, spec)
        if spec.renderer == "governance_index":
            return self._weave_governance_index(spec)
        if spec.renderer == "atlas":
            return self._weave_atlas(spec)
        if spec.renderer == "map":
            return self._weave_map(ctx, spec)
        if spec.renderer == "sidebar":
            return self._weave_sidebar(ctx, spec)
        if spec.renderer == "footer":
            return self._weave_footer(ctx, spec)
        if spec.renderer == "canonical_doc":
            return self._weave_canonical_page(spec)

        raise ValueError(f"Unknown page renderer: {spec.renderer}")

    def _ordered_surface_specs(self) -> list[WikiSurfacePageSpec]:
        """Return all page specs in manifest order."""
        return list(self._surface_spec_list)

    def _iter_query_aliases(self, spec: WikiSurfacePageSpec) -> list[str]:
        """Return normalized query aliases for dynamic preview matching."""
        aliases = {
            spec.wiki_name.lower(),
            spec.title.lower(),
            (spec.nav_label or spec.title).lower(),
            spec.page_type.name.lower().replace("_", " "),
            spec.page_type.value.lower().replace("-", " "),
            *spec.query_aliases,
        }
        return sorted({alias.strip() for alias in aliases if alias and len(alias.strip()) >= 3}, key=len, reverse=True)

    def resolve_page_type(self, query: str) -> WikiPageType:
        """Resolve a preview query against the declared registry rather than hardcoded branches."""
        normalized_query = query.lower()
        best_match: Optional[WikiSurfacePageSpec] = None
        best_length = 0
        for spec in self._ordered_surface_specs():
            if spec.page_class == "navigation":
                continue
            for alias in self._iter_query_aliases(spec):
                if alias in normalized_query and len(alias) > best_length:
                    best_match = spec
                    best_length = len(alias)
        return best_match.page_type if best_match else WikiPageType.HOME

    def _build_home_quick_links(self) -> str:
        """Render the featured home-page links from the surface manifest."""
        lines: list[str] = []
        for spec in self._ordered_surface_specs():
            if not spec.featured or spec.page_type == WikiPageType.HOME:
                continue
            public_summary = _surface_public_summary(spec)
            summary_suffix = f" - {public_summary}" if public_summary else ""
            lines.append(f"- {_format_surface_link(spec)}{summary_suffix}")
        return "\n".join(lines) or "- [[Start-Here|Start Here]]"

    def _build_sidebar_navigation(self) -> str:
        """Render grouped sidebar navigation from the surface manifest."""
        lines: list[str] = []
        for section in self._surface_sections:
            section_id = str(section.get("id") or "")
            section_title = str(section.get("title") or section_id)
            section_pages = [spec for spec in self._ordered_surface_specs() if spec.include_in_sidebar and spec.section == section_id]
            if not section_pages:
                continue
            lines.append(f"### {section_title}")
            for spec in section_pages:
                lines.append(f"- {_format_surface_link(spec)}")
            lines.append("")
        return "\n".join(lines).strip()

    def _weave_home(self, ctx: WikiContext, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate Home wiki page."""
        # Status section
        status_lines = []
        if ctx.agents:
            status_lines.append(f"✅ **{len(ctx.agents)} agents** registered in MANDALA")
        if ctx.node_count:
            status_lines.append(f"✅ **{ctx.node_count} knowledge nodes** in AKASHA")
        canonical_specs = [page_spec for page_spec in self._ordered_surface_specs() if page_spec.page_class == "canonical"]
        if canonical_specs:
            status_lines.append(f"✅ **{len(canonical_specs)} canonical documents** bound into the public surface")
        atlas_specs = [page_spec for page_spec in self._ordered_surface_specs() if page_spec.renderer == "atlas"]
        if atlas_specs:
            status_lines.append(f"✅ **{len(atlas_specs)} automated atlas pages** deriving structure from the registry")
        if not status_lines:
            status_lines.append("⚪ System initializing...")

        status_section = "\n".join(status_lines)

        content = TEMPLATE_HOME.format(
            system_name=ctx.system_name,
            version=ctx.version,
            agent_count=len(ctx.agents),
            node_count=ctx.node_count,
            timestamp=ctx.timestamp,
            quick_links=self._build_home_quick_links(),
            status_section=status_section,
        )

        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
            source_entities=["system", "mandala", "akasha"],
        )

    def _weave_pantheon(self, ctx: WikiContext, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate the federation registry page from MANDALA agent metadata."""
        # Domain sections
        domain_sections = []
        for domain, agents in sorted(ctx.domains.items()):
            section = f"### {domain}\n\n"
            for agent_id in sorted(agents):
                agent = next((a for a in ctx.agents if a["id"] == agent_id), None)
                if agent:
                    caps = ", ".join(agent.get("capabilities", [])[:3])
                    if len(agent.get("capabilities", [])) > 3:
                        caps += "..."
                    section += f"- **{agent['name']}** (`{agent_id}`) - {caps}\n"
            domain_sections.append(section)

        # Capability matrix
        all_caps: Set[str] = set()
        for caps in ctx.capabilities.values():
            all_caps.update(caps)

        cap_matrix_lines = ["| Agent | Capabilities |", "|-------|--------------|"]
        for agent_id, caps in sorted(ctx.capabilities.items()):
            cap_str = ", ".join(sorted(caps)[:5])
            if len(caps) > 5:
                cap_str += f" (+{len(caps) - 5})"
            cap_matrix_lines.append(f"| `{agent_id}` | {cap_str} |")

        content = TEMPLATE_PANTHEON.format(
            title=spec.title,
            intro=_surface_public_summary(spec, "The declared federation registry derived from MANDALA."),
            agent_count=len(ctx.agents),
            domain_count=len(ctx.domains),
            capability_count=len(all_caps),
            domain_sections="\n".join(domain_sections),
            capability_matrix="\n".join(cap_matrix_lines),
        )

        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
            source_entities=[a["id"] for a in ctx.agents],
        )

    def _weave_canonical_page(self, spec: WikiSurfacePageSpec) -> WikiPage:
        """Bind a canonical authored markdown document directly into the wiki surface."""
        source_path = self._workspace / str(spec.source_path or "")
        public_summary = _surface_public_summary(spec)
        canonical_intro_lines: list[str] = []
        if public_summary:
            canonical_intro_lines.append(f"> **Public abstract:** {public_summary}")
        if spec.source_path:
            canonical_intro_lines.append(
                f"> **Bound source:** {_render_repo_source_reference(str(spec.source_path), self._repo_web_url)}"
            )
        canonical_intro = "\n".join(canonical_intro_lines).strip()
        if source_path.exists():
            content = _normalize_bound_markdown(
                source_path.read_text(),
                source_path=str(spec.source_path or ""),
                workspace=self._workspace,
                source_page_specs=self._source_specs,
                repo_web_url=self._repo_web_url,
            )
        else:
            content = f"# {spec.title}\n\n_Source document not found: `{spec.source_path}`_\n"
        if canonical_intro:
            content = canonical_intro + "\n\n" + content.lstrip()
        content = (
            content.rstrip()
            + "\n\n---\n\n"
            + f"*Surface class: `{spec.page_class}` | Authority: `{spec.authority}` | Domain: `{spec.domain}` | Source: `{spec.source_path}`*\n"
        )
        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
            source_entities=[str(spec.source_path or spec.wiki_name)],
        )

    def _weave_governance_index(self, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate a derived governance index without flattening the constitution itself."""
        constitution_path = self._workspace / "CONSTITUTION.md"
        outline = _extract_markdown_outline(constitution_path)
        if outline:
            constitution_lines = []
            for level, heading in outline:
                indent = "  " if level >= 3 else ""
                constitution_lines.append(f"{indent}- **{heading}**")
            constitution_section = "\n".join(constitution_lines)
        else:
            constitution_section = "_Constitution outline not available_"

        governance_dir = self._workspace / "vibe_core" / "governance"
        governance_sources: list[str] = []
        governance_source_paths: list[str] = []
        if governance_dir.exists():
            for path in sorted(governance_dir.iterdir()):
                if not path.is_file() or path.name == "__init__.py" or path.suffix not in {".py", ".md"}:
                    continue
                label = _humanize_symbol_name(path.stem)
                rel_path = path.relative_to(self._workspace).as_posix()
                governance_source_paths.append(rel_path)
                governance_sources.append(f"- **{label}** — {_render_repo_source_reference(rel_path, self._repo_web_url)}")
        governance_section = "\n".join(governance_sources) or "_Governance sources not loaded_"

        governance_surface_pages = [
            page_spec for page_spec in self._ordered_surface_specs() if page_spec.domain == "governance" and page_spec.page_type != spec.page_type
        ]
        canonical_links = [
            f"- {_format_surface_link(page_spec)} - {_surface_public_summary(page_spec)}"
            for page_spec in governance_surface_pages
        ]
        content = TEMPLATE_GOVERNANCE_INDEX.format(
            title=spec.title,
            canonical_pages="\n".join(canonical_links),
            constitution_section=constitution_section,
            governance_section=governance_section,
        )
        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
            source_entities=["CONSTITUTION.md"] + governance_source_paths,
        )

    def _weave_atlas(self, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate a derived atlas/reference page from registry metadata and configured repo roots."""
        config = dict(spec.render_config)
        matching_specs = [page_spec for page_spec in self._ordered_surface_specs() if _match_registry_filters(page_spec, config)]
        if matching_specs:
            surface_rows = "\n".join(
                f"| {_format_surface_markdown_link(page_spec)} | `{page_spec.page_class}` | `{page_spec.authority}` | `{page_spec.domain}` | {_surface_public_summary(page_spec) or '-'} | `{page_spec.source_path or page_spec.renderer}` |"
                for page_spec in matching_specs
            )
        else:
            surface_rows = "| _None_ | - | - | - | - | - |"

        discovered_sources = _discover_source_paths(self._workspace, config)
        bound_source_paths = {str(page_spec.source_path) for page_spec in matching_specs if page_spec.source_path}
        source_lines = []
        for path in discovered_sources:
            if path in bound_source_paths and config.get("exclude_bound_sources", True):
                continue
            source_lines.append(f"- **{_humanize_symbol_name(Path(path).stem)}** — {_render_repo_source_reference(path, self._repo_web_url)}")
        source_section = "\n".join(source_lines) or "_No additional repository sources matched this atlas._"

        content = TEMPLATE_ATLAS.format(
            title=spec.title,
            intro=str(config.get("intro") or _surface_public_summary(spec, "Registry-derived reference atlas.")),
            surface_rows=surface_rows,
            source_section=source_section,
            surface_count=len(matching_specs),
            source_count=len(source_lines),
        )
        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
            source_entities=[page_spec.wiki_name for page_spec in matching_specs] + discovered_sources,
        )

    def _weave_map(self, ctx: WikiContext, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate a data-driven system map page."""
        # Module section
        if ctx.modules:
            module_lines = ["| Module | Files | Path |", "|--------|-------|------|"]
            for mod in sorted(ctx.modules, key=lambda m: m["name"]):
                module_lines.append(f"| `{mod['name']}` | {mod['files']} | `{mod['path']}` |")
            module_section = "\n".join(module_lines)
        else:
            module_section = "_Module structure not loaded_"

        if ctx.repo_areas:
            subsystem_lines = ["| Area | Python Files |", "|------|--------------|"]
            for area in ctx.repo_areas:
                subsystem_lines.append(f"| `{area['name']}` | {area['python_files']} |")
            subsystem_section = "\n".join(subsystem_lines)
        else:
            subsystem_section = "_Repository subsystem inventory not loaded_"

        if ctx.cartridge_families:
            runtime_lines = ["| Runtime Family | Agent Manifests |", "|----------------|------------------|"]
            for family in ctx.cartridge_families:
                runtime_lines.append(f"| `{family['name']}` | {family['agents']} |")
            runtime_section = "\n".join(runtime_lines)
        else:
            runtime_section = "_Runtime manifest inventory not loaded_"

        # Dependency section
        dependency_section = ctx.knowledge_summary or "_Dependency graph not loaded_"

        content = TEMPLATE_MAP.format(
            title=spec.title,
            intro=_surface_public_summary(spec, "System topology derived from repository structure, manifests, and graph metadata."),
            node_count=ctx.node_count,
            edge_count=ctx.edge_count,
            constraint_count=ctx.constraint_count,
            repo_python_files=ctx.repo_python_files,
            repo_markdown_files=ctx.repo_markdown_files,
            node_manifest_count=ctx.node_manifest_count,
            subsystem_section=subsystem_section,
            runtime_section=runtime_section,
            module_section=module_section,
            dependency_section=dependency_section,
        )

        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
            source_entities=[m["name"] for m in ctx.modules],
        )

    def _weave_sidebar(self, ctx: WikiContext, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate wiki sidebar."""
        content = TEMPLATE_SIDEBAR.format(
            system_name=ctx.system_name,
            navigation_sections=self._build_sidebar_navigation(),
            version=ctx.version,
        )

        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
        )

    def _weave_footer(self, ctx: WikiContext, spec: WikiSurfacePageSpec) -> WikiPage:
        """Generate wiki footer."""
        content = TEMPLATE_FOOTER.format(timestamp=ctx.timestamp)

        return WikiPage(
            page_type=spec.page_type,
            title=spec.title,
            wiki_name=spec.wiki_name,
            content=content,
        )

    def weave_all(self, ctx: Optional[WikiContext] = None) -> List[WikiPage]:
        """
        Weave all wiki pages.

        Returns:
            List of all generated WikiPage objects
        """
        ctx = ctx or self.gather_context()
        pages = []

        for spec in self._ordered_surface_specs():
            try:
                page = self.weave_page(spec.page_type, ctx)
                pages.append(page)
                logger.info(f"SUTRA: Wove {page.filename}")
            except Exception as e:
                logger.error(f"SUTRA: Failed to weave {spec.wiki_name}: {e}")

        return pages


# =============================================================================
# SECTION 4: WIKI SYNC - Git Operations
# =============================================================================


class WikiSync:
    """
    Synchronizes generated wiki pages to GitHub Wiki.

    GitHub wikis are separate git repos: <repo>.wiki.git
    This class handles clone, write, commit, push.

    OPUS-071: Now supports GITHUB_TOKEN authentication!

    "The sync is the bridge between thought and manifestation."
    """

    def __init__(self, workspace: Optional[Path] = None, shell_executor: Optional[ShellProtocol] = None):
        """
        Initialize wiki sync.

        Args:
            workspace: Workspace path (for detecting repo URL)
            shell_executor: Optional shell executor (for testing)
        """
        import os

        self._workspace = workspace or Path.cwd()
        self._wiki_dir: Optional[Path] = None
        # OPUS-071: Load GitHub token for authentication
        self._github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.shell = shell_executor or SystemShell()

    def _get_authenticated_url(self, url: str) -> str:
        """
        Transform URL to include authentication token.

        OPUS-071: Enables wiki push without manual git credential setup.

        Args:
            url: Original git URL

        Returns:
            URL with embedded token (if available) or original URL
        """
        if not self._github_token:
            logger.warning("SUTRA WikiSync: No GITHUB_TOKEN set - push may fail")
            return url

        # Transform git@github.com:user/repo.wiki.git -> https://token@github.com/user/repo.wiki.git
        if url.startswith("git@github.com:"):
            repo_path = url.replace("git@github.com:", "")
            return f"https://{self._github_token}@github.com/{repo_path}"

        # Transform https://github.com/user/repo.wiki.git -> https://token@github.com/user/repo.wiki.git
        if url.startswith("https://github.com/"):
            return url.replace("https://github.com/", f"https://{self._github_token}@github.com/")

        return url

    def has_credentials(self) -> bool:
        """Check if GitHub credentials are available."""
        return self._github_token is not None

    def get_wiki_url(self) -> Optional[str]:
        """
        Get the wiki repo URL from the main repo.

        Returns:
            Wiki git URL or None
        """
        try:
            result = self.shell.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self._workspace,
                check=True,
            )
            origin = result.stdout.strip()

            # Transform: github.com/user/repo.git -> github.com/user/repo.wiki.git
            if origin.endswith(".git"):
                return origin[:-4] + ".wiki.git"
            else:
                return origin + ".wiki.git"

        except Exception as e:
            logger.warning(f"SUTRA WikiSync: Could not get wiki URL: {e}")
            return None

    def clone_wiki(self, temp_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Clone the wiki repository.

        OPUS-071: Uses authenticated URL when GITHUB_TOKEN is available.

        Args:
            temp_dir: Optional temp directory (created if None)

        Returns:
            Path to cloned wiki or None on failure
        """
        wiki_url = self.get_wiki_url()
        if not wiki_url:
            return None

        # OPUS-071: Use authenticated URL for clone
        auth_url = self._get_authenticated_url(wiki_url)

        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp(prefix="sutra_wiki_"))

        try:
            self.shell.run(
                ["git", "clone", auth_url, str(temp_dir)],
                check=True,
            )
            self._wiki_dir = temp_dir
            logger.info(f"SUTRA WikiSync: Cloned wiki to {temp_dir}")
            return temp_dir

        except SystemError as e:
            # Wiki might not exist yet - initialize it
            err_msg = str(e).lower()
            if "not found" in err_msg or "empty repository" in err_msg:
                logger.info("SUTRA WikiSync: Wiki repo does not exist, will initialize")
                self._wiki_dir = temp_dir
                self.shell.run(["git", "init"], cwd=temp_dir, check=True)
                # Set remote for push
                if auth_url:
                    self.shell.run(
                        ["git", "remote", "add", "origin", auth_url],
                        cwd=temp_dir,
                        check=False,  # May fail if remote exists
                    )
                return temp_dir
            logger.error(f"SUTRA WikiSync: Clone failed: {e}")
            return None

    def write_pages(self, pages: List[WikiPage], wiki_dir: Optional[Path] = None) -> int:
        """
        Write wiki pages to the wiki directory.

        Args:
            pages: List of WikiPage objects
            wiki_dir: Wiki directory (uses self._wiki_dir if None)

        Returns:
            Number of pages written
        """
        target_dir = wiki_dir or self._wiki_dir
        if not target_dir:
            logger.error("SUTRA WikiSync: No wiki directory available")
            return 0

        written = 0
        for page in pages:
            try:
                page_path = target_dir / page.filename
                page_path.write_text(page.content)
                written += 1
                logger.debug(f"SUTRA WikiSync: Wrote {page.filename}")
            except Exception as e:
                logger.error(f"SUTRA WikiSync: Failed to write {page.filename}: {e}")

        return written

    def commit_and_push(self, message: str = "SUTRA: Update wiki documentation") -> bool:
        """
        Commit and push wiki changes.

        OPUS-071: Uses authenticated push with GITHUB_TOKEN.

        Args:
            message: Commit message

        Returns:
            True if successful
        """
        if not self._wiki_dir:
            logger.error("SUTRA WikiSync: No wiki directory available")
            return False

        try:
            # Configure git user for this repo (SUTRA is the author)
            self.shell.run(
                ["git", "config", "user.email", "sutra@manas.steward"],
                cwd=self._wiki_dir,
                check=False,
            )
            self.shell.run(
                ["git", "config", "user.name", "SUTRA (MANAS Cortex)"],
                cwd=self._wiki_dir,
                check=False,
            )

            # Add all changes
            self.shell.run(["git", "add", "-A"], cwd=self._wiki_dir, check=True)

            # Check if there are changes
            result = self.shell.run(
                ["git", "status", "--porcelain"],
                cwd=self._wiki_dir,
            )

            if not result.stdout.strip():
                logger.info("SUTRA WikiSync: No changes to commit")
                return True

            # Commit
            self.shell.run(["git", "commit", "-m", message], cwd=self._wiki_dir, check=True)

            # Push with authenticated URL
            wiki_url = self.get_wiki_url()
            if wiki_url:
                auth_url = self._get_authenticated_url(wiki_url)
                # Set push URL with auth
                self.shell.run(
                    ["git", "remote", "set-url", "origin", auth_url],
                    cwd=self._wiki_dir,
                    check=False,
                )
                self.shell.run(
                    ["git", "push", "-u", "origin", "master"],
                    cwd=self._wiki_dir,
                    check=True,
                )
                logger.info("📜 SUTRA WikiSync: Pushed wiki changes to GitHub!")

            return True

        except SystemError as e:
            logger.error(f"SUTRA WikiSync: Git operation failed: {e}")
            return False

    def sync(self, pages: List[WikiPage]) -> SutraResult:
        """
        Full sync: clone, write, commit, push.

        Args:
            pages: Wiki pages to sync

        Returns:
            SutraResult with sync status
        """
        result = SutraResult(success=False, pages_generated=pages)

        # Clone wiki
        wiki_dir = self.clone_wiki()
        if not wiki_dir:
            result.errors.append("Failed to clone wiki repository")
            return result

        # Write pages
        written = self.write_pages(pages, wiki_dir)
        if written == 0:
            result.errors.append("Failed to write any pages")
            return result

        result.pages_synced = [p.filename for p in pages[:written]]

        # Commit and push
        if self.commit_and_push():
            result.success = True
            wiki_url = self.get_wiki_url()
            if wiki_url:
                # Transform wiki git URL to web URL
                result.wiki_url = wiki_url.replace(".wiki.git", "/wiki").replace(
                    "git@github.com:", "https://github.com/"
                )
        else:
            result.errors.append("Failed to commit/push changes")

        return result


# =============================================================================
# SECTION 5: SUTRA ORCHESTRATOR - Main Entry Point
# =============================================================================


class SutraOrchestrator:
    """
    Orchestrates the full wiki generation and sync workflow.

    "The orchestrator conducts the symphony of threads."
    """

    def __init__(self, workspace: Optional[Path] = None, shell_executor: Optional[ShellProtocol] = None):
        """
        Initialize orchestrator.

        Args:
            workspace: Workspace path
            shell_executor: Optional shell executor
        """
        self._workspace = workspace or Path.cwd()
        self._weaver = SutraWeaver(workspace=self._workspace)
        self._sync = WikiSync(workspace=self._workspace, shell_executor=shell_executor)
        self._cached_context: Optional[WikiContext] = None

    def _get_context(self) -> WikiContext:
        """Cache gathered context for repeated preview/generation calls."""
        if self._cached_context is None:
            self._cached_context = self._weaver.gather_context()
        return self._cached_context

    def resolve_page_type(self, query: str) -> WikiPageType:
        """Resolve a query string to a declared surface page."""
        return self._weaver.resolve_page_type(query)

    def declared_surface_specs(self) -> list[WikiSurfacePageSpec]:
        """Expose the declared public surface for chat/status helpers."""
        return self._weaver._ordered_surface_specs()

    def export_surface_metadata(self) -> dict[str, Any]:
        """Export machine-readable surface metadata for federation consumers."""
        ctx = self._get_context()
        surface_specs = self.declared_surface_specs()
        non_navigation_specs = [spec for spec in surface_specs if spec.page_class != "navigation"]
        return {
            "kind": "wiki_surface_registry",
            "version": 1,
            "generated_at": ctx.timestamp,
            "repo_web_url": self._weaver._repo_web_url,
            "sections": self._weaver._surface_sections,
            "page_count": len(non_navigation_specs),
            "pages": [
                {
                    "id": spec.page_type.name,
                    "title": spec.title,
                    "wiki_name": spec.wiki_name,
                    "filename": f"{spec.wiki_name}.md",
                    "page_class": spec.page_class,
                    "authority": spec.authority,
                    "domain": spec.domain,
                    "section": spec.section,
                    "description": spec.description,
                    "public_summary": spec.public_summary,
                    "renderer": spec.renderer,
                    "source_path": spec.source_path,
                    "featured": spec.featured,
                    "include_in_sidebar": spec.include_in_sidebar,
                    "query_aliases": list(spec.query_aliases),
                }
                for spec in surface_specs
            ],
            "system_metrics": {
                "agent_count": len(ctx.agents),
                "domain_count": len(ctx.domains),
                "capability_count": sum(len(capabilities) for capabilities in ctx.capabilities.values()),
                "node_count": ctx.node_count,
                "edge_count": ctx.edge_count,
                "constraint_count": ctx.constraint_count,
                "module_count": len(ctx.modules),
                "repo_python_files": ctx.repo_python_files,
                "repo_markdown_files": ctx.repo_markdown_files,
                "node_manifest_count": ctx.node_manifest_count,
                "repo_areas": ctx.repo_areas,
                "cartridge_families": ctx.cartridge_families,
            },
        }

    def generate(self, page_types: Optional[List[WikiPageType]] = None) -> List[WikiPage]:
        """
        Generate wiki pages without syncing.

        Args:
            page_types: Specific pages to generate (all if None)

        Returns:
            List of generated pages
        """
        ctx = self._get_context()
        if page_types is None:
            return self._weaver.weave_all(ctx)

        return [self._weaver.weave_page(pt, ctx) for pt in page_types]

    def generate_and_sync(self, page_types: Optional[List[WikiPageType]] = None) -> SutraResult:
        """
        Generate and sync wiki pages.

        Args:
            page_types: Specific pages to generate (all if None)

        Returns:
            SutraResult with full status
        """
        pages = self.generate(page_types)

        if not pages:
            return SutraResult(success=False, errors=["No pages generated"])

        return self._sync.sync(pages)

    def preview(self, page_type: WikiPageType = WikiPageType.HOME) -> str:
        """
        Preview a wiki page without syncing.

        Args:
            page_type: Type of page to preview

        Returns:
            Generated markdown content
        """
        ctx = self._get_context()
        page = self._weaver.weave_page(page_type, ctx)
        return page.content


# =============================================================================
# SECTION 6: JNANA INTEGRATION - Chat Interface
# =============================================================================


def handle_sutra_query(content: str, workspace: Optional[Path] = None) -> str:
    """
    Handle wiki-related queries from JNANA chat.

    Args:
        content: User's query content
        workspace: Optional workspace path

    Returns:
        Response string
    """
    content_lower = content.lower()
    orchestrator = SutraOrchestrator(workspace=workspace)

    # Preview a specific page
    if any(word in content_lower for word in ["preview", "show", "display"]):
        page_type = orchestrator.resolve_page_type(content)

        content_preview = orchestrator.preview(page_type)
        # Truncate for chat
        if len(content_preview) > 1500:
            content_preview = content_preview[:1500] + "\n\n... (truncated)"

        return f"📜 **Wiki Preview: {page_type.value}**\n\n{content_preview}"

    # Generate (dry run)
    if any(word in content_lower for word in ["generate", "create", "build"]):
        pages = orchestrator.generate()
        lines = ["📜 **SUTRA** - Wiki Generation (Dry Run)", ""]
        for page in pages:
            lines.append(f"  ✅ {page.filename} ({len(page.content)} chars)")
        lines.append("\n_Use 'update wiki' or 'sync wiki' to push to GitHub_")
        return "\n".join(lines)

    # Full sync
    if any(word in content_lower for word in ["update", "sync", "push", "deploy"]):
        result = orchestrator.generate_and_sync()
        return result.to_chat_response()

    # Status/info
    return get_sutra_for_chat(workspace)


def get_sutra_for_chat(workspace: Optional[Path] = None) -> str:
    """
    Get SUTRA status for chat display.

    Args:
        workspace: Optional workspace path

    Returns:
        Status string
    """
    orchestrator = SutraOrchestrator(workspace=workspace)
    ctx = orchestrator._get_context()
    surface_specs = orchestrator.declared_surface_specs()

    wiki_url = orchestrator._sync.get_wiki_url()
    wiki_url_display = (
        wiki_url.replace(".wiki.git", "/wiki").replace("git@github.com:", "https://github.com/")
        if wiki_url
        else "Not configured"
    )

    preview_commands = [
        f'- "preview {((spec.query_aliases[0] if spec.query_aliases else spec.nav_label or spec.title).lower())}" - {_surface_public_summary(spec)}'
        for spec in surface_specs
        if spec.featured and spec.page_class != "navigation"
    ]
    page_lines = [
        f"- {spec.wiki_name}.md - {_surface_public_summary(spec, spec.title)}"
        for spec in surface_specs
        if spec.page_class != "navigation"
    ]

    return f"""📜 **SUTRA** (Wiki Documentation)
├─ Wiki URL: {wiki_url_display}
├─ Agents: {len(ctx.agents)}
├─ Knowledge Nodes: {ctx.node_count}
├─ Modules: {len(ctx.modules)}
└─ Declared Pages: {len([spec for spec in surface_specs if spec.page_class != 'navigation'])}

**Commands:**
- "preview wiki" - Show Home page preview
- "preview constitution" - Show canonical constitution page
- "generate wiki" - Dry run (no push)
- "update wiki" - Generate and push to GitHub
{chr(10).join(preview_commands)}

**Pages Generated:**
{chr(10).join(page_lines)}
"""


# =============================================================================
# SECTION 7: SINGLETON ACCESS
# =============================================================================


_sutra_orchestrator: Optional[SutraOrchestrator] = None


def get_sutra_orchestrator(workspace: Optional[Path] = None) -> SutraOrchestrator:
    """Get or create the global SUTRA orchestrator."""
    global _sutra_orchestrator
    if _sutra_orchestrator is None:
        _sutra_orchestrator = SutraOrchestrator(workspace)
    return _sutra_orchestrator
