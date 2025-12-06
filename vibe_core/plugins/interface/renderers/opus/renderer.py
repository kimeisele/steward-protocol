"""
OPUS Renderer - Master AI Dashboard.

Extends ArchitectureRenderer + OpusDocsProvider for all data sources.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from ..architecture.renderer import ArchitectureRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class OpusRenderer(ArchitectureRenderer):
    """Master AI Dashboard - extends Architecture with opus.* sources."""

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self._docs_path = Path("docs/architecture/OPUS")

    @property
    def name(self) -> str:
        return "opus"

    def _register_data_sources(self) -> None:
        """Register arch.* + opus.* sources."""
        super()._register_data_sources()
        # Kernel status
        self.register_data_source("kernel.status", self._get_kernel_status)
        self.register_data_source("opus.metrics", self._get_metrics)
        # From manifest.json (dynamic)
        self.register_data_source("opus.roadmap", self._get_roadmap)
        self.register_data_source("opus.documents", self._get_documents)
        self.register_data_source("opus.p0_plans", self._get_p0_plans)

    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest.json fresh each time."""
        manifest_path = self._docs_path / "manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text())
        return {}

    def _get_roadmap(self) -> List[Dict[str, str]]:
        """Return roadmap from manifest.json."""
        manifest = self._load_manifest()
        roadmap = manifest.get("roadmap", {})
        return [{"Phase": k, "Description": v} for k, v in roadmap.items()]

    def _get_documents(self) -> List[Dict[str, Any]]:
        """Return documents table from manifest.json."""
        manifest = self._load_manifest()
        return [
            {"ID": d["id"], "Title": d["title"], "Status": d["status"], "Priority": d["priority"]}
            for d in manifest.get("documents", [])
        ]

    def _get_p0_plans(self) -> str:
        """Return P0 doc contents from manifest.json."""
        manifest = self._load_manifest()
        p0_docs = [d for d in manifest.get("documents", []) if d.get("priority") == "P0"]
        lines = []
        for doc in p0_docs:
            doc_path = self._docs_path / doc["file"]
            if doc_path.exists():
                lines.append("<details>")
                lines.append(f"<summary>{doc['title']}</summary>")
                lines.append("")
                lines.append(doc_path.read_text())
                lines.append("")
                lines.append("</details>")
                lines.append("")
        return "\n".join(lines) if lines else "_No P0 plans_"

    def _get_kernel_status(self) -> str:
        """Kernel status line."""
        status = getattr(self.kernel, "status", "UNKNOWN")
        if hasattr(status, "value"):
            status = status.value

        agent_count = 0
        if hasattr(self.kernel, "agent_registry"):
            try:
                agent_count = len(self.kernel.agent_registry.list_agents())
            except Exception:
                pass

        loc = self._count_loc("vibe_core/kernel_impl.py")
        return f"**Kernel**: {status} | **Agents**: {agent_count} | **LOC**: {loc}"

    def _get_metrics(self) -> List[Dict[str, Any]]:
        """Kernel metrics table."""
        loc = self._count_loc("vibe_core/kernel_impl.py")
        target = 1008
        plugin_count = len(self.kernel._plugins) if hasattr(self.kernel, "_plugins") else 0

        return [
            {
                "Metric": "kernel_impl.py LOC",
                "Current": loc,
                "Target": target,
                "Delta": loc - target,
                "Status": "✅" if loc <= target else ("🟡" if loc <= target + 100 else "🔴"),
            },
            {
                "Metric": "Plugins Loaded",
                "Current": plugin_count,
                "Target": "8+",
                "Delta": "-",
                "Status": "✅" if plugin_count >= 8 else "🟡",
            },
        ]


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> OpusRenderer:
    """Factory function."""
    return OpusRenderer(kernel)
