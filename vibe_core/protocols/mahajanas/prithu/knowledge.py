"""
KNOWLEDGE GRAPH PROTOCOL - The Universal Knowledge Interface
=============================================================

POSITION: 4 (PRITHU - DHARMA Quarter HEAD)

The KnowledgeGraph is the universal repository of knowledge.
This protocol defines the interface - implementations live elsewhere.

DERIVED FROM MAHAMANTRA:
    Position 4 -> guardian=PRITHU, opcode=ASSERT_TRUTH, quarter=DHARMA

ANTI-MAYAVAD:
    - No Any types
    - All types explicit and WATERTIGHT
    - The protocol IS the contract, not a wrapper

OUROBOROS INTEGRATION:
    Shuddhi uses get_violations() and mark_violation_healed()
    to create the self-healing loop.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x8df5f6e7"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.mahamantra import HeadProtocol, MantraOpCode


# =============================================================================
# KNOWLEDGE GRAPH PROTOCOL BASE - Derives from MantraPosition 4
# =============================================================================


class KnowledgeGraphProtocolBase(HeadProtocol):
    """
    Knowledge Graph protocol ownership - DERIVED from Mahamantra position 4.

    NO MANUAL WIRING:
        _position_index = 4 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Avatara.PRITHU
        opcode()    -> MantraOpCode.COMPILE_AST
        quarter()   -> Quarter.DHARMA
        is_head()   -> True (HEAD position)
        parampara_vector() -> 185 (% 37 == 0)
    """

    _position_index: ClassVar[int] = 4  # THE ONLY CONFIGURATION


# =============================================================================
# NODE TYPES - WATERTIGHT (No Any!)
# =============================================================================


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""

    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    VIOLATION = "violation"
    FEATURE = "feature"
    AGENT = "agent"
    MODULE = "module"
    PACKAGE = "package"


class RelationType(str, Enum):
    """Types of relationships between nodes."""

    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    HEALED_BY = "healed_by"
    VIOLATES = "violates"


# =============================================================================
# VIOLATION NODE - WATERTIGHT (No Any!)
# =============================================================================


@dataclass
class ViolationNode:
    """
    A violation detected in the codebase.
    WATERTIGHT - explicit types only.
    """

    id: str
    file_path: str
    line: int
    column: int
    rule_id: str
    message: str
    severity: str
    healed: bool = False

    @property
    def properties(self) -> Dict[str, str | int | bool]:
        """Properties dict for compatibility."""
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity,
            "healed": self.healed,
        }


# =============================================================================
# KNOWLEDGE GRAPH PROTOCOL - The Universal Interface
# =============================================================================


@runtime_checkable
class KnowledgeGraphProtocol(Protocol):
    """
    The Universal Knowledge Graph Interface.

    DERIVED: Position 4 -> PRITHU, ASSERT_TRUTH, DHARMA

    4 Dimensions:
    - ONTOLOGY (Nodes): What exists
    - TOPOLOGY (Edges): How things relate
    - CONSTRAINTS (Rules): What is blocked
    - METRICS (Scores): How much

    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 4 in the Mahamantra."""
        ...

    # =========================================================================
    # ONTOLOGY - Nodes
    # =========================================================================

    def add_node(self, node_id: str, node_type: NodeType, properties: Dict[str, str | int | bool]) -> None:
        """Add a node to the graph."""
        ...

    def get_node(self, node_id: str) -> Optional[ViolationNode]:
        """Get a node by ID."""
        ...

    def query_nodes(
        self, node_type: NodeType, filters: Optional[Dict[str, str | int | bool]] = None
    ) -> List[ViolationNode]:
        """Query nodes by type and optional filters."""
        ...

    # =========================================================================
    # TOPOLOGY - Edges
    # =========================================================================

    def add_edge(self, source_id: str, target_id: str, relation: RelationType) -> None:
        """Add an edge between nodes."""
        ...

    def get_edges(self, node_id: str, direction: str = "outgoing") -> List[str]:
        """Get edges for a node. Direction: 'outgoing', 'incoming', 'both'."""
        ...

    # =========================================================================
    # OUROBOROS - Violation Tracking
    # =========================================================================

    def get_violations(
        self,
        rule_id: Optional[str] = None,
        healed: Optional[bool] = None,
    ) -> List[ViolationNode]:
        """
        OUROBOROS: Get violation nodes with optional filters.

        Args:
            rule_id: Filter by specific rule
            healed: Filter by healed status (True/False/None for all)

        Returns:
            List of ViolationNode objects
        """
        ...

    def mark_violation_healed(self, violation_id: str, remedy_id: str) -> None:
        """
        OUROBOROS: Mark a violation as healed and create HEALED_BY edge.

        Args:
            violation_id: The violation node ID
            remedy_id: The remedy that healed it
        """
        ...

    def add_violation(
        self,
        file_path: str,
        line: int,
        column: int,
        rule_id: str,
        message: str,
        severity: str = "MEDIUM",
    ) -> str:
        """
        Add a violation node to the graph.

        Returns:
            The violation node ID
        """
        ...

    # =========================================================================
    # LOADING
    # =========================================================================

    def load(self, knowledge_dir: Path) -> None:
        """Load knowledge from YAML files."""
        ...

    @property
    def is_loaded(self) -> bool:
        """Check if the graph has been loaded."""
        ...


# =============================================================================
# NULL KNOWLEDGE GRAPH - For testing
# =============================================================================


class NullKnowledgeGraph(KnowledgeGraphProtocolBase):
    """
    The Empty Graph - no knowledge loaded.
    Used for testing and when knowledge is not available.

    Inherits from KnowledgeGraphProtocolBase -> position 4 -> PRITHU.
    """

    def __init__(self) -> None:
        self._violations: Dict[str, ViolationNode] = {}

    def add_node(
        self, node_id: str = "", node_type: NodeType = None, properties: Dict[str, str | int | bool] = None
    ) -> None:
        pass

    def get_node(self, node_id: str = "") -> Optional[ViolationNode]:
        return self._violations.get(node_id)

    def query_nodes(
        self, node_type: NodeType = None, filters: Optional[Dict[str, str | int | bool]] = None
    ) -> List[ViolationNode]:
        return []

    def add_edge(self, source_id: str = "", target_id: str = "", relation: RelationType = None) -> None:
        pass

    def get_edges(self, node_id: str = "", direction: str = "outgoing") -> List[str]:
        return []

    def get_violations(
        self,
        rule_id: Optional[str] = None,
        healed: Optional[bool] = None,
    ) -> List[ViolationNode]:
        return []

    def mark_violation_healed(self, violation_id: str = "", remedy_id: str = "") -> None:
        if violation_id in self._violations:
            self._violations[violation_id].healed = True

    def add_violation(
        self,
        file_path: str = "",
        line: int = 0,
        column: int = 0,
        rule_id: str = "",
        message: str = "",
        severity: str = "MEDIUM",
    ) -> str:
        violation_id = f"v_{len(self._violations)}"
        self._violations[violation_id] = ViolationNode(
            id=violation_id,
            file_path=file_path,
            line=line,
            column=column,
            rule_id=rule_id,
            message=message,
            severity=severity,
        )
        return violation_id

    def load(self, knowledge_dir: Path = None) -> None:
        pass

    @property
    def is_loaded(self) -> bool:
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol Base
    "KnowledgeGraphProtocolBase",
    # Types (WATERTIGHT)
    "NodeType",
    "RelationType",
    "ViolationNode",
    # Protocol
    "KnowledgeGraphProtocol",
    # Null implementation
    "NullKnowledgeGraph",
]
