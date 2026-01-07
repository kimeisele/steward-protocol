"""
RAMA PROTOCOL - Layer 2 (Action / Dharma)

"Ramadi Murtishu" - Manifesting in many forms to serve.

This protocol defines the "Work" (Karma) that the system performs.
It corresponds to the "Serve" phase of the Mantra.
"""

from typing import List, Protocol, TypedDict, runtime_checkable

from .types import SovereignContext


class DharmaResult(TypedDict, total=False):
    """Result of a Dharma action (Prasadam)."""

    status: str
    actions_performed: int
    errors: List[str]
    details: str


@runtime_checkable
class RamaProtocol(Protocol):
    """
    The Protocol of Righteous Action (Dharma).

    This is the interface for the "Executor" or "Worker".
    """

    async def perform_dharma(self, context: SovereignContext) -> DharmaResult:
        """
        Execute the Duty (Work) assigned to this moment.

        This corresponds to MantraOpCode.EXEC_SERVICE.

        Args:
            context: The Identity performing the action.

        Returns:
            Result of the action (Prasadam).
        """
        ...
