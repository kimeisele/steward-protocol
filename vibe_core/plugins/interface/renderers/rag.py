"""
RAG Renderer.
Directly renders RAG.md as a Realtime Architecture Guide Status Page.

UNIFIED UI: Implements generate_content() pattern.
"""

from typing import Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer


class RagRenderer(BaseRenderer):
    """Directly renders RAG.md as a status page for the RAG system."""

    @property
    def name(self) -> str:
        return "rag"

    @property
    def output_file(self) -> str:
        return "RAG.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate RAG.md content (UNIFIED UI pattern)."""
        status = self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN"
        return self._generate_markdown(status)

    def _generate_markdown(self, status: str) -> str:
        """Generate Markdown content."""
        lines = ["# 🧠 RAG (Realtime Architecture Guide)", ""]

        lines.append(
            "> **Definition:** RAG in VibeOS stands for **Realtime Architecture Guide**, not just Retrieval Augmented Generation."
        )
        lines.append("")

        lines.append("## 📊 System Context")
        lines.append(f"- **Kernel Status:** `{status}`")
        lines.append(f"- **Analyst Agent:** {'Active' if 'analyst' in self.kernel.agent_registry else 'Inactive'}")
        lines.append("")

        lines.append("## 4D Analysis Dimensions")
        lines.append("The Analyst agent monitors the repository across 4 dimensions:")
        lines.append("1. **Time (Git):** Velocity, momentum, and history.")
        lines.append("2. **Code (AST):** Complexity, debt, and patterns.")
        lines.append("3. **Structure (Topology):** Module boundaries and dependencies.")
        lines.append("4. **Documentation (Semantics):** Coverage and meaning.")
        lines.append("")

        lines.append("## 🚀 Actions")
        lines.append("To generate a deep analysis report, run:")
        lines.append("```bash")
        lines.append("python scripts/dispatch.py analyst synthesize")
        lines.append("```")

        return "\n".join(lines)
