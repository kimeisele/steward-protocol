"""
Help Renderer.
Directly renders HELP.md from Kernel State and File System.

UNIFIED UI: Implements generate_content() pattern.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x70145f84"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from typing import List, Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer


class HelpRenderer(BaseRenderer):
    """Directly renders HELP.md as a System Control Center."""

    @property
    def name(self) -> str:
        return "help"

    @property
    def output_file(self) -> str:
        return "HELP.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate HELP.md content (UNIFIED UI pattern)."""
        scripts = self._scan_scripts()
        return self._generate_markdown(scripts)

    def _scan_scripts(self) -> List[str]:
        """Scan scripts/ directory for entry points."""
        scripts_dir = Path("scripts")
        if not scripts_dir.exists():
            return []

        return sorted([f.name for f in scripts_dir.glob("*.py")])

    def _generate_markdown(self, scripts: List[str]) -> str:
        """Generate Markdown content."""
        lines = ["# 🆘 HELP & CONTROL CENTER", ""]

        # 1. System Health (Diagnostics)
        status = self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN"
        agent_count = len(self.kernel.agent_registry)

        lines.append("## 🏥 System Diagnostics")
        lines.append(f"- **Kernel Status:** `{status}`")
        lines.append(f"- **Active Agents:** {agent_count}")
        lines.append(f"- **Ledger:** {'Online' if hasattr(self.kernel, '_ledger') else 'Offline'}")
        lines.append("")

        # 2. Control Room (Scripts)
        lines.append("## 🎛️ Control Room (Scripts)")
        if not scripts:
            lines.append("_No scripts found_")
        else:
            lines.append("Run these from your terminal:")
            lines.append("")
            for script in scripts:
                lines.append(f"- `python scripts/{script}`")
        lines.append("")

        # 3. Documentation Index
        lines.append("## 📚 Documentation Index")
        lines.append("- [**README.md**](README.md) - System Overview")
        lines.append("- [**AGENTS.md**](AGENTS.md) - Active Agents")
        lines.append("- [**CITYMAP.md**](CITYMAP.md) - Topology & Architecture")
        lines.append("- [**ENVOY.md**](ENVOY.md) - Terminal Interface")
        lines.append("- [**SETTINGS.md**](SETTINGS.md) - System Configuration")

        return "\n".join(lines)
