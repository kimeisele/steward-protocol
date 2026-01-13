"""
ENFORCE PROTOCOL - The Law of Karma (Layer 1)
==============================================

HARDENED (Phase 28):
- Replaced 'bool' returns with 'HolyName'.
- You cannot simply 'Pass' or 'Fail'. You generate Karma, Akarma, or Vikarma.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x87f518fe"  # GenesisByte: parampara % 37 == 0

from typing import List, Protocol, runtime_checkable
from vibe_core.protocols.substrate.byte import HolyName
from .types import EnforceContext, Rule, Verdict, SovereignContext


@runtime_checkable
class EnforceProtocol(Protocol):
    """
    The Law of Karma.

    HARDENED (Phase 28):
    Replaced 'bool' returns with 'HolyName'.
    You cannot simply 'Pass' or 'Fail'. You generate Karma, Akarma, or Vikarma.
    """

    def verify_action(self, action: str, ctx: SovereignContext) -> HolyName:
        """
        Prüft, ob die Aktion mit der Parampara harmoniert.

        Returns:
            KRISHNA (01): Action Authorized (Akarma / Devotion).
            RAMA (10):    Action Allowed with Warning (Karma / Duty).
            VOID (11):    Action Blocked (Vikarma / Sin/Error).
            HARE (00):    Action Ignored/Pending.
        """
        ...

    def enforce(self, action: str, context: EnforceContext) -> Verdict:
        """
        Enforce rules on an action.
        The 'context' now strictly contains a 'sovereign'.
        """
        ...

    def calculate_merkle_root(self, ctx: SovereignContext, action: str) -> str:
        """
        Berechnet den neuen Hash für den Ledger basierend auf:
        Identity + PreviousHash + Action + MantraResonance.
        """
        ...

    def get_rules(self) -> List[Rule]:
        """Get active rules (Transparency)."""
        ...
