"""
TESTS: _holographic.py - The Holographic Protocol
==================================================

REAL TESTS for:
1. Hologram class
2. CoherenceLevel enum
3. CoherencePolicy dataclass
4. Reflector class
5. Projector class
6. HolographicSystem class
"""

import pytest
from vibe_core.mahamantra.protocols._holographic import (
    # Core
    Hologram,
    # Coherence
    CoherenceLevel,
    CoherencePolicy,
    # Reflection & Projection
    Reflector,
    Projector,
    # System
    HolographicSystem,
    # Protocol
    HolographicProtocol,
    # Singleton
    get_holographic_system,
)


# =============================================================================
# Hologram Tests
# =============================================================================


class TestHologram:
    """Test Hologram class."""

    def test_hologram_creation(self):
        """Hologram can be created."""
        hologram = Hologram(_center="center_value")
        assert hologram.center == "center_value"

    def test_hologram_register(self):
        """register adds part."""
        hologram = Hologram(_center="center")
        hologram.register("part1", "value1")
        assert hologram.get("part1") == "value1"

    def test_hologram_get_not_found(self):
        """get returns None for unknown part."""
        hologram = Hologram(_center="center")
        assert hologram.get("unknown") is None

    def test_hologram_reflect(self):
        """reflect returns all parts."""
        hologram = Hologram(_center="center")
        hologram.register("a", "val_a")
        hologram.register("b", "val_b")
        all_parts = hologram.reflect()
        assert "a" in all_parts
        assert "b" in all_parts

    def test_hologram_project(self):
        """project returns parts with prefix."""
        hologram = Hologram(_center="center")
        hologram.register("brahma.sub1", "v1")
        hologram.register("brahma.sub2", "v2")
        hologram.register("narada.sub1", "v3")
        projected = hologram.project("brahma.")
        assert len(projected) == 2
        assert "brahma.sub1" in projected
        assert "brahma.sub2" in projected

    def test_hologram_all_names(self):
        """all_names returns frozenset of names."""
        hologram = Hologram(_center="center")
        hologram.register("a", 1)
        hologram.register("b", 2)
        names = hologram.all_names()
        assert isinstance(names, frozenset)
        assert "a" in names
        assert "b" in names

    def test_hologram_count(self):
        """count returns number of parts."""
        hologram = Hologram(_center="center")
        assert hologram.count() == 0
        hologram.register("a", 1)
        assert hologram.count() == 1
        hologram.register("b", 2)
        assert hologram.count() == 2


# =============================================================================
# CoherenceLevel Enum Tests
# =============================================================================


class TestCoherenceLevel:
    """Test CoherenceLevel enum."""

    def test_coherence_level_none(self):
        """CoherenceLevel has NONE."""
        assert CoherenceLevel.NONE.value == "none"

    def test_coherence_level_eventual(self):
        """CoherenceLevel has EVENTUAL."""
        assert CoherenceLevel.EVENTUAL.value == "eventual"

    def test_coherence_level_strong(self):
        """CoherenceLevel has STRONG."""
        assert CoherenceLevel.STRONG.value == "strong"

    def test_coherence_level_total(self):
        """CoherenceLevel has TOTAL."""
        assert CoherenceLevel.TOTAL.value == "total"


# =============================================================================
# CoherencePolicy Tests
# =============================================================================


class TestCoherencePolicy:
    """Test CoherencePolicy dataclass."""

    def test_coherence_policy_creation(self):
        """CoherencePolicy can be created."""
        policy = CoherencePolicy(level=CoherenceLevel.STRONG)
        assert policy.level == CoherenceLevel.STRONG

    def test_coherence_policy_defaults(self):
        """CoherencePolicy has correct defaults."""
        policy = CoherencePolicy(level=CoherenceLevel.STRONG)
        assert policy.sync_on_read is False
        assert policy.sync_on_write is True
        assert policy.propagation_delay_ms == 0


# =============================================================================
# Reflector Tests
# =============================================================================


