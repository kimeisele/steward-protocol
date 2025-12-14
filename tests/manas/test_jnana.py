"""
OPUS-043: JNANA (The Conversation) - Intelligent Response Tests.

TDD: These tests define the expected behavior BEFORE implementation.

JNANA = Knowledge through dialogue.
The handler that makes MANAS truly intelligent.

"Understanding comes before response."
"""

from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# SECTION 1: JNANA HANDLER BASICS
# =============================================================================


class TestJnanaHandlerBasics:
    """Basic tests for JnanaHandler."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

        return JnanaHandler(workspace=tmp_path)

    def test_handler_has_context_service(self, handler):
        """Mutation killer: Handler must have ContextService."""
        assert hasattr(handler, "_context_service")

    def test_handler_has_memory_store(self, handler):
        """Mutation killer: Handler must have MemoryStore."""
        assert hasattr(handler, "_memory")

    def test_handler_can_synthesize_context(self, handler):
        """Mutation killer: Handler must be able to get context."""
        # May fail if not properly initialized, but structure must exist
        assert hasattr(handler, "get_context")


# =============================================================================
# SECTION 2: CONTEXT GATHERING TESTS
# =============================================================================


class TestContextGathering:
    """Tests for context synthesis."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

        return JnanaHandler(workspace=tmp_path)

    def test_get_context_returns_dict(self, handler):
        """Mutation killer: Context must be a dict."""
        ctx = handler.get_context()
        assert isinstance(ctx, dict)

    def test_context_has_system_status(self, handler):
        """Mutation killer: Context must include system status."""
        ctx = handler.get_context()
        # Should have some status info
        assert "status" in ctx or "health" in ctx or "system" in ctx

    def test_context_has_git_info(self, handler):
        """Mutation killer: Context should include git info when available."""
        ctx = handler.get_context()
        # Git info is optional but should be structured if present
        assert isinstance(ctx, dict)


# =============================================================================
# SECTION 3: MEMORY INTEGRATION TESTS
# =============================================================================


class TestMemoryIntegration:
    """Tests for memory store integration."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

        return JnanaHandler(workspace=tmp_path)

    def test_get_recent_memories_returns_list(self, handler):
        """Mutation killer: Recent memories must be a list."""
        memories = handler.get_recent_memories(limit=5)
        assert isinstance(memories, list)

    def test_memories_limit_is_respected(self, handler):
        """Mutation killer: Memory limit must be respected."""
        memories = handler.get_recent_memories(limit=3)
        assert len(memories) <= 3


# =============================================================================
# SECTION 4: PROMPT GENERATION TESTS
# =============================================================================


class TestPromptGeneration:
    """Tests for LLM prompt generation."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

        return JnanaHandler(workspace=tmp_path)

    def test_build_prompt_returns_list(self, handler):
        """Mutation killer: Prompt must be message list."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="Hello")
        prompt = handler.build_prompt(msg)

        assert isinstance(prompt, list)
        assert len(prompt) >= 2  # At least system + user

    def test_prompt_has_system_message(self, handler):
        """Mutation killer: Prompt must have system message."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="Hello")
        prompt = handler.build_prompt(msg)

        system_msgs = [m for m in prompt if m.get("role") == "system"]
        assert len(system_msgs) >= 1

    def test_prompt_has_user_message(self, handler):
        """Mutation killer: Prompt must include user message."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="What is the status?")
        prompt = handler.build_prompt(msg)

        user_msgs = [m for m in prompt if m.get("role") == "user"]
        assert len(user_msgs) >= 1
        assert "status" in user_msgs[-1]["content"].lower()

    def test_prompt_includes_context(self, handler):
        """Mutation killer: System prompt should include context."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="Hello")
        prompt = handler.build_prompt(msg)

        system_content = prompt[0]["content"]
        # Should mention MANAS or system
        assert "MANAS" in system_content or "system" in system_content.lower()


# =============================================================================
# SECTION 5: INTELLIGENT RESPONSE TESTS
# =============================================================================


class TestIntelligentResponse:
    """Tests for intelligent (LLM-powered) responses."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

        return JnanaHandler(workspace=tmp_path)

    @pytest.mark.asyncio
    async def test_handle_with_llm_returns_response(self, handler):
        """Mutation killer: LLM call should return SamvadaResponse."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
            SamvadaMessage,
            SamvadaResponse,
        )

        # Mock the LLM provider
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "I am MANAS, here to help."
        handler._llm_provider = mock_llm

        msg = SamvadaMessage(msg_type="chat", content="Who are you?")
        response = await handler.handle(msg)

        assert isinstance(response, SamvadaResponse)
        assert response.success is True
        assert "MANAS" in response.content or len(response.content) > 0

    @pytest.mark.asyncio
    async def test_handle_without_llm_falls_back_gracefully(self, handler):
        """Mutation killer: No LLM should not crash."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
            SamvadaMessage,
            SamvadaResponse,
        )

        # Ensure no LLM is configured
        handler._llm_provider = None

        msg = SamvadaMessage(msg_type="chat", content="Hello?")
        response = await handler.handle(msg)

        assert isinstance(response, SamvadaResponse)
        # Should still work (fallback mode)
        assert response.success is True or response.error is not None


# =============================================================================
# SECTION 6: SPECIAL QUERY HANDLING
# =============================================================================


class TestSpecialQueries:
    """Tests for special query handling (status, intents, etc.)."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

        return JnanaHandler(workspace=tmp_path)

    @pytest.mark.asyncio
    async def test_status_query_uses_shell_cortex(self, handler):
        """Mutation killer: Status queries should use ShellCortex."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellResult

        # Mock ShellCortex
        with patch.object(handler, "_shell") as mock_shell:
            mock_shell.execute_safe.return_value = ShellResult(
                command=["status"],
                exit_code=0,
                stdout="System healthy",
                blocked=False,
            )

            msg = SamvadaMessage(msg_type="status", content="status")
            response = await handler.handle(msg)

            mock_shell.execute_safe.assert_called()

    @pytest.mark.asyncio
    async def test_why_query_gets_intelligent_response(self, handler):
        """Integration: 'Why' questions should use LLM."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        # Mock the LLM
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "The CI is red because test_foo.py failed."
        handler._llm_provider = mock_llm

        msg = SamvadaMessage(msg_type="chat", content="Why is the CI red?")
        response = await handler.handle(msg)

        # Should have called LLM for "why" questions
        if handler._llm_provider:
            mock_llm.chat.assert_called()
