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
    - Home.md: System overview, status, quick links
    - Pantheon.md: Agent registry (from MANDALA)
    - Law.md: Constitution and governance rules
    - Map.md: Architecture overview (from AKASHA)

"The wiki is the visible thread - what MANAS thinks, the wiki reflects."
"""

import logging
# subprocess removed
import tempfile
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
    PANTHEON = "Pantheon"  # Agent registry
    LAW = "Law"  # Constitution and governance
    MAP = "Map"  # Architecture overview
    SIDEBAR = "_Sidebar"  # Navigation sidebar
    FOOTER = "_Footer"  # Common footer


@dataclass
class WikiPage:
    """A generated wiki page."""

    page_type: WikiPageType
    title: str
    content: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_entities: List[str] = field(default_factory=list)

    @property
    def filename(self) -> str:
        """Get the filename for this page."""
        return f"{self.page_type.value}.md"


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

TEMPLATE_HOME = """# {system_name}

> *The wiki is the visible thread - what MANAS thinks, the wiki reflects.*

## System Overview

| Metric | Value |
|--------|-------|
| **Version** | {version} |
| **Agents** | {agent_count} registered |
| **Knowledge Nodes** | {node_count} |
| **Last Updated** | {timestamp} |

## Quick Links

- [[Pantheon]] - Agent Registry (Who lives in the City)
- [[Law]] - Constitution & Governance Rules
- [[Map]] - Architecture Overview

## Status

{status_section}

---

*Generated by SUTRA (The Thread) - OPUS-054*
"""

TEMPLATE_PANTHEON = """# Pantheon - Agent Registry

> *The gods of the city, each with their sacred duty.*

## Agent Overview

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

TEMPLATE_LAW = """# Law - Constitution & Governance

> *The sacred rules that bind the city.*

## Constitutional Articles

{constitution_section}

## Governance Rules

{governance_section}

## Enforcement

- **Guardian:** NARASIMHA (The Protector)
- **Protocol:** Platinum (No changes without tests)
- **Audit Level:** Paranoid

---

*Generated by SUTRA from governance configuration*
"""

TEMPLATE_MAP = """# Map - Architecture Overview

> *The topology of the cosmic city.*

## Knowledge Graph

| Dimension | Count |
|-----------|-------|
| **Nodes** (Ontology) | {node_count} |
| **Edges** (Topology) | {edge_count} |
| **Constraints** (Rules) | {constraint_count} |

## Module Structure

{module_section}

## Dependency Flow

{dependency_section}

## MANAS Cortex

The cognitive processing pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    MANAS (The Mind)                          │
│                                                              │
│   VEDA (Intent)    │    DHARMA (Context)   │   JNANA (Chat) │
│   SHABDA → ARTHA   │    Profile + Memory   │   Handlers     │
│   → KRIYA → PHALA  │                       │                │
│                                                              │
│   Supported by: AKASHA (Knowledge) + MANDALA (Config)       │
│                 SILPA (Refactor) + SUTRA (Wiki)             │
└─────────────────────────────────────────────────────────────┘
```

---

*Generated by SUTRA from AKASHA knowledge graph*
"""

TEMPLATE_SIDEBAR = """**{system_name}**

- [[Home]]
- [[Pantheon|Agents]]
- [[Law|Constitution]]
- [[Map|Architecture]]

---

*v{version}*
"""

