"""
Index Renderer.
Directly renders INDEX.md from Circuit Schema.

UNIFIED UI: Implements generate_content() pattern.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x0f6a5933"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

logger = logging.getLogger("INDEX_RENDERER")

# Circuit YAML path (relative to project root)
CIRCUIT_PATH = "vibe_core/playbook/circuits/doc_index_render.yaml"


class IndexRenderer(BaseRenderer):
    """
    Directly renders INDEX.md using VEDA-4 Circuit cognitive flow.
    """

    def __init__(self, kernel):
        super().__init__(kernel)
        self.root_dir = Path(".")
        self.doc_categories: Dict[str, List[Path]] = {}

        # Load circuit schema
        self.circuit = self._load_circuit()
        self.doc_schema = self.circuit.get("doc_schema", {})
        self.doc_descriptions = self.circuit.get("doc_descriptions", {})
        self.docs_allowlist = set(self.circuit.get("docs_allowlist", []))

    @property
    def name(self) -> str:
        return "index"

    @property
    def output_file(self) -> str:
        return "INDEX.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate INDEX.md content (UNIFIED UI pattern)."""
        self._scan_docs_directories()
        return self._generate_markdown()

    def _load_circuit(self) -> Dict[str, Any]:
        """Load circuit definition from YAML."""
        circuit_file = self.root_dir / CIRCUIT_PATH
        if not circuit_file.exists():
            logger.warning(f"Circuit file not found: {circuit_file}")
            return {"circuit": {}}

        try:
            with open(circuit_file) as f:
                data = yaml.safe_load(f)
            return data.get("circuit", {})
        except Exception as e:
            logger.error(f"Failed to load circuit: {e}")
            return {"circuit": {}}

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

    def _generate_markdown(self) -> str:
        """Render INDEX.md with circuit-driven VEDA-4 structure."""
        lines = ["# 🗂️ DOCUMENTATION INDEX", ""]
        lines.append(
            "> **VEDA-4 Structure:** Shabda (Entry) → Artha (Understand) → Pratyaya (Plan) → Karma (Execute) → Synth (Results)"
        )
        lines.append("")

        # Render Sections
        sections = ["shabda", "artha", "pratyaya", "karma", "synth"]
        for section in sections:
            content = self._render_section(section)
            if content:
                lines.append(f"## {section.upper()}")
                lines.append(content)
                lines.append("")

        return "\n".join(lines)

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
