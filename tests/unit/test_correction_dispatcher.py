"""Tests for CorrectionDispatcher service."""

from datetime import datetime
from pathlib import Path

import pytest

from vibe_core.protocols.correction import (
    DriftSeverity,
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.services.correction_dispatcher import (
    BasicCorrectionDispatcher,
    BasicCorrectionOrchestrator,
    BasicDriftRegistry,
)


class TestBasicDriftRegistry:
    """Tests for BasicDriftRegistry."""

    def test_register_detector(self):
        """Can register a detector."""
        registry = BasicDriftRegistry()

        def mock_detector():
            return []

        registry.register_detector(DriftSource.PERFORMANCE, mock_detector, "test_detector")

        assert "test_detector" in registry.get_detector_ids()

    def test_detect_runs_registered_detectors(self):
        """Detect runs all registered detectors."""
        registry = BasicDriftRegistry()

        def mock_detector():
            return [
                UnifiedDriftReport(
                    id="test_drift_1",
                    source=DriftSource.PERFORMANCE,
                    severity=DriftSeverity.WARNING,
                    message="Test drift",
                )
            ]

        registry.register_detector(DriftSource.PERFORMANCE, mock_detector, "test")

        drifts = registry.detect_all()
        assert len(drifts) == 1
        assert drifts[0].id == "test_drift_1"
        assert drifts[0].detector_id == "test"

    def test_unregister_detector(self):
        """Can unregister a detector."""
        registry = BasicDriftRegistry()

        def mock_detector():
            return []

        registry.register_detector(DriftSource.PERFORMANCE, mock_detector, "test")
        assert registry.unregister_detector("test")
        assert "test" not in registry.get_detector_ids()


class TestBasicCorrectionDispatcher:
    """Tests for BasicCorrectionDispatcher."""

    def test_register_handler(self):
        """Can register a handler."""
        dispatcher = BasicCorrectionDispatcher()

        def mock_handler(drift, strategy):
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.HEALED,
                handler_id="mock",
            )

        dispatcher.register_handler(DriftSource.PERFORMANCE, mock_handler, "test_handler")

        assert "test_handler" in dispatcher.get_handler_ids()

    def test_dispatch_calls_handler(self):
        """Dispatch calls the registered handler."""
        dispatcher = BasicCorrectionDispatcher()

        handler_called = []

        def mock_handler(drift, strategy):
            handler_called.append(drift.id)
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.HEALED,
                handler_id="mock",
            )

        dispatcher.register_handler(DriftSource.PERFORMANCE, mock_handler, "test")

        drift = UnifiedDriftReport(
            id="test_drift",
            source=DriftSource.PERFORMANCE,
            severity=DriftSeverity.WARNING,
            message="Test",
        )

        result = dispatcher.dispatch(drift)

        assert result.healed
        assert "test_drift" in handler_called

    def test_dispatch_skips_when_no_handler(self):
        """Dispatch returns SKIPPED when no handler registered."""
        dispatcher = BasicCorrectionDispatcher()

        drift = UnifiedDriftReport(
            id="test_drift",
            source=DriftSource.STRUCTURAL,
            severity=DriftSeverity.WARNING,
            message="Test",
        )

        result = dispatcher.dispatch(drift)

        assert result.status == HealingStatus.SKIPPED

    def test_handler_priority_order(self):
        """Higher priority handlers run first."""
        dispatcher = BasicCorrectionDispatcher()

        call_order = []

        def handler_low(drift, strategy):
            call_order.append("low")
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.FAILED,
                handler_id="low",
            )

        def handler_high(drift, strategy):
            call_order.append("high")
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.HEALED,
                handler_id="high",
            )

        dispatcher.register_handler(DriftSource.PERFORMANCE, handler_low, "low", priority=1)
        dispatcher.register_handler(DriftSource.PERFORMANCE, handler_high, "high", priority=10)

        drift = UnifiedDriftReport(
            id="test",
            source=DriftSource.PERFORMANCE,
            severity=DriftSeverity.WARNING,
            message="Test",
        )

        result = dispatcher.dispatch(drift)

        # High priority should run first and succeed
        assert call_order[0] == "high"
        assert result.handler_id == "high"
        assert result.healed


class TestBasicCorrectionOrchestrator:
    """Tests for BasicCorrectionOrchestrator."""

    def test_detect_and_report(self):
        """Orchestrator runs detection."""
        registry = BasicDriftRegistry()
        dispatcher = BasicCorrectionDispatcher()
        orchestrator = BasicCorrectionOrchestrator(registry, dispatcher, skip_default_init=True)

        def mock_detector():
            return [
                UnifiedDriftReport(
                    id="drift_1",
                    source=DriftSource.PERFORMANCE,
                    severity=DriftSeverity.WARNING,
                    message="Test",
                )
            ]

        registry.register_detector(DriftSource.PERFORMANCE, mock_detector, "test")

        drifts = orchestrator.detect_and_report()
        assert len(drifts) == 1

    def test_detect_and_heal(self):
        """Orchestrator runs detection and healing."""
        registry = BasicDriftRegistry()
        dispatcher = BasicCorrectionDispatcher()
        orchestrator = BasicCorrectionOrchestrator(registry, dispatcher, skip_default_init=True)

        def mock_detector():
            return [
                UnifiedDriftReport(
                    id="drift_1",
                    source=DriftSource.PERFORMANCE,
                    severity=DriftSeverity.WARNING,
                    message="Test",
                    auto_healable=True,
                )
            ]

        def mock_handler(drift, strategy):
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.HEALED,
                handler_id="mock",
            )

        registry.register_detector(DriftSource.PERFORMANCE, mock_detector, "detector")
        dispatcher.register_handler(DriftSource.PERFORMANCE, mock_handler, "handler")

        results = orchestrator.detect_and_heal(strategy=HealingStrategy.AUTO)

        assert len(results) == 1
        assert results[0].healed

    def test_auto_only_filter(self):
        """auto_only=True filters non-auto-healable drifts."""
        registry = BasicDriftRegistry()
        dispatcher = BasicCorrectionDispatcher()
        orchestrator = BasicCorrectionOrchestrator(registry, dispatcher, skip_default_init=True)

        def mock_detector():
            return [
                UnifiedDriftReport(
                    id="drift_1",
                    source=DriftSource.PERFORMANCE,
                    severity=DriftSeverity.WARNING,
                    message="Auto",
                    auto_healable=True,
                ),
                UnifiedDriftReport(
                    id="drift_2",
                    source=DriftSource.PERFORMANCE,
                    severity=DriftSeverity.ERROR,
                    message="Manual",
                    auto_healable=False,
                ),
            ]

        def mock_handler(drift, strategy):
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.HEALED,
                handler_id="mock",
            )

        registry.register_detector(DriftSource.PERFORMANCE, mock_detector, "detector")
        dispatcher.register_handler(DriftSource.PERFORMANCE, mock_handler, "handler")

        results = orchestrator.detect_and_heal(auto_only=True)

        # Only drift_1 should be healed
        assert len(results) == 1
        assert results[0].drift_id == "drift_1"
