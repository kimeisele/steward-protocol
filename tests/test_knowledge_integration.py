"""
Integration tests for Knowledge Graph with Steward Protocol components

Tests integration with:
- DegradationChain
- SemanticRouter
- UniversalProvider
- Boot sequence
"""

import pytest
from pathlib import Path
from vibe_core.knowledge import get_knowledge_graph, get_resolver
from vibe_core.llm.degradation_chain import DegradationChain


# ═══════════════════════════════════════════════════════════════════
# BOOT SEQUENCE INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def test_knowledge_graph_loads_on_import():
    """Test knowledge graph can be loaded."""
    graph = get_knowledge_graph()
    assert graph is not None
    assert graph._loaded is True
    assert len(graph.nodes) > 0


def test_knowledge_graph_singleton():
    """Test knowledge graph uses singleton pattern."""
    g1 = get_knowledge_graph()
    g2 = get_knowledge_graph()
    assert g1 is g2


def test_resolver_singleton():
    """Test resolver uses singleton pattern."""
    r1 = get_resolver()
    r2 = get_resolver()
    assert r1.graph is r2.graph


# ═══════════════════════════════════════════════════════════════════
# DEGRADATION CHAIN INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def test_degradation_chain_accepts_concepts():
    """Test DegradationChain can receive concepts parameter."""
    chain = DegradationChain()

    # Should accept concepts parameter without error
    response = chain.respond(
        user_input="test input",
        semantic_confidence=0.5,
        concepts={"security", "governance"}
    )

    assert response is not None
    assert hasattr(response, 'content')
    assert hasattr(response, 'fallback_used')


def test_degradation_chain_compiles_knowledge():
    """Test DegradationChain compiles knowledge context."""
    chain = DegradationChain()

    # The _compile_prompt method should be available
    assert hasattr(chain, '_compile_prompt')

    # Test prompt compilation
    prompt = chain._compile_prompt("test", "knowledge context here")
    assert "knowledge context here" in prompt


def test_degradation_chain_with_empty_concepts():
    """Test DegradationChain handles empty concepts gracefully."""
    chain = DegradationChain()

    response = chain.respond(
        user_input="test input",
        semantic_confidence=0.5,
        concepts=set()
    )

    assert response is not None


def test_degradation_chain_with_none_concepts():
    """Test DegradationChain handles None concepts gracefully."""
    chain = DegradationChain()

    response = chain.respond(
        user_input="test input",
        semantic_confidence=0.5,
        concepts=None
    )

    assert response is not None


# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE RESOLVER INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def test_resolver_concept_to_agent_mapping():
    """Test complete concept→agent mapping flow."""
    resolver = get_resolver()

    # Test multiple concept mappings
    mappings = {
        "content": "herald",
        "security": "watchman",
        "governance": "civic",
    }

    for concept, expected_agent in mappings.items():
        agent = resolver.get_agent_for_concept(concept)
        assert agent == expected_agent, f"Concept '{concept}' should map to '{expected_agent}' but got '{agent}'"


def test_resolver_authority_hierarchy():
    """Test authority hierarchy is correct."""
    resolver = get_resolver()

    # CIVIC should have highest authority
    civic_auth = resolver.get_agent_authority("civic")
    assert civic_auth == 10

    # All other agents should have lower authority
    agents = ["herald", "science", "watchman", "agora"]
    for agent in agents:
        auth = resolver.get_agent_authority(agent)
        assert auth < civic_auth, f"{agent} should have lower authority than CIVIC"


def test_resolver_constraint_enforcement():
    """Test constraint enforcement through resolver."""
    resolver = get_resolver()

    # Test UNFORGIVABLE_CRIMES constraints
    forbidden_actions = [
        {"path": ".git"},
        {"path": "kernel.py"},
    ]

    for context in forbidden_actions:
        allowed = resolver.is_action_allowed("modify", context)
        assert allowed is False, f"Action on {context} should be blocked"


# ═══════════════════════════════════════════════════════════════════
# SEMANTIC ROUTER INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def test_knowledge_available_for_routing():
    """Test knowledge graph is available for semantic router."""
    resolver = get_resolver()
    graph = resolver.graph

    # Verify graph has nodes for routing
    assert len(graph.nodes) > 0

    # Verify concept nodes exist
    concepts = graph.get_nodes_by_type(graph.get_node("concept_content").type)
    assert len(concepts) > 0


