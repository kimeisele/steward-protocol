"""
Architecture Plans Panel - Reads and displays OPUS manifest.json.

Shows current execution plans, their status, and priority.
"""

import json
from typing import TYPE_CHECKING, Any, Dict

from . import BasePanel

if TYPE_CHECKING:
    pass


class ArchitecturePlansPanel(BasePanel):
    """Displays architecture plans from OPUS/manifest.json."""

    @property
    def panel_id(self) -> str:
        return "architecture_plans"

    @property
    def title(self) -> str:
        return "Architecture Plans"

    @property
    def priority(self) -> int:
        return 5  # Show at top - most important for devs

    def _load_manifest(self) -> Dict[str, Any]:
        """Load OPUS manifest.json with caching."""
        cached = self.get_cached("manifest")
        if cached is not None:
            return cached

        manifest_path = self._root / "docs/architecture/OPUS/manifest.json"
        try:
            if manifest_path.exists():
                data = json.loads(manifest_path.read_text())
                self.set_cached("manifest", data)
                return data
        except Exception:
            pass

        return {}

    def _status_emoji(self, status: str) -> str:
        """Convert status to emoji."""
        mapping = {
            "active": "🔄",
            "ready": "✅",
            "pending": "⏳",
            "draft": "📝",
            "planned": "📋",
            "implemented": "✓",
            "superseded": "📦",
            "completed": "✅",
            "in_progress": "🔄",
        }
        return mapping.get(status.lower(), "❓")

    def _priority_badge(self, priority: str) -> str:
        """Convert priority to badge."""
        if priority == "P0":
            return "**🔴 P0**"
        elif priority == "P1":
            return "**🟡 P1**"
        elif priority == "P2":
            return "P2"
        else:
            return priority

    def render(self) -> str:
        """Render architecture plans from manifest."""
        manifest = self._load_manifest()

        if not manifest:
            return f"## {self.title}\n\n_No manifest.json found in docs/architecture/OPUS/_"

        lines = [f"## {self.title}", ""]

        # Header info
        name = manifest.get("name", "Unknown")
        version = manifest.get("version", "?")
        lines.append(f"**{name}** v{version}")
        lines.append("")

        # Documents list
        documents = manifest.get("documents", [])
        if documents:
            lines.append("### Current Plans")
            lines.append("")
            lines.append("| Priority | Status | Plan | Description |")
            lines.append("|----------|--------|------|-------------|")

            for doc in documents:
                priority = self._priority_badge(doc.get("priority", "P2"))
                status = self._status_emoji(doc.get("status", "draft"))
                title = doc.get("title", doc.get("id", "Unknown"))
                file = doc.get("file", "")
                desc = doc.get("description", "")[:50]

                # Make filename a link if it exists
                if file:
                    title = f"[{title}](docs/architecture/OPUS/{file})"

                lines.append(f"| {priority} | {status} | {title} | {desc} |")

            lines.append("")

        # Roadmap
        roadmap = manifest.get("roadmap", {})
        if roadmap:
            lines.append("### Roadmap")
            lines.append("")
            for phase, desc in roadmap.items():
                lines.append(f"- **{phase}**: {desc}")
            lines.append("")

        # Execution order (if present)
        exec_order = manifest.get("execution_order", {})
        if exec_order and exec_order.get("phases"):
            lines.append("### Execution Order")
            lines.append("")
            for phase in exec_order.get("phases", []):
                phase_num = phase.get("phase", "?")
                name = phase.get("name", "Unknown")
                status = self._status_emoji(phase.get("status", "pending"))
                tasks = phase.get("tasks", [])
                task_count = len(tasks)

                lines.append(f"- {status} **Phase {phase_num}: {name}** ({task_count} tasks)")

        return "\n".join(lines)