TEMPLATE_FOOTER = """---
*Generated by [SUTRA](https://github.com/kimeisele/steward-protocol) | {timestamp}*
"""


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

                # Group by domain
                if manifest.domain not in ctx.domains:
                    ctx.domains[manifest.domain] = []
                ctx.domains[manifest.domain].append(agent_id)

                # Group capabilities by agent
                ctx.capabilities[agent_id] = list(manifest.capabilities.keys())

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
            if constitution_path.exists():
                content = constitution_path.read_text()
                # Extract articles (simple parsing)
                for line in content.split("\n"):
                    if line.startswith("##"):
                        ctx.constitution_articles.append(line.replace("##", "").strip())

            # Governance rules from config
            governance_path = self._workspace / "vibe_core" / "governance"
            if governance_path.exists():
                for rule_file in governance_path.glob("*.py"):
                    ctx.governance_rules.append(rule_file.stem)

            logger.debug(f"SUTRA: Gathered {len(ctx.constitution_articles)} articles")

        except Exception as e:
            logger.warning(f"SUTRA: Could not gather constitution context: {e}")

    def _gather_module_context(self, ctx: WikiContext) -> None:
        """Gather module structure from vibe_core."""
        try:
            vibe_core = self._workspace / "vibe_core"
            if vibe_core.exists():
                for module_dir in vibe_core.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith("_"):
                        py_files = list(module_dir.glob("**/*.py"))
                        if py_files:
                            ctx.modules.append(
                                {
                                    "name": module_dir.name,
                                    "files": len(py_files),
                                    "path": str(module_dir.relative_to(self._workspace)),
                                }
                            )

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
        if page_type == WikiPageType.HOME:
            return self._weave_home(ctx)
        elif page_type == WikiPageType.PANTHEON:
            return self._weave_pantheon(ctx)
        elif page_type == WikiPageType.LAW:
            return self._weave_law(ctx)
        elif page_type == WikiPageType.MAP:
            return self._weave_map(ctx)
        elif page_type == WikiPageType.SIDEBAR:
            return self._weave_sidebar(ctx)
        elif page_type == WikiPageType.FOOTER:
            return self._weave_footer(ctx)
        else:
            raise ValueError(f"Unknown page type: {page_type}")

    def _weave_home(self, ctx: WikiContext) -> WikiPage:
        """Generate Home wiki page."""
        # Status section
        status_lines = []
        if ctx.agents:
            status_lines.append(f"✅ **{len(ctx.agents)} agents** registered in MANDALA")
        if ctx.node_count:
            status_lines.append(f"✅ **{ctx.node_count} knowledge nodes** in AKASHA")
        if not status_lines:
            status_lines.append("⚪ System initializing...")

        status_section = "\n".join(status_lines)

        content = TEMPLATE_HOME.format(
            system_name=ctx.system_name,
            version=ctx.version,
            agent_count=len(ctx.agents),
            node_count=ctx.node_count,
            timestamp=ctx.timestamp,
            status_section=status_section,
        )

        return WikiPage(
            page_type=WikiPageType.HOME,
            title="Home",
            content=content,
            source_entities=["system", "mandala", "akasha"],
        )

    def _weave_pantheon(self, ctx: WikiContext) -> WikiPage:
        """Generate Pantheon (agent registry) wiki page."""
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
            agent_count=len(ctx.agents),
            domain_count=len(ctx.domains),
            capability_count=len(all_caps),
            domain_sections="\n".join(domain_sections),
            capability_matrix="\n".join(cap_matrix_lines),
        )

        return WikiPage(
            page_type=WikiPageType.PANTHEON,
            title="Pantheon - Agent Registry",
            content=content,
            source_entities=[a["id"] for a in ctx.agents],
        )

    def _weave_law(self, ctx: WikiContext) -> WikiPage:
        """Generate Law (constitution) wiki page."""
        # Constitution section
        if ctx.constitution_articles:
            const_lines = []
            for i, article in enumerate(ctx.constitution_articles, 1):
                const_lines.append(f"{i}. **{article}**")
            constitution_section = "\n".join(const_lines)
        else:
            constitution_section = "_Constitution not loaded_"

        # Governance section
        if ctx.governance_rules:
            gov_lines = []
            for rule in ctx.governance_rules:
                gov_lines.append(f"- `{rule}`")
            governance_section = "\n".join(gov_lines)
        else:
            governance_section = "_Governance rules not loaded_"

        content = TEMPLATE_LAW.format(
            constitution_section=constitution_section,
            governance_section=governance_section,
        )

        return WikiPage(
            page_type=WikiPageType.LAW,
            title="Law - Constitution & Governance",
            content=content,
            source_entities=["constitution"] + ctx.governance_rules,
        )

    def _weave_map(self, ctx: WikiContext) -> WikiPage:
        """Generate Map (architecture) wiki page."""
        # Module section
        if ctx.modules:
            module_lines = ["| Module | Files | Path |", "|--------|-------|------|"]
            for mod in sorted(ctx.modules, key=lambda m: m["name"]):
                module_lines.append(f"| `{mod['name']}` | {mod['files']} | `{mod['path']}` |")
            module_section = "\n".join(module_lines)
        else:
            module_section = "_Module structure not loaded_"

        # Dependency section
        dependency_section = ctx.knowledge_summary or "_Dependency graph not loaded_"

        content = TEMPLATE_MAP.format(
            node_count=ctx.node_count,
            edge_count=ctx.edge_count,
            constraint_count=ctx.constraint_count,
            module_section=module_section,
            dependency_section=dependency_section,
        )

        return WikiPage(
            page_type=WikiPageType.MAP,
            title="Map - Architecture Overview",
            content=content,
            source_entities=[m["name"] for m in ctx.modules],
        )

    def _weave_sidebar(self, ctx: WikiContext) -> WikiPage:
        """Generate wiki sidebar."""
        content = TEMPLATE_SIDEBAR.format(
            system_name=ctx.system_name,
            version=ctx.version,
        )

        return WikiPage(
            page_type=WikiPageType.SIDEBAR,
            title="Sidebar",
            content=content,
        )

    def _weave_footer(self, ctx: WikiContext) -> WikiPage:
        """Generate wiki footer."""
        content = TEMPLATE_FOOTER.format(timestamp=ctx.timestamp)

        return WikiPage(
            page_type=WikiPageType.FOOTER,
            title="Footer",
            content=content,
        )

    def weave_all(self) -> List[WikiPage]:
        """
        Weave all wiki pages.

        Returns:
            List of all generated WikiPage objects
        """
        ctx = self.gather_context()
        pages = []

        for page_type in WikiPageType:
            try:
                page = self.weave_page(page_type, ctx)
                pages.append(page)
                logger.info(f"SUTRA: Wove {page.filename}")
            except Exception as e:
                logger.error(f"SUTRA: Failed to weave {page_type.value}: {e}")

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

    def generate(self, page_types: Optional[List[WikiPageType]] = None) -> List[WikiPage]:
        """
        Generate wiki pages without syncing.

        Args:
            page_types: Specific pages to generate (all if None)

        Returns:
            List of generated pages
        """
        if page_types is None:
            return self._weaver.weave_all()

        ctx = self._weaver.gather_context()
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
        ctx = self._weaver.gather_context()
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
        if "pantheon" in content_lower or "agent" in content_lower:
            page_type = WikiPageType.PANTHEON
        elif "law" in content_lower or "constitution" in content_lower:
            page_type = WikiPageType.LAW
        elif "map" in content_lower or "architecture" in content_lower:
            page_type = WikiPageType.MAP
        else:
            page_type = WikiPageType.HOME

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
    ctx = orchestrator._weaver.gather_context()

    wiki_url = orchestrator._sync.get_wiki_url()
    wiki_url_display = (
        wiki_url.replace(".wiki.git", "/wiki").replace("git@github.com:", "https://github.com/")
        if wiki_url
        else "Not configured"
    )

    return f"""📜 **SUTRA** (Wiki Documentation)
├─ Wiki URL: {wiki_url_display}
├─ Agents: {len(ctx.agents)}
├─ Knowledge Nodes: {ctx.node_count}
└─ Modules: {len(ctx.modules)}

**Commands:**
- "preview wiki" - Show Home page preview
- "preview pantheon" - Show agent registry preview
- "generate wiki" - Dry run (no push)
- "update wiki" - Generate and push to GitHub

**Pages Generated:**
- Home.md - System overview
- Pantheon.md - Agent registry
- Law.md - Constitution & governance
- Map.md - Architecture overview
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
