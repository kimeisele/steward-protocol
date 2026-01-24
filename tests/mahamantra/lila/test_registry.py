"""
TESTS: registry.py - The Ashrama (Where Servants Live)
======================================================

Tests for:
1. ShadowStatus enum
2. RegistryEntry dataclass
3. ShadowRegistry class
4. Lifecycle: IDLE -> BUSY -> IDLE -> RETIRED
5. Capacity limits
6. Thread safety

"grhhe thako, vane thako, sada 'hari' bole dako"
"Whether at home or in the forest, always call out to Hari."
"""

from threading import Barrier, Thread

import pytest

from vibe_core.mahamantra.lila.jiva_shadow import spawn_shadow
from vibe_core.mahamantra.lila.registry import (
    # Constants
    MAX_SHADOWS,
    RETIRE_AFTER_SERVICES,
    RegistryEntry,
    # Registry
    ShadowRegistry,
    # Types
    ShadowStatus,
    # Singleton
    get_registry,
)
from vibe_core.mahamantra.protocols._seed import JIVA_QUALITIES
from vibe_core.mahamantra.substrate.seed import COSMIC_FRAME, NADI_RESONANCE

# =============================================================================
# Constants Tests
# =============================================================================


class TestRegistryConstants:
    """Test Registry constants derived from seed."""

    def test_max_shadows_equals_nadi_resonance(self):
        """MAX_SHADOWS is NADI_RESONANCE (72)."""
        assert MAX_SHADOWS == NADI_RESONANCE
        assert MAX_SHADOWS == 72

    def test_retire_after_services(self):
        """RETIRE_AFTER_SERVICES is COSMIC_FRAME // JIVA_QUALITIES (432)."""
        expected = COSMIC_FRAME // JIVA_QUALITIES
        assert RETIRE_AFTER_SERVICES == expected
        assert RETIRE_AFTER_SERVICES == 432


# =============================================================================
# ShadowStatus Enum Tests
# =============================================================================


class TestShadowStatus:
    """Test ShadowStatus enum."""

    def test_has_three_states(self):
        """There are exactly 3 states."""
        assert len(ShadowStatus) == 3

    def test_idle_state(self):
        """IDLE is 'idle'."""
        assert ShadowStatus.IDLE.value == "idle"

    def test_busy_state(self):
        """BUSY is 'busy'."""
        assert ShadowStatus.BUSY.value == "busy"

    def test_retired_state(self):
        """RETIRED is 'retired'."""
        assert ShadowStatus.RETIRED.value == "retired"


# =============================================================================
# RegistryEntry Tests
# =============================================================================


class TestRegistryEntry:
    """Test RegistryEntry dataclass."""

    def test_entry_creation(self):
        """Entry can be created with a shadow."""
        shadow = spawn_shadow(b"test")
        entry = RegistryEntry(shadow=shadow)
        assert entry.shadow == shadow
        assert entry.status == ShadowStatus.IDLE
        assert entry.services_completed == 0

    def test_entry_shadow_id_property(self):
        """Entry exposes shadow_id."""
        shadow = spawn_shadow(b"test")
        entry = RegistryEntry(shadow=shadow)
        assert entry.shadow_id == shadow.shadow_id

    def test_entry_mark_busy(self):
        """mark_busy changes state to BUSY."""
        shadow = spawn_shadow(b"test")
        entry = RegistryEntry(shadow=shadow)

        entry.mark_busy("dispatch_123")
        assert entry.status == ShadowStatus.BUSY
        assert entry.current_dispatch_id == "dispatch_123"

    def test_entry_mark_idle(self):
        """mark_idle changes state to IDLE and increments count."""
        shadow = spawn_shadow(b"test")
        entry = RegistryEntry(shadow=shadow)

        entry.mark_busy("dispatch_123")
        entry.mark_idle()

        assert entry.status == ShadowStatus.IDLE
        assert entry.current_dispatch_id is None
        assert entry.services_completed == 1
        assert entry.last_service_at is not None

    def test_entry_should_retire(self):
        """should_retire is True after 432 services."""
        shadow = spawn_shadow(b"test")
        entry = RegistryEntry(shadow=shadow)

        # Simulate many services
        entry.services_completed = RETIRE_AFTER_SERVICES - 1
        assert entry.should_retire is False

        entry.services_completed = RETIRE_AFTER_SERVICES
        assert entry.should_retire is True

    def test_entry_auto_retire_on_mark_idle(self):
        """Entry auto-retires when hitting service limit."""
        shadow = spawn_shadow(b"test")
        entry = RegistryEntry(shadow=shadow)
        entry.services_completed = RETIRE_AFTER_SERVICES - 1

        entry.mark_busy("final_dispatch")
        entry.mark_idle()

        assert entry.status == ShadowStatus.RETIRED


