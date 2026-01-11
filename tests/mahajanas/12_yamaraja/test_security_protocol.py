"""
YAMARAJA SECURITY PROTOCOL TESTS
================================
TAG 0 Foundation Tests - WATERTIGHT Security

Tests for:
- SecurityLevel hierarchy (SUBSTRATE to APPLICATION)
- SecurityProtocol interface
- YamarajaService implementation
- Capability management (grant/revoke/check)
- Violation recording and response
- Self-audit functionality
- Quarantine system
- Ajamil Exception (Holy Name override)

"Even Brahma fears Yamaraja. Only the Holy Name is above him."
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from vibe_core.protocols.mahajanas.yamaraja import (
    Judgeable,
    JudgmentRecord,
    NullYamaraja,
    Verdict,
    YamarajaProtocol,
)
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.mahajanas.yamaraja.security import (
    NullSecurityProtocol,
    SecuredSubject,
    SecurityAuditRecord,
    SecurityCapability,
    SecurityLevel,
    SecurityProtocol,
    SecurityStateSnapshot,
    SecurityViolation,
)
from vibe_core.protocols.mahajanas.router import Mahajana


# =============================================================================
# MOCK LEDGER FOR TESTING
# =============================================================================


class MockLedger:
    """Mock ledger for testing without real persistence."""

    def __init__(self):
        self._events = []

    def record_event(self, event_type: str, agent_id: str, details: dict) -> str:
        event_id = f"EVT-{len(self._events)}"
        self._events.append({
            "event_id": event_id,
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
        })
        return event_id

    def get_events(self, event_type: str = None, limit: int = 100):
        events = self._events
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        return events[:limit]

    def count_events(self):
        return len(self._events)


# =============================================================================
# SECURITY LEVEL TESTS
# =============================================================================


class TestSecurityLevel:
    """Tests for SecurityLevel enum."""

    def test_level_hierarchy_values(self):
        """SecurityLevel values must be ordered from strictest to least strict."""
        assert SecurityLevel.SUBSTRATE.value == -1
        assert SecurityLevel.KERNEL.value == 0
        assert SecurityLevel.DEFENSE.value == 1
        assert SecurityLevel.NAGA.value == 2
        assert SecurityLevel.PLUGIN.value == 3
        assert SecurityLevel.APPLICATION.value == 4

    def test_level_ordering(self):
        """Lower values = stricter security."""
        levels = list(SecurityLevel)
        for i in range(len(levels) - 1):
            assert levels[i].value < levels[i + 1].value

    def test_critical_levels(self):
        """SUBSTRATE and KERNEL are critical levels."""
        assert SecurityLevel.SUBSTRATE.is_critical is True
        assert SecurityLevel.KERNEL.is_critical is True
        assert SecurityLevel.DEFENSE.is_critical is False
        assert SecurityLevel.NAGA.is_critical is False
        assert SecurityLevel.PLUGIN.is_critical is False
        assert SecurityLevel.APPLICATION.is_critical is False

    def test_response_types(self):
        """Each level has a defined response type."""
        assert SecurityLevel.SUBSTRATE.response_type == "SYSTEM_HALT"
        assert SecurityLevel.KERNEL.response_type == "KERNEL_PANIC"
        assert SecurityLevel.DEFENSE.response_type == "AUTO_HEAL"
        assert SecurityLevel.NAGA.response_type == "NAGA_RESPONSE"
        assert SecurityLevel.PLUGIN.response_type == "LOG_ALERT"
        assert SecurityLevel.APPLICATION.response_type == "USER_NOTIFY"


# =============================================================================
# SECURITY TYPEDDICT TESTS (WATERTIGHT)
# =============================================================================


class TestSecurityTypedDicts:
    """Test that all TypedDicts are properly structured."""

    def test_security_capability_structure(self):
        """SecurityCapability must have all required fields."""
        cap = SecurityCapability(
            name="read_file",
            level=SecurityLevel.APPLICATION.value,
            granted_by="admin",
            granted_at=datetime.now().isoformat(),
            expires_at=None,
            conditions=[],
        )
        assert "name" in cap
        assert "level" in cap
        assert "granted_by" in cap
        assert "granted_at" in cap
        assert "expires_at" in cap
        assert "conditions" in cap

    def test_security_violation_structure(self):
        """SecurityViolation must have all required fields."""
        violation = SecurityViolation(
            violation_id="VIO-001",
            level=SecurityLevel.DEFENSE.value,
            source="test_agent",
            target="test_resource",
            violation_type="unauthorized_access",
            details="Attempted access without capability",
            timestamp=datetime.now().isoformat(),
            response_taken="LOG_ALERT",
        )
        assert "violation_id" in violation
        assert "level" in violation
        assert "source" in violation
        assert "target" in violation
        assert "violation_type" in violation
        assert "details" in violation
        assert "timestamp" in violation
        assert "response_taken" in violation

    def test_security_audit_record_structure(self):
        """SecurityAuditRecord must have all required fields."""
        record = SecurityAuditRecord(
            audit_id="AUD-001",
            operation="grant_capability",
            subject="test_agent",
            level=SecurityLevel.APPLICATION.value,
            verdict=Verdict.ALLOW.value,
            reason="Test grant",
            timestamp=datetime.now().isoformat(),
            duration_ms=1.5,
            holy_name_checked=False,
        )
        assert "audit_id" in record
        assert "operation" in record
        assert "subject" in record
        assert "level" in record
        assert "verdict" in record
        assert "reason" in record
        assert "timestamp" in record
        assert "duration_ms" in record
        assert "holy_name_checked" in record

    def test_security_state_snapshot_structure(self):
        """SecurityStateSnapshot must have all required fields."""
        snapshot = SecurityStateSnapshot(
            snapshot_id="SNAP-001",
            timestamp=datetime.now().isoformat(),
            active_level=SecurityLevel.APPLICATION.value,
            capabilities_count=10,
            violations_24h=0,
            health_score=1.0,
        )
        assert "snapshot_id" in snapshot
        assert "timestamp" in snapshot
        assert "active_level" in snapshot
        assert "capabilities_count" in snapshot
        assert "violations_24h" in snapshot
        assert "health_score" in snapshot


# =============================================================================
# SECURED SUBJECT TESTS
# =============================================================================


class TestSecuredSubject:
    """Tests for SecuredSubject dataclass."""

    def test_secured_subject_creation(self):
        """SecuredSubject can be created with capabilities."""
        subject = SecuredSubject(
            subject_type="agent",
            subject_id="agent_001",
            capabilities=frozenset(["read_file", "write_file"]),
            security_level=SecurityLevel.APPLICATION,
        )
        assert subject.subject_type == "agent"
        assert subject.subject_id == "agent_001"
        assert subject.has_capability("read_file")
        assert subject.has_capability("write_file")
        assert not subject.has_capability("delete_file")

    def test_secured_subject_to_judgeable(self):
        """SecuredSubject can convert to base Judgeable."""
        subject = SecuredSubject(
            subject_type="agent",
            subject_id="agent_001",
            capabilities=frozenset(["read_file"]),
        )
        judgeable = subject.to_judgeable()
        assert isinstance(judgeable, Judgeable)
        assert judgeable.subject_type == "agent"
        assert judgeable.subject_id == "agent_001"


# =============================================================================
# NULL YAMARAJA TESTS
# =============================================================================


class TestNullYamaraja:
    """Tests for NullYamaraja (maximum mercy)."""

    def test_null_yamaraja_always_grants_mercy(self):
        """NullYamaraja always returns MERCY verdict."""
        yamaraja = NullYamaraja()
        judgeable = Judgeable(
            subject_type="test",
            subject_id="test_001",
            karma_history=["bad_action_1", "bad_action_2"],
        )
        verdict = yamaraja.judge(judgeable)
        assert verdict == Verdict.MERCY

    def test_null_yamaraja_holy_name_always_true(self):
        """NullYamaraja always finds Holy Name."""
        yamaraja = NullYamaraja()
        assert yamaraja.check_holy_name(object()) is True

    def test_null_yamaraja_no_assertions(self):
        """NullYamaraja does not assert."""
        yamaraja = NullYamaraja()
        # Should not raise even for false condition
        yamaraja.assert_truth(False, "This would normally fail")


# =============================================================================
# NULL SECURITY PROTOCOL TESTS
# =============================================================================


class TestNullSecurityProtocol:
    """Tests for NullSecurityProtocol (testing/development mode)."""

    def test_null_security_default_level(self):
        """NullSecurityProtocol defaults to APPLICATION level."""
        security = NullSecurityProtocol()
        assert security.active_level == SecurityLevel.APPLICATION

    def test_null_security_level_change(self):
        """NullSecurityProtocol allows any level change."""
        security = NullSecurityProtocol()
        result = security.set_level(SecurityLevel.SUBSTRATE, "testing")
        assert result is True
        assert security.active_level == SecurityLevel.SUBSTRATE

    def test_null_security_capability_grant(self):
        """NullSecurityProtocol grants any capability."""
        security = NullSecurityProtocol()
        cap = security.grant_capability(
            subject_id="agent_001",
            capability="admin_access",
            granter_id="system",
        )
        assert cap["name"] == "admin_access"
        assert cap["granted_by"] == "system"

    def test_null_security_capability_check(self):
        """NullSecurityProtocol always allows capability."""
        security = NullSecurityProtocol()
        # Without granting, still returns True (maximum mercy)
        assert security.check_capability("any_agent", "any_capability") is True

    def test_null_security_judge_mercy(self):
        """NullSecurityProtocol always judges MERCY."""
        security = NullSecurityProtocol()
        verdict = security.judge(object())
        assert verdict == Verdict.MERCY

    def test_null_security_self_audit(self):
        """NullSecurityProtocol audit shows perfect health."""
        security = NullSecurityProtocol()
        snapshot = security.audit_self()
        assert snapshot["health_score"] == 1.0
        assert snapshot["violations_24h"] == 0


# =============================================================================
# YAMARAJA SERVICE TESTS
# =============================================================================


class TestYamarajaService:
    """Tests for YamarajaService implementation."""

    @pytest.fixture
    def service(self):
        """Create YamarajaService with mock ledger."""
        from vibe_core.services.yamaraja_service import YamarajaService
        ledger = MockLedger()
        return YamarajaService(ledger=ledger)

    def test_service_initialization(self, service):
        """YamarajaService initializes correctly."""
        assert service.owner == Mahajana.YAMARAJA
        assert service.active_level == SecurityLevel.APPLICATION

    def test_service_level_change(self, service):
        """YamarajaService can change security level."""
        result = service.set_level(SecurityLevel.DEFENSE, "escalation test")
        assert result is True
        assert service.active_level == SecurityLevel.DEFENSE

    def test_service_substrate_level_denied(self, service):
        """YamarajaService denies direct SUBSTRATE level change."""
        result = service.set_level(SecurityLevel.SUBSTRATE, "unauthorized")
        assert result is False
        assert service.active_level == SecurityLevel.APPLICATION

    def test_service_enforce_level_passes(self, service):
        """enforce_level passes when current level meets minimum."""
        service.set_level(SecurityLevel.DEFENSE, "test")
        # DEFENSE (1) meets APPLICATION (4) minimum
        service.enforce_level(SecurityLevel.APPLICATION)  # Should not raise

    def test_service_enforce_level_fails(self, service):
        """enforce_level raises when current level doesn't meet minimum."""
        from vibe_core.services.yamaraja_service import SecurityError
        # APPLICATION (4) does not meet DEFENSE (1) minimum
        with pytest.raises(SecurityError):
            service.enforce_level(SecurityLevel.DEFENSE)

    def test_service_capability_grant(self, service):
        """YamarajaService can grant capabilities."""
        cap = service.grant_capability(
            subject_id="agent_001",
            capability="read_file",
            granter_id="admin",
        )
        assert cap["name"] == "read_file"
        assert cap["granted_by"] == "admin"
        assert service.check_capability("agent_001", "read_file") is True

    def test_service_capability_revoke(self, service):
        """YamarajaService can revoke capabilities."""
        service.grant_capability(
            subject_id="agent_001",
            capability="read_file",
            granter_id="admin",
        )
        assert service.check_capability("agent_001", "read_file") is True

        result = service.revoke_capability(
            subject_id="agent_001",
            capability="read_file",
            revoker_id="admin",
            reason="security concern",
        )
        assert result is True
        assert service.check_capability("agent_001", "read_file") is False

    def test_service_capability_list(self, service):
        """YamarajaService can list capabilities."""
        service.grant_capability("agent_001", "read_file", "admin")
        service.grant_capability("agent_001", "write_file", "admin")

        caps = service.list_capabilities("agent_001")
        assert len(caps) == 2
        cap_names = [c["name"] for c in caps]
        assert "read_file" in cap_names
        assert "write_file" in cap_names

    def test_service_violation_recording(self, service):
        """YamarajaService records violations."""
        violation = service.record_violation(
            level=SecurityLevel.DEFENSE,
            source="malicious_agent",
            target="protected_resource",
            violation_type="unauthorized_access",
            details="Attempted access without capability",
        )
        assert violation["violation_id"].startswith("VIO-")
        assert violation["level"] == SecurityLevel.DEFENSE.value
        assert violation["response_taken"] == "AUTO_HEAL"

    def test_service_self_audit(self, service):
        """YamarajaService can audit itself."""
        snapshot = service.audit_self()
        assert snapshot["snapshot_id"].startswith("SNAP-")
        assert snapshot["health_score"] == 1.0  # No violations yet

    def test_service_self_audit_health_degradation(self, service):
        """YamarajaService health degrades with violations."""
        # Record some violations
        for i in range(5):
            service.record_violation(
                level=SecurityLevel.PLUGIN,
                source=f"agent_{i}",
                target="resource",
                violation_type="test_violation",
                details="Test",
            )

        snapshot = service.audit_self()
        assert snapshot["health_score"] < 1.0
        assert snapshot["violations_24h"] == 5

    def test_service_quarantine(self, service):
        """YamarajaService can quarantine subjects."""
        service.grant_capability("agent_001", "read_file", "admin")
        assert service.check_capability("agent_001", "read_file") is True

        result = service.quarantine("agent_001", "suspicious activity", duration_seconds=3600)
        assert result is True
        assert service.check_capability("agent_001", "read_file") is False


