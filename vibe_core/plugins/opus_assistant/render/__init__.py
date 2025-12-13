"""
OPUS Render Module - BACKEND only (data provider).

ARCHITECTURE:
- OpusDashboardRenderer.render() → STRING (content only)
- NO file writes - InterfacePlugin handles that via kernel.io

Legacy opus_md_writer.py DELETED - no split-brain!
"""

from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
    OpusDashboardRenderer,
)

__all__ = [
    "OpusDashboardRenderer",
]
