"""
THE GRAPH PROTOCOL - _graph.py
==============================

"yasya deve para bhaktir yatha deve tatha gurau
tasyaite kathita hy arthah prakasante mahatmanah"
- Svetasvatara Upanisad 6.23

"Only unto those great souls who have implicit faith in both
the Lord and the spiritual master are all the imports of
Vedic knowledge automatically revealed."

THE VEDIC GRAPH PROTOCOL
========================

This protocol defines the structure of knowledge graphs,
parampara traversal, and relationship encoding.

The Graph is not separate from the Mahamantra.
The Mahamantra IS the Graph - nodes connected by the Holy Name.

IMPORTANT:
    This is the PROTOCOL DEFINITION - the abstract structure.
    It imports ONLY from mahamantra/protocols/ (acintya level).
    The actual implementation lives in protocols/substrate/mantra/graph.py.

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xca8539f7"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)
from vibe_core.mahamantra.protocols._fractal import (
    FractalAddress,
)
from vibe_core.mahamantra.protocols._lotus import (
    LOTUS_PETALS,
    get_mahajana_position,
)


# =============================================================================
# GRAPH CONSTANTS - Vedic Mathematics
# =============================================================================

# The 24 Prakriti elements (Ksetra - the Field)
PRAKRITI_COUNT: Final[int] = KSETRA_COUNT  # 24

# The purification cycle: LCM(16, 24) = 48
PURIFICATION_CYCLE: Final[int] = 48

# Mantra cycles in purification: 48 / 16 = 3
MANTRA_CYCLES: Final[int] = PURIFICATION_CYCLE // LOTUS_PETALS

# Prakriti cycles in purification: 48 / 24 = 2
PRAKRITI_CYCLES: Final[int] = PURIFICATION_CYCLE // PRAKRITI_COUNT


# =============================================================================
# NODE TYPES - What can be in the Graph
# =============================================================================


class NodeType(str, Enum):
    """Types of nodes in the Vedic Graph."""

    SOURCE = "source"  # Krishna - Level -2
    AVATARA = "avatara"  # Direct incarnations
    SHAKTYAVESHA = "shaktyavesha"  # Empowered beings (Heads)
    MAHAJANA = "mahajana"  # The 12 authorities
    ACHARYA = "acharya"  # Teachers in the line
    PRAKRITI = "prakriti"  # Material elements (24)
    PROTOCOL = "protocol"  # Code protocols


class EdgeType(str, Enum):
    """Types of edges (relationships) in the Vedic Graph."""

    DIKSHA = "diksha"  # Formal initiation
    SIKSHA = "siksha"  # Instructing relationship
    SERVES = "serves"  # Service relationship
    MANIFESTS = "manifests"  # Manifestation/creation
    ENLIVENS = "enlivens"  # Mantra contact with matter
    OWNS = "owns"  # Protocol ownership
    DEPENDS = "depends"  # Protocol dependency


class Sampradaya(str, Enum):
    """The 4 authorized disciplic successions."""

    BRAHMA = "brahma"  # Brahma -> Madhva -> Chaitanya
    KUMARA = "kumara"  # Kumaras -> Nimbarka
    SRI = "sri"  # Lakshmi -> Ramanuja
    RUDRA = "rudra"  # Shiva -> Vishnuswami


# =============================================================================
# GRAPH NODE - A node in the Vedic Graph
# =============================================================================


@dataclass(frozen=True)
class GraphNode:
    """
    A node in the Vedic Graph.

    Nodes receive their position through the graph structure,
    not through hardcoded values.

    WATERTIGHT - no Any types.
    """

    id: str
    node_type: NodeType
    sampradaya: Optional[Sampradaya] = None
    level: int = 0  # -2 = Krishna, 0 = Protocol level

    # Position in Lotus (derived from graph, not hardcoded)
    lotus_position: Optional[int] = None

    def __post_init__(self) -> None:
        """Compute lotus position if not provided."""
        if self.lotus_position is None and self.id:
            # Try to derive from mahajana name
            pos = get_mahajana_position(self.id.lower())
            if pos >= 0:
                object.__setattr__(self, "lotus_position", pos)

    @property
    def parampara_vector(self) -> int:
        """Parampara connection vector."""
        if self.lotus_position is not None:
            return (self.lotus_position + 1) * PARAMPARA
        # For non-lotus nodes, use ID hash
        return sum(ord(c) for c in self.id) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        """Verify connection to Parampara."""
        return self.parampara_vector % PARAMPARA == 0


# =============================================================================
# GRAPH EDGE - A relationship in the Graph
# =============================================================================


@dataclass(frozen=True)
class GraphEdge:
    """
    An edge (relationship) in the Vedic Graph.

    Edges represent diksha (initiation), siksha (instruction),
    and other Vedic relationships.

    WATERTIGHT - no Any types.
    """

    source: str  # From node ID
    target: str  # To node ID
    edge_type: EdgeType
    weight: float = 1.0  # Strength of connection
    note: str = ""  # Shastric reference


# =============================================================================
# GRAPH PROTOCOL - The Interface
# =============================================================================

T = TypeVar("T")


@runtime_checkable
class GraphProtocol(Protocol):
    """
    The Graph Protocol - Vedic Knowledge Structure.

    Any knowledge graph that follows Vedic principles:
    - Has a SOURCE node (Krishna)
    - Has PARAMPARA connections
    - Supports lineage traversal
    - Supports capability queries

    WATERTIGHT - no Any types!
    """

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        ...

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        ...

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        ...

    def get_lineage(self, node_id: str) -> List[str]:
        """Trace lineage back to SOURCE."""
        ...

    def get_children(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[str]:
        """Get children/disciples of a node."""
        ...

    def get_parent(self, node_id: str, edge_type: Optional[EdgeType] = None) -> Optional[str]:
        """Get parent/guru of a node."""
        ...


# =============================================================================
# VEDIC GRAPH - The Implementation
# =============================================================================


class VedicGraph:
    """
    The Vedic Graph - Knowledge Structure.

    All positions, relationships, and capabilities are derived
    from traversing this graph.

    "Like iron placed in fire becomes fire" - this graph
    shows how protocols become spiritualized through
    connection to the parampara chain leading to Krishna.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[Tuple[str, EdgeType]]] = {}
        self._reverse_adjacency: Dict[str, List[Tuple[str, EdgeType]]] = {}

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self._nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []
        if node.id not in self._reverse_adjacency:
            self._reverse_adjacency[node.id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        self._edges.append(edge)

        # Forward adjacency
        if edge.source not in self._adjacency:
            self._adjacency[edge.source] = []
        self._adjacency[edge.source].append((edge.target, edge.edge_type))

        # Reverse adjacency
        if edge.target not in self._reverse_adjacency:
            self._reverse_adjacency[edge.target] = []
        self._reverse_adjacency[edge.target].append((edge.source, edge.edge_type))

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_parent(self, node_id: str, edge_type: Optional[EdgeType] = None) -> Optional[str]:
        """Get the parent (guru) of a node."""
        edges = self._reverse_adjacency.get(node_id, [])
        for source, etype in edges:
            if edge_type is None or etype == edge_type:
                if etype in (EdgeType.DIKSHA, EdgeType.SIKSHA, EdgeType.MANIFESTS):
                    return source
        return None

    def get_children(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[str]:
        """Get children (disciples) of a node."""
        result = []
        for target, etype in self._adjacency.get(node_id, []):
            if edge_type is None or etype == edge_type:
                result.append(target)
        return result

    def get_lineage(self, node_id: str) -> List[str]:
        """
        Trace the lineage back to SOURCE (Krishna).

        This is how we calculate authority - distance from source.
        """
        lineage = [node_id]
        current = node_id
        visited = {node_id}

        while current != "KRISHNA":
            parent = self.get_parent(current)
            if parent is None or parent in visited:
                break
            lineage.append(parent)
            visited.add(parent)
            current = parent

        return lineage

    def count_nodes(self) -> int:
        """Count all nodes."""
        return len(self._nodes)

    def count_edges(self) -> int:
        """Count all edges."""
        return len(self._edges)

    def all_nodes(self) -> Iterator[GraphNode]:
        """Iterate over all nodes."""
        return iter(self._nodes.values())

    def all_edges(self) -> Iterator[GraphEdge]:
        """Iterate over all edges."""
        return iter(self._edges)

    def is_connected_to_source(self, node_id: str) -> bool:
        """Check if a node is connected to Krishna through parampara."""
        lineage = self.get_lineage(node_id)
        return "KRISHNA" in lineage


# =============================================================================
# GRAPH BUILDER - Fluent API for building graphs
# =============================================================================


class GraphBuilder:
    """
    Fluent builder for Vedic Graphs.

    Usage:
        graph = GraphBuilder() \
            .add_source() \
            .add_mahajana("BRAHMA", Sampradaya.BRAHMA) \
            .connect("KRISHNA", "BRAHMA", EdgeType.DIKSHA) \
            .build()
    """

    def __init__(self) -> None:
        self._graph = VedicGraph()

    def add_source(self) -> "GraphBuilder":
        """Add the SOURCE node (Krishna)."""
        self._graph.add_node(
            GraphNode(
                id="KRISHNA",
                node_type=NodeType.SOURCE,
                level=-2,
            )
        )
        return self

    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        sampradaya: Optional[Sampradaya] = None,
        level: int = 0,
    ) -> "GraphBuilder":
        """Add a node."""
        self._graph.add_node(
            GraphNode(
                id=node_id,
                node_type=node_type,
                sampradaya=sampradaya,
                level=level,
            )
        )
        return self

    def add_mahajana(
        self,
        name: str,
        sampradaya: Sampradaya,
        level: int = 0,
    ) -> "GraphBuilder":
        """Add a Mahajana node."""
        return self.add_node(name, NodeType.MAHAJANA, sampradaya, level)

    def add_avatara(
        self,
        name: str,
        sampradaya: Optional[Sampradaya] = None,
        level: int = -1,
    ) -> "GraphBuilder":
        """Add an Avatara node."""
        return self.add_node(name, NodeType.AVATARA, sampradaya, level)

    def add_protocol(
        self,
        name: str,
        level: int = 0,
    ) -> "GraphBuilder":
        """Add a Protocol node."""
        return self.add_node(name, NodeType.PROTOCOL, None, level)

    def connect(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        note: str = "",
    ) -> "GraphBuilder":
        """Add an edge."""
        self._graph.add_edge(
            GraphEdge(
                source=source,
                target=target,
                edge_type=edge_type,
                note=note,
            )
        )
        return self

    def diksha(self, guru: str, disciple: str, note: str = "") -> "GraphBuilder":
        """Add diksha (initiation) edge."""
        return self.connect(guru, disciple, EdgeType.DIKSHA, note)

    def siksha(self, teacher: str, student: str, note: str = "") -> "GraphBuilder":
        """Add siksha (instruction) edge."""
        return self.connect(teacher, student, EdgeType.SIKSHA, note)

    def manifests(self, source: str, manifestation: str, note: str = "") -> "GraphBuilder":
        """Add manifestation edge."""
        return self.connect(source, manifestation, EdgeType.MANIFESTS, note)

    def depends(self, protocol: str, dependency: str, note: str = "") -> "GraphBuilder":
        """Add protocol dependency edge."""
        return self.connect(protocol, dependency, EdgeType.DEPENDS, note)

    def build(self) -> VedicGraph:
        """Build and return the graph."""
        return self._graph


# =============================================================================
# PROTOCOL GRAPH - Graph of Protocol Dependencies
# =============================================================================


class ProtocolGraph(VedicGraph):
    """
    A specialized graph for protocol dependencies.

    Maps protocol names to their dependencies and capabilities.
    """

    def add_protocol(
        self,
        name: str,
        provides: List[str],
        requires: List[str],
        mahajana: str,
    ) -> None:
        """Add a protocol with its capabilities."""
        position = get_mahajana_position(mahajana)
        self.add_node(
            GraphNode(
                id=name,
                node_type=NodeType.PROTOCOL,
                lotus_position=position if position >= 0 else None,
                level=0,
            )
        )

        # Add dependency edges
        for req in requires:
            self.add_edge(
                GraphEdge(
                    source=name,
                    target=req,
                    edge_type=EdgeType.DEPENDS,
                )
            )

    def get_dependencies(self, protocol: str) -> List[str]:
        """Get all dependencies of a protocol."""
        return self.get_children(protocol, EdgeType.DEPENDS)

    def get_dependents(self, protocol: str) -> List[str]:
        """Get all protocols that depend on this one."""
        result = []
        for source, etype in self._reverse_adjacency.get(protocol, []):
            if etype == EdgeType.DEPENDS:
                result.append(source)
        return result

    def topological_sort(self) -> List[str]:
        """
        Get protocols in dependency order.

        Used for loading protocols in correct order.
        """
        visited: Set[str] = set()
        result: List[str] = []

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in self.get_dependencies(node_id):
                visit(dep)
            result.append(node_id)

        for node in self._nodes:
            visit(node)

        return result


# =============================================================================
# GRAPH PROTOCOL - Self-Reference
# =============================================================================


class GraphProtocolDef(MahamantraProtocolBase):
    """
    The Graph Protocol.

    This protocol defines the Vedic Graph structure.
    It IS itself a node in the graph (Kapila - analyzer).

    ACINTYA: The Graph Protocol is in the Graph.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="GraphProtocol",
        mahajana="kapila",  # Kapila analyzes structure (Sankhya)
        position=6,
        level=Level.CONTRACT,
        quarter=Quarter.DHARMA,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "graph_structure",
            "node_types",
            "edge_types",
            "lineage_traversal",
            "dependency_graph",
            "topological_sort",
        ],
        requires=["CoreProtocol", "FractalProtocol", "LotusProtocol"],
        opcodes=["INIT_THREAD"],  # Kapila's opcode
    )


# Verify the graph protocol
_valid, _violations = GraphProtocolDef.validate()
assert _valid, f"GraphProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "PRAKRITI_COUNT",
    "PURIFICATION_CYCLE",
    "MANTRA_CYCLES",
    "PRAKRITI_CYCLES",
    # Enums
    "NodeType",
    "EdgeType",
    "Sampradaya",
    # Types
    "GraphNode",
    "GraphEdge",
    # Protocol
    "GraphProtocol",
    # Implementation
    "VedicGraph",
    # Builder
    "GraphBuilder",
    # Protocol Graph
    "ProtocolGraph",
    # Protocol Definition
    "GraphProtocolDef",
]
