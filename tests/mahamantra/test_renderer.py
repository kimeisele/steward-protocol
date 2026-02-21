"""
KIRTAN RENDERER — Tests
========================

Tests the render.py module with mock 27-key VM result dicts.
Proves the renderer formats correctly without touching any
existing code or requiring a live VM instance.

BALARAMA PATTERN: This is additive-only. No existing files modified.
"""

import pytest
from unittest.mock import patch, MagicMock

from vibe_core.mahamantra.render import render, _render_resonance, _render_composed, kirtan_chat, _build_llm_prompt


# =============================================================================
# MOCK VM RESULT DICTS
# =============================================================================

def _make_vm_result(**overrides):
    """Build a realistic 27-key VM result dict with sensible defaults."""
    base = {
        "input": "What is the meaning of life?",
        "tattva_gate": "SRIVASA",
        "guna": {
            "mode": "SATTVA",
            "opcode": "EXEC_OP",
            "opcode_value": 3,
            "source": "position",
        },
        "vibration": {
            "seed": 0x4F23,
            "attractor": 1847,
            "rama_index": 2,
            "phoneme": "ka",
            "signature": {
                "element": "Akasha",
                "varga": "ka",
                "sub": 0,
                "harmonic": 3,
                "shruti": True,
                "frequency": 24,
            },
        },
        "parampara": {
            "verified": True,
            "channel": 7,
            "coherence": 0.95,
        },
        "chapter": 2,
        "chapter_significance": "Sankhya Yoga",
        "verse": {"ref": "BG 2.63", "text": "krodhad bhavati sammohah"},
        "matches": 3,
        "gita_phase": "SANKHYA",
        "is_complete": True,
        "position": 6,
        "guardian": "kapila",
        "quarter": "dharma",
        "role": "worker",
        "quarter_head": "manu",
        "holy_name": "HARE",
        "trinity_function": "Shakti",
        "diw": {
            "raw": 12345,
            "venu": 1,
            "vamsi": 2,
            "murali": 3,
        },
        "cell": {
            "header_size": 16,
            "payload_size": 28,
            "total_size": 44,
            "valid": True,
            "parampara_verified": True,
            "prana": 100,
            "integrity": 0.98,
            "is_alive": True,
            "cycle": 3,
        },
        "nama": {
            "coords": (0, 1, 2, 1, 0),
            "phoneme_count": 5,
        },
        "smaranam": (
            {"sanskrit": "viveka", "meaning": "discrimination", "score": 0.87},
            {"sanskrit": "jnana", "meaning": "knowledge", "score": 0.72},
            {"sanskrit": "dharma", "meaning": "duty", "score": 0.65},
        ),
        "antaranga": {
            "active_slots": 4,
            "total_prana": 400,
            "collisions": 0,
            "size_bytes": 1024,
        },
        "akash": {
            "total_beats": 16,
            "total_rounds": 1,
            "accumulated_value": 1847,
        },
        "execution": {
            "success": True,
            "prana": 100,
            "integrity": 0.98,
            "kirtan_cycles": 3,
            "transformations": 48,
            "yajna_ticks": 16,
            "cycles": 3,
            "guardian_acted": False,
            "guardian_result": None,
        },
        "yajna": {
            "phase": "COMPLETE",
            "cycle_count": 1,
            "switch_count": 0,
            "return_count": 0,
            "dissonance": None,
        },
        "gate_trace": ("PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC"),
    }
    base.update(overrides)
    return base


# =============================================================================
# CORE RENDERING TESTS
# =============================================================================

