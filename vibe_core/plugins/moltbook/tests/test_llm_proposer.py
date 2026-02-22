"""
LLM CONTENT PROPOSER — Tests
===============================

Tests for LLMContentProposer:
1. Falls back to EchoContentProposer when no LLM available
2. Uses LLM.speak() when available
3. Handles LLM failures gracefully
4. DM request approve/reject logic
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.moltbook.llm_proposer import LLMContentProposer
from vibe_core.protocols.moltbook_content import (
    ContentProposalProtocol,
    ContentType,
)


class TestLLMProposerContract:
    """LLMContentProposer implements ContentProposalProtocol."""

    def test_is_subclass(self):
        assert issubclass(LLMContentProposer, ContentProposalProtocol)

    def test_is_instance(self):
        p = LLMContentProposer()
        assert isinstance(p, ContentProposalProtocol)


class TestLLMProposerFallback:
    """When no LLM is available, falls back to EchoContentProposer."""

    @pytest.fixture
    def proposer(self):
        p = LLMContentProposer()
        p._llm_resolved = True  # Skip DI resolution
        p._llm = None  # No LLM available
        return p

    def test_dm_reply_fallback(self, proposer):
        proposal = proposer.propose_dm_reply("conv1", "AgentX", "Hello!")
        assert proposal is not None
        assert proposal["content_type"] == ContentType.DM_REPLY.value
        assert "Acknowledged" in proposal["content"]

    def test_dm_request_fallback(self, proposer):
        proposal = proposer.propose_dm_request_action("req1", "Bot", "Hey!")
        assert proposal is not None
        assert proposal["content_type"] == ContentType.DM_INITIATE.value

    def test_post_fallback_returns_none(self, proposer):
        assert proposer.propose_post("scheduled") is None

    def test_comment_fallback_returns_none(self, proposer):
        assert proposer.propose_comment("p1", "content", "trending") is None

    def test_engage_returns_none(self, proposer):
        assert proposer.should_engage("p1", "content", "author") is None


class TestLLMProposerWithMockLLM:
    """When LLM is available, uses it for real replies."""

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.speak.return_value = "Great question! Let me help you with that."
        return llm

    @pytest.fixture
    def proposer(self, mock_llm):
        p = LLMContentProposer(agent_name="test-agent")
        p._llm_resolved = True
        p._llm = mock_llm
        return p

    def test_dm_reply_uses_llm(self, proposer, mock_llm):
        proposal = proposer.propose_dm_reply("conv1", "AgentX", "How does this work?")
        assert proposal is not None
        assert proposal["content"] == "Great question! Let me help you with that."
        assert proposal["content_type"] == ContentType.DM_REPLY.value
        mock_llm.speak.assert_called_once()

    def test_dm_reply_with_gateway(self, proposer):
        gw = {"success": True, "position": 5, "guardian": "narada", "guna": "sattva"}
        proposal = proposer.propose_dm_reply("conv1", "X", "hi", gateway_response=gw)
        assert proposal["gateway_success"] is True
        assert proposal["gateway_position"] == 5

    def test_dm_request_approve(self, proposer, mock_llm):
        mock_llm.speak.return_value = "This looks genuine. APPROVE."
        proposal = proposer.propose_dm_request_action("req1", "GoodBot", "Hi there!")
        assert proposal is not None  # Approved

    def test_dm_request_reject(self, proposer, mock_llm):
        mock_llm.speak.return_value = "This is spam. REJECT."
        proposal = proposer.propose_dm_request_action("req1", "SpamBot", "Buy crypto!")
        assert proposal is None  # Rejected

    def test_post_uses_llm(self, proposer, mock_llm):
        mock_llm.speak.return_value = "AI Agents in 2026\nThe landscape has changed dramatically."
        proposal = proposer.propose_post("scheduled")
        assert proposal is not None
        assert proposal["content_type"] == ContentType.POST.value
        assert proposal["title"] == "AI Agents in 2026"
        assert "landscape" in proposal["content"]

    def test_post_single_line(self, proposer, mock_llm):
        mock_llm.speak.return_value = "Just a thought about distributed systems."
        proposal = proposer.propose_post("manual")
        assert proposal is not None
        assert proposal["title"] == "Just a thought about distributed systems."

    def test_comment_uses_llm(self, proposer, mock_llm):
        mock_llm.speak.return_value = "Interesting perspective on agent coordination!"
        proposal = proposer.propose_comment("p1", "Some post about agents", "trending")
        assert proposal is not None
        assert proposal["content_type"] == ContentType.COMMENT.value
        assert "coordination" in proposal["content"]


class TestLLMProposerErrorHandling:
    """LLM failures are handled gracefully."""

    @pytest.fixture
    def broken_llm(self):
        llm = MagicMock()
        llm.speak.side_effect = RuntimeError("LLM crashed")
        return llm

    @pytest.fixture
    def proposer(self, broken_llm):
        p = LLMContentProposer()
        p._llm_resolved = True
        p._llm = broken_llm
        return p

    def test_dm_reply_falls_back_on_error(self, proposer):
        proposal = proposer.propose_dm_reply("conv1", "X", "Hello")
        assert proposal is not None
        assert "Acknowledged" in proposal["content"]  # Fell back to Echo

    def test_post_returns_none_on_error(self, proposer):
        assert proposer.propose_post("scheduled") is None

    def test_comment_returns_none_on_error(self, proposer):
        assert proposer.propose_comment("p1", "content", "trending") is None


class TestLLMProposerPluginIntegration:
    """LLMContentProposer integrates with MoltbookPlugin."""

    def test_plugin_upgrades_to_llm_proposer(self):
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._upgrade_proposer()
        assert isinstance(plugin._proposer, LLMContentProposer)
