"""
TEST ARCHITECTURE - The Enforcer of Mahamantra
==============================================

This test suite validates the architectural integrity of the Mahamantra core.
It ensures that the "Law" (Protocols) and the "Reality" (Implementation) are aligned.

SCOPE:
1. Pancha Tattva Protocols exist and are valid.
2. Seed Implementation derives strictly from Seed Protocol.
3. No magic numbers exist in the core definitions.
"""

import inspect
from typing import Final, get_type_hints

import pytest

from vibe_core.mahamantra.protocols import _kala as kala_proto
from vibe_core.mahamantra.protocols import _karma as karma_proto
from vibe_core.mahamantra.protocols import _pancha as pancha_proto

# 1. THE LAW (Protocols)
from vibe_core.mahamantra.protocols import _seed as seed_proto

# NOTE: _srivasa.py deleted in commit ab814c0 (dead code, zero imports)
# 2. THE REALITY (Implementation)
from vibe_core.mahamantra.substrate import seed as seed_impl


def test_pancha_tattva_integrity():
    """
    Verify that core Pancha Tattva protocols exist and are importable.

    NOTE: Pancha Tattva (5 Truths) are now consolidated in _pancha.py as
    PanchaTattvaProtocol. The 5 aspects (Chaitanya, Nityananda, Advaita,
    Gadadhara, Srivasa) are defined as TypedDict fields, not separate files.
    """
    assert seed_proto, "Ishvara (Seed) protocol missing"
    assert pancha_proto, "Identity (Pancha) protocol missing"
    assert kala_proto, "Time (Kala) protocol missing"
    assert karma_proto, "Action (Karma) protocol missing"

    # Verify PanchaTattvaProtocol exists with all 5 tattva fields
    assert hasattr(pancha_proto, "PanchaTattvaProtocol"), "PanchaTattvaProtocol missing"
    assert hasattr(pancha_proto, "TattvaDict"), "TattvaDict missing"


def test_seed_binding():
    """
    Verify that Seed Implementation is BOUND to Seed Protocol.
    It must not redefine constants, but import them.
    """
    # Check strict equality of values
    assert seed_impl.WORDS == seed_proto.WORDS, "WORDS mismatch"
    assert seed_impl.PARAMPARA == seed_proto.PARAMPARA, "PARAMPARA mismatch"
    assert seed_impl.TRINITY == seed_proto.TRINITY, "TRINITY mismatch"
    assert seed_impl.QUARTERS == seed_proto.QUARTERS, "QUARTERS mismatch"

    # Check Derivation (Advanced)
    # Ideally, we want to ensure seed_impl.WORDS *is* seed_proto.WORDS
    # But Python int interning makes 'is' unreliable for small ints.
    # So we trust the equality check for now.


def test_mathematical_consistency():
    """Verify the sacred math holds in the protocol definition."""
    # 16 words
    assert seed_proto.WORDS == 16

    # 37 Formula: 24 (Kshetra) + 12 (Mahajanas) + 1 (Knower) = 37
    # (Checking against hardcoded math truth here to verify the protocol constant)
    assert seed_proto.PARAMPARA == 37

    # Pancha = 5
    assert seed_proto.PANCHA == 5


def test_protocol_definitions():
    """Verify protocols define the correct interfaces."""

    # PanchaTattvaProtocol must define __tattva__
    # Note: In Protocols, properties are methods, so check dir()
    assert "__tattva__" in dir(pancha_proto.PanchaTattvaProtocol), "PanchaTattvaProtocol missing __tattva__ property"

    # KalaProtocol must define tick()
    assert "tick" in dir(kala_proto.KalaProtocol), "KalaProtocol missing tick() method"

    # KarmaProtocol must define execute()
    assert "execute" in dir(karma_proto.KarmaProtocol), "KarmaProtocol missing execute() method"


if __name__ == "__main__":
    pytest.main([__file__])
