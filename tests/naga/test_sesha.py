"""
Tests for SeshaService - Der Träger der Welten.

Ananta Sesha - The FOUNDATION. The serpent on which Vishnu rests.

"Truth is purely additive."

This is the FOUNDATION's test suite. Every other NAGA depends on Sesha.
If Sesha fails, the world falls.

Tests:
- Ledger wrapper (get_top_hash, get_sequence, get_events_since)
- Block export/import for gossip sync
- Chain validation and conflict detection
- CorrectionHandler interface for STATE drift
- Degraded mode (no ledger)
- Error resilience
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.services.sesha import SeshaService
from vibe_core.protocols.correction import (
    DriftSeverity,
    DriftSource,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga import (
    ImportResult,
    LedgerBlock,
    NagaType,
    SyncStatus,
)

# =============================================================================
# Fixtures
# =============================================================================


class MockLedger:
    """Mock SQLiteLedger for testing Sesha without database."""

    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        self._fail_next = False
        self._integrity_result = {"corrupted": False, "total": 0, "valid": 0}

    def get_top_hash(self) -> str:
        """Get hash of latest event."""
        if self._fail_next:
            self._fail_next = False
            raise RuntimeError("Simulated ledger failure")
        if not self._events:
            return "0" * 64
        content = str(self._events[-1])
        return hashlib.sha256(content.encode()).hexdigest()

    def count_events(self) -> int:
        """Count total events."""
        if self._fail_next:
            self._fail_next = False
            raise RuntimeError("Simulated ledger failure")
        return len(self._events)

    def get_events_since(self, sequence: int) -> List[Dict[str, Any]]:
        """Get events since sequence."""
        if self._fail_next:
            self._fail_next = False
            raise RuntimeError("Simulated ledger failure")
        return self._events[sequence:]

    def record_event(
        self,
        event_type: str,
        agent_id: str,
        details: Dict[str, Any],
        result: Optional[str] = None,
        task_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> str:
        """Record an event to ledger."""
        event_id = f"EVT-{len(self._events) + 1:06d}"
        self._events.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "agent_id": agent_id,
                "details": details,
                "result": result,
                "task_id": task_id,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return event_id

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify chain integrity."""
        return self._integrity_result

    def simulate_failure(self):
        """Make next call fail."""
        self._fail_next = True

    def set_integrity(self, corrupted: bool):
        """Set integrity check result."""
        self._integrity_result = {
            "corrupted": corrupted,
            "total": len(self._events),
            "valid": 0 if corrupted else len(self._events),
        }


@pytest.fixture
def mock_ledger():
    """Fresh mock ledger."""
    return MockLedger()


@pytest.fixture
def sesha(mock_ledger):
    """Sesha with mock ledger."""
    return SeshaService(ledger=mock_ledger, block_size=10)


@pytest.fixture
def sesha_no_ledger():
    """Sesha without ledger - degraded mode."""
    return SeshaService(ledger=None)


# =============================================================================
# Initialization Tests
# =============================================================================


class TestInitialization:
    """Test Sesha initialization."""

    def test_init_with_ledger(self, sesha, mock_ledger):
        """Should initialize with ledger."""
        assert sesha._ledger is mock_ledger
        assert sesha._block_size == 10
        assert sesha._events_processed == 0
        assert sesha._errors == 0

    def test_init_without_ledger(self, sesha_no_ledger):
        """Should initialize in degraded mode without ledger."""
        assert sesha_no_ledger._ledger is None
        status = sesha_no_ledger.get_status()
        assert status.healthy is False

    def test_inject_ledger(self, sesha_no_ledger, mock_ledger):
        """Should allow ledger injection after construction."""
        assert sesha_no_ledger._ledger is None
        sesha_no_ledger.inject_ledger(mock_ledger)
        assert sesha_no_ledger._ledger is mock_ledger

    def test_default_block_size(self, mock_ledger):
        """Should use default block size of 100."""
        sesha = SeshaService(ledger=mock_ledger)
        assert sesha._block_size == 100


# =============================================================================
# Ledger Wrapper Tests
# =============================================================================


