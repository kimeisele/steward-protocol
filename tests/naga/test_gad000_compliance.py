"""
Tests for NAGA GAD-000 Compliance.

GAD-000 Principles tested:
- Parseability: Machine-readable reason codes and fingerprints
- Idempotency: Duplicate detection and deduplication
- 37th Principle: Cryptographic signatures on decisions

"Woher weiß ich dass du zur richtigen Zeit die richtigen Steps nimmst?"
"""

import time
from datetime import datetime
from unittest.mock import MagicMock

import pytest

# =============================================================================
# PHASE 1: PARSEABILITY TESTS
# =============================================================================


class TestDecisionReasonCodes:
    """Test machine-parseable decision reason codes."""

    def test_all_codes_have_values(self):
        from vibe_core.naga.cortex.decisions import DecisionReasonCode

        for code in DecisionReasonCode:
            assert code.value.startswith("D")
            assert len(code.value) == 4  # D001, D002, etc.

    def test_decision_includes_reason_code(self):
        from vibe_core.naga.cortex.decisions import (
            CortexDecision,
            DecisionAction,
            DecisionReasonCode,
        )

        decision = CortexDecision(
            action=DecisionAction.BITE,
            reason_code=DecisionReasonCode.D001_SECURITY_THREAT,
        )

        assert decision.reason_code == DecisionReasonCode.D001_SECURITY_THREAT
        assert decision.reason_code.value == "D001"

    def test_decision_str_includes_code(self):
        from vibe_core.naga.cortex.decisions import (
            CortexDecision,
            DecisionAction,
            DecisionReasonCode,
        )

        decision = CortexDecision(
            action=DecisionAction.HEAL,
            target="test.py",
            reason_code=DecisionReasonCode.D002_HEALABLE_VIOLATION,
        )

        # String representation should include the code
        s = str(decision)
        assert "D002" in s

    def test_factory_methods_set_correct_codes(self):
        from vibe_core.naga.cortex.decisions import (
            DecisionReasonCode,
            decide_bite,
            decide_consult,
            decide_escalate,
            decide_heal,
            decide_none,
            decide_route,
        )

        assert decide_none().reason_code == DecisionReasonCode.D005_NO_ACTION
        assert decide_bite("src").reason_code == DecisionReasonCode.D001_SECURITY_THREAT
        assert decide_heal("x", "rule").reason_code == DecisionReasonCode.D002_HEALABLE_VIOLATION
        assert decide_route("c", 0.1).reason_code == DecisionReasonCode.D003_CIRCUIT_DEGRADATION
        assert decide_consult({}).reason_code == DecisionReasonCode.D004_COGNITIVE_UPDATE
        assert decide_escalate("reason").reason_code == DecisionReasonCode.D006_ESCALATION_REQUIRED


class TestAlertCodes:
    """Test machine-parseable alert codes in CommitWatcher."""

    def test_all_alert_codes_have_values(self):
        from vibe_core.naga.commit_watcher import AlertCode

        for code in AlertCode:
            assert code.value.startswith("A")
            assert len(code.value) == 4  # A001, A002, etc.

    def test_alert_includes_code(self):
        from vibe_core.naga.commit_watcher import AlertCode, CommitAlert

        alert = CommitAlert(
            alert_type="PANIC_PATTERN",
            alert_code=AlertCode.A001_PANIC_PATTERN,
            severity="CRITICAL",
            message="Test alert",
        )

        assert alert.alert_code == AlertCode.A001_PANIC_PATTERN
        assert alert.alert_code.value == "A001"

    def test_alert_to_dict_includes_code(self):
        from vibe_core.naga.commit_watcher import AlertCode, CommitAlert

        alert = CommitAlert(
            alert_type="DEFERRAL_LOOP",
            alert_code=AlertCode.A003_DEFERRAL_LOOP,
            severity="WARNING",
            message="Decision paralysis",
        )

        d = alert.to_dict()
        assert d["alert_code"] == "A003"
        assert d["alert_type"] == "DEFERRAL_LOOP"


class TestViolationFingerprinting:
    """Test violation fingerprinting for idempotency."""

    def test_compute_violation_hash(self):
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.protocols.naga import VajraViolation

        takshaka = TakshakaService()

        v1 = VajraViolation(
            violation_type="SQL_INJECTION",
            source="user_input",
            details={},
        )

        v2 = VajraViolation(
            violation_type="SQL_INJECTION",
            source="user_input",
            details={"extra": "ignored"},
        )

        # Same type+source = same hash
        hash1 = takshaka._compute_violation_hash(v1)
        hash2 = takshaka._compute_violation_hash(v2)

        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated SHA256

    def test_different_violations_different_hashes(self):
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.protocols.naga import VajraViolation

        takshaka = TakshakaService()

        v1 = VajraViolation(
            violation_type="SQL_INJECTION",
            source="input_a",
        )

        v2 = VajraViolation(
            violation_type="CMD_INJECTION",
            source="input_a",
        )

        hash1 = takshaka._compute_violation_hash(v1)
        hash2 = takshaka._compute_violation_hash(v2)

        assert hash1 != hash2


