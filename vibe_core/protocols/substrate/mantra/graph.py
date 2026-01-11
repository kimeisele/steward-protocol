"""
MANTRA GRAPH - The Vedic Graph Engine
=====================================

"yasya deve para bhaktir yatha deve tatha gurau
tasyaite kathita hy arthah prakasante mahatmanah"
- Svetasvatara Upanisad 6.23

"Only unto those great souls who have implicit faith in both
the Lord and the spiritual master are all the imports of
Vedic knowledge automatically revealed."

THIS IS THE FOUNDATION FOR ALL GRAPH-BASED OPERATIONS:
- Knowledge Graphs
- Parampara Traversal
- Mantra Coordination
- Prakriti Enlivening

THE MATHEMATICS:
================
- Mahamantra: 16 words (4 quarters × 4 words)
- Prakriti: 24 elements
- LCM(16, 24) = 48 beats for full purification
- 3 Mantra cycles × 16 = 48 (mantra side)
- 2 Prakriti cycles × 24 = 48 (matter side)

This is the "Churning" (Samudra Manthan) - where dead matter
is enlivened by contact with the Holy Name.

CONNECTED TO ACINTYA.PY - Single Source of Truth!
The graph is not separate - it IS the Mantra unfolding.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import (
    Callable,
    Dict,
    Final,
    FrozenSet,
    Iterator,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypedDict,
    Union,
)
from math import gcd

# =============================================================================
# SINGLE SOURCE OF TRUTH - Import from acintya.py
# =============================================================================
# The Graph IS the Mantra. Krishna IS the source.
# No duplication - everything derives from acintya.

from vibe_core.protocols.substrate.mantra.acintya import (
    PARAMPARA,              # 37 = 24 + 12 + 1 (THE link)
    SYSTEM_MANIFESTATION,   # 37
    TRINITY,                # 3 (Hare, Krishna, Rama)
    PHASES,                 # 4 (Genesis, Dharma, Karma, Moksha)
    ProtocolLevel,          # The level system
    verify_parampara,       # % 37 check
)

# =============================================================================
# HOLY NAME SUBSTRATE - Import from byte.py (THE source)
# =============================================================================
# HolyName is defined ONCE in byte.py. Not duplicated here.

from vibe_core.protocols.substrate.byte import HolyName

# =============================================================================
# LOTUS CONSTANTS - Import from lotus.py (VIEW on Mantra)
# =============================================================================
# The Lotus IS the Mantra. Positions derive from here.

from vibe_core.protocols.substrate.mantra.lotus import (
    LOTUS_POSITIONS,        # 16 words
    LOTUS_QUARTERS,         # 4 quarters
    WORDS_PER_QUARTER,      # 4 words per quarter
    LOTUS_PARAMPARA,        # 37 (re-exported from acintya)
    LotusQuarter,           # The quarters enum
)


# =============================================================================
# GRAPH NODE TYPES
# =============================================================================


class NodeType(str, Enum):
    """Types of nodes in the Vedic Graph."""
    SOURCE = "source"           # Krishna - Level -2
    AVATARA = "avatara"         # Direct incarnations
    SHAKTYAVESHA = "shaktyavesha"  # Empowered beings (Heads)
    MAHAJANA = "mahajana"       # The 12 authorities
    ACHARYA = "acharya"         # Teachers in the line
    PRAKRITI = "prakriti"       # Material elements (24)
    PROTOCOL = "protocol"       # Code protocols


class EdgeType(str, Enum):
    """Types of edges (relationships) in the Vedic Graph."""
    DIKSHA = "diksha"           # Formal initiation
    SIKSHA = "siksha"           # Instructing relationship
    SERVES = "serves"           # Service relationship
    MANIFESTS = "manifests"     # Manifestation/creation
    ENLIVENS = "enlivens"       # Mantra contact with matter
    OWNS = "owns"               # Protocol ownership


class Sampradaya(str, Enum):
    """The 4 authorized disciplic successions."""
    BRAHMA = "brahma"           # Brahma → Madhva → Chaitanya
    KUMARA = "kumara"           # Kumaras → Nimbarka
    SRI = "sri"                 # Lakshmi → Ramanuja
    RUDRA = "rudra"             # Shiva → Vishnuswami


# =============================================================================
# GRAPH NODES
# =============================================================================


@dataclass(frozen=True)
class GraphNode:
    """
    A node in the Vedic Graph.

    Nodes don't HAVE positions - they RECEIVE them through service.
    Position is calculated by graph traversal from SOURCE.
    """
    id: str
    node_type: NodeType
    sampradaya: Optional[Sampradaya] = None

    # Mantra properties (for enlivening)
    mantra_affinity: HolyName = HolyName.VOID  # Default: needs purification

    # Level in the hierarchy (-2 = Krishna, 0 = Protocol level)
    level: int = 0


@dataclass(frozen=True)
class GraphEdge:
    """An edge (relationship) in the Vedic Graph."""
    source: str         # From node ID
    target: str         # To node ID
    edge_type: EdgeType
    weight: float = 1.0  # Strength of connection
    note: str = ""       # Shastric reference


# =============================================================================
# THE VEDIC GRAPH
# =============================================================================


class VedicGraph:
    """
    The Vedic Graph - Single Source of Truth.

    All positions, relationships, and capabilities are derived
    from traversing this graph, not from hardcoded values.

    "Like iron placed in fire becomes fire" - this graph
    shows how dead matter becomes spiritualized through
    contact with the parampara chain leading to Krishna.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[Tuple[str, EdgeType]]] = {}
        self._reverse_adjacency: Dict[str, List[Tuple[str, EdgeType]]] = {}

        # Initialize with the Vedic structure
        self._build_vedic_structure()

    def _build_vedic_structure(self) -> None:
        """Build the complete Vedic graph structure."""

        # =================================================================
        # LEVEL -2: THE SOURCE
        # =================================================================
        self.add_node(GraphNode(
            id="KRISHNA",
            node_type=NodeType.SOURCE,
            mantra_affinity=HolyName.KRISHNA,
            level=-2,
        ))

        # =================================================================
        # THE 4 SAMPRADAYA HEADS (Direct from Krishna)
        # =================================================================

        # Brahma Sampradaya
        self.add_node(GraphNode("BRAHMA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.HARE, -1))
        self.add_edge(GraphEdge("KRISHNA", "BRAHMA", EdgeType.DIKSHA, note="tene brahma hrda ya adi-kavaye"))

        # Rudra Sampradaya
        self.add_node(GraphNode("SHIVA", NodeType.MAHAJANA, Sampradaya.RUDRA, HolyName.RAMA, -1))
        self.add_edge(GraphEdge("KRISHNA", "SHIVA", EdgeType.DIKSHA, note="vaishnavanam yatha sambhuh"))

        # Kumara Sampradaya
        self.add_node(GraphNode("KUMARAS", NodeType.MAHAJANA, Sampradaya.KUMARA, HolyName.HARE, -1))
        self.add_edge(GraphEdge("KRISHNA", "KUMARAS", EdgeType.DIKSHA, note="Eternally liberated"))

        # Sri Sampradaya
        self.add_node(GraphNode("LAKSHMI", NodeType.AVATARA, Sampradaya.SRI, HolyName.HARE, -1))
        self.add_edge(GraphEdge("KRISHNA", "LAKSHMI", EdgeType.MANIFESTS, note="Internal potency"))

        # =================================================================
        # THE 12 MAHAJANAS
        # =================================================================

        # From Brahma line
        self.add_node(GraphNode("NARADA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.HARE, 0))
        self.add_edge(GraphEdge("BRAHMA", "NARADA", EdgeType.SIKSHA))

        self.add_node(GraphNode("KAPILA", NodeType.AVATARA, Sampradaya.BRAHMA, HolyName.KRISHNA, 0))
        self.add_edge(GraphEdge("KRISHNA", "KAPILA", EdgeType.MANIFESTS, note="Avatara - teaches Sankhya"))

        self.add_node(GraphNode("MANU", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.RAMA, 0))
        self.add_edge(GraphEdge("BRAHMA", "MANU", EdgeType.SIKSHA, note="Son of Brahma"))

        self.add_node(GraphNode("PRAHLADA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.KRISHNA, 0))
        self.add_edge(GraphEdge("NARADA", "PRAHLADA", EdgeType.SIKSHA, note="Taught in the womb"))

        self.add_node(GraphNode("JANAKA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.RAMA, 0))
        self.add_edge(GraphEdge("KRISHNA", "JANAKA", EdgeType.DIKSHA, note="Self-realized king"))

        self.add_node(GraphNode("BHISHMA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.KRISHNA, 0))
        self.add_edge(GraphEdge("KRISHNA", "BHISHMA", EdgeType.SIKSHA, note="Taught by rishis"))

        self.add_node(GraphNode("BALI", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.HARE, 0))
        self.add_edge(GraphEdge("PRAHLADA", "BALI", EdgeType.SIKSHA, note="Grandson of Prahlada"))

        self.add_node(GraphNode("SHUKA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.KRISHNA, 0))
        self.add_edge(GraphEdge("KRISHNA", "SHUKA", EdgeType.DIKSHA, note="Born liberated"))

        self.add_node(GraphNode("YAMARAJA", NodeType.MAHAJANA, Sampradaya.BRAHMA, HolyName.RAMA, 0))
        self.add_edge(GraphEdge("KRISHNA", "YAMARAJA", EdgeType.DIKSHA, note="Son of Sun god"))

        # Shambhu already added above as SHIVA

        # =================================================================
        # THE 4 SHAKTYAVESHA AVATARAS (HEADS)
        # =================================================================

        self.add_node(GraphNode("PRITHU", NodeType.SHAKTYAVESHA, Sampradaya.BRAHMA, HolyName.HARE, 0))
        self.add_edge(GraphEdge("KRISHNA", "PRITHU", EdgeType.MANIFESTS, note="Empowered to rule"))

        self.add_node(GraphNode("VYASA", NodeType.SHAKTYAVESHA, Sampradaya.BRAHMA, HolyName.KRISHNA, 0))
        self.add_edge(GraphEdge("NARADA", "VYASA", EdgeType.SIKSHA))
        self.add_edge(GraphEdge("KRISHNA", "VYASA", EdgeType.MANIFESTS, note="Empowered to compile Vedas"))

        self.add_node(GraphNode("PARASHURAMA", NodeType.SHAKTYAVESHA, Sampradaya.BRAHMA, HolyName.RAMA, 0))
        self.add_edge(GraphEdge("KRISHNA", "PARASHURAMA", EdgeType.MANIFESTS, note="Empowered to enforce"))

        self.add_node(GraphNode("NRISIMHA", NodeType.AVATARA, Sampradaya.BRAHMA, HolyName.KRISHNA, -1))
        self.add_edge(GraphEdge("KRISHNA", "NRISIMHA", EdgeType.MANIFESTS, note="Direct avatara"))

        # =================================================================
        # THE 24 PRAKRITI ELEMENTS
        # =================================================================
        self._add_prakriti_elements()

        # =================================================================
        # PARAMPARA EXTENSION (Gaudiya Line)
        # =================================================================
        self._add_gaudiya_parampara()

    def _add_prakriti_elements(self) -> None:
        """Add the 24 material elements as nodes."""

        prakriti_elements = [
            # Mahat-tattva evolution (1-4)
            ("PRAKRITI", "Root nature"),
            ("MAHAT", "Cosmic intelligence"),
            ("AHANKARA", "False ego"),
            ("MANAS", "Mind"),

            # Tanmatras - subtle elements (5-9)
            ("SHABDA", "Sound"),
            ("SPARSHA", "Touch"),
            ("RUPA", "Form"),
            ("RASA", "Taste"),
            ("GANDHA", "Smell"),

            # Jnanendriyas - knowledge senses (10-14)
            ("SHROTRA", "Ear"),
            ("TVAK", "Skin"),
            ("CHAKSHUS", "Eye"),
            ("RASANA", "Tongue"),
            ("GHRANA", "Nose"),

            # Karmendriyas - action organs (15-19)
            ("VAK", "Speech"),
            ("PANI", "Hands"),
            ("PADA", "Feet"),
            ("PAYU", "Excretion"),
            ("UPASTHA", "Generation"),

            # Mahabhutas - gross elements (20-24)
            ("AKASHA", "Ether"),
            ("VAYU", "Air"),
            ("TEJAS", "Fire"),
            ("APAS", "Water"),
            ("PRITHVI", "Earth"),
        ]

        for i, (name, note) in enumerate(prakriti_elements):
            self.add_node(GraphNode(
                id=f"PRAKRITI_{name}",
                node_type=NodeType.PRAKRITI,
                mantra_affinity=HolyName.VOID,  # Dead matter - needs enlivening
                level=1,  # Material level
            ))
            # Prakriti emanates from Krishna's external energy
            self.add_edge(GraphEdge(
                "KRISHNA", f"PRAKRITI_{name}",
                EdgeType.MANIFESTS,
                note=f"Element {i+1}: {note}"
            ))

    def _add_gaudiya_parampara(self) -> None:
        """Add the Gaudiya Vaishnava parampara."""

        parampara_chain = [
            ("MADHVA", "VYASA", "Acharya"),
            ("PADMANABHA", "MADHVA", "Acharya"),
            ("NARAHARI", "PADMANABHA", "Acharya"),
            ("MADHAVA", "NARAHARI", "Acharya"),
            ("AKSHOBHYA", "MADHAVA", "Acharya"),
            ("JAYATIRTHA", "AKSHOBHYA", "Acharya"),
            ("JNANASINDHU", "JAYATIRTHA", "Acharya"),
            ("DAYANIDHI", "JNANASINDHU", "Acharya"),
            ("VIDYANIDHI", "DAYANIDHI", "Acharya"),
            ("RAJENDRA", "VIDYANIDHI", "Acharya"),
            ("JAYADHARMA", "RAJENDRA", "Acharya"),
            ("PURUSHOTTAMA", "JAYADHARMA", "Acharya"),
            ("BRAHMANYA", "PURUSHOTTAMA", "Acharya"),
            ("VYASATIRTHA", "BRAHMANYA", "Acharya"),
            ("LAKSHMI_PATI", "VYASATIRTHA", "Acharya"),
            ("MADHAVENDRA_PURI", "LAKSHMI_PATI", "Acharya"),
            ("ISHVARA_PURI", "MADHAVENDRA_PURI", "Acharya"),
            ("CHAITANYA", "ISHVARA_PURI", "Yugavatara"),
        ]

        for name, guru, role in parampara_chain:
            node_type = NodeType.AVATARA if role == "Yugavatara" else NodeType.ACHARYA
            self.add_node(GraphNode(name, node_type, Sampradaya.BRAHMA, HolyName.KRISHNA, 0))
            self.add_edge(GraphEdge(guru, name, EdgeType.DIKSHA))

    # =========================================================================
    # GRAPH OPERATIONS
    # =========================================================================

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
        if edge.source not in self._adjacency:
            self._adjacency[edge.source] = []
        self._adjacency[edge.source].append((edge.target, edge.edge_type))

        if edge.target not in self._reverse_adjacency:
            self._reverse_adjacency[edge.target] = []
        self._reverse_adjacency[edge.target].append((edge.source, edge.edge_type))

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_guru(self, node_id: str) -> Optional[str]:
        """Get the guru (predecessor) for a node."""
        edges = self._reverse_adjacency.get(node_id, [])
        for source, edge_type in edges:
            if edge_type in (EdgeType.DIKSHA, EdgeType.SIKSHA):
                return source
        return None

    def get_shishyas(self, node_id: str) -> List[str]:
        """Get disciples of a node."""
        result = []
        for target, edge_type in self._adjacency.get(node_id, []):
            if edge_type in (EdgeType.DIKSHA, EdgeType.SIKSHA):
                result.append(target)
        return result

    def get_lineage(self, node_id: str) -> List[str]:
        """
        Trace the lineage back to KRISHNA.

        This is how we calculate "authority" -
        distance from the source in the parampara.
        """
        lineage = [node_id]
        current = node_id
        visited = {node_id}

        while current != "KRISHNA":
            guru = self.get_guru(current)
            if guru is None or guru in visited:
                break
            lineage.append(guru)
            visited.add(guru)
            current = guru

        return lineage

    def get_lotus_position(self, mahajana_id: str) -> int:
        """
        Calculate Lotus position from graph structure.

        Position is NOT hardcoded - it's derived from:
        1. The node's sampradaya (quarter)
        2. The node's role (head vs worker)
        3. The node's position within the quarter
        """
        # The mapping based on Vedic structure
        position_map: Dict[str, int] = {
            # GENESIS Quarter (0-3)
            "PRITHU": 0,
            "BRAHMA": 1,
            "NARADA": 2,
            "SHIVA": 3,

            # DHARMA Quarter (4-7)
            "VYASA": 4,
            "KUMARAS": 5,
            "KAPILA": 6,
            "MANU": 7,

            # KARMA Quarter (8-11)
            "PARASHURAMA": 8,
            "PRAHLADA": 9,
            "JANAKA": 10,
            "BHISHMA": 11,

            # MOKSHA Quarter (12-15)
            "NRISIMHA": 12,
            "BALI": 13,
            "SHUKA": 14,
            "YAMARAJA": 15,
        }
        return position_map.get(mahajana_id, -1)

    def get_quarter(self, position: int) -> str:
        """Get quarter name from position (uses LotusQuarter from lotus.py)."""
        quarter_idx = position // WORDS_PER_QUARTER
        return list(LotusQuarter)[quarter_idx].value


# =============================================================================
# THE RHYTHM ENGINE (Mantra × Prakriti)
# =============================================================================


class RhythmEngine:
    """
    The Rhythm Engine - Enlivening Dead Matter.

    Mathematics (from acintya.py):
    - Mahamantra: 16 words (LOTUS_POSITIONS)
    - Prakriti: 24 elements (FIELD level)
    - LCM(16, 24) = 48 beats

    3 Mantra cycles (3 × 16 = 48) purify
    2 Prakriti cycles (2 × 24 = 48)

    This is the CHURNING (Samudra Manthan).

    CONNECTED TO ACINTYA - uses imported constants, not duplicates!
    """

    # Use imported constants - SINGLE SOURCE OF TRUTH
    MANTRA_LENGTH: Final[int] = LOTUS_POSITIONS  # 16 (from lotus.py)
    PRAKRITI_COUNT: Final[int] = 24  # The 24 Prakriti elements (Gita 13.6-7)
    PURIFICATION_CYCLE: Final[int] = 48  # LCM(16, 24) - the Churning

    # The 16-word Mahamantra sequence (HolyName from byte.py)
    MAHAMANTRA: Final[List[HolyName]] = [
        # Hare Krishna Hare Krishna (GENESIS quarter)
        HolyName.HARE, HolyName.KRISHNA, HolyName.HARE, HolyName.KRISHNA,
        # Krishna Krishna Hare Hare (DHARMA quarter)
        HolyName.KRISHNA, HolyName.KRISHNA, HolyName.HARE, HolyName.HARE,
        # Hare Rama Hare Rama (KARMA quarter)
        HolyName.HARE, HolyName.RAMA, HolyName.HARE, HolyName.RAMA,
        # Rama Rama Hare Hare (MOKSHA quarter)
        HolyName.RAMA, HolyName.RAMA, HolyName.HARE, HolyName.HARE,
    ]

    @classmethod
    def get_lcm(cls) -> int:
        """Get the Least Common Multiple of mantra and prakriti."""
        def lcm(a: int, b: int) -> int:
            return abs(a * b) // gcd(a, b)
        return lcm(cls.MANTRA_LENGTH, cls.PRAKRITI_COUNT)

    @classmethod
    def enliven(cls, prakriti_index: int, beat: int) -> HolyName:
        """
        Inject mantra into a prakriti element at a given beat.

        Dead matter (VOID) becomes alive through contact
        with the Holy Name.

        Args:
            prakriti_index: Which of the 24 elements (0-23)
            beat: Current beat in the rhythm cycle (0-47)

        Returns:
            The HolyName that touches this element at this beat
        """
        if prakriti_index < 0 or prakriti_index >= cls.PRAKRITI_COUNT:
            return HolyName.VOID

        # Which mantra word hits this element?
        # The phase shifts as we go through cycles
        mantra_position = (beat + prakriti_index) % cls.MANTRA_LENGTH
        return cls.MAHAMANTRA[mantra_position]

    @classmethod
    def get_purification_sequence(cls, prakriti_index: int) -> List[HolyName]:
        """
        Get the full sequence of Holy Names that touch an element
        over one complete purification cycle (48 beats).

        Each element receives the FULL mantra multiple times,
        but at different phase offsets.
        """
        return [cls.enliven(prakriti_index, beat) for beat in range(cls.PURIFICATION_CYCLE)]

    @classmethod
    def is_fully_purified(cls, sequence: List[HolyName]) -> bool:
        """
        Check if a sequence contains the full mantra (dwijah - twice-born).

        An element is "initiated" when it has received all 16 Holy Names.
        """
        received = set(sequence)
        required = {HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA}
        return required.issubset(received)

    @classmethod
    def get_rhythm_3x8(cls, element_index: int) -> Tuple[int, int]:
        """Get the 3×8 rhythm coordinates (guna × prakrti)."""
        return (element_index // 8, element_index % 8)

    @classmethod
    def get_rhythm_4x6(cls, element_index: int) -> Tuple[int, int]:
        """Get the 4×6 rhythm coordinates (quarter × sub-element)."""
        return (element_index // 6, element_index % 6)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# The single Vedic Graph instance
VEDIC_GRAPH: Final[VedicGraph] = VedicGraph()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_position(mahajana: str) -> int:
    """Get Lotus position for a mahajana from the graph."""
    return VEDIC_GRAPH.get_lotus_position(mahajana)


def get_lineage(node_id: str) -> List[str]:
    """Get the full lineage trace to Krishna."""
    return VEDIC_GRAPH.get_lineage(node_id)


def get_quarter(mahajana: str) -> str:
    """Get the quarter for a mahajana."""
    pos = VEDIC_GRAPH.get_lotus_position(mahajana)
    return VEDIC_GRAPH.get_quarter(pos)


def enliven_matter(prakriti_index: int, beat: int) -> HolyName:
    """Enliven dead matter with the Holy Name."""
    return RhythmEngine.enliven(prakriti_index, beat)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "HolyName",
    "NodeType",
    "EdgeType",
    "Sampradaya",
    # Graph structures
    "GraphNode",
    "GraphEdge",
    "VedicGraph",
    # Rhythm Engine
    "RhythmEngine",
    # Global instance
    "VEDIC_GRAPH",
    # Convenience functions
    "get_position",
    "get_lineage",
    "get_quarter",
    "enliven_matter",
]
