"""
TESTS: _lotus.py - The Lotus Protocol
======================================

REAL TESTS for:
1. LotusMode enum
2. LotusPetal dataclass
3. LotusState dataclass
4. LotusRoute dataclass
5. LotusBase abstract class
6. LotusTree class
7. LotusHologram class
8. Mahajana mappings
"""

import pytest
from vibe_core.mahamantra.protocols._lotus import (
    # Constants
    LOTUS_PETALS,
    LOTUS_QUARTERS,
    PETALS_PER_QUARTER,
    MALA_BEADS,
    TRINITY,
    # Mahajana mappings
    MAHAJANA_POSITIONS,
    POSITION_MAHAJANAS,
    get_mahajana_position,
    get_position_mahajana,
    # Enums
    LotusMode,
    # Dataclasses
    LotusPetal,
    LotusState,
    LotusRoute,
    # Base class
    LotusBase,
    # Tree
    LotusTree,
    # Hologram
    LotusHologram,
    # Protocol
    LotusProtocolDef,
)
from vibe_core.mahamantra.protocols._core import Quarter


# =============================================================================
# Constants Tests
# =============================================================================


class TestLotusConstants:
    """Test Lotus constants."""

    def test_lotus_petals_is_16(self):
        """LOTUS_PETALS is 16."""
        assert LOTUS_PETALS == 16

    def test_lotus_quarters_is_4(self):
        """LOTUS_QUARTERS is 4."""
        assert LOTUS_QUARTERS == 4

    def test_petals_per_quarter_is_4(self):
        """PETALS_PER_QUARTER is 4."""
        assert PETALS_PER_QUARTER == 4

    def test_mala_beads_is_108(self):
        """MALA_BEADS is 108."""
        assert MALA_BEADS == 108

    def test_trinity_is_3(self):
        """TRINITY is 3."""
        assert TRINITY == 3

    def test_petals_math(self):
        """PETALS = QUARTERS * PETALS_PER_QUARTER."""
        assert LOTUS_PETALS == LOTUS_QUARTERS * PETALS_PER_QUARTER


# =============================================================================
# Mahajana Mappings Tests
# =============================================================================


class TestMahajanaMappings:
    """Test Mahajana position mappings."""

    def test_mahajana_positions_has_16_entries(self):
        """MAHAJANA_POSITIONS has 16 entries."""
        assert len(MAHAJANA_POSITIONS) == 16

    def test_position_mahajanas_has_16_entries(self):
        """POSITION_MAHAJANAS has 16 entries."""
        assert len(POSITION_MAHAJANAS) == 16

    def test_vyasa_at_position_0(self):
        """vyasa is at position 0."""
        assert MAHAJANA_POSITIONS["vyasa"] == 0

    def test_brahma_at_position_1(self):
        """brahma is at position 1."""
        assert MAHAJANA_POSITIONS["brahma"] == 1

    def test_yamaraja_at_position_15(self):
        """yamaraja is at position 15."""
        assert MAHAJANA_POSITIONS["yamaraja"] == 15

    def test_get_mahajana_position_valid(self):
        """get_mahajana_position returns position."""
        assert get_mahajana_position("vyasa") == 0
        assert get_mahajana_position("brahma") == 1
        assert get_mahajana_position("narada") == 2

    def test_get_mahajana_position_invalid(self):
        """get_mahajana_position returns -1 for invalid."""
        assert get_mahajana_position("unknown") == -1

    def test_get_position_mahajana_valid(self):
        """get_position_mahajana returns mahajana."""
        assert get_position_mahajana(0) == "vyasa"
        assert get_position_mahajana(1) == "brahma"
        assert get_position_mahajana(15) == "yamaraja"

    def test_get_position_mahajana_invalid(self):
        """get_position_mahajana returns 'unknown' for invalid."""
        assert get_position_mahajana(100) == "unknown"

    def test_mappings_are_inverses(self):
        """MAHAJANA_POSITIONS and POSITION_MAHAJANAS are inverses."""
        for name, pos in MAHAJANA_POSITIONS.items():
            assert POSITION_MAHAJANAS[pos] == name


# =============================================================================
# LotusMode Enum Tests
# =============================================================================


class TestLotusMode:
    """Test LotusMode enum."""

    def test_lotus_mode_seed(self):
        """LotusMode has SEED."""
        assert LotusMode.SEED.value == "seed"

    def test_lotus_mode_stem(self):
        """LotusMode has STEM."""
        assert LotusMode.STEM.value == "stem"

    def test_lotus_mode_bloom(self):
        """LotusMode has BLOOM."""
        assert LotusMode.BLOOM.value == "bloom"

    def test_lotus_mode_garuda(self):
        """LotusMode has GARUDA."""
        assert LotusMode.GARUDA.value == "garuda"


