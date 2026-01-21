"""
Tests for LOTUS - The Universal Kernel.

"The Lotus IS the wiring. The Mantra IS the routing."

WATERTIGHT: All types explicit, no Any.
"""

import pytest
from pathlib import Path
from typing import List

from vibe_core.protocols.substrate.mantra.lotus import (
    # Constants
    LOTUS_POSITIONS,
    LOTUS_QUARTERS,
    WORDS_PER_QUARTER,
    LOTUS_PARAMPARA,
    LOTUS_MALA,
    # Enums
    LotusMode,
    LotusQuarter,
    # Types
    LotusPetal,
    LotusNode,
    LotusState,
    LotusRoute,
    # Classes
    LotusHeartbeat,
    LotusBase,
    LotusRegistry,
    # Functions
    get_lotus,
    grow_lotus,
)


class TestHolyNameMathConstants:
    """Test the Holy Name Math constants."""

    def test_16_positions(self) -> None:
        """Mahamantra has exactly 16 words."""
        assert LOTUS_POSITIONS == 16

    def test_4_quarters(self) -> None:
        """Lotus has exactly 4 petals (quarters)."""
        assert LOTUS_QUARTERS == 4

    def test_4_words_per_quarter(self) -> None:
        """Each quarter has exactly 4 words."""
        assert WORDS_PER_QUARTER == 4

    def test_37_parampara(self) -> None:
        """Parampara = 24 + 12 + 1 = 37."""
        assert LOTUS_PARAMPARA == 37

    def test_108_mala(self) -> None:
        """Mala has 108 beads."""
        assert LOTUS_MALA == 108

    def test_16_times_4_equals_positions(self) -> None:
        """4 quarters × 4 words = 16 positions."""
        assert LOTUS_QUARTERS * WORDS_PER_QUARTER == LOTUS_POSITIONS


class TestLotusQuarter:
    """Test LotusQuarter enum."""

    def test_four_quarters(self) -> None:
        """There should be exactly 4 quarters."""
        assert len(LotusQuarter) == 4

    def test_quarter_values(self) -> None:
        """Quarter values should be correct."""
        assert LotusQuarter.GENESIS.value == "genesis"
        assert LotusQuarter.DHARMA.value == "dharma"
        assert LotusQuarter.KARMA.value == "karma"
        assert LotusQuarter.MOKSHA.value == "moksha"


class TestLotusMode:
    """Test LotusMode enum."""

    def test_four_modes(self) -> None:
        """There should be exactly 4 modes."""
        assert len(LotusMode) == 4

    def test_mode_values(self) -> None:
        """Mode values should be correct."""
        assert LotusMode.SEED.value == "seed"
        assert LotusMode.STENGEL.value == "stengel"
        assert LotusMode.BLÜTE.value == "blüte"
        assert LotusMode.GARUDA.value == "garuda"


