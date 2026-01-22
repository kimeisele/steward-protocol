"""
TESTS: kernel/fractal.py - Fractal Infinite Scalability
========================================================

REAL TESTS for:
1. FRACTAL_BASE, KSETRA_COUNT, MAHAJANA_COUNT, KSETRAJNA_COUNT constants
2. FractalNode dataclass
3. FractalTree class
4. scale_up function
5. scale_down function
6. verify_fractal_integrity function
"""

import pytest
from vibe_core.mahamantra.kernel.fractal import (
    FRACTAL_BASE,
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    KSETRAJNA_COUNT,
    FractalNode,
    FractalTree,
    scale_up,
    scale_down,
    verify_fractal_integrity,
)
from vibe_core.mahamantra.substrate.fractal import FractalLevel
from vibe_core.mahamantra.substrate.acintya import PARAMPARA


# =============================================================================
# Constants Tests
# =============================================================================


class TestFractalConstants:
    """Test fractal constants."""

    def test_fractal_base_is_37(self):
        """FRACTAL_BASE is 37."""
        assert FRACTAL_BASE == 37

    def test_fractal_base_equals_parampara(self):
        """FRACTAL_BASE equals PARAMPARA."""
        assert FRACTAL_BASE == PARAMPARA

    def test_ksetra_count_is_24(self):
        """KSETRA_COUNT is 24."""
        assert KSETRA_COUNT == 24

    def test_mahajana_count_is_12(self):
        """MAHAJANA_COUNT is 12."""
        assert MAHAJANA_COUNT == 12

    def test_ksetrajna_count_is_1(self):
        """KSETRAJNA_COUNT is 1."""
        assert KSETRAJNA_COUNT == 1

    def test_formula_sum_is_37(self):
        """24 + 12 + 1 = 37."""
        assert KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT == 37

    def test_formula_sum_equals_fractal_base(self):
        """Sum equals FRACTAL_BASE."""
        assert KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT == FRACTAL_BASE


# =============================================================================
# FractalNode Tests
# =============================================================================


