"""
TEST: Orchestrator Adapter - Rhythmic Compute Contract
=======================================================

"kīrtanīyaḥ sadā hariḥ"
"One should always chant the holy name of the Lord."
— Śikṣāṣṭakam, Verse 3

WHAT WE TEST:
1. Seven Beats: Each round has exactly 7 beats
2. Mala Structure: 108 rounds × 7 beats = 756 ticks
3. Resonance: Builds over time
4. Determinism: Same seed → same sequence
5. Beat Pattern: CALL/RESPONSE pattern correct

THE CONTRACT: These tests GUARANTEE correct rhythmic orchestration.
"""

import pytest

from vibe_core.mahamantra.adapters.orchestrator import (
    Orchestrator,
    TickResult,
    RoundResult,
    MalaResult,
    BEATS_PER_ROUND,
    ROUNDS_PER_MALA,
    TICKS_PER_MALA,
    BEAT_PATTERN,
    tick,
    round_compute,
    mala_compute,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    MALA,
    SEVEN,
)


class TestOrchestratorConstants:
    """Test fundamental constants."""

    def test_beats_per_round_is_seven(self):
        """Each round should have SEVEN (7) beats."""
        assert BEATS_PER_ROUND == SEVEN
        assert BEATS_PER_ROUND == 7

    def test_rounds_per_mala_is_mala(self):
        """Mala should have MALA (108) rounds."""
        assert ROUNDS_PER_MALA == MALA
        assert ROUNDS_PER_MALA == 108

    def test_ticks_per_mala_calculation(self):
        """Ticks per mala = 7 × 108 = 756."""
        assert TICKS_PER_MALA == BEATS_PER_ROUND * ROUNDS_PER_MALA
        assert TICKS_PER_MALA == 756

    def test_beat_pattern_length(self):
        """Beat pattern should have 7 entries."""
        assert len(BEAT_PATTERN) == BEATS_PER_ROUND


class TestOrchestratorTick:
    """Test single tick operation."""

    def test_tick_returns_result(self):
        """tick() should return TickResult."""
        o = Orchestrator()
        result = o.tick(42)
        assert isinstance(result, TickResult)

    def test_tick_advances_beat(self):
        """Each tick should advance beat counter."""
        o = Orchestrator()
        r1 = o.tick(42)
        r2 = o.tick(42)
        assert r1.beat == 1
        assert r2.beat == 2

    def test_beat_wraps_at_seven(self):
        """Beat should wrap from 7 to 1."""
        o = Orchestrator()
        for _ in range(7):
            o.tick(42)
        r8 = o.tick(42)  # 8th tick
        assert r8.beat == 1  # Wrapped

    def test_round_increments_on_wrap(self):
        """Round should increment when beat wraps."""
        o = Orchestrator()
        for _ in range(7):
            r = o.tick(42)
        assert r.round_num == 1
        r8 = o.tick(42)
        assert r8.round_num == 2

    def test_tick_value_within_mod_space(self):
        """Tick value should be within mod space."""
        o = Orchestrator()
        for seed in range(100):
            result = o.tick(seed)
            assert 0 <= result.value < MAHA_QUANTUM


class TestOrchestratorRound:
    """Test round operation (7 beats)."""

    def test_round_returns_seven_ticks(self):
        """round() should execute exactly 7 ticks."""
        o = Orchestrator()
        result = o.round(42)
        assert len(result.ticks) == 7

    def test_round_ticks_are_sequential(self):
        """Round ticks should be beats 1-7."""
        o = Orchestrator()
        result = o.round(42)
        beats = [t.beat for t in result.ticks]
        assert beats == [1, 2, 3, 4, 5, 6, 7]

    def test_round_final_value_matches_last_tick(self):
        """Round final value should match last tick."""
        o = Orchestrator()
        result = o.round(42)
        assert result.final_value == result.ticks[-1].value


