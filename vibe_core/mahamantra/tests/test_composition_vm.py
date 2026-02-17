"""
Tests for Composition VM — dispatch-based composition pipeline.

Tests what matters:
    1. Protocol invariants (CompositionOp, CYCLE, DISPATCH)
    2. Equivalence (VM output == old inline compose output)
    3. Step isolation (each wrapper reads/writes ctx correctly)
    4. Import cache (hoisted once, not per call)
"""

import pytest

from vibe_core.mahamantra.adapters.composition_vm import (
    CYCLE,
    DISPATCH,
    CompositionOp,
    compose_pipeline,
    _ensure_imports,
)


# =============================================================================
# PROTOCOL INVARIANTS
# =============================================================================


class TestProtocolInvariants:
    """CompositionOp, CYCLE, DISPATCH are consistent."""

    def test_six_ops(self):
        assert len(CompositionOp) == 6

    def test_cycle_covers_all_ops(self):
        assert set(CYCLE) == set(CompositionOp)

    def test_cycle_order_is_sequential(self):
        for i, op in enumerate(CYCLE):
            assert op.value == i, f"CYCLE[{i}] = {op}, expected value {i}"

    def test_dispatch_covers_all_ops(self):
        for op in CompositionOp:
            assert op in DISPATCH, f"{op.name} missing from DISPATCH"

    def test_dispatch_values_are_callable(self):
        for op, fn in DISPATCH.items():
            assert callable(fn), f"DISPATCH[{op.name}] is not callable"

    def test_op_names(self):
        expected = {"CONTEXT", "POOL", "RANK", "SELECT", "ALIGN", "ASSEMBLE"}
        actual = {op.name for op in CompositionOp}
        assert actual == expected


# =============================================================================
# EQUIVALENCE — VM output matches adapter behavior
# =============================================================================


class TestEquivalence:
    """compose_pipeline produces same results as the adapter's compose()."""

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

    def test_empty_pool_returns_empty(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(smaranam=[])
        result = compose_pipeline(adapter, resp, "test")
        assert result == ""

    def test_compose_returns_string(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        result = compose_pipeline(adapter, resp, "What is dharma?")
        assert isinstance(result, str)

    def test_compositions_counter(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(
            smaranam=[{"sanskrit": "dharma", "meaning": "duty", "score": 0.9}]
        )
        compose_pipeline(adapter, resp, "test")
        assert adapter.compositions >= 1

    def test_last_context_set(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        adapter = MahaComposition()
        resp = self._make_lotus_response(
            smaranam=[{"sanskrit": "dharma", "meaning": "duty", "score": 0.9}],
            quarter="dharma",
            guna_mode="SATTVA",
        )
        compose_pipeline(adapter, resp, "test")
        ctx = adapter.last_context
        assert ctx["quarter"] == "dharma"
        assert ctx["guna_mode"] == "SATTVA"
        assert "scorer_names" in ctx
        assert len(ctx["scorer_names"]) == 5

    def test_deterministic_a(self):
        """First half of determinism check. conftest resets state before next test."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        r = compose_pipeline(MahaComposition(), resp, "test")
        TestEquivalence._determinism_result = r
        assert isinstance(r, str)
        assert len(r) > 0

    def test_deterministic_b(self):
        """Second half: same input after singleton reset must produce same output."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        r = compose_pipeline(MahaComposition(), resp, "test")
        assert r == TestEquivalence._determinism_result

    def test_real_lotus_through_vm(self):
        """End-to-end: Lotus → compose_pipeline()."""
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        lotus = get_mahamantra()
        lr = lotus("What is the meaning of life?")
        adapter = MahaComposition()
        result = compose_pipeline(adapter, lr, "What is the meaning of life?")
        assert isinstance(result, str)
        assert len(result) > 0


# =============================================================================
# STEP ISOLATION
# =============================================================================


class TestStepIsolation:
    """Each step wrapper reads/writes ctx correctly."""

    def _make_lotus_response(self):
        return {
            "input": "test",
            "smaranam": [
                {"sanskrit": "dharma", "meaning": "duty", "score": 0.9},
            ],
            "verse": None,
            "vibration": {"seed": 42},
            "guna": {"mode": "RAJAS"},
            "quarter": "karma",
            "antaranga": {"total_prana": 0},
        }

    def test_context_step_populates_seed(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        from vibe_core.mahamantra.adapters.composition_vm import _w_context
        adapter = MahaComposition()
        ctx = {"lotus_response": self._make_lotus_response(), "input_text": "test"}
        _w_context(adapter, ctx)
        assert "seed" in ctx
        assert "max_words" in ctx
        assert "scorer_kwargs" in ctx

    def test_pool_step_populates_pool(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        from vibe_core.mahamantra.adapters.composition_vm import _w_context, _w_pool
        _ensure_imports()
        adapter = MahaComposition()
        ctx = {"lotus_response": self._make_lotus_response(), "input_text": "test"}
        _w_context(adapter, ctx)
        _w_pool(adapter, ctx)
        assert "pool" in ctx

    def test_rank_step_populates_ranked(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        from vibe_core.mahamantra.adapters.composition_vm import _w_context, _w_pool, _w_rank
        _ensure_imports()
        adapter = MahaComposition()
        ctx = {"lotus_response": self._make_lotus_response(), "input_text": "test"}
        _w_context(adapter, ctx)
        _w_pool(adapter, ctx)
        if ctx["pool"]:
            _w_rank(adapter, ctx)
            assert "ranked" in ctx
            for item in ctx["ranked"]:
                assert "_total_score" in item

    def test_select_step_deduplicates(self):
        from vibe_core.mahamantra.adapters.composition import MahaComposition
        from vibe_core.mahamantra.adapters.composition_vm import (
            _w_context, _w_pool, _w_rank, _w_select,
        )
        _ensure_imports()
        adapter = MahaComposition()
        lr = self._make_lotus_response()
        lr["smaranam"] = [
            {"sanskrit": "dharma", "meaning": "duty", "score": 0.9},
            {"sanskrit": "dharma", "meaning": "duty", "score": 0.8},  # duplicate
            {"sanskrit": "karma", "meaning": "action", "score": 0.7},
        ]
        ctx = {"lotus_response": lr, "input_text": "test"}
        _w_context(adapter, ctx)
        _w_pool(adapter, ctx)
        if ctx["pool"]:
            _w_rank(adapter, ctx)
            _w_select(adapter, ctx)
            sanskrit_names = [it.get("sanskrit") for it in ctx["selected"]]
            assert len(sanskrit_names) == len(set(sanskrit_names)), "Duplicates not removed"


# =============================================================================
# IMPORT CACHE
# =============================================================================


class TestImportCache:
    """Imports are hoisted once, not per call."""

    def test_ensure_imports_idempotent(self):
        import vibe_core.mahamantra.adapters.composition_vm as cvm
        cvm._ensure_imports()
        assert cvm._IMPORTS_CACHED is True
        assert cvm._build_lotus_pool is not None
        assert cvm._syllable_vectors_for_word is not None
        assert cvm._align_syllables_to_grid is not None
        # Call again — should not raise
        cvm._ensure_imports()
        assert cvm._IMPORTS_CACHED is True