class TestLedgerWrapper:
    """Test ledger wrapping methods."""

    def test_get_top_hash_returns_ledger_hash(self, sesha, mock_ledger):
        """Should return ledger's top hash."""
        mock_ledger.record_event("TEST", "agent", {"test": True})
        expected = mock_ledger.get_top_hash()
        assert sesha.get_top_hash() == expected

    def test_get_top_hash_empty_ledger(self, sesha):
        """Should return genesis hash for empty ledger."""
        result = sesha.get_top_hash()
        assert result == "0" * 64

    def test_get_top_hash_no_ledger(self, sesha_no_ledger):
        """Should return empty string without ledger."""
        assert sesha_no_ledger.get_top_hash() == ""

    def test_get_top_hash_handles_error(self, sesha, mock_ledger):
        """Should handle ledger error gracefully."""
        mock_ledger.simulate_failure()
        result = sesha.get_top_hash()
        assert result == ""
        assert sesha._errors == 1

    def test_get_sequence_returns_count(self, sesha, mock_ledger):
        """Should return event count as sequence."""
        mock_ledger.record_event("TEST", "agent", {})
        mock_ledger.record_event("TEST", "agent", {})
        assert sesha.get_sequence() == 2

    def test_get_sequence_empty_ledger(self, sesha):
        """Should return 0 for empty ledger."""
        assert sesha.get_sequence() == 0

    def test_get_sequence_no_ledger(self, sesha_no_ledger):
        """Should return 0 without ledger."""
        assert sesha_no_ledger.get_sequence() == 0

    def test_get_sequence_handles_error(self, sesha, mock_ledger):
        """Should handle ledger error gracefully."""
        mock_ledger.simulate_failure()
        result = sesha.get_sequence()
        assert result == 0
        assert sesha._errors == 1

    def test_get_events_since(self, sesha, mock_ledger):
        """Should return events since sequence."""
        for i in range(5):
            mock_ledger.record_event("TEST", f"agent_{i}", {"index": i})

        events = sesha.get_events_since(2)
        assert len(events) == 3
        assert events[0]["details"]["index"] == 2
        assert sesha._events_processed == 3

    def test_get_events_since_empty(self, sesha):
        """Should return empty list for empty ledger."""
        events = sesha.get_events_since(0)
        assert events == []

    def test_get_events_since_no_ledger(self, sesha_no_ledger):
        """Should return empty list without ledger."""
        assert sesha_no_ledger.get_events_since(0) == []

    def test_get_events_since_handles_error(self, sesha, mock_ledger):
        """Should handle ledger error gracefully."""
        mock_ledger.simulate_failure()
        result = sesha.get_events_since(0)
        assert result == []
        assert sesha._errors == 1


# =============================================================================
# Block Export Tests
# =============================================================================


class TestBlockExport:
    """Test block export for gossip sync."""

    def test_export_creates_valid_blocks(self, sesha, mock_ledger):
        """Should create blocks with correct structure."""
        for i in range(15):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        blocks = sesha.export_blocks(since=0)

        assert len(blocks) == 2  # 15 events / 10 per block = 2 blocks
        assert all(isinstance(b, LedgerBlock) for b in blocks)
        assert blocks[0].prev_hash == "0" * 64  # Genesis

    def test_export_chains_blocks_correctly(self, sesha, mock_ledger):
        """Should chain blocks with prev_hash -> hash."""
        for i in range(25):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        blocks = sesha.export_blocks(since=0)

        # Verify chain: each block's prev_hash equals previous block's hash
        for i in range(1, len(blocks)):
            assert blocks[i].prev_hash == blocks[i - 1].hash

    def test_export_respects_limit(self, sesha, mock_ledger):
        """Should respect block limit."""
        for i in range(100):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        blocks = sesha.export_blocks(since=0, limit=3)
        assert len(blocks) == 3

    def test_export_from_sequence(self, sesha, mock_ledger):
        """Should export from specific sequence."""
        for i in range(20):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        blocks = sesha.export_blocks(since=10)

        # Should have 10 events in 1 block
        assert len(blocks) == 1
        assert len(blocks[0].events) == 10

    def test_export_empty_ledger(self, sesha):
        """Should return empty list for empty ledger."""
        blocks = sesha.export_blocks()
        assert blocks == []

    def test_export_no_ledger(self, sesha_no_ledger):
        """Should return empty list without ledger."""
        assert sesha_no_ledger.export_blocks() == []

    def test_export_handles_error(self, sesha, mock_ledger):
        """Should handle export error gracefully."""
        mock_ledger.record_event("TEST", "agent", {})
        mock_ledger.simulate_failure()

        result = sesha.export_blocks()
        assert result == []
        assert sesha._errors >= 1


# =============================================================================
# Block Import Tests
# =============================================================================


