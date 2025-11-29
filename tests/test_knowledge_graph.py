"""
Unit tests for UnifiedKnowledgeGraph

Tests all 4 dimensions:
- ONTOLOGY (Nodes)
- TOPOLOGY (Edges)
- CONSTRAINTS (Rules)
- METRICS (Scores)
"""

import pytest
from pathlib import Path
from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
from vibe_core.knowledge.schema import (
    Node, Edge, Constraint, Metric,
    NodeType, RelationType, ConstraintType, ConstraintAction, MetricType
)


@pytest.fixture
def empty_graph():
    """Empty graph for testing."""
    return UnifiedKnowledgeGraph()


@pytest.fixture
def loaded_graph():
    """Graph loaded with test knowledge."""
    graph = UnifiedKnowledgeGraph()
    knowledge_dir = Path(__file__).parent.parent / "knowledge"
    if knowledge_dir.exists():
        graph.load(knowledge_dir)
    return graph


# ═══════════════════════════════════════════════════════════════════
# DIMENSION 1: ONTOLOGY TESTS (Nodes)
# ═══════════════════════════════════════════════════════════════════

def test_graph_initialization(empty_graph):
    """Test graph initializes with empty structures."""
    assert len(empty_graph.nodes) == 0
    assert len(empty_graph.edges) == 0
    assert len(empty_graph.constraints) == 0
    assert len(empty_graph.metrics) == 0
    assert empty_graph._loaded is False


def test_load_knowledge(loaded_graph):
    """Test loading knowledge from YAML files."""
    assert loaded_graph._loaded is True
    assert len(loaded_graph.nodes) > 0
    assert len(loaded_graph.edges) > 0
    assert len(loaded_graph.constraints) > 0


def test_get_node(loaded_graph):
    """Test retrieving individual nodes."""
    civic = loaded_graph.get_node("civic")
    assert civic is not None
    assert civic.type == NodeType.AGENT
    assert civic.name == "CIVIC"
    assert civic.domain == "governance"


def test_get_nodes_by_type(loaded_graph):
    """Test filtering nodes by type."""
    agents = loaded_graph.get_nodes_by_type(NodeType.AGENT)
    concepts = loaded_graph.get_nodes_by_type(NodeType.CONCEPT)

    assert len(agents) > 0
    assert len(concepts) > 0
    assert all(n.type == NodeType.AGENT for n in agents)
    assert all(n.type == NodeType.CONCEPT for n in concepts)


def test_get_nodes_by_domain(loaded_graph):
    """Test filtering nodes by domain."""
    governance = loaded_graph.get_nodes_by_domain("governance")
    assert len(governance) > 0
    assert all(n.domain == "governance" for n in governance)


def test_search_nodes(loaded_graph):
    """Test keyword search in nodes."""
    results = loaded_graph.search_nodes("governance")
    assert len(results) > 0
    assert any("governance" in n.description.lower() for n in results)


# ═══════════════════════════════════════════════════════════════════
# DIMENSION 2: TOPOLOGY TESTS (Edges)
# ═══════════════════════════════════════════════════════════════════

def test_get_edges(loaded_graph):
    """Test retrieving edges from a node."""
    civic_edges = loaded_graph.get_edges("civic")
    assert len(civic_edges) > 0


def test_get_edges_by_relation(loaded_graph):
    """Test filtering edges by relation type."""
    civic_overrides = loaded_graph.get_edges("civic", RelationType.OVERRIDES)
    assert len(civic_overrides) > 0
    assert all(e.relation == RelationType.OVERRIDES for e in civic_overrides)


def test_get_incoming_edges(loaded_graph):
    """Test retrieving incoming edges."""
    # Herald should have incoming edges from CIVIC
    herald_incoming = loaded_graph.get_incoming_edges("herald", RelationType.OVERRIDES)
    assert len(herald_incoming) > 0


def test_traverse(loaded_graph):
    """Test graph traversal."""
    # Traverse dependencies from a node
    deps = loaded_graph.traverse("herald", RelationType.DEPENDS_ON, depth=2)
    assert isinstance(deps, dict)


