"""
Ephemeral Renderer (4D Hypercube).
Renders EPHEMERAL.md via kernel.io.

UNIFIED UI: Implements generate_content() pattern.
"""

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

    def render(self) -> None:
        """Legacy render - DEPRECATED."""
        content = self.generate_content()
        if content:
            self.kernel.io.write_document(
                name="EPHEMERAL.md",
                content=content,
                doc_type=DocumentType.READONLY,
                writer_id="interface_plugin",
                add_header=True,
            )

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
