"""
Ephemeral Renderer (4D Hypercube).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from vibe_core.doc_renderer import DocRenderer

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_EPHEMERAL")


class EphemeralRenderer(BaseRenderer):
    """Renders EPHEMERAL.md (Hypercube Interface)."""

    def __init__(self, kernel):
        super().__init__(kernel)
        self.doc_renderer = DocRenderer()
        self.merge_history: List[Dict[str, Any]] = []
        self.max_history = 10

    @property
    def name(self) -> str:
        return "ephemeral"

    def render(self) -> None:
        # Gather state
        state = {
            "merge_history": self.merge_history,
            "active_cities": [],
            "family_tree": {},
        }

        # Render
        try:
            self.doc_renderer.render_ephemeral(state)
        except Exception as e:
            logger.error(f"Error rendering EPHEMERAL.md: {e}")

    # Public API for recording merges (can be called by kernel via interface plugin if needed)
    # Note: Currently this state is local to the renderer.
    # Ideally, this should be in a separate 'EphemeralPlugin' that just holds state,
    # and this renderer just reads it. But for now, we keep it simple.
    def record_merge(self, merge_record: Dict[str, Any]) -> None:
        self.merge_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "child_id": str(merge_record.get("child_id", ""))[:8],
                "proof": str(merge_record.get("child_ledger_hash", ""))[:12],
                "result": str(merge_record.get("result", ""))[:100],
            }
        )
        if len(self.merge_history) > self.max_history:
            self.merge_history = self.merge_history[-self.max_history :]