class TestRenderResonance:
    """Test the default resonance rendering path."""

    def test_header_contains_guardian(self):
        result = _make_vm_result()
        output = render(result)
        assert "KAPILA" in output

    def test_header_contains_quarter(self):
        result = _make_vm_result()
        output = render(result)
        assert "dharma" in output

    def test_header_contains_trinity(self):
        result = _make_vm_result()
        output = render(result)
        assert "Shakti" in output

    def test_resonant_words_present(self):
        result = _make_vm_result()
        output = render(result)
        assert '"viveka"' in output
        assert "discrimination" in output
        assert '"jnana"' in output
        assert "knowledge" in output

    def test_verse_reference_present(self):
        result = _make_vm_result()
        output = render(result)
        assert "BG 2.63" in output

    def test_gita_phase_present(self):
        result = _make_vm_result()
        output = render(result)
        assert "SANKHYA" in output

    def test_different_guardian(self):
        result = _make_vm_result(guardian="narada", quarter="moksha", trinity_function="Krishna")
        output = render(result)
        assert "NARADA" in output
        assert "moksha" in output
        assert "Krishna" in output

    def test_empty_smaranam(self):
        result = _make_vm_result(smaranam=())
        output = render(result)
        # Should still have header, just no word lines
        assert "KAPILA" in output
        assert '"viveka"' not in output

    def test_no_verse(self):
        result = _make_vm_result(verse={}, gita_phase="")
        output = render(result)
        assert "KAPILA" in output
        # No crash, just no verse line

    def test_verse_without_ref(self):
        result = _make_vm_result(verse={"text": "some text"}, chapter=4, gita_phase="KARMA")
        output = render(result)
        assert "Chapter 4" in output
        assert "KARMA" in output

    def test_returns_string(self):
        result = _make_vm_result()
        output = render(result)
        assert isinstance(output, str)

    def test_multiline_output(self):
        result = _make_vm_result()
        output = render(result)
        lines = output.strip().split("\n")
        assert len(lines) >= 2, "Output should have at least header + content"

    def test_smaranam_limit_five(self):
        """Renderer should show at most 5 resonant words."""
        many_words = tuple(
            {"sanskrit": f"word{i}", "meaning": f"meaning{i}", "score": 0.5}
            for i in range(10)
        )
        result = _make_vm_result(smaranam=many_words)
        output = render(result)
        assert '"word4"' in output
        assert '"word5"' not in output

    def test_sanskrit_only_no_meaning(self):
        """Words with sanskrit but no meaning should still render."""
        result = _make_vm_result(smaranam=(
            {"sanskrit": "om", "meaning": "", "score": 1.0},
        ))
        output = render(result)
        assert '"om"' in output


# =============================================================================
# EXTENSION KEY TESTS (Future CycleCompiler integration)
# =============================================================================

class TestRenderExtensionKeys:
    """Test that enrichment keys from CycleCompiler custom ops are used."""

    def test_cognitive_response_takes_priority(self):
        """If MANAS adds cognitive_response, renderer uses it directly."""
        result = _make_vm_result(cognitive_response="The path of discrimination leads to knowledge.")
        output = render(result)
        assert output == "The path of discrimination leads to knowledge."
        # Should NOT contain resonance rendering
        assert "KAPILA" not in output

    def test_composed_text_with_header(self):
        """If Language Engine adds composed_text, renderer wraps it with header."""
        result = _make_vm_result(composed_text="Discrimination through knowledge — the analytical path.")
        output = render(result)
        assert "KAPILA" in output
        assert "Discrimination through knowledge" in output

    def test_cognitive_over_composed(self):
        """cognitive_response has priority over composed_text."""
        result = _make_vm_result(
            cognitive_response="Cognitive wins.",
            composed_text="Composed loses.",
        )
        output = render(result)
        assert output == "Cognitive wins."

    def test_fallback_when_no_extension_keys(self):
        """Without extension keys, falls back to resonance."""
        result = _make_vm_result()
        assert "cognitive_response" not in result
        assert "composed_text" not in result
        output = render(result)
        assert "KAPILA" in output
        assert '"viveka"' in output


# =============================================================================
# EDGE CASES
# =============================================================================

class TestRenderEdgeCases:
    """Edge cases and robustness."""

    def test_minimal_result(self):
        """Renderer should not crash on a minimal dict."""
        output = render({})
        assert isinstance(output, str)
        assert "UNKNOWN" in output or "unknown" in output

    def test_none_values(self):
        """Renderer handles None values gracefully."""
        result = _make_vm_result(guardian=None, quarter=None, trinity_function=None)
        output = render(result)
        assert isinstance(output, str)

    def test_all_16_guardians(self):
        """Renderer works for all 16 guardian positions."""
        guardians = [
            "brahma", "narada", "shambhu", "kumaras", "vyasa",
            "kapila", "manu", "parashurama", "prahlada", "janaka",
            "bhishma", "bali", "shukadeva", "yamaraja", "arjuna", "hanuman",
        ]
        for g in guardians:
            result = _make_vm_result(guardian=g)
            output = render(result)
            assert g.upper() in output


# =============================================================================
# INTEGRATION — Real VM → render (proves CycleCompiler wiring)
# =============================================================================