class TestLotusHeartbeat:
    """Test the Lotus heartbeat (continuous chanting)."""

    def test_initial_position(self) -> None:
        """Heartbeat starts at position 0."""
        heartbeat = LotusHeartbeat()
        assert heartbeat.position == 0

    def test_pulse_advances_position(self) -> None:
        """Pulse advances position by 1."""
        heartbeat = LotusHeartbeat()
        new_pos = heartbeat.pulse()
        assert new_pos == 1
        assert heartbeat.position == 1

    def test_position_wraps_at_16(self) -> None:
        """Position wraps from 15 to 0."""
        heartbeat = LotusHeartbeat()
        heartbeat.position = 15  # Set position directly
        new_pos = heartbeat.pulse()
        assert new_pos == 0
        assert heartbeat.mantra_count == 1

    def test_mala_count_at_108(self) -> None:
        """Mala count increases after 108 mantras."""
        heartbeat = LotusHeartbeat()
        # 108 mantras × 16 positions = 1728 pulses
        for _ in range(108 * 16):
            heartbeat.pulse()
        assert heartbeat.mala_count == 1

    def test_current_quarter(self) -> None:
        """Current quarter calculated from position."""
        heartbeat = LotusHeartbeat()
        heartbeat.position = 0
        assert heartbeat.current_quarter == LotusQuarter.GENESIS

        heartbeat.position = 5
        assert heartbeat.current_quarter == LotusQuarter.DHARMA

        heartbeat.position = 10
        assert heartbeat.current_quarter == LotusQuarter.KARMA

        heartbeat.position = 14
        assert heartbeat.current_quarter == LotusQuarter.MOKSHA

    def test_head_positions(self) -> None:
        """HEAD positions are 0, 4, 8, 12."""
        heartbeat = LotusHeartbeat()
        heartbeat.position = 0
        assert heartbeat.is_at_head_position is True

        heartbeat.position = 4
        assert heartbeat.is_at_head_position is True

        heartbeat.position = 1
        assert heartbeat.is_at_head_position is False

    def test_parampara_connection(self) -> None:
        """Parampara hash should be connected (% 37 == 0)."""
        heartbeat = LotusHeartbeat()
        assert heartbeat.verify_connection() is True

    def test_mantra_connection(self) -> None:
        """LotusHeartbeat wraps MantraHeartbeat - they are ONE."""
        heartbeat = LotusHeartbeat()
        # The Lotus IS the Mantra - verify connection
        assert heartbeat.is_chanting is False  # Not chanting yet
        heartbeat.pulse()  # Chant once
        assert heartbeat.is_chanting is True  # Now chanting


