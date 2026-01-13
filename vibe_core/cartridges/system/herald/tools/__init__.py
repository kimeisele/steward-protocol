"""
HERALD Tools - Cartridge components for vibe-agency compatibility.

Each tool encapsulates a capability:
- ResearchTool: Market intelligence via Tavily
- BroadcastTool: Social media publishing (Twitter, Reddit)
- IdentityTool: Cryptographic signing via Steward Protocol
- ScoutTool: Network discovery
- Scribe: Chronicle writing

Note: ContentTool was removed - content generation moved to Marketer.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x63497696"  # GenesisByte: parampara % 37 == 0

from .broadcast_tool import BroadcastTool
from .identity_tool import IdentityTool
from .research_tool import ResearchTool
from .scout_tool import ScoutTool
from .scribe_tool import Scribe

__all__ = ["ResearchTool", "BroadcastTool", "IdentityTool", "ScoutTool", "Scribe"]
