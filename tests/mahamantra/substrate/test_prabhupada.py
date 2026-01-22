"""
TESTS: prabhupada.py - The Bona Fide Link
=========================================

"tasmād guruṁ prapadyeta jijñāsuḥ śreya uttamam"

REAL TESTS for:
1. Prabhupada class (singleton)
2. verify_link() method
3. transmit() method
4. prabhupada singleton instance
"""

import pytest
from vibe_core.mahamantra.substrate.prabhupada import (
    Prabhupada,
    prabhupada,
)


# =============================================================================
# Prabhupada Singleton Tests
# =============================================================================


class TestPrabhupadaSingleton:
    """Test Prabhupada singleton pattern."""

    def test_prabhupada_instance_exists(self):
        """prabhupada singleton instance exists."""
        assert prabhupada is not None

    def test_prabhupada_is_prabhupada_class(self):
        """prabhupada is instance of Prabhupada class."""
        assert isinstance(prabhupada, Prabhupada)

    def test_singleton_returns_same_instance(self):
        """Multiple Prabhupada() calls return same instance."""
        instance1 = Prabhupada()
        instance2 = Prabhupada()
        assert instance1 is instance2

    def test_singleton_matches_module_instance(self):
        """Prabhupada() matches module-level prabhupada."""
        instance = Prabhupada()
        assert instance is prabhupada


# =============================================================================
# verify_link() Method Tests
# =============================================================================


class TestVerifyLink:
    """Test Prabhupada.verify_link method."""

    def test_verify_link_no_identity_fails(self):
        """Object without __mahajana__ or mahajana fails."""
        class NoIdentity:
            pass

        result = prabhupada.verify_link(NoIdentity())
        assert result is False

    def test_verify_link_no_genesis_fails(self):
        """Object with identity but no genesis fails."""
        class NoGenesis:
            __mahajana__ = "vyasa"

        result = prabhupada.verify_link(NoGenesis())
        assert result is False

    def test_verify_link_invalid_genesis_fails(self):
        """Object with invalid genesis (not % 37) fails."""
        class InvalidGenesis:
            __mahajana__ = "vyasa"
            __genesis__ = "0x00000001"  # 1 is not divisible by 37

        result = prabhupada.verify_link(InvalidGenesis())
        assert result is False

    def test_verify_link_valid_genesis_succeeds(self):
        """Object with valid genesis (% 37 == 0) succeeds."""
        class ValidComponent:
            __mahajana__ = "vyasa"
            __genesis__ = "0x00000025"  # 37 in hex, divisible by 37

        result = prabhupada.verify_link(ValidComponent())
        assert result is True

    def test_verify_link_larger_valid_genesis(self):
        """Object with larger valid genesis succeeds."""
        class ValidComponent:
            __mahajana__ = "brahma"
            __genesis__ = "0x0000004a"  # 74 = 37 * 2

        result = prabhupada.verify_link(ValidComponent())
        assert result is True

    def test_verify_link_with_mahajana_attribute(self):
        """Object with mahajana (not __mahajana__) works."""
        class MahajanaAttr:
            mahajana = "narada"
            genesis = "0x00000025"  # 37

        result = prabhupada.verify_link(MahajanaAttr())
        assert result is True

    def test_verify_link_non_string_genesis_fails(self):
        """Non-string genesis fails."""
        class IntGenesis:
            __mahajana__ = "shambhu"
            __genesis__ = 37  # int, not string

        result = prabhupada.verify_link(IntGenesis())
        assert result is False

    def test_verify_link_invalid_hex_fails(self):
        """Invalid hex string fails."""
        class InvalidHex:
            __mahajana__ = "kapila"
            __genesis__ = "not_hex"

        result = prabhupada.verify_link(InvalidHex())
        assert result is False

    def test_verify_link_empty_genesis_fails(self):
        """Empty genesis string fails."""
        class EmptyGenesis:
            __mahajana__ = "manu"
            __genesis__ = ""

        result = prabhupada.verify_link(EmptyGenesis())
        assert result is False


