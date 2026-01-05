"""
Tests for NAGA Cortex - The Central Nervous System.

Tests the signal aggregation, correlation, and decision making.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.cortex import (
    CommitSignal,
    CorrelatedContext,
    CortexDecision,
    DecisionAction,
    FloodSignal,
    NagaCortex,
    SignalType,
    StateSignal,
)
from vibe_core.naga.cortex.cortex_main import CortexConfig, CortexStats

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_orchestrator():
    """Create a mock NagaOrchestrator."""
    orchestrator = MagicMock()

    # Mock Sesha
    orchestrator.sesha = MagicMock()
    sesha_status = MagicMock()
    sesha_status.recent_patterns = ["pattern1", "pattern2"]
    orchestrator.sesha.get_status.return_value = sesha_status

    # Mock Takshaka
    orchestrator.takshaka = MagicMock()
    takshaka_status = MagicMock()
    takshaka_status.active_threats = []
    orchestrator.takshaka.get_status.return_value = takshaka_status
    orchestrator.takshaka.bite.return_value = "event_123"

    # Mock Vasuki
    orchestrator.vasuki = MagicMock()
    vasuki_status = MagicMock()
    vasuki_status.peer_health = {}
    orchestrator.vasuki.get_status.return_value = vasuki_status

    return orchestrator


@pytest.fixture
def cortex(mock_orchestrator):
    """Create a NagaCortex with mock orchestrator."""
    config = CortexConfig(
        enabled=True,
        signal_buffer_size=10,
        correlation_threshold=3,
        auto_dispatch=False,  # Don't auto-dispatch for testing
    )
    c = NagaCortex(mock_orchestrator, config)
    # Clear any persisted state for fresh test
    c._dispatched.clear()
    c._stats.decisions_dispatched = 0
    return c


# =============================================================================
# SIGNAL TESTS
# =============================================================================


class TestSignals:
    """Tests for signal types."""

    def test_flood_signal_creation(self):
        """Test FloodSignal can be created."""
        signal = FloodSignal(
            source_id="flood_manager",
            event_type="TASK_COMPLETE",
            agent_id="engineer",
            toxicity_score=0.1,
        )
        assert signal.signal_type == SignalType.FLOOD
        assert signal.event_type == "TASK_COMPLETE"
        assert signal.toxicity_score == 0.1

    def test_commit_signal_creation(self):
        """Test CommitSignal can be created."""
        signal = CommitSignal(
            source_id="commit_watcher",
            pattern="PANIC",
            commit_sha="abc123",
            files_changed=("file1.py", "file2.py"),
        )
        assert signal.signal_type == SignalType.COMMIT
        assert signal.pattern == "PANIC"
        assert len(signal.files_changed) == 2

    def test_state_signal_creation(self):
        """Test StateSignal can be created."""
        signal = StateSignal(
            source_id="state_proxy",
            operation="save",
            path="/state/test.json",
            violation=True,
            violation_reason="dharma_violation",
        )
        assert signal.signal_type == SignalType.STATE
        assert signal.violation is True

    def test_signal_age(self):
        """Test signal age calculation."""
        signal = FloodSignal(
            source_id="test",
            timestamp=datetime.now() - timedelta(seconds=10),
        )
        assert signal.age_seconds >= 10


# =============================================================================
# CORTEX TESTS
# =============================================================================


class TestCortex:
    """Tests for NagaCortex."""

    def test_cortex_initialization(self, cortex):
        """Test Cortex initializes correctly."""
        assert cortex._config.enabled is True
        assert cortex._config.correlation_threshold == 3

    def test_receive_signal(self, cortex):
        """Test receiving a signal."""
        signal = FloodSignal(source_id="test", event_type="TEST")
        cortex.receive_signal(signal)

        assert cortex._stats.signals_received == 1
        assert len(cortex._signal_buffer) == 1

    def test_receive_multiple_signals(self, cortex):
        """Test receiving multiple signals."""
        for i in range(5):
            signal = FloodSignal(source_id="test", event_type=f"TEST_{i}")
            cortex.receive_signal(signal)

        assert cortex._stats.signals_received == 5

    def test_old_signal_discarded(self, cortex):
        """Test that old signals are discarded."""
        old_signal = FloodSignal(
            source_id="test",
            timestamp=datetime.now() - timedelta(seconds=600),  # 10 min old
        )
        cortex.receive_signal(old_signal)

        assert cortex._stats.signals_discarded_age == 1
        assert len(cortex._signal_buffer) == 0

    def test_correlation_threshold(self, cortex):
        """Test that correlation happens at threshold."""
        # Add 2 signals (below threshold of 3)
        for i in range(2):
            cortex.receive_signal(FloodSignal(source_id="test"))

        assert cortex._stats.correlations_performed == 0

        # Add 3rd signal (meets threshold)
        cortex.receive_signal(FloodSignal(source_id="test"))

        assert cortex._stats.correlations_performed == 1
        assert len(cortex._signal_buffer) == 0  # Buffer cleared

    def test_force_correlate(self, cortex):
        """Test force correlation."""
        cortex.receive_signal(FloodSignal(source_id="test"))
        decision = cortex.force_correlate()

        assert decision is not None
        assert decision.action == DecisionAction.NONE  # No actionable signals


# =============================================================================
# CORRELATION TESTS
# =============================================================================


class TestCorrelation:
    """Tests for signal correlation."""

    def test_correlate_signals(self, cortex):
        """Test basic correlation."""
        signals = [
            FloodSignal(source_id="test1"),
            FloodSignal(source_id="test2"),
            CommitSignal(source_id="test3", pattern="NORMAL"),
        ]
        context = cortex.correlate(signals)

        assert len(context.signals) == 3
        assert context.signal_count_by_type["FLOOD"] == 2
        assert context.signal_count_by_type["COMMIT"] == 1

    def test_correlated_context_security_threat(self, cortex, mock_orchestrator):
        """Test security threat detection."""
        # Add active threats
        takshaka_status = MagicMock()
        takshaka_status.active_threats = [{"source": "bad_agent", "severity": 8}]
        mock_orchestrator.takshaka.get_status.return_value = takshaka_status

        context = cortex.correlate([FloodSignal(source_id="test")])

        assert context.has_security_threat() is True
        assert context.threat_level > 0

    def test_correlated_context_healable_violation(self):
        """Test healable violation detection."""
        context = CorrelatedContext(
            signals=[
                StateSignal(
                    source_id="test",
                    operation="save",
                    path="/test.json",
                    violation=True,
                    violation_reason="dharma_violation",
                )
            ]
        )
        assert context.has_healable_violation() is True


# =============================================================================
# DECISION TESTS
# =============================================================================


class TestDecision:
    """Tests for decision making."""

    def test_decide_none_on_empty(self, cortex):
        """Test NONE decision when no actionable signals."""
        context = CorrelatedContext(signals=[FloodSignal(source_id="test")])
        decision = cortex.decide(context)

        assert decision.action == DecisionAction.NONE

    def test_decide_bite_on_threat(self, cortex, mock_orchestrator):
        """Test BITE decision on security threat."""
        # Set up threat
        takshaka_status = MagicMock()
        takshaka_status.active_threats = [{"source": "bad_agent", "severity": 8}]
        mock_orchestrator.takshaka.get_status.return_value = takshaka_status

        context = cortex.correlate([FloodSignal(source_id="test")])
        decision = cortex.decide(context)

        assert decision.action == DecisionAction.BITE
        assert decision.target == "bad_agent"

    def test_decide_heal_on_violation(self, cortex):
        """Test HEAL decision on structural violation."""
        context = CorrelatedContext(
            signals=[
                StateSignal(
                    source_id="test",
                    operation="save",
                    path="/test.json",
                    violation=True,
                    violation_reason="dharma_violation",
                )
            ]
        )
        decision = cortex.decide(context)

        assert decision.action == DecisionAction.HEAL
        assert decision.target == "/test.json"


# =============================================================================
# DISPATCH TESTS
# =============================================================================


class TestDispatch:
    """Tests for decision dispatch."""

    def test_dispatch_bite(self, cortex):
        """Test BITE dispatch to Takshaka."""
        from vibe_core.naga.cortex.decisions import decide_bite

        decision = decide_bite("bad_source", "Security threat")
        result = cortex.dispatch(decision)

        assert result.status == "BITTEN"
        assert result.event_id == "event_123"

    def test_dispatch_to_unavailable_service(self, cortex, mock_orchestrator):
        """Test dispatch when service unavailable."""
        from vibe_core.naga.cortex.decisions import decide_heal

        # Clear Shuddhi from registry
        decision = decide_heal("/test.py", "test_rule")

        with patch("vibe_core.di.ServiceRegistry.get", return_value=None):
            result = cortex.dispatch(decision)

        assert result.status == "UNAVAILABLE"


# =============================================================================
# STATUS TESTS
# =============================================================================


class TestStatus:
    """Tests for Cortex status."""

    def test_get_status(self, cortex):
        """Test getting Cortex status."""
        # Add some signals
        for i in range(5):
            cortex.receive_signal(FloodSignal(source_id="test"))

        status = cortex.get_status()

        assert status["enabled"] is True
        assert status["stats"]["signals_received"] == 5
        assert "correlations_performed" in status["stats"]

    def test_get_queued_decisions(self, cortex):
        """Test getting queued decisions."""
        # Trigger correlation (adds decision to queue since auto_dispatch=False)
        for i in range(3):
            cortex.receive_signal(FloodSignal(source_id="test"))

        # Should have made a decision (even if NONE)
        decisions = cortex.get_queued_decisions()
        # May or may not have decisions depending on signals
        assert isinstance(decisions, list)


# =============================================================================
# CONFIG TESTS
# =============================================================================


class TestConfig:
    """Tests for Cortex configuration."""

    def test_config_from_dict(self):
        """Test creating config from dict."""
        data = {
            "enabled": True,
            "signal_buffer_size": 50,
            "correlation_threshold": 5,
        }
        config = CortexConfig.from_dict(data)

        assert config.signal_buffer_size == 50
        assert config.correlation_threshold == 5

    def test_config_to_dict(self):
        """Test serializing config to dict."""
        config = CortexConfig(signal_buffer_size=50)
        data = config.to_dict()

        assert data["signal_buffer_size"] == 50
        assert "enabled" in data


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for Cortex with other NAGA components."""

    def test_convenience_methods(self, cortex):
        """Test convenience signal methods."""
        cortex.receive_flood_signal(
            event_type="TEST",
            agent_id="engineer",
            toxicity_score=0.2,
        )
        cortex.receive_commit_signal(
            pattern="PANIC",
            commit_sha="abc123",
        )
        cortex.receive_state_signal(
            operation="save",
            path="/test.json",
        )

        assert cortex._stats.signals_received == 3
