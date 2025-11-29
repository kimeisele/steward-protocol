"""
Knowledge Loader

Loads YAML files into the UnifiedKnowledgeGraph.
Parses nodes, edges, constraints, and metrics from YAML format.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from .graph import UnifiedKnowledgeGraph

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

logger = logging.getLogger("KNOWLEDGE_LOADER")


class KnowledgeLoader:
    """Loads YAML files into the UnifiedKnowledgeGraph."""

    def __init__(self, graph: "UnifiedKnowledgeGraph"):
        self.graph = graph

    def load_all(self, knowledge_dir: Path) -> None:
        """Load all knowledge from directory structure."""
        knowledge_dir = Path(knowledge_dir)

        # Load core knowledge
        core_dir = knowledge_dir / "core"
        if core_dir.exists():
            self._load_directory(core_dir, domain="core")

        # Load domain knowledge
        domains_dir = knowledge_dir / "domains"
        if domains_dir.exists():
            for domain_dir in domains_dir.iterdir():
                if domain_dir.is_dir():
                    self._load_directory(domain_dir, domain=domain_dir.name)

        logger.info(f"Loaded knowledge from {knowledge_dir}")

    def _load_directory(self, dir_path: Path, domain: str) -> None:
        """Load all YAML files from a directory."""
        for yaml_file in dir_path.glob("*.yaml"):
            self._load_file(yaml_file, domain)

    def _load_file(self, file_path: Path, domain: str) -> None:
        """Load a single YAML file."""
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            if data is None:
                return

            # Determine file type by content
            if "nodes" in data or "agents" in data or "features" in data:
                self._load_nodes(data, domain)

            if "edges" in data or "relations" in data or "dependencies" in data:
                self._load_edges(data)

            if "constraints" in data or "rules" in data:
                self._load_constraints(data)

            if "metrics" in data or "scores" in data or "authority" in data:
                self._load_metrics(data)

            logger.debug(f"Loaded {file_path.name}")

        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")

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
            self.graph.nodes[node.id] = node

    def _load_edges(self, data: dict) -> None:
        """Load edges from data."""
        edges_data = data.get("edges") or data.get("relations") or data.get("dependencies") or []

        for edge_data in edges_data:
            relation = RelationType(edge_data.get("relation", "depends_on"))
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                relation=relation,
                weight=edge_data.get("weight", 1.0),
                properties=edge_data.get("properties", {}),
            )

            if edge.source not in self.graph.edges:
                self.graph.edges[edge.source] = []
            self.graph.edges[edge.source].append(edge)

    def _load_constraints(self, data: dict) -> None:
        """Load constraints from data."""
        constraints_data = data.get("constraints") or data.get("rules") or []

        for c_data in constraints_data:
            constraint_type = ConstraintType(c_data.get("type", "hard"))
            action = ConstraintAction(c_data.get("action", "block"))

            constraint = Constraint(
                id=c_data["id"],
                type=constraint_type,
                condition=c_data.get("condition", ""),
                action=action,
                message=c_data.get("message", "Constraint violated"),
                applies_to=c_data.get("applies_to", ["*"]),
            )
            self.graph.constraints[constraint.id] = constraint

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

            if metric.node_id not in self.graph.metrics:
                self.graph.metrics[metric.node_id] = {}
            self.graph.metrics[metric.node_id][metric_type] = metric