class TestBlockImport:
    """Test block import from peers."""

    def _create_valid_block(self, events: List[Dict], prev_hash: str, sequence: int) -> LedgerBlock:
        """Create a valid block for testing."""
        block_content = str(events) + prev_hash
        block_hash = hashlib.sha256(block_content.encode()).hexdigest()
        return LedgerBlock(
            sequence=sequence,
            events=events,
            hash=block_hash,
            prev_hash=prev_hash,
            timestamp=datetime.now(),
        )

    def test_import_empty_blocks(self, sesha):
        """Should handle empty block list."""
        result = sesha.import_blocks([])
        assert result.success is True
        assert result.blocks_imported == 0

    def test_import_no_ledger(self, sesha_no_ledger):
        """Should fail without ledger."""
        block = self._create_valid_block([{"event_type": "TEST", "agent_id": "test"}], "0" * 64, 1)
        result = sesha_no_ledger.import_blocks([block])
        assert result.success is False

    def test_import_valid_blocks(self, sesha, mock_ledger):
        """Should import valid blocks."""
        events = [{"event_type": "TEST", "agent_id": "test", "details": {"i": i}} for i in range(5)]
        block = self._create_valid_block(events, "0" * 64, 5)

        result = sesha.import_blocks([block])

        assert result.success is True
        assert result.blocks_imported == 1

    def test_import_validates_chain(self, sesha, mock_ledger):
        """Should reject broken chain."""
        events1 = [{"event_type": "TEST", "agent_id": "test"}]
        events2 = [{"event_type": "TEST", "agent_id": "test"}]

        block1 = self._create_valid_block(events1, "0" * 64, 1)
        block2 = self._create_valid_block(events2, "wrong_hash", 2)  # Bad prev_hash

        result = sesha.import_blocks([block1, block2])
        assert result.success is False
        assert "Broken chain" in result.message

    def test_import_validates_hash(self, sesha, mock_ledger):
        """Should reject invalid hash."""
        events = [{"event_type": "TEST", "agent_id": "test"}]
        block = LedgerBlock(
            sequence=1,
            events=events,
            hash="invalid_hash",  # Wrong hash
            prev_hash="0" * 64,
            timestamp=datetime.now(),
        )

        result = sesha.import_blocks([block])
        assert result.success is False
        assert "Invalid hash" in result.message

    def test_import_detects_gap(self, sesha, mock_ledger):
        """Should detect chain gap."""
        # First add some events to ledger
        for i in range(5):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        # Try to import block that doesn't connect
        events = [{"event_type": "TEST", "agent_id": "test"}]
        block = self._create_valid_block(events, "wrong_prev_hash", 10)

        result = sesha.import_blocks([block])
        assert result.success is False
        assert "gap" in result.message.lower() or "already" in result.message.lower()

    def test_import_records_events(self, sesha, mock_ledger):
        """Should record imported events to ledger."""
        events = [
            {"event_type": "SYNC_TEST", "agent_id": "peer", "details": {"test": True}},
            {"event_type": "SYNC_TEST", "agent_id": "peer", "details": {"test": False}},
        ]
        block = self._create_valid_block(events, "0" * 64, 2)

        initial_count = mock_ledger.count_events()
        sesha.import_blocks([block])

        assert mock_ledger.count_events() == initial_count + 2


# =============================================================================
# Sync Protocol Tests
# =============================================================================


class TestSyncProtocol:
    """Test sync request protocol."""

    def test_sync_synchronized(self, sesha, mock_ledger):
        """Should return SYNCHRONIZED when hashes match."""
        mock_ledger.record_event("TEST", "agent", {})
        my_hash = sesha.get_top_hash()
        my_seq = sesha.get_sequence()

        request = sesha.request_sync(peer_hash=my_hash, peer_sequence=my_seq)

        assert request.status == SyncStatus.SYNCHRONIZED
        assert request.my_hash == my_hash

    def test_sync_need_sync_behind(self, sesha, mock_ledger):
        """Should return NEED_SYNC when behind peer."""
        mock_ledger.record_event("TEST", "agent", {})

        request = sesha.request_sync(peer_hash="different_hash", peer_sequence=10)

        assert request.status == SyncStatus.NEED_SYNC
        assert request.my_sequence < 10

    def test_sync_need_sync_ahead(self, sesha, mock_ledger):
        """Should return NEED_SYNC when ahead of peer."""
        for i in range(10):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        request = sesha.request_sync(peer_hash="different_hash", peer_sequence=2)

        assert request.status == SyncStatus.NEED_SYNC
        assert request.my_sequence > 2

    def test_sync_conflict(self, sesha, mock_ledger):
        """Should return CONFLICT when same sequence but different hash."""
        for i in range(5):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        request = sesha.request_sync(peer_hash="different_hash", peer_sequence=5)

        assert request.status == SyncStatus.CONFLICT


