"""
Unified Knowledge Graph Module

4 Dimensions:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xbf2d6e32"  # GenesisByte: parampara % 37 == 0

from .graph import UnifiedKnowledgeGraph, get_knowledge_graph
from .resolver import KnowledgeResolver, get_resolver
from .schema import (
    Constraint,
    ConstraintAction,
    ConstraintType,
    Edge,
    Metric,
    MetricType,
    Node,
    NodeType,
    RelationType,
)

__all__ = [
    # Main classes
    "UnifiedKnowledgeGraph",
    "KnowledgeResolver",
    # Factory functions
    "get_knowledge_graph",
    "get_resolver",
    # Schema types
    "Node",
    "Edge",
    "Constraint",
    "Metric",
    # Enums
    "NodeType",
    "RelationType",
    "ConstraintType",
    "ConstraintAction",
    "MetricType",
]
