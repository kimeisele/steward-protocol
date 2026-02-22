"""
TESTS: _ouroboros.py - The Ouroboros Protocol
==============================================

REAL TESTS for:
1. Ouroboros constants
2. BodyType, BodyHealth, GeneActivationState, HealingPattern enums
3. OuroborosEventType enum
4. OuroborosEvent dataclass
5. NullGene implementation
6. OuroborosProtocol
"""

import pytest
from vibe_core.mahamantra.protocols._ouroboros import (
    # Constants
    OUROBOROS_CYCLE,
    BODY_COUNT,
    LAYER_PRAKRITI,
    LAYER_SHESHA,
    LAYER_OUROBOROS,
    LAYER_SERVICE,
    # Body types
    BodyType,
    BodyHealth,
    # Gene states
    GeneActivationState,
    # Healing patterns
    HealingPattern,
    # Event types
    OuroborosEventType,
    # Event
    OuroborosEvent,
    # Null implementation
    NullGene,
    # The Protocol
    OuroborosProtocol,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestOuroborosConstants:
    """Test Ouroboros constants."""

    def test_ouroboros_cycle_is_108(self):
        """OUROBOROS_CYCLE is 108."""
        assert OUROBOROS_CYCLE == 108

    def test_body_count_is_3(self):
        """BODY_COUNT is 3."""
        assert BODY_COUNT == 3

    def test_layer_prakriti(self):
        """LAYER_PRAKRITI is -2."""
        assert LAYER_PRAKRITI == -2

    def test_layer_shesha(self):
        """LAYER_SHESHA is -1."""
        assert LAYER_SHESHA == -1

    def test_layer_ouroboros(self):
        """LAYER_OUROBOROS is 0."""
        assert LAYER_OUROBOROS == 0

    def test_layer_service(self):
        """LAYER_SERVICE is 1."""
        assert LAYER_SERVICE == 1


# =============================================================================
# BodyType Enum Tests
# =============================================================================


class TestBodyType:
    """Test BodyType enum."""

    def test_body_type_sthula(self):
        """BodyType has STHULA."""
        assert BodyType.STHULA.value == "sthula"

    def test_body_type_prana(self):
        """BodyType has PRANA."""
        assert BodyType.PRANA.value == "prana"

    def test_body_type_purusha(self):
        """BodyType has PURUSHA."""
        assert BodyType.PURUSHA.value == "purusha"

    def test_body_type_count(self):
        """There are 3 body types."""
        assert len(BodyType) == 3


# =============================================================================
# BodyHealth Enum Tests
# =============================================================================


class TestBodyHealth:
    """Test BodyHealth enum."""

    def test_body_health_pristine(self):
        """BodyHealth has PRISTINE."""
        assert BodyHealth.PRISTINE.value == "pristine"

    def test_body_health_healthy(self):
        """BodyHealth has HEALTHY."""
        assert BodyHealth.HEALTHY.value == "healthy"

    def test_body_health_degraded(self):
        """BodyHealth has DEGRADED."""
        assert BodyHealth.DEGRADED.value == "degraded"

    def test_body_health_critical(self):
        """BodyHealth has CRITICAL."""
        assert BodyHealth.CRITICAL.value == "critical"

    def test_body_health_dissolved(self):
        """BodyHealth has DISSOLVED."""
        assert BodyHealth.DISSOLVED.value == "dissolved"


# =============================================================================
# GeneActivationState Enum Tests
# =============================================================================


class TestGeneActivationState:
    """Test GeneActivationState enum."""

    def test_gene_state_dormant(self):
        """GeneActivationState has DORMANT."""
        assert GeneActivationState.DORMANT.value == "dormant"

    def test_gene_state_activating(self):
        """GeneActivationState has ACTIVATING."""
        assert GeneActivationState.ACTIVATING.value == "activating"

    def test_gene_state_active(self):
        """GeneActivationState has ACTIVE."""
        assert GeneActivationState.ACTIVE.value == "active"

    def test_gene_state_healing(self):
        """GeneActivationState has HEALING."""
        assert GeneActivationState.HEALING.value == "healing"

    def test_gene_state_dissolving(self):
        """GeneActivationState has DISSOLVING."""
        assert GeneActivationState.DISSOLVING.value == "dissolving"

    def test_gene_state_dead(self):
        """GeneActivationState has DEAD."""
        assert GeneActivationState.DEAD.value == "dead"


# =============================================================================
# HealingPattern Enum Tests
# =============================================================================


class TestHealingPattern:
    """Test HealingPattern enum."""

    def test_healing_pattern_arjuna(self):
        """HealingPattern has ARJUNA."""
        assert HealingPattern.ARJUNA.value == "arjuna"

    def test_healing_pattern_pralaya(self):
        """HealingPattern has PRALAYA."""
        assert HealingPattern.PRALAYA.value == "pralaya"

    def test_healing_pattern_resurrection(self):
        """HealingPattern has RESURRECTION."""
        assert HealingPattern.RESURRECTION.value == "resurrection"


# =============================================================================
# OuroborosEventType Enum Tests
# =============================================================================


class TestOuroborosEventType:
    """Test OuroborosEventType enum."""

    def test_event_type_gene_registered(self):
        """OuroborosEventType has GENE_REGISTERED."""
        assert OuroborosEventType.GENE_REGISTERED.value == "gene.registered"

    def test_event_type_heartbeat(self):
        """OuroborosEventType has HEARTBEAT."""
        assert OuroborosEventType.HEARTBEAT.value == "system.heartbeat"

    def test_event_type_pralaya(self):
        """OuroborosEventType has PRALAYA_INITIATED."""
        assert OuroborosEventType.PRALAYA_INITIATED.value == "system.pralaya"


# =============================================================================
# OuroborosEvent Tests
# =============================================================================


class TestOuroborosEvent:
    """Test OuroborosEvent dataclass."""

    def test_ouroboros_event_creation(self):
        """OuroborosEvent can be created."""
        event = OuroborosEvent(
            event_type=OuroborosEventType.HEARTBEAT,
            source="system",
        )
        assert event.event_type == OuroborosEventType.HEARTBEAT
        assert event.source == "system"

    def test_ouroboros_event_is_frozen(self):
        """OuroborosEvent is frozen."""
        event = OuroborosEvent(
            event_type=OuroborosEventType.HEARTBEAT,
            source="test",
        )
        with pytest.raises(Exception):
            event.source = "changed"


# =============================================================================
# NullGene Tests
# =============================================================================


class TestNullGene:
    """Test NullGene implementation."""

    def test_null_gene_creation(self):
        """NullGene can be created."""
        gene = NullGene("test")
        assert gene.manifest["name"] == "test"

    def test_null_gene_default_state(self):
        """NullGene starts in DORMANT state."""
        gene = NullGene()
        assert gene.state == GeneActivationState.DORMANT

    def test_null_gene_activate(self):
        """NullGene.activate works."""
        gene = NullGene()
        result = gene.activate()
        assert result is True
        assert gene.state == GeneActivationState.ACTIVE

    def test_null_gene_deactivate(self):
        """NullGene.deactivate works."""
        gene = NullGene()
        gene.activate()
        result = gene.deactivate()
        assert result is True
        assert gene.state == GeneActivationState.DORMANT

    def test_null_gene_health(self):
        """NullGene.get_health returns HEALTHY."""
        gene = NullGene()
        assert gene.get_health() == BodyHealth.HEALTHY

    def test_null_gene_snapshot(self):
        """NullGene.snapshot returns None."""
        gene = NullGene()
        assert gene.snapshot() is None

    def test_null_gene_restore(self):
        """NullGene.restore returns True."""
        gene = NullGene()
        assert gene.restore("any_path") is True


# =============================================================================
# OuroborosProtocol Tests
# =============================================================================


class TestOuroborosProtocol:
    """Test OuroborosProtocol."""

    def test_ouroboros_protocol_validates(self):
        """OuroborosProtocol validates."""
        valid, violations = OuroborosProtocol.validate()
        assert valid is True

    def test_ouroboros_protocol_identity(self):
        """OuroborosProtocol has correct identity."""
        identity = OuroborosProtocol.get_identity()
        assert identity.name == "OuroborosProtocol"
        assert identity.mahajana == "shuka"
        assert identity.position == 14

    def test_ouroboros_protocol_provides(self):
        """OuroborosProtocol provides ouroboros capabilities."""
        cap = OuroborosProtocol.get_capability()
        assert "gene_registry" in cap.provides
        assert "self_healing" in cap.provides
        assert "resurrection" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _ouroboros

        expected = [
            "OUROBOROS_CYCLE",
            "BodyType",
            "BodyHealth",
            "GeneActivationState",
            "HealingPattern",
            "OuroborosEventType",
            "OuroborosEvent",
            "NullGene",
            "OuroborosProtocol",
        ]
        for item in expected:
            assert item in _ouroboros.__all__, f"{item} should be in __all__"
