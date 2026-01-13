"""
Ephemeral Renderer (4D Hypercube).
Renders EPHEMERAL.md via kernel.io.

UNIFIED UI: Implements generate_content() pattern.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x00f9cc24"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_EPHEMERAL")


class EphemeralRenderer(BaseRenderer):
    """Renders EPHEMERAL.md (Hypercube Interface)."""

    def __init__(self, kernel):
        super().__init__(kernel)
        self.merge_history: List[Dict[str, Any]] = []
        self.max_history = 10

    @property
    def name(self) -> str:
        return "ephemeral"

    @property
    def output_file(self) -> str:
        return "EPHEMERAL.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate EPHEMERAL.md content (UNIFIED UI pattern)."""
        try:
            return self._generate_markdown()
        except Exception as e:
            logger.error(f"Error generating EPHEMERAL content: {e}")
            return None

    def _generate_markdown(self) -> str:
        lines = ["# EPHEMERAL HYPERCUBE", ""]

        # Merge History
        lines.extend(["## Merge History", "", "| Time | Child ID | Result |", "| :--- | :--- | :--- |"])

        if not self.merge_history:
            lines.append("| _No merges recorded_ | | |")
        else:
            for entry in reversed(self.merge_history):
                lines.append(
                    f"| {entry.get('timestamp', '')} | {entry.get('child_id', '')} | {entry.get('result', '')} |"
                )

        lines.append("")

        # Active Cities (OPUS-023: Query live child kernels)
        lines.extend(self._render_active_cities())

        return "\n".join(lines)

    def _render_active_cities(self) -> List[str]:
        """
        Render active ephemeral cities from kernel._child_kernels.

        OPUS-023: Fractal UI Architecture
        Makes running child kernels visible in parent dashboard.
        """
        lines = ["## Active Cities", "", "| City ID | Status | Ledger Size |", "| :--- | :--- | :--- |"]

        child_kernels = getattr(self.kernel, "_child_kernels", [])

        if not child_kernels:
            lines.append("| _No active cities_ | | |")
        else:
            for child in child_kernels:
                city_id = str(id(child))[:8]
                # Check if child is booted
                status = "RUNNING" if getattr(child, "_booted", False) else "INIT"
                # Get ledger event count
                try:
                    ledger_size = len(child._ledger.get_all_events()) if hasattr(child, "_ledger") else 0
                except Exception:
                    ledger_size = 0
                lines.append(f"| {city_id} | {status} | {ledger_size} events |")

        lines.append("")
        return lines

    def record_merge(self, merge_record: Dict[str, Any]) -> None:
        """Record a merge event."""
        self.merge_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "child_id": str(merge_record.get("child_id", ""))[:8],
                "result": str(merge_record.get("result", ""))[:100],
            }
        )
        if len(self.merge_history) > self.max_history:
            self.merge_history = self.merge_history[-self.max_history :]
