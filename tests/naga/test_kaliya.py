"""
Tests for KALIYA Service - The Quarantine Agent.

Mythology: Krishna banished Kaliya to the ocean - isolated but alive.
The footprints on Kaliya's hoods protect him from Garuda.

Purpose: Isolate misbehaving components WITHOUT killing them.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.services.kaliya import KaliyaService, QuarantineRecord
from vibe_core.state.state_service import get_state_service, reset_state_service


@pytest.fixture
def state_service(temp_dir):
    """Provide a real StateService pointed at a temp directory."""
    reset_state_service()
    return get_state_service(workspace=temp_dir)


@pytest.fixture
def kaliya(state_service):
    """Provide a KaliyaService with real state persistence."""
    return KaliyaService(state_service=state_service)


class TestKaliyaBasics:
    """Test basic Kaliya initialization and status."""

    def test_initialization(self, kaliya):
        assert kaliya._quarantined_count == 0
        assert kaliya._errors == 0
        assert len(kaliya._quarantine_registry) == 0

    def test_get_status(self, kaliya):
        status = kaliya.get_status()

        assert status.naga_type.value == "kaliya"
        assert status.healthy is True
        assert status.events_processed == 0


class TestQuarantineOperations:
    """Test quarantine and release operations."""

    def test_quarantine_component(self, kaliya):
        record = kaliya.quarantine(
            component_id="bad_agent_001",
            reason="Excessive violations",
        )

        assert record.component_id == "bad_agent_001"
        assert record.reason == "Excessive violations"
        assert record.started_at is not None
        assert kaliya._quarantined_count == 1

    def test_is_quarantined_returns_true(self, kaliya):
        kaliya.quarantine("test_component", "testing")

        assert kaliya.is_quarantined("test_component") is True
        assert kaliya.is_quarantined("other_component") is False

    def test_release_from_quarantine(self, kaliya):
        kaliya.quarantine("test_component", "testing")

        assert kaliya.is_quarantined("test_component") is True

        kaliya.release("test_component")

        assert kaliya.is_quarantined("test_component") is False

    def test_quarantine_duration_expires(self, state_service):
        # We need a new instance with short duration for this specific test
        kaliya = KaliyaService(state_service=state_service, default_duration_seconds=0.1)
        kaliya.quarantine("test_component", "testing")

        assert kaliya.is_quarantined("test_component") is True

        import time

        time.sleep(0.15)

        assert kaliya.is_quarantined("test_component") is False


class TestQuarantineRecord:
    """Test QuarantineRecord functionality."""

    def test_record_has_required_fields(self, kaliya):
        record = kaliya.quarantine("comp_123", "bad behavior")

        assert hasattr(record, "component_id")
        assert hasattr(record, "reason")
        assert hasattr(record, "started_at")
        assert hasattr(record, "duration_seconds")
        assert hasattr(record, "violation_count")

    def test_record_is_expired(self):
        # Pure data test, no service needed
        record = QuarantineRecord(
            component_id="test",
            reason="test",
            started_at=datetime.now() - timedelta(seconds=100),
            duration_seconds=10,
        )

        assert record.is_expired() is True

    def test_record_not_expired(self):
        # Pure data test
        record = QuarantineRecord(
            component_id="test",
            reason="test",
            started_at=datetime.now(),
            duration_seconds=3600,
        )

        assert record.is_expired() is False


class TestViolationTracking:
    """Test violation counting before quarantine."""

    def test_record_violation_increments_count(self, kaliya):
        kaliya.record_violation("comp_001")
        kaliya.record_violation("comp_001")
        kaliya.record_violation("comp_001")

        assert kaliya.get_violation_count("comp_001") == 3

    def test_auto_quarantine_on_threshold(self, state_service):
        kaliya = KaliyaService(state_service=state_service, violation_threshold=3)

        kaliya.record_violation("comp_001")
        kaliya.record_violation("comp_001")

        assert kaliya.is_quarantined("comp_001") is False

        kaliya.record_violation("comp_001")  # Third violation

        assert kaliya.is_quarantined("comp_001") is True

    def test_violations_reset_after_quarantine(self, state_service):
        kaliya = KaliyaService(state_service=state_service, violation_threshold=2)

        kaliya.record_violation("comp_001")
        kaliya.record_violation("comp_001")  # Auto-quarantine

        assert kaliya.is_quarantined("comp_001") is True

        kaliya.release("comp_001")

        assert kaliya.get_violation_count("comp_001") == 0


class TestEscalation:
    """Test escalation to sovereign (37th)."""

    def test_escalate_after_repeated_quarantines(self, state_service):
        kaliya = KaliyaService(
            state_service=state_service,
            violation_threshold=1,
            escalation_threshold=3,
        )

        # Three quarantine cycles - but 3rd triggers escalation so can't release
        kaliya.record_violation("bad_comp")  # Quarantine 1
        kaliya.release("bad_comp")
        kaliya.record_violation("bad_comp")  # Quarantine 2
        kaliya.release("bad_comp")
        kaliya.record_violation("bad_comp")  # Quarantine 3 → escalation

        # Should be escalated now
        assert kaliya.is_escalated("bad_comp") is True

    def test_escalated_component_cannot_be_released(self, state_service):
        kaliya = KaliyaService(state_service=state_service, violation_threshold=1, escalation_threshold=2)

        kaliya.record_violation("bad_comp")
        kaliya.release("bad_comp")
        kaliya.record_violation("bad_comp")  # Second quarantine → escalation

        assert kaliya.is_escalated("bad_comp") is True

        # Try to release - should fail
        with pytest.raises(Exception, match="escalated"):
            kaliya.release("bad_comp")


class TestSignedQuarantine:
    """Test that quarantine records are signed (37th Principle)."""

    def test_quarantine_record_is_signed(self, state_service):
        from vibe_core.naga.identity import NagaIdentity

        identity = NagaIdentity.generate(agent_id="kaliya_test")
        kaliya = KaliyaService(identity=identity, state_service=state_service)

        record = kaliya.quarantine("comp_001", "testing")

        assert record.signer_id == "kaliya_test"
        assert record.signature is not None


class TestCortexIntegration:
    """Test integration with NagaCortex."""

    def test_notify_cortex_on_quarantine(self, state_service):
        mock_cortex = MagicMock()
        kaliya = KaliyaService(cortex=mock_cortex, state_service=state_service)

        kaliya.quarantine("comp_001", "testing")

        mock_cortex.receive_kaliya_event.assert_called_once()

    def test_notify_cortex_on_escalation(self, state_service):
        mock_cortex = MagicMock()
        kaliya = KaliyaService(
            cortex=mock_cortex,
            state_service=state_service,
            violation_threshold=1,
            escalation_threshold=1,
        )

        kaliya.record_violation("comp_001")  # Quarantine + escalate

        # Should have received both quarantine and escalation events
        assert mock_cortex.receive_kaliya_event.call_count >= 1


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
