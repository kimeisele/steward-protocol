"""
TESTS: kernel/singularity.py - The Mahamantra Object
=====================================================

REAL TESTS for:
1. TickState TypedDict
2. ProtocolRouter class
3. ModuleRouter class
4. Mahamantra class
5. mahamantra singleton
"""

import pytest
from vibe_core.mahamantra.kernel.singularity import (
    TickState,
    ProtocolRouter,
    ModuleRouter,
    Mahamantra,
    mahamantra,
)
from vibe_core.mahamantra.substrate import (
    MantraPosition,
    Quarter,
    Mahajana,
    Avatara,
)
from vibe_core.mahamantra.substrate.seed import PARAMPARA, WORDS


# =============================================================================
# TickState TypedDict Tests
# =============================================================================


class TestTickState:
    """Test TickState TypedDict."""

    def test_tick_state_creation(self):
        """TickState can be created."""
        state: TickState = {
            "tick": 5,
            "position": 5,
            "quarter": "dharma",
            "guardian": "kumaras",
            "word": "krishna",
            "opcode": 5,
            "mala": 0,
            "mantra": 0,
            "lila": 5,
        }
        assert state["tick"] == 5
        assert state["quarter"] == "dharma"

    def test_tick_state_required_fields(self):
        """TickState has all required fields."""
        state: TickState = {
            "tick": 0,
            "position": 0,
            "quarter": "genesis",
            "guardian": "vyasa",
            "word": "hare",
            "opcode": None,
            "mala": 0,
            "mantra": 0,
            "lila": 0,
        }
        assert "tick" in state
        assert "position" in state
        assert "quarter" in state
        assert "guardian" in state
        assert "word" in state
        assert "opcode" in state
        assert "mala" in state
        assert "mantra" in state
        assert "lila" in state


# =============================================================================
# ProtocolRouter Tests
# =============================================================================


class TestProtocolRouter:
    """Test ProtocolRouter class."""

    def test_protocol_router_creation(self):
        """ProtocolRouter can be created."""
        router = ProtocolRouter()
        assert router is not None

    def test_protocol_router_repr(self):
        """ProtocolRouter has string representation."""
        router = ProtocolRouter()
        assert repr(router) == "ProtocolRouter(16 positions)"

    def test_protocol_router_getitem(self):
        """ProtocolRouter can access by index."""
        router = ProtocolRouter()
        # This loads the protocol base for position 0
        base = router[0]
        assert base is not None

    def test_protocol_router_getitem_invalid(self):
        """ProtocolRouter raises KeyError for invalid index."""
        router = ProtocolRouter()
        with pytest.raises(KeyError):
            _ = router[99]

    def test_protocol_router_getitem_negative(self):
        """ProtocolRouter raises KeyError for negative index."""
        router = ProtocolRouter()
        with pytest.raises(KeyError):
            _ = router[-1]

    def test_protocol_router_by_name(self):
        """ProtocolRouter can access by name."""
        router = ProtocolRouter()
        base = router.by_name("vyasa")
        assert base is not None

    def test_protocol_router_by_name_invalid(self):
        """ProtocolRouter raises KeyError for unknown guardian."""
        router = ProtocolRouter()
        with pytest.raises(KeyError):
            router.by_name("unknown_xyz")

    def test_protocol_router_property_vyasa(self):
        """ProtocolRouter.vyasa returns position 0."""
        router = ProtocolRouter()
        base = router.vyasa
        assert base is not None

    def test_protocol_router_property_brahma(self):
        """ProtocolRouter.brahma returns position 1."""
        router = ProtocolRouter()
        base = router.brahma
        assert base is not None

    def test_protocol_router_property_narada(self):
        """ProtocolRouter.narada returns position 2."""
        router = ProtocolRouter()
        base = router.narada
        assert base is not None

    def test_protocol_router_property_yamaraja(self):
        """ProtocolRouter.yamaraja returns position 15."""
        router = ProtocolRouter()
        base = router.yamaraja
        assert base is not None

    def test_protocol_router_caching(self):
        """ProtocolRouter caches loaded bases."""
        router = ProtocolRouter()
        base1 = router[0]
        base2 = router[0]
        assert base1 is base2


# =============================================================================
# ModuleRouter Tests
# =============================================================================