# =============================================================================
# transmit() Method Tests
# =============================================================================


class TestTransmit:
    """Test Prabhupada.transmit method."""

    def test_transmit_returns_seed_unchanged(self):
        """transmit returns seed unchanged (As It Is)."""
        seed = "Hare Krishna Hare Krishna"
        result = prabhupada.transmit(seed)
        assert result == seed

    def test_transmit_preserves_empty_string(self):
        """transmit preserves empty string."""
        result = prabhupada.transmit("")
        assert result == ""

    def test_transmit_preserves_unicode(self):
        """transmit preserves unicode."""
        seed = "हरे कृष्ण हरे कृष्ण"
        result = prabhupada.transmit(seed)
        assert result == seed


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestProtocolCompliance:
    """Test Prabhupada protocol compliance."""

    def test_implements_prabhupada_protocol(self):
        """Prabhupada implements PrabhupadaProtocol."""
        from vibe_core.mahamantra.protocols._prabhupada import PrabhupadaProtocol
        assert isinstance(prabhupada, PrabhupadaProtocol)

    def test_has_verify_link(self):
        """Prabhupada has verify_link method."""
        assert hasattr(prabhupada, "verify_link")
        assert callable(prabhupada.verify_link)

    def test_has_transmit(self):
        """Prabhupada has transmit method."""
        assert hasattr(prabhupada, "transmit")
        assert callable(prabhupada.transmit)


# =============================================================================
# Parampara Validation Tests
# =============================================================================


class TestParamparaValidation:
    """Test parampara validation logic."""

    def test_37_is_valid(self):
        """37 (0x25) is valid parampara."""
        class Valid37:
            __mahajana__ = "test"
            __genesis__ = "0x00000025"  # 37

        assert prabhupada.verify_link(Valid37()) is True

    def test_74_is_valid(self):
        """74 (0x4a) is valid parampara (37 * 2)."""
        class Valid74:
            __mahajana__ = "test"
            __genesis__ = "0x0000004a"  # 74

        assert prabhupada.verify_link(Valid74()) is True

    def test_111_is_valid(self):
        """111 (0x6f) is valid parampara (37 * 3)."""
        class Valid111:
            __mahajana__ = "test"
            __genesis__ = "0x0000006f"  # 111

        assert prabhupada.verify_link(Valid111()) is True

    def test_444_is_valid(self):
        """444 (0x1bc) is valid parampara (37 * 12)."""
        class Valid444:
            __mahajana__ = "test"
            __genesis__ = "0x000001bc"  # 444

        assert prabhupada.verify_link(Valid444()) is True

    def test_36_is_invalid(self):
        """36 is not valid parampara."""
        class Invalid36:
            __mahajana__ = "test"
            __genesis__ = "0x00000024"  # 36

        assert prabhupada.verify_link(Invalid36()) is False

    def test_38_is_invalid(self):
        """38 is not valid parampara."""
        class Invalid38:
            __mahajana__ = "test"
            __genesis__ = "0x00000026"  # 38

        assert prabhupada.verify_link(Invalid38()) is False


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Test edge cases for Prabhupada."""

    def test_verify_link_none_object(self):
        """verify_link with None-like object."""
        # None itself doesn't have attributes, so hasattr returns False
        class NullLike:
            pass

        result = prabhupada.verify_link(NullLike())
        assert result is False

    def test_verify_link_zero_genesis(self):
        """Zero genesis (0x0) is divisible by 37."""
        class ZeroGenesis:
            __mahajana__ = "test"
            __genesis__ = "0x00000000"  # 0

        # 0 % 37 == 0, so technically valid
        result = prabhupada.verify_link(ZeroGenesis())
        assert result is True

    def test_verify_link_large_genesis(self):
        """Large valid genesis works."""
        class LargeGenesis:
            __mahajana__ = "test"
            __genesis__ = "0xffffffff"  # Very large

        # May or may not be divisible by 37
        result = prabhupada.verify_link(LargeGenesis())
        # Just check it doesn't crash
        assert isinstance(result, bool)
