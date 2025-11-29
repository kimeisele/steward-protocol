"""
Integration Tests for Offline-First Features.

Tests the DegradationChain, ContextAwareAgent, and Tool Injection Pattern.

Run with: pytest tests/test_offline_features.py -v
"""

import pytest
from unittest.mock import patch, MagicMock


class TestDegradationChain:
    """Tests for DegradationChain graceful degradation."""

    def test_degradation_chain_initialization(self):
        """Test DegradationChain initializes correctly."""
        from vibe_core.llm.degradation_chain import DegradationChain, DegradationLevel

        chain = DegradationChain()

        assert chain is not None
        assert chain.current_level in [
            DegradationLevel.FULL,
            DegradationLevel.TEMPLATES,
            DegradationLevel.MINIMAL,
        ]

    def test_degradation_chain_template_fallback(self):
        """Test DegradationChain falls back to templates when offline."""
        from vibe_core.llm.degradation_chain import DegradationChain, DegradationLevel

        chain = DegradationChain()

        # Low confidence should trigger template fallback
        response = chain.respond(
            user_input="Hello, what is the status?",
            semantic_confidence=0.3,  # Low confidence
        )

        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        # Should use template (not local_llm unless installed)
        assert response.fallback_used in ["template:greeting", "template:status", "template:unknown", "local_llm"]

    def test_degradation_chain_high_confidence_bypass(self):
        """Test high confidence bypasses degradation (SATYA path)."""
        from vibe_core.llm.degradation_chain import DegradationChain

        chain = DegradationChain()

        response = chain.respond(
            user_input="Execute task",
            semantic_confidence=0.95,  # High confidence (SATYA)
        )

        assert response is not None
        # High confidence should indicate direct execution
        assert response.fallback_used == "none"
        assert "SATYA" in response.content

    def test_degradation_chain_medium_confidence_clarification(self):
        """Test medium confidence triggers clarification (MANTHAN path)."""
        from vibe_core.llm.degradation_chain import DegradationChain

        chain = DegradationChain()

        response = chain.respond(
            user_input="Do something",
            semantic_confidence=0.7,  # Medium confidence (MANTHAN)
        )

        assert response is not None
        assert response.fallback_used == "clarification"

    def test_degradation_chain_status(self):
        """Test DegradationChain status reporting."""
        from vibe_core.llm.degradation_chain import DegradationChain

        chain = DegradationChain()
        status = chain.get_status()

        assert "level" in status
        assert "local_llm_available" in status
        assert "templates_loaded" in status
        assert status["templates_loaded"] > 0


class TestContextAwareAgent:
    """Tests for ContextAwareAgent with offline capability."""

    def test_context_aware_agent_creation(self):
        """Test ContextAwareAgent can be created."""
        from vibe_core.agents import ContextAwareAgent

        class TestAgent(ContextAwareAgent):
            def process(self, task):
                return {"status": "ok"}

        agent = TestAgent(
            agent_id="test_agent",
            name="TestAgent",
            version="1.0.0",
        )

        assert agent.agent_id == "test_agent"
        assert agent.name == "TestAgent"

    def test_context_aware_agent_degradation_chain(self):
        """Test ContextAwareAgent provides DegradationChain."""
        from vibe_core.agents import ContextAwareAgent

        class TestAgent(ContextAwareAgent):
            def process(self, task):
                return {"status": "ok"}

        agent = TestAgent(
            agent_id="test_agent",
            name="TestAgent",
            version="1.0.0",
        )

        chain = agent.get_degradation_chain()
        assert chain is not None

    def test_context_aware_agent_chat_with_fallback(self):
        """Test chat_with_fallback returns response."""
        from vibe_core.agents import ContextAwareAgent

        class TestAgent(ContextAwareAgent):
            def process(self, task):
                return {"status": "ok"}

        agent = TestAgent(
            agent_id="test_agent",
            name="TestAgent",
            version="1.0.0",
        )

        response = agent.chat_with_fallback("Hello, status please")

        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0

    def test_context_aware_agent_degradation_status(self):
        """Test degradation status is available."""
        from vibe_core.agents import ContextAwareAgent

        class TestAgent(ContextAwareAgent):
            def process(self, task):
                return {"status": "ok"}

        agent = TestAgent(
            agent_id="test_agent",
            name="TestAgent",
            version="1.0.0",
        )

        status = agent.get_degradation_status()

        assert "level" in status
        assert status["level"] in ["full", "templates", "minimal", "unavailable"]