class TestViolationIdempotency:
    """Test that duplicate violations are deduplicated."""

    def test_duplicate_violation_returns_existing_id(self):
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.protocols.naga import VajraViolation

        # Mock ledger
        mock_ledger = MagicMock()
        mock_ledger.record_event = MagicMock(return_value="event_123")

        takshaka = TakshakaService(ledger=mock_ledger)

        violation = VajraViolation(
            violation_type="TEST_VIOLATION",
            source="test_source",
        )

        # First call
        id1 = takshaka.bite(violation)
        assert id1 == "event_123"
        assert mock_ledger.record_event.call_count == 1

        # Second call with same violation - should return existing ID
        id2 = takshaka.bite(violation)
        assert id2 == "event_123"
        # Should NOT have called record_event again
        assert mock_ledger.record_event.call_count == 1

    def test_violation_hash_stored_in_details(self):
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.protocols.naga import VajraViolation

        mock_ledger = MagicMock()
        mock_ledger.record_event = MagicMock(return_value="event_456")

        takshaka = TakshakaService(ledger=mock_ledger)

        violation = VajraViolation(
            violation_type="PROMPT_INJECTION",
            source="agent_x",
        )

        takshaka.bite(violation)

        # Check that violation_hash was included in details
        call_args = mock_ledger.record_event.call_args
        details = call_args.kwargs.get("details", {})
        assert "violation_hash" in details
        assert len(details["violation_hash"]) == 16


# =============================================================================
# PHASE 2: 37TH PRINCIPLE TESTS (SIGNATURES)
# =============================================================================


class TestDecisionSigning:
    """Test decision signing for 37th Principle."""

    @pytest.fixture
    def mock_identity(self):
        """Create a mock NAGA identity."""
        from vibe_core.naga.identity import NagaIdentity

        return NagaIdentity.generate("test_naga")

    def test_decision_starts_unsigned(self):
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction

        decision = CortexDecision(action=DecisionAction.BITE)

        assert decision.is_signed is False
        assert decision.signature is None
        assert decision.signer_id == ""

    def test_sign_decision(self, mock_identity):
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction

        decision = CortexDecision(
            action=DecisionAction.HEAL,
            target="test.py",
        )

        decision.sign(mock_identity)

        assert decision.is_signed is True
        assert decision.signature is not None
        assert decision.signer_id == "test_naga"
        assert decision.signature_timestamp is not None

    def test_verify_valid_signature(self, mock_identity):
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction

        decision = CortexDecision(action=DecisionAction.ROUTE, target="circuit_1")

        decision.sign(mock_identity)

        assert decision.verify(mock_identity) is True

    def test_verify_fails_with_wrong_identity(self, mock_identity):
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction
        from vibe_core.naga.identity import NagaIdentity

        decision = CortexDecision(action=DecisionAction.CONSULT)
        decision.sign(mock_identity)

        # Different identity
        other_identity = NagaIdentity.generate("other_naga")

        assert decision.verify(other_identity) is False

    def test_signing_payload_is_deterministic(self):
        from vibe_core.naga.cortex.decisions import (
            CortexDecision,
            DecisionAction,
            DecisionReasonCode,
        )

        decision = CortexDecision(
            action=DecisionAction.BITE,
            target="malicious",
            reason_code=DecisionReasonCode.D001_SECURITY_THREAT,
        )

        # Multiple calls should produce identical payload
        p1 = decision._signing_payload()
        p2 = decision._signing_payload()

        assert p1 == p2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestParseabilityIntegration:
    """Test that all parseable codes work together."""

    def test_cortex_decision_full_audit_trail(self):
        """Test that a decision has all machine-parseable fields."""
        from vibe_core.naga.cortex.decisions import (
            CortexDecision,
            DecisionAction,
            DecisionReasonCode,
        )

        decision = CortexDecision(
            action=DecisionAction.BITE,
            target="suspicious_agent",
            reason_code=DecisionReasonCode.D001_SECURITY_THREAT,
            reasoning="Detected SQL injection attempt",
            confidence=0.95,
        )

        # All parseable fields present
        assert decision.action.name == "BITE"
        assert decision.reason_code.value == "D001"
        assert decision.target == "suspicious_agent"
        assert decision.confidence == 0.95

    def test_alert_full_audit_trail(self):
        """Test that an alert has all machine-parseable fields."""
        from vibe_core.naga.commit_watcher import AlertCode, CommitAlert

        alert = CommitAlert(
            alert_type="PANIC_PATTERN",
            alert_code=AlertCode.A001_PANIC_PATTERN,
            severity="CRITICAL",
            message="3 panic dumps in 5 minutes",
            details={"panic_count": 3, "window_seconds": 300},
        )

        d = alert.to_dict()

        # All parseable fields in dict
        assert d["alert_type"] == "PANIC_PATTERN"
        assert d["alert_code"] == "A001"
        assert d["severity"] == "CRITICAL"
        assert "panic_count" in d["details"]


