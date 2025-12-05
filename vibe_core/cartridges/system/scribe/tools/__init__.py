"""
SCRIBE Documentation Generation Tools

All renderer tools implement the Tool protocol and are kernel-managed.

NOTE: Renderers are NOT auto-imported to avoid circular imports.
Import explicitly when needed:
    from vibe_core.cartridges.system.scribe.tools.agents_renderer import AgentsRenderer
"""

# Export shared utilities only (no circular imports)
from .base import Tool, ToolResult, get_template_dir, load_template

__all__ = [
    "Tool",
    "ToolResult",
    "load_template",
    "get_template_dir",
]
