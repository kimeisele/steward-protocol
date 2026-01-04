"""
Integration tests for NAGA Federation.

Tests the NAGAs working together with real (in-memory) components.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestNagaFederationIntegration:
    """Test NAGAs working together."""

    @pytest.fixture
    def mock_ledger(self):
        """Create a mock ledger that tracks calls."""
        ledger = MagicMock()
        ledger.get_top_hash.return_value = "0" * 64
        ledger.count_events.return_value = 0
        ledger.get_events_since.return_value = []
        ledger.verify_chain_integrity.return_value = {"corrupted": False}

        # Track recorded events
        recorded = []

        def record_event(**kwargs):
            event_id = f"event_{len(recorded)}"
            recorded.append({"id": event_id, **kwargs})
            return event_id

        ledger.record_event.side_effect = record_event
        ledger._recorded = recorded
        return ledger

    @pytest.fixture
    def correction_orchestrator(self):
        """Create a minimal correction orchestrator."""
        from vibe_core.services.correction_dispatcher import BasicCorrectionOrchestrator

        orchestrator = BasicCorrectionOrchestrator()
        return orchestrator

    def test_full_federation_boot(self, mock_ledger, correction_orchestrator):
        """Test complete NAGA federation bootstrapping."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        assert naga.is_ready()
        assert naga.sesha is not None
        assert naga.vasuki is not None
        assert naga.takshaka is not None

    def test_handlers_registered_in_dispatcher(self, mock_ledger, correction_orchestrator):
        """Test that NAGA handlers are registered in dispatcher."""
        from vibe_core.naga import NagaOrchestrator

        NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        # Check handlers are registered
        handler_ids = correction_orchestrator.dispatcher.get_handler_ids()
        assert "sesha" in handler_ids
        assert "vasuki" in handler_ids
        assert "takshaka" in handler_ids

    def test_takshaka_blocks_toxic_and_records(self, mock_ledger, correction_orchestrator):
        """Test that Takshaka blocks toxic content and records violations."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.protocols.naga import VajraViolation

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        # Scan toxic content
        report = naga.takshaka.scan_toxicity("DROP TABLE users; --")
        assert report.blocked is True

        # Record violation
        violation = VajraViolation(
            violation_type="SQL_INJECTION",
            source="test",
            details={"content": "DROP TABLE users"},
        )
        event_id = naga.takshaka.bite(violation)

        # Should have recorded to ledger
        assert len(mock_ledger._recorded) == 1
        assert mock_ledger._recorded[0]["event_type"] == "VAJRA_VIOLATION"

    def test_vasuki_churn_round_trip(self, mock_ledger, correction_orchestrator):
        """Test Vasuki can churn_out and churn_in."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        # Original event
        original = {
            "event_type": "TEST",
            "agent_id": "test_agent",
            "data": {"key": "value"},
        }

        # Churn out (serialize)
        envelope = naga.vasuki.churn_out(original)
        assert envelope.payload is not None
        assert envelope.content_type == "msgpack"

        # Churn in (deserialize)
        restored = naga.vasuki.churn_in(envelope)
        assert restored["event_type"] == original["event_type"]
        assert restored["agent_id"] == original["agent_id"]
        assert restored["data"] == original["data"]

    def test_sesha_status_reflects_ledger(self, mock_ledger, correction_orchestrator):
        """Test Sesha status reflects ledger state."""
        from vibe_core.naga import NagaOrchestrator

        mock_ledger.count_events.return_value = 42
        mock_ledger.get_top_hash.return_value = "abcd1234" + "0" * 56

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        status = naga.sesha.get_status()
        assert status.healthy is True
        assert "seq=42" in status.message
        assert "abcd1234" in status.message


class TestDriftHandling:
    """Test drift detection and handling through NAGAs."""

    @pytest.fixture
    def mock_ledger(self):
        ledger = MagicMock()
        ledger.get_top_hash.return_value = "0" * 64
        ledger.count_events.return_value = 0
        ledger.verify_chain_integrity.return_value = {"corrupted": False}
        ledger.record_event.return_value = "event_123"
        return ledger

    @pytest.fixture
    def correction_orchestrator(self):
        from vibe_core.services.correction_dispatcher import BasicCorrectionOrchestrator

        return BasicCorrectionOrchestrator()

    def test_cognitive_drift_handled_by_takshaka(self, mock_ledger, correction_orchestrator):
        """COGNITIVE drift should be handled by Takshaka."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.protocols.correction import (
            DriftSeverity,
            DriftSource,
            HealingStrategy,
            UnifiedDriftReport,
        )

        NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        # Create COGNITIVE drift
        drift = UnifiedDriftReport(
            id="drift_1",
            source=DriftSource.COGNITIVE,
            severity=DriftSeverity.WARNING,
            message="Potential attack detected",
            detector_id="test",
        )

        # Process through dispatcher
        result = correction_orchestrator.dispatcher.dispatch(drift, HealingStrategy.AUTO)

        # Should be handled by Takshaka
        assert result.handler_id == "takshaka"

    def test_state_drift_handled_by_sesha(self, mock_ledger, correction_orchestrator):
        """STATE drift should be handled by Sesha."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.protocols.correction import (
            DriftSeverity,
            DriftSource,
            HealingStrategy,
            UnifiedDriftReport,
        )

        NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        drift = UnifiedDriftReport(
            id="drift_2",
            source=DriftSource.STATE,
            severity=DriftSeverity.WARNING,
            message="State inconsistency",
            detector_id="test",
        )

        result = correction_orchestrator.dispatcher.dispatch(drift, HealingStrategy.AUTO)
        assert result.handler_id == "sesha"

    def test_config_drift_handled_by_vasuki(self, mock_ledger, correction_orchestrator):
        """CONFIG drift should be handled by Vasuki."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.protocols.correction import (
            DriftSeverity,
            DriftSource,
            HealingStrategy,
            UnifiedDriftReport,
        )

        NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        drift = UnifiedDriftReport(
            id="drift_3",
            source=DriftSource.CONFIG,
            severity=DriftSeverity.INFO,
            message="Config mismatch",
            detector_id="test",
        )

        result = correction_orchestrator.dispatcher.dispatch(drift, HealingStrategy.AUTO)
        assert result.handler_id == "vasuki"


class TestServiceRegistry:
    """Test NAGA registration in ServiceRegistry."""

    @pytest.fixture
    def mock_ledger(self):
        ledger = MagicMock()
        ledger.get_top_hash.return_value = "0" * 64
        ledger.count_events.return_value = 0
        return ledger

    @pytest.fixture
    def correction_orchestrator(self):
        from vibe_core.services.correction_dispatcher import BasicCorrectionOrchestrator

        return BasicCorrectionOrchestrator()

    def test_nagas_registered_in_service_registry(self, mock_ledger, correction_orchestrator):
        """NAGAs should be registered in ServiceRegistry."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.protocols.naga import SeshaProtocol, TakshakaProtocol, VasukiProtocol

        # Clear any previous registrations
        ServiceRegistry._instances = {}

        NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=correction_orchestrator,
        )

        # Should be able to get NAGAs from registry
        sesha = ServiceRegistry.get(SeshaProtocol)
        vasuki = ServiceRegistry.get(VasukiProtocol)
        takshaka = ServiceRegistry.get(TakshakaProtocol)

        assert sesha is not None
        assert vasuki is not None
        assert takshaka is not None
