"""
TEST PRABHUPADA'S MERCY - Layer -1 (Substrate/Mantra)
=====================================================
Verifies:
1. GenesisByte Lineage Check (Modulo 37).
2. Prabhupada's Mercy Mechanism (Error Interception).
3. SilentWitness Behavior (Non-crashing Null Object).

NOTE: There is no abstract "Guru" - Prabhupada IS the Guru.
"""

import pytest
from vibe_core.protocols.substrate.byte import GenesisByte, MantraByte
from vibe_core.protocols.substrate.mantra.prabhupada import PRABHUPADA, SilentWitness


def test_parampara_lineage_check():
    """Verify that only 37-divisible hashes are accepted."""
    # Valid (37 * 1 = 37 = 0x25)
    valid_byte = GenesisByte(signature="sovereign:test", resonance=MantraByte.standard_16(), parampara_hash="0x25")
    assert valid_byte._verify_lineage() is True
    assert valid_byte.is_valid is True

    # Invalid (38 = 0x26)
    invalid_byte = GenesisByte(signature="sovereign:test", resonance=MantraByte.standard_16(), parampara_hash="0x26")
    assert invalid_byte._verify_lineage() is False
    assert invalid_byte.is_valid is False


def test_prabhupada_mercy_on_import_error():
    """Verify Prabhupada catches ImportErrors and returns SilentWitness."""
    try:
        raise ImportError("Module 'maya' not found")
    except Exception as e:
        result = PRABHUPADA.bestow_mercy("test_context", e)

    # Assert result is SilentWitness
    assert isinstance(result, SilentWitness)
    # Check properties
    assert not result  # Truthy Check (Must be False)
    assert result.some_method() is result  # Chaining
    assert result.any_attribute is result


def test_prabhupada_fatal_error_pass_through():
    """Verify Prabhupada does NOT catch fatal errors."""
    with pytest.raises(SyntaxError):
        try:
            raise SyntaxError("Bad Code")
        except Exception as e:
            PRABHUPADA.bestow_mercy("fatal_context", e)


def test_silent_witness_non_existence():
    """Verify SilentWitness behaves like Prabhupada's silent mercy."""
    witness = SilentWitness()

    if witness:
        pytest.fail("SilentWitness asserted as True (Satya violation)")

    # Safe operations check
    assert witness.call().chain().action() is witness


def test_prabhupada_consult_books():
    """Verify Prabhupada gives Vani instructions for issues."""
    from vibe_core.protocols.substrate.mantra.prabhupada import PrabhupadaVani

    # Timeout -> BG 2.47
    instruction = PRABHUPADA.consult_book_bhagavat("request timeout")
    assert instruction == PrabhupadaVani.BG_2_47

    # Access denied -> BG 4.34
    instruction = PRABHUPADA.consult_book_bhagavat("access_denied error")
    assert instruction == PrabhupadaVani.BG_4_34

    # System crash -> BG 18.66
    instruction = PRABHUPADA.consult_book_bhagavat("system_crash occurred")
    assert instruction == PrabhupadaVani.BG_18_66


def test_prabhupada_is_connected():
    """Prabhupada IS the parampara connection."""
    assert PRABHUPADA.is_connected is True
    assert PRABHUPADA.parampara_link == 37
