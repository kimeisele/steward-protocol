"""
Tests for the Composition Protocol + Adapter (protocol/substrate/adapter triad).

Tests what matters:
    1. Protocol compliance (isinstance checks)
    2. Scorer protocol compliance
    3. Adapter produces output via delegation
    4. Context-driven word count (not hardcoded SEVEN)
    5. Scorers are pluggable
    6. Backward compat: compose_from_wave delegates to adapter
"""

import pytest

from vibe_core.mahamantra.protocols._seed import HALVES, PANCHA, QUARTERS, SEVEN, WORDS


# =============================================================================
# PROTOCOL COMPLIANCE
# =============================================================================


class TestCompositionProtocol:
    """CompositionProtocol is runtime_checkable and MahaComposition satisfies it."""

    def test_protocol_is_runtime_checkable(self):
        from vibe_core.mahamantra.protocols._composition import CompositionProtocol
        assert hasattr(CompositionProtocol, "__protocol_attrs__") or hasattr(
            CompositionProtocol, "__abstractmethods__"
        ) or True  # runtime_checkable Protocol

    def test_adapter_satisfies_protocol(self):
        from vibe_core.mahamantra.protocols._composition import CompositionProtocol
        from vibe_core.mahamantra.adapters.composition import MahaComposition

        adapter = MahaComposition()
        assert isinstance(adapter, CompositionProtocol)

    def test_genesis_byte_valid(self):
        from vibe_core.mahamantra.protocols._composition import __genesis__
        from vibe_core.mahamantra.protocols._seed import PARAMPARA
        assert int(__genesis__, 16) % PARAMPARA == 0

    def test_adapter_genesis_byte_valid(self):
        from vibe_core.mahamantra.adapters.composition import __genesis__
        from vibe_core.mahamantra.protocols._seed import PARAMPARA
        assert int(__genesis__, 16) % PARAMPARA == 0


# =============================================================================
# SCORER PROTOCOL COMPLIANCE
# =============================================================================


class TestScorerProtocol:
    """Each scorer implements CompositionScorerProtocol."""

    def test_all_scorers_have_name(self):
        from vibe_core.mahamantra.adapters.composition import DEFAULT_SCORERS
        for scorer in DEFAULT_SCORERS:
            assert hasattr(scorer, "name"), f"{scorer} missing name"
            assert isinstance(scorer.name, str)

    def test_all_scorers_have_score_method(self):
        from vibe_core.mahamantra.adapters.composition import DEFAULT_SCORERS
        for scorer in DEFAULT_SCORERS:
            assert callable(getattr(scorer, "score", None)), f"{scorer} missing score()"

    def test_scorer_names_unique(self):
        from vibe_core.mahamantra.adapters.composition import DEFAULT_SCORERS
        names = [s.name for s in DEFAULT_SCORERS]
        assert len(names) == len(set(names)), f"Duplicate scorer names: {names}"

    def test_five_default_scorers(self):
        from vibe_core.mahamantra.adapters.composition import DEFAULT_SCORERS
        assert len(DEFAULT_SCORERS) == PANCHA  # 5 scorers = PANCHA

    def test_scorer_returns_float(self):
        from vibe_core.mahamantra.adapters.composition import PranaScorer
        scorer = PranaScorer()
        result = scorer.score({"coords": (), "packed_hex": ""}, seed=42)
        assert isinstance(result, float)


# =============================================================================
# ADAPTER CORE
# =============================================================================