def test_can_reach(loaded_graph):
    """Test path checking between nodes."""
    # CIVIC should be able to reach HERALD via OVERRIDES
    can_reach = loaded_graph.can_reach("civic", "herald", RelationType.OVERRIDES)
    assert can_reach is True


def test_get_path(loaded_graph):
    """Test shortest path finding."""
    path = loaded_graph.get_path("civic", "herald", RelationType.OVERRIDES)
    assert len(path) >= 2
    assert path[0] == "civic"
    assert path[-1] == "herald"


# ═══════════════════════════════════════════════════════════════════
# DIMENSION 3: CONSTRAINT TESTS (Rules)
# ═══════════════════════════════════════════════════════════════════

def test_get_constraints(loaded_graph):
    """Test retrieving constraints."""
    all_constraints = loaded_graph.get_constraints()
    assert len(all_constraints) > 0


def test_check_constraint(loaded_graph):
    """Test constraint violation checking."""
    # Create a constraint that should trigger
    constraint = Constraint(
        id="test",
        type=ConstraintType.HARD,
        condition=".git",
        action=ConstraintAction.BLOCK,
        message="Test constraint",
        applies_to=["*"]
    )

    # Context with .git should violate
    violated = loaded_graph.check_constraint(constraint, {"path": ".git"})
    assert violated is True

    # Context without .git should not violate
    not_violated = loaded_graph.check_constraint(constraint, {"path": "safe.py"})
    assert not_violated is False


def test_is_allowed(loaded_graph):
    """Test action permission checking."""
    # Modifying .git should be blocked
    allowed = loaded_graph.is_allowed("modify", {"path": ".git"})
    assert allowed is False

    # Modifying normal file should be allowed
    allowed = loaded_graph.is_allowed("modify", {"path": "test.py"})
    assert allowed is True


# ═══════════════════════════════════════════════════════════════════
# DIMENSION 4: METRIC TESTS (Scores)
# ═══════════════════════════════════════════════════════════════════

def test_get_metric(loaded_graph):
    """Test retrieving metric values."""
    civic_authority = loaded_graph.get_metric("civic", MetricType.AUTHORITY)
    assert civic_authority == 10


def test_get_all_metrics(loaded_graph):
    """Test retrieving all metrics for a node."""
    civic_metrics = loaded_graph.get_all_metrics("civic")
    assert MetricType.AUTHORITY in civic_metrics
    assert civic_metrics[MetricType.AUTHORITY] == 10


def test_compare(loaded_graph):
    """Test metric comparison."""
    # CIVIC (authority 10) > HERALD (authority 9)
    result = loaded_graph.compare("civic", "herald", MetricType.AUTHORITY)
    assert result == 1

    # HERALD (authority 9) < CIVIC (authority 10)
    result = loaded_graph.compare("herald", "civic", MetricType.AUTHORITY)
    assert result == -1


def test_rank_by_metric(loaded_graph):
    """Test ranking nodes by metric."""
    agents = ["civic", "herald", "science", "agora"]
    ranked = loaded_graph.rank_by_metric(agents, MetricType.AUTHORITY, descending=True)

    # CIVIC should be first (authority 10)
    assert ranked[0] == "civic"
    # AGORA should be last (authority 4)
    assert ranked[-1] == "agora"


# ═══════════════════════════════════════════════════════════════════
# COMBINED TESTS
# ═══════════════════════════════════════════════════════════════════

def test_get_context_for_task(loaded_graph):
    """Test atomic context retrieval."""
    context = loaded_graph.get_context_for_task("security", depth=1)

    assert "nodes" in context
    assert "edges" in context
    assert "constraints" in context
    assert "metrics" in context
    assert len(context["nodes"]) > 0


def test_compile_prompt_context(loaded_graph):
    """Test prompt context compilation."""
    prompt_context = loaded_graph.compile_prompt_context("governance")

    assert isinstance(prompt_context, str)
    assert len(prompt_context) > 0
    assert "RELEVANT KNOWLEDGE:" in prompt_context or len(prompt_context) == 0
