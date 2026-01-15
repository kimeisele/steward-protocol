"""
TEST PHOENIX RECOVERY
=====================

Simulates kill -9 and verifies state restoration.

THE GUARANTEE:
--------------
1. System ticks N times
2. Process dies (kill -9)
3. System restarts
4. State restored to position N

NO SPAGHETTI. Just the Phoenix guarantee.
"""

import json
from pathlib import Path

import pytest

from vibe_core.mahamantra.kernel.phoenix import (
    STATE_FILE,
    clear_state,
    init_phoenix,
    load_state,
    save_state,
)
from vibe_core.mahamantra.protocols._seed import LILA, PARAMPARA, WORDS


class TestPhoenixRecovery:
    """Phoenix state persistence tests."""

    def setup_method(self):
        """Clear state before each test."""
        clear_state()

    def teardown_method(self):
        """Clean up state after each test."""
        clear_state()

    def test_fresh_start_no_state(self):
        """Fresh start returns (0, 0) when no state exists."""
        tick, lila_tick = init_phoenix()
        assert tick == 0
        assert lila_tick == 0

    def test_save_and_load_state(self):
        """State saves to disk and loads correctly."""
        # Save state
        save_state(tick=5, lila_tick=23)

        # Verify file exists
        assert STATE_FILE.exists()

        # Load state
        state = load_state()
        assert state is not None
        assert state["tick"] == 5
        assert state["lila_tick"] == 23
        assert state["parampara"] == PARAMPARA

    def test_phoenix_restoration(self):
        """Simulates kill -9 and restart."""
        # PHASE 1: Initial run
        save_state(tick=7, lila_tick=31)

        # PHASE 2: Process dies (kill -9)
        # ... system restarts ...

        # PHASE 3: Restoration
        tick, lila_tick = init_phoenix()

        assert tick == 7, "Tick position not restored!"
        assert lila_tick == 31, "Lila tick position not restored!"

    def test_corrupted_state_returns_zero(self):
        """Corrupted state file returns fresh start."""
        # Write corrupted state
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text('{"invalid": "json"')

        # Should return fresh start
        tick, lila_tick = init_phoenix()
        assert tick == 0
        assert lila_tick == 0

    def test_invalid_parampara_rejected(self):
        """State with wrong parampara constant is rejected."""
        # Write state with wrong parampara
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps({"tick": 5, "lila_tick": 23, "parampara": 999})
        )

        # Should reject and return fresh start
        state = load_state()
        assert state is None

        tick, lila_tick = init_phoenix()
        assert tick == 0
        assert lila_tick == 0

    def test_out_of_bounds_positions_rejected(self):
        """State with invalid positions is rejected."""
        # Tick out of bounds
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps({"tick": 999, "lila_tick": 23, "parampara": PARAMPARA})
        )

        state = load_state()
        assert state is None

        # Lila tick out of bounds
        STATE_FILE.write_text(
            json.dumps({"tick": 5, "lila_tick": 999, "parampara": PARAMPARA})
        )

        state = load_state()
        assert state is None

    def test_atomic_write(self):
        """State writes are atomic (temp file + rename)."""
        # First save
        save_state(tick=3, lila_tick=15)

        # Second save (should not corrupt if interrupted)
        save_state(tick=4, lila_tick=16)

        # Verify final state
        state = load_state()
        assert state["tick"] == 4
        assert state["lila_tick"] == 16

        # Temp file should not exist
        temp_file = STATE_FILE.with_suffix(".tmp")
        assert not temp_file.exists()

    def test_boundary_positions(self):
        """Test boundary positions (0, WORDS-1, LILA-1)."""
        # Position 0
        save_state(tick=0, lila_tick=0)
        state = load_state()
        assert state["tick"] == 0
        assert state["lila_tick"] == 0

        # Max positions
        save_state(tick=WORDS - 1, lila_tick=LILA - 1)
        state = load_state()
        assert state["tick"] == WORDS - 1
        assert state["lila_tick"] == LILA - 1

    def test_multiple_cycles(self):
        """Simulates multiple crash/restart cycles."""
        # Cycle 1
        save_state(tick=5, lila_tick=20)
        tick, lila = init_phoenix()
        assert tick == 5 and lila == 20

        # Cycle 2
        save_state(tick=10, lila_tick=35)
        tick, lila = init_phoenix()
        assert tick == 10 and lila == 35

        # Cycle 3
        save_state(tick=0, lila_tick=0)
        tick, lila = init_phoenix()
        assert tick == 0 and lila == 0


class TestMahamantraIntegration:
    """Test Phoenix integration with MahamantraLotus."""

    def setup_method(self):
        """Clear state before each test."""
        clear_state()

    def teardown_method(self):
        """Clean up state after each test."""
        clear_state()

    def test_tick_persists_state(self):
        """Verify tick() persists state to disk."""
        from vibe_core.mahamantra import mahamantra

        # Reset to 0 manually (simulate fresh start)
        from vibe_core.mahamantra import MahamantraLotus
        MahamantraLotus._tick = 0
        MahamantraLotus._lila_tick = 0

        # Tick 3 times
        mahamantra.tick()
        mahamantra.tick()
        mahamantra.tick()

        # State should be saved
        state = load_state()
        assert state is not None
        assert state["tick"] == 3  # Advanced to position 3

    def test_lila_tick_persists_state(self):
        """Verify lila_tick() persists state to disk."""
        from vibe_core.mahamantra import mahamantra

        # Reset to 0 manually
        from vibe_core.mahamantra import MahamantraLotus
        MahamantraLotus._tick = 0
        MahamantraLotus._lila_tick = 0

        # Lila tick 5 times
        mahamantra.lila_tick()
        mahamantra.lila_tick()
        mahamantra.lila_tick()
        mahamantra.lila_tick()
        mahamantra.lila_tick()

        # State should be saved
        state = load_state()
        assert state is not None
        assert state["lila_tick"] == 5  # Advanced to lila position 5

    def test_full_cycle_with_restart(self):
        """
        Full integration test:
        1. Tick N times
        2. Simulate restart (reload module)
        3. Verify state restored
        """
        from vibe_core.mahamantra import MahamantraLotus

        # PHASE 1: Initial run
        MahamantraLotus._tick = 0
        MahamantraLotus._lila_tick = 0

        # Perform some ticks
        from vibe_core.mahamantra import mahamantra
        for _ in range(7):
            mahamantra.tick()

        for _ in range(13):
            mahamantra.lila_tick()

        # PHASE 2: Simulate restart
        # Manually call init_phoenix to simulate module reload
        tick, lila = init_phoenix()

        # PHASE 3: Verify restoration
        assert tick == 7, f"Expected tick=7, got {tick}"
        assert lila == 13, f"Expected lila=13, got {lila}"
