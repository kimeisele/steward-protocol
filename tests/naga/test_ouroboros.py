"""
Tests for NAGA OUROBOROS - Self-healing loop detection (GAD-000 Recoverability).
"""

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from vibe_core.naga.ouroboros import (
    CorrectionEvent,
    LoopAlert,
    LoopCode,
    NagaOuroboros,
)

# =============================================================================
# MOCK DECISION
# =============================================================================


class MockAction(Enum):
    BITE = "bite"
    HEAL = "heal"
    NONE = "none"


class MockReasonCode(Enum):
    D001_SECURITY_THREAT = "D001"
    D002_HEALABLE = "D002"


@dataclass
class MockCortexDecision:
    """Mock decision for testing."""

    action: MockAction = MockAction.BITE
    target: str = "test_target"
    timestamp: datetime = None
    reason_code: MockReasonCode = MockReasonCode.D001_SECURITY_THREAT

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# =============================================================================
# TESTS
# =============================================================================


class TestCorrectionEvent:
    """Test CorrectionEvent dataclass."""

    def test_to_dict(self):
        event = CorrectionEvent(
            source_naga="cortex",
            target_naga="shuddhi",
            decision_hash="abc123",
            timestamp=1234567890.0,
            reason_code="D001",
        )
        d = event.to_dict()

        assert d["source_naga"] == "cortex"
        assert d["target_naga"] == "shuddhi"
        assert d["decision_hash"] == "abc123"
        assert d["timestamp"] == 1234567890.0
        assert d["reason_code"] == "D001"


class TestLoopAlert:
    """Test LoopAlert dataclass."""

    def test_to_dict(self):
        event = CorrectionEvent(source_naga="cortex", target_naga="shuddhi", decision_hash="abc")
        alert = LoopAlert(
            loop_code=LoopCode.L001_SIMPLE_LOOP,
            severity="CRITICAL",
            message="Test loop",
            participants=["cortex", "shuddhi"],
            events=[event],
        )
        d = alert.to_dict()

        assert d["loop_code"] == "L001"
        assert d["severity"] == "CRITICAL"
        assert d["message"] == "Test loop"
        assert d["participants"] == ["cortex", "shuddhi"]
        assert len(d["events"]) == 1


class TestOuroborosBasics:
    """Test basic OUROBOROS operations."""

    @pytest.fixture
    def ouroboros(self):
        return NagaOuroboros(orchestrator=None)

    def test_initialization(self, ouroboros):
        status = ouroboros.get_status()

        assert status["corrections_observed"] == 0
        assert status["loops_detected"] == 0
        assert status["history_size"] == 0
        assert status["paused_sources"] == []

    def test_observe_correction_increments_counter(self, ouroboros):
        decision = MockCortexDecision()
        ouroboros.observe_correction("cortex", "shuddhi", decision)

        status = ouroboros.get_status()
        assert status["corrections_observed"] == 1
        assert status["history_size"] == 1

    def test_reset_clears_state(self, ouroboros):
        decision = MockCortexDecision()
        ouroboros.observe_correction("cortex", "shuddhi", decision)
        ouroboros.reset()

        status = ouroboros.get_status()
        assert status["corrections_observed"] == 0
        assert status["history_size"] == 0


class TestSimpleLoopDetection:
    """Test A→B→A loop detection."""

    @pytest.fixture
    def ouroboros(self):
        return NagaOuroboros(orchestrator=None, loop_window_seconds=60.0)

    def test_detects_simple_loop(self, ouroboros):
        decision = MockCortexDecision()

        # A→B (no loop)
        result1 = ouroboros.observe_correction("A", "B", decision)
        assert result1 is None

        # B→A (loop!)
        result2 = ouroboros.observe_correction("B", "A", decision)
        assert result2 is not None
        assert result2.loop_code == LoopCode.L001_SIMPLE_LOOP
        assert set(result2.participants) == {"A", "B"}

    def test_no_loop_if_different_targets(self, ouroboros):
        decision = MockCortexDecision()

        ouroboros.observe_correction("A", "B", decision)
        result = ouroboros.observe_correction("C", "D", decision)

        assert result is None

    def test_dedup_same_loop(self, ouroboros):
        decision = MockCortexDecision()

        ouroboros.observe_correction("A", "B", decision)
        result1 = ouroboros.observe_correction("B", "A", decision)
        assert result1 is not None

        # Same pattern again - should be deduped
        ouroboros.observe_correction("A", "B", decision)
        result2 = ouroboros.observe_correction("B", "A", decision)
        assert result2 is None  # Already seen


