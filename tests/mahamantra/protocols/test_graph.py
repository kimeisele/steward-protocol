"""
TESTS: _graph.py - The Graph Protocol
======================================

REAL TESTS for:
1. Graph constants
2. NodeType, EdgeType, Sampradaya enums
3. GraphNode, GraphEdge dataclasses
4. VedicGraph class
5. GraphBuilder class
6. ProtocolGraph class
"""

import pytest
from vibe_core.mahamantra.protocols._graph import (
    # Constants
    PRAKRITI_COUNT,
    PURIFICATION_CYCLE,
    MANTRA_CYCLES,
    PRAKRITI_CYCLES,
    # Enums
    NodeType,
    EdgeType,
    Sampradaya,
    # Dataclasses
    GraphNode,
    GraphEdge,
    # Classes
    VedicGraph,
    GraphBuilder,
    ProtocolGraph,
    # Protocol
    GraphProtocolDef,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestGraphConstants:
    """Test graph constants."""

    def test_prakriti_count_is_24(self):
        """PRAKRITI_COUNT is 24."""
        assert PRAKRITI_COUNT == 24

    def test_purification_cycle_is_48(self):
        """PURIFICATION_CYCLE is 48 (LCM of 16 and 24)."""
        assert PURIFICATION_CYCLE == 48

    def test_mantra_cycles_is_3(self):
        """MANTRA_CYCLES is 3 (48/16)."""
        assert MANTRA_CYCLES == 3

    def test_prakriti_cycles_is_2(self):
        """PRAKRITI_CYCLES is 2 (48/24)."""
        assert PRAKRITI_CYCLES == 2


# =============================================================================
# NodeType Enum Tests
# =============================================================================


class TestNodeType:
    """Test NodeType enum."""

    def test_node_type_source(self):
        """NodeType has SOURCE."""
        assert NodeType.SOURCE.value == "source"

    def test_node_type_avatara(self):
        """NodeType has AVATARA."""
        assert NodeType.AVATARA.value == "avatara"

    def test_node_type_shaktyavesha(self):
        """NodeType has SHAKTYAVESHA."""
        assert NodeType.SHAKTYAVESHA.value == "shaktyavesha"

    def test_node_type_mahajana(self):
        """NodeType has MAHAJANA."""
        assert NodeType.MAHAJANA.value == "mahajana"

    def test_node_type_acharya(self):
        """NodeType has ACHARYA."""
        assert NodeType.ACHARYA.value == "acharya"

    def test_node_type_prakriti(self):
        """NodeType has PRAKRITI."""
        assert NodeType.PRAKRITI.value == "prakriti"

    def test_node_type_protocol(self):
        """NodeType has PROTOCOL."""
        assert NodeType.PROTOCOL.value == "protocol"


# =============================================================================
# EdgeType Enum Tests
# =============================================================================


class TestEdgeType:
    """Test EdgeType enum."""

    def test_edge_type_diksha(self):
        """EdgeType has DIKSHA."""
        assert EdgeType.DIKSHA.value == "diksha"

    def test_edge_type_siksha(self):
        """EdgeType has SIKSHA."""
        assert EdgeType.SIKSHA.value == "siksha"

    def test_edge_type_serves(self):
        """EdgeType has SERVES."""
        assert EdgeType.SERVES.value == "serves"

    def test_edge_type_manifests(self):
        """EdgeType has MANIFESTS."""
        assert EdgeType.MANIFESTS.value == "manifests"

    def test_edge_type_depends(self):
        """EdgeType has DEPENDS."""
        assert EdgeType.DEPENDS.value == "depends"


# =============================================================================
# Sampradaya Enum Tests
# =============================================================================


class TestSampradaya:
    """Test Sampradaya enum."""

    def test_sampradaya_brahma(self):
        """Sampradaya has BRAHMA."""
        assert Sampradaya.BRAHMA.value == "brahma"

    def test_sampradaya_kumara(self):
        """Sampradaya has KUMARA."""
        assert Sampradaya.KUMARA.value == "kumara"

    def test_sampradaya_sri(self):
        """Sampradaya has SRI."""
        assert Sampradaya.SRI.value == "sri"

    def test_sampradaya_rudra(self):
        """Sampradaya has RUDRA."""
        assert Sampradaya.RUDRA.value == "rudra"

    def test_sampradaya_count(self):
        """There are 4 sampradayas."""
        assert len(Sampradaya) == 4


# =============================================================================
# GraphNode Tests
# =============================================================================


class TestGraphNode:
    """Test GraphNode dataclass."""

    def test_graph_node_creation(self):
        """GraphNode can be created."""
        node = GraphNode(
            id="test",
            node_type=NodeType.PROTOCOL,
        )
        assert node.id == "test"
        assert node.node_type == NodeType.PROTOCOL

    def test_graph_node_source(self):
        """SOURCE node creation."""
        node = GraphNode(
            id="KRISHNA",
            node_type=NodeType.SOURCE,
            level=-2,
        )
        assert node.level == -2

    def test_graph_node_mahajana_position(self):
        """Mahajana node gets lotus_position from name."""
        node = GraphNode(
            id="vyasa",
            node_type=NodeType.MAHAJANA,
            sampradaya=Sampradaya.BRAHMA,
        )
        assert node.lotus_position == 0

    def test_graph_node_parampara_vector(self):
        """parampara_vector computed correctly."""
        node = GraphNode(
            id="vyasa",
            node_type=NodeType.MAHAJANA,
            lotus_position=0,
        )
        from vibe_core.mahamantra.protocols._core import PARAMPARA
        assert node.parampara_vector == (0 + 1) * PARAMPARA

    def test_graph_node_is_connected(self):
        """is_connected is True for valid nodes."""
        node = GraphNode(
            id="vyasa",
            node_type=NodeType.MAHAJANA,
            lotus_position=0,
        )
        assert node.is_connected is True

    def test_graph_node_is_frozen(self):
        """GraphNode is frozen."""
        node = GraphNode(id="test", node_type=NodeType.PROTOCOL)
        with pytest.raises(Exception):
            node.id = "changed"


# =============================================================================
# GraphEdge Tests
# =============================================================================


class TestGraphEdge:
    """Test GraphEdge dataclass."""

    def test_graph_edge_creation(self):
        """GraphEdge can be created."""
        edge = GraphEdge(
            source="KRISHNA",
            target="BRAHMA",
            edge_type=EdgeType.DIKSHA,
        )
        assert edge.source == "KRISHNA"
        assert edge.target == "BRAHMA"

    def test_graph_edge_weight_default(self):
        """Default weight is 1.0."""
        edge = GraphEdge(
            source="A",
            target="B",
            edge_type=EdgeType.SIKSHA,
        )
        assert edge.weight == 1.0

    def test_graph_edge_is_frozen(self):
        """GraphEdge is frozen."""
        edge = GraphEdge(source="A", target="B", edge_type=EdgeType.DIKSHA)
        with pytest.raises(Exception):
            edge.source = "C"


# =============================================================================
# VedicGraph Tests
# =============================================================================


class TestVedicGraph:
    """Test VedicGraph class."""

    def test_vedic_graph_creation(self):
        """VedicGraph can be created."""
        graph = VedicGraph()
        assert graph is not None

    def test_vedic_graph_add_node(self):
        """add_node adds node."""
        graph = VedicGraph()
        node = GraphNode(id="test", node_type=NodeType.PROTOCOL)
        graph.add_node(node)
        assert graph.get_node("test") is node

    def test_vedic_graph_add_edge(self):
        """add_edge adds edge."""
        graph = VedicGraph()
        graph.add_node(GraphNode(id="A", node_type=NodeType.PROTOCOL))
        graph.add_node(GraphNode(id="B", node_type=NodeType.PROTOCOL))
        edge = GraphEdge(source="A", target="B", edge_type=EdgeType.DEPENDS)
        graph.add_edge(edge)
        assert graph.count_edges() == 1

    def test_vedic_graph_get_parent(self):
        """get_parent finds parent."""
        graph = VedicGraph()
        graph.add_node(GraphNode(id="A", node_type=NodeType.MAHAJANA))
        graph.add_node(GraphNode(id="B", node_type=NodeType.ACHARYA))
        graph.add_edge(GraphEdge(source="A", target="B", edge_type=EdgeType.DIKSHA))
        parent = graph.get_parent("B")
        assert parent == "A"

    def test_vedic_graph_get_children(self):
        """get_children finds children."""
        graph = VedicGraph()
        graph.add_node(GraphNode(id="A", node_type=NodeType.MAHAJANA))
        graph.add_node(GraphNode(id="B", node_type=NodeType.ACHARYA))
        graph.add_node(GraphNode(id="C", node_type=NodeType.ACHARYA))
        graph.add_edge(GraphEdge(source="A", target="B", edge_type=EdgeType.DIKSHA))
        graph.add_edge(GraphEdge(source="A", target="C", edge_type=EdgeType.DIKSHA))
        children = graph.get_children("A")
        assert "B" in children
        assert "C" in children

    def test_vedic_graph_get_lineage(self):
        """get_lineage traces back to source."""
        graph = VedicGraph()
        graph.add_node(GraphNode(id="KRISHNA", node_type=NodeType.SOURCE))
        graph.add_node(GraphNode(id="BRAHMA", node_type=NodeType.MAHAJANA))
        graph.add_node(GraphNode(id="DISCIPLE", node_type=NodeType.ACHARYA))
        graph.add_edge(GraphEdge(source="KRISHNA", target="BRAHMA", edge_type=EdgeType.DIKSHA))
        graph.add_edge(GraphEdge(source="BRAHMA", target="DISCIPLE", edge_type=EdgeType.DIKSHA))

        lineage = graph.get_lineage("DISCIPLE")
        assert lineage == ["DISCIPLE", "BRAHMA", "KRISHNA"]

    def test_vedic_graph_is_connected_to_source(self):
        """is_connected_to_source checks connection."""
        graph = VedicGraph()
        graph.add_node(GraphNode(id="KRISHNA", node_type=NodeType.SOURCE))
        graph.add_node(GraphNode(id="BRAHMA", node_type=NodeType.MAHAJANA))
        graph.add_edge(GraphEdge(source="KRISHNA", target="BRAHMA", edge_type=EdgeType.DIKSHA))

        assert graph.is_connected_to_source("BRAHMA") is True

    def test_vedic_graph_count_nodes(self):
        """count_nodes counts all nodes."""
        graph = VedicGraph()
        graph.add_node(GraphNode(id="A", node_type=NodeType.PROTOCOL))
        graph.add_node(GraphNode(id="B", node_type=NodeType.PROTOCOL))
        assert graph.count_nodes() == 2


# =============================================================================
# GraphBuilder Tests
# =============================================================================


class TestGraphBuilder:
    """Test GraphBuilder class."""

    def test_graph_builder_add_source(self):
        """add_source adds KRISHNA node."""
        graph = GraphBuilder().add_source().build()
        assert graph.get_node("KRISHNA") is not None

    def test_graph_builder_add_mahajana(self):
        """add_mahajana adds mahajana node."""
        graph = (
            GraphBuilder()
            .add_source()
            .add_mahajana("BRAHMA", Sampradaya.BRAHMA)
            .build()
        )
        node = graph.get_node("BRAHMA")
        assert node is not None
        assert node.node_type == NodeType.MAHAJANA

    def test_graph_builder_diksha(self):
        """diksha adds diksha edge."""
        graph = (
            GraphBuilder()
            .add_source()
            .add_mahajana("BRAHMA", Sampradaya.BRAHMA)
            .diksha("KRISHNA", "BRAHMA")
            .build()
        )
        parent = graph.get_parent("BRAHMA")
        assert parent == "KRISHNA"

    def test_graph_builder_fluent_api(self):
        """Builder supports fluent API."""
        graph = (
            GraphBuilder()
            .add_source()
            .add_mahajana("BRAHMA", Sampradaya.BRAHMA)
            .add_mahajana("NARADA", Sampradaya.BRAHMA)
            .diksha("KRISHNA", "BRAHMA")
            .diksha("BRAHMA", "NARADA")
            .build()
        )
        assert graph.count_nodes() == 3
        assert graph.count_edges() == 2


# =============================================================================
# ProtocolGraph Tests
# =============================================================================


class TestProtocolGraph:
    """Test ProtocolGraph class."""

    def test_protocol_graph_add_protocol(self):
        """add_protocol adds protocol node."""
        graph = ProtocolGraph()
        graph.add_protocol(
            name="TestProtocol",
            provides=["feature1"],
            requires=["CoreProtocol"],
            mahajana="vyasa",
        )
        node = graph.get_node("TestProtocol")
        assert node is not None
        assert node.lotus_position == 0

    def test_protocol_graph_get_dependencies(self):
        """get_dependencies returns dependencies."""
        graph = ProtocolGraph()
        graph.add_protocol("Core", provides=[], requires=[], mahajana="vyasa")
        graph.add_protocol("Other", provides=[], requires=["Core"], mahajana="brahma")

        deps = graph.get_dependencies("Other")
        assert "Core" in deps

    def test_protocol_graph_get_dependents(self):
        """get_dependents returns dependents."""
        graph = ProtocolGraph()
        graph.add_protocol("Core", provides=[], requires=[], mahajana="vyasa")
        graph.add_protocol("Other", provides=[], requires=["Core"], mahajana="brahma")

        dependents = graph.get_dependents("Core")
        assert "Other" in dependents

    def test_protocol_graph_topological_sort(self):
        """topological_sort returns correct order."""
        graph = ProtocolGraph()
        graph.add_protocol("Core", provides=[], requires=[], mahajana="vyasa")
        graph.add_protocol("Fractal", provides=[], requires=["Core"], mahajana="kapila")
        graph.add_protocol("Lotus", provides=[], requires=["Fractal"], mahajana="prithu")

        order = graph.topological_sort()
        # Core should come before Fractal, Fractal before Lotus
        assert order.index("Core") < order.index("Fractal")
        assert order.index("Fractal") < order.index("Lotus")


# =============================================================================
# GraphProtocolDef Tests
# =============================================================================


class TestGraphProtocolDef:
    """Test GraphProtocolDef."""

    def test_graph_protocol_validates(self):
        """GraphProtocolDef validates."""
        valid, violations = GraphProtocolDef.validate()
        assert valid is True

    def test_graph_protocol_identity(self):
        """GraphProtocolDef has correct identity."""
        identity = GraphProtocolDef.get_identity()
        assert identity.name == "GraphProtocol"
        assert identity.mahajana == "kapila"


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _graph
        expected = [
            "NodeType",
            "EdgeType",
            "Sampradaya",
            "GraphNode",
            "GraphEdge",
            "VedicGraph",
            "GraphBuilder",
            "ProtocolGraph",
        ]
        for item in expected:
            assert item in _graph.__all__, f"{item} should be in __all__"
