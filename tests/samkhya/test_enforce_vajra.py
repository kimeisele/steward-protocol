from datetime import datetime

import pytest

from vibe_core.protocols.universal import EnforceContext, SovereignContext, Verdict
from vibe_core.services.capability_enforcer import CapabilityEnforcerService


class TestEnforceVajra:
    """
    The Vajra Tests (Diamant-Härte).
    Prüft, ob das Gesetz (EnforceProtocol) unbestechlich ist.
    """

    @pytest.fixture
    def enforcer(self):
        return CapabilityEnforcerService()

    @pytest.fixture
    def sovereign_alice(self):
        return SovereignContext(
            identity_id="Alice",
            signature="sig_alice_123",  # Mock signature
            roles=["user"],
        )

    def test_anti_mayavad_rejection(self, enforcer):
        """Testet, dass Anfragen ohne Souverän sofort abgelehnt werden."""
        ctx = EnforceContext(
            caller_id="Alice",
            resource="flight_system",
            action="access",
            sovereign=None,  # <-- KEIN SOUVERÄN (Mayavad)
        )

        verdict = enforcer.enforce("access", ctx)
        assert verdict == Verdict.DENY

    def test_identity_spoofing_prevention(self, enforcer, sovereign_alice):
        """Testet, dass man nicht unter falscher Flagge segeln kann."""
        ctx = EnforceContext(
            caller_id="Bob",  # <-- Bob behauptet er handelt...
            resource="flight_system",
            action="access",
            sovereign=sovereign_alice,  # <-- ...aber Alice hat unterschrieben!
        )

        verdict = enforcer.enforce("access", ctx)
        assert verdict == Verdict.DENY

    def test_legitimate_access(self, enforcer, sovereign_alice):
        """Testet den glücklichen Pfad (Dharma)."""
        ctx = EnforceContext(caller_id="Alice", resource="some_capability", action="access", sovereign=sovereign_alice)

        # Default policy ist allow für 'access' wenn capability registered
        # (CapabilityEnforcer deferiert an Kernel für Details, hier True als Mock)
        verdict = enforcer.enforce("access", ctx)
        assert verdict == Verdict.ALLOW

    def test_system_revocation(self, enforcer):
        """Testet, dass System-Identitäten mit korrektem Kontext revoken dürfen."""
        sys_sov = SovereignContext(identity_id="KERNEL", signature="sys_sig")

        ctx = EnforceContext(caller_id="KERNEL", resource="Alice", action="revoke", sovereign=sys_sov)

        verdict = enforcer.enforce("revoke", ctx)
        assert verdict == Verdict.ALLOW
