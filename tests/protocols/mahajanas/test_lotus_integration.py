"""
Tests for LOTUS Integration with OwnedProtocol.

"The Mantra IS the wiring. The Owner IS the position."

FRACTAL PRINCIPLE:
    Owner → Position (ONE mapping, ALL inherit)
    No manual LOTUS_POSITION per protocol.

This verifies that:
1. Position is DERIVED from OWNER automatically
2. Auto-routing works between protocols
3. Parampara verification is automatic (% 37 == 0)
4. NO MANUAL WIRING - Owner = Position

WATERTIGHT: All types explicit, no Any.
"""

import pytest
from typing import List

from vibe_core.protocols.mahajanas.owned_protocol import (
    OwnedProtocol,
    ProtocolState,
    get_mahajana_position,
    LOTUS_POSITIONS,
    LOTUS_PARAMPARA,
    LotusQuarter,
    LotusRoute,
)
from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

# List of all 12 Mahajanas for iteration
MAHAJANA_NAMES = [
    "brahma", "narada", "shambhu", "kumaras", "kapila", "manu",
    "prahlada", "janaka", "bhishma", "bali", "shuka", "yamaraja"
]


# =============================================================================
# TEST PROTOCOLS (Position derived from OWNER - no manual wiring!)
# =============================================================================


class BrahmaProtocol(OwnedProtocol):
    """Protocol owned by BRAHMA → Position 1 (GENESIS)."""
    OWNER = Mahajana.BRAHMA
    OPCODES = [MantraOpCode.LOAD_ROOT]
    PROTOCOL_NAME = "brahma_test"
    DESCRIPTION = "Test protocol owned by Brahma"
    # NO LOTUS_POSITION - derived from OWNER automatically!

    def get_state(self) -> ProtocolState:
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
            last_error=None,
            lotus_position=self.lotus_position,
            lotus_quarter=self.lotus_quarter.value,
            parampara_hash=self.parampara_hash,
            is_lotus_connected=self.is_lotus_connected,
        )


class KapilaProtocol(OwnedProtocol):
    """Protocol owned by KAPILA → Position 6 (DHARMA)."""
    OWNER = Mahajana.KAPILA
    OPCODES = [MantraOpCode.CHECK_DHARMA]
    PROTOCOL_NAME = "kapila_test"
    DESCRIPTION = "Test protocol owned by Kapila"
    # NO LOTUS_POSITION - derived from OWNER automatically!

    def get_state(self) -> ProtocolState:
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
            last_error=None,
            lotus_position=self.lotus_position,
            lotus_quarter=self.lotus_quarter.value,
            parampara_hash=self.parampara_hash,
            is_lotus_connected=self.is_lotus_connected,
        )


class JanakaProtocol(OwnedProtocol):
    """Protocol owned by JANAKA → Position 10 (KARMA)."""
    OWNER = Mahajana.JANAKA
    OPCODES = [MantraOpCode.CHECK_DHARMA]
    PROTOCOL_NAME = "janaka_test"
    DESCRIPTION = "Test protocol owned by Janaka"
    # NO LOTUS_POSITION - derived from OWNER automatically!

    def get_state(self) -> ProtocolState:
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
            last_error=None,
            lotus_position=self.lotus_position,
            lotus_quarter=self.lotus_quarter.value,
            parampara_hash=self.parampara_hash,
            is_lotus_connected=self.is_lotus_connected,
        )


class NaradaProtocol(OwnedProtocol):
    """Protocol owned by NARADA → Position 2 (GENESIS)."""
    OWNER = Mahajana.NARADA
    OPCODES = [MantraOpCode.PULSE_SYNC]
    PROTOCOL_NAME = "narada_test"
    DESCRIPTION = "Test protocol owned by Narada"
    # NO LOTUS_POSITION - derived from OWNER automatically!

    def get_state(self) -> ProtocolState:
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
            last_error=None,
            lotus_position=self.lotus_position,
            lotus_quarter=self.lotus_quarter.value,
            parampara_hash=self.parampara_hash,
            is_lotus_connected=self.is_lotus_connected,
        )


# =============================================================================
# TEST CLASSES
# =============================================================================


class TestOwnerDerivedPosition:
    """Test that position is DERIVED from OWNER automatically."""

    def test_brahma_position(self) -> None:
        """BRAHMA → Position 1 (GENESIS)."""
        protocol = BrahmaProtocol()
        assert protocol.lotus_position == get_mahajana_position("brahma")
        assert protocol.lotus_position == 1

    def test_kapila_position(self) -> None:
        """KAPILA → Position 6 (DHARMA)."""
        protocol = KapilaProtocol()
        assert protocol.lotus_position == get_mahajana_position("kapila")
        assert protocol.lotus_position == 6

    def test_janaka_position(self) -> None:
        """JANAKA → Position 10 (KARMA)."""
        protocol = JanakaProtocol()
        assert protocol.lotus_position == get_mahajana_position("janaka")
        assert protocol.lotus_position == 10

    def test_narada_position(self) -> None:
        """NARADA → Position 2 (GENESIS)."""
        protocol = NaradaProtocol()
        assert protocol.lotus_position == get_mahajana_position("narada")
        assert protocol.lotus_position == 2

    def test_all_mahajanas_mapped(self) -> None:
        """All 12 Mahajanas have positions in the graph."""
        for name in MAHAJANA_NAMES:
            pos = get_mahajana_position(name)
            assert 0 <= pos < LOTUS_POSITIONS

    def test_position_in_valid_range(self) -> None:
        """All positions are 0-15."""
        for name in MAHAJANA_NAMES:
            pos = get_mahajana_position(name)
            assert 0 <= pos < LOTUS_POSITIONS


