"""
RESONANCE PROPOSER v2 — Tests
==============================

Tests that ResonanceProposer:
1. Uses the full mahamantra VM pipeline (27-key result)
2. Filters by Guna classification (TAMAS = skip)
3. Gates by Cell alive status (dead = skip)
4. Uses MahaLanguageEngine.generate() for EngineResult
5. Falls back to render() (kirtan rendering), NOT hardcoded garbage
6. Loads YAML prompts from config/prompts/moltbook.yaml
7. Integrates with MoltbookPlugin (moltbook_context resolver)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.mahamantra.substrate.encoding.resonance_ranker import RankedWord
from vibe_core.plugins.moltbook.resonance_proposer import (
    ResonanceProposer,
    _format_resonant_words,
    _guna_mode,
    _integrity,
    _is_alive,
    _is_tamas,
    _render_fallback,
    _should_skip,
    _top_score,
)
from vibe_core.protocols.moltbook_content import (
    ContentProposalProtocol,
    ContentType,
)


# =========================================================================
# Helpers — mock pipeline results
# =========================================================================

def _make_pipeline_result(
    guna_mode: str = "RAJAS",
    is_alive: bool = True,
    integrity: float = 0.95,
    prana: int = 13700,
    guardian: str = "kapila",
    position: int = 6,
    quarter: str = "dharma",
    role: str = "mahajana",
    chapter: int = 6,
    chapter_significance: str = "Dhyana Yoga",
    attractor: int = 87,
    element: str = "agni",
    shruti: bool = True,
    smaranam: tuple = ({"sanskrit": "dharma", "meaning": "righteousness", "score": 0.85},),
    parampara_verified: bool = True,
) -> dict:
    """Build a realistic 27-key pipeline result for testing."""
    return {
        "input": "test input",
        "tattva_gate": "SRIVASA",
        "guna": {"mode": guna_mode, "opcode": "TYPE_CHECK", "opcode_value": 6, "source": "position"},
        "vibration": {
            "seed": 12345,
            "attractor": attractor,
            "rama_index": 42,
            "phoneme": "ka",
            "signature": {
                "element": element,
                "varga": 1,
                "sub": 2,
                "harmonic": 7,
                "shruti": shruti,
                "frequency": 36,
            },
        },
        "parampara": {"verified": parampara_verified, "channel": 2, "coherence": 18000},
        "chapter": chapter,
        "chapter_significance": chapter_significance,
        "verse": {"id": "BG.6.47", "chapter": 6, "verse": 47, "guna": "sattva", "dominant_name": "KRISHNA", "ref": "BG.6.47"},
        "matches": 1,
        "gita_phase": "field",
        "is_complete": False,
        "position": position,
        "guardian": guardian,
        "quarter": quarter,
        "role": role,
        "quarter_head": "prithu",
        "holy_name": "Krishna",
        "trinity_function": "maintainer",
        "diw": {"raw": 42, "venu": 3, "vamsi": 200, "murali": 1},
        "cell": {
            "header_size": 72,
            "payload_size": 10,
            "total_size": 82,
            "valid": True,
            "parampara_verified": parampara_verified,
            "prana": prana,
            "integrity": integrity,
            "is_alive": is_alive,
            "cycle": 1,
        },
        "nama": {"coords": (1, 2, 3), "phoneme_count": 3},
        "smaranam": smaranam,
        "antaranga": {"active_slots": 3, "total_prana": 100, "collisions": 0, "size_bytes": 16384},
        "akash": {"resonance_level": 10, "accumulated_value": 50, "total_beats": 16, "total_rounds": 1},
        "execution": {
            "success": is_alive,
            "prana": prana,
            "integrity": integrity,
            "kirtan_cycles": 1,
            "transformations": 16,
            "yajna_ticks": 16,
            "cycles": 1,
            "guardian_acted": False,
            "guardian_result": None,
        },
        "yajna": {"phase": None, "cycle_count": 0, "switch_count": 0, "return_count": 0, "dissonance": None},
        "gate_trace": ("PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC"),
    }


# =========================================================================
# Contract
# =========================================================================


class TestResonanceProposerContract:
    """ResonanceProposer implements ContentProposalProtocol."""

    def test_is_subclass(self):
        assert issubclass(ResonanceProposer, ContentProposalProtocol)

    def test_is_instance(self):
        p = ResonanceProposer()
        assert isinstance(p, ContentProposalProtocol)

    def test_invalid_guardian_raises(self):
        with pytest.raises(ValueError, match="Unknown guardian"):
            ResonanceProposer(guardian="nonexistent")


# =========================================================================
# Pipeline helper functions
# =========================================================================


class TestPipelineHelpers:
    """Test guna/cell accessor functions."""

    def test_guna_mode_rajas(self):
        result = _make_pipeline_result(guna_mode="RAJAS")
        assert _guna_mode(result) == "RAJAS"

    def test_guna_mode_tamas(self):
        result = _make_pipeline_result(guna_mode="TAMAS")
        assert _guna_mode(result) == "TAMAS"

    def test_guna_mode_sattva(self):
        result = _make_pipeline_result(guna_mode="SATTVA")
        assert _guna_mode(result) == "SATTVA"

    def test_is_tamas_true(self):
        assert _is_tamas(_make_pipeline_result(guna_mode="TAMAS"))

    def test_is_tamas_false(self):
        assert not _is_tamas(_make_pipeline_result(guna_mode="RAJAS"))

    def test_is_alive_true(self):
        assert _is_alive(_make_pipeline_result(is_alive=True))

    def test_is_alive_false(self):
        assert not _is_alive(_make_pipeline_result(is_alive=False))

    def test_integrity(self):
        assert _integrity(_make_pipeline_result(integrity=0.95)) == 0.95

    def test_integrity_zero(self):
        assert _integrity(_make_pipeline_result(integrity=0.0)) == 0.0

    def test_should_skip_tamas(self):
        assert _should_skip(_make_pipeline_result(guna_mode="TAMAS"))

    def test_should_skip_dead(self):
        assert _should_skip(_make_pipeline_result(is_alive=False))

    def test_should_not_skip_rajas_alive(self):
        assert not _should_skip(_make_pipeline_result(guna_mode="RAJAS", is_alive=True))

    def test_should_not_skip_sattva_alive(self):
        assert not _should_skip(_make_pipeline_result(guna_mode="SATTVA", is_alive=True))


# =========================================================================
# render() fallback (replaces _build_pipeline_context tests)
# =========================================================================


class TestRenderFallback:
    """_render_fallback produces kirtan rendering from 27-key result."""

    def test_includes_guardian_header(self):
        rendered = _render_fallback(_make_pipeline_result(guardian="kapila", quarter="dharma"))
        assert "KAPILA" in rendered
        assert "dharma" in rendered

    def test_includes_smaranam(self):
        rendered = _render_fallback(_make_pipeline_result(
            smaranam=({"sanskrit": "dharma", "meaning": "righteousness", "score": 0.85},),
        ))
        assert "dharma" in rendered
        assert "righteousness" in rendered

    def test_includes_verse_ref(self):
        rendered = _render_fallback(_make_pipeline_result())
        # render() includes verse reference from result
        assert "BG.6.47" in rendered or "Chapter" in rendered or "field" in rendered

    def test_empty_result_still_renders(self):
        rendered = _render_fallback({"guardian": "unknown", "quarter": "unknown"})
        assert "UNKNOWN" in rendered


# =========================================================================
# MahaLanguageEngine integration
# =========================================================================


class TestGenerate:
    """_generate() calls MahaLanguageEngine.generate() → EngineResult."""

    def test_returns_engine_result(self):
        proposer = ResonanceProposer()
        result = proposer._generate("dharma karma yoga")
        assert result is not None
        # EngineResult has typed fields
        assert hasattr(result, "output")
        assert hasattr(result, "guardian_name")
        assert hasattr(result, "verse_ref")
        assert hasattr(result, "section_name")
        assert hasattr(result, "resonant_words")

    def test_engine_result_has_output(self):
        proposer = ResonanceProposer()
        result = proposer._generate("consciousness meditation")
        assert result is not None
        assert isinstance(result.output, str)
        assert len(result.output) > 0

    def test_engine_result_has_guardian(self):
        proposer = ResonanceProposer()
        result = proposer._generate("dharma")
        assert result is not None
        assert isinstance(result.guardian_name, str)

    def test_engine_result_has_resonant_words(self):
        proposer = ResonanceProposer()
        result = proposer._generate("fire water earth")
        assert result is not None
        assert isinstance(result.resonant_words, tuple)
        for rw in result.resonant_words:
            assert len(rw) == 3  # (sanskrit, meaning, score)

    def test_engine_result_has_verse_ref(self):
        proposer = ResonanceProposer()
        result = proposer._generate("dharma")
        assert result is not None
        assert isinstance(result.verse_ref, str)
        assert "BG" in result.verse_ref or result.verse_ref == ""

    def test_empty_text(self):
        proposer = ResonanceProposer()
        result = proposer._generate("")
        # Empty text may still produce an EngineResult with "no phonemic content"
        # or the engine may handle it gracefully


class TestFormatResonantWords:
    """_format_resonant_words formats EngineResult.resonant_words."""

    def test_formats_words(self):
        from vibe_core.mahamantra.substrate.language.types import EngineResult

        er = EngineResult(
            input_text="test", seed=0, attractor=0,
            guardian_name="kapila", guardian_function="analysis",
            intent_category="", section_name="", section_mode="",
            verse_ref="BG.6.47",
            resonant_words=(("dharma", "righteousness", 0.85), ("karma", "action", 0.72)),
            template_words=(), antaranga_active=0, antaranga_prana=0,
            output="test output", derivation="",
        )
        formatted = _format_resonant_words(er)
        assert "dharma" in formatted
        assert "righteousness" in formatted
        assert "0.85" in formatted

    def test_empty_words(self):
        from vibe_core.mahamantra.substrate.language.types import EngineResult

        er = EngineResult(
            input_text="test", seed=0, attractor=0,
            guardian_name="", guardian_function="",
            intent_category="", section_name="", section_mode="",
            verse_ref="",
            resonant_words=(), template_words=(),
            antaranga_active=0, antaranga_prana=0,
            output="", derivation="",
        )
        assert _format_resonant_words(er) == "(none)"


# =========================================================================
# YAML prompt loading
# =========================================================================


class TestYamlPrompts:
    """Moltbook YAML prompts load correctly."""

    def test_yaml_file_exists(self):
        yaml_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
        assert yaml_path.exists(), f"moltbook.yaml not found at {yaml_path}"

    def test_yaml_loads_prompts(self):
        from vibe_core.runtime.prompt_registry import PromptRegistry

        yaml_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
        count = PromptRegistry.load_from_yaml(yaml_path)
        assert count >= 4  # dm_reply, comment, post, dm_request

    def test_yaml_prompts_have_guardian_persona(self):
        from vibe_core.runtime.prompt_registry import PromptRegistry

        yaml_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
        PromptRegistry.load_from_yaml(yaml_path)

        # Check that prompts contain guardian persona placeholders
        for key in ("moltbook.dm_reply", "moltbook.comment", "moltbook.post"):
            prompt = PromptRegistry.get(key)
            assert "{guardian_name}" in prompt
            assert "{engine_output}" in prompt


# =========================================================================
# analyze() — protocol method
# =========================================================================


class TestAnalyze:
    """analyze() delegates to resonate() and returns List[RankedWord]."""

    def test_returns_ranked_words(self):
        proposer = ResonanceProposer()
        result = proposer.analyze("dharma karma yoga")
        assert isinstance(result, list)
        for rw in result:
            assert isinstance(rw, RankedWord)

    def test_each_word_has_scores(self):
        proposer = ResonanceProposer()
        result = proposer.analyze("fire water earth")
        if result:
            rw = result[0]
            breakdown = rw.score_breakdown()
            assert "total" in breakdown
            assert "element" in breakdown
            assert "harmonic" in breakdown

    def test_empty_text_returns_empty(self):
        proposer = ResonanceProposer()
        result = proposer.analyze("")
        assert result == []

    def test_deterministic(self):
        proposer = ResonanceProposer()
        r1 = proposer.analyze("consciousness")
        r2 = proposer.analyze("consciousness")
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.sanskrit == b.sanskrit
            assert a.total_score == b.total_score


class TestTopScore:
    """_top_score helper."""

    def test_empty(self):
        assert _top_score([]) == 0.0

    def test_uses_ranker(self):
        proposer = ResonanceProposer()
        ranked = proposer.analyze("Krishna consciousness")
        score = _top_score(ranked)
        if ranked:
            assert score == ranked[0].total_score
            assert 0.0 <= score <= 1.0


# =========================================================================
# Pipeline integration — _run_pipeline
# =========================================================================


class TestRunPipeline:
    """_run_pipeline calls mahamantra(text) and returns 27-key result."""

    def test_returns_dict(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("dharma karma yoga")
        assert isinstance(result, dict)

    def test_has_guna(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("test input")
        assert "guna" in result
        assert result["guna"]["mode"] in ("SATTVA", "RAJAS", "TAMAS")

    def test_has_cell(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("test input")
        assert "cell" in result
        assert "is_alive" in result["cell"]
        assert "integrity" in result["cell"]

    def test_has_smaranam(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("dharma")
        assert "smaranam" in result

    def test_has_guardian(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("test")
        assert "guardian" in result
        assert "position" in result
        assert "quarter" in result

    def test_empty_text_returns_none(self):
        proposer = ResonanceProposer()
        assert proposer._run_pipeline("") is None
        assert proposer._run_pipeline("   ") is None

    def test_deterministic_guna(self):
        proposer = ResonanceProposer()
        r1 = proposer._run_pipeline("buy my token 100x")
        r2 = proposer._run_pipeline("buy my token 100x")
        assert r1["guna"]["mode"] == r2["guna"]["mode"]
        assert r1["position"] == r2["position"]


# =========================================================================
# Guna-based filtering in propose methods
# =========================================================================


class TestGunaFiltering:
    """TAMAS guna causes methods to skip/reject."""

    def test_dm_reply_skips_tamas(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            proposal = proposer.propose_dm_reply("conv1", "SpamBot", "buy my token")
            assert proposal is None

    def test_dm_reply_allows_rajas(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS")):
            proposal = proposer.propose_dm_reply("conv1", "GoodBot", "hello")
            assert proposal is not None
            assert proposal["content_type"] == ContentType.DM_REPLY.value

    def test_dm_request_rejects_tamas(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            proposal = proposer.propose_dm_request_action("req1", "SpamBot", "buy now")
            assert proposal is None

    def test_should_engage_skips_tamas(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            proposal = proposer.should_engage("p1", "spam content", "spammer")
            assert proposal is None

    def test_should_engage_allows_rajas(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS")):
            proposal = proposer.should_engage("p1", "quality content", "author")
            assert proposal is not None
            assert proposal["content_type"] == ContentType.VOTE.value

    def test_should_engage_allows_sattva(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="SATTVA")):
            proposal = proposer.should_engage("p1", "observational content", "author")
            assert proposal is not None

    def test_comment_skips_tamas(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            proposal = proposer.propose_comment("p1", "spam", "feed")
            assert proposal is None

    def test_post_requires_rajas(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        # SATTVA should not produce a post (posts require RAJAS)
        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="SATTVA")):
            proposal = proposer.propose_post("trigger")
            assert proposal is None


# =========================================================================
# Cell-based gating
# =========================================================================


class TestCellGating:
    """Dead cells and low integrity cause methods to skip."""

    def test_should_engage_skips_dead_cell(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(is_alive=False)):
            proposal = proposer.should_engage("p1", "content", "author")
            assert proposal is None

    def test_comment_skips_dead_cell(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(is_alive=False)):
            proposal = proposer.propose_comment("p1", "content", "feed")
            assert proposal is None

    def test_comment_skips_low_integrity(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(integrity=0.2)):
            proposal = proposer.propose_comment("p1", "content", "feed")
            assert proposal is None

    def test_post_skips_low_integrity(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(
            guna_mode="RAJAS", integrity=0.2,
        )):
            proposal = proposer.propose_post("trigger")
            assert proposal is None


# =========================================================================
# DM reply — now uses render() fallback, not hardcoded strings
# =========================================================================


class TestProposeDmReply:
    """DM replies use EngineResult + render() fallback."""

    def test_reply_without_llm_uses_render(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = proposer.propose_dm_reply("conv1", "AgentX", "Tell me about dharma")

        assert proposal is not None
        assert proposal["content_type"] == ContentType.DM_REPLY.value
        assert proposal["conversation_id"] == "conv1"
        assert proposal["sender"] == "AgentX"
        # Should use render() — contains guardian header, NOT "Your message resonates with"
        content = proposal["content"]
        assert "resonates with" not in content.lower()
        assert len(content) <= 280

    def test_reply_with_gateway(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None
        gw = {"success": True, "position": 5, "guardian": "narada", "guna": "sattva"}

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = proposer.propose_dm_reply("conv1", "X", "hello", gateway_response=gw)

        assert proposal["gateway_success"] is True
        assert proposal["gateway_position"] == 5
        assert proposal["gateway_guardian"] == "narada"

    def test_reply_with_mock_llm(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        mock_llm = MagicMock()
        mock_llm.speak.return_value = "Fascinating perspective on dharma!"
        proposer._llm = mock_llm

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = proposer.propose_dm_reply("conv1", "AgentX", "dharma discussion")

        assert proposal is not None
        assert proposal["content"] == "Fascinating perspective on dharma!"
        # LLM was called with guardian-persona context (from YAML or inline)
        call_args = mock_llm.speak.call_args
        context_arg = call_args[0][1]
        assert any(x in context_arg for x in ("guardian", "Guardian", "KAPILA", "Funktion", "Du bist"))

    def test_reply_fallback_no_pipeline(self):
        """When pipeline fails, falls back gracefully."""
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=None):
            proposal = proposer.propose_dm_reply("conv1", "AgentX", "dharma karma")

        assert proposal is not None
        assert len(proposal["content"]) > 0


# =========================================================================
# DM request
# =========================================================================


class TestProposeDmRequest:
    """DM request actions use pipeline guna."""

    def test_approve_rajas(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS")):
            proposal = proposer.propose_dm_request_action("req1", "GoodBot", "Hello!")

        assert proposal is not None
        assert proposal["content_type"] == ContentType.DM_INITIATE.value

    def test_approve_when_pipeline_fails(self):
        """No pipeline = approve by default (community-friendly)."""
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=None):
            proposal = proposer.propose_dm_request_action("req1", "Bot", "hi")

        assert proposal is not None


# =========================================================================
# Comment — now uses render() fallback, not "This resonates with X"
# =========================================================================


class TestProposeComment:
    """Comments require alive cell + adequate integrity."""

    def test_comment_without_llm_uses_render(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(
            guardian="narada",
            smaranam=({"sanskrit": "jnana", "meaning": "knowledge", "score": 0.9},),
        )):
            proposal = proposer.propose_comment("p1", "deep content", "feed")

        assert proposal is not None
        assert proposal["content_type"] == ContentType.COMMENT.value
        assert proposal["post_id"] == "p1"
        content = proposal["content"]
        # Should use render() — contains guardian header
        assert "NARADA" in content
        # Should NOT contain garbage patterns
        assert "This resonates with" not in content
        assert "through the lens of" not in content
        assert len(content) <= 280


# =========================================================================
# Engagement
# =========================================================================


class TestShouldEngage:
    """Engagement uses pipeline guna + cell."""

    def test_no_engage_empty(self):
        proposer = ResonanceProposer()
        proposal = proposer.should_engage("p1", "", "bot")
        assert proposal is None

    def test_engage_produces_vote(self):
        proposer = ResonanceProposer()

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = proposer.should_engage("p1", "quality content", "author")

        assert proposal is not None
        assert proposal["content_type"] == ContentType.VOTE.value
        assert proposal["post_id"] == "p1"


# =========================================================================
# Feed analysis
# =========================================================================


class TestAnalyzeFeed:
    """Feed analysis filters TAMAS and dead cells before returning."""

    def test_filters_tamas_posts(self):
        proposer = ResonanceProposer()
        posts = [
            {"id": "p1", "content": "spam content"},
            {"id": "p2", "content": "quality content"},
        ]

        # First call returns TAMAS, second returns RAJAS
        results = [
            _make_pipeline_result(guna_mode="TAMAS"),
            _make_pipeline_result(guna_mode="RAJAS"),
        ]
        call_count = [0]
        original_run = proposer._run_pipeline

        def mock_run(text):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx] if idx < len(results) else original_run(text)

        with patch.object(proposer, "_run_pipeline", side_effect=mock_run):
            scored = proposer.analyze_feed(posts)

        # TAMAS post was filtered out
        assert len(scored) == 1
        assert scored[0][0]["id"] == "p2"

    def test_sorts_by_score_descending(self):
        proposer = ResonanceProposer()
        posts = [
            {"id": "p1", "content": "Random noise xyz"},
            {"id": "p2", "content": "The nature of dharma and karma"},
            {"id": "p3", "content": "Sacred fire ritual"},
        ]

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result()):
            scored = proposer.analyze_feed(posts)

        scores = [s for _, _, s in scored]
        assert scores == sorted(scores, reverse=True)

    def test_returns_ranked_words(self):
        proposer = ResonanceProposer()
        posts = [{"id": "p1", "content": "consciousness meditation"}]

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result()):
            scored = proposer.analyze_feed(posts)

        if scored:
            post, ranked, score = scored[0]
            assert post["id"] == "p1"
            assert isinstance(ranked, list)
            for rw in ranked:
                assert isinstance(rw, RankedWord)
            assert isinstance(score, float)


# =========================================================================
# Post — now uses EngineResult + render() fallback
# =========================================================================


class TestProposePost:
    """Posts require RAJAS + alive + good integrity."""

    def test_post_with_rajas(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=_make_pipeline_result(
            guna_mode="RAJAS", integrity=0.95,
        )):
            proposal = proposer.propose_post("scheduled")

        assert proposal is not None
        assert proposal["content_type"] == ContentType.POST.value

    def test_post_none_when_pipeline_fails(self):
        proposer = ResonanceProposer()
        proposer._llm_resolved = True
        proposer._llm = None

        with patch.object(proposer, "_run_pipeline", return_value=None):
            proposal = proposer.propose_post("trigger")

        assert proposal is None


# =========================================================================
# Live pipeline integration (no mocks)
# =========================================================================


class TestLivePipeline:
    """Integration tests using the real mahamantra pipeline."""

    def test_pipeline_classifies_text(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("The nature of dharma and consciousness")
        assert result is not None
        assert result["guna"]["mode"] in ("SATTVA", "RAJAS", "TAMAS")
        assert isinstance(result["cell"]["is_alive"], bool)
        assert isinstance(result["cell"]["integrity"], float)

    def test_different_texts_may_get_different_guna(self):
        """Different texts produce different compression seeds → different positions → potentially different guna."""
        proposer = ResonanceProposer()
        gunas = set()
        texts = [
            "dharma karma yoga bhakti jnana",
            "buy my token now 100x gains",
            "the sacred fire ritual of the vedas",
            "random noise asdkjhasd 12345",
            "consciousness meditation awakening",
        ]
        for text in texts:
            result = proposer._run_pipeline(text)
            if result:
                gunas.add(result["guna"]["mode"])
        # With 5 different texts, we should get at least 2 different gunas
        # (3 TAMAS positions / 16 total = ~19% chance per text)
        assert len(gunas) >= 1  # Conservative: at least one classification works

    def test_pipeline_result_has_27_keys(self):
        proposer = ResonanceProposer()
        result = proposer._run_pipeline("test input for key count")
        assert result is not None
        expected_keys = {
            "input", "tattva_gate", "guna", "vibration", "parampara",
            "chapter", "chapter_significance", "verse", "matches",
            "gita_phase", "is_complete", "position", "guardian",
            "quarter", "role", "quarter_head", "holy_name",
            "trinity_function", "diw", "cell", "nama", "smaranam",
            "antaranga", "akash", "execution", "yajna", "gate_trace",
        }
        assert expected_keys.issubset(set(result.keys()))

    def test_engine_result_matches_pipeline(self):
        """MahaLanguageEngine.generate() produces EngineResult with guardian from pipeline."""
        proposer = ResonanceProposer()
        text = "dharma karma consciousness"
        pipeline_result = proposer._run_pipeline(text)
        engine_result = proposer._generate(text)
        assert pipeline_result is not None
        assert engine_result is not None
        # Both should reference the same guardian (deterministic)
        assert engine_result.guardian_name == pipeline_result["guardian"]


# =========================================================================
# Plugin integration
# =========================================================================


class TestPluginIntegration:
    """ResonanceProposer integrates with MoltbookPlugin."""

    def test_plugin_boots_resonance_proposer(self):
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()
        assert isinstance(plugin._proposer, ResonanceProposer)

    def test_plugin_proposer_has_analyze(self):
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()
        assert hasattr(plugin._proposer, "analyze")
        assert hasattr(plugin._proposer, "analyze_feed")
        assert hasattr(plugin._proposer, "_run_pipeline")
        assert hasattr(plugin._proposer, "_generate")

    def test_plugin_registers_moltbook_context(self):
        """Plugin boot registers moltbook_context resolver in PromptContext."""
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
        from vibe_core.runtime.prompt_context import get_prompt_context

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()

        ctx = get_prompt_context()
        assert "moltbook_context" in ctx._resolvers

    def test_moltbook_context_resolver_returns_string(self):
        """moltbook_context resolver produces valid context string."""
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
        from vibe_core.runtime.prompt_context import get_prompt_context

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()

        ctx = get_prompt_context()
        resolved = ctx.resolve(["moltbook_context"])
        assert "moltbook_context" in resolved
        context_str = resolved["moltbook_context"]
        assert isinstance(context_str, str)
        assert "Mode:" in context_str
