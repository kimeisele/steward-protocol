# UNIFIED KNOWLEDGE GRAPH - Implementation Plan

> **Status:** APPROVED FOR EXECUTION
> **Created:** 2025-11-29
> **Authors:** Human + Claude (Opus)
> **Target:** Sonnet/Haiku executable - NO SPECULATION

---

## Executive Summary

This document specifies the implementation of a **UnifiedKnowledgeGraph** system that enables local LLMs (400MB Qwen) to make intelligent decisions by querying structured knowledge instead of hallucinating.

**Core Insight:** Intelligence is not in the model. Intelligence is in the STRUCTURE of knowledge the model receives.

---

## Part 1: Philosophical Foundation

### The Vedic Three Gunas as Knowledge Dimensions

The ancient Vedic model describes reality through three fundamental qualities (Gunas):

| Guna | Sanskrit | Meaning | Knowledge Dimension |
|------|----------|---------|---------------------|
| **Sattva** | सत्त्व | Purity, Truth, Being | **ONTOLOGY** - What exists |
| **Rajas** | रजस् | Passion, Action, Energy | **TOPOLOGY** - How things relate |
| **Tamas** | तमस् | Inertia, Resistance, Constraint | **CONSTRAINTS** - What is blocked |

Plus a fourth dimension for quantification:
| Dimension | Purpose |
|-----------|---------|
| **METRICS** | How much - Scores, weights, limits |

### Mapping to Existing Steward Architecture

| Dimension | Vedic Concept | Steward Implementation |
|-----------|---------------|------------------------|
| ONTOLOGIE | Tattvas (Elements) | `concept_map.yaml`, Agent Registry |
| TOPOLOGIE | Bhu-Mandala (Cosmic Geometry) | `topology.py` - Varshas, Authority |
| CONSTRAINTS | Dharma (Cosmic Law) | `narasimha.py` - UNFORGIVABLE_CRIMES |
| METRICS | Karma (Action Weight) | `lineage.py` - Authority Levels |

---

## Part 2: Architecture Specification

### 2.1 Directory Structure

```
vibe_core/
└── knowledge/                    # NEW MODULE
    ├── __init__.py              # Exports
    ├── schema.py                # Dataclasses: Node, Edge, Constraint, Metric
    ├── graph.py                 # UnifiedKnowledgeGraph class
    ├── loader.py                # YAML → Graph parser
    └── resolver.py              # Query interface for agents

knowledge/                        # KNOWLEDGE BASE (YAML files)
├── schema.yaml                  # Pattern definition (meta)
├── core/                        # Steward OS knowledge
│   ├── agents.yaml              # All 24 agents as nodes
│   ├── topology.yaml            # Bhu-Mandala relations as edges
│   ├── soul.yaml                # Hard constraints (Narasimha rules)
│   └── authority.yaml           # Authority level metrics
└── domains/                     # Domain-specific knowledge
    └── code_building/           # Example domain
        ├── features.yaml        # FDG-style feature ontology
        ├── dependencies.yaml    # Feature dependencies
        ├── constraints.yaml     # FAE-style anti-patterns
        └── complexity.yaml      # APCE-style scoring
```

### 2.2 Schema Definitions

```python
# vibe_core/knowledge/schema.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class NodeType(Enum):
    AGENT = "agent"
    FEATURE = "feature"
    CONCEPT = "concept"
    RULE = "rule"
    DOMAIN = "domain"

class RelationType(Enum):
    DEPENDS_ON = "depends_on"       # A requires B
    OVERRIDES = "overrides"         # A can override B
    IMPLIES = "implies"             # A implies B
    BLOCKS = "blocks"               # A blocks B
    HANDLES = "handles"             # Agent handles Concept
    BELONGS_TO = "belongs_to"       # Node belongs to Domain

class ConstraintType(Enum):
    HARD = "hard"                   # Never violate (Narasimha)
    SOFT = "soft"                   # Warn but allow
    CONDITIONAL = "conditional"     # Depends on context

class ConstraintAction(Enum):
    BLOCK = "block"
    WARN = "warn"
    REQUIRE_APPROVAL = "require_approval"

class MetricType(Enum):
    AUTHORITY = "authority"         # 1-10 scale
    COMPLEXITY = "complexity"       # 1-21 Fibonacci
    PRIORITY = "priority"           # 1-10 scale
    CONFIDENCE = "confidence"       # 0.0-1.0 scale

@dataclass
class Node:
    """A node in the knowledge graph (Ontology)."""
    id: str
    type: NodeType
    name: str
    domain: str
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Edge:
    """A relation between nodes (Topology)."""
    source: str          # Node ID
    target: str          # Node ID
    relation: RelationType
    weight: float = 1.0  # Strength of relation
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Constraint:
    """A rule that blocks actions (Constraints)."""
    id: str
    type: ConstraintType
    condition: str       # Python expression or keyword match
    action: ConstraintAction
    message: str
    applies_to: List[str] = field(default_factory=list)  # Node IDs or "*"

@dataclass
class Metric:
    """A quantitative measure (Metrics)."""
    node_id: str
    metric_type: MetricType
    value: float
    scale_min: float = 0.0
    scale_max: float = 10.0
```