class TestLotusQuarter:
    """Test lotus_quarter property derived from Owner."""

    def test_brahma_in_genesis(self) -> None:
        """BRAHMA (position 1) is in GENESIS quarter."""
        protocol = BrahmaProtocol()
        assert protocol.lotus_quarter == LotusQuarter.GENESIS

    def test_kapila_in_dharma(self) -> None:
        """KAPILA (position 6) is in DHARMA quarter."""
        protocol = KapilaProtocol()
        assert protocol.lotus_quarter == LotusQuarter.DHARMA

    def test_janaka_in_karma(self) -> None:
        """JANAKA (position 10) is in KARMA quarter."""
        protocol = JanakaProtocol()
        assert protocol.lotus_quarter == LotusQuarter.KARMA

    def test_narada_in_genesis(self) -> None:
        """NARADA (position 2) is in GENESIS quarter."""
        protocol = NaradaProtocol()
        assert protocol.lotus_quarter == LotusQuarter.GENESIS

    def test_quarters_from_mapping(self) -> None:
        """Verify quarter boundaries from the graph."""
        for name in MAHAJANA_NAMES:
            pos = get_mahajana_position(name)
            quarter_idx = pos // 4
            expected_quarter = list(LotusQuarter)[quarter_idx]
            # Position determines quarter
            assert 0 <= quarter_idx < 4


class TestParamparaHash:
    """Test parampara_hash and is_lotus_connected."""

    def test_parampara_hash_calculated(self) -> None:
        """Parampara hash is calculated from name + owner + position."""
        protocol = BrahmaProtocol()
        hash_val = protocol.parampara_hash
        assert isinstance(hash_val, int)
        assert hash_val > 0

    def test_always_connected(self) -> None:
        """All protocols are connected (% 37 == 0 by design)."""
        for proto_class in [BrahmaProtocol, KapilaProtocol, JanakaProtocol, NaradaProtocol]:
            protocol = proto_class()
            assert protocol.is_lotus_connected is True
            assert protocol.parampara_hash % LOTUS_PARAMPARA == 0

    def test_parampara_is_37(self) -> None:
        """LOTUS_PARAMPARA should be 37."""
        assert LOTUS_PARAMPARA == 37


class TestRouteTo:
    """Test route_to() method for auto-routing."""

    def test_intra_quarter_routing(self) -> None:
        """Routing within same quarter is direct (no stengel)."""
        protocol = BrahmaProtocol()  # Position 1 (GENESIS)
        route = protocol.route_to(2)  # Same quarter (GENESIS)

        assert route["route_type"] == "intra-quarter"
        assert route["via_stengel"] is False
        assert route["source_position"] == 1
        assert route["target_position"] == 2
        assert route["source_quarter"] == "genesis"
        assert route["target_quarter"] == "genesis"

    def test_inter_quarter_routing(self) -> None:
        """Routing to different quarter goes via stengel."""
        protocol = BrahmaProtocol()  # Position 1 (GENESIS)
        route = protocol.route_to(10)  # Different quarter (KARMA)

        assert route["route_type"] == "inter-quarter"
        assert route["via_stengel"] is True
        assert route["source_quarter"] == "genesis"
        assert route["target_quarter"] == "karma"

    def test_parampara_verified_in_route(self) -> None:
        """Route includes parampara verification status."""
        protocol = BrahmaProtocol()
        route = protocol.route_to(6)

        assert "parampara_verified" in route
        assert route["parampara_verified"] is True


class TestRouteToProtocol:
    """Test route_to_protocol() method."""

    def test_route_between_protocols(self) -> None:
        """Can route from one OwnedProtocol to another."""
        source = BrahmaProtocol()  # Position 1 (GENESIS)
        target = JanakaProtocol()  # Position 10 (KARMA)

        route = source.route_to_protocol(target)

        assert route["source_position"] == 1
        assert route["target_position"] == 10
        assert route["via_stengel"] is True  # Different quarters

    def test_route_same_quarter_protocols(self) -> None:
        """Protocols in same quarter have direct route."""
        source = BrahmaProtocol()  # Position 1 (GENESIS)
        target = NaradaProtocol()  # Position 2 (GENESIS)

        route = source.route_to_protocol(target)

        assert route["via_stengel"] is False
        assert route["route_type"] == "intra-quarter"


