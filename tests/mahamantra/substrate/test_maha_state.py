"""
TEST MAHASTATE - Sovereign State Adapter (BALARAMA PATTERN)
============================================================

Tests for MahaState as BALARAMA adapter that wraps ALL existing state systems:
- Sovereign operations (pierce/set/get)
- Wrapped systems (Prakriti, StateService, StateSyncHolon, etc.)
- State persistence
- Garuda integration
- Observer callbacks
- Threshold constants

NO validation tests (Kumaras handles that).
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Tuple
from unittest.mock import MagicMock, patch

from vibe_core.mahamantra.substrate.maha_state import (
    StateEntry,
    MahaState,
    get_maha_state,
    pierce,
    STATE_DIR,
    STATE_FILE,
    # Threshold constants
    MAX_STATE_ENTRIES,
    KERNEL_RESERVE,
    MALA_THRESHOLD,
    KISHORA_MAX_STALE,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def clean_state():
    """Reset MahaState singleton for clean test."""
    MahaState.reset_instance()
    yield
    MahaState.reset_instance()


@pytest.fixture
def temp_state_dir(tmp_path):
    """Use temp directory for state persistence."""
    state_dir = tmp_path / "mahamantra"
    state_dir.mkdir(parents=True)

    MahaState.reset_instance()
    state = MahaState.get_instance()
    state._state_dir = state_dir
    yield state_dir
    MahaState.reset_instance()


# =============================================================================
# TEST: StateEntry
# =============================================================================


class TestStateEntry:
    """Tests for StateEntry dataclass."""

    def test_creation(self):
        entry = StateEntry(
            key="test.key",
            value="test_value",
            source="sovereign",
            timestamp="2026-01-01T00:00:00",
        )
        assert entry.key == "test.key"
        assert entry.value == "test_value"
        assert entry.source == "sovereign"
        assert entry.pierced is False
        assert entry.hash != ""

    def test_creation_with_pierce(self):
        entry = StateEntry(
            key="test.key",
            value=42,
            source="sovereign",
            timestamp="2026-01-01T00:00:00",
            pierced=True,
        )
        assert entry.pierced is True

    def test_immutable(self):
        entry = StateEntry(
            key="test",
            value="val",
            source="sovereign",
            timestamp="2026-01-01T00:00:00",
        )
        with pytest.raises(AttributeError):
            entry.key = "other"  # type: ignore

    def test_to_dict(self):
        entry = StateEntry(
            key="test",
            value=123,
            source="config",
            timestamp="2026-01-01T00:00:00",
            pierced=True,
        )
        d = entry.to_dict()
        assert d["key"] == "test"
        assert d["value"] == 123
        assert d["source"] == "config"
        assert d["pierced"] is True
        assert "hash" in d

    def test_from_dict(self):
        data = {
            "key": "restored",
            "value": 456,
            "source": "sovereign",
            "timestamp": "2026-01-01T00:00:00",
            "pierced": False,
            "hash": "abc123",
        }
        entry = StateEntry.from_dict(data)
        assert entry.key == "restored"
        assert entry.value == 456
        assert entry.hash == "abc123"

    def test_verify_integrity_valid(self):
        entry = StateEntry(
            key="test",
            value="val",
            source="sovereign",
            timestamp="2026-01-01T00:00:00",
        )
        assert entry.verify_integrity() is True

    def test_verify_integrity_tampered(self):
        entry = StateEntry(
            key="test",
            value="val",
            source="sovereign",
            timestamp="2026-01-01T00:00:00",
        )
        # Tamper with hash
        object.__setattr__(entry, "hash", "tampered")
        assert entry.verify_integrity() is False


# =============================================================================
# TEST: MahaState Singleton
# =============================================================================


class TestMahaStateSingleton:
    """Tests for MahaState singleton behavior."""

    def test_get_instance_returns_same(self, clean_state):
        s1 = MahaState.get_instance()
        s2 = MahaState.get_instance()
        assert s1 is s2

    def test_reset_clears_instance(self, clean_state):
        s1 = MahaState.get_instance()
        MahaState.reset_instance()
        s2 = MahaState.get_instance()
        assert s1 is not s2

    def test_convenience_function(self, clean_state):
        state = get_maha_state()
        assert state is MahaState.get_instance()


# =============================================================================
# TEST: Set/Get Operations
# =============================================================================


class TestSetGetOperations:
    """Tests for set/get/has/keys operations."""

    def test_set_and_get(self, clean_state):
        state = get_maha_state()
        state.set("my.key", "my_value")
        assert state.get("my.key") == "my_value"

    def test_get_default(self, clean_state):
        state = get_maha_state()
        assert state.get("nonexistent", "default") == "default"

    def test_has(self, clean_state):
        state = get_maha_state()
        state.set("exists", 123)
        assert state.has("exists") is True
        assert state.has("missing") is False

    def test_keys(self, clean_state):
        state = get_maha_state()
        state.set("a", 1)
        state.set("b", 2)
        keys = state.keys()
        assert "a" in keys
        assert "b" in keys
        assert isinstance(keys, frozenset)

    def test_get_entry(self, clean_state):
        state = get_maha_state()
        state.set("test", "value", source="boot")
        entry = state.get_entry("test")
        assert entry is not None
        assert entry.source == "boot"

    def test_delete(self, clean_state):
        state = get_maha_state()
        state.set("to_delete", 999)
        assert state.has("to_delete")
        result = state.delete("to_delete")
        assert result is True
        assert not state.has("to_delete")

    def test_delete_nonexistent(self, clean_state):
        state = get_maha_state()
        result = state.delete("never_existed")
        assert result is False

    def test_value_types(self, clean_state):
        state = get_maha_state()
        state.set("str", "string")
        state.set("int", 42)
        state.set("float", 3.14)
        state.set("bool", True)
        state.set("none", None)

        assert state.get("str") == "string"
        assert state.get("int") == 42
        assert state.get("float") == 3.14
        assert state.get("bool") is True
        assert state.get("none") is None


# =============================================================================
# TEST: Pierce Operations
# =============================================================================


class TestPierceOperations:
    """Tests for pierce/unpierce - sovereign config override."""

    def test_pierce_sets_pierced_flag(self, clean_state):
        state = get_maha_state()
        state.pierce("override.key", "sovereign_value")
        entry = state.get_entry("override.key")
        assert entry is not None
        assert entry.pierced is True
        assert entry.value == "sovereign_value"

    def test_pierce_convenience_function(self, clean_state):
        pierce("func.key", 999)
        state = get_maha_state()
        assert state.get("func.key") == 999

    def test_pierced_keys(self, clean_state):
        state = get_maha_state()
        state.set("normal", 1)
        state.pierce("pierced1", 2)
        state.pierce("pierced2", 3)

        pierced = state.pierced_keys()
        assert "pierced1" in pierced
        assert "pierced2" in pierced
        assert "normal" not in pierced

    def test_unpierce(self, clean_state):
        state = get_maha_state()
        state.pierce("to_unpierce", 123)
        assert state.has("to_unpierce")

        result = state.unpierce("to_unpierce")
        assert result is True
        assert not state.has("to_unpierce")

    def test_unpierce_non_pierced(self, clean_state):
        state = get_maha_state()
        state.set("not_pierced", 1)
        result = state.unpierce("not_pierced")
        assert result is False

    def test_pierce_dedup(self, clean_state):
        """Rapid duplicate pierce calls should be skipped."""
        state = get_maha_state()
        observer_calls: List[str] = []

        def observer(key: str, entry: StateEntry) -> None:
            observer_calls.append(key)

        state.observe(observer)

        # First pierce - should notify
        state.pierce("dedup.key", "value")
        # Immediate duplicate - should be skipped
        state.pierce("dedup.key", "value")

        # Only one notification
        assert observer_calls.count("dedup.key") == 1


# =============================================================================
# TEST: Observers
# =============================================================================


class TestObservers:
    """Tests for state change observers."""

    def test_observe_callback(self, clean_state):
        state = get_maha_state()
        calls: List[Tuple[str, StateEntry]] = []

        def callback(key: str, entry: StateEntry) -> None:
            calls.append((key, entry))

        state.observe(callback)
        state.set("observed.key", "observed_value")

        assert len(calls) == 1
        assert calls[0][0] == "observed.key"
        assert calls[0][1].value == "observed_value"

    def test_unobserve(self, clean_state):
        state = get_maha_state()
        calls: List[str] = []

        def callback(key: str, entry: StateEntry) -> None:
            calls.append(key)

        state.observe(callback)
        state.set("first", 1)
        state.unobserve(callback)
        state.set("second", 2)

        assert "first" in calls
        assert "second" not in calls

    def test_observer_exception_handled(self, clean_state):
        state = get_maha_state()

        def bad_callback(key: str, entry: StateEntry) -> None:
            raise RuntimeError("Intentional error")

        state.observe(bad_callback)
        # Should not raise
        state.set("test", "value")


# =============================================================================
# TEST: Garuda Integration
# =============================================================================


class TestGarudaIntegration:
    """Tests for Garuda (Naga control) integration."""

    def test_garuda_flight_context(self, clean_state):
        state = get_maha_state()

        # Before flight
        assert state.is_garuda_flying is False

        # During flight (with mock Garuda)
        mock_garuda = MagicMock()
        mock_garuda.is_flying = False
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        mock_garuda.fly.return_value = mock_context
        state._garuda_ref = mock_garuda

        with state.garuda_flight():
            pass

        mock_garuda.fly.assert_called_once()

    def test_garuda_not_available(self, clean_state):
        """Should return no-op context when Garuda not available."""
        state = get_maha_state()
        state._garuda_ref = None

        # Should not raise
        with state.garuda_flight():
            pass


# =============================================================================
# TEST: Persistence
# =============================================================================


class TestPersistence:
    """Tests for state persistence to disk."""

    def test_save_creates_file(self, temp_state_dir):
        state = get_maha_state()
        state.set("persisted", "value")
        state.save()

        state_file = temp_state_dir / STATE_FILE
        assert state_file.exists()

    def test_save_json_valid(self, temp_state_dir):
        state = get_maha_state()
        state.pierce("json.test", 42)
        state.save()

        state_file = temp_state_dir / STATE_FILE
        data = json.loads(state_file.read_text())

        assert "version" in data
        assert "entries" in data
        assert "json.test" in data["entries"]
        assert "thresholds" in data

    def test_load_restores_state(self, temp_state_dir):
        # Create and save state
        state1 = get_maha_state()
        state1._state_dir = temp_state_dir
        state1.pierce("load.test", "restored_value")
        state1.save()

        # Reset and load with same dir
        MahaState.reset_instance()
        state2 = MahaState.get_instance()
        state2._state_dir = temp_state_dir
        state2._load_state()

        assert state2.get("load.test") == "restored_value"

    def test_roundtrip(self, temp_state_dir):
        state1 = get_maha_state()
        state1._state_dir = temp_state_dir
        state1.set("str", "hello")
        state1.set("int", 123)
        state1.pierce("bool", True)
        state1.save()

        MahaState.reset_instance()
        state2 = MahaState.get_instance()
        state2._state_dir = temp_state_dir
        state2._load_state()

        assert state2.get("str") == "hello"
        assert state2.get("int") == 123
        assert state2.get("bool") is True
        assert "bool" in state2.pierced_keys()


# =============================================================================
# TEST: Threshold Constants
# =============================================================================


class TestThresholdConstants:
    """Tests for threshold constants from seed.py."""

    def test_max_state_entries(self):
        assert MAX_STATE_ENTRIES == 72  # NADI_RESONANCE

    def test_kernel_reserve(self):
        assert KERNEL_RESERVE == 16  # HIDDEN_RESERVE

    def test_mala_threshold(self):
        assert MALA_THRESHOLD == 108  # MALA

    def test_kishora_max_stale(self):
        assert KISHORA_MAX_STALE == 79  # KISHORA_NUMERATOR


# =============================================================================
# TEST: Status
# =============================================================================


class TestStatus:
    """Tests for get_status()."""

    def test_status_fields(self, clean_state):
        state = get_maha_state()
        state.pierce("a", 1)
        state.set("b", 2)

        status = state.get_status()

        assert "boot_count" in status
        assert "uptime_seconds" in status
        assert "entries_count" in status
        assert status["entries_count"] >= 2
        assert "pierced_count" in status
        assert status["pierced_count"] >= 1
        assert "garuda_flying" in status
        assert "systems" in status
        assert "thresholds" in status

    def test_wrapped_systems_status(self, clean_state):
        state = get_maha_state()
        systems = state.get_wrapped_systems()

        # Initially all should be accessible (will lazy load on access)
        assert "prakriti" in systems
        assert "state_service" in systems
        assert "sync_holon" in systems
        assert "weaver" in systems
        assert "cognitive_weaver" in systems
        assert "guna_classifier" in systems


# =============================================================================
# TEST: BALARAMA Wrapped Systems
# =============================================================================


class TestBalaaramaWrappedSystems:
    """Tests for BALARAMA adapter pattern - wrapped systems."""

    def test_prakriti_property_accessible(self, clean_state):
        state = get_maha_state()
        # Just check it doesn't crash on access
        # May return None if vibe_core.state not available
        _ = state.prakriti

    def test_state_service_property_accessible(self, clean_state):
        state = get_maha_state()
        _ = state.state_service

    def test_prakriti_layer_accessors(self, clean_state):
        state = get_maha_state()
        # These may return None if prakriti not loaded
        _ = state.git
        _ = state.files
        _ = state.ledger
        _ = state.kernel
        _ = state.ephemeral
        _ = state.personas


# =============================================================================
# TEST: Exports
# =============================================================================


class TestExports:
    """Tests for module exports."""

    def test_all_exports_importable(self):
        from vibe_core.mahamantra.substrate.maha_state import __all__

        for name in __all__:
            assert hasattr(
                __import__("vibe_core.mahamantra.substrate.maha_state", fromlist=[name]),
                name
            )

    def test_substrate_exports(self):
        from vibe_core.mahamantra.substrate import (
            MahaState,
            StateEntry,
            get_maha_state,
            pierce,
        )
        assert MahaState is not None
        assert StateEntry is not None

    def test_mahamantra_exports(self):
        from vibe_core.mahamantra import (
            MahaState,
            StateEntry,
            get_maha_state,
            pierce,
        )
        assert MahaState is not None
