"""
Ephemeral Renderer (4D Hypercube).
Renders EPHEMERAL.md via kernel.io.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

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

    def render(self) -> None:
        """Render EPHEMERAL.md via kernel I/O."""
        try:
            content = self._generate_content()
            self.kernel.io.write_document(
                name="EPHEMERAL.md",
                content=content,
                doc_type=DocumentType.READONLY,
                writer_id="interface_plugin",
                add_header=True,
            )
        except Exception as e:
            logger.error(f"Error rendering EPHEMERAL.md: {e}")

    def _generate_content(self) -> str:
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
        lines.extend(["## Active Cities", "", "_No active cities detected_", ""])

        return "\n".join(lines)

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
