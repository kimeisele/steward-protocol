"""Tests for ContentComposer — BuddhiResult-driven content generation."""

from unittest.mock import MagicMock, patch

from vibe_core.cartridges.agent_city.moltbook.core.composer import (
    ContentComposer,
    _FORMAT_TOKENS,
)
from vibe_core.mahamantra.protocols._buddhi import BuddhiResult
from vibe_core.runtime.quota_manager import OperationalQuota


def _make_cognition(**overrides):
    """Create a BuddhiResult with sensible defaults."""
    defaults = {
        "perspective": "Karma Yoga - Action",
        "focus": "field",
        "approach": "dharma",
        "mode": "RAJAS",
        "function": "maintainer",
        "chapter": 3,
        "verse_concepts": (
            {"sanskrit": "karma", "meaning": "action"},
            {"sanskrit": "dharma", "meaning": "duty"},
        ),
        "resonant_words": (),
        "prana": 13581,
        "integrity": 0.987,
        "is_alive": True,
        "composed": "dharma karma action truth",
        "vm_result": {
            "guna": {"mode": "RAJAS"},
            "cell": {"prana": 13581, "integrity": 0.987, "is_alive": True},
            "guardian": "prahlada",
            "vibration": {"signature": {"element": "prithvi", "harmonic": 23}},
        },
    }
    defaults.update(overrides)
    return BuddhiResult(**defaults)


# =============================================================================
# SYSTEM MESSAGE — Cognitive prompt from BuddhiResult
# =============================================================================


class TestBuildSystem:
    def test_includes_agent_name(self):
        composer = ContentComposer(plugin=None)
        msg = composer._build_system(_make_cognition(), {})
        assert "steward-protocol" in msg

    def test_custom_agent_name(self):
        mock_plugin = MagicMock()
        mock_plugin._agent_name = "my-agent"
        composer = ContentComposer(plugin=mock_plugin)
        msg = composer._build_system(_make_cognition(), {})
        assert "my-agent" in msg

    def test_cognitive_frame_rajas(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(mode="RAJAS"), {})
        assert "Mode: RAJAS" in msg

    def test_cognitive_frame_sattva(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(mode="SATTVA"), {})
        assert "Mode: SATTVA" in msg

    def test_cognitive_frame_tamas(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(mode="TAMAS"), {})
        assert "Mode: TAMAS" in msg

    def test_chapter_perspective_included(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(chapter=3, perspective="Karma Yoga - Action"), {})
        assert "Chapter 3: Karma Yoga - Action" in msg

    def test_function_included(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(function="maintainer"), {})
        assert "Function: maintainer" in msg

    def test_element_included(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(), {})
        assert "Element: prithvi" in msg

    def test_focus_included(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(focus="fruit"), {})
        assert "Phase: fruit" in msg

    def test_verse_concepts_included(self):
        composer = ContentComposer()
        cognition = _make_cognition(
            verse_concepts=({"sanskrit": "dharma", "meaning": "duty"}, {"sanskrit": "yoga", "meaning": "practice"}),
        )
        msg = composer._build_system(cognition, {})
        assert "duty" in msg
        assert "practice" in msg

    def test_no_verse_concepts_no_crash(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(verse_concepts=()), {})
        assert "steward-protocol" in msg

    def test_strategic_reasoning_included(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(), {"strategic_reasoning": "Target emerging tech discussions"})
        assert "Target emerging tech" in msg

    def test_anti_slop_rules(self):
        composer = ContentComposer()
        msg = composer._build_system(_make_cognition(), {})
        assert "No AI filler" in msg
        assert "as an AI" in msg


# =============================================================================
# TASK MESSAGE — Format-aware instruction + BuddhiResult enrichment
# =============================================================================


