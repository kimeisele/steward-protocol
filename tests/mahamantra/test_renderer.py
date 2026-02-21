"""
KIRTAN RENDERER — Tests
========================

Tests the render.py module with mock 27-key VM result dicts.
Proves the renderer formats correctly without touching any
existing code or requiring a live VM instance.

BALARAMA PATTERN: This is additive-only. No existing files modified.
"""

import pytest

from vibe_core.mahamantra.render import render, _render_resonance, _render_composed


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