def test_agent_handles_relations():
    """Test agent→concept HANDLES relations exist."""
    graph = get_knowledge_graph()

    # Find HANDLES relations
    from vibe_core.knowledge.schema import RelationType

    herald_edges = graph.get_edges("herald", RelationType.HANDLES)
    assert len(herald_edges) > 0, "HERALD should have HANDLES relations"


# ═══════════════════════════════════════════════════════════════════
# UNIVERSAL PROVIDER INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def test_concepts_can_be_extracted():
    """Test that concepts can be extracted from parameters."""
    # Simulate IntentVector parameters
    parameters = {
        "concepts": ["security", "governance", "content"]
    }

    # Should be able to convert to set
    concepts = set(parameters["concepts"])
    assert len(concepts) == 3
    assert "security" in concepts


# ═══════════════════════════════════════════════════════════════════
# END-TO-END SCENARIOS
# ═══════════════════════════════════════════════════════════════════

def test_end_to_end_security_query():
    """Test complete security query flow."""
    resolver = get_resolver()

    # 1. Detect concept
    concept = "security"

    # 2. Route to agent
    agent = resolver.get_agent_for_concept(concept)
    assert agent == "watchman"

    # 3. Get agent authority
    authority = resolver.get_agent_authority(agent)
    assert authority == 5

    # 4. Check constraints
    allowed = resolver.is_action_allowed("bypass firewall", {})
    assert allowed is False


def test_end_to_end_content_creation():
    """Test complete content creation flow."""
    resolver = get_resolver()

    # 1. Detect concept
    concept = "content"

    # 2. Route to agent
    agent = resolver.get_agent_for_concept(concept)
    assert agent == "herald"

    # 3. Get agent authority
    authority = resolver.get_agent_authority(agent)
    assert authority == 9

    # 4. Verify CIVIC can override
    can_override = resolver.can_agent_override("civic", agent)
    assert can_override is True


def test_end_to_end_governance_flow():
    """Test complete governance flow."""
    resolver = get_resolver()

    # 1. Detect concept
    concept = "governance"

    # 2. Route to agent
    agent = resolver.get_agent_for_concept(concept)
    assert agent == "civic"

    # 3. Verify highest authority
    authority = resolver.get_agent_authority(agent)
    assert authority == 10

    # 4. Verify cannot be overridden
    high_auth_agents = resolver.get_agents_by_authority(min_authority=10)
    assert agent in high_auth_agents


# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE COMPILATION FOR LLM
# ═══════════════════════════════════════════════════════════════════

def test_knowledge_context_compilation():
    """Test compiling knowledge for LLM prompts."""
    resolver = get_resolver()

    # Compile context for security
    context = resolver.compile_context("security")
    assert isinstance(context, str)

    # Should contain relevant information if knowledge exists
    if len(context) > 0:
        # Should have structured sections
        assert any(keyword in context for keyword in ["RELEVANT", "CONSTRAINTS", "KNOWLEDGE"])


def test_multiple_concepts_compilation():
    """Test compiling context for multiple concepts."""
    resolver = get_resolver()

    # Simulate multiple concepts from semantic analysis
    concepts = {"security", "governance"}

    all_context = ""
    for concept in concepts:
        all_context += resolver.compile_context(concept) + "\n\n"

    assert isinstance(all_context, str)
    assert len(all_context) > 0


# ═══════════════════════════════════════════════════════════════════
# ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════

def test_handles_missing_knowledge_gracefully():
    """Test system handles missing knowledge gracefully."""
    resolver = get_resolver()

    # Unknown concept should return None, not crash
    agent = resolver.get_agent_for_concept("nonexistent_xyz_concept")
    assert agent is None


def test_handles_missing_metrics_gracefully():
    """Test system handles missing metrics gracefully."""
    resolver = get_resolver()

    # Unknown agent should return default value
    authority = resolver.get_agent_authority("nonexistent_agent")
    assert authority == 5  # Default value
