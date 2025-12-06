"""
OPUS Renderer - Bidirectional Dashboard.

MERGES live data into existing OPUS.md, preserving:
- Blockers (AI can write)
- Next Actions (AI proposes, human approves)
- Extraction Log history

Updates:
- Kernel Stats (LOC)
- Test counts
- Git status
- Timestamp
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from ..base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_OPUS")


class OpusRenderer(BaseRenderer):
    """Renders OPUS.md with bidirectional merge."""

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self._opus_path = Path("OPUS.md")

    @property
    def name(self) -> str:
        return "opus"

    def render(self) -> None:
        """Merge live data into existing OPUS.md."""
        if not self._opus_path.exists():
            logger.warning("OPUS.md not found - skipping render")
            return

        content = self._opus_path.read_text()

        # Update live sections
        content = self._update_kernel_loc(content)
        content = self._update_timestamp(content)

        # Write back
        try:
            self.kernel.io.write_document(name="OPUS.md", content=content, writer_id="RENDERER_OPUS")
        except Exception as e:
            logger.error(f"Write failed: {e}")

    def _update_kernel_loc(self, content: str) -> str:
        """Update kernel_impl.py LOC in the table."""
        try:
            kernel_path = Path("vibe_core/kernel_impl.py")
            if kernel_path.exists():
                loc = len(kernel_path.read_text().splitlines())

                # Update the LOC value in the metrics table
                # Pattern: | kernel_impl.py LOC | NUMBER | 1008 | STATUS |
                pattern = r"\| kernel_impl\.py LOC \| \d+ \|"
                replacement = f"| kernel_impl.py LOC | {loc} |"
                content = re.sub(pattern, replacement, content)

                # Update status based on LOC
                if loc <= 1008:
                    status = "COMPLETE"
                elif loc <= 1108:
                    status = "ALMOST"
                else:
                    status = "IN_PROGRESS"

                # Update status in same row
                pattern = r"(\| kernel_impl\.py LOC \| \d+ \| 1008 \| )\w+"
                replacement = f"\\g<1>{status}"
                content = re.sub(pattern, replacement, content)

        except Exception as e:
            logger.warning(f"Could not update kernel LOC: {e}")

        return content

    def _update_timestamp(self, content: str) -> str:
        """Update the last updated timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Update footer timestamp
        pattern = r"\*Rendered by: OpusRenderer \| Last updated: [^*]+\*"
        replacement = f"*Rendered by: OpusRenderer | Last updated: {timestamp}*"
        content = re.sub(pattern, replacement, content)

        return content


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> OpusRenderer:
    """Factory function."""
    return OpusRenderer(kernel)