# =============================================================================
# PHASE 3: RECOVERABILITY TESTS (OUROBOROS)
# =============================================================================


class TestLoopCodeParseability:
    """Test that OUROBOROS loop codes are machine-parseable."""

    def test_all_loop_codes_have_values(self):
        from vibe_core.naga.ouroboros import LoopCode

        for code in LoopCode:
            assert code.value.startswith("L")
            assert len(code.value) == 4  # L001, L002, etc.

    def test_loop_alert_includes_code(self):
        from vibe_core.naga.ouroboros import CorrectionEvent, LoopAlert, LoopCode

        event = CorrectionEvent(
            source_naga="cortex",
            target_naga="shuddhi",
            decision_hash="abc123",
        )

        alert = LoopAlert(
            loop_code=LoopCode.L001_SIMPLE_LOOP,
            severity="CRITICAL",
            message="Loop detected",
            participants=["cortex", "shuddhi"],
            events=[event],
        )

        d = alert.to_dict()
        assert d["loop_code"] == "L001"

    def test_all_loop_codes_documented(self):
        from vibe_core.naga.ouroboros import LoopCode

        # All codes should be defined
        codes = [c.value for c in LoopCode]
        assert "L001" in codes  # Simple loop
        assert "L002" in codes  # Triangle loop
        assert "L003" in codes  # Rapid fire
        assert "L004" in codes  # Cascade


class TestOuroborosRecoverability:
    """Test OUROBOROS loop detection and recovery (GAD-000 Recoverability)."""

    @pytest.fixture
    def mock_decision(self):
        """Create a mock CortexDecision."""
        from vibe_core.naga.cortex.decisions import (
            CortexDecision,
            DecisionAction,
            DecisionReasonCode,
        )

        return CortexDecision(
            action=DecisionAction.HEAL,
            target="test_path",
            reason_code=DecisionReasonCode.D002_HEALABLE_VIOLATION,
        )

    @pytest.fixture
    def ouroboros(self):
        from vibe_core.naga.ouroboros import NagaOuroboros

        return NagaOuroboros(orchestrator=None, loop_window_seconds=60.0)

    def test_detects_simple_loop_with_real_decision(self, ouroboros, mock_decision):
        """Test A→B→A detection with real CortexDecision."""
        from vibe_core.naga.ouroboros import LoopCode

        # A corrects B
        result1 = ouroboros.observe_correction("cortex", "shuddhi", mock_decision)
        assert result1 is None

        # B corrects A - LOOP!
        result2 = ouroboros.observe_correction("shuddhi", "cortex", mock_decision)
        assert result2 is not None
        assert result2.loop_code == LoopCode.L001_SIMPLE_LOOP

    def test_circuit_breaker_prevents_further_damage(self, ouroboros, mock_decision):
        """Test that rapid-firing sources are paused."""
        from vibe_core.naga.ouroboros import LoopCode

        # Configure low threshold
        ouroboros._rapid_fire_threshold = 3
        ouroboros._rapid_fire_window = 60.0

        # Rapid fire from one source
        for i in range(3):
            ouroboros.observe_correction("runaway_naga", f"target_{i}", mock_decision)

        # Source should be paused
        assert ouroboros.is_paused("runaway_naga")

        # Further corrections from paused source should not add to history
        initial_history = len(ouroboros._history)
        ouroboros.observe_correction("runaway_naga", "another_target", mock_decision)
        # History should not grow (correction ignored)
        assert len(ouroboros._history) == initial_history

    def test_recovery_after_pause_expires(self, ouroboros, mock_decision):
        """Test that paused sources recover after timeout."""
        # Manually set an already-expired pause
        ouroboros._paused_sources["recovered_naga"] = time.time() - 1.0

        # Should no longer be paused
        assert ouroboros.is_paused("recovered_naga") is False

        # Can operate normally again
        result = ouroboros.observe_correction("recovered_naga", "target", mock_decision)
        # Should be processed (no loop in this case)
        assert ouroboros.get_status()["history_size"] == 1

    def test_manual_intervention_unpause(self, ouroboros, mock_decision):
        """Test 37th Principle: human can manually unpause."""
        ouroboros.pause_source("stuck_naga", duration=3600)  # 1 hour pause

        assert ouroboros.is_paused("stuck_naga")

        # Human intervention
        ouroboros.unpause_source("stuck_naga")

        assert not ouroboros.is_paused("stuck_naga")