class TestReflector:
    """Test Reflector class."""

    def test_reflector_creation(self):
        """Reflector can be created."""
        hologram = Hologram(_center="center")
        reflector = Reflector(hologram)
        assert reflector is not None

    def test_reflector_reflect_from(self):
        """reflect_from returns all parts."""
        hologram = Hologram(_center="center")
        hologram.register("a", 1)
        hologram.register("b", 2)
        reflector = Reflector(hologram)

        # Reflect from any point gives complete picture
        result = reflector.reflect_from("a")
        assert "a" in result
        assert "b" in result

    def test_reflector_reflect_from_nonexistent(self):
        """reflect_from from nonexistent still works (holographic)."""
        hologram = Hologram(_center="center")
        hologram.register("a", 1)
        reflector = Reflector(hologram)

        # Even from nonexistent point, we see everything
        result = reflector.reflect_from("nonexistent")
        assert "a" in result


# =============================================================================
# Projector Tests
# =============================================================================


class TestProjector:
    """Test Projector class."""

    def test_projector_creation(self):
        """Projector can be created."""
        hologram = Hologram(_center="center")
        projector = Projector(hologram)
        assert projector is not None

    def test_projector_project_to(self):
        """project_to returns specific part."""
        hologram = Hologram(_center="center")
        hologram.register("target", "value")
        projector = Projector(hologram)

        result = projector.project_to("target")
        assert result == "value"

    def test_projector_project_to_not_found(self):
        """project_to returns None for unknown."""
        hologram = Hologram(_center="center")
        projector = Projector(hologram)

        result = projector.project_to("unknown")
        assert result is None


# =============================================================================
# HolographicSystem Tests
# =============================================================================


class TestHolographicSystem:
    """Test HolographicSystem class."""

    def test_holographic_system_create(self):
        """HolographicSystem.create works."""
        system = HolographicSystem.create("center")
        assert system is not None
        assert system.hologram.center == "center"

    def test_holographic_system_register(self):
        """register delegates to hologram."""
        system = HolographicSystem.create("center")
        system.register("part1", "value1")
        assert system.hologram.get("part1") == "value1"

    def test_holographic_system_reflect(self):
        """reflect returns all parts."""
        system = HolographicSystem.create("center")
        system.register("a", 1)
        system.register("b", 2)
        result = system.reflect()
        assert "a" in result
        assert "b" in result

    def test_holographic_system_reflect_from(self):
        """reflect with from_name."""
        system = HolographicSystem.create("center")
        system.register("a", 1)
        result = system.reflect(from_name="a")
        assert "a" in result

    def test_holographic_system_project(self):
        """project returns specific part."""
        system = HolographicSystem.create("center")
        system.register("target", "value")
        result = system.project("target")
        assert result == "value"

    def test_holographic_system_has_reflector_and_projector(self):
        """System has reflector and projector."""
        system = HolographicSystem.create("center")
        assert isinstance(system.reflector, Reflector)
        assert isinstance(system.projector, Projector)

    def test_holographic_system_default_coherence(self):
        """Default coherence is STRONG."""
        system = HolographicSystem.create("center")
        assert system.coherence.level == CoherenceLevel.STRONG


# =============================================================================
# Singleton Tests
# =============================================================================


class TestHolographicSingleton:
    """Test holographic singleton."""

    def test_get_holographic_system_returns_system(self):
        """get_holographic_system returns HolographicSystem."""
        system = get_holographic_system()
        assert isinstance(system, HolographicSystem)

    def test_get_holographic_system_is_singleton(self):
        """get_holographic_system returns same instance."""
        sys1 = get_holographic_system()
        sys2 = get_holographic_system()
        assert sys1 is sys2


# =============================================================================
# HolographicProtocol Tests
# =============================================================================


class TestHolographicProtocol:
    """Test HolographicProtocol."""

    def test_holographic_protocol_validates(self):
        """HolographicProtocol validates."""
        valid, violations = HolographicProtocol.validate()
        assert valid is True

    def test_holographic_protocol_identity(self):
        """HolographicProtocol has correct identity."""
        identity = HolographicProtocol.get_identity()
        assert identity.name == "HolographicProtocol"
        assert identity.mahajana == "narada"

    def test_holographic_protocol_provides(self):
        """HolographicProtocol provides holographic capabilities."""
        cap = HolographicProtocol.get_capability()
        assert "hologram" in cap.provides
        assert "reflection" in cap.provides
        assert "projection" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _holographic

        expected = [
            "Hologram",
            "CoherenceLevel",
            "CoherencePolicy",
            "Reflector",
            "Projector",
            "HolographicSystem",
            "HolographicProtocol",
            "get_holographic_system",
        ]
        for item in expected:
            assert item in _holographic.__all__, f"{item} should be in __all__"
