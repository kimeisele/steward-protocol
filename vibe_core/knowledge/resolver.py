"""
Knowledge Resolver

High-level interface for agents to query knowledge.
Provides semantic queries that map to graph operations.
"""

import logging
from typing import Any, Dict, List, Optional

from .graph import get_knowledge_graph, UnifiedKnowledgeGraph
from .schema import MetricType, NodeType, RelationType

logger = logging.getLogger("KNOWLEDGE_RESOLVER")


class KnowledgeResolver:
    """
    High-level interface for agents to query knowledge.
    Provides semantic queries that map to graph operations.
    """

    def __init__(self, graph: Optional[UnifiedKnowledgeGraph] = None):
        self.graph = graph or get_knowledge_graph()

    # ═══════════════════════════════════════════════════════════════════
    # AGENT QUERIES
    # ═══════════════════════════════════════════════════════════════════

    def get_agent_for_concept(self, concept: str) -> Optional[str]:
        """Which agent handles this concept?"""
        agents = self.graph.get_nodes_by_type(NodeType.AGENT)

        for agent in agents:
            edges = self.graph.get_edges(agent.id, RelationType.HANDLES)
            for edge in edges:
                target_node = self.graph.get_node(edge.target)
                if target_node and concept.lower() in target_node.name.lower():
                    return agent.id

        return None

    def get_agent_authority(self, agent_id: str) -> int:
        """Get authority level for an agent (1-10)."""
        authority = self.graph.get_metric(agent_id, MetricType.AUTHORITY)
        return int(authority) if authority else 5

    def can_agent_override(self, agent_a: str, agent_b: str) -> bool:
        """Can agent A override agent B?"""
        auth_a = self.get_agent_authority(agent_a)
        auth_b = self.get_agent_authority(agent_b)
        return auth_a > auth_b

    def get_agents_by_authority(self, min_authority: int = 0) -> List[str]:
        """Get agents with at least min_authority level."""
        agents = self.graph.get_nodes_by_type(NodeType.AGENT)
        result = []

        for agent in agents:
            auth = self.get_agent_authority(agent.id)
            if auth >= min_authority:
                result.append(agent.id)

        return self.graph.rank_by_metric(result, MetricType.AUTHORITY, descending=True)

    # ═══════════════════════════════════════════════════════════════════
    # TASK QUERIES
    # ═══════════════════════════════════════════════════════════════════

    def get_dependencies(self, feature_id: str, depth: int = 2) -> List[str]:
        """Get all dependencies for a feature."""
        deps = self.graph.traverse(feature_id, RelationType.DEPENDS_ON, depth)
        return list(deps.keys())

    def get_complexity(self, feature_id: str) -> int:
        """Get complexity score for a feature."""
        complexity = self.graph.get_metric(feature_id, MetricType.COMPLEXITY)
        return int(complexity) if complexity else 5

    def estimate_total_complexity(self, feature_ids: List[str]) -> int:
        """Estimate total complexity including dependencies."""
        all_features = set(feature_ids)

        for fid in feature_ids:
            deps = self.get_dependencies(fid)
            all_features.update(deps)

        total = sum(self.get_complexity(f) for f in all_features)
        return total

    # ═══════════════════════════════════════════════════════════════════
    # CONSTRAINT QUERIES
    # ═══════════════════════════════════════════════════════════════════

    def is_action_allowed(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if action is allowed."""
        return self.graph.is_allowed(action, context)

    def get_violations(self, action: str, context: Dict[str, Any]) -> List[str]:
        """Get list of constraint violation messages."""
        violations = self.graph.check_constraints(action, context)
        return [v.message for v in violations]

    def get_blocked_features(self, scope: str = "v1.0") -> List[str]:
        """Get features that are blocked for a scope."""
        blocked = []
        features = self.graph.get_nodes_by_type(NodeType.FEATURE)

        for feature in features:
            constraints = self.graph.get_constraints(feature.id)
            for c in constraints:
                if scope in c.condition:
                    blocked.append(feature.id)
                    break

        return blocked

    # ═══════════════════════════════════════════════════════════════════
    # PROMPT COMPILATION
    # ═══════════════════════════════════════════════════════════════════

    def compile_context(self, task: str, max_nodes: int = 10) -> str:
        """
        Compile relevant knowledge into prompt context.
        ATOMIC: Only includes relevant nodes.
        """
        return self.graph.compile_prompt_context(task)

    def get_response_template(self, concept: str) -> Optional[str]:
        """Get a response template for a concept if one exists."""
        nodes = self.graph.search_nodes(concept)
        for node in nodes:
            if "template" in node.properties:
                return node.properties["template"]
        return None


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def get_resolver() -> KnowledgeResolver:
    """Get a KnowledgeResolver instance."""
    return KnowledgeResolver()
