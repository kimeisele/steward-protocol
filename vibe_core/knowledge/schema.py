"""
Knowledge Graph Schema Definitions

Defines the 4 dimensions of the Unified Knowledge Graph:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""

    AGENT = "agent"
    FEATURE = "feature"
    CONCEPT = "concept"
    RULE = "rule"
    DOMAIN = "domain"


class RelationType(Enum):
    """Types of relations between nodes."""

    DEPENDS_ON = "depends_on"  # A requires B
    OVERRIDES = "overrides"  # A can override B
    IMPLIES = "implies"  # A implies B
    BLOCKS = "blocks"  # A blocks B
    HANDLES = "handles"  # Agent handles Concept
    BELONGS_TO = "belongs_to"  # Node belongs to Domain


class ConstraintType(Enum):
    """Types of constraints."""

    HARD = "hard"  # Never violate (Narasimha)
    SOFT = "soft"  # Warn but allow
    CONDITIONAL = "conditional"  # Depends on context


class ConstraintAction(Enum):
    """Actions to take when constraint is violated."""

    BLOCK = "block"
    WARN = "warn"
    REQUIRE_APPROVAL = "require_approval"


class MetricType(Enum):
    """Types of metrics."""

    AUTHORITY = "authority"  # 1-10 scale
    COMPLEXITY = "complexity"  # 1-21 Fibonacci
    PRIORITY = "priority"  # 1-10 scale
    CONFIDENCE = "confidence"  # 0.0-1.0 scale


@dataclass
class Node:
    """A node in the knowledge graph (Ontology - Sattva)."""

    id: str
    type: NodeType
    name: str
    domain: str
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """A relation between nodes (Topology - Rajas)."""

    source: str  # Node ID
    target: str  # Node ID
    relation: RelationType
    weight: float = 1.0  # Strength of relation
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Constraint:
    """A rule that blocks actions (Constraints - Tamas)."""

    id: str
    type: ConstraintType
    condition: str  # Python expression or keyword match
    action: ConstraintAction
    message: str
    applies_to: List[str] = field(default_factory=list)  # Node IDs or "*"


@dataclass
class Metric:
    """A quantitative measure (Metrics - Karma)."""

    node_id: str
    metric_type: MetricType
    value: float
    scale_min: float = 0.0
    scale_max: float = 10.0
