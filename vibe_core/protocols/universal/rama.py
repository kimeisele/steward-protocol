"""
RAMA PROTOCOL - Layer 2 (Action / Dharma)

"Ramadi Murtishu" - Manifesting in many forms to serve.

This protocol defines the "Work" (Karma) that the system performs.
It corresponds to the "Serve" phase of the Mantra.

GAD-000 COMPLIANT:
- Discoverability: Protocol is runtime_checkable
- Observability: list_pending_dharmas() ← RED-003 FIX
- Parseability: DharmaResult + DharmaStatus dataclasses
- Composability: Results pipeable
- Idempotency: idempotency_key parameter ← RED-002 FIX
- Recoverability: cancel_dharma() for cleanup
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x3c85b504"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, List, Optional, Protocol, TypedDict, runtime_checkable

from .types import SovereignContext


class DharmaResult(TypedDict, total=False):
    """Result of a Dharma action (Prasadam)."""

    status: str
    actions_performed: int
    errors: List[str]
    details: str
    idempotency_key: str  # RED-002: Echo back the key


@dataclass
class DharmaStatus:
    """GAD-000 Observability: Status of a pending/running Dharma."""

    dharma_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    started_at: Optional[datetime] = None
    context_id: str = ""
    progress: float = 0.0  # 0.0 to 1.0


@runtime_checkable
class RamaProtocol(Protocol):
    """
    The Protocol of Righteous Action (Dharma).

    This is the interface for the "Executor" or "Worker".

    GAD-000:
    - Idempotency via idempotency_key
    - Observability via list_pending_dharmas()
    """

    async def perform_dharma(
        self,
        context: SovereignContext,
        idempotency_key: Optional[str] = None,  # RED-002 FIX
    ) -> DharmaResult:
        """
        Execute the Duty (Work) assigned to this moment.

        This corresponds to MantraOpCode.EXTEND_CAP.

        Args:
            context: The Identity performing the action.
            idempotency_key: Optional key for safe retry (GAD-000).

        Returns:
            Result of the action (Prasadam).
        """
        ...

    def list_pending_dharmas(self) -> Iterator[DharmaStatus]:
        """
        GAD-000 Observability: List all pending/running dharmas.

        Returns:
            Iterator of DharmaStatus for streaming (GAD-000 Composability).
        """
        ...

    def cancel_dharma(self, dharma_id: str) -> bool:
        """
        GAD-000 Recoverability: Cancel a pending dharma.

        Args:
            dharma_id: ID of dharma to cancel.

        Returns:
            True if cancelled, False if not found or already completed.
        """
        ...
