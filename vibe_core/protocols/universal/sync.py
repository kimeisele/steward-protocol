from typing import Protocol, runtime_checkable

from .types import SyncResult, SyncStatus


@runtime_checkable
class SyncProtocol(Protocol):
    """
    Atomic protocol for synchronization operations.
    Standardizes how state is synchronized between systems.
    """

    def sync(self) -> SyncResult:
        """Perform synchronization."""
        ...

    def get_sync_status(self) -> SyncStatus:
        """Get current sync status."""
        ...

    def is_synced(self) -> bool:
        """Check if synchronized."""
        ...