# =============================================================================
# LotusPetal Tests
# =============================================================================


class TestLotusPetal:
    """Test LotusPetal dataclass."""

    def test_lotus_petal_create(self):
        """LotusPetal.create works."""
        petal = LotusPetal.create(0, "vyasa")
        assert petal.position == 0
        assert petal.mahajana == "vyasa"

    def test_lotus_petal_quarter(self):
        """Quarter is derived from position."""
        petal_genesis = LotusPetal.create(0, "vyasa")
        petal_dharma = LotusPetal.create(4, "prithu")
        petal_karma = LotusPetal.create(8, "parashurama")
        petal_moksha = LotusPetal.create(12, "nrisimha")
        assert petal_genesis.quarter == Quarter.GENESIS
        assert petal_dharma.quarter == Quarter.DHARMA
        assert petal_karma.quarter == Quarter.KARMA
        assert petal_moksha.quarter == Quarter.MOKSHA

    def test_lotus_petal_is_head(self):
        """HEAD positions are every 4th (0, 4, 8, 12)."""
        for i in range(16):
            petal = LotusPetal.create(i, get_position_mahajana(i))
            if i % 4 == 0:
                assert petal.is_head is True
            else:
                assert petal.is_head is False

    def test_lotus_petal_parampara_vector(self):
        """parampara_vector is computed correctly."""
        from vibe_core.mahamantra.protocols._core import PARAMPARA

        petal = LotusPetal.create(0, "vyasa")
        assert petal.parampara_vector == (0 + 1) * PARAMPARA

    def test_lotus_petal_is_connected(self):
        """is_connected is always True for valid petals."""
        petal = LotusPetal.create(0, "vyasa")
        assert petal.is_connected is True

    def test_lotus_petal_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            LotusPetal.create(16, "invalid")

    def test_lotus_petal_is_frozen(self):
        """LotusPetal is frozen."""
        petal = LotusPetal.create(0, "vyasa")
        with pytest.raises(Exception):
            petal.position = 1


# =============================================================================
# LotusState Tests
# =============================================================================


class TestLotusState:
    """Test LotusState dataclass."""

    def test_lotus_state_creation(self):
        """LotusState can be created."""
        state = LotusState()
        assert state.position == 0
        assert state.mantra_count == 0
        assert state.mala_count == 0

    def test_lotus_state_chant(self):
        """chant advances position."""
        state = LotusState()
        state.chant()
        assert state.position == 1

    def test_lotus_state_chant_wraps(self):
        """chant wraps at 16."""
        state = LotusState(position=15)
        state.chant()
        assert state.position == 0

    def test_lotus_state_mantra_count_increments(self):
        """mantra_count increments after 16 chants."""
        state = LotusState(position=15)
        assert state.mantra_count == 0
        state.chant()  # wraps to 0
        assert state.mantra_count == 1

    def test_lotus_state_mala_count_increments(self):
        """mala_count increments after 108 mantras."""
        state = LotusState(position=15, mantra_count=107)
        state.chant()
        assert state.mala_count == 1
        assert state.mantra_count == 0

    def test_lotus_state_quarter(self):
        """quarter property returns current quarter."""
        state = LotusState(position=0)
        assert state.quarter == Quarter.GENESIS
        state.position = 4
        assert state.quarter == Quarter.DHARMA

    def test_lotus_state_is_at_head(self):
        """is_at_head returns True at HEAD positions."""
        state = LotusState(position=0)
        assert state.is_at_head is True
        state.position = 1
        assert state.is_at_head is False
        state.position = 4
        assert state.is_at_head is True

    def test_lotus_state_current_mahajana(self):
        """current_mahajana returns mahajana name."""
        state = LotusState(position=0)
        assert state.current_mahajana == "vyasa"
        state.position = 1
        assert state.current_mahajana == "brahma"


# =============================================================================
# LotusRoute Tests
# =============================================================================


