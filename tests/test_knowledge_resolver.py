"""
Unit tests for KnowledgeResolver

Tests high-level semantic queries for agents.
"""

from pathlib import Path

import pytest

from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
from vibe_core.knowledge.resolver import KnowledgeResolver, get_resolver


@pytest.fixture
def resolver():
    """Resolver with loaded knowledge."""
    graph = UnifiedKnowledgeGraph()
    knowledge_dir = Path(__file__).parent.parent / "knowledge"
    if knowledge_dir.exists():
        graph.load(knowledge_dir)
    return KnowledgeResolver(graph)


# ═══════════════════════════════════════════════════════════════════
# AGENT QUERIES
# ═══════════════════════════════════════════════════════════════════


def test_get_agent_for_concept(resolver):
    """Test concept to agent mapping."""
    # "content" concept should map to herald
    agent = resolver.get_agent_for_concept("content")
    assert agent == "herald"

    # "security" concept should map to watchman
    agent = resolver.get_agent_for_concept("security")
    assert agent == "watchman"

    # "governance" concept should map to civic
    agent = resolver.get_agent_for_concept("governance")
    assert agent == "civic"


def test_get_agent_for_unknown_concept(resolver):
    """Test unknown concept returns None."""
    agent = resolver.get_agent_for_concept("nonexistent_concept_xyz")
    assert agent is None


def test_get_agent_authority(resolver):
    """Test retrieving agent authority levels."""
    # CIVIC should have authority 10 (Mount Meru)
    assert resolver.get_agent_authority("civic") == 10

    # HERALD should have authority 9
    assert resolver.get_agent_authority("herald") == 9

    # AGORA should have authority 4 (boundary)
    assert resolver.get_agent_authority("agora") == 4

    # Unknown agent should default to 5
    assert resolver.get_agent_authority("unknown_agent") == 5


def test_can_agent_override(resolver):
    """Test authority-based override checking."""
    # CIVIC (10) can override HERALD (9)
    assert resolver.can_agent_override("civic", "herald") is True

    # HERALD (9) cannot override CIVIC (10)
    assert resolver.can_agent_override("herald", "civic") is False

    # HERALD (9) can override SCIENCE (7)
    assert resolver.can_agent_override("herald", "science") is True


def test_get_agents_by_authority(resolver):
    """Test filtering agents by minimum authority."""
    # Get agents with authority >= 9 (should include CIVIC, HERALD, TEMPLE)
    high_authority = resolver.get_agents_by_authority(min_authority=9)
    assert len(high_authority) >= 2
    assert "civic" in high_authority
    assert "herald" in high_authority

    # List should be sorted by authority (descending)
    authorities = [resolver.get_agent_authority(a) for a in high_authority]
    assert authorities == sorted(authorities, reverse=True)


# ═══════════════════════════════════════════════════════════════════
# TASK QUERIES
# ═══════════════════════════════════════════════════════════════════


def test_get_dependencies(resolver):
    """Test retrieving feature dependencies."""
    # Herald depends on CIVIC for licensing
    deps = resolver.get_dependencies("herald", depth=1)
    assert isinstance(deps, list)


def test_get_complexity(resolver):
    """Test retrieving complexity scores."""
    # Test with a node that might have complexity
    complexity = resolver.get_complexity("civic")
    assert isinstance(complexity, int)
    assert complexity >= 1


def test_estimate_total_complexity(resolver):
    """Test estimating total complexity with dependencies."""
    total = resolver.estimate_total_complexity(["civic", "herald"])
    assert isinstance(total, int)
    assert total >= 0


# ═══════════════════════════════════════════════════════════════════
# CONSTRAINT QUERIES
# ═══════════════════════════════════════════════════════════════════


def test_is_action_allowed(resolver):
    """Test action permission checking."""
    # Modifying .git should be blocked
    assert resolver.is_action_allowed("modify", {"path": ".git"}) is False

    # Modifying normal files should be allowed
    assert resolver.is_action_allowed("modify", {"path": "test.py"}) is True


def test_get_violations(resolver):
    """Test retrieving violation messages."""
    violations = resolver.get_violations("modify", {"path": ".git"})
    assert len(violations) > 0
    assert any(".git" in v.lower() for v in violations)


def test_get_blocked_features(resolver):
    """Test retrieving blocked features for a scope."""
    # This might return empty list if no features are blocked for v1.0
    blocked = resolver.get_blocked_features(scope="v1.0")
    assert isinstance(blocked, list)


# ═══════════════════════════════════════════════════════════════════
# PROMPT COMPILATION
# ═══════════════════════════════════════════════════════════════════


def test_compile_context(resolver):
    """Test compiling knowledge context for prompts."""
    context = resolver.compile_context("security")
    assert isinstance(context, str)


def test_compile_context_for_governance(resolver):
    """Test compiling governance context."""
    context = resolver.compile_context("governance")
    assert isinstance(context, str)
    # Should contain relevant knowledge if nodes exist
    if len(context) > 0:
        assert "RELEVANT KNOWLEDGE:" in context or "CONSTRAINTS:" in context


def test_get_response_template(resolver):
    """Test retrieving response templates."""
    # Most nodes won't have templates, so this should return None
    template = resolver.get_response_template("security")
    # Either None or a string
    assert template is None or isinstance(template, str)


# ═══════════════════════════════════════════════════════════════════
# SINGLETON PATTERN
# ═══════════════════════════════════════════════════════════════════


def test_get_resolver_singleton():
    """Test get_resolver() returns a resolver instance."""
    resolver = get_resolver()
    assert isinstance(resolver, KnowledgeResolver)
    assert resolver.graph is not None


def test_get_resolver_uses_same_graph():
    """Test get_resolver() uses singleton graph."""
    r1 = get_resolver()
    r2 = get_resolver()
    # Both should use the same underlying graph instance
    assert r1.graph is r2.graph


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION SCENARIOS
# ═══════════════════════════════════════════════════════════════════


def test_full_routing_scenario(resolver):
    """Test complete routing scenario: concept → agent → authority."""
    # 1. Map concept to agent
    agent = resolver.get_agent_for_concept("content")
    assert agent == "herald"

    # 2. Check agent authority
    authority = resolver.get_agent_authority(agent)
    assert authority == 9

    # 3. Verify agent can be overridden by CIVIC
    can_override = resolver.can_agent_override("civic", agent)
    assert can_override is True


def test_security_constraint_scenario(resolver):
    """Test security constraint checking scenario."""
    # 1. Check if modifying .git is allowed
    allowed = resolver.is_action_allowed("modify", {"path": ".git"})
    assert allowed is False

    # 2. Get violation messages
    violations = resolver.get_violations("modify", {"path": ".git"})
    assert len(violations) > 0

    # 3. Verify normal files are allowed
    allowed = resolver.is_action_allowed("modify", {"path": "src/main.py"})
    assert allowed is True