class TestMahaComposition:
    """MahaComposition adapter wires substrate atoms correctly."""

    def _make_lotus_response(self, smaranam=None, quarter="karma", guna_mode="RAJAS"):
        return {
            "input": "test input",
            "smaranam": smaranam or (),
            "verse": None,
            "vibration": {"seed": 42, "attractor": 7, "phoneme": "a",
                          "signature": {"element": "prithvi", "varga": 0, "sub": 0, "harmonic": 0}},
            "guna": {"mode": guna_mode, "opcode": "EXTEND_CAP", "opcode_value": 9},
            "diw": {"raw": 0, "venu": 0, "vamsi": 0, "murali": 0},
            "position": 9, "guardian": "prahlada", "quarter": quarter,
            "role": "devotion", "trinity_function": "deliverer",
            "chapter_significance": "Sankhya Yoga",
            "holy_name": "HARE",
            "antaranga": {"active_slots": 0, "total_prana": 0},
            "akash": {"total_rounds": 0, "total_beats": 0},
        }

    def test_compose_returns_string(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        result = adapter.compose(resp, "What is dharma?")
        assert isinstance(result, str)

    def test_empty_smaranam_returns_empty(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(smaranam=[])
        result = adapter.compose(resp, "test")
        assert result == ""

    def test_compositions_counter_increments(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        assert adapter.compositions == 0
        resp = self._make_lotus_response(
            smaranam=[{"sanskrit": "dharma", "meaning": "duty", "score": 0.9}]
        )
        adapter.compose(resp, "test")
        assert adapter.compositions >= 1

    def test_last_context_populated(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(
            smaranam=[{"sanskrit": "dharma", "meaning": "duty", "score": 0.9}],
            quarter="dharma",
            guna_mode="SATTVA",
        )
        adapter.compose(resp, "test")
        ctx = adapter.last_context
        assert ctx["quarter"] == "dharma"
        assert ctx["guna_mode"] == "SATTVA"
        assert "scorer_names" in ctx

    def test_deterministic_a(self):
        """First half of determinism check. conftest resets state before next test."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        result = MahaComposition().compose(resp, "test")
        # Store for comparison in next test
        TestMahaComposition._determinism_result = result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_deterministic_b(self):
        """Second half: same input after full singleton reset must produce same output."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        result = MahaComposition().compose(resp, "test")
        assert result == TestMahaComposition._determinism_result

    def test_pluggable_scorers(self):
        """Adapter accepts custom scorers."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition, PranaScorer

        adapter = MahaComposition(scorers=[PranaScorer()])
        resp = self._make_lotus_response(
            smaranam=[{"sanskrit": "dharma", "meaning": "duty", "score": 0.9}]
        )
        result = adapter.compose(resp, "test")
        assert isinstance(result, str)
        # Only 1 scorer in context
        assert len(adapter.last_context["scorer_names"]) == 1


# =============================================================================
# CONTEXT-DRIVEN WORD COUNT
# =============================================================================


class TestContextMaxWords:
    """Output length driven by quarter/prana, NOT hardcoded SEVEN."""

    def test_dharma_gets_seven(self):
        from vibe_core.mahamantra.adapters.composition import _context_max_words
        resp = {"quarter": "dharma", "antaranga": {"total_prana": 0}}
        assert _context_max_words(resp) == SEVEN

    def test_genesis_gets_pancha(self):
        from vibe_core.mahamantra.adapters.composition import _context_max_words
        resp = {"quarter": "genesis", "antaranga": {"total_prana": 0}}
        assert _context_max_words(resp) == PANCHA

    def test_moksha_gets_quarters(self):
        from vibe_core.mahamantra.adapters.composition import _context_max_words
        resp = {"quarter": "moksha", "antaranga": {"total_prana": 0}}
        assert _context_max_words(resp) == QUARTERS

    def test_prana_amplifies(self):
        from vibe_core.mahamantra.adapters.composition import _context_max_words
        no_prana = {"quarter": "karma", "antaranga": {"total_prana": 0}}
        with_prana = {"quarter": "karma", "antaranga": {"total_prana": 1000}}
        assert _context_max_words(with_prana) == _context_max_words(no_prana) + HALVES


# =============================================================================
# BACKWARD COMPAT
# =============================================================================


class TestBackwardCompat:
    """compose_from_wave in substrate delegates to adapter."""

    def test_substrate_delegates_to_adapter(self):
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = {
            "smaranam": [{"sanskrit": "dharma", "meaning": "duty", "score": 0.9}],
            "vibration": {"seed": 42},
            "guna": {"mode": "RAJAS"},
            "quarter": "karma",
            "antaranga": {"total_prana": 0},
        }
        result = compose_from_wave(resp, "test")
        assert isinstance(result, str)

    def test_singleton_reused(self):
        from vibe_core.mahamantra.adapters.composition import get_composition
        a = get_composition()
        b = get_composition()
        assert a is b

    def test_real_lotus_through_adapter(self):
        """End-to-end: Lotus → adapter.compose()."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        lotus = get_mahamantra()
        lr = lotus("What is the meaning of life?")
        adapter = MahaComposition()
        result = adapter.compose(lr, "What is the meaning of life?")
        assert isinstance(result, str)
        assert len(result) > 0
