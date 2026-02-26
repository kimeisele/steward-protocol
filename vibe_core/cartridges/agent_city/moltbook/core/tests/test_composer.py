"""Tests for ContentComposer — extracted from agency_director.py."""

from unittest.mock import MagicMock, patch

from vibe_core.cartridges.agent_city.moltbook.core.composer import (
    ContentComposer,
    _build_task_message,
)


class TestBuildTaskMessage:
    def test_comment_template(self):
        msg = _build_task_message("comment", "Hello world")
        assert "Write a comment responding to: Hello world" in msg

    def test_post_template(self):
        msg = _build_task_message("post", "AI agents")
        assert "Write an original post about: AI agents" in msg

    def test_dm_reply_template(self):
        msg = _build_task_message("dm_reply", "Thanks for your message")
        assert "Reply to this message: Thanks for your message" in msg

    def test_with_knowledge_context(self):
        msg = _build_task_message("post", "topic", knowledge="Some domain context")
        assert "Domain context: Some domain context" in msg

    def test_without_knowledge_context(self):
        msg = _build_task_message("post", "topic")
        assert "Domain context" not in msg

    def test_truncates_long_input(self):
        long_input = "x" * 500
        msg = _build_task_message("post", long_input)
        # Template uses input_text[:200]
        assert len(msg) < 500

    def test_fallback_template(self):
        msg = _build_task_message("unknown_type", "some input")
        assert "Write about: some input" in msg


class TestTruncateSmart:
    def test_no_truncation_needed(self):
        assert ContentComposer.truncate_smart("Hello", 100) == "Hello"

    def test_truncate_at_sentence(self):
        text = "First sentence. Second sentence. Third sentence."
        result = ContentComposer.truncate_smart(text, 35)
        assert result.endswith(".")
        assert len(result) <= 35

    def test_truncate_at_exclamation(self):
        text = "Wow! That is amazing! Really great!"
        result = ContentComposer.truncate_smart(text, 25)
        assert "!" in result
        assert len(result) <= 25

    def test_truncate_at_space(self):
        text = "no_sentence_boundary_but_has spaces_between words"
        result = ContentComposer.truncate_smart(text, 30)
        assert len(result) <= 30

    def test_truncate_hard_limit(self):
        text = "a" * 500
        result = ContentComposer.truncate_smart(text, 100)
        assert len(result) == 100


class TestContentComposer:
    def test_compose_returns_empty_when_no_llm(self):
        """No LLM provider → empty string (not word salad)."""
        composer = ContentComposer(plugin=None)
        # Mock to avoid actual infrastructure
        with patch.object(composer, "_run_engine", return_value=None):
            with patch("vibe_core.cartridges.agent_city.moltbook.core.composer._load_yaml_prompts"):
                with patch.object(composer, "_try_llm", return_value=None):
                    result = composer.compose(
                        pipeline_result={"guna": {"mode": "RAJAS"}},
                        input_text="test topic",
                        content_type="post",
                        input_ctx={"raw_input": "test topic"},
                    )
        assert result == ""

    def test_compose_returns_llm_content(self):
        """LLM content is returned when available."""
        composer = ContentComposer(plugin=None)
        with patch.object(composer, "_run_engine", return_value=None):
            with patch("vibe_core.cartridges.agent_city.moltbook.core.composer._load_yaml_prompts"):
                with patch.object(composer, "_try_llm", return_value="Generated content"):
                    result = composer.compose(
                        pipeline_result={"guna": {"mode": "RAJAS"}},
                        input_text="test topic",
                        content_type="post",
                        input_ctx={"raw_input": "test topic"},
                    )
        assert result == "Generated content"

    def test_compose_extracts_agent_name(self):
        """Agent name extracted from plugin._agent_name."""
        mock_plugin = MagicMock()
        mock_plugin._agent_name = "my-cool-agent"
        composer = ContentComposer(plugin=mock_plugin)

        prompt_ctx_captured = {}

        def capture_try_llm(ctx, task_input, content_type):
            prompt_ctx_captured.update(ctx)
            return "content"

        with patch.object(composer, "_run_engine", return_value=None):
            with patch("vibe_core.cartridges.agent_city.moltbook.core.composer._load_yaml_prompts"):
                with patch.object(composer, "_try_llm", side_effect=capture_try_llm):
                    composer.compose(
                        pipeline_result={},
                        input_text="topic",
                        content_type="post",
                        input_ctx={},
                    )
        assert prompt_ctx_captured.get("agent_name") == "my-cool-agent"

    def test_run_pipeline_empty_text(self):
        composer = ContentComposer()
        assert composer._run_pipeline("") is None
        assert composer._run_pipeline("   ") is None
