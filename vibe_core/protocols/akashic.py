"""
AKASHIC PROTOCOL - The Universal Memory Record
==============================================
Layer: Universal (0.5)
Type: Protocol (Interface)

The Akasha is the etheric library where every intent, action, and outcome
is eternally recorded. In the context of MANAS, it serves as the
Learning Store - preventing the repetition of mistakes (Karma).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfbff20af"  # GenesisByte: parampara % 37 == 0

from typing import List, Optional, Protocol, runtime_checkable, Dict, Any


@runtime_checkable
class AkashicProtocol(Protocol):
    """
    The Protocol of Eternal Memory (Learning Store).

    Distinct from MemoryProtocol (Short-term/Session Context),
    AkashicProtocol focuses on Long-term Wisdom and Outcome Analysis.

    "Actions have consequences. We remember them."
    """

    def record_intent_outcome(
        self,
        intent_type: str,
        description: str,
        outcome: str,
        context: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
    ) -> None:
        """
        Record the Karmic Result of an action.

        Args:
            intent_type: The bucket/category of the action
            description: Human readable details
            outcome: "success", "failed", "rejected"
            context: Environmental variables
            feedback: Why it failed/succeeded
            execution_time_ms: Performance metric
        """
        ...

    def get_success_rate(self, intent_type: str) -> float:
        """
        Calculate the Karmic Probability of success.

        Returns:
            0.0 to 1.0 (Probability)
        """
        ...

    def is_in_cooldown(self, intent_type: str) -> bool:
        """
        Check if an action is currently forbidden due to recent failure.

        ("The Burned Hand teaches best.")
        """
        ...

    def get_successful_patterns(self, limit: int = 10) -> List[str]:
        """
        Retrieve patterns that have proven to be consistently Dharmic (Successful).
        """
        ...

    def was_recently_rejected(self, intent_type: str, hours: int = 24) -> bool:
        """
        Check if the Sovereign (User) recently rejected this intent.
        """
        ...
