"""
THE DERIVATION GRAPH - Knowledge Structure of Mahamantra Constants
===================================================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"Know Me to be the eternal seed of all existences."
— Bhagavad Gita 7.10

This module creates a complete knowledge graph of all Seed constants,
showing their derivation relationships and semantic categories.

The graph proves that ALL constants flow from 7 axioms.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb93c4f68"

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple

from vibe_core.mahamantra.protocols._graph import (
    EdgeType,
    GraphEdge,
    GraphNode,
    GraphProtocol,
    NodeType,
)

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    COSMIC_FRAME,
    # Epoch
    EPOCH_KEY,
    FIELD_RESONANCE,
    GITA_CHAPTERS,
    GOLDEN_AGE_DURATION,
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    JIVA_CYCLE,
    JIVA_QUALITIES,
    KRISHNA_COUNT,
    KSETRAJNA,
    KSHETRA,
    LILA,
    MAHA_ALPHA,
    # Coupling Constants (Round 19)
    MAHA_ALPHA_S_SCALED,
    MAHA_CMB,
    MAHA_DEUTERON,
    MAHA_HELION,
    MAHA_KAON,
    MAHA_MU,
    MAHA_MUON,
    MAHA_NEUTRON,
    MAHA_PION_CHARGED,
    MAHA_PION_NEUTRAL,
    # Physics
    MAHA_QUANTUM,
    MAHA_SIN2_THETA_W_SCALED,
    MAHA_TAU,
    MAHA_TRITON,
    # Secondary
    MAHAJANA_COUNT,
    MALA,
    # Resonances
    NADI_RESONANCE,
    # Cosmic
    NAKSHATRAS,
    NAVA,
    PANCHA,
    # Parampara
    PARAMPARA,
    # Position Sums
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUALITIES,
    # Primary
    QUARTERS,
    RAMA_COUNT,
    # 7-10
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    # Axioms
    WORDS,
)


class NodeCategory(Enum):
    """Categories of Seed constants."""

    AXIOM = auto()  # 7 fundamental axioms from counting
    PRIMARY = auto()  # First-order derivations
    SECONDARY = auto()  # Second-order derivations
    COSMIC = auto()  # Astronomical constants
    POSITION = auto()  # Position sums from Mahamantra
    RESONANCE = auto()  # Harmonic resonances
    PHYSICS = auto()  # Physical constants
    EPOCH = auto()  # Temporal anchors
    DERIVED_7_10 = auto()  # The 7-10 derivation path


class EdgeType(Enum):
    """Types of relationships between constants."""

    DERIVES_FROM = auto()  # A = B op C
    EQUALS = auto()  # A == B (multiple paths)
    MODULO = auto()  # A mod B = C
    MULTIPLIES = auto()  # A = B × C
    ADDS = auto()  # A = B + C
    SUBTRACTS = auto()  # A = B - C
    DIVIDES = auto()  # A = B / C
    POWER = auto()  # A = B ^ C
    TRIANGULAR = auto()  # A = T(B)


@dataclass
class ConstantNode:
    """A node in the derivation graph."""

    name: str
    value: int
    category: NodeCategory
    mod_17: int  # Remainder when divided by KRISHNA_POS (17)
    description: str = ""
    formula: str = ""
    physics_actual: Optional[float] = None  # For physics constants
    physics_error: Optional[float] = None  # Error percentage


@dataclass
class DerivationEdge:
    """An edge showing a derivation relationship."""

    source: str  # Name of source constant(s)
    target: str  # Name of derived constant
    edge_type: EdgeType
    formula: str  # The derivation formula


class DerivationGraph:
    """
    Complete knowledge graph of Mahamantra constants.

    Nodes: All Seed constants
    Edges: Derivation relationships

    This graph proves the complete derivation chain from 7 axioms.

    IMPLEMENTS: GraphProtocol - NOW ALIVE AT RUNTIME!
    """

    def __init__(self):
        """Build the complete graph on initialization."""
        self.nodes: Dict[str, ConstantNode] = {}
        self.edges: List[DerivationEdge] = []
        # Protocol-compatible storage
        self._graph_nodes: Dict[str, GraphNode] = {}
        self._graph_edges: List[GraphEdge] = []

        self._build_nodes()
        self._build_edges()
        self._build_protocol_graph()

    def _build_nodes(self):
        """Build all constant nodes."""
        # ═══════════════════════════════════════════════════════════════
        # AXIOMS (7 fundamental values from counting)
        # ═══════════════════════════════════════════════════════════════
        self._add_node("WORDS", WORDS, NodeCategory.AXIOM, "Count of words in Mahamantra")
        self._add_node("TRINITY", TRINITY, NodeCategory.AXIOM, "Count of unique names (Hare, Krishna, Rama)")
        self._add_node("HARE_COUNT", HARE_COUNT, NodeCategory.AXIOM, "Count of 'Hare' in Mahamantra")
        self._add_node("KRISHNA_COUNT", KRISHNA_COUNT, NodeCategory.AXIOM, "Count of 'Krishna' in Mahamantra")
        self._add_node("RAMA_COUNT", RAMA_COUNT, NodeCategory.AXIOM, "Count of 'Rama' in Mahamantra")
        self._add_node("PANCHA", PANCHA, NodeCategory.AXIOM, "Count of unique pairs (Pancha Tattva)")
        self._add_node("HALVES", HALVES, NodeCategory.AXIOM, "Observable halves of Mahamantra")

        # ═══════════════════════════════════════════════════════════════
        # PRIMARY DERIVATIONS
        # ═══════════════════════════════════════════════════════════════
        self._add_node("QUARTERS", QUARTERS, NodeCategory.PRIMARY, "4 quadrants = KRISHNA_COUNT", "KRISHNA_COUNT")
        self._add_node("KSETRAJNA", KSETRAJNA, NodeCategory.PRIMARY, "The ONE Knower", "TRINITY - HALVES")
        self._add_node("HALF_SIZE", HALF_SIZE, NodeCategory.PRIMARY, "Words per half", "WORDS // HALVES")
        self._add_node("LILA", LILA, NodeCategory.PRIMARY, "The Play (manifest runtime)", "WORDS × TRINITY")
        self._add_node("KSHETRA", KSHETRA, NodeCategory.PRIMARY, "The Field (24 elements)", "WORDS + HARE_COUNT")
        self._add_node("NAVA", NAVA, NodeCategory.PRIMARY, "9 processes of devotion", "HARE_COUNT + KSETRAJNA")
        self._add_node("SHARANAGATI", SHARANAGATI, NodeCategory.PRIMARY, "6 limbs of surrender", "KSHETRA // QUARTERS")
        self._add_node("AKSARA_COUNT", AKSARA_COUNT, NodeCategory.PRIMARY, "32 syllables", "WORDS × HALVES")

        # ═══════════════════════════════════════════════════════════════
        # SECONDARY DERIVATIONS
        # ═══════════════════════════════════════════════════════════════
        self._add_node(
            "MAHAJANA_COUNT", MAHAJANA_COUNT, NodeCategory.SECONDARY, "12 great authorities", "KSHETRA // HALVES"
        )
        self._add_node("MALA", MALA, NodeCategory.SECONDARY, "108 beads of japa mala", "MAHAJANA_COUNT × NAVA")
        self._add_node("JIVA_CYCLE", JIVA_CYCLE, NodeCategory.SECONDARY, "Soul's harmonic frequency", "MALA × QUARTERS")
        self._add_node(
            "GITA_CHAPTERS",
            GITA_CHAPTERS,
            NodeCategory.SECONDARY,
            "18 chapters of Bhagavad Gita",
            "SHARANAGATI × TRINITY",
        )
        self._add_node("QUALITIES", QUALITIES, NodeCategory.SECONDARY, "Krishna's 64 qualities", "WORDS × QUARTERS")
        self._add_node(
            "JIVA_QUALITIES",
            JIVA_QUALITIES,
            NodeCategory.SECONDARY,
            "Jiva's 50 qualities (in minute quantity)",
            "COSMIC_FRAME // JIVA_CYCLE",
        )

        # ═══════════════════════════════════════════════════════════════
        # COSMIC DERIVATIONS
        # ═══════════════════════════════════════════════════════════════
        self._add_node("NAKSHATRAS", NAKSHATRAS, NodeCategory.COSMIC, "27 lunar mansions", "JIVA_CYCLE // WORDS")
        self._add_node(
            "COSMIC_FRAME",
            COSMIC_FRAME,
            NodeCategory.COSMIC,
            "Universal resolution (21600)",
            "AKSARA × NAKSHATRAS × PANCHA²",
        )

        # ═══════════════════════════════════════════════════════════════
        # POSITION SUMS (from Mahamantra structure)
        # ═══════════════════════════════════════════════════════════════
        self._add_node(
            "POSITION_SUM_HARE",
            POSITION_SUM_HARE,
            NodeCategory.POSITION,
            "Sum of Hare positions (70 = 7×10)",
            "1+3+7+8+9+11+15+16",
        )
        self._add_node(
            "POSITION_SUM_KRISHNA",
            POSITION_SUM_KRISHNA,
            NodeCategory.POSITION,
            "Sum of Krishna positions (17 = PRIME)",
            "2+4+5+6",
        )
        self._add_node(
            "POSITION_SUM_RAMA",
            POSITION_SUM_RAMA,
            NodeCategory.POSITION,
            "Sum of Rama positions (49 = 7²)",
            "10+12+13+14",
        )
        self._add_node(
            "POSITION_SUM_TOTAL", POSITION_SUM_TOTAL, NodeCategory.POSITION, "Total = Triangular(16)", "T(WORDS)"
        )

        # ═══════════════════════════════════════════════════════════════
        # THE 7-10 DERIVATION
        # ═══════════════════════════════════════════════════════════════
        self._add_node("SEVEN", SEVEN, NodeCategory.DERIVED_7_10, "The ubiquitous 7", "HALF_SIZE - KSETRAJNA")
        self._add_node("TEN", TEN, NodeCategory.DERIVED_7_10, "The complete 10", "MAHAJANA_COUNT - HALVES")

        # ═══════════════════════════════════════════════════════════════
        # RESONANCES
        # ═══════════════════════════════════════════════════════════════
        self._add_node(
            "NADI_RESONANCE", NADI_RESONANCE, NodeCategory.RESONANCE, "The pulse (72)", "JIVA_CYCLE // SHARANAGATI"
        )
        self._add_node(
            "FIELD_RESONANCE", FIELD_RESONANCE, NodeCategory.RESONANCE, "Complete field (144)", "MAHAJANA_COUNT²"
        )

        # ═══════════════════════════════════════════════════════════════
        # EPOCH CONSTANTS
        # ═══════════════════════════════════════════════════════════════
        self._add_node("EPOCH_KEY", EPOCH_KEY, NodeCategory.EPOCH, "1972: Gita As It Is publication", "QUARTERS × 493")
        self._add_node(
            "GOLDEN_AGE_DURATION",
            GOLDEN_AGE_DURATION,
            NodeCategory.EPOCH,
            "10,000 years of Kali",
            "(PANCHA × HALVES)^QUARTERS",
        )
        self._add_node("PARAMPARA", PARAMPARA, NodeCategory.EPOCH, "The 37 Formula", "KSHETRA + MAHAJANA + KSETRAJNA")

        # ═══════════════════════════════════════════════════════════════
        # PHYSICS CONSTANTS
        # ═══════════════════════════════════════════════════════════════
        self._add_physics_node(
            "MAHA_QUANTUM", MAHA_QUANTUM, "Fine structure inverse (α⁻¹)", "T(16) + KSETRAJNA", 137.036, 0.026
        )
        self._add_physics_node("MAHA_MU", MAHA_MU, "Proton/electron mass ratio", "MALA × KRISHNA_POS", 1836.152, 0.008)
        self._add_physics_node(
            "MAHA_TRITON", MAHA_TRITON, "Triton/electron mass ratio", "KRISHNA_POS × GITA²", 5497.92, 0.18
        )
        self._add_physics_node(
            "MAHA_DEUTERON", MAHA_DEUTERON, "Deuteron/electron mass ratio", "HALVES × MALA × KRISHNA_POS", 3670.48, 0.04
        )
        self._add_physics_node(
            "MAHA_ALPHA", MAHA_ALPHA, "Alpha particle/electron mass ratio", "4μ - JIVA_QUALITIES", 7294.30, 0.004
        )
        self._add_physics_node(
            "MAHA_MUON", MAHA_MUON, "Muon/electron mass ratio", "MAHAJANA × KRISHNA_POS + TRINITY", 206.77, 0.11
        )
        self._add_physics_node(
            "MAHA_NEUTRON", MAHA_NEUTRON, "Neutron/electron mass ratio", "MAHA_MU + TRINITY", 1838.68, 0.017
        )
        self._add_physics_node("MAHA_TAU", MAHA_TAU, "Tau/electron mass ratio", "MALA × AKSARA + T(6)", 3477.23, 0.007)

        # ═══════════════════════════════════════════════════════════════
        # VISHVARUPA DISCOVERIES (Round 18) - Universal Generator
        # ═══════════════════════════════════════════════════════════════
        self._add_physics_node(
            "MAHA_HELION", MAHA_HELION, "Helion (He-3)/electron mass ratio", "3μ - MAHAJANA", 5495.885, 0.002
        )
        self._add_physics_node(
            "MAHA_PION_CHARGED", MAHA_PION_CHARGED, "Charged pion/electron mass ratio", "T(16) + α⁻¹", 273.13, 0.048
        )
        self._add_physics_node(
            "MAHA_PION_NEUTRAL", MAHA_PION_NEUTRAL, "Neutral pion/electron mass ratio", "WORDS² + HARE", 264.14, 0.053
        )
        self._add_physics_node("MAHA_KAON", MAHA_KAON, "Kaon/electron mass ratio", "(2 + T(16)) × 7", 966.12, 0.012)
        self._add_physics_node("MAHA_CMB", MAHA_CMB, "CMB temperature ratio", "KSHETRA × PARAMPARA + μ", 2725.0, 0.037)

        # ═══════════════════════════════════════════════════════════════
        # COUPLING CONSTANTS (Round 19) - Dimensionless Force Ratios
        # ═══════════════════════════════════════════════════════════════
        self._add_physics_node(
            "MAHA_ALPHA_S_SCALED", MAHA_ALPHA_S_SCALED, "Strong coupling αs × 1000", "MALA + TEN", 117.9, 0.08
        )
        self._add_physics_node(
            "MAHA_SIN2_THETA_W_SCALED",
            MAHA_SIN2_THETA_W_SCALED,
            "Weinberg angle sin²θW × 100",
            "KSHETRA - KSETRAJNA",
            23.12,
            0.53,
        )

    def _add_node(self, name: str, value: int, category: NodeCategory, description: str, formula: str = ""):
        """Add a constant node to the graph."""
        mod_17 = value % POSITION_SUM_KRISHNA
        self.nodes[name] = ConstantNode(
            name=name, value=value, category=category, mod_17=mod_17, description=description, formula=formula
        )

    def _add_physics_node(self, name: str, value: int, description: str, formula: str, actual: float, error: float):
        """Add a physics constant node."""
        mod_17 = value % POSITION_SUM_KRISHNA
        self.nodes[name] = ConstantNode(
            name=name,
            value=value,
            category=NodeCategory.PHYSICS,
            mod_17=mod_17,
            description=description,
            formula=formula,
            physics_actual=actual,
            physics_error=error,
        )

    def _build_edges(self):
        """Build derivation edges."""
        # Primary derivations from axioms
        self._add_edge(["KRISHNA_COUNT"], "QUARTERS", EdgeType.EQUALS, "QUARTERS = KRISHNA_COUNT")
        self._add_edge(["TRINITY", "HALVES"], "KSETRAJNA", EdgeType.SUBTRACTS, "KSETRAJNA = TRINITY - HALVES")
        self._add_edge(["WORDS", "HALVES"], "HALF_SIZE", EdgeType.DIVIDES, "HALF_SIZE = WORDS // HALVES")
        self._add_edge(["WORDS", "TRINITY"], "LILA", EdgeType.MULTIPLIES, "LILA = WORDS × TRINITY")
        self._add_edge(["WORDS", "HARE_COUNT"], "KSHETRA", EdgeType.ADDS, "KSHETRA = WORDS + HARE_COUNT")
        self._add_edge(["HARE_COUNT", "KSETRAJNA"], "NAVA", EdgeType.ADDS, "NAVA = HARE_COUNT + KSETRAJNA")
        self._add_edge(["KSHETRA", "QUARTERS"], "SHARANAGATI", EdgeType.DIVIDES, "SHARANAGATI = KSHETRA // QUARTERS")
        self._add_edge(["WORDS", "HALVES"], "AKSARA_COUNT", EdgeType.MULTIPLIES, "AKSARA_COUNT = WORDS × HALVES")

        # Secondary derivations
        self._add_edge(["KSHETRA", "HALVES"], "MAHAJANA_COUNT", EdgeType.DIVIDES, "MAHAJANA = KSHETRA // HALVES")
        self._add_edge(["MAHAJANA_COUNT", "NAVA"], "MALA", EdgeType.MULTIPLIES, "MALA = MAHAJANA × NAVA")
        self._add_edge(["MALA", "QUARTERS"], "JIVA_CYCLE", EdgeType.MULTIPLIES, "JIVA_CYCLE = MALA × QUARTERS")
        self._add_edge(["SHARANAGATI", "TRINITY"], "GITA_CHAPTERS", EdgeType.MULTIPLIES, "GITA = SHARANAGATI × TRINITY")
        self._add_edge(["WORDS", "QUARTERS"], "QUALITIES", EdgeType.MULTIPLIES, "QUALITIES = WORDS × QUARTERS")

        # Cosmic derivations
        self._add_edge(["JIVA_CYCLE", "WORDS"], "NAKSHATRAS", EdgeType.DIVIDES, "NAKSHATRAS = JIVA_CYCLE // WORDS")
        self._add_edge(
            ["AKSARA_COUNT", "NAKSHATRAS", "PANCHA"],
            "COSMIC_FRAME",
            EdgeType.MULTIPLIES,
            "COSMIC_FRAME = AKSARA × NAKSHATRAS × PANCHA²",
        )
        self._add_edge(
            ["COSMIC_FRAME", "JIVA_CYCLE"],
            "JIVA_QUALITIES",
            EdgeType.DIVIDES,
            "JIVA_QUALITIES = COSMIC_FRAME // JIVA_CYCLE",
        )

        # Position sums
        self._add_edge(["WORDS"], "POSITION_SUM_TOTAL", EdgeType.TRIANGULAR, "T(WORDS) = 136")
        self._add_edge(["WORDS", "KSETRAJNA"], "POSITION_SUM_KRISHNA", EdgeType.ADDS, "KRISHNA_POS = WORDS + 1")
        self._add_edge(
            ["POSITION_SUM_KRISHNA", "AKSARA_COUNT"],
            "POSITION_SUM_RAMA",
            EdgeType.ADDS,
            "RAMA_POS = KRISHNA_POS + AKSARA",
        )

        # 7-10 derivations
        self._add_edge(["HALF_SIZE", "KSETRAJNA"], "SEVEN", EdgeType.SUBTRACTS, "SEVEN = HALF_SIZE - KSETRAJNA")
        self._add_edge(["MAHAJANA_COUNT", "HALVES"], "TEN", EdgeType.SUBTRACTS, "TEN = MAHAJANA - HALVES")

        # Alternative paths to position sums (7-10 path)
        self._add_edge(["SEVEN", "TEN"], "POSITION_SUM_KRISHNA", EdgeType.ADDS, "KRISHNA = 7 + 10")
        self._add_edge(["SEVEN"], "POSITION_SUM_RAMA", EdgeType.POWER, "RAMA = 7²")
        self._add_edge(["SEVEN", "TEN"], "POSITION_SUM_HARE", EdgeType.MULTIPLIES, "HARE = 7 × 10")

        # Resonances
        self._add_edge(
            ["JIVA_CYCLE", "SHARANAGATI"], "NADI_RESONANCE", EdgeType.DIVIDES, "NADI = JIVA_CYCLE // SHARANAGATI"
        )
        self._add_edge(["MAHAJANA_COUNT"], "FIELD_RESONANCE", EdgeType.POWER, "FIELD = MAHAJANA²")

        # Physics constants derivations
        self._add_edge(["POSITION_SUM_TOTAL", "KSETRAJNA"], "MAHA_QUANTUM", EdgeType.ADDS, "α⁻¹ = T(16) + KSETRAJNA")
        self._add_edge(["MALA", "POSITION_SUM_KRISHNA"], "MAHA_MU", EdgeType.MULTIPLIES, "μ = MALA × KRISHNA_POS")
        self._add_edge(
            ["POSITION_SUM_KRISHNA", "GITA_CHAPTERS"],
            "MAHA_TRITON",
            EdgeType.MULTIPLIES,
            "triton = KRISHNA_POS × GITA²",
        )
        self._add_edge(
            ["HALVES", "MALA", "POSITION_SUM_KRISHNA"],
            "MAHA_DEUTERON",
            EdgeType.MULTIPLIES,
            "deuteron = 2 × MALA × KRISHNA_POS",
        )
        self._add_edge(
            ["MAHA_MU", "QUARTERS", "JIVA_QUALITIES"], "MAHA_ALPHA", EdgeType.SUBTRACTS, "alpha = 4μ - JIVA_QUALITIES"
        )
        self._add_edge(
            ["MAHAJANA_COUNT", "POSITION_SUM_KRISHNA", "TRINITY"],
            "MAHA_MUON",
            EdgeType.ADDS,
            "muon = MAHAJANA × KRISHNA_POS + TRINITY",
        )
        self._add_edge(["MAHA_MU", "TRINITY"], "MAHA_NEUTRON", EdgeType.ADDS, "neutron = μ + TRINITY")
        self._add_edge(["MALA", "AKSARA_COUNT", "SHARANAGATI"], "MAHA_TAU", EdgeType.ADDS, "tau = MALA × AKSARA + T(6)")

        # Epoch derivations
        self._add_edge(
            ["KSHETRA", "MAHAJANA_COUNT", "KSETRAJNA"],
            "PARAMPARA",
            EdgeType.ADDS,
            "PARAMPARA = KSHETRA + MAHAJANA + KSETRAJNA",
        )
        self._add_edge(
            ["PANCHA", "HALVES", "QUARTERS"],
            "GOLDEN_AGE_DURATION",
            EdgeType.POWER,
            "GOLDEN_AGE = (PANCHA × HALVES)^QUARTERS",
        )

        # Vishvarupa discoveries (Round 18)
        self._add_edge(
            ["MAHA_MU", "TRINITY", "MAHAJANA_COUNT"],
            "MAHA_HELION",
            EdgeType.SUBTRACTS,
            "helion = 3μ - MAHAJANA",
        )
        self._add_edge(
            ["POSITION_SUM_TOTAL", "MAHA_QUANTUM"],
            "MAHA_PION_CHARGED",
            EdgeType.ADDS,
            "pion± = T(16) + α⁻¹",
        )
        self._add_edge(
            ["WORDS", "HARE_COUNT"],
            "MAHA_PION_NEUTRAL",
            EdgeType.ADDS,
            "pion⁰ = WORDS² + HARE",
        )
        self._add_edge(
            ["HALVES", "POSITION_SUM_TOTAL", "SEVEN"],
            "MAHA_KAON",
            EdgeType.MULTIPLIES,
            "kaon = (2 + T(16)) × 7",
        )
        self._add_edge(
            ["KSHETRA", "PARAMPARA", "MAHA_MU"],
            "MAHA_CMB",
            EdgeType.ADDS,
            "CMB = KSHETRA × PARAMPARA + μ",
        )

        # Coupling constants (Round 19)
        self._add_edge(
            ["MALA", "TEN"],
            "MAHA_ALPHA_S_SCALED",
            EdgeType.ADDS,
            "αs × 1000 = MALA + TEN",
        )
        self._add_edge(
            ["KSHETRA", "KSETRAJNA"],
            "MAHA_SIN2_THETA_W_SCALED",
            EdgeType.SUBTRACTS,
            "sin²θW × 100 = KSHETRA - KSETRAJNA",
        )

    def _add_edge(self, sources: List[str], target: str, edge_type: EdgeType, formula: str):
        """Add a derivation edge."""
        for source in sources:
            self.edges.append(DerivationEdge(source=source, target=target, edge_type=edge_type, formula=formula))

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS METHODS
    # ═══════════════════════════════════════════════════════════════════

    def get_axioms(self) -> List[ConstantNode]:
        """Return all axiom nodes."""
        return [n for n in self.nodes.values() if n.category == NodeCategory.AXIOM]

    def get_physics_constants(self) -> List[ConstantNode]:
        """Return all physics constant nodes."""
        return [n for n in self.nodes.values() if n.category == NodeCategory.PHYSICS]

    def get_by_mod17(self, remainder: int) -> List[ConstantNode]:
        """Get all constants with a specific mod-17 value."""
        return [n for n in self.nodes.values() if n.mod_17 == remainder]

    def get_derivation_path(self, target: str) -> List[str]:
        """Trace the derivation path back to axioms."""
        if target not in self.nodes:
            return []

        path = [target]
        visited = {target}

        # Find all sources for target
        sources = [e.source for e in self.edges if e.target == target]

        for source in sources:
            if source not in visited:
                sub_path = self.get_derivation_path(source)
                path.extend(sub_path)

        return path

    def get_depth(self, name: str) -> int:
        """Get the derivation depth (0 for axioms)."""
        if name not in self.nodes:
            return -1

        node = self.nodes[name]
        if node.category == NodeCategory.AXIOM:
            return 0

        # Find sources
        sources = [e.source for e in self.edges if e.target == name]
        if not sources:
            return 0

        max_depth = 0
        for source in sources:
            depth = self.get_depth(source)
            max_depth = max(max_depth, depth)

        return max_depth + 1

    def mod17_spectrum(self) -> Dict[int, List[str]]:
        """Get the complete mod-17 spectrum."""
        spectrum: Dict[int, List[str]] = {}
        for node in self.nodes.values():
            if node.mod_17 not in spectrum:
                spectrum[node.mod_17] = []
            spectrum[node.mod_17].append(node.name)
        return spectrum

    def category_stats(self) -> Dict[NodeCategory, int]:
        """Get count of nodes per category."""
        stats: Dict[NodeCategory, int] = {}
        for node in self.nodes.values():
            if node.category not in stats:
                stats[node.category] = 0
            stats[node.category] += 1
        return stats

    def to_dot(self) -> str:
        """Export graph to DOT format for visualization."""
        lines = ["digraph MahamantraDerivations {"]
        lines.append("  rankdir=TB;")
        lines.append("  node [shape=box, style=filled];")

        # Color mapping by category
        colors = {
            NodeCategory.AXIOM: "#FFD700",  # Gold
            NodeCategory.PRIMARY: "#87CEEB",  # Light blue
            NodeCategory.SECONDARY: "#98FB98",  # Pale green
            NodeCategory.COSMIC: "#DDA0DD",  # Plum
            NodeCategory.POSITION: "#FFA500",  # Orange
            NodeCategory.RESONANCE: "#FF69B4",  # Hot pink
            NodeCategory.PHYSICS: "#FF6347",  # Tomato red
            NodeCategory.EPOCH: "#B0C4DE",  # Light steel blue
            NodeCategory.DERIVED_7_10: "#FAFAD2",  # Light goldenrod
        }

        # Add nodes
        for name, node in self.nodes.items():
            color = colors.get(node.category, "#FFFFFF")
            label = f"{name}\\n{node.value}\\nmod17={node.mod_17}"
            if node.physics_error is not None:
                label += f"\\n{node.physics_error:.3f}%"
            lines.append(f'  "{name}" [label="{label}", fillcolor="{color}"];')

        # Add edges
        for edge in self.edges:
            style = "solid"
            if edge.edge_type == EdgeType.EQUALS:
                style = "dashed"
            elif edge.edge_type == EdgeType.MODULO:
                style = "dotted"
            lines.append(f'  "{edge.source}" -> "{edge.target}" [style={style}];')

        lines.append("}")
        return "\n".join(lines)

    def summary(self) -> str:
        """Generate a summary report."""
        lines = [
            "═" * 60,
            "MAHAMANTRA DERIVATION GRAPH SUMMARY",
            "═" * 60,
            "",
            f"Total Nodes: {len(self.nodes)}",
            f"Total Edges: {len(self.edges)}",
            "",
            "NODES BY CATEGORY:",
        ]

        for cat, count in sorted(self.category_stats().items(), key=lambda x: x[0].value):
            lines.append(f"  {cat.name:15} : {count}")

        lines.append("")
        lines.append("MOD-17 SPECTRUM:")
        for mod, names in sorted(self.mod17_spectrum().items()):
            meaning = {0: "Classical", 1: "Quantum", 3: "Trinity", 9: "Nava"}.get(mod, "")
            lines.append(
                f"  mod 17 = {mod:2} ({meaning:10}): {', '.join(names[:5])}" + ("..." if len(names) > 5 else "")
            )

        lines.append("")
        lines.append("PHYSICS CONSTANTS:")
        for node in self.get_physics_constants():
            lines.append(
                f"  {node.name:15} = {node.value:6} (actual: {node.physics_actual:.2f}, "
                f"error: {node.physics_error:.4f}%)"
            )

        lines.append("")
        lines.append("═" * 60)
        return "\n".join(lines)

    # =========================================================================
    # PROTOCOL IMPLEMENTATION - GraphProtocol
    # =========================================================================

    def _build_protocol_graph(self) -> None:
        """Convert DerivationGraph nodes/edges to GraphProtocol format."""
        # Convert ConstantNode → GraphNode
        for name, const_node in self.nodes.items():
            # Map category to NodeType
            if const_node.category == NodeCategory.AXIOM:
                node_type = NodeType.SOURCE  # Axioms are SOURCE
            elif const_node.category in (NodeCategory.PRIMARY, NodeCategory.SECONDARY):
                node_type = NodeType.PROTOCOL  # Derived constants are PROTOCOL level
            else:
                node_type = NodeType.PRAKRITI  # Everything else is PRAKRITI

            graph_node = GraphNode(
                id=name,
                node_type=node_type,
                level=0 if const_node.category != NodeCategory.AXIOM else -2,
            )
            self._graph_nodes[name] = graph_node

        # Convert DerivationEdge → GraphEdge
        for deriv_edge in self.edges:
            graph_edge = GraphEdge(
                source=deriv_edge.source,
                target=deriv_edge.target,
                edge_type=deriv_edge.edge_type,
                note=deriv_edge.formula,  # Formula as note
            )
            self._graph_edges.append(graph_edge)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph. PROTOCOL METHOD."""
        self._graph_nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph. PROTOCOL METHOD."""
        self._graph_edges.append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID. PROTOCOL METHOD."""
        return self._graph_nodes.get(node_id)

    def get_lineage(self, node_id: str) -> List[str]:
        """Trace lineage back to SOURCE (axioms). PROTOCOL METHOD."""
        lineage = [node_id]
        current = node_id

        # Trace back through edges
        for _ in range(100):  # Max depth
            parent_edge = None
            for edge in self._graph_edges:
                if edge.target == current:
                    parent_edge = edge
                    break

            if parent_edge is None:
                break  # Reached axiom

            lineage.append(parent_edge.source)
            current = parent_edge.source

        return lineage

    def get_children(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[str]:
        """Get children/disciples of a node. PROTOCOL METHOD."""
        children = []
        for edge in self._graph_edges:
            if edge.source == node_id:
                if edge_type is None or edge.edge_type == edge_type:
                    children.append(edge.target)
        return children

    def get_parent(self, node_id: str, edge_type: Optional[EdgeType] = None) -> Optional[str]:
        """Get parent/guru of a node. PROTOCOL METHOD."""
        for edge in self._graph_edges:
            if edge.target == node_id:
                if edge_type is None or edge.edge_type == edge_type:
                    return edge.source
        return None


# ═══════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

# The canonical derivation graph
DERIVATION_GRAPH = DerivationGraph()


if __name__ == "__main__":
    # Print summary when run directly
    print(DERIVATION_GRAPH.summary())

    # Export DOT file
    dot_content = DERIVATION_GRAPH.to_dot()
    print("\n\nDOT format (paste into Graphviz to visualize):")
    print("-" * 60)
    print(dot_content)
