"""
TESTS: _steward.py - The Steward Protocol
==========================================

REAL TESTS for:
1. Steward constants
2. StewardMode, StewardHealth enums
3. StewardState dataclass
4. StewardAudit dataclass
5. StewardSystem class
"""

import pytest
from vibe_core.mahamantra.protocols._steward import (
    # Constants
    STEWARD_NAME,
    STEWARD_VERSION,
    KSETRA,
    KSETRAJNA,
    MAHAJANAS,
    POSITIONS,
    # Enums
    StewardMode,
    StewardHealth,
    # Dataclasses
    StewardState,
    StewardAudit,
    # System
    StewardSystem,
    # Protocol
    StewardProtocolDef,
    # Convenience
    get_steward,
    steward,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestStewardConstants:
    """Test Steward constants."""

    def test_steward_name(self):
        """STEWARD_NAME is 'Steward'."""
        assert STEWARD_NAME == "Steward"

    def test_steward_version(self):
        """STEWARD_VERSION includes PARAMPARA (37)."""
        assert "37" in STEWARD_VERSION

    def test_ksetra_is_24(self):
        """KSETRA is 24."""
        assert KSETRA == 24

    def test_ksetrajna_is_1(self):
        """KSETRAJNA is 1."""
        assert KSETRAJNA == 1

    def test_mahajanas_is_12(self):
        """MAHAJANAS has 12 elements."""
        assert len(MAHAJANAS) == 12

    def test_positions_is_16(self):
        """POSITIONS is 16."""
        assert POSITIONS == 16


# =============================================================================
# StewardMode Enum Tests
# =============================================================================


class TestStewardMode:
    """Test StewardMode enum."""

    def test_steward_mode_seed(self):
        """StewardMode has SEED."""
        assert StewardMode.SEED.value == "seed"

    def test_steward_mode_awakening(self):
        """StewardMode has AWAKENING."""
        assert StewardMode.AWAKENING.value == "awakening"

    def test_steward_mode_active(self):
        """StewardMode has ACTIVE."""
        assert StewardMode.ACTIVE.value == "active"

    def test_steward_mode_governance(self):
        """StewardMode has GOVERNANCE."""
        assert StewardMode.GOVERNANCE.value == "governance"

    def test_steward_mode_maintenance(self):
        """StewardMode has MAINTENANCE."""
        assert StewardMode.MAINTENANCE.value == "maintenance"

    def test_steward_mode_hibernation(self):
        """StewardMode has HIBERNATION."""
        assert StewardMode.HIBERNATION.value == "hibernation"

    def test_steward_mode_moksha(self):
        """StewardMode has MOKSHA."""
        assert StewardMode.MOKSHA.value == "moksha"


# =============================================================================
# StewardHealth Enum Tests
# =============================================================================


class TestStewardHealth:
    """Test StewardHealth enum."""

    def test_steward_health_pristine(self):
        """StewardHealth has PRISTINE."""
        assert StewardHealth.PRISTINE.value == "pristine"

    def test_steward_health_healthy(self):
        """StewardHealth has HEALTHY."""
        assert StewardHealth.HEALTHY.value == "healthy"

    def test_steward_health_degraded(self):
        """StewardHealth has DEGRADED."""
        assert StewardHealth.DEGRADED.value == "degraded"

    def test_steward_health_critical(self):
        """StewardHealth has CRITICAL."""
        assert StewardHealth.CRITICAL.value == "critical"

    def test_steward_health_failing(self):
        """StewardHealth has FAILING."""
        assert StewardHealth.FAILING.value == "failing"


# =============================================================================
# StewardState Tests
# =============================================================================


class TestStewardState:
    """Test StewardState dataclass."""

    def test_steward_state_creation(self):
        """StewardState can be created."""
        state = StewardState()
        assert state.name == STEWARD_NAME
        assert state.version == STEWARD_VERSION

    def test_steward_state_default_mode(self):
        """Default mode is SEED."""
        state = StewardState()
        assert state.mode == StewardMode.SEED

    def test_steward_state_default_health(self):
        """Default health is PRISTINE."""
        state = StewardState()
        assert state.health == StewardHealth.PRISTINE

    def test_steward_state_heartbeat(self):
        """heartbeat updates timestamp and connection."""
        state = StewardState()
        state.heartbeat()
        assert state.last_heartbeat is not None
        assert state.parampara_connected is True

    def test_steward_state_awaken(self):
        """awaken changes mode and sets started_at."""
        state = StewardState()
        state.awaken()
        assert state.mode == StewardMode.AWAKENING
        assert state.started_at is not None

    def test_steward_state_activate(self):
        """activate changes mode to ACTIVE."""
        state = StewardState()
        state.activate()
        assert state.mode == StewardMode.ACTIVE

    def test_steward_state_enter_governance(self):
        """enter_governance changes mode to GOVERNANCE."""
        state = StewardState()
        state.enter_governance()
        assert state.mode == StewardMode.GOVERNANCE

    def test_steward_state_shutdown(self):
        """shutdown changes mode to MOKSHA."""
        state = StewardState()
        state.shutdown()
        assert state.mode == StewardMode.MOKSHA


# =============================================================================
# StewardAudit Tests
# =============================================================================


class TestStewardAudit:
    """Test StewardAudit dataclass."""

    def test_steward_audit_creation(self):
        """StewardAudit can be created."""
        state = StewardState()
        audit = StewardAudit(
            timestamp="2024-01-01T00:00:00",
            state=state,
            health_score=1.0,
            protocol_count=10,
            protocol_issues=[],
            bridge_count=5,
            bridge_issues=[],
            parampara_connected=True,
            disconnected_protocols=[],
        )
        assert audit.health_score == 1.0

    def test_steward_audit_is_healthy(self):
        """is_healthy returns True for score >= 0.8."""
        state = StewardState()
        audit = StewardAudit(
            timestamp="2024-01-01",
            state=state,
            health_score=0.8,
            protocol_count=0,
            protocol_issues=[],
            bridge_count=0,
            bridge_issues=[],
            parampara_connected=True,
            disconnected_protocols=[],
        )
        assert audit.is_healthy is True

    def test_steward_audit_is_unhealthy(self):
        """is_healthy returns False for score < 0.8."""
        state = StewardState()
        audit = StewardAudit(
            timestamp="2024-01-01",
            state=state,
            health_score=0.7,
            protocol_count=0,
            protocol_issues=[],
            bridge_count=0,
            bridge_issues=[],
            parampara_connected=True,
            disconnected_protocols=[],
        )
        assert audit.is_healthy is False

    def test_steward_audit_summary(self):
        """summary returns formatted string."""
        state = StewardState()
        audit = StewardAudit(
            timestamp="2024-01-01",
            state=state,
            health_score=1.0,
            protocol_count=10,
            protocol_issues=[],
            bridge_count=5,
            bridge_issues=[],
            parampara_connected=True,
            disconnected_protocols=[],
        )
        summary = audit.summary
        assert "Steward Audit" in summary
        assert "Health: 100%" in summary
        assert "Protocols: 10" in summary


# =============================================================================
# StewardSystem Tests
# =============================================================================


class TestStewardSystem:
    """Test StewardSystem class."""

    def test_steward_system_singleton(self):
        """StewardSystem is singleton."""
        sys1 = StewardSystem()
        sys2 = StewardSystem()
        assert sys1 is sys2

    def test_steward_system_state(self):
        """state property returns StewardState."""
        system = StewardSystem()
        assert isinstance(system.state, StewardState)

    def test_steward_system_awaken(self):
        """awaken changes state mode."""
        system = StewardSystem()
        system.awaken()
        assert system.state.mode == StewardMode.AWAKENING

    def test_steward_system_activate(self):
        """activate changes state mode."""
        system = StewardSystem()
        system.activate()
        assert system.state.mode == StewardMode.ACTIVE

    def test_steward_system_heartbeat(self):
        """heartbeat updates state."""
        system = StewardSystem()
        system.heartbeat()
        assert system.state.last_heartbeat is not None

    def test_steward_system_lotus(self):
        """lotus property returns LotusHologram."""
        system = StewardSystem()
        from vibe_core.mahamantra.protocols._lotus import LotusHologram
        assert isinstance(system.lotus, LotusHologram)

    def test_steward_system_graph(self):
        """graph property returns ProtocolGraph."""
        system = StewardSystem()
        from vibe_core.mahamantra.protocols._graph import ProtocolGraph
        assert isinstance(system.graph, ProtocolGraph)

    def test_steward_system_bridges(self):
        """bridges property returns BridgeRegistry."""
        system = StewardSystem()
        from vibe_core.mahamantra.protocols._bridge import BridgeRegistry
        assert isinstance(system.bridges, BridgeRegistry)

    def test_steward_system_audit(self):
        """audit returns StewardAudit."""
        system = StewardSystem()
        audit = system.audit()
        assert isinstance(audit, StewardAudit)


# =============================================================================
# Convenience Functions Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_steward_returns_system(self):
        """get_steward returns StewardSystem."""
        system = get_steward()
        assert isinstance(system, StewardSystem)

    def test_get_steward_is_singleton(self):
        """get_steward returns same instance."""
        sys1 = get_steward()
        sys2 = get_steward()
        assert sys1 is sys2

    def test_steward_alias(self):
        """steward is alias for get_steward."""
        sys1 = steward()
        sys2 = get_steward()
        assert sys1 is sys2


# =============================================================================
# StewardProtocolDef Tests
# =============================================================================


class TestStewardProtocolDef:
    """Test StewardProtocolDef."""

    def test_steward_protocol_validates(self):
        """StewardProtocolDef validates."""
        valid, violations = StewardProtocolDef.validate()
        assert valid is True

    def test_steward_protocol_identity(self):
        """StewardProtocolDef has correct identity."""
        identity = StewardProtocolDef.get_identity()
        assert identity.name == "StewardProtocol"
        assert identity.mahajana == "prithu"

    def test_steward_protocol_provides(self):
        """StewardProtocolDef provides system capabilities."""
        cap = StewardProtocolDef.get_capability()
        assert "system_identity" in cap.provides
        assert "system_lifecycle" in cap.provides
        assert "system_audit" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _steward
        expected = [
            "StewardMode",
            "StewardHealth",
            "StewardState",
            "StewardAudit",
            "StewardSystem",
            "StewardProtocolDef",
            "get_steward",
            "steward",
        ]
        for item in expected:
            assert item in _steward.__all__, f"{item} should be in __all__"
