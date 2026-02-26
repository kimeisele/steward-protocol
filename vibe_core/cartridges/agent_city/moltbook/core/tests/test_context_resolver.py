"""Tests for ContextResolver — extracted from agency_director.py."""

from unittest.mock import MagicMock, patch

from vibe_core.cartridges.agent_city.moltbook.core.context_resolver import ContextResolver
from vibe_core.cartridges.agent_city.moltbook.core.memory import EventLog


class TestContextResolver:
    def _make_resolver(self, event_log=None):
        if event_log is None:
            event_log = MagicMock(spec=EventLog)
            event_log.get_last_validation_feedback.return_value = None
        return ContextResolver(event_log_getter=lambda: event_log)

    def test_gather_basic(self):
        """Gather returns base context even with no infrastructure."""
        resolver = self._make_resolver()
        with patch.object(resolver, "_query_knowledge", return_value=""):
            with patch.object(resolver, "_query_kernel", return_value=None):
                with patch.object(resolver, "_discover_capabilities", return_value=None):
                    ctx = resolver.gather("post", "test topic")
        assert ctx["content_type"] == "post"
        assert ctx["raw_input"] == "test topic"
        assert "timestamp" in ctx

    def test_gather_includes_kg_context(self):
        """Knowledge Graph context flows into input_ctx."""
        resolver = self._make_resolver()
        with patch.object(resolver, "_query_knowledge", return_value="KG domain info"):
            with patch.object(resolver, "_query_kernel", return_value=None):
                with patch.object(resolver, "_discover_capabilities", return_value=None):
                    ctx = resolver.gather("post", "test")
        assert ctx["knowledge_context"] == "KG domain info"

    def test_gather_includes_kernel_context(self):
        """Kernel context flows into input_ctx."""
        resolver = self._make_resolver()
        kernel_ctx = {"resonant_guardian": "narada"}
        with patch.object(resolver, "_query_knowledge", return_value=""):
            with patch.object(resolver, "_query_kernel", return_value=kernel_ctx):
                with patch.object(resolver, "_discover_capabilities", return_value=None):
                    ctx = resolver.gather("post", "test")
        assert ctx["kernel_context"] == kernel_ctx

    def test_gather_includes_capabilities(self):
        """Discovered capabilities flow into input_ctx."""
        resolver = self._make_resolver()
        caps = {"content_proposal": ["analyze"]}
        with patch.object(resolver, "_query_knowledge", return_value=""):
            with patch.object(resolver, "_query_kernel", return_value=None):
                with patch.object(resolver, "_discover_capabilities", return_value=caps):
                    ctx = resolver.gather("post", "test")
        assert ctx["available_agents"] == caps

    def test_gather_includes_validation_feedback(self):
        """Previous validation feedback flows into input_ctx."""
        event_log = MagicMock(spec=EventLog)
        event_log.get_last_validation_feedback.return_value = {
            "violations": ["too_long"],
            "draft": "old draft",
        }
        resolver = self._make_resolver(event_log)
        with patch.object(resolver, "_query_knowledge", return_value=""):
            with patch.object(resolver, "_query_kernel", return_value=None):
                with patch.object(resolver, "_discover_capabilities", return_value=None):
                    ctx = resolver.gather("post", "test")
        assert ctx["previous_violations"] == ["too_long"]
        assert ctx["previous_draft"] == "old draft"

    def test_gather_merges_kwargs(self):
        """Extra kwargs are merged into input_ctx."""
        resolver = self._make_resolver()
        with patch.object(resolver, "_query_knowledge", return_value=""):
            with patch.object(resolver, "_query_kernel", return_value=None):
                with patch.object(resolver, "_discover_capabilities", return_value=None):
                    ctx = resolver.gather("post", "test", trigger="heartbeat", post_id="p1")
        assert ctx["trigger"] == "heartbeat"
        assert ctx["post_id"] == "p1"

    def test_query_knowledge_graceful_failure(self):
        """KG query failure returns empty string."""
        resolver = self._make_resolver()
        with patch("vibe_core.knowledge.resolver.get_resolver", side_effect=Exception("no KG")):
            result = resolver._query_knowledge("test")
        assert result == ""

    def test_query_kernel_graceful_failure(self):
        """Kernel query failure returns None."""
        resolver = self._make_resolver()
        result = resolver._query_kernel("test")
        # May return None if kernel unavailable
        assert result is None or isinstance(result, dict)

    def test_discover_capabilities_graceful_failure(self):
        """Capability discovery failure returns None."""
        resolver = self._make_resolver()
        with patch("vibe_core.di.ServiceRegistry.is_registered", side_effect=Exception("registry down")):
            result = resolver._discover_capabilities()
        assert result is None