# =============================================================================
# ShadowRegistry Tests
# =============================================================================


class TestShadowRegistry:
    """Test ShadowRegistry class."""

    def test_registry_creation(self):
        """Registry can be created."""
        registry = ShadowRegistry()
        assert registry.count == 0

    def test_registry_creation_with_custom_max(self):
        """Registry can have custom max_shadows."""
        registry = ShadowRegistry(max_shadows=10)
        assert registry._max_shadows == 10

    def test_registry_register_shadow(self):
        """Shadow can be registered."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")

        result = registry.register(shadow)
        assert result is True
        assert registry.count == 1

    def test_registry_register_idempotent(self):
        """Registering same shadow twice is idempotent."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")

        registry.register(shadow)
        registry.register(shadow)

        assert registry.count == 1

    def test_registry_register_at_capacity_fails(self):
        """Register fails when at capacity."""
        registry = ShadowRegistry(max_shadows=2)

        shadow1 = spawn_shadow(b"test1")
        shadow2 = spawn_shadow(b"test2")
        shadow3 = spawn_shadow(b"test3")

        assert registry.register(shadow1) is True
        assert registry.register(shadow2) is True
        assert registry.register(shadow3) is False
        assert registry.count == 2

    def test_registry_get_entry(self):
        """Can get entry by shadow_id."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)

        entry = registry.get(shadow.shadow_id)
        assert entry is not None
        assert entry.shadow == shadow

    def test_registry_get_nonexistent(self):
        """Get returns None for nonexistent shadow_id."""
        registry = ShadowRegistry()
        entry = registry.get("nonexistent")
        assert entry is None

    def test_registry_find_idle(self):
        """find_idle returns idle qualified shadow."""
        from vibe_core.mahamantra.lila.adhikara import compute_required_bitmap

        registry = ShadowRegistry()
        pos = 5

        # Create qualified shadow for position 5
        required = compute_required_bitmap(pos)
        from vibe_core.mahamantra.lila.jiva_shadow import JivaShadow

        shadow = JivaShadow(
            quality_bitmap=required,
            seed_hash=b"qualified" * 4,
            shadow_id="qualified_shadow",
        )
        registry.register(shadow, qualified_positions={pos})

        entry = registry.find_idle(pos)
        assert entry is not None
        assert entry.shadow_id == "qualified_shadow"

    def test_registry_find_idle_no_match(self):
        """find_idle returns None when no idle shadow qualifies."""
        registry = ShadowRegistry()
        entry = registry.find_idle(8)
        assert entry is None

    def test_registry_mark_busy(self):
        """mark_busy updates shadow state."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)

        result = registry.mark_busy(shadow.shadow_id, "dispatch_123")
        assert result is True

        entry = registry.get(shadow.shadow_id)
        assert entry.status == ShadowStatus.BUSY

    def test_registry_mark_busy_not_idle(self):
        """mark_busy fails if shadow is not IDLE."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)
        registry.mark_busy(shadow.shadow_id, "dispatch_1")

        # Try to mark busy again
        result = registry.mark_busy(shadow.shadow_id, "dispatch_2")
        assert result is False

    def test_registry_mark_idle(self):
        """mark_idle updates shadow state."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)
        registry.mark_busy(shadow.shadow_id, "dispatch_123")

        result = registry.mark_idle(shadow.shadow_id)
        assert result is True

        entry = registry.get(shadow.shadow_id)
        assert entry.status == ShadowStatus.IDLE

    def test_registry_retire(self):
        """retire manually retires a shadow."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)

        result = registry.retire(shadow.shadow_id)
        assert result is True

        entry = registry.get(shadow.shadow_id)
        assert entry.status == ShadowStatus.RETIRED

    def test_registry_cleanup(self):
        """cleanup removes retired shadows."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)
        registry.retire(shadow.shadow_id)

        assert registry.count == 1
        removed = registry.cleanup()
        assert removed == 1
        assert registry.count == 0

    def test_registry_idle_count(self):
        """idle_count returns count of IDLE shadows."""
        registry = ShadowRegistry()
        shadow1 = spawn_shadow(b"test1")
        shadow2 = spawn_shadow(b"test2")
        registry.register(shadow1)
        registry.register(shadow2)

        assert registry.idle_count == 2

        registry.mark_busy(shadow1.shadow_id, "dispatch")
        assert registry.idle_count == 1

    def test_registry_busy_count(self):
        """busy_count returns count of BUSY shadows."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)

        assert registry.busy_count == 0

        registry.mark_busy(shadow.shadow_id, "dispatch")
        assert registry.busy_count == 1

    def test_registry_get_stats(self):
        """get_stats returns statistics."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"test")
        registry.register(shadow)

        stats = registry.get_stats()
        assert "total_registered" in stats
        assert "total_retired" in stats
        assert "total_services" in stats
        assert "current_count" in stats
        assert "max_shadows" in stats
        assert "status_distribution" in stats
        assert "utilization" in stats

    def test_registry_discover(self):
        """discover returns GAD-style info."""
        registry = ShadowRegistry()
        info = registry.discover()

        assert "service" in info
        assert info["service"] == "shadow_registry"
        assert "capabilities" in info