# =============================================================================
# AJAMIL EXCEPTION TESTS
# =============================================================================


class TestAjamilException:
    """
    Tests for the Ajamil Exception.
    The Holy Name overrides ALL judgment.
    """

    @pytest.fixture
    def service(self):
        """Create YamarajaService with mock ledger."""
        from vibe_core.services.yamaraja_service import YamarajaService
        return YamarajaService(ledger=MockLedger())

    def test_holy_name_in_karma_history(self, service):
        """Subject with Holy Name in karma gets MERCY."""
        judgeable = Judgeable(
            subject_type="soul",
            subject_id="ajamil",
            karma_history=["sin_1", "sin_2", "NARAYANA", "sin_3"],
        )
        assert service.check_holy_name(judgeable) is True
        verdict = service.judge(judgeable)
        assert verdict == Verdict.MERCY

    def test_hare_krishna_detection(self, service):
        """All forms of Holy Name are detected."""
        names_to_test = ["HARE", "KRISHNA", "RAMA", "NARAYANA", "GOVINDA", "HARI"]

        for name in names_to_test:
            judgeable = Judgeable(
                subject_type="soul",
                subject_id=f"devotee_{name.lower()}",
                karma_history=[f"chanted {name}"],
            )
            assert service.check_holy_name(judgeable) is True, f"Failed for {name}"

    def test_no_holy_name_normal_judgment(self, service):
        """Subject without Holy Name gets normal judgment."""
        judgeable = Judgeable(
            subject_type="soul",
            subject_id="materialist",
            karma_history=["good_action", "neutral_action"],
        )
        assert service.check_holy_name(judgeable) is False
        # Normal judgment based on karma (neutral = ALLOW)
        verdict = service.judge(judgeable)
        assert verdict in [Verdict.ALLOW, Verdict.ATONE]