# =============================================================================
# CorrectionHandler Tests
# =============================================================================


class TestCorrectionHandler:
    """Test CorrectionHandler interface."""

    def test_as_handler_returns_callable(self, sesha):
        """Should return handler function."""
        handler = sesha.as_handler()
        assert callable(handler)

    def test_handler_skips_non_state_drift(self, sesha):
        """Should skip non-STATE drift."""
        handler = sesha.as_handler()

        drift = UnifiedDriftReport(
            id="test-drift",
            source=DriftSource.CONFIG,  # Not STATE
            severity=DriftSeverity.WARNING,
            message="Config drift",
            detector_id="test",
        )

        result = handler(drift, HealingStrategy.AUTO)
        assert result.status == HealingStatus.SKIPPED

    def test_handler_defers_state_drift(self, sesha):
        """Should defer STATE drift (needs peer connection)."""
        handler = sesha.as_handler()

        drift = UnifiedDriftReport(
            id="test-drift",
            source=DriftSource.STATE,
            severity=DriftSeverity.WARNING,
            message="State drift",
            detector_id="test",
        )

        result = handler(drift, HealingStrategy.AUTO)
        assert result.status == HealingStatus.DEFERRED

    def test_handler_dry_run(self, sesha):
        """Should return DEFERRED for dry run."""
        handler = sesha.as_handler()

        drift = UnifiedDriftReport(
            id="test-drift",
            source=DriftSource.STATE,
            severity=DriftSeverity.WARNING,
            message="State drift",
            detector_id="test",
        )

        result = handler(drift, HealingStrategy.DRY_RUN)
        assert result.status == HealingStatus.DEFERRED


# =============================================================================
# Drift Detection Tests
# =============================================================================


class TestDriftDetection:
    """Test drift detection via ledger integrity."""

    def test_detect_no_drift_healthy_ledger(self, sesha, mock_ledger):
        """Should return no drift for healthy ledger."""
        mock_ledger.set_integrity(corrupted=False)

        reports = sesha.detect_drift()
        assert reports == []

    def test_detect_drift_corrupted_ledger(self, sesha, mock_ledger):
        """Should detect drift when ledger corrupted."""
        mock_ledger.set_integrity(corrupted=True)

        reports = sesha.detect_drift()

        assert len(reports) == 1
        assert reports[0].source == DriftSource.STATE
        assert reports[0].severity == DriftSeverity.CRITICAL

    def test_detect_drift_no_ledger(self, sesha_no_ledger):
        """Should return empty for no ledger."""
        reports = sesha_no_ledger.detect_drift()
        assert reports == []


# =============================================================================
# Status Tests
# =============================================================================


class TestStatus:
    """Test NAGA status reporting."""

    def test_status_healthy_with_ledger(self, sesha, mock_ledger):
        """Should be healthy with ledger and low errors."""
        mock_ledger.record_event("TEST", "agent", {})

        status = sesha.get_status()

        assert status.naga_type == NagaType.SESHA
        assert status.healthy is True
        assert "seq=" in status.message
        assert "hash=" in status.message

    def test_status_unhealthy_no_ledger(self, sesha_no_ledger):
        """Should be unhealthy without ledger."""
        status = sesha_no_ledger.get_status()
        assert status.healthy is False

    def test_status_unhealthy_many_errors(self, sesha, mock_ledger):
        """Should be unhealthy with many errors."""
        sesha._errors = 15

        status = sesha.get_status()
        assert status.healthy is False

    def test_status_tracks_events_processed(self, sesha, mock_ledger):
        """Should track events processed."""
        for i in range(5):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        sesha.get_events_since(0)  # Process events

        status = sesha.get_status()
        assert status.events_processed == 5

    def test_status_tracks_errors(self, sesha, mock_ledger):
        """Should track errors."""
        mock_ledger.simulate_failure()
        sesha.get_top_hash()  # Trigger error

        status = sesha.get_status()
        assert status.errors == 1


# =============================================================================
# Error Resilience Tests
# =============================================================================


