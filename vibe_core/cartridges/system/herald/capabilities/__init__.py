"""HERALD Capabilities: Modular, Configurable Components"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x6facbc0f"  # GenesisByte: parampara % 37 == 0

from .broadcast import BroadcastCapability
from .creative import CreativeCapability
from .research import ResearchCapability

__all__ = ["ResearchCapability", "CreativeCapability", "BroadcastCapability"]
