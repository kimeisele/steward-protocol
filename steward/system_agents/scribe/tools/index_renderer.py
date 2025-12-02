#!/usr/bin/env python3
"""
SCRIBE Index Renderer - VEDA-4 Circuit Documentation Index

VEDA-4 COGNITIVE FLOW:
  SHABDA   → Entry points (where to start)
  ARTHA    → Understanding (learn the system)
  PRATYAYA → Planning (architecture & guides)
  KARMA    → Execution (operations & agents)
  SYNTH    → Results (dashboards & reports)

Tool Protocol Compliant (Kernel-Managed).
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from .base import Tool, ToolResult, get_kernel_status, load_template

logger = logging.getLogger("SCRIBE_INDEX")


class IndexRenderer(Tool):
    """Generate INDEX.md using VEDA-4 Circuit Structure.

    Maps documentation to cognitive flow phases:
    - SHABDA: Entry points for new users
    - ARTHA: Understanding the system
    - PRATYAYA: Planning and architecture
    - KARMA: Execution and operations
    - SYNTH: Results and dashboards
    """

    # VEDA-4 SECTION MAPPING
    # Each phase maps to specific docs for cognitive flow

    SHABDA_DOCS: List[str] = [
        "README.md",
        "HELP.md",
    ]

    ARTHA_DOCS: List[str] = [
        "CONSTITUTION.md",
        "STEWARD.md",
        "CITYMAP.md",
        "AGI_MANIFESTO.md",
    ]

    KARMA_DOCS: List[str] = [
        "OPERATIONS.md",
        "SETTINGS.md",
        "AGENTS.md",
    ]

    SYNTH_DOCS: List[str] = [
        "DASHBOARD.md",
        "PROOF.md",
        "INDEX.md",
    ]

    # docs/ subdirectories mapped to VEDA-4 phases
    PRATYAYA_DIRS: Set[str] = {"architecture", "guides"}
    KARMA_DIRS: Set[str] = {"deployment", "security"}
    SYNTH_DIRS: Set[str] = {"reports"}
    ARTHA_DIRS: Set[str] = {"governance", "philosophy"}

    # All allowed docs/ subdirectories
    DOCS_ALLOWLIST: Set[str] = {
        "architecture",
        "deployment",
        "governance",
        "guides",
        "philosophy",
        "reports",
        "security",
    }

    def __init__(self, root_dir: str = "."):
        """Initialize VEDA-4 Index Renderer."""
        self.root_dir = Path(root_dir)
        self.doc_categories: Dict[str, List[Path]] = {}

    @property
    def name(self) -> str:
        return "scribe.index_renderer"

    @property
    def description(self) -> str:
        return "Generate INDEX.md using VEDA-4 Circuit cognitive flow"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render INDEX.md",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if parameters["action"] not in ["generate"]:
            raise ValueError(f"Invalid action: {parameters['action']}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute VEDA-4 Circuit Index generation."""
        logger.info("🔬 VEDA-4 Circuit: Generating INDEX.md...")

        try:
            # SHABDA: Capture request
            logger.info("🔊 SHABDA: Capturing generation request...")
            action = parameters["action"]

            if action == "generate":
                # ARTHA: Understand filesystem
                logger.info("📖 ARTHA: Scanning documentation...")
                self._scan_docs_directories()

                # PRATYAYA: Plan structure
                logger.info("🧠 PRATYAYA: Planning VEDA-4 structure...")

                # KARMA: Execute rendering
                logger.info("⚡ KARMA: Rendering sections...")
                content = self._render_veda4_index()

                # SYNTH: Synthesize result
                logger.info("🔬 SYNTH: Index complete!")
                return ToolResult(success=True, output=content)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"❌ VEDA-4 Circuit failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _scan_docs_directories(self):
        """Scan docs/ subdirectories."""
        docs_dir = self.root_dir / "docs"
        if not docs_dir.exists():
            return

        for subdir in docs_dir.iterdir():
            if not subdir.is_dir():
                continue
            if subdir.name not in self.DOCS_ALLOWLIST:
                continue

            md_files = list(subdir.glob("**/*.md"))
            md_files = [f for f in md_files if "/archive/" not in str(f)]
            if md_files:
                self.doc_categories[subdir.name] = sorted(md_files)

    def _render_veda4_index(self) -> str:
        """Render INDEX.md with VEDA-4 cognitive structure."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        kernel_status = get_kernel_status(str(self.root_dir))

        template = load_template("index.jinja2")
        content = template.render(
            timestamp=timestamp,
            generator="SCRIBE",
            kernel_status=kernel_status,
            shabda_content=self._render_shabda(),
            artha_content=self._render_artha(),
            pratyaya_content=self._render_pratyaya(),
            karma_content=self._render_karma(),
            synth_content=self._render_synth(),
        )

        return content

    def _render_shabda(self) -> str:
        """SHABDA: Entry points - where to start."""
        output = ""
        for doc_name in self.SHABDA_DOCS:
            doc_path = self.root_dir / doc_name
            if doc_path.exists():
                desc = self._get_description(doc_name)
                output += f"- **[{doc_name}]({doc_name})** — {desc}\n"
        return output

    def _render_artha(self) -> str:
        """ARTHA: Understanding - learn the system."""
        output = ""

        # Root docs
        for doc_name in self.ARTHA_DOCS:
            doc_path = self.root_dir / doc_name
            if doc_path.exists():
                desc = self._get_description(doc_name)
                output += f"- **[{doc_name}]({doc_name})** — {desc}\n"

        # docs/ directories (governance, philosophy)
        for dir_name in sorted(self.ARTHA_DIRS):
            files = self.doc_categories.get(dir_name, [])
            if files:
                output += f"\n**{dir_name.title()}:**\n"
                for doc_path in files[:5]:  # Limit to 5
                    rel_path = doc_path.relative_to(self.root_dir)
                    desc = self._get_description(doc_path.name)
                    output += f"- [{rel_path}]({rel_path}) — {desc}\n"

        return output

    def _render_pratyaya(self) -> str:
        """PRATYAYA: Planning - architecture & guides."""
        output = ""

        for dir_name in ["architecture", "guides"]:
            files = self.doc_categories.get(dir_name, [])
            if files:
                title = "Architecture" if dir_name == "architecture" else "Guides"
                output += f"**{title}:**\n"
                for doc_path in files[:10]:  # Limit to 10
                    rel_path = doc_path.relative_to(self.root_dir)
                    desc = self._get_description(doc_path.name)
                    output += f"- [{rel_path}]({rel_path}) — {desc}\n"
                output += "\n"

        return output

    def _render_karma(self) -> str:
        """KARMA: Execution - operations & agents."""
        output = ""

        # Root docs
        for doc_name in self.KARMA_DOCS:
            doc_path = self.root_dir / doc_name
            if doc_path.exists():
                desc = self._get_description(doc_name)
                output += f"- **[{doc_name}]({doc_name})** — {desc}\n"

        # docs/ directories (deployment, security)
        for dir_name in sorted(self.KARMA_DIRS):
            files = self.doc_categories.get(dir_name, [])
            if files:
                output += f"\n**{dir_name.title()}:**\n"
                for doc_path in files[:5]:
                    rel_path = doc_path.relative_to(self.root_dir)
                    desc = self._get_description(doc_path.name)
                    output += f"- [{rel_path}]({rel_path}) — {desc}\n"

        return output

    def _render_synth(self) -> str:
        """SYNTH: Results - dashboards & reports."""
        output = ""

        # Root docs
        for doc_name in self.SYNTH_DOCS:
            doc_path = self.root_dir / doc_name
            if doc_path.exists():
                desc = self._get_description(doc_name)
                output += f"- **[{doc_name}]({doc_name})** — {desc}\n"

        # docs/reports
        files = self.doc_categories.get("reports", [])
        if files:
            output += "\n**Reports:**\n"
            for doc_path in files[:8]:
                rel_path = doc_path.relative_to(self.root_dir)
                desc = self._get_description(doc_path.name)
                output += f"- [{rel_path}]({rel_path}) — {desc}\n"

        return output

    def _get_description(self, filename: str) -> str:
        """Get description for a document."""
        descriptions = {
            # SHABDA
            "README.md": "Quick start guide",
            "HELP.md": "Operations & commands",
            # ARTHA
            "CONSTITUTION.md": "Constitutional governance",
            "STEWARD.md": "Protocol specification",
            "CITYMAP.md": "System architecture",
            "AGI_MANIFESTO.md": "Governed Intelligence philosophy",
            # KARMA
            "OPERATIONS.md": "System operations",
            "SETTINGS.md": "Configuration options",
            "AGENTS.md": "Agent registry & tools",
            # SYNTH
            "DASHBOARD.md": "Live status dashboard",
            "PROOF.md": "Verification proof",
            "INDEX.md": "Navigation index (this file)",
            # Known docs
            "DEPLOYMENT.md": "Deployment guide",
            "ARCHITECTURE.md": "Architecture overview",
        }
        return descriptions.get(filename, filename.replace(".md", "").replace("_", " "))

    # Standalone mode
    def scan_and_render(self) -> str:
        """Standalone method for generate_docs.py."""
        self._scan_docs_directories()
        return self._render_veda4_index()

    def _scan_and_render(self) -> str:
        """Internal render with scan."""
        self._scan_docs_directories()
        return self._render_veda4_index()
