"""
TESTS: yajna.py - The Offering Architecture
===========================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ"

REAL TESTS for:
1. Constants (PRIME_SIGNATURE, MAHA_POSITIONS, etc.)
2. Exceptions (DissonanceError, TamasBlockError, ParamparaBreakError)
3. Guna enum
4. Bhoga and Prasadam dataclasses
5. MantraByte class
6. Yajna class
7. Convenience functions (get_yajna, offer)
"""

import pytest
from vibe_core.mahamantra.substrate.yajna import (
    # Constants
    PRIME_SIGNATURE,
    MAHA_POSITIONS,
    MALA_ROUNDS,
    TRINITY,
    STD_MANTRA_PATTERN,
    # Exceptions
    DissonanceError,
    TamasBlockError,
    ParamparaBreakError,
    # Enums
    Guna,
    HolyName,
    # Types
    Bhoga,
    Prasadam,
    # Core
    MantraByte,
    Yajna,
    # Functions
    get_yajna,
    offer,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestYajnaConstants:
    """Test Yajna constants."""

    def test_prime_signature_is_37(self):
        """PRIME_SIGNATURE is 37."""
        assert PRIME_SIGNATURE == 37

    def test_maha_positions_is_16(self):
        """MAHA_POSITIONS is 16."""
        assert MAHA_POSITIONS == 16

    def test_mala_rounds_is_108(self):
        """MALA_ROUNDS is 108."""
        assert MALA_ROUNDS == 108

    def test_trinity_is_3(self):
        """TRINITY is 3."""
        assert TRINITY == 3

    def test_std_mantra_pattern_exists(self):
        """STD_MANTRA_PATTERN exists."""
        assert STD_MANTRA_PATTERN is not None
        assert isinstance(STD_MANTRA_PATTERN, int)


# =============================================================================
# Exceptions Tests
# =============================================================================


class TestYajnaExceptions:
    """Test Yajna exceptions."""

    def test_dissonance_error_is_value_error(self):
        """DissonanceError inherits from ValueError."""
        assert issubclass(DissonanceError, ValueError)

    def test_tamas_block_error_is_permission_error(self):
        """TamasBlockError inherits from PermissionError."""
        assert issubclass(TamasBlockError, PermissionError)

    def test_parampara_break_error_is_value_error(self):
        """ParamparaBreakError inherits from ValueError."""
        assert issubclass(ParamparaBreakError, ValueError)

    def test_can_raise_dissonance_error(self):
        """Can raise DissonanceError."""
        with pytest.raises(DissonanceError):
            raise DissonanceError("Spiritual frequency too low")

    def test_can_raise_tamas_block_error(self):
        """Can raise TamasBlockError."""
        with pytest.raises(TamasBlockError):
            raise TamasBlockError("TAMAS operation blocked")

    def test_can_raise_parampara_break_error(self):
        """Can raise ParamparaBreakError."""
        with pytest.raises(ParamparaBreakError):
            raise ParamparaBreakError("Lineage broken")


# =============================================================================
# Guna Enum Tests
# =============================================================================


class TestGuna:
    """Test Guna enum."""

    def test_guna_has_3_modes(self):
        """Guna has 3 modes."""
        assert len(Guna) == 3

    def test_sattva_is_0(self):
        """SATTVA is 0."""
        assert Guna.SATTVA.value == 0

    def test_rajas_is_1(self):
        """RAJAS is 1."""
        assert Guna.RAJAS.value == 1

    def test_tamas_is_2(self):
        """TAMAS is 2."""
        assert Guna.TAMAS.value == 2

    def test_guna_is_int_enum(self):
        """Guna is IntEnum."""
        from enum import IntEnum

        assert issubclass(Guna, IntEnum)


# =============================================================================
# HolyName Enum Tests
# =============================================================================


class TestHolyName:
    """Test HolyName enum."""

    def test_holy_name_has_hare(self):
        """HolyName has HARE."""
        assert hasattr(HolyName, "HARE")

    def test_holy_name_has_krishna(self):
        """HolyName has KRISHNA."""
        assert hasattr(HolyName, "KRISHNA")

    def test_holy_name_has_rama(self):
        """HolyName has RAMA."""
        assert hasattr(HolyName, "RAMA")


# =============================================================================
# Bhoga Dataclass Tests
# =============================================================================


class TestBhoga:
    """Test Bhoga dataclass."""

    def test_bhoga_creation(self):
        """Bhoga can be created."""
        bhoga = Bhoga(
            operation="test_op",
            payload={"data": "value"},
            position=0,
            guna=Guna.SATTVA,
        )
        assert bhoga.operation == "test_op"
        assert bhoga.position == 0
        assert bhoga.guna == Guna.SATTVA

    def test_bhoga_is_frozen(self):
        """Bhoga is frozen (immutable)."""
        bhoga = Bhoga(
            operation="test",
            payload={},
            position=0,
            guna=Guna.SATTVA,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            bhoga.operation = "changed"

    def test_bhoga_requires_confirmation_tamas(self):
        """TAMAS bhoga requires confirmation."""
        bhoga = Bhoga(
            operation="delete",
            payload={},
            position=0,
            guna=Guna.TAMAS,
        )
        assert bhoga.requires_confirmation is True

    def test_bhoga_no_confirmation_sattva(self):
        """SATTVA bhoga doesn't require confirmation."""
        bhoga = Bhoga(
            operation="read",
            payload={},
            position=0,
            guna=Guna.SATTVA,
        )
        assert bhoga.requires_confirmation is False

    def test_bhoga_no_confirmation_rajas(self):
        """RAJAS bhoga doesn't require confirmation."""
        bhoga = Bhoga(
            operation="write",
            payload={},
            position=0,
            guna=Guna.RAJAS,
        )
        assert bhoga.requires_confirmation is False

    def test_bhoga_has_timestamp(self):
        """Bhoga has timestamp."""
        bhoga = Bhoga(
            operation="test",
            payload={},
            position=0,
            guna=Guna.SATTVA,
        )
        assert bhoga.timestamp > 0


# =============================================================================
# Prasadam Dataclass Tests
# =============================================================================


class TestPrasadam:
    """Test Prasadam dataclass."""

    def test_prasadam_blessed_creation(self):
        """Prasadam.blessed creates successful prasadam."""
        prasadam = Prasadam.blessed(
            result="success",
            position=0,
            guardian="prithu",
            guna=Guna.SATTVA,
        )
        assert prasadam.success is True
        assert prasadam.result == "success"
        assert prasadam.error is None
        assert prasadam.parampara_valid is True

    def test_prasadam_rejected_creation(self):
        """Prasadam.rejected creates failed prasadam."""
        prasadam = Prasadam.rejected(
            error="Operation failed",
            position=0,
            guardian="prithu",
            guna=Guna.TAMAS,
        )
        assert prasadam.success is False
        assert prasadam.result is None
        assert prasadam.error == "Operation failed"
        assert prasadam.parampara_valid is False

    def test_prasadam_is_frozen(self):
        """Prasadam is frozen (immutable)."""
        prasadam = Prasadam.blessed(
            result="test",
            position=0,
            guardian="test",
            guna=Guna.SATTVA,
        )
        with pytest.raises(Exception):
            prasadam.success = False

    def test_prasadam_has_coherence(self):
        """Prasadam has coherence field."""
        prasadam = Prasadam.blessed(
            result="test",
            position=0,
            guardian="test",
            guna=Guna.SATTVA,
            coherence=0.95,
        )
        assert prasadam.coherence == 0.95


# =============================================================================
# MantraByte Tests
# =============================================================================


class TestMantraByte:
    """Test MantraByte class."""

    def test_mantra_byte_standard_creation(self):
        """MantraByte.standard() creates standard mantra."""
        mantra = MantraByte.standard()
        assert mantra is not None

    def test_mantra_byte_packed_value(self):
        """MantraByte has packed value."""
        mantra = MantraByte.standard()
        assert mantra.packed == STD_MANTRA_PATTERN

    def test_mantra_byte_get_name_valid(self):
        """get_name returns HolyName for valid index."""
        mantra = MantraByte.standard()
        name = mantra.get_name(0)
        assert isinstance(name, HolyName)

    def test_mantra_byte_get_name_invalid(self):
        """get_name returns VOID for invalid index."""
        mantra = MantraByte.standard()
        name = mantra.get_name(100)
        assert name == HolyName.VOID

    def test_mantra_byte_resonance_check(self):
        """resonance_check returns coherence score (COSMIC_FRAME scaled)."""
        mantra = MantraByte.standard()
        coherence = mantra.resonance_check()
        assert 0 <= coherence <= 21600

    def test_mantra_byte_standard_is_coherent(self):
        """Standard MantraByte is fully coherent (COSMIC_FRAME = 21600)."""
        mantra = MantraByte.standard()
        coherence = mantra.resonance_check()
        assert coherence == 21600

    def test_mantra_byte_validate_parampara_37(self):
        """validate_parampara returns True for 37."""
        mantra = MantraByte()
        assert mantra.validate_parampara(37) is True

    def test_mantra_byte_validate_parampara_74(self):
        """validate_parampara returns True for 74."""
        mantra = MantraByte()
        assert mantra.validate_parampara(74) is True

    def test_mantra_byte_validate_parampara_36(self):
        """validate_parampara returns False for 36."""
        mantra = MantraByte()
        assert mantra.validate_parampara(36) is False

    def test_mantra_byte_is_iterable(self):
        """MantraByte is iterable."""
        mantra = MantraByte.standard()
        names = list(mantra)
        assert len(names) == MAHA_POSITIONS

    def test_mantra_byte_repr(self):
        """MantraByte has repr."""
        mantra = MantraByte.standard()
        repr_str = repr(mantra)
        assert "MantraByte" in repr_str


# =============================================================================
# Yajna Class Tests
# =============================================================================


class TestYajna:
    """Test Yajna class."""

    def test_yajna_creation(self):
        """Yajna can be created."""
        yajna = Yajna()
        assert yajna is not None

    def test_yajna_coherence(self):
        """Yajna has coherence property (COSMIC_FRAME scaled)."""
        yajna = Yajna()
        assert 0 <= yajna.coherence <= 21600

    def test_yajna_position(self):
        """Yajna has position property."""
        yajna = Yajna()
        assert yajna.position == 0

    def test_yajna_chant_advances_position(self):
        """chant() advances position."""
        yajna = Yajna()
        initial_pos = yajna.position
        yajna.chant()
        assert yajna.position == (initial_pos + 1) % MAHA_POSITIONS

    def test_yajna_chant_returns_true(self):
        """chant() returns True for valid state."""
        yajna = Yajna()
        result = yajna.chant()
        assert result is True

    def test_yajna_confirm_tamas(self):
        """confirm_tamas() sets confirmation flag."""
        yajna = Yajna()
        yajna.confirm_tamas()
        # Internal flag should be set
        assert yajna._confirmed_tamas is True

    def test_yajna_reset_confirmation(self):
        """reset_confirmation() clears flag."""
        yajna = Yajna()
        yajna.confirm_tamas()
        yajna.reset_confirmation()
        assert yajna._confirmed_tamas is False


# =============================================================================
# Yajna.offer Tests
# =============================================================================


class TestYajnaOffer:
    """Test Yajna.offer method."""

    def test_offer_sattva_succeeds(self):
        """SATTVA offer succeeds."""
        yajna = Yajna()
        bhoga = Bhoga(
            operation="status",
            payload={},
            position=0,
            guna=Guna.SATTVA,
        )
        prasadam = yajna.offer(bhoga, lambda x: {"status": "ok"})
        assert prasadam.success is True

    def test_offer_tamas_without_confirmation_raises(self):
        """TAMAS without confirmation raises TamasBlockError."""
        yajna = Yajna()
        bhoga = Bhoga(
            operation="delete",
            payload={},
            position=0,
            guna=Guna.TAMAS,
        )
        with pytest.raises(TamasBlockError):
            yajna.offer(bhoga, lambda x: None)

    def test_offer_tamas_with_confirmation_succeeds(self):
        """TAMAS with confirmation succeeds."""
        yajna = Yajna()
        yajna.confirm_tamas()
        bhoga = Bhoga(
            operation="delete",
            payload={},
            position=0,
            guna=Guna.TAMAS,
        )
        prasadam = yajna.offer(bhoga, lambda x: "deleted")
        assert prasadam.success is True

    def test_offer_handler_exception_returns_rejected(self):
        """Handler exception returns rejected prasadam."""
        yajna = Yajna()
        bhoga = Bhoga(
            operation="failing",
            payload={},
            position=0,
            guna=Guna.SATTVA,
        )

        def failing_handler(x):
            raise ValueError("Handler error")

        prasadam = yajna.offer(bhoga, failing_handler)
        assert prasadam.success is False
        assert "Handler error" in prasadam.error


# =============================================================================
# get_yajna Singleton Tests
# =============================================================================


class TestGetYajna:
    """Test get_yajna function."""

    def test_get_yajna_returns_yajna(self):
        """get_yajna returns Yajna instance."""
        yajna = get_yajna()
        assert isinstance(yajna, Yajna)

    def test_get_yajna_returns_same_instance(self):
        """get_yajna returns same instance (singleton)."""
        yajna1 = get_yajna()
        yajna2 = get_yajna()
        assert yajna1 is yajna2


# =============================================================================
# offer Convenience Function Tests
# =============================================================================


class TestOfferFunction:
    """Test offer convenience function."""

    def test_offer_function_works(self):
        """offer() convenience function works."""
        prasadam = offer(
            operation="test",
            payload={"data": "value"},
            position=0,
            guna=Guna.SATTVA,
            handler=lambda x: x["data"],
        )
        assert prasadam.success is True
        assert prasadam.result == "value"


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import yajna

        expected = [
            "PRIME_SIGNATURE",
            "MAHA_POSITIONS",
            "MALA_ROUNDS",
            "TRINITY",
            "DissonanceError",
            "TamasBlockError",
            "ParamparaBreakError",
            "Guna",
            "HolyName",
            "Bhoga",
            "Prasadam",
            "MantraByte",
            "Yajna",
            "get_yajna",
            "offer",
        ]
        for item in expected:
            assert item in yajna.__all__, f"{item} should be in __all__"