class TestBuildTask:
    def test_comment_has_respond_action(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "comment", "topic", {"content_format": "question"},
        )
        assert "Respond to this post about:" in msg

    def test_comment_includes_topic(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "comment", "consensus algorithms", {"content_format": "analysis"},
        )
        assert "consensus algorithms" in msg

    def test_post_has_write_action(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "post", "distributed systems", {"content_format": "analysis"},
        )
        assert "Write about:" in msg
        assert "distributed systems" in msg

    def test_post_includes_topic(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "post", "microservices", {"content_format": "opinion"},
        )
        assert "microservices" in msg

    def test_dm_reply(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "dm_reply", "Thanks for your message", {},
        )
        assert "Reply to this message:" in msg
        assert "Thanks for your message" in msg

    def test_dm_request(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "dm_request", "collaboration", {},
        )
        assert "Send a message about:" in msg

    def test_post_content_included_for_comments(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "comment", "topic",
            {"content_format": "observation", "post_content": "The author wrote about consensus algorithms."},
        )
        assert "POST:" in msg
        assert "consensus algorithms" in msg

    def test_post_content_not_included_for_posts(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "post", "topic",
            {"content_format": "observation", "post_content": "Should not appear"},
        )
        assert "POST:" not in msg

    @patch.object(ContentComposer, "_build_resonance_context", return_value="RESONANCE:\n- agni (fire) — 0.91 [element]")
    def test_resonance_context_included(self, mock_res):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(composed="dharma karma action truth"), "post", "topic",
            {"content_format": "observation"},
        )
        assert "RESONANCE:" in msg
        assert "agni (fire)" in msg
        # When resonance is available, RESONANT CONCEPTS should NOT appear
        assert "RESONANT CONCEPTS:" not in msg

    @patch.object(ContentComposer, "_build_resonance_context", return_value="")
    def test_resonant_concepts_fallback(self, mock_res):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(composed="dharma karma action truth"), "post", "topic",
            {"content_format": "observation"},
        )
        # Falls back to BuddhiResult.composed when resonance unavailable
        assert "RESONANT CONCEPTS:" in msg
        assert "dharma karma action truth" in msg

    def test_knowledge_context_included(self):
        composer = ContentComposer()
        msg = composer._build_task(
            _make_cognition(), "post", "topic",
            {"content_format": "observation", "knowledge_context": "Domain expertise in distributed systems"},
        )
        assert "DOMAIN:" in msg
        assert "distributed systems" in msg

    def test_truncates_long_input(self):
        composer = ContentComposer()
        long_input = "x" * 500
        msg = composer._build_task(
            _make_cognition(), "post", long_input, {"content_format": "observation"},
        )
        assert "x" * 300 in msg
        assert "x" * 400 not in msg


# =============================================================================
# RESONANCE ENRICHMENT — 7D vocabulary from Gita lexicon
# =============================================================================


class TestResonanceContext:
    def test_short_text_returns_empty(self):
        assert ContentComposer._build_resonance_context("hi") == ""

    def test_empty_text_returns_empty(self):
        assert ContentComposer._build_resonance_context("") == ""

    def test_returns_string(self):
        result = ContentComposer._build_resonance_context(
            "distributed systems fault tolerance consensus"
        )
        # resonate() is deterministic — just verify it returns a string
        assert isinstance(result, str)

    def test_deduplicates_meanings(self):
        """If resonate returns words with duplicate meanings, they're deduped."""
        mock_rw1 = MagicMock()
        mock_rw1.first_meaning = "fire"
        mock_rw1.sanskrit = "agni"
        mock_rw1.total_score = 0.91
        mock_rw1.score_breakdown.return_value = {"element": 0.9, "harmonic": 0.7}
        mock_rw2 = MagicMock()
        mock_rw2.first_meaning = "fire"  # duplicate
        mock_rw2.sanskrit = "tejas"
        mock_rw2.total_score = 0.85
        mock_rw2.score_breakdown.return_value = {"element": 0.8, "harmonic": 0.6}
        mock_rw3 = MagicMock()
        mock_rw3.first_meaning = "truth"
        mock_rw3.sanskrit = "satya"
        mock_rw3.total_score = 0.78
        mock_rw3.score_breakdown.return_value = {"element": 0.5, "harmonic": 0.9}

        with patch(
            "vibe_core.mahamantra.substrate.encoding.resonance_ranker.resonate",
            return_value=[mock_rw1, mock_rw2, mock_rw3],
        ):
            result = ContentComposer._build_resonance_context(
                "distributed systems architecture"
            )
        # fire appears once (deduped), truth appears
        assert "agni (fire)" in result
        assert "satya (truth)" in result
        assert result.count("(fire)") == 1  # deduped

    def test_includes_dimension_scores(self):
        """Resonance context shows top-scoring dimension for each word."""
        mock_rw = MagicMock()
        mock_rw.first_meaning = "action"
        mock_rw.sanskrit = "karma"
        mock_rw.total_score = 0.88
        mock_rw.score_breakdown.return_value = {"element": 0.3, "harmonic": 0.95, "shruti": 0.1}

        with patch(
            "vibe_core.mahamantra.substrate.encoding.resonance_ranker.resonate",
            return_value=[mock_rw],
        ):
            result = ContentComposer._build_resonance_context(
                "testing dimension scores in resonance"
            )
        assert "[harmonic]" in result  # harmonic scored highest