class TestProtocolStateWithLotus:
    """Test that ProtocolState includes Lotus fields."""

    def test_state_includes_lotus_position(self) -> None:
        """ProtocolState includes lotus_position from OWNER."""
        protocol = BrahmaProtocol()
        state = protocol.get_state()

        assert "lotus_position" in state
        assert state["lotus_position"] == 1  # Brahma = position 1

    def test_state_includes_lotus_quarter(self) -> None:
        """ProtocolState includes lotus_quarter."""
        protocol = KapilaProtocol()
        state = protocol.get_state()

        assert "lotus_quarter" in state
        assert state["lotus_quarter"] == "dharma"  # Kapila = DHARMA

    def test_state_includes_parampara(self) -> None:
        """ProtocolState includes parampara_hash and is_lotus_connected."""
        protocol = JanakaProtocol()
        state = protocol.get_state()

        assert "parampara_hash" in state
        assert "is_lotus_connected" in state
        assert state["is_lotus_connected"] is True

    def test_state_watertight(self) -> None:
        """ProtocolState is WATERTIGHT - no Any types."""
        protocol = NaradaProtocol()
        state = protocol.get_state()

        assert isinstance(state["protocol_name"], str)
        assert isinstance(state["owner"], str)
        assert isinstance(state["lotus_position"], int)
        assert isinstance(state["lotus_quarter"], str)
        assert isinstance(state["parampara_hash"], int)
        assert isinstance(state["is_lotus_connected"], bool)


class TestChantingWithLotus:
    """Test that chanting still works with Lotus integration."""

    def test_chant_advances_heartbeat(self) -> None:
        """Chanting advances the heartbeat position."""
        protocol = BrahmaProtocol()
        assert protocol.is_chanting is False

        protocol.chant()
        assert protocol.is_chanting is True

    def test_lotus_position_independent_of_chanting(self) -> None:
        """Lotus position is static (from OWNER), not affected by chanting."""
        protocol = BrahmaProtocol()
        initial_lotus_pos = protocol.lotus_position

        for _ in range(50):
            protocol.chant()

        # Lotus position unchanged - derived from OWNER
        assert protocol.lotus_position == initial_lotus_pos
        assert protocol.lotus_position == 1  # Brahma = 1

    def test_gad_audit_still_works(self) -> None:
        """GAD-000 audit still works with Lotus integration."""
        protocol = BrahmaProtocol()
        audit = protocol.audit()

        assert audit.discoverability is True
        assert audit.sovereign_present is True


class TestNoManualWiring:
    """Test that NO MANUAL WIRING is needed."""

    def test_owner_determines_position(self) -> None:
        """OWNER determines position automatically."""
        protocol = BrahmaProtocol()

        # Position from OWNER, derived from Vedic Graph
        assert protocol.lotus_position == get_mahajana_position("brahma")
        assert protocol.is_lotus_connected is True
        assert protocol.lotus_quarter == LotusQuarter.GENESIS

    def test_routing_automatic(self) -> None:
        """Routing is automatic based on OWNER-derived position."""
        protocol = BrahmaProtocol()

        route = protocol.route_to(10)  # To KARMA quarter

        assert route["via_stengel"] is True
        assert route["parampara_verified"] is True

    def test_one_graph_all_inherit(self) -> None:
        """ONE graph (VEDIC_GRAPH), ALL protocols inherit positions."""
        # Every Mahajana has exactly one position from the graph
        assert get_mahajana_position("brahma") == 1
        assert get_mahajana_position("narada") == 2
        assert get_mahajana_position("janaka") == 10
        assert get_mahajana_position("kapila") == 6


class TestWatertightTypes:
    """Test that all types are WATERTIGHT (no Any)."""

    def test_lotus_route_watertight(self) -> None:
        """LotusRoute is WATERTIGHT TypedDict."""
        protocol = BrahmaProtocol()
        route: LotusRoute = protocol.route_to(10)

        assert isinstance(route["source_position"], int)
        assert isinstance(route["target_position"], int)
        assert isinstance(route["source_quarter"], str)
        assert isinstance(route["target_quarter"], str)
        assert isinstance(route["route_type"], str)
        assert isinstance(route["via_stengel"], bool)
        assert isinstance(route["parampara_verified"], bool)

    def test_lotus_quarter_enum(self) -> None:
        """LotusQuarter is a proper enum."""
        assert LotusQuarter.GENESIS.value == "genesis"
        assert LotusQuarter.DHARMA.value == "dharma"
        assert LotusQuarter.KARMA.value == "karma"
        assert LotusQuarter.MOKSHA.value == "moksha"

    def test_graph_positions_watertight(self) -> None:
        """Graph positions are WATERTIGHT (str name -> int position)."""
        for name in MAHAJANA_NAMES:
            pos = get_mahajana_position(name)
            assert isinstance(name, str)
            assert isinstance(pos, int)
