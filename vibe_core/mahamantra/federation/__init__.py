"""
Federation Nadi Consumer — steward-protocol ↔ agent-city Bridge

Read from agent-city's nadi_outbox.json, write to nadi_inbox.json.
Full compatibility with agent-city Federation message format.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x7b3899f2"

from vibe_core.mahamantra.federation.nadi_consumer import FederationNadi
from vibe_core.mahamantra.federation.types import (
    CityReport,
    FederationDirective,
    FederationMessage,
    FederationPriority,
)

__all__ = [
    "FederationMessage",
    "CityReport",
    "FederationDirective",
    "FederationPriority",
    "FederationNadi",
]