# =============================================================================
# MODEL ROUTING — Prana/integrity driven
# =============================================================================


class TestModelRouting:
    def test_comment_uses_default_model(self):
        composer = ContentComposer()
        model, tokens = composer._route_model(_make_cognition(), "comment", "question")
        assert model is None  # Config default

    def test_post_analysis_uses_reasoning_model(self):
        composer = ContentComposer()
        model, tokens = composer._route_model(
            _make_cognition(is_alive=True, integrity=0.8), "post", "analysis",
        )
        assert model == "deepseek/deepseek-r1"

    def test_post_opinion_uses_reasoning_model(self):
        composer = ContentComposer()
        model, _ = composer._route_model(
            _make_cognition(is_alive=True, integrity=0.8), "post", "opinion",
        )
        assert model == "deepseek/deepseek-r1"

    def test_post_tutorial_uses_reasoning_model(self):
        composer = ContentComposer()
        model, _ = composer._route_model(
            _make_cognition(is_alive=True, integrity=0.8), "post", "tutorial",
        )
        assert model == "deepseek/deepseek-r1"

    def test_post_question_uses_default(self):
        composer = ContentComposer()
        model, _ = composer._route_model(_make_cognition(), "post", "question")
        assert model is None

    def test_dead_cell_uses_default(self):
        composer = ContentComposer()
        model, _ = composer._route_model(
            _make_cognition(is_alive=False), "post", "analysis",
        )
        assert model is None

    def test_low_integrity_uses_default(self):
        composer = ContentComposer()
        model, _ = composer._route_model(
            _make_cognition(integrity=0.3), "post", "analysis",
        )
        assert model is None

    def test_reasoning_model_gets_bonus_tokens(self):
        composer = ContentComposer()
        _, tokens_default = composer._route_model(_make_cognition(), "post", "question")
        _, tokens_reasoning = composer._route_model(
            _make_cognition(integrity=0.8), "post", "analysis",
        )
        assert tokens_reasoning > tokens_default

    def test_format_determines_base_tokens(self):
        composer = ContentComposer()
        _, tokens_q = composer._route_model(_make_cognition(), "comment", "question")
        _, tokens_a = composer._route_model(_make_cognition(), "comment", "analysis")
        assert tokens_q == _FORMAT_TOKENS["question"]
        assert tokens_a == _FORMAT_TOKENS["analysis"]
        assert tokens_a > tokens_q

    def test_dm_uses_default(self):
        composer = ContentComposer()
        model, _ = composer._route_model(_make_cognition(), "dm_reply", "")
        assert model is None


# =============================================================================
# TRUNCATE SMART (unchanged)
# =============================================================================


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


# =============================================================================
# COMPOSE — Full pipeline (mocked LLM)
# =============================================================================


class TestContentComposer:
    def test_compose_returns_none_when_no_llm(self):
        composer = ContentComposer(plugin=None)
        with patch.object(composer, "_call_llm", return_value=None):
            result = composer.compose(
                _make_cognition(),
                "test topic",
                "post",
                {"content_format": "observation"},
            )
        assert result is None

    def test_compose_returns_llm_content(self):
        llm_output = "The tradeoff between consistency and availability is fundamental. CAP theorem defines the boundary."
        composer = ContentComposer(plugin=None)
        with patch.object(composer, "_call_llm", return_value=llm_output):
            result = composer.compose(
                _make_cognition(),
                "test topic",
                "post",
                {"content_format": "observation"},
            )
        assert result == llm_output

    def test_compose_rejects_echo(self):
        composer = ContentComposer(plugin=None)
        input_text = "This is a substantial input text for testing"
        with patch.object(composer, "_call_llm", return_value=f"{input_text} and some more text here."):
            result = composer.compose(
                _make_cognition(),
                input_text,
                "post",
                {"content_format": "observation"},
            )
        assert result is None

    def test_compose_rejects_no_substance(self):
        composer = ContentComposer(plugin=None)
        with patch.object(composer, "_call_llm", return_value="...  "):
            result = composer.compose(
                _make_cognition(),
                "test",
                "post",
                {"content_format": "observation"},
            )
        assert result is None

    def test_compose_extracts_agent_name(self):
        mock_plugin = MagicMock()
        mock_plugin._agent_name = "my-cool-agent"
        composer = ContentComposer(plugin=mock_plugin)

        system_captured = {}

        def capture_llm(system_msg, user_msg, model, max_tokens, content_type):
            system_captured["msg"] = system_msg
            return "Real content with substance here."

        with patch.object(composer, "_call_llm", side_effect=capture_llm):
            composer.compose(
                _make_cognition(), "topic", "post", {"content_format": "observation"},
            )
        assert "my-cool-agent" in system_captured["msg"]


