"""
Ephemeral Renderer (4D Hypercube).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

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
        try:
            content = self._generate_content()
            with open("EPHEMERAL.md", "w") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error rendering EPHEMERAL.md: {e}")

    def _generate_content(self) -> str:
        lines = ["# 🧊 EPHEMERAL HYPERCUBE", ""]

        # Merge History
        lines.extend(
            ["## 🧬 Merge History", "", "| Time | Child ID | Proof | Result |", "| :--- | :--- | :--- | :--- |"]
        )

        if not self.merge_history:
            lines.append("_No merges recorded_")
        else:
            for entry in reversed(self.merge_history):
                lines.append(
                    f"| {entry.get('timestamp', '')} | {entry.get('child_id', '')} | {entry.get('proof', '')} | {entry.get('result', '')} |"
                )

        lines.append("")

        # Active Cities (Placeholder for now)
        lines.extend(["## 🏙️ Active Cities", "", "_No active cities detected_", ""])

        return "\n".join(lines)

    # Public API for recording merges (can be called by kernel via interface plugin if needed)
    def record_merge(self, merge_record: Dict[str, Any]) -> None:
        self.merge_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "child_id": str(merge_record.get("child_id", ""))[:8],
                "child_ledger_hash": str(merge_record.get("child_ledger_hash", ""))[:12],
                "result": str(merge_record.get("result", ""))[:100],
            }
        )
        if len(self.merge_history) > self.max_history:
            self.merge_history = self.merge_history[-self.max_history :]
