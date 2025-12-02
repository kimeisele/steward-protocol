#!/usr/bin/env python3
"""
SCRIBE Index Renderer - SCHEMA-DRIVEN Documentation Index

WHITELIST APPROACH: Only explicitly allowed files/dirs are indexed.
- Root: Whitelist of allowed .md files
- Docs: Schema of allowed subdirectories only
- NO garbage: archive/, prompts/, temp/ ignored by default

Tool Protocol Compliant (Kernel-Managed).
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

# Import from shared base (eliminates DRY violation)
from .base import Tool, ToolResult, get_kernel_status, load_template


class IndexRenderer(Tool):
    """Generate INDEX.md using SCHEMA-DRIVEN indexing (Whitelist approach).

    Only explicitly allowed files/directories are indexed.
    Garbage (archive/, prompts/, temp files) is ignored.
    """

    # SCHEMA: Allowed root .md files (WHITELIST)
    ROOT_ALLOWLIST: Set[str] = {
        # Auto-generated
        "README.md",
        "AGENTS.md",
        "CITYMAP.md",
        "DASHBOARD.md",
        "HELP.md",
        "INDEX.md",
        "SETTINGS.md",
        # Governance
        "CONSTITUTION.md",
        "STEWARD.md",
        "AGI_MANIFESTO.md",
        # Operational
        "OPERATIONS.md",
        "PROOF.md",
    }

    # SCHEMA: Allowed docs/ subdirectories (WHITELIST)
    DOCS_ALLOWLIST: Set[str] = {
        "architecture",
        "deployment",
        "governance",
        "guides",
        "philosophy",
        "reports",
        "security",
    }

    # Category display titles
    CATEGORY_TITLES: Dict[str, str] = {
        "architecture": "## 🏗️ Architecture Documentation",
        "deployment": "## 🚀 Deployment & Operations",
        "governance": "## ⚖️ Governance",
        "guides": "## 📖 Guides & References",
        "philosophy": "## 💭 Philosophy & Context",
        "reports": "## 📊 Status Reports",
        "security": "## 🔒 Security",
    }

    def __init__(self, root_dir: str = "."):
        """Initialize renderer.

        Args:
            root_dir: Project root directory (for standalone mode)
        """
        self.root_dir = Path(root_dir)

        # Discovered files (populated by scanning)
        self.root_docs: List[Path] = []
        self.doc_categories: Dict[str, List[Path]] = {}

    @property
    def name(self) -> str:
        return "scribe.index_renderer"

    @property
    def description(self) -> str:
        return "Generate INDEX.md from filesystem introspection"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render INDEX.md content",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate renderer parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if parameters["action"] not in ["generate"]:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be 'generate'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute renderer operation."""
        try:
            action = parameters["action"]
            if action == "generate":
                content = self._scan_and_render()
                return ToolResult(success=True, output=content)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _scan_filesystem(self):
        """Scan filesystem using WHITELIST approach - only allowed files/dirs."""
        # Scan root directory - WHITELIST only + GAD-* pattern
        for md_file in self.root_dir.glob("*.md"):
            if not md_file.is_file():
                continue

            # Allow GAD-* pattern (Governance & Design docs)
            if md_file.name.startswith("GAD-"):
                self.root_docs.append(md_file)
                continue

            # Check whitelist
            if md_file.name in self.ROOT_ALLOWLIST:
                self.root_docs.append(md_file)

        # Scan docs/ subdirectories - WHITELIST only, with RECURSIVE support
        docs_dir = self.root_dir / "docs"
        if docs_dir.exists():
            for subdir in docs_dir.iterdir():
                if not subdir.is_dir():
                    continue

                # Only scan whitelisted directories
                if subdir.name not in self.DOCS_ALLOWLIST:
                    continue

                # Recursive glob to find .md files in subdirectories (e.g., GAD-0XX/)
                md_files = list(subdir.glob("**/*.md"))
                # Exclude archive/ subdirectory
                md_files = [f for f in md_files if "/archive/" not in str(f)]
                if md_files:
                    self.doc_categories[subdir.name] = sorted(md_files)

    def _render_root_docs(self) -> str:
        """Render root .md files as links."""
        if not self.root_docs:
            return "No markdown files found in root directory."

        # Categorize root docs
        auto_gen = ["README.md", "AGENTS.md", "CITYMAP.md", "DASHBOARD.md", "HELP.md", "INDEX.md"]
        governance = ["CONSTITUTION.md", "STEWARD.md"]
        philosophy = ["AGI_MANIFESTO.md"]
        gad_docs = []
        other = []

        for doc in sorted(self.root_docs):
            name = doc.name
            if name in auto_gen:
                continue  # Handle separately
            elif name in governance:
                continue  # Handle separately
            elif name in philosophy:
                continue  # Handle separately
            elif name.startswith("GAD-"):
                gad_docs.append(doc)
            else:
                other.append(doc)

        output = ""

        # Auto-generated docs
        output += "### Auto-Generated Documentation\n"
        for doc_name in auto_gen:
            doc_path = self.root_dir / doc_name
            if doc_path.exists():
                desc = self._get_doc_description(doc_name)
                output += f"- **[{doc_name}]({doc_name})** — {desc}\n"
        output += "\n"

        # Governance docs
        governance_found = [self.root_dir / d for d in governance if (self.root_dir / d).exists()]
        if governance_found:
            output += "### Constitutional Governance\n"
            for doc in governance_found:
                desc = self._get_doc_description(doc.name)
                output += f"- **[{doc.name}]({doc.name})** — {desc}\n"
            output += "\n"

        # Philosophy docs
        philosophy_found = [self.root_dir / d for d in philosophy if (self.root_dir / d).exists()]
        if philosophy_found:
            output += "### Philosophy & Manifestos\n"
            for doc in philosophy_found:
                desc = self._get_doc_description(doc.name)
                output += f"- **[{doc.name}]({doc.name})** — {desc}\n"
            output += "\n"

        # GAD docs
        if gad_docs:
            output += "### GAD (Governance & Design) Framework\n"
            for doc in sorted(gad_docs):
                desc = self._get_doc_description(doc.name)
                output += f"- **[{doc.name}]({doc.name})** — {desc}\n"
            output += "\n"

        # Other docs
        if other:
            output += "### Other Documentation\n"
            for doc in sorted(other):
                output += f"- **[{doc.name}]({doc.name})**\n"
            output += "\n"

        return output

    def _render_docs_categories(self) -> str:
        """Render docs/ subdirectories using category titles."""
        if not self.doc_categories:
            return ""

        output = ""

        # Render in schema order
        for category, title in self.CATEGORY_TITLES.items():
            files = self.doc_categories.get(category, [])
            if not files:
                continue

            output += f"{title}\n\n"

            for doc_path in files:
                rel_path = doc_path.relative_to(self.root_dir)
                desc = self._get_doc_description(doc_path.name)
                output += f"- **[{rel_path}]({rel_path})** — {desc}\n"

            output += "\n"

        return output

    def _get_doc_description(self, filename: str) -> str:
        """Get description for a document (minimal hardcoding, only for well-known files)."""
        descriptions = {
            # Auto-generated
            "README.md": "Project overview and quick start",
            "AGENTS.md": "Complete agent registry (auto-generated)",
            "CITYMAP.md": "3-layer system architecture (auto-generated)",
            "DASHBOARD.md": "Operational dashboard (auto-generated)",
            "HELP.md": "Operations control center (auto-generated)",
            "INDEX.md": "Documentation index (this file)",
            # Governance
            "CONSTITUTION.md": "Constitutional rules and governance",
            "STEWARD.md": "STEWARD Protocol specification",
            # Philosophy
            "AGI_MANIFESTO.md": "Governed Intelligence manifesto",
            # Known architecture docs
            "ARCHITECTURE.md": "System architecture overview",
            "UNIVERSE_MIGRATION_PLAN.md": "System migration master plan",
            # Known deployment docs
            "DEPLOYMENT.md": "Deployment guide",
            # Default
        }
        return descriptions.get(filename, filename.replace(".md", "").replace("_", " "))

    def _scan_and_render(self) -> str:
        """Scan filesystem and generate INDEX.md using external template."""
        self._scan_filesystem()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        # Get kernel status for unified header
        kernel_status = get_kernel_status(str(self.root_dir))

        # Pre-render sections for template
        template = load_template("index.jinja2")
        content = template.render(
            # Unified header variables
            timestamp=timestamp,
            generator="SCRIBE",
            kernel_status=kernel_status,
            # Index-specific variables
            root_docs_content=self._render_root_docs(),
            docs_categories_content=self._render_docs_categories(),
        )

        return content

    # Standalone mode method name (for generate_docs.py)
    def scan_and_render(self) -> str:
        """Standalone method to scan and generate INDEX.md.

        Same as _scan_and_render() but public for standalone mode.
        """
        return self._scan_and_render()