class TestFractalNode:
    """Test FractalNode dataclass."""

    def test_fractal_node_creation(self):
        """FractalNode can be created."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=("brahma",),
        )
        assert node is not None
        assert node.ksetrajna == "test"

    def test_fractal_node_ksetrajna(self):
        """FractalNode has ksetrajna (the 1)."""
        node = FractalNode(
            ksetrajna="knower",
            ksetra=[],
            mahajanas=(),
        )
        assert node.ksetrajna == "knower"

    def test_fractal_node_ksetra(self):
        """FractalNode has ksetra (the 24)."""
        data = ["a", "b", "c"]
        node = FractalNode(
            ksetrajna="test",
            ksetra=data,
            mahajanas=(),
        )
        assert node.ksetra == data

    def test_fractal_node_mahajanas(self):
        """FractalNode has mahajanas (the 12)."""
        guardians = ("brahma", "narada", "shambhu")
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=guardians,
        )
        assert node.mahajanas == guardians

    def test_fractal_node_default_level(self):
        """FractalNode defaults to PADA level."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
        )
        assert node.level == FractalLevel.PADA

    def test_fractal_node_custom_level(self):
        """FractalNode accepts custom level."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            level=FractalLevel.VAKYA,
        )
        assert node.level == FractalLevel.VAKYA

    def test_fractal_node_default_parampara_vector(self):
        """FractalNode defaults to parampara_vector 0."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
        )
        assert node.parampara_vector == 0

    def test_fractal_node_custom_parampara_vector(self):
        """FractalNode accepts custom parampara_vector."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            parampara_vector=444,
        )
        assert node.parampara_vector == 444

    def test_fractal_node_is_connected_false(self):
        """is_connected returns False for non-multiple of 37."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            parampara_vector=10,
        )
        assert node.is_connected is False

    def test_fractal_node_is_connected_true(self):
        """is_connected returns True for multiple of 37."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            parampara_vector=37,
        )
        assert node.is_connected is True

    def test_fractal_node_is_connected_zero(self):
        """is_connected returns True for 0 (0 % 37 == 0)."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            parampara_vector=0,
        )
        assert node.is_connected is True

    def test_fractal_node_is_connected_444(self):
        """is_connected returns True for 444."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            parampara_vector=444,
        )
        assert node.is_connected is True

    def test_fractal_node_formula_sum(self):
        """formula_sum calculates correctly."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b", "c"],  # 3
            mahajanas=("brahma", "narada"),  # 2
        )
        # 3 + 2 + 1 = 6
        assert node.formula_sum == 6

    def test_fractal_node_formula_sum_37(self):
        """formula_sum is 37 with correct counts."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=list(range(24)),  # 24 elements
            mahajanas=tuple(f"m{i}" for i in range(12)),  # 12 mahajanas
        )
        # 24 + 12 + 1 = 37
        assert node.formula_sum == 37

    def test_fractal_node_depth_no_children(self):
        """depth returns 0 for node with no children."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b", "c"],
            mahajanas=(),
        )
        assert node.depth == 0

    def test_fractal_node_depth_with_children(self):
        """depth returns correct depth for nested nodes."""
        child = FractalNode(
            ksetrajna="child",
            ksetra=[],
            mahajanas=(),
        )
        parent = FractalNode(
            ksetrajna="parent",
            ksetra=[child],
            mahajanas=(),
        )
        assert parent.depth == 1

    def test_fractal_node_depth_deep_nesting(self):
        """depth returns correct depth for deeply nested nodes."""
        grandchild = FractalNode(
            ksetrajna="grandchild",
            ksetra=[],
            mahajanas=(),
        )
        child = FractalNode(
            ksetrajna="child",
            ksetra=[grandchild],
            mahajanas=(),
        )
        parent = FractalNode(
            ksetrajna="parent",
            ksetra=[child],
            mahajanas=(),
        )
        assert parent.depth == 2

    def test_fractal_node_iterate_level(self):
        """iterate_level finds nodes at target level."""
        child = FractalNode(
            ksetrajna="child",
            ksetra=[],
            mahajanas=(),
            level=FractalLevel.PADA,
        )
        parent = FractalNode(
            ksetrajna="parent",
            ksetra=[child],
            mahajanas=(),
            level=FractalLevel.VAKYA,
        )

        pada_nodes = list(parent.iterate_level(FractalLevel.PADA))
        assert len(pada_nodes) == 1
        assert pada_nodes[0].ksetrajna == "child"

    def test_fractal_node_iterate_level_multiple(self):
        """iterate_level finds multiple nodes at target level."""
        child1 = FractalNode(
            ksetrajna="child1",
            ksetra=[],
            mahajanas=(),
            level=FractalLevel.PADA,
        )
        child2 = FractalNode(
            ksetrajna="child2",
            ksetra=[],
            mahajanas=(),
            level=FractalLevel.PADA,
        )
        parent = FractalNode(
            ksetrajna="parent",
            ksetra=[child1, child2],
            mahajanas=(),
            level=FractalLevel.VAKYA,
        )

        pada_nodes = list(parent.iterate_level(FractalLevel.PADA))
        assert len(pada_nodes) == 2

    def test_fractal_node_zoom_in_empty_path(self):
        """zoom_in with empty path returns self."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
        )
        result = node.zoom_in([])
        assert result is node

    def test_fractal_node_zoom_in_valid_path(self):
        """zoom_in with valid path returns correct node."""
        child = FractalNode(
            ksetrajna="child",
            ksetra=[],
            mahajanas=(),
        )
        parent = FractalNode(
            ksetrajna="parent",
            ksetra=[child],
            mahajanas=(),
        )

        result = parent.zoom_in([0])
        assert result is child

    def test_fractal_node_zoom_in_invalid_path(self):
        """zoom_in with invalid path returns None."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b"],
            mahajanas=(),
        )
        result = node.zoom_in([10])
        assert result is None

    def test_fractal_node_zoom_in_leaf(self):
        """zoom_in to leaf creates virtual node."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["leaf_value"],
            mahajanas=("brahma",),
        )
        result = node.zoom_in([0])
        assert result is not None
        assert result.ksetrajna == "leaf_value"


# =============================================================================
# FractalTree Tests
# =============================================================================


class TestFractalTree:
    """Test FractalTree class."""

    def test_fractal_tree_creation(self):
        """FractalTree can be created."""
        root = FractalNode(
            ksetrajna="root",
            ksetra=[],
            mahajanas=(),
        )
        tree = FractalTree(root=root)
        assert tree is not None
        assert tree.root is root

    def test_fractal_tree_create_standard(self):
        """FractalTree.create_standard creates standard tree."""
        tree = FractalTree.create_standard()
        assert tree is not None
        assert tree.root.ksetrajna == "mahamantra"

    def test_fractal_tree_standard_has_quarters(self):
        """Standard tree has 4 quarters."""
        tree = FractalTree.create_standard()
        assert len(tree.root.ksetra) == 4

    def test_fractal_tree_standard_quarter_names(self):
        """Standard tree quarters have correct names."""
        tree = FractalTree.create_standard()
        quarter_names = [q.ksetrajna for q in tree.root.ksetra]
        assert quarter_names == ["genesis", "dharma", "karma", "moksha"]

    def test_fractal_tree_standard_words_per_quarter(self):
        """Standard tree has 4 words per quarter."""
        tree = FractalTree.create_standard()
        for quarter in tree.root.ksetra:
            assert len(quarter.ksetra) == 4

    def test_fractal_tree_standard_total_words(self):
        """Standard tree has 16 total words."""
        tree = FractalTree.create_standard()
        total_words = sum(len(q.ksetra) for q in tree.root.ksetra)
        assert total_words == 16

    def test_fractal_tree_standard_is_connected(self):
        """Standard tree is connected to Parampara."""
        tree = FractalTree.create_standard()
        assert tree.is_connected is True

    def test_fractal_tree_iterate(self):
        """FractalTree.iterate works correctly."""
        tree = FractalTree.create_standard()
        vakya_nodes = list(tree.iterate(FractalLevel.VAKYA))
        # Root + 4 quarters = 5 VAKYA level nodes
        assert len(vakya_nodes) == 5

    def test_fractal_tree_iterate_pada(self):
        """FractalTree.iterate finds PADA nodes."""
        tree = FractalTree.create_standard()
        pada_nodes = list(tree.iterate(FractalLevel.PADA))
        # 16 words at PADA level
        assert len(pada_nodes) == 16

    def test_fractal_tree_zoom(self):
        """FractalTree.zoom works correctly."""
        tree = FractalTree.create_standard()
        # Zoom into first quarter
        quarter = tree.zoom([0])
        assert quarter is not None
        assert quarter.ksetrajna == "genesis"

    def test_fractal_tree_zoom_deep(self):
        """FractalTree.zoom works for deep paths."""
        tree = FractalTree.create_standard()
        # Zoom into first quarter, first word
        word = tree.zoom([0, 0])
        assert word is not None
        assert word.ksetrajna == "hare"

    def test_fractal_tree_depth(self):
        """FractalTree.depth returns correct depth."""
        tree = FractalTree.create_standard()
        # Root -> Quarters -> Words = depth 2
        assert tree.depth == 2

    def test_fractal_tree_custom_root(self):
        """FractalTree works with custom root."""
        root = FractalNode(
            ksetrajna="custom",
            ksetra=["a", "b", "c"],
            mahajanas=("brahma",),
            parampara_vector=37,
        )
        tree = FractalTree(root=root)
        assert tree.root.ksetrajna == "custom"
        assert tree.is_connected is True


# =============================================================================
# scale_up Tests
# =============================================================================


class TestScaleUp:
    """Test scale_up function."""

    def test_scale_up_multiplies_ksetra(self):
        """scale_up multiplies ksetra by factor."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b"],
            mahajanas=(),
        )
        scaled = scale_up(node, factor=3)
        assert len(scaled.ksetra) == 6
        assert scaled.ksetra == ["a", "b", "a", "b", "a", "b"]

    def test_scale_up_preserves_ksetrajna(self):
        """scale_up preserves ksetrajna."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a"],
            mahajanas=(),
        )
        scaled = scale_up(node, factor=2)
        assert scaled.ksetrajna == "test"

    def test_scale_up_preserves_mahajanas(self):
        """scale_up preserves mahajanas."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a"],
            mahajanas=("brahma", "narada"),
        )
        scaled = scale_up(node, factor=2)
        assert scaled.mahajanas == ("brahma", "narada")

    def test_scale_up_multiplies_parampara_vector(self):
        """scale_up multiplies parampara_vector."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a"],
            mahajanas=(),
            parampara_vector=37,
        )
        scaled = scale_up(node, factor=2)
        assert scaled.parampara_vector == 74

    def test_scale_up_default_factor(self):
        """scale_up uses factor 37 by default."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a"],
            mahajanas=(),
            parampara_vector=1,
        )
        scaled = scale_up(node)
        assert len(scaled.ksetra) == 37
        assert scaled.parampara_vector == 37

    def test_scale_up_changes_level(self):
        """scale_up decreases level (zooms out)."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a"],
            mahajanas=(),
            level=FractalLevel.PADA,
        )
        scaled = scale_up(node, factor=2)
        # Level should decrease (go up in hierarchy)
        assert scaled.level.value < node.level.value or scaled.level == FractalLevel.VARNA


# =============================================================================
# scale_down Tests
# =============================================================================


class TestScaleDown:
    """Test scale_down function."""

    def test_scale_down_reduces_ksetra(self):
        """scale_down reduces ksetra by factor."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b", "c", "d", "e", "f"],
            mahajanas=(),
        )
        scaled = scale_down(node, factor=2)
        assert scaled.ksetra == ["a", "c", "e"]

    def test_scale_down_preserves_ksetrajna(self):
        """scale_down preserves ksetrajna."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b", "c", "d"],
            mahajanas=(),
        )
        scaled = scale_down(node, factor=2)
        assert scaled.ksetrajna == "test"

    def test_scale_down_preserves_mahajanas(self):
        """scale_down preserves mahajanas."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b", "c", "d"],
            mahajanas=("brahma", "narada"),
        )
        scaled = scale_down(node, factor=2)
        assert scaled.mahajanas == ("brahma", "narada")

    def test_scale_down_divides_parampara_vector(self):
        """scale_down divides parampara_vector."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b", "c", "d"],
            mahajanas=(),
            parampara_vector=74,
        )
        scaled = scale_down(node, factor=2)
        assert scaled.parampara_vector == 37

    def test_scale_down_default_factor(self):
        """scale_down uses factor 37 by default."""
        # Create node with 37 elements
        node = FractalNode(
            ksetrajna="test",
            ksetra=list(range(37)),
            mahajanas=(),
            parampara_vector=74,
        )
        scaled = scale_down(node)
        # Takes every 37th element: [0]
        assert len(scaled.ksetra) == 1
        assert scaled.parampara_vector == 2

    def test_scale_down_changes_level(self):
        """scale_down increases level (zooms in)."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=list(range(4)),
            mahajanas=(),
            level=FractalLevel.VAKYA,
        )
        scaled = scale_down(node, factor=2)
        # Level should increase (go down in hierarchy)
        assert scaled.level.value > node.level.value or scaled.level == FractalLevel.SADHANA


