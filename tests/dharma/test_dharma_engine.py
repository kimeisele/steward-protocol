"""
TEST SUITE: DHARMA ENGINE
=========================
"Proof of Life" for the Unified Mahamantra Architecture.

Verifies:
1. Protocol Compliance (Types)
2. Axiomatic Integrity (Values derived from Seed)
3. Component Functionality (Linguist, Layers, Matrix, Hologram)
4. Integration (Engine Facade)
"""

import pytest
from typing import List
from vibe_core.mahamantra.dharma.engine import dharma
from vibe_core.mahamantra.protocols.dharma_protocol import DharmaProtocol, SwarupaData, AksharaData, FractalNodeData
from vibe_core.mahamantra.protocols._seed import WORDS, TRINITY, LILA, SHARANAGATI, TEN, HALVES, KSHETRA, KSETRAJNA


def test_engine_singleton_compliance():
    """Verify the engine implements the Protocol."""
    # Runtime check (Python doesn't enforce Protocols at runtime easily without tools,
    # but we can check method existence)
    assert hasattr(dharma, "get_form")
    assert hasattr(dharma, "get_layer")
    assert hasattr(dharma, "analyze_field")
    assert hasattr(dharma, "expand_universe")


def test_linguist_axiomatic_integrity():
    """Verify Swarupa values match _seed.py axioms."""
    # Test KRISHNA
    krishna = dharma.get_form("KRISHNA")
    assert isinstance(krishna, SwarupaData)
    assert krishna.key == "KRISHNA"

    # Check Indices against Axioms:
    # K (16) = WORDS
    # r (6)  = SHARANAGATI
    # s (46) = LILA - HALVES
    # n (30) = KSHETRA + SHARANAGATI
    # a (0)
    indices = [a.index for a in krishna.aksharas]
    expected = [WORDS, SHARANAGATI, LILA - HALVES, KSHETRA + SHARANAGATI, 0]
    assert indices == expected, "KRISHNA indices must match Axioms"

    # Test Devanagari Rendering (Sandhi)
    # k + r + s + n + a -> kṛṣṇa -> कृषण
    # Note: Our simple Sandhi might render specific ligatures differently based on logic.
    # Current logic: k+r(vowel) -> kṛ (कृ)
    # s(consonant) -> ṣ (ष)
    # n(consonant) + a(vowel) -> ṇa (ण)
    # Result: कृषण
    assert "कृ" in krishna.deva
    assert "ण" in krishna.deva


def test_layers_dynamic_seeding():
    """Verify Layers compute seeds dynamically."""
    # Attractor 16 (Time)
    # Sequence: HARE(100), KRISHNA(98)...
    # 100 % 16 = 4.
    # Layer: [4, ...]
    layer_16 = dharma.get_layer(16)
    assert len(layer_16) == 16
    assert layer_16[0] == 4

    # Attractor 108 (Relations)
    layer_108 = dharma.get_layer(108)
    assert len(layer_108) == 16
    # Check for non-zero values (proving projection works)
    assert any(x > 0 for x in layer_108)


def test_matrix_interactions():
    """Verify Genesis Matrix Logic."""
    # Field Analysis
    field = dharma.analyze_field()
    assert len(field) == 4

    # Spark Interaction (Q3 + Q4)
    # Shiva Fusion (46) was observed in manual tests
    spark = dharma.get_spark(2, 3)
    assert isinstance(spark, int)
    assert 0 <= spark < 49


def test_hologram_recursion():
    """Verify Fractal Expansion."""
    root = dharma.expand_universe(depth=1)
    assert isinstance(root, FractalNodeData)
    assert root.value == "ADI-SEED"

    # Depth 1: Should have 16 Words
    assert len(root.children) == 16
    for child in root.children:
        assert child.value.startswith("WORD:")
        # Level Check
        assert child.level == 1

        # Check Word Children (Atoms) - Depth 2 check logic
        # Since we ran depth=1, atoms might be depth 2 (check implementation)
        # expand_node(root, 1) expands root -> words.
        # Inside loop: expand_node(word, 0) -> stops.
        # So Words should have children (Atoms)?
        # Let's check logic:
        # _expand_node(root, 1):
        #   create word (level 1)
        #   create atoms (level 2) attached to word
        #   recurse(atom, 0) -> stops.
        # So yes, Words should have Atoms!

        assert len(child.children) > 0
        assert child.children[0].value.startswith("ATOM:")