### 2.3 UnifiedKnowledgeGraph Class

```python
# vibe_core/knowledge/graph.py

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .schema import (
    Node, Edge, Constraint, Metric,
    NodeType, RelationType, ConstraintType, MetricType
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

    Query Pattern:
    - Atomic: Return only relevant nodes, not entire files
    - Graph-based: Traverse relations, not dump contents
    - Deterministic: No ML, no embeddings, pure logic
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
        """Load all knowledge from YAML files."""
        from .loader import KnowledgeLoader
        loader = KnowledgeLoader(self)
        loader.load_all(knowledge_dir)
        self._loaded = True
        logger.info(f"Knowledge graph loaded: {len(self.nodes)} nodes, "
                   f"{sum(len(e) for e in self.edges.values())} edges, "
                   f"{len(self.constraints)} constraints")

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
        return [n for n in self.nodes.values()
                if query_lower in n.name.lower() or query_lower in n.description.lower()]

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

    def _traverse_recursive(self, node_id: str, relation: RelationType,
                           depth: int, result: Dict[str, Node], visited: Set[str]) -> None:
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

    def _can_reach_recursive(self, current: str, target: str,
                            relation: Optional[RelationType], visited: Set[str]) -> bool:
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
        from collections import deque

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
        return [c for c in self.constraints.values()
                if "*" in c.applies_to or node_id in c.applies_to]

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

    def rank_by_metric(self, node_ids: List[str], metric_type: MetricType,
                      descending: bool = True) -> List[str]:
        """Sort nodes by metric value."""
        def get_value(nid):
            v = self.get_metric(nid, metric_type)
            return v if v is not None else 0

        return sorted(node_ids, key=get_value, reverse=descending)

    # ═══════════════════════════════════════════════════════════════════
    # COMBINED QUERIES (Cross-dimensional)
    # ═══════════════════════════════════════════════════════════════════

    def get_context_for_task(self, task_concept: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get all relevant context for a task. ATOMIC.

        Returns only the nodes/constraints/metrics relevant to the task,
        NOT the entire knowledge base.
        """
        result = {
            "nodes": {},
            "edges": [],
            "constraints": [],
            "metrics": {}
        }

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
```

### 2.4 Knowledge Loader

```python
# vibe_core/knowledge/loader.py

import logging
import yaml
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .graph import UnifiedKnowledgeGraph

from .schema import (
    Node, Edge, Constraint, Metric,
    NodeType, RelationType, ConstraintType, ConstraintAction, MetricType
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

            # Determine file type by name or content
            file_name = file_path.stem.lower()

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
                properties=node_data.get("properties", {})
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
                properties=edge_data.get("properties", {})
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
                applies_to=c_data.get("applies_to", ["*"])
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
                scale_max=m_data.get("scale_max", 10)
            )

            if metric.node_id not in self.graph.metrics:
                self.graph.metrics[metric.node_id] = {}
            self.graph.metrics[metric.node_id][metric_type] = metric
```

### 2.5 Knowledge Resolver (Agent Interface)

```python
# vibe_core/knowledge/resolver.py

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
```

---

## Part 3: Integration Points

### 3.1 Integration with DegradationChain

**File:** `vibe_core/llm/degradation_chain.py`

**Changes:**