class TestOrchestratorMultipleRounds:
    """Test multiple rounds."""

    def test_rounds_executes_correct_count(self):
        """rounds() should execute specified count."""
        o = Orchestrator()
        results = o.rounds(42, count=3)
        assert len(results) == 3

    def test_rounds_chain_correctly(self):
        """Each round should start from previous round's final value."""
        o = Orchestrator()
        results = o.rounds(42, count=3)
        # Second round's seed should be first round's final value
        # (This is implicit in the algorithm)
        assert results[1].seed == results[0].final_value


class TestOrchestratorMala:
    """Test complete mala (108 rounds)."""

    def test_mala_returns_result(self):
        """mala() should return MalaResult."""
        o = Orchestrator()
        result = o.mala(42)
        assert isinstance(result, MalaResult)

    def test_mala_total_ticks_correct(self):
        """Mala should report 756 total ticks."""
        o = Orchestrator()
        result = o.mala(42)
        assert result.total_ticks == TICKS_PER_MALA

    def test_mala_resonance_builds(self):
        """Mala should build significant resonance."""
        o = Orchestrator()
        result = o.mala(42)
        # After 756 ticks, resonance should be substantial
        assert result.final_resonance > 0.5


class TestOrchestratorResonance:
    """Test resonance building."""

    def test_resonance_starts_at_zero(self):
        """Initial resonance should be 0."""
        o = Orchestrator()
        assert o.state["resonance"] == 0.0

    def test_resonance_increases_with_ticks(self):
        """Resonance should increase with each tick."""
        o = Orchestrator()
        o.tick(42)
        r1 = o.state["resonance"]
        o.tick(42)
        r2 = o.state["resonance"]
        assert r2 > r1

    def test_resonance_caps_at_one(self):
        """Resonance should never exceed 1.0."""
        o = Orchestrator()
        for _ in range(1000):
            o.tick(42)
        assert o.state["resonance"] <= 1.0


class TestOrchestratorReset:
    """Test reset functionality."""

    def test_reset_clears_state(self):
        """reset() should clear all state."""
        o = Orchestrator()
        o.tick(42)
        o.tick(42)
        o.reset()
        assert o.state["round"] == 0
        assert o.state["beat"] == 0
        assert o.state["resonance"] == 0.0


class TestOrchestratorBeatPattern:
    """Test beat pattern semantics."""

    def test_beat_pattern_has_call_response(self):
        """Pattern should include CALL and RESPONSE."""
        assert "CALL" in BEAT_PATTERN
        assert "RESPONSE" in BEAT_PATTERN

    def test_beat_pattern_has_immune(self):
        """Pattern should include IMMUNE beat (beat 3)."""
        assert "IMMUNE" in BEAT_PATTERN
        assert BEAT_PATTERN[2] == "IMMUNE"  # Beat 3 is immune

    def test_tick_reports_call_response(self):
        """Tick should report call/response status."""
        o = Orchestrator()
        result = o.tick(42)
        assert result.call_response in ("CALL", "RESPONSE", "IMMUNE")


class TestOrchestratorConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_tick_function(self):
        """tick() should work."""
        result = tick(42)
        assert isinstance(result, TickResult)

    def test_round_compute_function(self):
        """round_compute() should work."""
        result = round_compute(42)
        assert isinstance(result, RoundResult)

    def test_mala_compute_function(self):
        """mala_compute() should work."""
        result = mala_compute(42)
        assert isinstance(result, MalaResult)


class TestOrchestratorDeterminism:
    """Test deterministic behavior."""

    def test_same_seed_same_sequence(self):
        """Same seed should produce same sequence."""
        o1 = Orchestrator()
        o2 = Orchestrator()

        r1 = o1.round(42)
        r2 = o2.round(42)

        for i in range(7):
            assert r1.ticks[i].value == r2.ticks[i].value

    def test_deterministic_mala(self):
        """Complete mala should be deterministic."""
        o1 = Orchestrator()
        o2 = Orchestrator()

        m1 = o1.mala(42)
        m2 = o2.mala(42)

        assert m1.final_value == m2.final_value
        assert m1.attractor == m2.attractor