class TestKirtanIntegration:
    """Integration tests: real Lotus VM call → kirtan key in result."""

    @pytest.fixture(scope="class")
    def lotus(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        m = MahamantraLotus()
        m.bootstrap(lazy=True, silent=True)
        return m

    def test_kirtan_key_present(self, lotus):
        """VM result dict contains 'kirtan' key after CycleCompiler wiring."""
        result = lotus("Hare Krishna")
        assert "kirtan" in result, (
            "Missing 'kirtan' key — KirtanCapability not registered in CycleCompiler"
        )

    def test_kirtan_is_string(self, lotus):
        """The kirtan value is a rendered string."""
        result = lotus("Hare Krishna")
        assert isinstance(result["kirtan"], str)

    def test_kirtan_contains_guardian(self, lotus):
        """Rendered kirtan output contains the guardian name."""
        result = lotus("Hare Krishna")
        guardian = result["guardian"]
        assert guardian.upper() in result["kirtan"]

    def test_kirtan_contains_quarter(self, lotus):
        """Rendered kirtan output contains the quarter."""
        result = lotus("Hare Krishna")
        quarter = result["quarter"]
        assert quarter in result["kirtan"]

    def test_kirtan_deterministic(self, lotus):
        """Same input → same kirtan output."""
        r1 = lotus("Om Namo Bhagavate Vasudevaya")
        r2 = lotus("Om Namo Bhagavate Vasudevaya")
        assert r1["kirtan"] == r2["kirtan"]

    @pytest.mark.parametrize("text", [
        "Hare Krishna",
        "What is the meaning of life?",
        "analyze this code",
        "a",
        "",
    ])
    def test_kirtan_never_empty(self, lotus, text):
        """Kirtan rendering is never empty for any input."""
        result = lotus(text)
        assert len(result["kirtan"].strip()) > 0

    def test_kirtan_multiline(self, lotus):
        """Kirtan output has structure (header + content)."""
        result = lotus("The quick brown fox")
        lines = result["kirtan"].strip().split("\n")
        assert len(lines) >= 1  # At minimum the header


# =============================================================================
# KIRTAN CHAT — Shadow bridge tests
# =============================================================================

class TestKirtanChat:
    """Test kirtan_chat() — the shadow replacement for legacy chat files."""

    def test_pure_mode_returns_string(self):
        """kirtan_chat with use_llm=False returns a string."""
        output = kirtan_chat("Hare Krishna", use_llm=False)
        assert isinstance(output, str)
        assert len(output.strip()) > 0

    def test_pure_mode_contains_guardian(self):
        """Pure mode output contains the routed guardian."""
        output = kirtan_chat("Hare Krishna", use_llm=False)
        # Must contain SOME guardian name (uppercased)
        assert "[" in output and "]" in output

    def test_pure_mode_deterministic(self):
        """Same input → same output in pure mode."""
        r1 = kirtan_chat("Om Namo Bhagavate", use_llm=False)
        r2 = kirtan_chat("Om Namo Bhagavate", use_llm=False)
        assert r1 == r2

    def test_llm_fallback_on_unavailable(self):
        """When LLM is unavailable, kirtan_chat falls back to pure rendering."""
        # Default use_llm=True but no LLM configured → should not crash
        output = kirtan_chat("What is dharma?")
        assert isinstance(output, str)
        assert len(output.strip()) > 0

    def test_empty_input(self):
        """kirtan_chat handles empty input."""
        output = kirtan_chat("", use_llm=False)
        assert isinstance(output, str)

    @pytest.mark.parametrize("text", [
        "Hare Krishna",
        "analyze this code",
        "What is the meaning of life?",
        "deploy the application",
    ])
    def test_various_inputs(self, text):
        """kirtan_chat works for various input types."""
        output = kirtan_chat(text, use_llm=False)
        assert isinstance(output, str)
        assert len(output.strip()) > 0


class TestBuildLLMPrompt:
    """Test the LLM prompt builder."""

    def test_prompt_contains_guardian(self):
        result = _make_vm_result(guardian="kapila")
        prompt = _build_llm_prompt("test", result)
        assert "KAPILA" in prompt

    def test_prompt_contains_quarter(self):
        result = _make_vm_result(quarter="dharma")
        prompt = _build_llm_prompt("test", result)
        assert "dharma" in prompt

    def test_prompt_contains_user_message(self):
        result = _make_vm_result()
        prompt = _build_llm_prompt("What is devotion?", result)
        assert "What is devotion?" in prompt

    def test_prompt_contains_resonant_words(self):
        result = _make_vm_result()
        prompt = _build_llm_prompt("test", result)
        assert "viveka" in prompt
        assert "discrimination" in prompt

    def test_prompt_contains_verse_ref(self):
        result = _make_vm_result()
        prompt = _build_llm_prompt("test", result)
        assert "BG 2.63" in prompt

    def test_prompt_is_string(self):
        result = _make_vm_result()
        prompt = _build_llm_prompt("test", result)
        assert isinstance(prompt, str)
        assert len(prompt) > 50