# =============================================================================
# DEFENSE PROTOCOL INTEGRATION TESTS
# =============================================================================


class TestDefenseIntegration:
    """Tests for 4 Regulating Principles integration."""

    @pytest.fixture
    def service(self):
        """Create YamarajaService with mock ledger."""
        from vibe_core.services.yamaraja_service import YamarajaService
        return YamarajaService(ledger=MockLedger())

    def test_get_sanitizer(self, service):
        """get_sanitizer returns DAYA (Mercy) implementation."""
        from vibe_core.protocols.defense import IDataSanitizer
        sanitizer = service.get_sanitizer()
        assert isinstance(sanitizer, IDataSanitizer)

    def test_get_verifier(self, service):
        """get_verifier returns SATYAM (Truth) implementation."""
        from vibe_core.protocols.defense import IOutputVerifier
        verifier = service.get_verifier()
        assert isinstance(verifier, IOutputVerifier)

    def test_get_resource_manager(self, service):
        """get_resource_manager returns TAPAS (Austerity) implementation."""
        from vibe_core.protocols.defense import IResourceManager
        manager = service.get_resource_manager()
        assert isinstance(manager, IResourceManager)

    def test_get_network_guard(self, service):
        """get_network_guard returns SAUCAM (Cleanliness) implementation."""
        from vibe_core.protocols.defense import INetworkGuard
        guard = service.get_network_guard()
        assert isinstance(guard, INetworkGuard)


# =============================================================================
# OWNER VERIFICATION
# =============================================================================


class TestOwnership:
    """Tests for Mahajana ownership verification."""

    def test_yamaraja_owns_security(self):
        """Security is owned by Yamaraja (12th Mahajana) - Position 15."""
        from vibe_core.mahamantra import mahamantra
        # Yamaraja is at position 15 in the Mahamantra
        pos = mahamantra[15]
        assert pos.guardian == Mahajana.YAMARAJA
        # Protocol base derives ownership from position
        assert mahamantra.protocols.yamaraja._position_index == 15

    @pytest.fixture
    def service(self):
        """Create YamarajaService with mock ledger."""
        from vibe_core.services.yamaraja_service import YamarajaService
        return YamarajaService(ledger=MockLedger())

    def test_service_owner(self, service):
        """YamarajaService has correct owner."""
        assert service.owner == Mahajana.YAMARAJA