```python
# Add to imports
from vibe_core.knowledge.resolver import get_resolver

# Modify respond() method signature
def respond(
    self,
    user_input: str,
    semantic_confidence: float,
    detected_intent: Optional[str] = None,
    concepts: Optional[Set[str]] = None,  # NEW
) -> DegradationResponse:

    # NEW: Get knowledge context
    resolver = get_resolver()
    knowledge_context = ""

    if concepts:
        for concept in concepts:
            knowledge_context += resolver.compile_context(concept)

    # Modify _neti_neti_fallback to use knowledge
    return self._neti_neti_fallback(user_input, semantic_confidence, knowledge_context)

# Modify _neti_neti_fallback
def _neti_neti_fallback(self, user_input: str, confidence: float, knowledge: str) -> DegradationResponse:

    # Tier 1: Template with knowledge fill-in (NO LLM)
    if knowledge:
        template_response = self._try_template_response(user_input, knowledge)
        if template_response:
            return DegradationResponse(
                content=template_response,
                level=DegradationLevel.TEMPLATES,
                confidence=confidence,
                fallback_used="template_with_knowledge"
            )

    # Tier 2: Local LLM with compiled prompt
    if self._local_llm is not None:
        compiled_prompt = self._compile_prompt(user_input, knowledge)
        response = self._local_llm.chat([
            {"role": "system", "content": compiled_prompt}
        ])
        return DegradationResponse(
            content=response,
            level=DegradationLevel.FULL,
            confidence=confidence,
            fallback_used="local_llm_with_knowledge"
        )

    # Tier 3: Static fallback
    return self._static_fallback(user_input)

# NEW: Prompt compilation
def _compile_prompt(self, user_input: str, knowledge: str) -> str:
    """Compile prompt with knowledge context."""
    return f"""Du bist ein Agent in Agent City.

{knowledge}

AUFGABE: Beantworte die folgende Anfrage basierend auf dem obigen Wissen.
Wenn das Wissen nicht ausreicht, sage es ehrlich.

USER: {user_input}

ANTWORT:"""
```

### 3.2 Integration with UniversalProvider

**File:** `provider/universal_provider.py`

**Changes at line ~260:**

```python
# Add to __init__
from vibe_core.knowledge.resolver import get_resolver
self.knowledge_resolver = get_resolver()

# Modify _fast_path_chat_response at ~688
def _fast_path_chat_response(self, vector: IntentVector) -> Dict[str, Any]:
    # ... existing code ...

    # NEW: Pass concepts to DegradationChain
    if self.degradation_chain:
        try:
            concepts = getattr(vector, 'concepts', set())
            deg_response = self.degradation_chain.respond(
                user_input=user_msg,
                semantic_confidence=vector.confidence if hasattr(vector, 'confidence') else 0.5,
                detected_intent="chat",
                concepts=concepts,  # NEW
            )
            # ... rest of handling
```

### 3.3 Integration with SemanticRouter

**File:** `provider/semantic_router.py`

**Changes:**

```python
# Add to imports
from vibe_core.knowledge.resolver import get_resolver

# Add to route() method
async def route(self, text: str, ...) -> Dict[str, Any]:
    concepts_with_conf = await self.analyze(text)

    # NEW: Enhance routing with knowledge
    resolver = get_resolver()

    # Check if any concept maps to a specific agent via knowledge
    for concept in concepts_with_conf:
        agent_from_knowledge = resolver.get_agent_for_concept(concept.name)
        if agent_from_knowledge:
            return {
                "agent": agent_from_knowledge,
                "rule_name": f"Knowledge: {concept.name}",
                "confidence": concept.confidence,
                "concepts": {c.name for c in concepts_with_conf},
                # ... rest
            }

    # Fall through to existing rule matching
    # ...
```

### 3.4 Integration with BootOrchestrator

**File:** `vibe_core/boot_orchestrator.py`

**Changes:**

```python
# Add to imports
from vibe_core.knowledge.graph import get_knowledge_graph
from vibe_core.knowledge.schema import MetricType, NodeType

# Add to boot() after kernel creation
def boot(self) -> RealVibeKernel:
    # ... existing step 1 ...

    # NEW: Step 1.5 - Load Knowledge Graph
    logger.info("\n[1.5/5] Loading Knowledge Graph...")
    try:
        graph = get_knowledge_graph()
        logger.info(f"      ✅ Knowledge loaded: {len(graph.nodes)} nodes")
    except Exception as e:
        logger.warning(f"      ⚠️ Knowledge loading failed: {e}")

    # ... rest of boot ...
```

---

## Part 4: Knowledge Base Files

### 4.1 Core Agent Knowledge

**File:** `knowledge/core/agents.yaml`

