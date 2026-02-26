"""Tests for ContentComposer — extracted from agency_director.py."""

from unittest.mock import MagicMock, patch

from vibe_core.cartridges.agent_city.moltbook.core.composer import (
    ContentComposer,
    _GENESIS_PRANA,
    _TIER_MAP,
    _TIER_MODELS,
    _build_task_message,
    _resolve_model_tier,
)
from vibe_core.mahamantra.substrate.core.seed import COSMIC_FRAME, PANCHA, TRINITY
from vibe_core.runtime.quota_manager import OperationalQuota


class TestBuildTaskMessage:
    def test_comment_with_format(self):
        msg = _build_task_message("comment", "Hello world", content_format="question")
        assert "Hello world" in msg

    def test_post_with_format(self):
        msg = _build_task_message("post", "AI agents", content_format="analysis")
        assert "AI agents" in msg

    def test_dm_reply_template(self):
        msg = _build_task_message("dm_reply", "Thanks for your message")
        assert "Reply to this message: Thanks for your message" in msg

    def test_with_knowledge_context(self):
        msg = _build_task_message("post", "topic", knowledge="Some domain context", content_format="opinion")
        assert "Domain context: Some domain context" in msg

    def test_without_knowledge_context(self):
        msg = _build_task_message("post", "topic", content_format="observation")
        assert "Domain context" not in msg

    def test_truncates_long_input(self):
        long_input = "x" * 500
        msg = _build_task_message("post", long_input, content_format="observation")
        # Template uses input_text[:300]
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

        def capture_try_llm(ctx, task_input, content_type, **kwargs):
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


# =============================================================================
# TIER-BASED MODEL ROUTING
# =============================================================================


class TestModelTierRouting:
    """Atomic per-task model routing. Like an agency: Chef/Senior/Azubi."""

    def test_comment_question_is_azubi(self):
        tier, model = _resolve_model_tier("comment", "question")
        assert tier == 0
        assert model is None  # Config default

    def test_comment_observation_is_azubi(self):
        tier, model = _resolve_model_tier("comment", "observation")
        assert tier == 0

    def test_dm_reply_is_azubi(self):
        tier, model = _resolve_model_tier("dm_reply", "")
        assert tier == 0

    def test_dm_request_is_azubi(self):
        tier, model = _resolve_model_tier("dm_request", "whatever")
        assert tier == 0

    def test_comment_analysis_is_senior(self):
        tier, model = _resolve_model_tier("comment", "analysis")
        assert tier == 1

    def test_post_question_is_senior(self):
        tier, model = _resolve_model_tier("post", "question")
        assert tier == 1

    def test_post_analysis_is_chef(self):
        tier, model = _resolve_model_tier("post", "analysis")
        assert tier == 2
        assert model == "deepseek/deepseek-r1"

    def test_post_opinion_is_chef(self):
        tier, model = _resolve_model_tier("post", "opinion")
        assert tier == 2

    def test_post_tutorial_is_chef(self):
        tier, model = _resolve_model_tier("post", "tutorial")
        assert tier == 2

    def test_unknown_type_defaults_to_azubi(self):
        tier, model = _resolve_model_tier("unknown", "whatever")
        assert tier == 0

    def test_low_prana_downgrades_chef_to_azubi(self):
        """Explicitly low prana (0 < prana < GENESIS_PRANA) forces Azubi."""
        tier, model = _resolve_model_tier("post", "analysis", prana=100)
        assert tier == 0
        assert model is None  # Downgraded from chef

    def test_low_prana_downgrades_senior_to_azubi(self):
        tier, _ = _resolve_model_tier("comment", "analysis", prana=50)
        assert tier == 0

    def test_zero_prana_means_unknown_no_downgrade(self):
        """prana=0 means 'unknown' (chamber unavailable) — no downgrade."""
        tier, _ = _resolve_model_tier("comment", "analysis", prana=0)
        assert tier == 1  # Stays senior — zero is unknown, not low

    def test_zero_prana_no_downgrade_for_azubi(self):
        """Azubi stays azubi even with zero prana."""
        tier, _ = _resolve_model_tier("comment", "question", prana=0)
        assert tier == 0

    def test_high_prana_high_integrity_upgrades_senior(self):
        """High prana + high integrity upgrades senior → chef."""
        high_prana = _GENESIS_PRANA * 11  # > 10× GENESIS
        high_integrity = COSMIC_FRAME * TRINITY // PANCHA + 1  # Above threshold
        tier, model = _resolve_model_tier("comment", "analysis", integrity_cf=high_integrity, prana=high_prana)
        assert tier == 2  # Upgraded from senior to chef
        assert model == "deepseek/deepseek-r1"

    def test_high_prana_low_integrity_no_upgrade(self):
        """High prana but low integrity → no upgrade."""
        high_prana = _GENESIS_PRANA * 11
        low_integrity = 1000  # Below threshold
        tier, _ = _resolve_model_tier("comment", "analysis", integrity_cf=low_integrity, prana=high_prana)
        assert tier == 1  # Stays senior

    def test_chef_not_downgraded_with_high_prana(self):
        """Already-chef tier is not downgraded when prana is high."""
        tier, _ = _resolve_model_tier("post", "analysis", prana=_GENESIS_PRANA * 5)
        assert tier == 2

    def test_tier_map_covers_all_content_types(self):
        """All main content_type/format combos are in the tier map."""
        assert ("comment", "question") in _TIER_MAP
        assert ("post", "analysis") in _TIER_MAP
        assert ("dm_reply", None) in _TIER_MAP
        assert ("dm_request", None) in _TIER_MAP

    def test_all_tiers_have_models(self):
        """Every tier has a model entry (None = config default)."""
        for tier_level in (0, 1, 2):
            assert tier_level in _TIER_MODELS


# =============================================================================
# QUOTA MODEL-AWARENESS
# =============================================================================


class TestQuotaModelAwareness:
    """QuotaManager uses correct per-model pricing (not hardcoded Claude)."""

    def test_deepseek_cheaper_than_claude(self):
        quota = OperationalQuota()
        claude_cost = quota._estimate_cost(10000, model="anthropic/claude-sonnet-4")
        deepseek_cost = quota._estimate_cost(10000, model="deepseek/deepseek-v3.2")
        # DeepSeek is ~10× cheaper than Claude at minimum
        assert deepseek_cost < claude_cost / 5

    def test_unknown_model_uses_default(self):
        quota = OperationalQuota()
        cost = quota._estimate_cost(10000, model="unknown/model-xyz")
        # Should use default pricing (not crash)
        assert cost > 0

    def test_no_model_uses_default(self):
        quota = OperationalQuota()
        cost = quota._estimate_cost(10000, model="")
        assert cost > 0

    def test_deepseek_r1_priced(self):
        quota = OperationalQuota()
        r1_cost = quota._estimate_cost(10000, model="deepseek/deepseek-r1")
        v3_cost = quota._estimate_cost(10000, model="deepseek/deepseek-v3.2")
        # R1 is more expensive than v3.2
        assert r1_cost > v3_cost
