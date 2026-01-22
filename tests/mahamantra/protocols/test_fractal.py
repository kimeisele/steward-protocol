"""
TESTS: _fractal.py - The Fractal Protocol
==========================================

REAL TESTS for:
1. FractalAddress dataclass
2. FractalNode dataclass
3. FractalTree dataclass
4. GrowthPattern enum
5. GrowthRule dataclass
6. FractalProtocol
"""

import pytest
from vibe_core.mahamantra.protocols._fractal import (
    # Core types
    FractalAddress,
    FractalNode,
    FractalTree,
    # Growth
    GrowthPattern,
    GrowthRule,
    # Protocol
    FractalProtocol,
)
from vibe_core.mahamantra.protocols._core import Quarter


# =============================================================================
# FractalAddress Tests
# =============================================================================


class TestFractalAddress:
    """Test FractalAddress dataclass."""

    def test_fractal_address_creation(self):
        """FractalAddress can be created."""
        addr = FractalAddress(path=(0,))
        assert addr.path == (0,)

    def test_fractal_address_empty_raises(self):
        """Empty path raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            FractalAddress(path=())

    def test_fractal_address_invalid_component_raises(self):
        """Invalid component (>=16) raises ValueError."""
        with pytest.raises(ValueError, match="must be 0-15"):
            FractalAddress(path=(16,))

    def test_fractal_address_negative_component_raises(self):
        """Negative component raises ValueError."""
        with pytest.raises(ValueError, match="must be 0-15"):
            FractalAddress(path=(-1,))

    def test_fractal_address_depth(self):
        """depth returns correct length."""
        addr1 = FractalAddress(path=(0,))
        addr2 = FractalAddress(path=(0, 1, 2))
        assert addr1.depth == 1
        assert addr2.depth == 3

    def test_fractal_address_position(self):
        """position returns first component."""
        addr = FractalAddress(path=(5, 3, 2))
        assert addr.position == 5

    def test_fractal_address_quarter(self):
        """quarter derived from position."""
        addr_genesis = FractalAddress(path=(0,))
        addr_dharma = FractalAddress(path=(4,))
        addr_karma = FractalAddress(path=(8,))
        addr_moksha = FractalAddress(path=(12,))
        assert addr_genesis.quarter == Quarter.GENESIS
        assert addr_dharma.quarter == Quarter.DHARMA
        assert addr_karma.quarter == Quarter.KARMA
        assert addr_moksha.quarter == Quarter.MOKSHA

    def test_fractal_address_parent_address(self):
        """parent_address returns parent or None."""
        addr = FractalAddress(path=(0, 1, 2))
        parent = addr.parent_address
        assert parent is not None
        assert parent.path == (0, 1)

    def test_fractal_address_parent_address_root(self):
        """Root address has no parent."""
        addr = FractalAddress(path=(0,))
        assert addr.parent_address is None

    def test_fractal_address_child_address(self):
        """child_address creates child."""
        addr = FractalAddress(path=(0,))
        child = addr.child_address(5)
        assert child.path == (0, 5)

    def test_fractal_address_child_address_invalid_raises(self):
        """Invalid sub-position raises."""
        addr = FractalAddress(path=(0,))
        with pytest.raises(ValueError):
            addr.child_address(16)

    def test_fractal_address_is_ancestor_of(self):
        """is_ancestor_of checks ancestry."""
        parent = FractalAddress(path=(0, 1))
        child = FractalAddress(path=(0, 1, 2))
        assert parent.is_ancestor_of(child) is True
        assert child.is_ancestor_of(parent) is False

    def test_fractal_address_is_descendant_of(self):
        """is_descendant_of checks descendancy."""
        parent = FractalAddress(path=(0, 1))
        child = FractalAddress(path=(0, 1, 2))
        assert child.is_descendant_of(parent) is True
        assert parent.is_descendant_of(child) is False

    def test_fractal_address_common_ancestor(self):
        """common_ancestor finds shared ancestor."""
        addr1 = FractalAddress(path=(0, 1, 2))
        addr2 = FractalAddress(path=(0, 1, 3))
        common = addr1.common_ancestor(addr2)
        assert common is not None
        assert common.path == (0, 1)

    def test_fractal_address_common_ancestor_none(self):
        """common_ancestor returns None if no common ancestor."""
        addr1 = FractalAddress(path=(0, 1))
        addr2 = FractalAddress(path=(1, 2))
        common = addr1.common_ancestor(addr2)
        assert common is None

    def test_fractal_address_to_string(self):
        """to_string creates string representation."""
        addr = FractalAddress(path=(0, 1, 2))
        assert addr.to_string() == "0.1.2"

    def test_fractal_address_from_string(self):
        """from_string parses string."""
        addr = FractalAddress.from_string("0.1.2")
        assert addr.path == (0, 1, 2)

    def test_fractal_address_root(self):
        """root creates root address."""
        addr = FractalAddress.root(5)
        assert addr.path == (5,)

    def test_fractal_address_is_frozen(self):
        """FractalAddress is frozen."""
        addr = FractalAddress(path=(0,))
        with pytest.raises(Exception):
            addr.path = (1,)


# =============================================================================
# FractalNode Tests
# =============================================================================


class TestFractalNode:
    """Test FractalNode dataclass."""

    def test_fractal_node_creation(self):
        """FractalNode can be created."""
        addr = FractalAddress(path=(0,))
        node = FractalNode(address=addr, payload="test")
        assert node.payload == "test"

    def test_fractal_node_add_child(self):
        """add_child creates child node."""
        addr = FractalAddress(path=(0,))
        node = FractalNode(address=addr, payload="parent")
        child = node.add_child(1, "child")
        assert child.payload == "child"
        assert child.address.path == (0, 1)
        assert child.parent is node

    def test_fractal_node_add_child_duplicate_raises(self):
        """Adding child at existing position raises."""
        addr = FractalAddress(path=(0,))
        node = FractalNode(address=addr, payload="parent")
        node.add_child(1, "child1")
        with pytest.raises(ValueError, match="already exists"):
            node.add_child(1, "child2")

    def test_fractal_node_get_child(self):
        """get_child returns child or None."""
        addr = FractalAddress(path=(0,))
        node = FractalNode(address=addr, payload="parent")
        node.add_child(1, "child")
        assert node.get_child(1) is not None
        assert node.get_child(2) is None

    def test_fractal_node_get_descendant(self):
        """get_descendant traverses path."""
        addr = FractalAddress(path=(0,))
        root = FractalNode(address=addr, payload="root")
        child = root.add_child(1, "child")
        grandchild = child.add_child(2, "grandchild")

        found = root.get_descendant((1, 2))
        assert found is grandchild

    def test_fractal_node_all_descendants(self):
        """all_descendants iterates depth-first."""
        addr = FractalAddress(path=(0,))
        root = FractalNode(address=addr, payload="root")
        root.add_child(1, "child1")
        root.add_child(2, "child2")

        descendants = list(root.all_descendants())
        assert len(descendants) == 2

    def test_fractal_node_all_ancestors(self):
        """all_ancestors iterates bottom-up."""
        addr = FractalAddress(path=(0,))
        root = FractalNode(address=addr, payload="root")
        child = root.add_child(1, "child")
        grandchild = child.add_child(2, "grandchild")

        ancestors = list(grandchild.all_ancestors())
        assert len(ancestors) == 2
        assert ancestors[0] is child
        assert ancestors[1] is root

    def test_fractal_node_depth(self):
        """depth returns address depth."""
        addr = FractalAddress(path=(0, 1, 2))
        node = FractalNode(address=addr, payload="test")
        assert node.depth == 3

    def test_fractal_node_is_leaf(self):
        """is_leaf returns True if no children."""
        addr = FractalAddress(path=(0,))
        node = FractalNode(address=addr, payload="test")
        assert node.is_leaf is True
        node.add_child(1, "child")
        assert node.is_leaf is False

    def test_fractal_node_is_root(self):
        """is_root returns True if no parent."""
        addr = FractalAddress(path=(0,))
        root = FractalNode(address=addr, payload="root")
        assert root.is_root is True
        child = root.add_child(1, "child")
        assert child.is_root is False

    def test_fractal_node_count_descendants(self):
        """count_descendants counts all descendants."""
        addr = FractalAddress(path=(0,))
        root = FractalNode(address=addr, payload="root")
        child = root.add_child(1, "child")
        child.add_child(2, "grandchild")
        assert root.count_descendants() == 2


# =============================================================================
# FractalTree Tests
# =============================================================================


class TestFractalTree:
    """Test FractalTree dataclass."""

    def test_fractal_tree_creation(self):
        """FractalTree can be created."""
        tree = FractalTree()
        assert tree is not None

    def test_fractal_tree_add_root(self):
        """add_root adds a root node."""
        tree = FractalTree()
        node = tree.add_root(0, "payload0")
        assert node.payload == "payload0"
        assert node.address.path == (0,)

    def test_fractal_tree_add_root_duplicate_raises(self):
        """Adding duplicate root raises."""
        tree = FractalTree()
        tree.add_root(0, "first")
        with pytest.raises(ValueError, match="already exists"):
            tree.add_root(0, "second")

    def test_fractal_tree_get_root(self):
        """get_root returns root or None."""
        tree = FractalTree()
        tree.add_root(0, "payload")
        assert tree.get_root(0) is not None
        assert tree.get_root(1) is None

    def test_fractal_tree_get_node(self):
        """get_node finds node by address."""
        tree = FractalTree()
        root = tree.add_root(0, "root")
        child = root.add_child(1, "child")

        addr = FractalAddress(path=(0, 1))
        found = tree.get_node(addr)
        assert found is child

    def test_fractal_tree_add_node(self):
        """add_node adds at address."""
        tree = FractalTree()
        tree.add_root(0, "root")

        addr = FractalAddress(path=(0, 1))
        node = tree.add_node(addr, "child")
        assert node.payload == "child"

    def test_fractal_tree_add_node_root(self):
        """add_node can add root."""
        tree = FractalTree()
        addr = FractalAddress(path=(5,))
        node = tree.add_node(addr, "root5")
        assert node.payload == "root5"

    def test_fractal_tree_add_node_no_parent_raises(self):
        """add_node without parent raises."""
        tree = FractalTree()
        addr = FractalAddress(path=(0, 1, 2))  # No root 0
        with pytest.raises(ValueError, match="does not exist"):
            tree.add_node(addr, "orphan")

    def test_fractal_tree_all_nodes(self):
        """all_nodes iterates all nodes."""
        tree = FractalTree()
        tree.add_root(0, "root0")
        tree.add_root(1, "root1")
        root0 = tree.get_root(0)
        root0.add_child(2, "child")

        nodes = list(tree.all_nodes())
        assert len(nodes) == 3

    def test_fractal_tree_count_nodes(self):
        """count_nodes counts all nodes."""
        tree = FractalTree()
        tree.add_root(0, "root0")
        tree.add_root(1, "root1")
        root0 = tree.get_root(0)
        root0.add_child(2, "child")

        assert tree.count_nodes() == 3


# =============================================================================
# GrowthPattern Enum Tests
# =============================================================================


class TestGrowthPattern:
    """Test GrowthPattern enum."""

    def test_growth_pattern_full(self):
        """GrowthPattern has FULL."""
        assert GrowthPattern.FULL.value == "full"

    def test_growth_pattern_sparse(self):
        """GrowthPattern has SPARSE."""
        assert GrowthPattern.SPARSE.value == "sparse"

    def test_growth_pattern_balanced(self):
        """GrowthPattern has BALANCED."""
        assert GrowthPattern.BALANCED.value == "balanced"

    def test_growth_pattern_lazy(self):
        """GrowthPattern has LAZY."""
        assert GrowthPattern.LAZY.value == "lazy"


# =============================================================================
# GrowthRule Tests
# =============================================================================


class TestGrowthRule:
    """Test GrowthRule dataclass."""

    def test_growth_rule_creation(self):
        """GrowthRule can be created."""
        rule = GrowthRule(pattern=GrowthPattern.FULL)
        assert rule.pattern == GrowthPattern.FULL

    def test_growth_rule_max_depth_default(self):
        """Default max_depth is 16."""
        rule = GrowthRule(pattern=GrowthPattern.FULL)
        assert rule.max_depth == 16

    def test_growth_rule_should_grow_under_max(self):
        """should_grow returns True under max_depth."""
        rule = GrowthRule(pattern=GrowthPattern.FULL, max_depth=3)
        addr = FractalAddress(path=(0, 1))  # depth 2
        assert rule.should_grow(addr) is True

    def test_growth_rule_should_grow_at_max(self):
        """should_grow returns False at max_depth."""
        rule = GrowthRule(pattern=GrowthPattern.FULL, max_depth=2)
        addr = FractalAddress(path=(0, 1))  # depth 2
        assert rule.should_grow(addr) is False

    def test_growth_rule_custom_can_grow(self):
        """Custom can_grow function."""
        def only_even(addr):
            return addr.position % 2 == 0

        rule = GrowthRule(
            pattern=GrowthPattern.SPARSE,
            can_grow=only_even,
        )
        addr_even = FractalAddress(path=(0,))
        addr_odd = FractalAddress(path=(1,))
        assert rule.should_grow(addr_even) is True
        assert rule.should_grow(addr_odd) is False


# =============================================================================
# FractalProtocol Tests
# =============================================================================


class TestFractalProtocol:
    """Test FractalProtocol."""

    def test_fractal_protocol_validates(self):
        """FractalProtocol validates."""
        valid, violations = FractalProtocol.validate()
        assert valid is True

    def test_fractal_protocol_identity(self):
        """FractalProtocol has correct identity."""
        identity = FractalProtocol.get_identity()
        assert identity.name == "FractalProtocol"
        assert identity.mahajana == "kapila"
        assert identity.position == 3

    def test_fractal_protocol_provides_capabilities(self):
        """FractalProtocol provides fractal capabilities."""
        cap = FractalProtocol.get_capability()
        assert "fractal_address" in cap.provides
        assert "fractal_node" in cap.provides
        assert "fractal_tree" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _fractal
        expected = [
            "FractalAddress",
            "FractalNode",
            "FractalTree",
            "GrowthPattern",
            "GrowthRule",
            "FractalProtocol",
        ]
        for item in expected:
            assert item in _fractal.__all__, f"{item} should be in __all__"
