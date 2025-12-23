"""
Unified Knowledge Graph Implementation

The Universal Knowledge Graph with 4 Dimensions:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much

Query Pattern:
- Atomic: Return only relevant nodes, not entire files
- Graph-based: Traverse relations, not dump contents
- Deterministic: No ML, no embeddings, pure logic
"""

import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

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

logger = logging.getLogger("KNOWLEDGE_GRAPH")


class UnifiedKnowledgeGraph:
    """
    The Universal Knowledge Graph.

    4 Dimensions:
    - ONTOLOGY (Nodes): What exists
    - TOPOLOGY (Edges): How things relate
    - CONSTRAINTS (Rules): What is blocked
    - METRICS (Scores): How much
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}  # source_id -> [edges]
        self.constraints: Dict[str, Constraint] = {}
        self.metrics: Dict[str, Dict[MetricType, Metric]] = {}  # node_id -> {type: metric}
        self._loaded = False

    # ═══════════════════════════════════════════════════════════════════
    # LOADING
    # ═══════════════════════════════════════════════════════════════════

    def load(self, knowledge_dir: Path) -> None:
        """Load all knowledge from YAML files using Unified Loader strategy."""
        from vibe_core.loaders.knowledge_loader import KnowledgeLoader

        # In Unified Loader world, we scan the paths
        # We can either use discover_and_load() or manually invoke if we want strict control

        # Force a scan of the provided directory
        items, metadata = KnowledgeLoader.discover_and_load(scan_paths=[knowledge_dir], force_refresh=True)

        # Populate the graph from the loaded items
        self._populate_from_items(items, metadata)

        self._loaded = True
        logger.info(
            f"Knowledge graph loaded: {len(self.nodes)} nodes, "
            f"{sum(len(e) for e in self.edges.values())} edges, "
            f"{len(self.constraints)} constraints"
        )

    def _populate_from_items(self, items: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """Populate graph structures from loaded raw items."""
        for item_id, data in items.items():
            meta = metadata.get(item_id)
            domain = meta.domain if meta else "core"

            # Delegate to specialized loaders (which we can keep as methods on the graph or helpers)
            # Determine file type by content - logic moved from legacy loader
            if "nodes" in data or "agents" in data or "features" in data:
                self._load_nodes(data, domain)

            if "edges" in data or "relations" in data or "dependencies" in data:
                self._load_edges(data)

            if "constraints" in data or "rules" in data:
                self._load_constraints(data)

            if "metrics" in data or "scores" in data or "authority" in data:
                self._load_metrics(data)

    # ═══════════════════════════════════════════════════════════════════
    # LEGACY LOAD HELPERS (Ported from legacy loader to live on Graph)
    # ═══════════════════════════════════════════════════════════════════

    def _load_nodes(self, data: dict, domain: str) -> None:
        """Load nodes from data."""
        nodes_data = data.get("nodes") or data.get("agents") or data.get("features") or []

        for node_data in nodes_data:
            node_type = NodeType(node_data.get("type", "concept"))
            node = Node(
                id=node_data["id"],
                type=node_type,
                name=node_data.get("name", node_data["id"]),
                domain=node_data.get("domain", domain),
                description=node_data.get("description", ""),
                properties=node_data.get("properties", {}),
            )
            self.nodes[node.id] = node

    def _load_edges(self, data: dict) -> None:
        """Load edges from data."""
        edges_data = data.get("edges") or data.get("relations") or data.get("dependencies") or []

        for edge_data in edges_data:
            if not isinstance(edge_data, dict):
                # Skip invalid edge data (e.g. strings in dependencies list)
                continue

            relation = RelationType(edge_data.get("relation", "depends_on"))
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                relation=relation,
                weight=edge_data.get("weight", 1.0),
                properties=edge_data.get("properties", {}),
            )

            if edge.source not in self.edges:
                self.edges[edge.source] = []
            self.edges[edge.source].append(edge)

    def _load_constraints(self, data: dict) -> None:
        """Load constraints from data.

        NOTE: Only load from 'constraints' key, NOT 'rules'.
        'rules' are routing rules (different structure with 'triggers', 'agent', etc.)
        """
        constraints_data = data.get("constraints") or []

        for c_data in constraints_data:
            if not isinstance(c_data, dict):
                logger.debug(f"Skipping invalid constraint data: {c_data}")
                continue

            # Validate required fields - skip malformed entries
            if "condition" not in c_data:
                logger.debug(f"Skipping constraint without condition: {c_data.get('id', 'unknown')}")
                continue

            c_type = ConstraintType(c_data.get("type", "hard"))
            action = ConstraintAction(c_data.get("action", "block"))

            constraint = Constraint(
                id=c_data.get("id", f"constraint_{len(self.constraints)}"),
                type=c_type,
                condition=c_data.get("condition", ""),
                action=action,
                message=c_data.get("message", "Constraint violated"),
                applies_to=c_data.get("applies_to", ["*"]),
            )
            self.constraints[constraint.id] = constraint

    def _load_metrics(self, data: dict) -> None:
        """Load metrics from data."""
        metrics_data = data.get("metrics") or data.get("scores") or data.get("authority") or []

        for m_data in metrics_data:
            metric_type = MetricType(m_data.get("metric_type", "priority"))

            metric = Metric(
                node_id=m_data["node_id"],
                metric_type=metric_type,
                value=m_data.get("value", 0),
                scale_min=m_data.get("scale_min", 0),
                scale_max=m_data.get("scale_max", 10),
            )

            if metric.node_id not in self.metrics:
                self.metrics[metric.node_id] = {}
            self.metrics[metric.node_id][metric_type] = metric

    # ═══════════════════════════════════════════════════════════════════
    # DIMENSION 1: ONTOLOGY QUERIES (What exists)
    # ═══════════════════════════════════════════════════════════════════

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a single node by ID. ATOMIC."""
        return self.nodes.get(node_id)

    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Get all nodes of a type."""
        return [n for n in self.nodes.values() if n.type == node_type]

    def get_nodes_by_domain(self, domain: str) -> List[Node]:
        """Get all nodes in a domain."""
        return [n for n in self.nodes.values() if n.domain == domain]

    def search_nodes(self, query: str) -> List[Node]:
        """Simple keyword search in node names/descriptions."""
        query_lower = query.lower()
        return [n for n in self.nodes.values() if query_lower in n.name.lower() or query_lower in n.description.lower()]

    # ═══════════════════════════════════════════════════════════════════
    # DIMENSION 2: TOPOLOGY QUERIES (How things relate)
    # ═══════════════════════════════════════════════════════════════════

    def get_edges(self, node_id: str, relation: Optional[RelationType] = None) -> List[Edge]:
        """Get all edges from a node, optionally filtered by relation type."""
        edges = self.edges.get(node_id, [])
        if relation:
            edges = [e for e in edges if e.relation == relation]
        return edges

    def get_incoming_edges(self, node_id: str, relation: Optional[RelationType] = None) -> List[Edge]:
        """Get all edges TO a node."""
        incoming = []
        for source_id, edges in self.edges.items():
            for edge in edges:
                if edge.target == node_id:
                    if relation is None or edge.relation == relation:
                        incoming.append(edge)
        return incoming

    def traverse(self, node_id: str, relation: RelationType, depth: int = 1) -> Dict[str, Node]:
        """
        Traverse graph from node following relation type.
        Returns dict of node_id -> Node for all reached nodes.
        ATOMIC: Only returns relevant subgraph.
        """
        result = {}
        visited = set()
        self._traverse_recursive(node_id, relation, depth, result, visited)
        return result

    def _traverse_recursive(
        self, node_id: str, relation: RelationType, depth: int, result: Dict[str, Node], visited: Set[str]
    ) -> None:
        if depth < 0 or node_id in visited:
            return
        visited.add(node_id)

        node = self.get_node(node_id)
        if node:
            result[node_id] = node

        if depth > 0:
            for edge in self.get_edges(node_id, relation):
                self._traverse_recursive(edge.target, relation, depth - 1, result, visited)

    def can_reach(self, from_id: str, to_id: str, relation: Optional[RelationType] = None) -> bool:
        """Check if there's a path from one node to another."""
        visited = set()
        return self._can_reach_recursive(from_id, to_id, relation, visited)

    def _can_reach_recursive(
        self, current: str, target: str, relation: Optional[RelationType], visited: Set[str]
    ) -> bool:
        if current == target:
            return True
        if current in visited:
            return False
        visited.add(current)

        for edge in self.get_edges(current, relation):
            if self._can_reach_recursive(edge.target, target, relation, visited):
                return True
        return False

    def get_path(self, from_id: str, to_id: str, relation: Optional[RelationType] = None) -> List[str]:
        """Get shortest path between nodes. Returns list of node IDs."""
        queue = deque([(from_id, [from_id])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current == to_id:
                return path
            if current in visited:
                continue
            visited.add(current)

            for edge in self.get_edges(current, relation):
                if edge.target not in visited:
                    queue.append((edge.target, path + [edge.target]))

        return []  # No path found

    # ═══════════════════════════════════════════════════════════════════
    # DIMENSION 3: CONSTRAINT QUERIES (What is blocked)
    # ═══════════════════════════════════════════════════════════════════

    def get_constraints(self, node_id: Optional[str] = None) -> List[Constraint]:
        """Get constraints, optionally filtered by node."""
        if node_id is None:
            return list(self.constraints.values())
        return [c for c in self.constraints.values() if "*" in c.applies_to or node_id in c.applies_to]

    def check_constraint(self, constraint: Constraint, context: Dict[str, Any]) -> bool:
        """Check if a constraint condition is met. Returns True if VIOLATED."""
        # Simple keyword matching for now
        condition = constraint.condition.lower()
        for key, value in context.items():
            if isinstance(value, str) and condition in value.lower():
                return True
        return False

    def check_constraints(self, action: str, context: Dict[str, Any]) -> List[Constraint]:
        """Check all constraints and return violations."""
        context_with_action = {**context, "action": action}
        violations = []

        for constraint in self.constraints.values():
            if self.check_constraint(constraint, context_with_action):
                violations.append(constraint)

        return violations

    def is_allowed(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if action is allowed (no hard constraint violations)."""
        violations = self.check_constraints(action, context)
        hard_violations = [v for v in violations if v.type == ConstraintType.HARD]
        return len(hard_violations) == 0

    # ═══════════════════════════════════════════════════════════════════
    # DIMENSION 4: METRIC QUERIES (How much)
    # ═══════════════════════════════════════════════════════════════════

    def get_metric(self, node_id: str, metric_type: MetricType) -> Optional[float]:
        """Get a specific metric value for a node."""
        node_metrics = self.metrics.get(node_id, {})
        metric = node_metrics.get(metric_type)
        return metric.value if metric else None

    def get_all_metrics(self, node_id: str) -> Dict[MetricType, float]:
        """Get all metrics for a node."""
        node_metrics = self.metrics.get(node_id, {})
        return {mt: m.value for mt, m in node_metrics.items()}

    def compare(self, node_a: str, node_b: str, metric_type: MetricType) -> int:
        """Compare two nodes by metric. Returns -1, 0, or 1."""
        a = self.get_metric(node_a, metric_type)
        b = self.get_metric(node_b, metric_type)

        if a is None or b is None:
            return 0
        if a < b:
            return -1
        if a > b:
            return 1
        return 0

    def rank_by_metric(self, node_ids: List[str], metric_type: MetricType, descending: bool = True) -> List[str]:
        """Sort nodes by metric value."""

        def get_value(nid):
            v = self.get_metric(nid, metric_type)
            return v if v is not None else 0

        return sorted(node_ids, key=get_value, reverse=descending)

    def resolve_wildcards(self) -> int:
        """
        Resolve wildcard target IDs in edges.
        Example: 'class:*:Base' -> 'class:vibe_core/base.py:Base'

        Returns:
            Number of edges updated
        """
        resolved_count = 0

        # 1. Map simple name to full node IDs for specific types
        # node_name -> [node_ids]
        name_map = defaultdict(list)
        for node_id, node in self.nodes.items():
            name_map[node.name].append(node_id)

        # 2. Iterate through all edges and look for wildcards
        for source_id, edges in self.edges.items():
            for edge in edges:
                if "*" in edge.target:
                    # Extract type and name from pattern like "class:*:MyClass"
                    parts = edge.target.split(":")
                    if len(parts) == 3:
                        target_type = parts[0]
                        target_name = parts[2]

                        # Find potential matches
                        matches = name_map.get(target_name, [])
                        for match_id in matches:
                            match_node = self.nodes.get(match_id)
                            # Check if type matches (e.g. 'class')
                            if match_node and match_node.type.value == target_type:
                                # Update edge target to first match (best effort)
                                edge.target = match_id
                                resolved_count += 1
                                break

        if resolved_count > 0:
            logger.info(f"Resolved {resolved_count} wildcard edges")

        return resolved_count

    # ═══════════════════════════════════════════════════════════════════
    # COMBINED QUERIES (Cross-dimensional)
    # ═══════════════════════════════════════════════════════════════════

    def get_context_for_task(self, task_concept: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get all relevant context for a task. ATOMIC.

        Returns only the nodes/constraints/metrics relevant to the task,
        NOT the entire knowledge base.
        """
        result = {"nodes": {}, "edges": [], "constraints": [], "metrics": {}}

        # Find matching nodes
        matches = self.search_nodes(task_concept)
        for node in matches:
            result["nodes"][node.id] = node

            # Get dependencies (topology)
            deps = self.traverse(node.id, RelationType.DEPENDS_ON, depth)
            result["nodes"].update(deps)

            # Get edges
            result["edges"].extend(self.get_edges(node.id))

            # Get constraints
            result["constraints"].extend(self.get_constraints(node.id))

            # Get metrics
            result["metrics"][node.id] = self.get_all_metrics(node.id)

        return result

    def compile_prompt_context(self, task_concept: str) -> str:
        """
        Compile knowledge into a prompt-ready string.
        ATOMIC: Only relevant knowledge, not entire graph.
        """
        ctx = self.get_context_for_task(task_concept, depth=2)

        lines = []

        # Nodes (Ontology)
        if ctx["nodes"]:
            lines.append("RELEVANT KNOWLEDGE:")
            for node in ctx["nodes"].values():
                lines.append(f"  - {node.name}: {node.description}")

        # Dependencies (Topology)
        deps = [e for e in ctx["edges"] if e.relation == RelationType.DEPENDS_ON]
        if deps:
            lines.append("\nDEPENDENCIES:")
            for edge in deps:
                lines.append(f"  - {edge.source} requires {edge.target}")

        # Constraints
        if ctx["constraints"]:
            lines.append("\nCONSTRAINTS:")
            for c in ctx["constraints"]:
                lines.append(f"  - {c.message}")

        # Metrics
        if ctx["metrics"]:
            lines.append("\nSCORES:")
            for node_id, metrics in ctx["metrics"].items():
                if metrics:
                    metrics_str = ", ".join(f"{k.value}={v}" for k, v in metrics.items())
                    lines.append(f"  - {node_id}: {metrics_str}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_graph_instance: Optional[UnifiedKnowledgeGraph] = None


def get_knowledge_graph() -> UnifiedKnowledgeGraph:
    """Get or create the global knowledge graph instance."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = UnifiedKnowledgeGraph()
        # Load from default location
        knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        if knowledge_dir.exists():
            _graph_instance.load(knowledge_dir)
    return _graph_instance