# =============================================================================
# verify_fractal_integrity Tests
# =============================================================================


class TestVerifyFractalIntegrity:
    """Test verify_fractal_integrity function."""

    def test_verify_integrity_connected_tree(self):
        """verify_fractal_integrity returns True for connected tree."""
        tree = FractalTree.create_standard()
        assert verify_fractal_integrity(tree) is True

    def test_verify_integrity_disconnected_root(self):
        """verify_fractal_integrity returns False for disconnected root."""
        root = FractalNode(
            ksetrajna="test",
            ksetra=[],
            mahajanas=(),
            parampara_vector=10,  # Not multiple of 37
        )
        tree = FractalTree(root=root)
        assert verify_fractal_integrity(tree) is False

    def test_verify_integrity_disconnected_child(self):
        """verify_fractal_integrity returns False for disconnected child."""
        child = FractalNode(
            ksetrajna="child",
            ksetra=[],
            mahajanas=(),
            parampara_vector=10,  # Disconnected
        )
        root = FractalNode(
            ksetrajna="root",
            ksetra=[child],
            mahajanas=(),
            parampara_vector=37,  # Connected
        )
        tree = FractalTree(root=root)
        assert verify_fractal_integrity(tree) is False

    def test_verify_integrity_all_connected(self):
        """verify_fractal_integrity returns True when all nodes connected."""
        child = FractalNode(
            ksetrajna="child",
            ksetra=[],
            mahajanas=(),
            parampara_vector=37,
        )
        root = FractalNode(
            ksetrajna="root",
            ksetra=[child],
            mahajanas=(),
            parampara_vector=74,
        )
        tree = FractalTree(root=root)
        assert verify_fractal_integrity(tree) is True

    def test_verify_integrity_deeply_nested(self):
        """verify_fractal_integrity checks deeply nested nodes."""
        grandchild = FractalNode(
            ksetrajna="grandchild",
            ksetra=[],
            mahajanas=(),
            parampara_vector=37,
        )
        child = FractalNode(
            ksetrajna="child",
            ksetra=[grandchild],
            mahajanas=(),
            parampara_vector=37,
        )
        root = FractalNode(
            ksetrajna="root",
            ksetra=[child],
            mahajanas=(),
            parampara_vector=37,
        )
        tree = FractalTree(root=root)
        assert verify_fractal_integrity(tree) is True

    def test_verify_integrity_mixed_content(self):
        """verify_fractal_integrity handles mixed ksetra content."""
        child = FractalNode(
            ksetrajna="child",
            ksetra=[],
            mahajanas=(),
            parampara_vector=37,
        )
        root = FractalNode(
            ksetrajna="root",
            ksetra=[child, "leaf_value", 123],  # Mixed content
            mahajanas=(),
            parampara_vector=37,
        )
        tree = FractalTree(root=root)
        assert verify_fractal_integrity(tree) is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestFractalIntegration:
    """Integration tests for fractal operations."""

    def test_scale_up_and_down_inverse(self):
        """scale_up and scale_down affect parampara_vector inversely."""
        node = FractalNode(
            ksetrajna="test",
            ksetra=["a", "b"],
            mahajanas=(),
            parampara_vector=37,
        )

        # Scale up then down
        scaled_up = scale_up(node, factor=2)
        scaled_back = scale_down(scaled_up, factor=2)

        # Parampara vector should match (37 * 2 // 2 = 37)
        assert scaled_back.parampara_vector == node.parampara_vector
        # Ksetrajna should be preserved
        assert scaled_back.ksetrajna == node.ksetrajna
        # Mahajanas should be preserved
        assert scaled_back.mahajanas == node.mahajanas

    def test_standard_tree_maintains_37_formula(self):
        """Standard tree maintains 37 formula."""
        tree = FractalTree.create_standard()

        # Root has 12 mahajanas
        assert len(tree.root.mahajanas) == 12

        # Each quarter has subset of mahajanas
        for quarter in tree.root.ksetra:
            assert len(quarter.mahajanas) == 3

    def test_zoom_and_iterate_consistency(self):
        """zoom and iterate give consistent results."""
        tree = FractalTree.create_standard()

        # Get first PADA node via iterate
        pada_nodes = list(tree.iterate(FractalLevel.PADA))
        first_pada = pada_nodes[0]

        # Get first PADA node via zoom
        zoomed = tree.zoom([0, 0])

        # Should be the same
        assert first_pada.ksetrajna == zoomed.ksetrajna


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.kernel import fractal

        expected = [
            "FRACTAL_BASE",
            "KSETRA_COUNT",
            "MAHAJANA_COUNT",
            "KSETRAJNA_COUNT",
            "FractalNode",
            "FractalTree",
            "scale_up",
            "scale_down",
            "verify_fractal_integrity",
        ]
        for item in expected:
            assert item in fractal.__all__, f"{item} should be in __all__"