class TestOfflineCapableMixin:
    """Tests for OfflineCapableMixin tool injection pattern."""

    def test_offline_capable_mixin_initialization(self):
        """Test OfflineCapableMixin can be initialized."""
        from vibe_core.agents.context_aware_agent import OfflineCapableMixin
        from vibe_core.llm.degradation_chain import DegradationChain

        class TestTool(OfflineCapableMixin):
            def __init__(self, degradation_chain=None):
                self.init_offline_capability(degradation_chain)

        chain = DegradationChain()
        tool = TestTool(degradation_chain=chain)

        assert tool._degradation_chain is not None

    def test_offline_capable_mixin_is_offline_property(self):
        """Test is_offline property works correctly."""
        from vibe_core.agents.context_aware_agent import OfflineCapableMixin
        from vibe_core.llm.degradation_chain import DegradationChain

        class TestTool(OfflineCapableMixin):
            def __init__(self, degradation_chain=None):
                self.init_offline_capability(degradation_chain)

        # Without chain - should be offline
        tool_no_chain = TestTool()
        assert tool_no_chain.is_offline is True

        # With chain - depends on chain level
        chain = DegradationChain()
        tool_with_chain = TestTool(degradation_chain=chain)
        # Will be offline if no LocalLLM installed
        assert isinstance(tool_with_chain.is_offline, bool)

    def test_offline_capable_mixin_fallback_response(self):
        """Test fallback_response generates response."""
        from vibe_core.agents.context_aware_agent import OfflineCapableMixin
        from vibe_core.llm.degradation_chain import DegradationChain

        class TestTool(OfflineCapableMixin):
            def __init__(self, degradation_chain=None):
                self.init_offline_capability(degradation_chain)

        chain = DegradationChain()
        tool = TestTool(degradation_chain=chain)

        response = tool.fallback_response("test query", tool_name="TestTool")

        assert response is not None
        assert "status" in response
        assert response["status"] == "offline"
        assert "content" in response


class TestResearchToolOffline:
    """Tests for ResearchTool with DegradationChain."""

    def test_research_tool_with_degradation_chain(self):
        """Test ResearchTool accepts DegradationChain."""
        from steward.system_agents.herald.tools.research_tool import ResearchTool
        from vibe_core.llm.degradation_chain import DegradationChain

        chain = DegradationChain()
        tool = ResearchTool(degradation_chain=chain)

        assert tool._degradation_chain is not None

    def test_research_tool_offline_fallback(self):
        """Test ResearchTool falls back to templates when offline."""
        from steward.system_agents.herald.tools.research_tool import ResearchTool
        from vibe_core.llm.degradation_chain import DegradationChain

        chain = DegradationChain()
        tool = ResearchTool(degradation_chain=chain)

        # Without Tavily API, should use fallback
        result = tool.scan("AI agents autonomous")

        assert result is not None
        assert len(result) > 0
        # Should contain context about agents (from template)
        assert "agent" in result.lower() or "autonomous" in result.lower()

    def test_research_tool_status(self):
        """Test ResearchTool reports status correctly."""
        from steward.system_agents.herald.tools.research_tool import ResearchTool
        from vibe_core.llm.degradation_chain import DegradationChain

        chain = DegradationChain()
        tool = ResearchTool(degradation_chain=chain)

        status = tool.get_research_status()

        assert "tavily_available" in status
        assert "degradation_chain" in status
        assert "offline_capable" in status
        assert status["degradation_chain"] is True
        assert status["offline_capable"] is True


class TestHeraldMigration:
    """Tests for HERALD ContextAwareAgent migration."""

    def test_herald_inherits_from_context_aware_agent(self):
        """Test HERALD inherits from ContextAwareAgent."""
        from steward.system_agents.herald.cartridge_main import HeraldCartridge
        from vibe_core.agents import ContextAwareAgent

        herald = HeraldCartridge()

        assert isinstance(herald, ContextAwareAgent)

    def test_herald_has_degradation_chain(self):
        """Test HERALD has DegradationChain available."""
        from steward.system_agents.herald.cartridge_main import HeraldCartridge

        herald = HeraldCartridge()

        chain = herald.get_degradation_chain()
        assert chain is not None

    def test_herald_research_tool_has_degradation_chain(self):
        """Test HERALD's ResearchTool has DegradationChain."""
        from steward.system_agents.herald.cartridge_main import HeraldCartridge

        herald = HeraldCartridge()

        assert herald.research._degradation_chain is not None

    def test_herald_version_bumped(self):
        """Test HERALD version was bumped for migration."""
        from steward.system_agents.herald.cartridge_main import HeraldCartridge

        herald = HeraldCartridge()

        # Version should be 3.1.0 or higher (post-migration)
        version_parts = herald.version.split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])

        assert major >= 3
        if major == 3:
            assert minor >= 1

    def test_herald_chat_with_fallback(self):
        """Test HERALD can use chat_with_fallback."""
        from steward.system_agents.herald.cartridge_main import HeraldCartridge

        herald = HeraldCartridge()

        response = herald.chat_with_fallback("What is the status?")

        assert response is not None
        assert response.content is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
