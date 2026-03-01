"""
MAHA STATE — State Management Tests
=====================================

Tests MahaState singleton, StateEntry integrity,
pierce operations, observer pattern, constants.
"""

import pytest
import tempfile
from pathlib import Path


# ============================================================================
# Constants
# ============================================================================


class TestMahaStateConstants:
    """Constants derive from seed."""

    def test_max_state_entries(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MAX_STATE_ENTRIES

        assert MAX_STATE_ENTRIES == 72  # NADI_RESONANCE

    def test_kernel_reserve(self):
        from vibe_core.mahamantra.substrate.state.maha_state import KERNEL_RESERVE

        assert KERNEL_RESERVE == 16  # HIDDEN_RESERVE = WORDS

    def test_mala_threshold(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MALA_THRESHOLD

        assert MALA_THRESHOLD == 108  # MALA

    def test_max_backups(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MAX_BACKUPS

        assert MAX_BACKUPS == 5  # PANCHA


# ============================================================================
# StateEntry
# ============================================================================


class TestStateEntry:
    """StateEntry is a frozen dataclass with integrity verification."""

    def test_create_entry(self):
        from vibe_core.mahamantra.substrate.state.maha_state import StateEntry

        entry = StateEntry(key="test", value="hello", source="sovereign", timestamp="2026-01-01T00:00:00")
        assert entry.key == "test"
        assert entry.value == "hello"
        assert entry.source == "sovereign"
        assert entry.pierced is False

    def test_entry_to_dict_roundtrip(self):
        from vibe_core.mahamantra.substrate.state.maha_state import StateEntry

        entry = StateEntry(key="k", value=42, source="computed", timestamp="2026-01-01T00:00:00")
        d = entry.to_dict()
        assert isinstance(d, dict)
        assert d["key"] == "k"
        assert d["value"] == 42

        restored = StateEntry.from_dict(d)
        assert restored.key == entry.key
        assert restored.value == entry.value
        assert restored.source == entry.source

    def test_entry_integrity(self):
        from vibe_core.mahamantra.substrate.state.maha_state import StateEntry

        entry = StateEntry(key="x", value="y", source="boot", timestamp="2026-01-01T00:00:00")
        assert entry.verify_integrity() is True

    def test_entry_pierced(self):
        from vibe_core.mahamantra.substrate.state.maha_state import StateEntry

        entry = StateEntry(key="p", value="v", source="sovereign", timestamp="now", pierced=True)
        assert entry.pierced is True


# ============================================================================
# MahaState Singleton
# ============================================================================


class TestMahaState:
    """MahaState is a singleton with state operations."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        MahaState.reset_instance()
        yield
        MahaState.reset_instance()

    def test_singleton(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            a = MahaState.get_instance(Path(tmp))
            b = MahaState.get_instance(Path(tmp))
            assert a is b

    def test_set_get(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            state.set("answer", 42)
            assert state.get("answer") == 42

    def test_has(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            assert state.has("nonexistent") is False
            state.set("exists", True)
            assert state.has("exists") is True

    def test_delete(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            state.set("tmp", "val")
            assert state.delete("tmp") is True
            assert state.has("tmp") is False
            assert state.delete("tmp") is False

    def test_keys(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            state.set("a", 1)
            state.set("b", 2)
            keys = state.keys()
            assert isinstance(keys, frozenset)
            assert "a" in keys
            assert "b" in keys

    def test_pierce(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            state.set("normal", "value")
            state.pierce("normal", "overridden")
            assert state.get("normal") == "overridden"
            entry = state.get_entry("normal")
            assert entry is not None
            assert entry.pierced is True

    def test_unpierce(self):
        """unpierce() deletes the pierced entry entirely."""
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            state.pierce("key", "val")
            assert state.has("key") is True
            assert state.unpierce("key") is True
            assert state.has("key") is False  # deleted
            assert state.unpierce("key") is False  # already gone

    def test_pierced_keys(self):
        from vibe_core.mahamantra.substrate.state.maha_state import MahaState

        with tempfile.TemporaryDirectory() as tmp:
            state = MahaState.get_instance(Path(tmp))
            state.pierce("x", 1)
            state.pierce("y", 2)
            pierced = state.pierced_keys()
            assert "x" in pierced
            assert "y" in pierced