# =============================================================================
# Singleton Tests
# =============================================================================


class TestGetRegistry:
    """Test get_registry singleton function."""

    def test_get_registry_returns_singleton(self):
        """get_registry returns same instance."""
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2

    def test_get_registry_is_shadow_registry(self):
        """get_registry returns ShadowRegistry instance."""
        registry = get_registry()
        assert isinstance(registry, ShadowRegistry)


# =============================================================================
# Thread Safety Tests
# =============================================================================


class TestRegistryThreadSafety:
    """Test ShadowRegistry thread safety."""

    def test_concurrent_register(self):
        """Concurrent registrations are thread-safe."""
        registry = ShadowRegistry(max_shadows=100)
        shadows = [spawn_shadow(f"shadow_{i}".encode()) for i in range(50)]
        barrier = Barrier(10)

        def register_shadows(shadow_subset):
            barrier.wait()
            for shadow in shadow_subset:
                registry.register(shadow)

        threads = []
        for i in range(10):
            subset = shadows[i * 5 : (i + 1) * 5]
            t = Thread(target=register_shadows, args=(subset,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should be registered
        assert registry.count == 50

    def test_concurrent_mark_busy_idle(self):
        """Concurrent state changes are thread-safe."""
        registry = ShadowRegistry()
        shadow = spawn_shadow(b"concurrent_test")
        registry.register(shadow)

        results = {"busy_ok": 0, "idle_ok": 0}

        def toggle_state(iterations):
            for _ in range(iterations):
                if registry.mark_busy(shadow.shadow_id, "d"):
                    results["busy_ok"] += 1
                    registry.mark_idle(shadow.shadow_id)
                    results["idle_ok"] += 1

        threads = [Thread(target=toggle_state, args=(10,)) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Final state should be IDLE
        entry = registry.get(shadow.shadow_id)
        assert entry.status == ShadowStatus.IDLE


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.lila import registry

        expected = [
            "MAX_SHADOWS",
            "RETIRE_AFTER_SERVICES",
            "ShadowStatus",
            "RegistryEntry",
            "ShadowRegistry",
            "get_registry",
        ]
        for item in expected:
            assert item in registry.__all__, f"{item} should be in __all__"
