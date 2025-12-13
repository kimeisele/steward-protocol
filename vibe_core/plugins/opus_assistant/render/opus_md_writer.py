"""
OPUS.md Writer - DEPRECATED Legacy Wrapper.

⚠️ ARCHITECTURE:
- opus_assistant is BACKEND only (data provider)
- InterfacePlugin is FRONTEND (writes via kernel.io)
- This file exists ONLY for backward compatibility

DO NOT USE write() methods - they will raise errors.
Use InterfacePlugin.render_view("opus") instead.
"""

import warnings
from pathlib import Path
from typing import Any, Optional


class OpusMdWriter:
    """
    DEPRECATED: Use InterfacePlugin.render_view("opus") instead.

    This class exists only for backward compatibility.
    write() methods will raise errors - use render() for content only.
    """

    def __init__(self, workspace_root: Path, kernel: Optional[Any] = None):
        """Initialize by creating the real renderer."""
        from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
            OpusDashboardRenderer,
        )

        self._renderer = OpusDashboardRenderer(workspace_root, kernel)

    def write(self, quick: bool = False) -> Path:
        """
        REMOVED: Direct file writes violate architecture.

        Use InterfacePlugin.render_view("opus") instead.
        """
        raise NotImplementedError(
            "OpusMdWriter.write() removed - opus_assistant is BACKEND only. "
            "Use InterfacePlugin.render_view('opus') for file writes."
        )

    def _generate_content(self, quick: bool = False, preserved: Optional[dict] = None) -> str:
        """Generate content (for backward compatibility)."""
        warnings.warn(
            "OpusMdWriter._generate_content() is deprecated. Use OpusDashboardRenderer.render() directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._renderer.render(quick=quick)


def write_opus_md(workspace_root: Path, kernel: Optional[Any] = None, quick: bool = False) -> Path:
    """
    REMOVED: Direct file writes violate architecture.

    Use InterfacePlugin.render_view("opus") instead.
    """
    raise NotImplementedError(
        "write_opus_md() removed - opus_assistant is BACKEND only. "
        "Use InterfacePlugin.render_view('opus') for file writes."
    )
