"""
TEST RAMA ROUTER (The Conviction)
=================================

Verifies the integration of the Rama Grid Adapter.
Ensures:
1. Protocol Compliance (PhoneticRoutingProtocol)
2. Mathematical Correctness (Father Algorithm vs Router Addition)
3. Type Safety (SSOT / No Phoenix Classes)
"""
import pytest
from vibe_core.mahamantra.adapters.rama_router import get_phonetic_router, RamaPhoneticRouter
from vibe_core.mahamantra.protocols.routing import PhoneticRoutingProtocol
from vibe_core.protocols.substrate.resonance import PhoneticClass

def test_router_protocol_compliance():
    """Verify that the adapter implements the Protocol."""
    router = get_phonetic_router()
    assert isinstance(router, RamaPhoneticRouter)
    # Structural check
    assert hasattr(router, 'route_to_rama')
    assert hasattr(router, 'get_phoneme')
    assert hasattr(router, 'get_phonetic_class')

def test_true_algorithm_mapping():
    """
    Verify 'The True Algorithm' mappings.
    The logic: f(p) = 17(p-1) mod 49
    """
    router = get_phonetic_router()
    
    # 1. Vyasa (Genesis) -> Rama 0 ('a')
    # f(1) = 17(0) = 0
    assert router.route_to_rama(1) == 0
    assert router.get_phoneme(0) == "a"
    assert router.get_phonetic_class(0) == PhoneticClass.VOWEL_A
    
    # 2. Brahma (Load Root) -> Rama 17 ('kha')
    # f(2) = 17(1) = 17
    # 17 - 16 (Words) = 1. Grid index 1.
    # Row 0 (Ka-varga), Col 1 (2nd char) = "kha"
    assert router.route_to_rama(2) == 17
    assert router.get_phoneme(17) == "kha"
    assert router.get_phonetic_class(17) == PhoneticClass.GUTTURAL

    # 12. Bhishma (Commit) -> Rama 40 ('ma') - The Seal
    assert router.route_to_rama(12) == 40
    assert router.get_phoneme(40) == "ma"
    assert router.get_phonetic_class(40) == PhoneticClass.LABIAL

def test_ssot_types():
    """
    Verify we are using the Single Source of Truth for types.
    NO Phoenix Classes (re-defined enums).
    """
    router = get_phonetic_router()
    p_class = router.get_phonetic_class(0)
    
    # Must be the exact Enum from resonance.py
    assert p_class is PhoneticClass.VOWEL_A
    assert isinstance(p_class, PhoneticClass)

def test_boundary_conditions():
    """Verify edges of the grid."""
    router = get_phonetic_router()
    
    # Postion 16 (Yamaraja) -> Rama 10 ('e')
    # f(16) = 17(15) = 255
    # 255 % 49 = 10.
    # Index 10 in SVARAS is "e" (Position 11 in 1-based list)
    assert router.route_to_rama(16) == 10
    assert router.get_phoneme(10) == "e"
    assert router.get_phonetic_class(10) == PhoneticClass.VOWEL_E
