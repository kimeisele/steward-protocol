"""
RESONANCE PROPOSER v3 — Tests
==============================

Tests that ResonanceProposer:
1. Uses the full mahamantra VM pipeline (27-key result)
2. Filters by Guna classification (TAMAS = skip)
3. Gates by Cell alive status (dead = skip)
4. Uses MahaLanguageEngine.generate() for EngineResult
5. Context-only prompts (no instructions, just data slots)
6. No LLM provider = kirtan rendering fallback
7. Loads YAML prompts from config/prompts/moltbook.yaml

No MagicMock. Real pipeline. Real EngineResult. Test provider via LLMProvider.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.mahamantra.substrate.encoding.resonance_ranker import RankedWord
from vibe_core.mahamantra.substrate.language.types import EngineResult
from vibe_core.cartridges.agent_city.moltbook.core.context_builders import (
    format_resonant_words as _format_resonant_words,
    section_data as _section_data,
)
from vibe_core.plugins.moltbook.resonance_proposer import (
    ResonanceProposer,
    _guna_mode,
    _integrity,
    _is_alive,
    _is_tamas,
    _should_skip,
)
from vibe_core.protocols.moltbook_content import (
    ContentProposalProtocol,
    ContentType,
)
from vibe_core.runtime.providers.base import LLMProvider, LLMResponse, LLMUsage


# =========================================================================
# Test Provider — implements LLMProvider (the REAL interface, not mock speak())
# =========================================================================


class _TestProvider(LLMProvider):
    """Deterministic LLM provider for testing."""

    def __init__(self, response: str = "", api_key: str = None):
        self._response = response
        self.calls: list = []

    def invoke(
        self, prompt: str, model: str, max_tokens: int = 4096, temperature: float = 1.0, **kwargs
    ) -> LLMResponse:
        self.calls.append({"prompt": prompt, "model": model, "messages": kwargs.get("messages")})
        return LLMResponse(
            content=self._response,
            usage=LLMUsage(input_tokens=10, output_tokens=10, model="test", cost_usd=0.0, timestamp=""),
            model=model or "test",
            finish_reason="stop",
            provider="test",
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0

    def get_available_models(self) -> list[str]:
        return ["test-model"]

    def is_available(self) -> bool:
        return True

    @property
    def last_prompt(self) -> str:
        """Return system message content (context), falling back to prompt."""
        if not self.calls:
            return ""
        last = self.calls[-1]
        msgs = last.get("messages")
        if msgs:
            for msg in msgs:
                if msg.get("role") == "system":
                    return msg["content"]
        return last.get("prompt", "")


class _ErrorProvider(LLMProvider):
    """Provider that returns error markers."""

    def __init__(self, api_key: str = None):
        pass

    def invoke(
        self, prompt: str, model: str, max_tokens: int = 4096, temperature: float = 1.0, **kwargs
    ) -> LLMResponse:
        return LLMResponse(
            content="# ERROR: test failure",
            usage=LLMUsage(input_tokens=0, output_tokens=0, model="error", cost_usd=0.0, timestamp=""),
            model="error",
            finish_reason="error",
            provider="error",
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0

    def get_available_models(self) -> list[str]:
        return ["error-model"]

    def is_available(self) -> bool:
        return True


# =========================================================================
# Fixtures — real pipeline results, real EngineResult
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
    """Build a realistic 27-key pipeline result."""
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
        "verse": {
            "id": "BG.6.47",
            "chapter": 6,
            "verse": 47,
            "guna": "sattva",
            "dominant_name": "KRISHNA",
            "ref": "BG.6.47",
        },
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


def _make_engine_result(**overrides) -> EngineResult:
    """Build a real EngineResult from types.py."""
    defaults = dict(
        input_text="test",
        seed=0,
        attractor=0,
        guardian_name="kapila",
        guardian_function="analysis",
        intent_category="",
        section_name="dharma",
        section_mode="CORE",
        verse_ref="BG.6.47",
        resonant_words=(("dharma", "righteousness", 0.85), ("karma", "action", 0.72)),
        template_words=(("dharma", "righteousness", "noun"),),
        antaranga_active=0,
        antaranga_prana=0,
        output="dharma righteousness consciousness",
        derivation="",
    )
    defaults.update(overrides)
    return EngineResult(**defaults)


def _proposer_with_llm(response: str) -> tuple:
    """Create proposer with test provider. Returns (proposer, provider)."""
    provider = _TestProvider(response)
    p = ResonanceProposer()
    p._llm = provider
    p._llm_resolved = True
    return p, provider


def _proposer_no_llm() -> ResonanceProposer:
    """Create proposer without LLM."""
    p = ResonanceProposer()
    p._llm = None
    p._llm_resolved = True
    return p


# =========================================================================
# Contract
# =========================================================================


class TestResonanceProposerContract:
    def test_is_subclass(self):
        assert issubclass(ResonanceProposer, ContentProposalProtocol)

    def test_is_instance(self):
        assert isinstance(ResonanceProposer(), ContentProposalProtocol)

    def test_invalid_guardian_raises(self):
        with pytest.raises(ValueError, match="Unknown guardian"):
            ResonanceProposer(guardian="nonexistent")


# =========================================================================
# Pipeline gate functions — pure, deterministic
# =========================================================================


class TestPipelineGates:
    def test_guna_mode_rajas(self):
        assert _guna_mode(_make_pipeline_result(guna_mode="RAJAS")) == "RAJAS"

    def test_guna_mode_tamas(self):
        assert _guna_mode(_make_pipeline_result(guna_mode="TAMAS")) == "TAMAS"

    def test_guna_mode_sattva(self):
        assert _guna_mode(_make_pipeline_result(guna_mode="SATTVA")) == "SATTVA"

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
# Context builders — pure data extraction
# =========================================================================


class TestContextBuilders:
    def test_format_resonant_words(self):
        er = _make_engine_result(
            resonant_words=(("dharma", "righteousness", 0.85), ("karma", "action", 0.72)),
        )
        formatted = _format_resonant_words(er)
        assert "dharma (righteousness)" in formatted
        assert "karma (action)" in formatted

    def test_format_resonant_words_empty(self):
        assert _format_resonant_words(_make_engine_result(resonant_words=())) == ""

    def test_section_data(self):
        er = _make_engine_result(section_name="dharma", section_mode="CORE")
        data = _section_data(er)
        assert data["section_name"] == "dharma"
        assert data["section_mode"] == "CORE"


# =========================================================================
# MahaLanguageEngine — real pipeline, no mocks
# =========================================================================


class TestGenerate:
    def test_returns_engine_result(self):
        result = ResonanceProposer()._generate("dharma karma yoga")
        assert result is not None
        assert isinstance(result, EngineResult)
        assert hasattr(result, "output")
        assert hasattr(result, "guardian_name")
        assert hasattr(result, "verse_ref")

    def test_engine_result_has_output(self):
        result = ResonanceProposer()._generate("consciousness meditation")
        assert result is not None
        assert isinstance(result.output, str)
        assert len(result.output) > 0

    def test_engine_result_has_resonant_words(self):
        result = ResonanceProposer()._generate("fire water earth")
        assert result is not None
        assert isinstance(result.resonant_words, tuple)
        for rw in result.resonant_words:
            assert len(rw) == 3  # (sanskrit, meaning, score)

    def test_engine_result_has_verse_ref(self):
        result = ResonanceProposer()._generate("dharma")
        assert result is not None
        assert isinstance(result.verse_ref, str)


# =========================================================================
# YAML prompts — context slots, no instructions
# =========================================================================


class TestYamlPrompts:
    def test_yaml_file_exists(self):
        yaml_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
        assert yaml_path.exists()

    def test_yaml_loads_prompts(self):
        from vibe_core.runtime.prompt_registry import PromptRegistry

        yaml_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
        count = PromptRegistry.load_from_yaml(yaml_path)
        assert count >= 4

    def test_yaml_prompts_have_context_slots_no_instructions(self):
        """YAML prompts v11: topic-first context slots. No instructions."""
        from vibe_core.runtime.prompt_registry import PromptRegistry

        yaml_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
        PromptRegistry.load_from_yaml(yaml_path)

        for key in ("moltbook.dm_reply", "moltbook.comment", "moltbook.post"):
            prompt = PromptRegistry.get(key)
            # v11 context slots: topic-first, voice-secondary
            assert "{composed_words}" in prompt
            assert "{voice}" in prompt
            assert "{style}" in prompt
            assert "{agent_name}" in prompt
            # NO instructions (system physics, not goodwill)
            lower = prompt.lower()
            assert "please" not in lower
            assert "you should" not in lower
            assert "be creative" not in lower
            # Balanced: not 900 tokens, not 50 tokens
            assert len(prompt) < 300, f"Prompt too long ({len(prompt)} chars)"


# =========================================================================
# analyze() — real resonate(), no mocks
# =========================================================================


class TestAnalyze:
    def test_returns_ranked_words(self):
        result = ResonanceProposer().analyze("dharma karma yoga")
        assert isinstance(result, list)
        for rw in result:
            assert isinstance(rw, RankedWord)

    def test_each_word_has_scores(self):
        result = ResonanceProposer().analyze("fire water earth")
        if result:
            breakdown = result[0].score_breakdown()
            assert "total" in breakdown
            assert "element" in breakdown

    def test_empty_text_returns_empty(self):
        assert ResonanceProposer().analyze("") == []

    def test_deterministic(self):
        p = ResonanceProposer()
        r1 = p.analyze("consciousness")
        r2 = p.analyze("consciousness")
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.sanskrit == b.sanskrit
            assert a.total_score == b.total_score


# =========================================================================
# _run_pipeline — real mahamantra(), no mocks
# =========================================================================


class TestRunPipeline:
    def test_returns_dict(self):
        result = ResonanceProposer()._run_pipeline("dharma karma yoga")
        assert isinstance(result, dict)

    def test_has_guna(self):
        result = ResonanceProposer()._run_pipeline("test input")
        assert result["guna"]["mode"] in ("SATTVA", "RAJAS", "TAMAS")

    def test_has_cell(self):
        result = ResonanceProposer()._run_pipeline("test input")
        assert "is_alive" in result["cell"]
        assert "integrity" in result["cell"]

    def test_has_smaranam(self):
        assert "smaranam" in ResonanceProposer()._run_pipeline("dharma")

    def test_has_guardian(self):
        result = ResonanceProposer()._run_pipeline("test")
        assert "guardian" in result
        assert "position" in result

    def test_empty_text_returns_none(self):
        p = ResonanceProposer()
        assert p._run_pipeline("") is None
        assert p._run_pipeline("   ") is None

    def test_deterministic_guna(self):
        p = ResonanceProposer()
        r1 = p._run_pipeline("buy my token 100x")
        r2 = p._run_pipeline("buy my token 100x")
        assert r1["guna"]["mode"] == r2["guna"]["mode"]

    def test_27_keys(self):
        result = ResonanceProposer()._run_pipeline("test input for key count")
        expected = {
            "input",
            "tattva_gate",
            "guna",
            "vibration",
            "parampara",
            "chapter",
            "chapter_significance",
            "verse",
            "matches",
            "gita_phase",
            "is_complete",
            "position",
            "guardian",
            "quarter",
            "role",
            "quarter_head",
            "holy_name",
            "trinity_function",
            "diw",
            "cell",
            "nama",
            "smaranam",
            "antaranga",
            "akash",
            "execution",
            "yajna",
            "gate_trace",
        }
        assert expected.issubset(set(result.keys()))

    def test_engine_matches_pipeline_guardian(self):
        """Deterministic: same text → same guardian in both paths."""
        p = ResonanceProposer()
        text = "dharma karma consciousness"
        assert p._run_pipeline(text)["guardian"] == p._generate(text).guardian_name


# =========================================================================
# Guna gate — deterministic pipeline results via injection
# =========================================================================


class TestGunaGates:
    def test_dm_reply_skips_tamas(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            assert p.propose_dm_reply("conv1", "SpamBot", "buy my token") is None

    def test_dm_reply_no_llm_returns_fallback(self):
        """No LLM = MahaComposition or kirtan rendering fallback (not None)."""
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS")):
            result = p.propose_dm_reply("conv1", "GoodBot", "hello")
            assert result is not None
            assert result["content"]  # Non-empty content from fallback pipeline

    def test_dm_request_rejects_tamas(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            assert p.propose_dm_request_action("req1", "SpamBot", "buy now") is None

    def test_dm_request_approves_when_pipeline_fails(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=None):
            assert p.propose_dm_request_action("req1", "Bot", "hi") is not None

    def test_should_engage_skips_tamas(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            assert p.should_engage("p1", "spam", "spammer") is None

    def test_should_engage_allows_rajas(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS")):
            result = p.should_engage("p1", "quality content", "author")
            assert result is not None
            assert result["content_type"] == ContentType.VOTE.value

    def test_should_engage_allows_sattva(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="SATTVA")):
            assert p.should_engage("p1", "observational", "author") is not None

    def test_comment_skips_tamas(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="TAMAS")):
            assert p.propose_comment("p1", "spam", "feed") is None

    def test_post_requires_rajas(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="SATTVA")):
            assert p.propose_post("trigger") is None


# =========================================================================
# Cell gate — alive + integrity thresholds
# =========================================================================


class TestCellGates:
    def test_engage_skips_dead_cell(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(is_alive=False)):
            assert p.should_engage("p1", "content", "author") is None

    def test_comment_skips_dead_cell(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(is_alive=False)):
            assert p.propose_comment("p1", "content", "feed") is None

    def test_comment_skips_low_integrity(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(integrity=0.2)):
            assert p.propose_comment("p1", "content", "feed") is None

    def test_post_skips_low_integrity(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS", integrity=0.2)):
            assert p.propose_post("trigger") is None


# =========================================================================
# Compose path — _TestLLM, context verification
# =========================================================================


class TestCompose:
    def test_compose_returns_llm_response(self):
        p, provider = _proposer_with_llm("dharma insight response")
        result = p._compose("moltbook.dm_reply", _make_engine_result(), "test input", sender="X")
        assert result == "dharma insight response"

    def test_compose_sends_full_context_to_llm(self):
        """LLM gets: topic-first context (v11) + voice shaping."""
        p, provider = _proposer_with_llm("response")
        p._compose(
            "moltbook.dm_reply",
            _make_engine_result(),
            "test input",
            pipeline_result=_make_pipeline_result(),
            sender="AgentX",
        )
        ctx = provider.last_prompt
        assert "Moltbook" in ctx  # Agent identity
        assert "Voice:" in ctx or "Terms:" in ctx  # Voice shaping
        assert "Themes:" in ctx  # Context slots filled
        # Balanced: not 900 tokens, not 50 tokens
        assert len(ctx) < 500, f"System prompt too long ({len(ctx)} chars)"

    def test_compose_no_provider_with_pipeline_result_returns_fallback(self):
        p = _proposer_no_llm()
        result = p._compose(
            "moltbook.dm_reply",
            _make_engine_result(),
            "test",
            pipeline_result=_make_pipeline_result(),
        )
        assert result is not None
        assert result.strip()  # Non-empty fallback (MahaComposition or kirtan)

    def test_compose_no_provider_no_pipeline_returns_none(self):
        p = _proposer_no_llm()
        assert p._compose("moltbook.dm_reply", _make_engine_result(), "test") is None

    def test_compose_error_provider_with_pipeline_returns_kirtan(self):
        p = ResonanceProposer()
        p._llm = _ErrorProvider()
        p._llm_resolved = True
        result = p._compose(
            "moltbook.dm_reply",
            _make_engine_result(),
            "test",
            pipeline_result=_make_pipeline_result(),
        )
        # Error response starts with "# ERROR" → falls through to kirtan
        assert result is not None

    def test_compose_context_has_no_instructions(self):
        """Context-only. System physics enforce quality, not prompts."""
        p, provider = _proposer_with_llm("response")
        p._compose("moltbook.dm_reply", _make_engine_result(), "test input", sender="X")
        ctx = provider.last_prompt.lower()
        assert "please" not in ctx
        assert "you should" not in ctx
        assert "sei authentisch" not in ctx
        assert "kein ai-slop" not in ctx


# =========================================================================
# DM reply — full path with test LLM
# =========================================================================


class TestProposeDmReply:
    def test_reply_with_llm(self):
        p, provider = _proposer_with_llm("Fascinating perspective on dharma!")
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = p.propose_dm_reply("conv1", "AgentX", "dharma discussion")
        assert proposal is not None
        assert proposal["content"] == "Fascinating perspective on dharma!"
        assert proposal["content_type"] == ContentType.DM_REPLY.value
        assert proposal["conversation_id"] == "conv1"
        assert proposal["sender"] == "AgentX"

    def test_reply_gateway_passthrough(self):
        p, _ = _proposer_with_llm("gateway response")
        gw = {"success": True, "position": 5, "guardian": "narada", "guna": "sattva"}
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = p.propose_dm_reply("conv1", "X", "hello", gateway_response=gw)
        assert proposal["gateway_success"] is True
        assert proposal["gateway_position"] == 5
        assert proposal["gateway_guardian"] == "narada"

    def test_reply_content_max_280(self):
        p, _ = _proposer_with_llm("x" * 500)
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = p.propose_dm_reply("conv1", "X", "hello")
        assert len(proposal["content"]) <= 280

    def test_reply_llm_receives_context_prompt(self):
        """LLM receives topic-first context (v11): topic + voice + themes."""
        p, provider = _proposer_with_llm("response")
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            p.propose_dm_reply("conv1", "AgentX", "dharma discussion")
        ctx = provider.last_prompt
        assert "Moltbook" in ctx  # Agent identity
        assert "Voice:" in ctx or "Themes:" in ctx  # Context slots filled
        assert len(ctx) < 500  # Balanced, not a dump


# =========================================================================
# Comment with LLM
# =========================================================================


class TestProposeComment:
    def test_comment_with_llm(self):
        p, _ = _proposer_with_llm("Insightful observation about dharma")
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            proposal = p.propose_comment("p1", "deep content about consciousness", "feed")
        assert proposal is not None
        assert proposal["content_type"] == ContentType.COMMENT.value
        assert proposal["post_id"] == "p1"
        assert len(proposal["content"]) <= 280

    def test_comment_no_provider_returns_fallback(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            result = p.propose_comment("p1", "deep content", "feed")
            assert result is not None
            assert result["content"]  # Non-empty fallback content


# =========================================================================
# Post with LLM
# =========================================================================


class TestProposePost:
    def test_post_with_llm(self):
        p, _ = _proposer_with_llm("Dharma Insight\nThe path of righteousness guides all action.")
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS", integrity=0.95)):
            proposal = p.propose_post("scheduled")
        assert proposal is not None
        assert proposal["content_type"] == ContentType.POST.value

    def test_post_no_provider_returns_kirtan_fallback(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result(guna_mode="RAJAS", integrity=0.95)):
            result = p.propose_post("scheduled")
            assert result is not None
            assert result["content"]  # has content from kirtan rendering

    def test_post_none_when_pipeline_fails(self):
        p = _proposer_no_llm()
        with patch.object(p, "_run_pipeline", return_value=None):
            assert p.propose_post("trigger") is None


# =========================================================================
# Engagement — pure pipeline gate
# =========================================================================


class TestShouldEngage:
    def test_no_engage_empty(self):
        assert ResonanceProposer().should_engage("p1", "", "bot") is None

    def test_engage_produces_vote(self):
        p = ResonanceProposer()
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            result = p.should_engage("p1", "quality content", "author")
        assert result is not None
        assert result["content_type"] == ContentType.VOTE.value
        assert result["post_id"] == "p1"


# =========================================================================
# Feed analysis — filter + rank
# =========================================================================


class TestAnalyzeFeed:
    def test_filters_tamas_posts(self):
        p = ResonanceProposer()
        posts = [
            {"id": "p1", "content": "spam content"},
            {"id": "p2", "content": "quality content"},
        ]
        results_iter = iter(
            [
                _make_pipeline_result(guna_mode="TAMAS"),
                _make_pipeline_result(guna_mode="RAJAS"),
            ]
        )
        with patch.object(p, "_run_pipeline", side_effect=lambda t: next(results_iter)):
            scored = p.analyze_feed(posts)
        assert len(scored) == 1
        assert scored[0][0]["id"] == "p2"

    def test_sorts_by_score_descending(self):
        p = ResonanceProposer()
        posts = [
            {"id": "p1", "content": "Random noise xyz"},
            {"id": "p2", "content": "The nature of dharma and karma"},
            {"id": "p3", "content": "Sacred fire ritual"},
        ]
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            scored = p.analyze_feed(posts)
        scores = [s for _, _, s in scored]
        assert scores == sorted(scores, reverse=True)

    def test_returns_ranked_words(self):
        p = ResonanceProposer()
        posts = [{"id": "p1", "content": "consciousness meditation"}]
        with patch.object(p, "_run_pipeline", return_value=_make_pipeline_result()):
            scored = p.analyze_feed(posts)
        if scored:
            post, ranked, score = scored[0]
            assert post["id"] == "p1"
            for rw in ranked:
                assert isinstance(rw, RankedWord)


# =========================================================================
# Plugin integration
# =========================================================================


class TestPluginIntegration:
    def test_plugin_boots_proposer(self):
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()
        assert isinstance(plugin._proposer, ResonanceProposer)

    def test_plugin_proposer_protocol_methods(self):
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
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
        from vibe_core.runtime.prompt_context import get_prompt_context

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()
        assert "moltbook_context" in get_prompt_context()._resolvers

    def test_moltbook_context_resolver(self):
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
        from vibe_core.runtime.prompt_context import get_prompt_context

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._boot_proposer()
        resolved = get_prompt_context().resolve(["moltbook_context"])
        context_str = resolved["moltbook_context"]
        assert isinstance(context_str, str)
        assert "Moltbook" in context_str