class TestTriangleLoopDetection:
    """Test A→B→C→A loop detection."""

    @pytest.fixture
    def ouroboros(self):
        return NagaOuroboros(orchestrator=None, loop_window_seconds=60.0)

    def test_detects_triangle_loop(self, ouroboros):
        decision = MockCortexDecision()

        ouroboros.observe_correction("A", "B", decision)
        ouroboros.observe_correction("B", "C", decision)
        result = ouroboros.observe_correction("C", "A", decision)

        assert result is not None
        assert result.loop_code == LoopCode.L002_TRIANGLE_LOOP
        assert set(result.participants) == {"A", "B", "C"}

    def test_no_triangle_if_chain_breaks(self, ouroboros):
        decision = MockCortexDecision()

        ouroboros.observe_correction("A", "B", decision)
        ouroboros.observe_correction("B", "C", decision)
        # C→D (not back to A)
        result = ouroboros.observe_correction("C", "D", decision)

        assert result is None


class TestRapidFireDetection:
    """Test rapid fire detection."""

    @pytest.fixture
    def ouroboros(self):
        return NagaOuroboros(
            orchestrator=None,
            rapid_fire_threshold=3,  # Low threshold for testing
            rapid_fire_window=10.0,
        )

    def test_detects_rapid_fire(self, ouroboros):
        decision = MockCortexDecision()

        # Fire same source rapidly
        ouroboros.observe_correction("spammer", "target1", decision)
        ouroboros.observe_correction("spammer", "target2", decision)
        result = ouroboros.observe_correction("spammer", "target3", decision)

        assert result is not None
        assert result.loop_code == LoopCode.L003_RAPID_FIRE
        assert "spammer" in result.participants

    def test_pauses_rapid_firer(self, ouroboros):
        decision = MockCortexDecision()

        for i in range(3):
            ouroboros.observe_correction("spammer", f"target{i}", decision)

        assert ouroboros.is_paused("spammer") is True

    def test_different_sources_not_rapid_fire(self, ouroboros):
        decision = MockCortexDecision()

        ouroboros.observe_correction("A", "target", decision)
        ouroboros.observe_correction("B", "target", decision)
        result = ouroboros.observe_correction("C", "target", decision)

        assert result is None


class TestCircuitBreaker:
    """Test pause/unpause circuit breaker."""

    @pytest.fixture
    def ouroboros(self):
        return NagaOuroboros(orchestrator=None)

    def test_manual_pause(self, ouroboros):
        assert ouroboros.is_paused("source") is False

        ouroboros.pause_source("source", duration=60.0)
        assert ouroboros.is_paused("source") is True

    def test_manual_unpause(self, ouroboros):
        ouroboros.pause_source("source", duration=60.0)
        ouroboros.unpause_source("source")

        assert ouroboros.is_paused("source") is False

    def test_paused_source_ignored(self, ouroboros):
        decision = MockCortexDecision()

        ouroboros.pause_source("paused_naga", duration=60.0)

        # Corrections from paused source are ignored
        ouroboros.observe_correction("paused_naga", "target", decision)

        # History should be empty (correction ignored)
        status = ouroboros.get_status()
        assert status["corrections_observed"] == 1  # Counted but not added to history
        # The history won't include it as we returned early
        assert status["paused_sources"] == ["paused_naga"]

    def test_is_paused_respects_expiry(self, ouroboros):
        # Pause for very short duration
        ouroboros._paused_sources["source"] = time.time() - 1.0  # Already expired

        assert ouroboros.is_paused("source") is False
        assert "source" not in ouroboros._paused_sources  # Cleaned up


class TestAlertHandlers:
    """Test alert handler callbacks."""

    @pytest.fixture
    def ouroboros(self):
        return NagaOuroboros(orchestrator=None, rapid_fire_threshold=2)

    def test_handler_called_on_loop(self, ouroboros):
        alerts_received: List[LoopAlert] = []

        def handler(alert: LoopAlert):
            alerts_received.append(alert)

        ouroboros.add_alert_handler(handler)

        decision = MockCortexDecision()
        ouroboros.observe_correction("A", "B", decision)
        ouroboros.observe_correction("B", "A", decision)

        assert len(alerts_received) == 1
        assert alerts_received[0].loop_code == LoopCode.L001_SIMPLE_LOOP

    def test_handler_error_is_silent(self, ouroboros):
        def bad_handler(alert: LoopAlert):
            raise ValueError("Handler exploded!")

        ouroboros.add_alert_handler(bad_handler)

        decision = MockCortexDecision()
        ouroboros.observe_correction("A", "B", decision)
        # Should not raise
        ouroboros.observe_correction("B", "A", decision)


class TestLoopCodes:
    """Test loop code enum."""

    def test_all_codes_have_values(self):
        assert LoopCode.L001_SIMPLE_LOOP.value == "L001"
        assert LoopCode.L002_TRIANGLE_LOOP.value == "L002"
        assert LoopCode.L003_RAPID_FIRE.value == "L003"
        assert LoopCode.L004_CASCADE_DETECTED.value == "L004"
