"""
LIBRARIAN Tools - Knowledge Management

All tools implement the Tool Protocol (vibe_core.tools.tool_protocol.Tool).
These tools are registered with the kernel, not owned by the agent.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x28b1a3a1"  # GenesisByte: parampara % 37 == 0

from .catalog_tool import CatalogBookTool
from .recommend_tool import RecommendBooksTool
from .search_tool import SearchBooksTool

__all__ = [
    "CatalogBookTool",
    "SearchBooksTool",
    "RecommendBooksTool",
]