class TestLotusBase:
    """Test the LotusBase abstract class."""

    def test_create_lotus_subclass(self) -> None:
        """Can create a subclass of LotusBase."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 5
            LOTUS_NAME = "test_protocol"

        lotus = TestLotus()
        assert lotus.lotus_position == 5
        assert lotus.lotus_name == "test_protocol"

    def test_auto_quarter_calculation(self) -> None:
        """Quarter is auto-calculated from position."""

        class GenesisLotus(LotusBase):
            LOTUS_POSITION = 2
            LOTUS_NAME = "genesis_test"

        class MokshaLotus(LotusBase):
            LOTUS_POSITION = 14
            LOTUS_NAME = "moksha_test"

        genesis = GenesisLotus()
        assert genesis.lotus_quarter == LotusQuarter.GENESIS

        moksha = MokshaLotus()
        assert moksha.lotus_quarter == LotusQuarter.MOKSHA

    def test_parampara_connection_automatic(self) -> None:
        """Parampara connection is automatic (always connected)."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 7
            LOTUS_NAME = "connected_test"

        lotus = TestLotus()
        # Should be connected (we design the hash to be % 37 == 0)
        assert lotus.is_connected is True

    def test_chant_advances_heartbeat(self) -> None:
        """Chanting advances the heartbeat."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 0
            LOTUS_NAME = "chanting_test"

        lotus = TestLotus()
        assert lotus.is_chanting is False

        new_pos = lotus.chant()
        assert lotus.is_chanting is True
        assert new_pos == 1

    def test_mode_transformation(self) -> None:
        """Can transform between modes."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 0
            LOTUS_NAME = "transform_test"

        lotus = TestLotus()
        assert lotus.mode == LotusMode.SEED

        lotus.become_garuda()
        assert lotus.mode == LotusMode.GARUDA

        lotus.become_seed()
        assert lotus.mode == LotusMode.SEED

    def test_routing_same_quarter(self) -> None:
        """Routing within same quarter is direct."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 1
            LOTUS_NAME = "routing_test"

        lotus = TestLotus()
        route = lotus.route_to(3)  # Same quarter (GENESIS)

        assert route["route_type"] == "intra-quarter"
        assert route["via_stengel"] is False

    def test_routing_different_quarter(self) -> None:
        """Routing to different quarter goes via stengel."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 1
            LOTUS_NAME = "routing_test"

        lotus = TestLotus()
        route = lotus.route_to(10)  # Different quarter (KARMA)

        assert route["route_type"] == "inter-quarter"
        assert route["via_stengel"] is True

    def test_get_state_watertight(self) -> None:
        """get_state returns WATERTIGHT LotusNode."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 8
            LOTUS_NAME = "state_test"

        lotus = TestLotus()
        state: LotusNode = lotus.get_state()

        assert state["name"] == "state_test"
        assert state["position"] == 8
        assert state["quarter"] == "karma"
        assert "is_connected" in state
        assert "is_chanting" in state


class TestLotusRegistry:
    """Test the Lotus registry (auto-discovery)."""

    def test_registry_initializes_petals(self) -> None:
        """Registry initializes all 4 petals."""
        registry = LotusRegistry()
        petals = registry.get_petals()

        assert len(petals) == 4
        assert LotusQuarter.GENESIS in petals
        assert LotusQuarter.DHARMA in petals
        assert LotusQuarter.KARMA in petals
        assert LotusQuarter.MOKSHA in petals

    def test_petal_structure(self) -> None:
        """Each petal has correct structure."""
        registry = LotusRegistry()
        petals = registry.get_petals()

        genesis = petals[LotusQuarter.GENESIS]
        assert genesis["positions"] == [0, 1, 2, 3]
        assert genesis["head_avatara"] == "prithu"
        assert "brahma" in genesis["worker_mahajanas"]

    def test_registry_chants(self) -> None:
        """Registry can chant."""
        registry = LotusRegistry()
        pos = registry.chant()
        assert pos == 1

    def test_registry_state_watertight(self) -> None:
        """get_state returns WATERTIGHT LotusState."""
        registry = LotusRegistry()
        state: LotusState = registry.get_state()

        assert state["mode"] == "stengel"
        assert "total_nodes" in state
        assert "petals" in state
        assert "health" in state


class TestWatertightTypes:
    """Test that all types are WATERTIGHT (no Any)."""

    def test_lotus_petal_watertight(self) -> None:
        """LotusPetal should be WATERTIGHT."""
        petal: LotusPetal = {
            "quarter": "genesis",
            "positions": [0, 1, 2, 3],
            "head_avatara": "prithu",
            "worker_mahajanas": ["brahma", "narada", "shambhu"],
        }
        assert petal["quarter"] == "genesis"

    def test_lotus_node_watertight(self) -> None:
        """LotusNode should be WATERTIGHT."""
        node: LotusNode = {
            "path": "/protocols/mahajanas/brahma",
            "name": "brahma",
            "position": 1,
            "quarter": "genesis",
            "owner_type": "mahajana",
            "owner_name": "brahma",
            "parampara_hash": 37,
            "is_connected": True,
            "is_chanting": True,
            "discovered_at": "2025-01-11T12:00:00",
        }
        assert node["is_connected"] is True

    def test_lotus_route_watertight(self) -> None:
        """LotusRoute should be WATERTIGHT."""
        route: LotusRoute = {
            "source_position": 1,
            "target_position": 10,
            "source_quarter": "genesis",
            "target_quarter": "karma",
            "route_type": "inter-quarter",
            "via_stengel": True,
            "parampara_verified": True,
        }
        assert route["via_stengel"] is True

    def test_lotus_state_watertight(self) -> None:
        """LotusState should be WATERTIGHT."""
        state: LotusState = {
            "mode": "seed",
            "total_nodes": 16,
            "connected_nodes": 16,
            "disconnected_nodes": 0,
            "chanting_nodes": 12,
            "petals": [],
            "health": "pristine",
            "last_pulse": "2025-01-11T12:00:00",
            "mala_count": 3,
        }
        assert state["health"] == "pristine"


class TestGlobalLotus:
    """Test global Lotus singleton."""

    def test_get_lotus_singleton(self) -> None:
        """get_lotus returns same instance."""
        lotus1 = get_lotus()
        lotus2 = get_lotus()
        assert lotus1 is lotus2

    def test_grow_lotus_returns_state(self) -> None:
        """grow_lotus returns LotusState."""
        # Use a temp path that exists
        state = grow_lotus(Path("/tmp"))
        assert "total_nodes" in state
        assert "petals" in state
