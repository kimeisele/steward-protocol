"""
SESHA Protocol - Der Träger der Welten (Data/Ledger/Gossip)

Ananta Sesha - Die unendliche Schlange, Träger der Wahrheit.
PROMPT.md: "Truth is purely additive."

Responsibilities:
- Wrap existing SQLiteLedger for gossip sync
- Export/Import blocks for federation
- Maintain hash chain integrity
- NO complex consensus (Keep Sesha dumb)

Integration:
- Registers as handler for DriftSource.STATE
- Detects state drift via hash comparison
- Heals by syncing missing blocks
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga.types import EventDict, EventRecord, NagaStatus, NagaType


class SyncStatus(str, Enum):
    """Status of a gossip sync operation."""

    SYNCHRONIZED = "synchronized"  # Hashes match
    NEED_SYNC = "need_sync"  # Missing blocks
    CONFLICT = "conflict"  # Divergent chains
    ERROR = "error"  # Sync failed


@dataclass
class LedgerBlock:
    """A chunk of ledger events for gossip sync."""

    sequence: int
    events: List[EventDict]
    hash: str
    prev_hash: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, object]:
        return {
            "sequence": self.sequence,
            "events": self.events,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SyncRequest:
    """Request for gossip sync between nodes."""

    my_hash: str
    my_sequence: int
    peer_hash: Optional[str] = None
    status: SyncStatus = SyncStatus.NEED_SYNC


@dataclass
class ImportResult:
    """Result of importing blocks from another node."""

    success: bool
    blocks_imported: int = 0
    final_sequence: int = 0
    final_hash: str = ""
    message: str = ""
    conflicts: List[str] = field(default_factory=list)


@runtime_checkable
class SeshaProtocol(Protocol):
    """
    Ananta Sesha - Die unendliche Schlange, Träger der Wahrheit.

    PROMPT.md: "Truth is purely additive."

    Responsibilities:
    - Wrap existing SQLiteLedger for gossip sync
    - Export/Import blocks for federation
    - Maintain hash chain integrity
    - NO complex consensus (Keep Sesha dumb)

    Integration:
    - Registers as handler for DriftSource.STATE
    - Detects state drift via hash comparison
    - Heals by syncing missing blocks

    Usage:
        sesha = ServiceRegistry.get(SeshaProtocol)
        blocks = sesha.export_blocks(since=100)
        result = peer.sesha.import_blocks(blocks)
    """

    # === Event Recording (PUBLIC API) ===

    def record_event(self, event: EventRecord) -> bool:
        """
        Record an event to the ledger.

        YAMARAJA: This is the ONE entry point for writing to the ledger.
        No more accessing _ledger directly!

        Args:
            event: Typed event record (EventRecord TypedDict)

        Returns:
            True if recorded successfully, False otherwise

        Raises:
            ValueError: If event_type or agent_id is missing
        """
        ...

    # === Event Reading (PUBLIC API) ===

    def get_recent_events(self, limit: int = 10) -> List[EventDict]:
        """
        Get recent events from the ledger.

        YAMARAJA: This is the ONE entry point for reading recent events.
        No more accessing _ledger directly!

        Args:
            limit: Maximum number of events to return (default 10)

        Returns:
            List of recent events (newest first)
        """
        ...

    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[EventDict]:
        """
        Get events of a specific type from the ledger.

        YAMARAJA: This is the ONE entry point for filtered reading.
        No more accessing _ledger directly!

        Args:
            event_type: Type of events to retrieve
            limit: Maximum number of events to return (default 100)

        Returns:
            List of matching events (newest first)
        """
        ...

    # === Ledger Wrapper ===

    def get_top_hash(self) -> str:
        """Get the hash of the latest ledger block."""
        ...

    def get_sequence(self) -> int:
        """Get the current sequence number."""
        ...

    def get_events_since(self, sequence: int) -> List[EventDict]:
        """Get all events since a sequence number."""
        ...

    # === Gossip Sync ===

    def export_blocks(self, since: int = 0, limit: int = 100) -> List[LedgerBlock]:
        """
        Export blocks for gossip to peers.

        Args:
            since: Start sequence (0 = from beginning)
            limit: Max blocks to export

        Returns:
            List of LedgerBlocks for transfer
        """
        ...

    def import_blocks(self, blocks: List[LedgerBlock]) -> ImportResult:
        """
        Import blocks received from a peer.

        Validates hash chain before accepting.

        Args:
            blocks: Blocks to import

        Returns:
            ImportResult with success/failure details
        """
        ...

    def request_sync(self, peer_hash: str, peer_sequence: int) -> SyncRequest:
        """
        Initiate sync with a peer.

        Compares hashes to determine if sync needed.

        Args:
            peer_hash: The peer's top hash
            peer_sequence: The peer's sequence number

        Returns:
            SyncRequest indicating action needed
        """
        ...

    # === CorrectionHandler Interface ===

    def as_handler(self) -> CorrectionHandler:
        """
        Get this NAGA as a CorrectionHandler.

        Register with:
            dispatcher.register_handler(
                DriftSource.STATE,
                sesha.as_handler(),
                handler_id="sesha",
                priority=50
            )
        """
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullSesha:
    """No-op Sesha for when ledger is unavailable."""

    def record_event(self, event: EventRecord) -> bool:
        """No-op - returns False (no ledger available)."""
        return False

    def get_recent_events(self, limit: int = 10) -> List[EventDict]:
        """No-op - returns empty list (no ledger available)."""
        return []

    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[EventDict]:
        """No-op - returns empty list (no ledger available)."""
        return []

    def get_top_hash(self) -> str:
        return ""

    def get_sequence(self) -> int:
        return 0

    def get_events_since(self, sequence: int) -> List[EventDict]:
        return []

    def export_blocks(self, since: int = 0, limit: int = 100) -> List[LedgerBlock]:
        return []

    def import_blocks(self, blocks: List[LedgerBlock]) -> ImportResult:
        return ImportResult(success=False, message="No ledger")

    def request_sync(self, peer_hash: str, peer_sequence: int) -> SyncRequest:
        return SyncRequest(my_hash="", my_sequence=0, status=SyncStatus.ERROR)

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_sesha",
                message="Sesha not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Not initialized")
