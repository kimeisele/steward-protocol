"""
Unified Knowledge Graph Module

4 Dimensions:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much
"""

from .graph import UnifiedKnowledgeGraph, get_knowledge_graph
from .resolver import KnowledgeResolver, get_resolver
from .schema import (
    Node, Edge, Constraint, Metric,
    NodeType, RelationType, ConstraintType, ConstraintAction, MetricType
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
