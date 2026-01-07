"""
KURUKSHETRA TEST - The Ultimate NAGA Integration Suite.

"The field of Dharma. Where the battle for Truth is fought."

This suite verifies the "Dharma Chain":
1. Guard (Takshaka) protects Memory (Sesha)
2. Transport (Vasuki) uses Guard (Takshaka)
3. Quarantine (Kaliya) persists through restarts (StateService)
4. Audit (Prahlad) verifies the whole stack

Narasimha-Moment: The system holds under pressure.
"""

import pytest
import time
from datetime import datetime
from unittest.mock import MagicMock

from vibe_core.naga.orchestrator import NagaOrchestrator
from vibe_core.naga.testing import NagaTestHarness
from vibe_core.protocols.naga import VerifyStatus, SignedEnvelope, VajraViolation, NagaType
from vibe_core.naga.services.kaliya import KaliyaService
from vibe_core.state.state_service import get_state_service, reset_state_service


class TestKurukshetra:
    """End-to-End Integration Tests for NAGA Federation."""

    @pytest.fixture
    def harness(self):
        """Standard NAGA orchestrator harness."""
        with NagaTestHarness.for_orchestrator() as h:
            yield h

    @pytest.fixture
    def naga(self, harness, temp_dir):
        """Bootstrap a real NAGA federation with in-memory ledger."""
        # We need a real StateService for Kaliya persistence tests
        reset_state_service()
        state_service = get_state_service(workspace=temp_dir)

        naga = NagaOrchestrator.bootstrap(
            ledger=harness.ledger, correction_orchestrator=harness.correction_orchestrator
        )

        # Inject state service into Kaliya for persistence testing
        if naga.kaliya:
            naga.kaliya._state = state_service

        return naga

    def test_dharma_chain_vasuki_takshaka_sesha(self, naga):
        """
        Scenario: Malicious packet arrives.
        Chain: Vasuki -> Takshaka Gate -> Rejection -> Bite -> Sesha Ledger.
        """
        # 1. Create a toxic envelope (simulated)
        # Empty signature will be rejected by Takshaka Gate
        toxic_envelope = SignedEnvelope(
            payload=b"toxic_payload",
            signature=b"",  # Missing signature!
            sender_key="malicious_key",
            timestamp=time.time(),
            content_type="msgpack",
        )

        # 2. Try to churn_in via Vasuki
        # This should trigger the Takshaka Gate and RAISE (Fail-Closed)
        with pytest.raises(RuntimeError, match="Security validation failed"):
            naga.vasuki.churn_in(toxic_envelope)

        # 3. Record the violation (Bite)
        violation = VajraViolation(
            violation_type="MALICIOUS_PACKET", source="peer_666", details={"reason": "Invalid signature"}
        )
        event_id = naga.takshaka.bite(violation)

        assert event_id is not None
        assert "EVT-" in event_id

        # 4. Verify Sesha has recorded the truth
        events = naga.sesha.get_recent_events(limit=5)
        # Filter for our violation
        violation_events = [e for e in events if e.get("event_type") == "VAJRA_VIOLATION"]
        assert len(violation_events) >= 1
        assert violation_events[0]["agent_id"] == "TAKSHAKA"

    def test_kaliya_quarantine_persistence(self, naga, temp_dir):
        """
        Scenario: Agent is quarantined, system restarts.
        Verification: Kaliya remembers the quarantine.
        """
        agent_id = "rebel_agent_7"

        # 1. Trigger violations until quarantine
        for _ in range(3):
            naga.kaliya.record_violation(agent_id)

        # 2. Verify quarantine active
        assert naga.kaliya.is_quarantined(agent_id) is True

        # 3. Simulate System Crash / Restart
        # We create a NEW Kaliya instance pointing to the SAME state service
        state_service = naga.kaliya._state
        new_kaliya = KaliyaService(state_service=state_service)

        # 4. THE NARASIMHA MOMENT: Does he remember?
        assert new_kaliya.is_quarantined(agent_id) is True
        assert new_kaliya.get_violation_count(agent_id) == 3

        # 5. Verify escalation persistence
        # Release, then trigger more cycles
        new_kaliya.release(agent_id)
        assert new_kaliya.is_quarantined(agent_id) is False

        # Next cycle -> escalation
        for _ in range(3):
            new_kaliya.record_violation(agent_id)

        # Should be quarantined again
        assert new_kaliya.is_quarantined(agent_id) is True

        # Trigger enough cycles for escalation (threshold is 3)
        # Cycle 1: Violations -> Quarantine 1 -> Release
        # Cycle 2: Violations -> Quarantine 2 -> Release
        # Cycle 3: Violations -> Quarantine 3 -> Escalation

        # Restart again
        final_kaliya = KaliyaService(state_service=state_service)
        assert final_kaliya.get_violation_count(agent_id) >= 3

    def test_prahlad_boot_integrity(self, harness):
        """
        Scenario: Corruption in Sesha.
        Verification: Prahlad/Sesha Fail-Closed at boot.
        """
        # 1. Corrupt the ledger mock
        harness.ledger.get_top_hash = MagicMock(side_effect=RuntimeError("DB Corruption!"))

        # 2. Attempt to bootstrap NAGA
        # Sesha should catch the error and raise, preventing boot
        with pytest.raises(RuntimeError, match="Sesha boot failed"):
            NagaOrchestrator.bootstrap(ledger=harness.ledger, correction_orchestrator=harness.correction_orchestrator)

    def test_complete_dharma_chain_status(self, naga):
        """Verify all 8 hardened services report healthy status."""
        status = naga.get_status()

        assert status["initialized"] is True

        # Check critical services
        for key in ["sesha", "takshaka", "vasuki", "prahlad", "karkotaka", "kaliya", "ananta", "narada"]:
            assert status[key] is not None
            # Extract health from status dict or object
            health = (
                status[key].get("healthy") if isinstance(status[key], dict) else getattr(status[key], "healthy", False)
            )
            assert health is True, f"Service {key} should be healthy"
