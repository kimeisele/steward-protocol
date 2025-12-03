#!/usr/bin/env python3
"""
SCRIBE Index Renderer - Circuit-Driven Documentation Index

SCHEMA-DRIVEN (NOT HARDCODED):
  All mappings loaded from: vibe_core/playbook/circuits/doc_index_render.yaml

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
from typing import Any

import yaml

from .base import Tool, ToolResult, get_kernel_status, load_template

logger = logging.getLogger("SCRIBE_INDEX")

# Circuit YAML path (relative to project root)
CIRCUIT_PATH = "vibe_core/playbook/circuits/doc_index_render.yaml"


class IndexRenderer(Tool):
    """Generate INDEX.md using Circuit-Driven VEDA-4 Structure.

    All document mappings loaded from circuit YAML - NO HARDCODING.
    Schema-driven configuration for maintainability.
    """

    def __init__(self, root_dir: str = "."):
        """Initialize Circuit-Driven Index Renderer."""
        self.root_dir = Path(root_dir)
        self.doc_categories: dict[str, list[Path]] = {}

        # Load circuit schema
        self.circuit = self._load_circuit()
        self.doc_schema = self.circuit.get("doc_schema", {})
        self.doc_descriptions = self.circuit.get("doc_descriptions", {})
        self.docs_allowlist = set(self.circuit.get("docs_allowlist", []))

    def _load_circuit(self) -> dict[str, Any]:
        """Load circuit definition from YAML."""
        circuit_file = self.root_dir / CIRCUIT_PATH
        if not circuit_file.exists():
            logger.warning(f"Circuit file not found: {circuit_file}")
            return {"circuit": {}}

        with open(circuit_file) as f:
            data = yaml.safe_load(f)

        circuit = data.get("circuit", {})
        logger.info(f"📜 Loaded circuit: {circuit.get('id', 'UNKNOWN')}")
        return circuit

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
        circuit_id = self.circuit.get("id", "DOC_INDEX_RENDER")
        logger.info(f"🔬 Circuit [{circuit_id}]: Executing...")

        try:
            # SHABDA: Capture request (from circuit states)
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
            logger.error(f"❌ Circuit [{circuit_id}] failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _scan_docs_directories(self):
        """Scan docs/ subdirectories (using circuit allowlist)."""
        docs_dir = self.root_dir / "docs"
        if not docs_dir.exists():
            return

        for subdir in docs_dir.iterdir():
            if not subdir.is_dir():
                continue
            if subdir.name not in self.docs_allowlist:
                continue

            md_files = list(subdir.glob("**/*.md"))
            md_files = [f for f in md_files if "/archive/" not in str(f)]
            if md_files:
                self.doc_categories[subdir.name] = sorted(md_files)

    def _render_veda4_index(self) -> str:
        """Render INDEX.md with circuit-driven VEDA-4 structure."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        kernel_status = get_kernel_status(str(self.root_dir))

        template = load_template("index.jinja2")
        content = template.render(
            timestamp=timestamp,
            generator="SCRIBE",
            kernel_status=kernel_status,
            shabda_content=self._render_section("shabda"),
            artha_content=self._render_section("artha"),
            pratyaya_content=self._render_section("pratyaya"),
            karma_content=self._render_section("karma"),
            synth_content=self._render_section("synth"),
        )

        return content

    def _render_section(self, section_name: str) -> str:
        """Render a VEDA-4 section from circuit schema."""
        section = self.doc_schema.get(section_name, {})
        if not section:
            return ""

        output = ""

        # Root docs from circuit schema
        root_docs = section.get("root_docs", [])
        for doc_name in root_docs:
            doc_path = self.root_dir / doc_name
            if doc_path.exists():
                desc = self._get_description(doc_name)
                output += f"- **[{doc_name}]({doc_name})** — {desc}\n"

        # docs/ directories from circuit schema
        doc_dirs = section.get("doc_dirs", [])
        for dir_name in sorted(doc_dirs):
            files = self.doc_categories.get(dir_name, [])
            if files:
                output += f"\n**{dir_name.title()}:**\n"
                # Limit varies by section type
                limit = 10 if section_name == "pratyaya" else 8 if section_name == "synth" else 5
                for doc_path in files[:limit]:
                    rel_path = doc_path.relative_to(self.root_dir)
                    desc = self._get_description(doc_path.name)
                    output += f"- [{rel_path}]({rel_path}) — {desc}\n"

        return output

    def _get_description(self, filename: str) -> str:
        """Get description from circuit schema."""
        # Use circuit-defined descriptions
        if filename in self.doc_descriptions:
            return self.doc_descriptions[filename]
        # Fallback: generate from filename
        return filename.replace(".md", "").replace("_", " ")

    # Standalone mode
    def scan_and_render(self) -> str:
        """Standalone method for generate_docs.py."""
        self._scan_docs_directories()
        return self._render_veda4_index()

    def _scan_and_render(self) -> str:
        """Internal render with scan."""
        self._scan_docs_directories()
        return self._render_veda4_index()