class TestModuleRouter:
    """Test ModuleRouter class."""

    def test_module_router_creation(self):
        """ModuleRouter can be created."""
        router = ModuleRouter()
        assert router is not None

    def test_module_router_repr(self):
        """ModuleRouter has string representation."""
        router = ModuleRouter()
        assert repr(router) == "ModuleRouter(16 modules)"

    def test_module_router_getattr(self):
        """ModuleRouter can access by attribute."""
        router = ModuleRouter()
        module = router.vyasa
        assert module is not None

    def test_module_router_getattr_invalid(self):
        """ModuleRouter raises AttributeError for unknown module."""
        router = ModuleRouter()
        with pytest.raises(AttributeError):
            _ = router.unknown_xyz

    def test_module_router_getitem(self):
        """ModuleRouter can access by index."""
        router = ModuleRouter()
        module = router[0]
        assert module is not None

    def test_module_router_getitem_invalid(self):
        """ModuleRouter raises KeyError for invalid index."""
        router = ModuleRouter()
        with pytest.raises(KeyError):
            _ = router[99]

    def test_module_router_caching(self):
        """ModuleRouter caches loaded modules."""
        router = ModuleRouter()
        mod1 = router.vyasa
        mod2 = router.vyasa
        assert mod1 is mod2


# =============================================================================
# Mahamantra Tests
# =============================================================================