class TestOuroborosIdempotency:
    """Test OUROBOROS deduplication (GAD-000 Idempotency)."""

    @pytest.fixture
    def mock_decision(self):
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction

        return CortexDecision(action=DecisionAction.BITE, target="x")

    @pytest.fixture
    def ouroboros(self):
        from vibe_core.naga.ouroboros import NagaOuroboros

        return NagaOuroboros(orchestrator=None)

    def test_same_loop_not_alerted_twice(self, ouroboros, mock_decision):
        """Test that identical loops are deduplicated."""
        # First loop
        ouroboros.observe_correction("A", "B", mock_decision)
        alert1 = ouroboros.observe_correction("B", "A", mock_decision)
        assert alert1 is not None

        # Same pattern again - should be deduped
        ouroboros.observe_correction("A", "B", mock_decision)
        alert2 = ouroboros.observe_correction("B", "A", mock_decision)
        assert alert2 is None  # Deduplicated

    def test_loop_hash_is_deterministic(self, ouroboros):
        """Test that loop hash computation is deterministic."""
        from vibe_core.naga.ouroboros import CorrectionEvent

        event1 = CorrectionEvent(
            source_naga="A",
            target_naga="B",
            decision_hash="hash1",
        )
        event2 = CorrectionEvent(
            source_naga="B",
            target_naga="A",
            decision_hash="hash2",
        )

        hash1 = ouroboros._compute_loop_hash([event1, event2])
        hash2 = ouroboros._compute_loop_hash([event1, event2])

        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated SHA256


class TestOuroborosOrchestatorIntegration:
    """Test OUROBOROS integration with NagaOrchestrator."""

    def test_loop_recorded_to_ledger(self):
        """Test that loops are recorded to ledger via Sesha."""
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction
        from vibe_core.naga.ouroboros import NagaOuroboros

        # Mock orchestrator with sesha
        mock_ledger = MagicMock()
        mock_ledger.record_event = MagicMock()

        mock_sesha = MagicMock()
        mock_sesha._ledger = mock_ledger

        mock_orchestrator = MagicMock()
        mock_orchestrator.sesha = mock_sesha
        mock_orchestrator.takshaka = None

        ouroboros = NagaOuroboros(orchestrator=mock_orchestrator)

        decision = CortexDecision(action=DecisionAction.HEAL, target="x")

        # Trigger a loop
        ouroboros.observe_correction("A", "B", decision)
        ouroboros.observe_correction("B", "A", decision)

        # Should have recorded to ledger
        assert mock_ledger.record_event.called
        call_args = mock_ledger.record_event.call_args
        assert "NAGA_LOOP" in call_args.kwargs.get("event_type", "")

    def test_critical_loop_triggers_takshaka_bite(self):
        """Test that critical loops are recorded as violations."""
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction
        from vibe_core.naga.ouroboros import NagaOuroboros

        # Mock orchestrator with takshaka
        mock_takshaka = MagicMock()
        mock_takshaka.bite = MagicMock()

        mock_orchestrator = MagicMock()
        mock_orchestrator.sesha = None
        mock_orchestrator.takshaka = mock_takshaka

        ouroboros = NagaOuroboros(orchestrator=mock_orchestrator)

        decision = CortexDecision(action=DecisionAction.BITE, target="x")

        # Trigger a loop (simple loop is CRITICAL)
        ouroboros.observe_correction("cortex", "shuddhi", decision)
        ouroboros.observe_correction("shuddhi", "cortex", decision)

        # Should have called bite
        assert mock_takshaka.bite.called


class TestRecoverabilityStatus:
    """Test OUROBOROS status reporting for observability."""

    def test_status_includes_all_required_fields(self):
        from vibe_core.naga.ouroboros import NagaOuroboros

        ouroboros = NagaOuroboros(orchestrator=None)
        status = ouroboros.get_status()

        # Required fields for GAD-000 Observability
        assert "corrections_observed" in status
        assert "loops_detected" in status
        assert "history_size" in status
        assert "paused_sources" in status
        assert "uptime_seconds" in status
        assert "config" in status

    def test_status_reflects_actual_state(self):
        from vibe_core.naga.cortex.decisions import CortexDecision, DecisionAction
        from vibe_core.naga.ouroboros import NagaOuroboros

        ouroboros = NagaOuroboros(orchestrator=None)
        decision = CortexDecision(action=DecisionAction.NONE)

        # Make some corrections
        ouroboros.observe_correction("A", "B", decision)
        ouroboros.observe_correction("B", "A", decision)  # Loop

        status = ouroboros.get_status()

        assert status["corrections_observed"] == 2
        assert status["loops_detected"] == 1
        assert status["history_size"] == 2
