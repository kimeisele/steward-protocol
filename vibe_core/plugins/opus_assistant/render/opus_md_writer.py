"""
OPUS.md Writer - Thin wrapper for backward compatibility.

OPUS-029 Phase 10: All rendering now done via Jinja2 templates.
This file exists ONLY for backward compatibility with old imports.

The REAL renderer is: opus_dashboard_renderer.py

DO NOT ADD f-strings here. If you need to change the output,
edit the template: templates/opus_dashboard.md.j2
"""

from pathlib import Path
from typing import Any, Optional


class OpusMdWriter:
    """
    DEPRECATED: Use OpusDashboardRenderer instead.

    This class exists only for backward compatibility.
    All methods delegate to the template-based renderer.
    """

    def __init__(self, workspace_root: Path, kernel: Optional[Any] = None):
        """Initialize by creating the real renderer."""
        from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
            OpusDashboardRenderer,
        )

        self._renderer = OpusDashboardRenderer(workspace_root, kernel)

    def write(self, quick: bool = False) -> Path:
        """Delegate to template renderer."""
        return self._renderer.write(quick=quick)

    def _generate_content(self, quick: bool = False, preserved: Optional[dict] = None) -> str:
        """Delegate to template renderer."""
        return self._renderer.render(quick=quick)


def write_opus_md(workspace_root: Path, kernel: Optional[Any] = None, quick: bool = False) -> Path:
    """
    Convenience function - delegates to template renderer.

    Args:
        workspace_root: Project root
        kernel: Optional kernel for runtime data
        quick: Skip expensive verification

    Returns:
        Path to OPUS.md
    """
    from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
        OpusDashboardRenderer,
    )

    renderer = OpusDashboardRenderer(workspace_root, kernel)
    return renderer.write(quick=quick)
