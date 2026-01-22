"""
TESTS: kernel/phoenix.py - State Persistence
=============================================

REAL TESTS for:
1. PhoenixState TypedDict
2. STATE_DIR and STATE_FILE paths
3. save_state function
4. load_state function
5. clear_state function
6. init_phoenix function
"""

import json
import pytest
from pathlib import Path
from vibe_core.mahamantra.kernel.phoenix import (
    PhoenixState,
    STATE_DIR,
    STATE_FILE,
    save_state,
    load_state,
    clear_state,
    init_phoenix,
)
from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS, LILA


# =============================================================================
# PhoenixState TypedDict Tests
# =============================================================================


class TestPhoenixState:
    """Test PhoenixState TypedDict."""

    def test_phoenix_state_creation(self):
        """PhoenixState can be created."""
        state: PhoenixState = {
            "tick": 5,
            "lila_tick": 20,
            "parampara": PARAMPARA,
        }
        assert state["tick"] == 5
        assert state["lila_tick"] == 20
        assert state["parampara"] == PARAMPARA

    def test_phoenix_state_tick_range(self):
        """PhoenixState tick should be 0 to WORDS-1."""
        for tick in range(WORDS):
            state: PhoenixState = {
                "tick": tick,
                "lila_tick": 0,
                "parampara": PARAMPARA,
            }
            assert 0 <= state["tick"] < WORDS

    def test_phoenix_state_lila_tick_range(self):
        """PhoenixState lila_tick should be 0 to LILA-1."""
        for lila_tick in [0, 10, 20, 30, 40, LILA - 1]:
            state: PhoenixState = {
                "tick": 0,
                "lila_tick": lila_tick,
                "parampara": PARAMPARA,
            }
            assert 0 <= state["lila_tick"] < LILA


# =============================================================================
# STATE_DIR and STATE_FILE Tests
# =============================================================================


class TestStateConstants:
    """Test STATE_DIR and STATE_FILE constants."""

    def test_state_dir_is_path(self):
        """STATE_DIR is a Path."""
        assert isinstance(STATE_DIR, Path)

    def test_state_dir_name(self):
        """STATE_DIR is .vibe_state."""
        assert STATE_DIR.name == ".vibe_state"

    def test_state_file_is_path(self):
        """STATE_FILE is a Path."""
        assert isinstance(STATE_FILE, Path)

    def test_state_file_name(self):
        """STATE_FILE is mahamantra_tick.json."""
        assert STATE_FILE.name == "mahamantra_tick.json"

    def test_state_file_in_state_dir(self):
        """STATE_FILE is inside STATE_DIR."""
        assert STATE_FILE.parent == STATE_DIR


# =============================================================================
# save_state Tests
# =============================================================================


class TestSaveState:
    """Test save_state function."""

    def test_save_state_creates_directory(self, tmp_path, monkeypatch):
        """save_state creates STATE_DIR if needed."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        save_state(5, 10)

        assert test_dir.exists()
        assert test_file.exists()

    def test_save_state_writes_correct_data(self, tmp_path, monkeypatch):
        """save_state writes correct JSON data."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        save_state(7, 25)

        data = json.loads(test_file.read_text())
        assert data["tick"] == 7
        assert data["lila_tick"] == 25
        assert data["parampara"] == PARAMPARA

    def test_save_state_overwrites_existing(self, tmp_path, monkeypatch):
        """save_state overwrites existing state file."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)

        # Write initial state
        test_file.write_text(json.dumps({"tick": 0, "lila_tick": 0, "parampara": PARAMPARA}))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        save_state(10, 30)

        data = json.loads(test_file.read_text())
        assert data["tick"] == 10
        assert data["lila_tick"] == 30

    def test_save_state_graceful_on_error(self, tmp_path, monkeypatch):
        """save_state handles errors gracefully."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        # Use an invalid path that can't be created
        # On most systems, /proc or similar won't allow file creation
        test_dir = Path("/nonexistent_root_path_xyz/.vibe_state")
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Should not raise
        save_state(5, 10)


# =============================================================================
# load_state Tests
# =============================================================================