class TestMahamantra:
    """Test Mahamantra class."""

    def test_mahamantra_creation(self):
        """Mahamantra can be created."""
        m = Mahamantra()
        assert m is not None

    def test_mahamantra_parampara_constant(self):
        """Mahamantra.PARAMPARA is 37."""
        m = Mahamantra()
        assert m.PARAMPARA == 37
        assert m.PARAMPARA == PARAMPARA

    def test_mahamantra_len(self):
        """len(mahamantra) is 16."""
        m = Mahamantra()
        assert len(m) == 16
        assert len(m) == WORDS

    def test_mahamantra_getitem(self):
        """mahamantra[i] returns MantraPosition."""
        m = Mahamantra()
        pos = m[0]
        assert isinstance(pos, MantraPosition)

    def test_mahamantra_getitem_all_positions(self):
        """mahamantra[i] works for all 16 positions."""
        m = Mahamantra()
        for i in range(16):
            pos = m[i]
            assert isinstance(pos, MantraPosition)
            assert pos.index == i

    def test_mahamantra_iter(self):
        """for pos in mahamantra works."""
        m = Mahamantra()
        positions = list(m)
        assert len(positions) == 16
        for pos in positions:
            assert isinstance(pos, MantraPosition)

    def test_mahamantra_repr(self):
        """mahamantra has string representation."""
        m = Mahamantra()
        assert repr(m) == "Mahamantra(16 positions, 37 connection)"

    # -------------------------------------------------------------------------
    # Guardian Properties
    # -------------------------------------------------------------------------

    def test_mahamantra_vyasa(self):
        """mahamantra.vyasa returns position 0."""
        m = Mahamantra()
        pos = m.vyasa
        assert pos.index == 0

    def test_mahamantra_brahma(self):
        """mahamantra.brahma returns position 1."""
        m = Mahamantra()
        pos = m.brahma
        assert pos.index == 1

    def test_mahamantra_narada(self):
        """mahamantra.narada returns position 2."""
        m = Mahamantra()
        pos = m.narada
        assert pos.index == 2

    def test_mahamantra_shambhu(self):
        """mahamantra.shambhu returns position 3."""
        m = Mahamantra()
        pos = m.shambhu
        assert pos.index == 3

    def test_mahamantra_prithu(self):
        """mahamantra.prithu returns position 4."""
        m = Mahamantra()
        pos = m.prithu
        assert pos.index == 4

    def test_mahamantra_kumaras(self):
        """mahamantra.kumaras returns position 5."""
        m = Mahamantra()
        pos = m.kumaras
        assert pos.index == 5

    def test_mahamantra_kapila(self):
        """mahamantra.kapila returns position 6."""
        m = Mahamantra()
        pos = m.kapila
        assert pos.index == 6

    def test_mahamantra_manu(self):
        """mahamantra.manu returns position 7."""
        m = Mahamantra()
        pos = m.manu
        assert pos.index == 7

    def test_mahamantra_parashurama(self):
        """mahamantra.parashurama returns position 8."""
        m = Mahamantra()
        pos = m.parashurama
        assert pos.index == 8

    def test_mahamantra_prahlada(self):
        """mahamantra.prahlada returns position 9."""
        m = Mahamantra()
        pos = m.prahlada
        assert pos.index == 9

    def test_mahamantra_janaka(self):
        """mahamantra.janaka returns position 10."""
        m = Mahamantra()
        pos = m.janaka
        assert pos.index == 10

    def test_mahamantra_bhishma(self):
        """mahamantra.bhishma returns position 11."""
        m = Mahamantra()
        pos = m.bhishma
        assert pos.index == 11

    def test_mahamantra_nrisimha(self):
        """mahamantra.nrisimha returns position 12."""
        m = Mahamantra()
        pos = m.nrisimha
        assert pos.index == 12

    def test_mahamantra_bali(self):
        """mahamantra.bali returns position 13."""
        m = Mahamantra()
        pos = m.bali
        assert pos.index == 13

    def test_mahamantra_shuka(self):
        """mahamantra.shuka returns position 14."""
        m = Mahamantra()
        pos = m.shuka
        assert pos.index == 14

    def test_mahamantra_yamaraja(self):
        """mahamantra.yamaraja returns position 15."""
        m = Mahamantra()
        pos = m.yamaraja
        assert pos.index == 15

    # -------------------------------------------------------------------------
    # Quarter Properties
    # -------------------------------------------------------------------------

    def test_mahamantra_genesis(self):
        """mahamantra.genesis returns positions 0-3."""
        m = Mahamantra()
        positions = m.genesis
        assert len(positions) == 4
        assert [p.index for p in positions] == [0, 1, 2, 3]

    def test_mahamantra_dharma(self):
        """mahamantra.dharma returns positions 4-7."""
        m = Mahamantra()
        positions = m.dharma
        assert len(positions) == 4
        assert [p.index for p in positions] == [4, 5, 6, 7]

    def test_mahamantra_karma(self):
        """mahamantra.karma returns positions 8-11."""
        m = Mahamantra()
        positions = m.karma
        assert len(positions) == 4
        assert [p.index for p in positions] == [8, 9, 10, 11]

    def test_mahamantra_moksha(self):
        """mahamantra.moksha returns positions 12-15."""
        m = Mahamantra()
        positions = m.moksha
        assert len(positions) == 4
        assert [p.index for p in positions] == [12, 13, 14, 15]

    def test_mahamantra_quarters(self):
        """mahamantra.quarters returns all 4 quarters."""
        m = Mahamantra()
        quarters = m.quarters
        assert len(quarters) == 4
        assert "genesis" in quarters
        assert "dharma" in quarters
        assert "karma" in quarters
        assert "moksha" in quarters

    # -------------------------------------------------------------------------
    # Group Properties
    # -------------------------------------------------------------------------

    def test_mahamantra_positions(self):
        """mahamantra.positions returns all 16 positions."""
        m = Mahamantra()
        assert len(m.positions) == 16

    def test_mahamantra_heads(self):
        """mahamantra.heads returns 4 HEADs."""
        m = Mahamantra()
        heads = m.heads
        assert len(heads) == 4
        # HEADs are at positions 0, 4, 8, 12
        assert [h.index for h in heads] == [0, 4, 8, 12]

    def test_mahamantra_workers(self):
        """mahamantra.workers returns 12 Workers."""
        m = Mahamantra()
        workers = m.workers
        assert len(workers) == 12

    # -------------------------------------------------------------------------
    # Routing Properties
    # -------------------------------------------------------------------------

    def test_mahamantra_protocols(self):
        """mahamantra.protocols returns ProtocolRouter."""
        m = Mahamantra()
        assert isinstance(m.protocols, ProtocolRouter)

    def test_mahamantra_mod(self):
        """mahamantra.mod returns ModuleRouter."""
        m = Mahamantra()
        assert isinstance(m.mod, ModuleRouter)

    def test_mahamantra_registry(self):
        """mahamantra.registry returns ProtocolRegistry."""
        m = Mahamantra()
        registry = m.registry
        assert registry is not None

    # -------------------------------------------------------------------------
    # Verify
    # -------------------------------------------------------------------------

    def test_mahamantra_verify_connected(self):
        """verify returns True for multiples of 37."""
        m = Mahamantra()
        assert m.verify(0) is True
        assert m.verify(37) is True
        assert m.verify(74) is True
        assert m.verify(444) is True

    def test_mahamantra_verify_disconnected(self):
        """verify returns False for non-multiples of 37."""
        m = Mahamantra()
        assert m.verify(1) is False
        assert m.verify(10) is False
        assert m.verify(36) is False
        assert m.verify(38) is False

    def test_mahamantra_is_connected(self):
        """is_connected is alias for verify."""
        m = Mahamantra()
        assert m.is_connected(37) is True
        assert m.is_connected(10) is False

    # -------------------------------------------------------------------------
    # Lookup
    # -------------------------------------------------------------------------

    def test_mahamantra_by_guardian_string(self):
        """by_guardian works with string."""
        m = Mahamantra()
        pos = m.by_guardian("brahma")
        assert pos.index == 1

    def test_mahamantra_by_guardian_mahajana(self):
        """by_guardian works with Mahajana."""
        m = Mahamantra()
        pos = m.by_guardian(Mahajana.BRAHMA)
        assert pos.index == 1

    def test_mahamantra_by_guardian_avatara(self):
        """by_guardian works with Avatara."""
        m = Mahamantra()
        pos = m.by_guardian(Avatara.VYASA)
        assert pos.index == 0

    def test_mahamantra_by_guardian_invalid(self):
        """by_guardian raises KeyError for unknown guardian."""
        m = Mahamantra()
        with pytest.raises(KeyError):
            m.by_guardian("unknown_xyz")

    # -------------------------------------------------------------------------
    # Tick and Chant
    # -------------------------------------------------------------------------

    def test_mahamantra_tick(self):
        """tick returns TickState."""
        m = Mahamantra()
        state = m.tick()
        assert "tick" in state
        assert "position" in state
        assert "quarter" in state
        assert "guardian" in state
        assert "word" in state

    def test_mahamantra_tick_advances(self):
        """tick advances the position."""
        m = Mahamantra()
        # Reset to known state
        Mahamantra._tick_counter = 0

        state1 = m.tick()
        state2 = m.tick()

        # Positions should differ (modulo 16)
        assert state1["tick"] != state2["tick"] or state1["tick"] == 15

    def test_mahamantra_get_tick(self):
        """get_tick returns current position."""
        m = Mahamantra()
        tick = m.get_tick()
        assert 0 <= tick < 16

    def test_mahamantra_get_quarter(self):
        """get_quarter returns current quarter."""
        m = Mahamantra()
        quarter = m.get_quarter()
        assert quarter in (Quarter.GENESIS, Quarter.DHARMA, Quarter.KARMA, Quarter.MOKSHA)

    def test_mahamantra_chant_quarter(self):
        """chant_quarter returns words for one quarter."""
        m = Mahamantra()
        words = m.chant_quarter("genesis")
        # Genesis quarter has 4 words
        word_list = words.split()
        assert len(word_list) == 4

    def test_mahamantra_chant(self):
        """chant returns complete mantra."""
        m = Mahamantra()
        full = m.chant()
        # 16 words total
        words = full.split()
        assert len(words) == 16

    # -------------------------------------------------------------------------
    # Listeners
    # -------------------------------------------------------------------------

    def test_mahamantra_register_listener(self):
        """register_listener adds callback."""
        m = Mahamantra()
        received = []

        def listener(state):
            received.append(state)

        m.register_listener(listener)
        m.tick()

        assert len(received) >= 1

    def test_mahamantra_listener_receives_tick_state(self):
        """Listener receives TickState on tick."""
        m = Mahamantra()
        received = []

        def listener(state):
            received.append(state)

        m.register_listener(listener)
        m.tick()

        assert len(received) >= 1
        state = received[-1]
        assert "tick" in state
        assert "guardian" in state

    # -------------------------------------------------------------------------
    # Vedic Audit
    # -------------------------------------------------------------------------

    def test_mahamantra_vedic_audit(self):
        """vedic_audit returns audit dict."""
        m = Mahamantra()
        audit = m.vedic_audit()
        assert isinstance(audit, dict)
        assert "shabda" in audit
        assert "artha" in audit
        assert "pratyaya" in audit
        assert "karma" in audit

    def test_mahamantra_is_vedic(self):
        """is_vedic returns boolean."""
        m = Mahamantra()
        assert isinstance(m.is_vedic, bool)


# =============================================================================
# Singleton Tests
# =============================================================================


class TestMahamantraSingleton:
    """Test mahamantra singleton."""

    def test_singleton_exists(self):
        """mahamantra singleton exists."""
        assert mahamantra is not None

    def test_singleton_is_mahamantra(self):
        """mahamantra is Mahamantra instance."""
        assert isinstance(mahamantra, Mahamantra)

    def test_singleton_access_by_index(self):
        """mahamantra[i] works."""
        pos = mahamantra[5]
        assert pos.index == 5

    def test_singleton_access_by_guardian(self):
        """mahamantra.brahma works."""
        pos = mahamantra.brahma
        assert pos.index == 1

    def test_singleton_protocols_access(self):
        """mahamantra.protocols works."""
        router = mahamantra.protocols
        assert isinstance(router, ProtocolRouter)

    def test_singleton_mod_access(self):
        """mahamantra.mod works."""
        router = mahamantra.mod
        assert isinstance(router, ModuleRouter)


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.kernel import singularity

        expected = [
            "Mahamantra",
            "mahamantra",
            "ProtocolRouter",
            "ModuleRouter",
        ]
        for item in expected:
            assert item in singularity.__all__, f"{item} should be in __all__"