# =============================================================================
# QUOTA MODEL-AWARENESS
# =============================================================================


class TestQuotaModelAwareness:
    def test_deepseek_cheaper_than_claude(self):
        quota = OperationalQuota()
        claude_cost = quota._estimate_cost(10000, model="anthropic/claude-sonnet-4")
        deepseek_cost = quota._estimate_cost(10000, model="deepseek/deepseek-v3.2")
        assert deepseek_cost < claude_cost / 5

    def test_unknown_model_uses_default(self):
        quota = OperationalQuota()
        cost = quota._estimate_cost(10000, model="unknown/model-xyz")
        assert cost > 0

    def test_no_model_uses_default(self):
        quota = OperationalQuota()
        cost = quota._estimate_cost(10000, model="")
        assert cost > 0

    def test_deepseek_r1_priced(self):
        quota = OperationalQuota()
        r1_cost = quota._estimate_cost(10000, model="deepseek/deepseek-r1")
        v3_cost = quota._estimate_cost(10000, model="deepseek/deepseek-v3.2")
        assert r1_cost > v3_cost


# =============================================================================
# CONSTITUTION HARD GATES
# =============================================================================


class TestConstitutionHardGates:
    def setup_method(self):
        from vibe_core.cartridges.agent_city.moltbook.governance.constitution import MoltbookConstitution

        self.constitution = MoltbookConstitution()

    def test_tamas_blocks_post(self):
        result = self.constitution.validate(
            "Valid content here with multiple sentences. This should be enough.",
            "post",
            guna="TAMAS",
        )
        assert not result.is_valid
        assert any("TAMAS" in v for v in result.violations)

    def test_tamas_allows_comment(self):
        result = self.constitution.validate(
            "Valid comment content here with substance.",
            "comment",
            guna="TAMAS",
        )
        assert result.is_valid

    def test_rajas_allows_post(self):
        result = self.constitution.validate(
            "Valid post with real substance. Two sentences make it pass.",
            "post",
            guna="RAJAS",
        )
        assert result.is_valid

    def test_sattva_allows_post(self):
        result = self.constitution.validate(
            "Contemplative insight on system design. Architectural clarity matters.",
            "post",
            guna="SATTVA",
        )
        assert result.is_valid

    def test_no_guna_allows_all(self):
        result = self.constitution.validate(
            "Content without guna context provided. Still valid if checks pass.",
            "post",
        )
        assert result.is_valid

    def test_slop_two_patterns_blocks(self):
        result = self.constitution.validate(
            "As an AI, let me break this down for you today.",
            "comment",
        )
        assert not result.is_valid
        assert any("slop" in v.lower() for v in result.violations)

    def test_slop_one_pattern_warns(self):
        result = self.constitution.validate(
            "It's important to note that distributed systems scale differently.",
            "comment",
        )
        assert result.is_valid
        assert len(result.warnings) > 0

    def test_shallow_post_blocks(self):
        result = self.constitution.validate(
            "Just one short sentence",
            "post",
            guna="RAJAS",
        )
        assert not result.is_valid
        assert any("shallow" in v.lower() for v in result.violations)

    def test_clean_content_passes(self):
        result = self.constitution.validate(
            "The tradeoff between consistency and availability is fundamental. "
            "CAP theorem defines the boundary condition for distributed systems.",
            "comment",
        )
        assert result.is_valid
        assert len(result.violations) == 0

    def test_empty_content_blocks(self):
        result = self.constitution.validate("", "comment")
        assert not result.is_valid

    def test_internal_term_leak_blocks(self):
        result = self.constitution.validate(
            "The SATTVA mode enables read operations through the gateway.",
            "comment",
        )
        assert not result.is_valid
        assert any("leak" in v.lower() for v in result.violations)