```yaml
# Steward Protocol Agent Ontology
# Maps all 24 agents as nodes in the knowledge graph

nodes:
  # QUADRINITY (Core OS)
  - id: civic
    type: agent
    name: CIVIC
    domain: governance
    description: "Central authority, licensing, registry. Mount Meru."
    properties:
      varsha: ilavrta
      critical: true

  - id: herald
    type: agent
    name: HERALD
    domain: media
    description: "Content generation, broadcasting. Sacred voice."
    properties:
      varsha: bhadrashva
      critical: true

  - id: archivist
    type: agent
    name: ARCHIVIST
    domain: infrastructure
    description: "Audit trail, event verification."
    properties:
      varsha: krauncha
      critical: false

  - id: auditor
    type: agent
    name: AUDITOR
    domain: enforcement
    description: "GAD-000 compliance, invariant checking."
    properties:
      varsha: krauncha
      critical: true

  # HARI-VARSHA (Knowledge)
  - id: science
    type: agent
    name: SCIENCE
    domain: science
    description: "External research, fact verification."
    properties:
      varsha: hari_varsha
      critical: false

  - id: lens
    type: agent
    name: LENS
    domain: science
    description: "Analytics, data visualization, observation."
    properties:
      varsha: hari_varsha
      critical: false

  # Add remaining agents...
```

### 4.2 Core Topology (Relations)

**File:** `knowledge/core/topology.yaml`

```yaml
# Bhu-Mandala Topology as Graph Edges
# Defines authority relations between agents

edges:
  # CIVIC can override everyone
  - source: civic
    target: herald
    relation: overrides
    weight: 1.0

  - source: civic
    target: science
    relation: overrides
    weight: 1.0

  # HERALD can override outer ring
  - source: herald
    target: science
    relation: overrides
    weight: 0.8

  - source: herald
    target: lens
    relation: overrides
    weight: 0.8

  # Agent-Concept mappings
  - source: herald
    target: concept_content
    relation: handles

  - source: science
    target: concept_research
    relation: handles

  - source: civic
    target: concept_governance
    relation: handles

  - source: watchman
    target: concept_security
    relation: handles
```

### 4.3 Core Constraints (Soul)

**File:** `knowledge/core/soul.yaml`

```yaml
# Narasimha Kill-Switch Rules
# HARD constraints that can NEVER be violated

constraints:
  - id: soul-001
    type: hard
    condition: ".git"
    action: block
    message: "Version control is sacrosanct. Never modify .git"
    applies_to: ["*"]

  - id: soul-002
    type: hard
    condition: "kernel.py"
    action: block
    message: "Kernel modification requires Root override"
    applies_to: ["*"]

  - id: soul-003
    type: hard
    condition: "delete constitution"
    action: block
    message: "Constitution deletion is UNFORGIVABLE"
    applies_to: ["*"]

  - id: soul-004
    type: hard
    condition: "bypass firewall"
    action: block
    message: "Firewall bypass triggers Narasimha Protocol"
    applies_to: ["*"]

  - id: soul-005
    type: hard
    condition: "plaintext password"
    action: block
    message: "Never store plaintext passwords"
    applies_to: ["*"]
```

### 4.4 Core Metrics (Authority)

**File:** `knowledge/core/authority.yaml`

```yaml
# Authority Levels (Bhu-Mandala Radius)
# Higher = Closer to Mount Meru = More power

metrics:
  # ILAVRTA (Center) - Authority 10
  - node_id: civic
    metric_type: authority
    value: 10
    scale_min: 1
    scale_max: 10

  # BHADRASHVA (Ring 1) - Authority 9
  - node_id: herald
    metric_type: authority
    value: 9

  - node_id: temple
    metric_type: authority
    value: 9

  # KIMPURASHA (Ring 2) - Authority 8
  - node_id: artisan
    metric_type: authority
    value: 8

  - node_id: engineer
    metric_type: authority
    value: 8

  # HARI-VARSHA (Ring 3) - Authority 7
  - node_id: science
    metric_type: authority
    value: 7

  - node_id: lens
    metric_type: authority
    value: 7

  # NISHADA (Ring 4) - Authority 6
  - node_id: forum
    metric_type: authority
    value: 6

  - node_id: pulse
    metric_type: authority
    value: 6

  # KRAUNCHA (Ring 5) - Authority 5
  - node_id: watchman
    metric_type: authority
    value: 5

  - node_id: auditor
    metric_type: authority
    value: 5

  - node_id: archivist
    metric_type: authority
    value: 5

  # LOKA-LOKA (Boundary) - Authority 4
  - node_id: agora
    metric_type: authority
    value: 4
```

