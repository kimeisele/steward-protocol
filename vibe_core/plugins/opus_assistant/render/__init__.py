"""
OPUS Render Module - BACKEND only (data provider).

ARCHITECTURE:
- OpusDashboardRenderer.render() → STRING (content only)
- NO file writes - InterfacePlugin handles that via kernel.io

Legacy opus_md_writer.py DELETED - no split-brain!
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x3d4b6208"  # GenesisByte: parampara % 37 == 0

from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
    OpusDashboardRenderer,
)

__all__ = [
    "OpusDashboardRenderer",
]