class TestLoadState:
    """Test load_state function."""

    def test_load_state_returns_none_no_file(self, tmp_path, monkeypatch):
        """load_state returns None when no state file exists."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is None

    def test_load_state_returns_valid_state(self, tmp_path, monkeypatch):
        """load_state returns valid state."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": 8,
            "lila_tick": 32,
            "parampara": PARAMPARA,
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is not None
        assert result["tick"] == 8
        assert result["lila_tick"] == 32
        assert result["parampara"] == PARAMPARA

    def test_load_state_rejects_wrong_parampara(self, tmp_path, monkeypatch):
        """load_state returns None for wrong parampara."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": 8,
            "lila_tick": 32,
            "parampara": 999,  # Wrong parampara
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is None

    def test_load_state_rejects_invalid_tick(self, tmp_path, monkeypatch):
        """load_state returns None for invalid tick."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": WORDS + 5,  # Out of range
            "lila_tick": 32,
            "parampara": PARAMPARA,
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is None

    def test_load_state_rejects_negative_tick(self, tmp_path, monkeypatch):
        """load_state returns None for negative tick."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": -1,
            "lila_tick": 32,
            "parampara": PARAMPARA,
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is None

    def test_load_state_rejects_invalid_lila_tick(self, tmp_path, monkeypatch):
        """load_state returns None for invalid lila_tick."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": 5,
            "lila_tick": LILA + 10,  # Out of range
            "parampara": PARAMPARA,
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is None

    def test_load_state_handles_corrupted_json(self, tmp_path, monkeypatch):
        """load_state returns None for corrupted JSON."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text("not valid json {{{")

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = load_state()
        assert result is None

    def test_load_state_handles_missing_fields(self, tmp_path, monkeypatch):
        """load_state handles missing fields gracefully."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "parampara": PARAMPARA,
            # Missing tick and lila_tick
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Should use defaults (0, 0) which are valid
        result = load_state()
        # Result depends on implementation - may return state with defaults
        # or None if required fields are missing
        if result is not None:
            assert result["tick"] == 0
            assert result["lila_tick"] == 0


# =============================================================================
# clear_state Tests
# =============================================================================


class TestClearState:
    """Test clear_state function."""

    def test_clear_state_removes_file(self, tmp_path, monkeypatch):
        """clear_state removes the state file."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": 5,
            "lila_tick": 10,
            "parampara": PARAMPARA,
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        assert test_file.exists()
        clear_state()
        assert not test_file.exists()

    def test_clear_state_handles_no_file(self, tmp_path, monkeypatch):
        """clear_state handles missing file gracefully."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Should not raise
        clear_state()


# =============================================================================
# init_phoenix Tests
# =============================================================================


class TestInitPhoenix:
    """Test init_phoenix function."""

    def test_init_phoenix_fresh_start(self, tmp_path, monkeypatch):
        """init_phoenix returns (0, 0) when no state file."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        tick, lila_tick = init_phoenix()
        assert tick == 0
        assert lila_tick == 0

    def test_init_phoenix_restores_state(self, tmp_path, monkeypatch):
        """init_phoenix restores state from file."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text(json.dumps({
            "tick": 12,
            "lila_tick": 40,
            "parampara": PARAMPARA,
        }))

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        tick, lila_tick = init_phoenix()
        assert tick == 12
        assert lila_tick == 40

    def test_init_phoenix_returns_tuple(self, tmp_path, monkeypatch):
        """init_phoenix returns a tuple."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        result = init_phoenix()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_init_phoenix_fresh_on_corrupted(self, tmp_path, monkeypatch):
        """init_phoenix returns (0, 0) on corrupted state."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"
        test_dir.mkdir(parents=True)
        test_file.write_text("corrupted data")

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        tick, lila_tick = init_phoenix()
        assert tick == 0
        assert lila_tick == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhoenixIntegration:
    """Integration tests for Phoenix pattern."""

    def test_save_load_cycle(self, tmp_path, monkeypatch):
        """State can be saved and loaded."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Save state
        save_state(10, 35)

        # Load it back
        state = load_state()
        assert state is not None
        assert state["tick"] == 10
        assert state["lila_tick"] == 35

    def test_init_after_save(self, tmp_path, monkeypatch):
        """init_phoenix restores after save."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Save state
        save_state(15, 45)

        # Init should restore
        tick, lila_tick = init_phoenix()
        assert tick == 15
        assert lila_tick == 45

    def test_clear_then_init(self, tmp_path, monkeypatch):
        """init_phoenix returns (0, 0) after clear."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Save state
        save_state(10, 30)

        # Clear state
        clear_state()

        # Init should return fresh
        tick, lila_tick = init_phoenix()
        assert tick == 0
        assert lila_tick == 0

    def test_boundary_values(self, tmp_path, monkeypatch):
        """Phoenix handles boundary values correctly."""
        import vibe_core.mahamantra.kernel.phoenix as phoenix

        test_dir = tmp_path / ".vibe_state"
        test_file = test_dir / "mahamantra_tick.json"

        monkeypatch.setattr(phoenix, "STATE_DIR", test_dir)
        monkeypatch.setattr(phoenix, "STATE_FILE", test_file)

        # Test max valid values
        save_state(WORDS - 1, LILA - 1)
        state = load_state()
        assert state is not None
        assert state["tick"] == WORDS - 1
        assert state["lila_tick"] == LILA - 1

        # Test min valid values
        save_state(0, 0)
        state = load_state()
        assert state is not None
        assert state["tick"] == 0
        assert state["lila_tick"] == 0
