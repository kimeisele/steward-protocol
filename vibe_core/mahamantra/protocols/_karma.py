"""
KARMA PROTOCOL - The Action (Execution & Logs)
==============================================

"karmani eva adhikaras te ma phalesu kadacana"
"You have a right to perform your prescribed duty, but you are not entitled to the fruits of action."
— Bhagavad Gita 2.47

POSITION: Hare Rama (Karma Quarter) / Advaita (Causality)
FUNCTION: Execution, Side-Effects, Ledger.

This protocol defines HOW actions are executed and recorded.
Every action produces a Log Entry (Karma Phalam).

LOCATION: vibe_core.mahamantra.protocols._karma (THE LAW)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x50862801"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Optional, Protocol, TypedDict, runtime_checkable

from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict


class KarmaPhalam(TypedDict):
    """The fruit of action (Result + Log)."""

    action_id: str
    timestamp: str
    status: str
    result: Optional[object]
    error: Optional[str]


@runtime_checkable
class KarmaProtocol(PanchaTattvaProtocol, Protocol):
    """
    The Action Protocol.
    Defines execution and consequence (logging).
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "Action Protocol",
            "nityananda": "Seed Protocol",
            "advaita": "Causality Logic",
            "gadadhara": "Execution Flow",
            "srivasa": "Ledger Governance",
        }

    def execute(self, action: str, params: Dict[str, object]) -> KarmaPhalam:
        """
        Execute an action and return its fruit (Karma).
        MUST be recorded in the Ledger.
        """
        ...

    def log_karma(self, phalam: KarmaPhalam) -> None:
        """Record the fruit of action to the immutable Ledger."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KarmaPhalam",
    "KarmaProtocol",
]