class TestLotusRoute:
    """Test LotusRoute dataclass."""

    def test_lotus_route_calculate_same_quarter(self):
        """Route within quarter is direct."""
        route = LotusRoute.calculate(0, 1)
        assert route.source == 0
        assert route.target == 1
        assert route.via_stem is False
        assert route.crosses_quarters is False
        assert route.path == (0, 1)

    def test_lotus_route_calculate_cross_quarter(self):
        """Route across quarters goes via stem."""
        route = LotusRoute.calculate(0, 4)
        assert route.via_stem is True
        assert route.crosses_quarters is True
        assert route.path == (0, 0, 4, 4)  # source -> source_head -> target_head -> target

    def test_lotus_route_is_frozen(self):
        """LotusRoute is frozen."""
        route = LotusRoute.calculate(0, 1)
        with pytest.raises(Exception):
            route.source = 2


# =============================================================================
# LotusBase Tests
# =============================================================================


class TestLotusBase:
    """Test LotusBase abstract class."""

    def test_lotus_base_subclass(self):
        """Can create LotusBase subclass."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 5
            LOTUS_NAME = "kumaras"

        lotus = TestLotus()
        assert lotus.lotus_position == 5
        assert lotus.lotus_mahajana == "kumaras"

    def test_lotus_base_quarter(self):
        """lotus_quarter derived from position."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 4
            LOTUS_NAME = "prithu"

        lotus = TestLotus()
        assert lotus.lotus_quarter == Quarter.DHARMA

    def test_lotus_base_chant(self):
        """chant advances state."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 0
            LOTUS_NAME = "vyasa"

        lotus = TestLotus()
        lotus.chant()
        assert lotus.state.position == 1

    def test_lotus_base_route_to(self):
        """route_to calculates route."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 0
            LOTUS_NAME = "vyasa"

        lotus = TestLotus()
        route = lotus.route_to(5)
        assert route.source == 0
        assert route.target == 5

    def test_lotus_base_is_connected(self):
        """is_connected is True."""

        class TestLotus(LotusBase):
            LOTUS_POSITION = 0
            LOTUS_NAME = "vyasa"

        lotus = TestLotus()
        assert lotus.is_connected is True


# =============================================================================
# LotusTree Tests
# =============================================================================


class TestLotusTree:
    """Test LotusTree class."""

    def test_lotus_tree_creation(self):
        """LotusTree can be created."""
        tree = LotusTree()
        assert tree is not None

    def test_lotus_tree_has_16_petals(self):
        """LotusTree has 16 petals."""
        tree = LotusTree()
        assert len(tree.petals) == 16

    def test_lotus_tree_get_petal(self):
        """get_petal returns petal."""
        tree = LotusTree()
        petal = tree.get_petal(0)
        assert petal is not None
        assert petal.position == 0

    def test_lotus_tree_get_petals_in_quarter(self):
        """get_petals_in_quarter returns 4 petals."""
        tree = LotusTree()
        genesis_petals = tree.get_petals_in_quarter(Quarter.GENESIS)
        assert len(genesis_petals) == 4
        for petal in genesis_petals:
            assert petal.quarter == Quarter.GENESIS


# =============================================================================
# LotusHologram Tests
# =============================================================================


class TestLotusHologram:
    """Test LotusHologram class."""

    def test_lotus_hologram_creation(self):
        """LotusHologram can be created."""
        hologram = LotusHologram()
        assert hologram is not None

    def test_lotus_hologram_get_petal(self):
        """get_petal returns petal by name."""
        hologram = LotusHologram()
        petal = hologram.get_petal("vyasa")
        assert petal is not None
        assert petal.mahajana == "vyasa"

    def test_lotus_hologram_reflect_all(self):
        """reflect_all returns all petals."""
        hologram = LotusHologram()
        all_petals = hologram.reflect_all()
        assert len(all_petals) == 16

    def test_lotus_hologram_route(self):
        """route calculates route between mahajanas."""
        hologram = LotusHologram()
        route = hologram.route("vyasa", "brahma")
        assert route is not None
        assert route.source == 0
        assert route.target == 1


# =============================================================================
# LotusProtocolDef Tests
# =============================================================================


class TestLotusProtocolDef:
    """Test LotusProtocolDef."""

    def test_lotus_protocol_validates(self):
        """LotusProtocolDef validates."""
        valid, violations = LotusProtocolDef.validate()
        assert valid is True

    def test_lotus_protocol_identity(self):
        """LotusProtocolDef has correct identity."""
        identity = LotusProtocolDef.get_identity()
        assert identity.name == "LotusProtocol"
        assert identity.mahajana == "prithu"


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _lotus

        expected = [
            "LotusMode",
            "LotusPetal",
            "LotusState",
            "LotusRoute",
            "LotusBase",
            "LotusTree",
            "LotusHologram",
        ]
        for item in expected:
            assert item in _lotus.__all__, f"{item} should be in __all__"
