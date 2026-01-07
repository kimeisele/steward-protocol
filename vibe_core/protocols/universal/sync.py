from typing import Optional, Protocol, runtime_checkable

from .types import SovereignContext, SyncResult, SyncStatus


@runtime_checkable
class SyncProtocol(Protocol):
    """
    Atomic protocol for synchronization operations.

    GAD-000 COMPLIANCE:
    - Discoverability: Type-safe interfaces.
    - Observability: 'get_sync_status' provides structured state.
    - Parseability: 'SyncResult' contains structured errors.
    - Composability: Can be triggered via orchestration.
    - Idempotency: Sync should be intrinsically idempotent.
    - Recoverability: Sync is the primary recovery mechanism (Ouroboros).
    """

    def sync(self, context: Optional[SovereignContext] = None) -> SyncResult:
        """
        Perform synchronization.
        Args:
            context: (Required for Anti-Mayavad) Identity initiating sync.
        """
        ...

    def get_sync_status(self, context: Optional[SovereignContext] = None) -> SyncStatus:
        """Get current sync status."""
        ...

    def is_synced(self, context: Optional[SovereignContext] = None) -> bool:
        """Check if synchronized."""
        ...
