"""
SESHA SERVICE - Der Träger der Welten.

Ananta Sesha - Die unendliche Schlange, auf der Vishnu ruht.

PROMPT.md: "Truth is purely additive."

Responsibilities:
- Wrap SQLiteLedger for gossip sync
- Export/import blocks for federation
- Hash-based sync requests
- Detect STATE drift via integrity checks

Integration:
- Registers as CorrectionHandler for DriftSource.STATE
- Auto-discovered by Narada via @naga_service decorator
"""

import hashlib
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.correction import (
    DriftSeverity,
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga import (
    ImportResult,
    LedgerBlock,
    NagaStatus,
    NagaType,
    SeshaProtocol,
    SyncRequest,
    SyncStatus,
)
from vibe_core.protocols.naga.groups import DataProtocol

if TYPE_CHECKING:
    from vibe_core.ledger import SQLiteLedger

logger = logging.getLogger("SESHA")


@naga_service(
    name="Sesha",
    lord=NagaLord.SESHA,
    drift_source="state",
    priority=85,
    capabilities=[NagaCapability.LEDGER],
    protocol_class="vibe_core.protocols.naga.SeshaProtocol",
)
class SeshaService(NagaBaseService, SeshaProtocol, DataProtocol):
    """
    Ananta Sesha - Trägt die Welten.

    Wraps the existing SQLiteLedger for gossip sync.
    Does NOT replace the ledger - extends it invisibly.

    INTERFACE GROUPS:
    - SeshaProtocol (domain-specific: ledger, blocks, sync)
    - DataProtocol (generic: get_hash, get_sequence, is_synced)

    OUROBOROS: Inherits NagaBaseService for self-monitoring.
    """

    def __init__(
        self,
        ledger: Optional["SQLiteLedger"] = None,
        block_size: int = 100,
    ):
        """
        Initialize Sesha.

        Args:
            ledger: The SQLiteLedger to wrap. If None, operates in degraded mode.
            block_size: Number of events per block for sync.
        """
        super().__init__(service_name="Sesha")
        self._ledger = ledger
        self._block_size = block_size
        self._events_processed = 0
        self._errors = 0
        self._last_heartbeat = datetime.now()

        logger.info("🐍 SESHA initialized - The Foundation holds")

    def inject_ledger(self, ledger: "SQLiteLedger") -> None:
        """Inject ledger after construction (for lazy init)."""
        self._ledger = ledger
        logger.debug("SESHA: Ledger injected")

    # =========================================================================
    # Ledger Wrapper Methods
    # =========================================================================

    def get_top_hash(self) -> str:
        """Get the hash of the latest ledger state."""
        if not self._ledger:
            return ""
        try:
            return self._ledger.get_top_hash()
        except Exception as e:
            logger.error(f"SESHA: get_top_hash failed: {e}")
            self._errors += 1
            return ""

    def get_sequence(self) -> int:
        """Get the current sequence number (event count)."""
        if not self._ledger:
            return 0
        try:
            return self._ledger.count_events()
        except Exception as e:
            logger.error(f"SESHA: get_sequence failed: {e}")
            self._errors += 1
            return 0

    # =========================================================================
    # DataProtocol Implementation (Interface Group - Seva for Prahlad)
    # =========================================================================

    def get_hash(self) -> str:
        """Get current state hash (DataProtocol - Foundation for Prahlad)."""
        return self.get_top_hash()

    def is_synced(self) -> bool:
        """Check if data is synchronized (DataProtocol)."""
        if not self._ledger:
            return False
        try:
            # Synced if ledger exists and has no errors
            return self._errors == 0 and self.get_sequence() > 0
        except Exception:
            return False

    # =========================================================================
    # Events API
    # =========================================================================

    def get_events_since(self, sequence: int) -> List[Dict[str, str]]:
        """Get all events since a sequence number."""
        if not self._ledger:
            return []
        try:
            events = self._ledger.get_events_since(sequence)
            self._events_processed += len(events)
            return events
        except Exception as e:
            logger.error(f"SESHA: get_events_since failed: {e}")
            self._errors += 1
            return []

    # =========================================================================
    # Gossip Sync Protocol
    # =========================================================================

    @naga_governed(operation="export_blocks")
    def export_blocks(self, since: int = 0, limit: int = 100) -> List[LedgerBlock]:
        """Export blocks for gossip to peers."""
        if not self._ledger:
            return []

        try:
            events = self.get_events_since(since)
            if not events:
                return []

            blocks = []
            prev_hash = self._get_hash_at_sequence(since)

            for i in range(0, len(events), self._block_size):
                chunk = events[i : i + self._block_size]
                if not chunk:
                    continue

                block_content = str(chunk) + prev_hash
                block_hash = hashlib.sha256(block_content.encode()).hexdigest()

                block = LedgerBlock(
                    sequence=since + i + len(chunk),
                    events=chunk,
                    hash=block_hash,
                    prev_hash=prev_hash,
                    timestamp=datetime.now(),
                )
                blocks.append(block)
                prev_hash = block_hash

                if len(blocks) >= limit:
                    break

            logger.debug(f"SESHA: Exported {len(blocks)} blocks ({len(events)} events)")
            return blocks

        except Exception as e:
            logger.error(f"SESHA: export_blocks failed: {e}")
            self._errors += 1
            return []

    @naga_governed(operation="import_blocks")
    def import_blocks(self, blocks: List[LedgerBlock]) -> ImportResult:
        """Import blocks received from a peer."""
        if not self._ledger:
            return ImportResult(success=False, message="No ledger available")

        if not blocks:
            return ImportResult(success=True, blocks_imported=0, message="No blocks to import")

        try:
            my_hash = self.get_top_hash()
            my_sequence = self.get_sequence()

            first_block = blocks[0]
            if first_block.prev_hash != my_hash and my_sequence > 0:
                if first_block.sequence <= my_sequence:
                    return ImportResult(
                        success=False,
                        message="Already have these blocks",
                        final_sequence=my_sequence,
                        final_hash=my_hash,
                    )
                return ImportResult(
                    success=False,
                    message=f"Chain gap: expected prev_hash {my_hash[:8]}...",
                    conflicts=[f"gap_at_{my_sequence}"],
                )

            # Validate chain
            prev = first_block.prev_hash
            for block in blocks:
                if block.prev_hash != prev:
                    return ImportResult(
                        success=False,
                        message=f"Broken chain at sequence {block.sequence}",
                    )
                expected = hashlib.sha256((str(block.events) + prev).encode()).hexdigest()
                if block.hash != expected:
                    return ImportResult(
                        success=False,
                        message=f"Invalid hash at sequence {block.sequence}",
                    )
                prev = block.hash

            # Import events
            imported = 0
            for block in blocks:
                for event in block.events:
                    try:
                        self._ledger.record_event(
                            event_type=event.get("event_type", "SYNC_IMPORT"),
                            agent_id=event.get("agent_id", "sesha"),
                            details=event.get("details", {}),
                            result=event.get("result"),
                            task_id=event.get("task_id"),
                            error=event.get("error"),
                        )
                        imported += 1
                    except Exception as e:
                        logger.warning(f"SESHA: Failed to import event: {e}")

            self._events_processed += imported
            logger.info(f"SESHA: Imported {imported} events from {len(blocks)} blocks")

            return ImportResult(
                success=True,
                blocks_imported=len(blocks),
                final_sequence=self.get_sequence(),
                final_hash=self.get_top_hash(),
                message=f"Imported {imported} events",
            )

        except Exception as e:
            logger.error(f"SESHA: import_blocks failed: {e}")
            self._errors += 1
            return ImportResult(success=False, message=str(e))

    def request_sync(self, peer_hash: str, peer_sequence: int) -> SyncRequest:
        """Initiate sync with a peer."""
        my_hash = self.get_top_hash()
        my_sequence = self.get_sequence()

        if my_hash == peer_hash:
            return SyncRequest(
                my_hash=my_hash,
                my_sequence=my_sequence,
                peer_hash=peer_hash,
                status=SyncStatus.SYNCHRONIZED,
            )

        if my_sequence < peer_sequence:
            return SyncRequest(
                my_hash=my_hash,
                my_sequence=my_sequence,
                peer_hash=peer_hash,
                status=SyncStatus.NEED_SYNC,
            )

        if my_sequence > peer_sequence:
            return SyncRequest(
                my_hash=my_hash,
                my_sequence=my_sequence,
                peer_hash=peer_hash,
                status=SyncStatus.NEED_SYNC,
            )

        return SyncRequest(
            my_hash=my_hash,
            my_sequence=my_sequence,
            peer_hash=peer_hash,
            status=SyncStatus.CONFLICT,
        )

    def _get_hash_at_sequence(self, sequence: int) -> str:
        """Get hash at a specific sequence (or genesis hash if 0)."""
        if sequence <= 0:
            return "0" * 64
        if sequence >= self.get_sequence():
            return self.get_top_hash()
        return "0" * 64  # Fallback

    # =========================================================================
    # CorrectionHandler Interface
    # =========================================================================

    def as_handler(self) -> Callable:
        """Get this NAGA as a CorrectionHandler for DriftSource.STATE."""

        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            self._last_heartbeat = datetime.now()

            if drift.source != DriftSource.STATE:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="sesha",
                    message=f"Not a STATE drift: {drift.source}",
                )

            if strategy == HealingStrategy.DRY_RUN:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.DEFERRED,
                    handler_id="sesha",
                    message="Sync requires peer connection (DRY_RUN)",
                )

            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.DEFERRED,
                handler_id="sesha",
                message="Sync pending peer connection",
            )

        return handler

    @naga_governed(operation="detect_drift")
    def detect_drift(self) -> List[UnifiedDriftReport]:
        """Detect STATE drift via ledger integrity check."""
        if not self._ledger:
            return []

        reports = []
        try:
            integrity = self._ledger.verify_chain_integrity()
            if integrity.get("corrupted"):
                reports.append(
                    UnifiedDriftReport(
                        id=f"sesha_integrity_{datetime.now().timestamp()}",
                        source=DriftSource.STATE,
                        severity=DriftSeverity.CRITICAL,
                        message="Ledger chain integrity compromised",
                        detector_id="sesha",
                        auto_healable=False,
                        requires_approval=True,
                        raw_data=integrity,
                    )
                )
        except Exception as e:
            logger.error(f"SESHA: detect_drift failed: {e}")
            self._errors += 1

        return reports

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        return NagaStatus(
            naga_type=NagaType.SESHA,
            healthy=self._ledger is not None and self._errors < 10,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._events_processed,
            errors=self._errors,
            message=f"seq={self.get_sequence()}, hash={self.get_top_hash()[:8]}...",
        )