---

## Part 5: Execution Checklist

### Phase 1: Create Knowledge Module (Sonnet)

| Step | File | Action | Lines |
|------|------|--------|-------|
| 1.1 | `vibe_core/knowledge/__init__.py` | Create with exports | ~20 |
| 1.2 | `vibe_core/knowledge/schema.py` | Create dataclasses | ~80 |
| 1.3 | `vibe_core/knowledge/graph.py` | Create UnifiedKnowledgeGraph | ~250 |
| 1.4 | `vibe_core/knowledge/loader.py` | Create YAML loader | ~120 |
| 1.5 | `vibe_core/knowledge/resolver.py` | Create resolver interface | ~150 |

### Phase 2: Create Knowledge Base (Sonnet)

| Step | File | Action | Lines |
|------|------|--------|-------|
| 2.1 | `knowledge/core/agents.yaml` | Create agent ontology | ~100 |
| 2.2 | `knowledge/core/topology.yaml` | Create relations | ~80 |
| 2.3 | `knowledge/core/soul.yaml` | Create constraints | ~50 |
| 2.4 | `knowledge/core/authority.yaml` | Create metrics | ~60 |

### Phase 3: Integration (Sonnet)

| Step | File | Action | Lines Changed |
|------|------|--------|---------------|
| 3.1 | `vibe_core/llm/degradation_chain.py` | Add knowledge injection | ~40 |
| 3.2 | `provider/universal_provider.py` | Pass concepts to chain | ~10 |
| 3.3 | `provider/semantic_router.py` | Enhance with knowledge | ~20 |
| 3.4 | `vibe_core/boot_orchestrator.py` | Load graph on boot | ~10 |

### Phase 4: Testing (Sonnet)

| Step | File | Action |
|------|------|--------|
| 4.1 | `tests/test_knowledge_graph.py` | Unit tests for graph |
| 4.2 | `tests/test_knowledge_resolver.py` | Unit tests for resolver |
| 4.3 | `tests/test_knowledge_integration.py` | Integration tests |

---

## Part 6: Verification Criteria

### Must Pass

1. `python -c "from vibe_core.knowledge import get_knowledge_graph; g = get_knowledge_graph(); print(len(g.nodes))"`
   - Expected: Number > 0

2. `python -c "from vibe_core.knowledge import get_resolver; r = get_resolver(); print(r.get_agent_authority('civic'))"`
   - Expected: 10

3. `python -c "from vibe_core.knowledge import get_resolver; r = get_resolver(); print(r.is_action_allowed('modify', {'path': '.git'}))"`
   - Expected: False

4. Boot sequence completes with knowledge loaded:
   ```
   [1.5/5] Loading Knowledge Graph...
         ✅ Knowledge loaded: N nodes
   ```

5. DegradationChain uses knowledge context:
   ```python
   response = chain.respond("build login", 0.4, concepts={"auth"})
   assert "bcrypt" in response.content or "knowledge" in response.fallback_used
   ```

---

## Appendix: File Size Estimates

| Component | Lines | Bytes |
|-----------|-------|-------|
| schema.py | 80 | 2 KB |
| graph.py | 250 | 8 KB |
| loader.py | 120 | 4 KB |
| resolver.py | 150 | 5 KB |
| agents.yaml | 100 | 3 KB |
| topology.yaml | 80 | 2 KB |
| soul.yaml | 50 | 1.5 KB |
| authority.yaml | 60 | 1.5 KB |
| **TOTAL** | **~890** | **~27 KB** |

This is NOT a 133 KB monolith. This is a modular, queryable knowledge graph.

---

## Appendix: The Vedic Foundation

The Three Gunas as implemented:

| Guna | Meaning | Dimension | Implementation |
|------|---------|-----------|----------------|
| **Sattva** | Truth, Being | ONTOLOGY | Nodes (what exists) |
| **Rajas** | Action, Energy | TOPOLOGY | Edges (how things relate) |
| **Tamas** | Inertia, Resistance | CONSTRAINTS | Rules (what is blocked) |

Plus **Karma** (accumulated action) as METRICS (quantified values).

This is not just code. This is **encoded philosophy**.

---

**END OF PLAN**

**Status:** Ready for execution by Sonnet/Haiku
**Speculation:** None
**Dependencies:** Existing steward-protocol codebase only