class TestErrorResilience:
    """Test error handling and resilience."""

    def test_survives_ledger_errors(self, sesha, mock_ledger):
        """Should survive multiple ledger errors."""
        for _ in range(5):
            mock_ledger.simulate_failure()
            sesha.get_top_hash()
            mock_ledger.simulate_failure()
            sesha.get_sequence()
            mock_ledger.simulate_failure()
            sesha.get_events_since(0)

        # Should still be functional
        mock_ledger.record_event("TEST", "agent", {})
        assert sesha.get_sequence() == 1
        assert sesha._errors == 15

    def test_error_does_not_leak(self, sesha, mock_ledger):
        """Errors should not propagate to caller."""
        mock_ledger.simulate_failure()

        # Should not raise
        result = sesha.get_top_hash()
        assert result == ""

    def test_degraded_mode_safe(self, sesha_no_ledger):
        """Should be safe in degraded mode."""
        # All these should return safe defaults, not raise
        assert sesha_no_ledger.get_top_hash() == ""
        assert sesha_no_ledger.get_sequence() == 0
        assert sesha_no_ledger.get_events_since(0) == []
        assert sesha_no_ledger.export_blocks() == []
        assert sesha_no_ledger.detect_drift() == []


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_large_event_count(self, sesha, mock_ledger):
        """Should handle large number of events."""
        for i in range(1000):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        assert sesha.get_sequence() == 1000

        blocks = sesha.export_blocks(since=0, limit=100)
        assert len(blocks) == 100

    def test_empty_event_details(self, sesha, mock_ledger):
        """Should handle events with empty details."""
        mock_ledger.record_event("TEST", "agent", {})

        events = sesha.get_events_since(0)
        assert len(events) == 1
        assert events[0]["details"] == {}

    def test_special_characters_in_events(self, sesha, mock_ledger):
        """Should handle special characters in events."""
        mock_ledger.record_event(
            "TEST",
            "agent",
            {
                "unicode": "🐍 Sesha",
                "quotes": '"quoted"',
                "newlines": "line1\nline2",
            },
        )

        events = sesha.get_events_since(0)
        assert "🐍" in events[0]["details"]["unicode"]

    def test_hash_at_sequence_boundaries(self, sesha, mock_ledger):
        """Test hash retrieval at sequence boundaries."""
        for i in range(5):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        # Sequence 0 returns genesis hash
        assert sesha._get_hash_at_sequence(0) == "0" * 64

        # Negative sequence returns genesis hash
        assert sesha._get_hash_at_sequence(-1) == "0" * 64

        # Beyond sequence returns top hash
        assert sesha._get_hash_at_sequence(100) == sesha.get_top_hash()


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Test integration scenarios."""

    def test_export_import_roundtrip(self, mock_ledger):
        """Exported blocks should be importable by another Sesha."""
        # Sesha A creates events
        sesha_a = SeshaService(ledger=mock_ledger, block_size=5)
        for i in range(15):
            mock_ledger.record_event("TEST", "agent_a", {"i": i})

        # Export blocks
        blocks = sesha_a.export_blocks(since=0)
        assert len(blocks) == 3

        # Sesha B imports blocks
        ledger_b = MockLedger()
        sesha_b = SeshaService(ledger=ledger_b, block_size=5)

        result = sesha_b.import_blocks(blocks)
        assert result.success is True
        assert ledger_b.count_events() == 15

    def test_sync_flow(self, mock_ledger):
        """Test full sync flow between two Seshas."""
        # Sesha A has more events
        sesha_a = SeshaService(ledger=mock_ledger, block_size=10)
        for i in range(20):
            mock_ledger.record_event("TEST", "agent", {"i": i})

        # Sesha B is behind
        ledger_b = MockLedger()
        sesha_b = SeshaService(ledger=ledger_b, block_size=10)

        # B requests sync status
        request = sesha_b.request_sync(peer_hash=sesha_a.get_top_hash(), peer_sequence=sesha_a.get_sequence())
        assert request.status == SyncStatus.NEED_SYNC

        # A exports blocks for B
        blocks = sesha_a.export_blocks(since=request.my_sequence)

        # B imports blocks
        result = sesha_b.import_blocks(blocks)
        assert result.success is True

        # B should now be synchronized
        final_request = sesha_b.request_sync(peer_hash=sesha_a.get_top_hash(), peer_sequence=sesha_a.get_sequence())
        # Note: Won't be SYNCHRONIZED because B's hash is different
        # (events recorded differently), but sequence matches
        assert final_request.my_sequence == sesha_a.get_sequence()
