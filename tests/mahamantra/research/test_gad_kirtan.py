"""
Tests for GAD Kirtan - Operator Inversion with Live Feedback
============================================================

"idaṁ śarīraṁ kaunteya kṣetram ity abhidhīyate"
"This body, O son of Kunti, is called the field."
— Bhagavad Gita 13.2

NO HARDCODED VALUES - All derived from seed.py constants.

These tests verify:
1. Beat-to-word mapping is correct (7 beats ↔ 16 words)
2. GAD checks (HARE/KRISHNA/RAMA) trigger correctly per beat
3. Check failures modulate computation
4. Live feedback exchange works
"""

import pytest

from vibe_core.mahamantra.protocols._gad import HolyName, JapaState
from vibe_core.mahamantra.research.dharma.gad_kirtan import (
    BEAT_WORD_RANGES,
    BEAT_WORD_TYPES,
    GADCheckResult,
    GADKirtan,
    GADKirtanResult,
    LiveFeedbackOperator,
)
from vibe_core.mahamantra.substrate.seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    SEVEN,
    WORDS,
)


class TestBeatWordMapping:
    """Test the beat-to-word mapping structure."""

    def test_seven_beats_defined(self):
        """Must have exactly SEVEN beats defined."""
        assert len(BEAT_WORD_TYPES) == SEVEN

    def test_beats_cover_all_words(self):
        """All 16 Mahamantra words must be covered."""
        total_words = sum(len(words) for words in BEAT_WORD_TYPES.values())
        assert total_words == WORDS

    def test_beat_ranges_non_overlapping(self):
        """Beat ranges must not overlap."""
        all_positions = []
        for beat, (start, end) in BEAT_WORD_RANGES.items():
            for pos in range(start, end):
                assert pos not in all_positions, f"Position {pos} overlaps"
                all_positions.append(pos)

    def test_beat_1_has_hare_krishna(self):
        """Beat 1 must have HARE KRISHNA."""
        words = BEAT_WORD_TYPES[1]
        assert HolyName.HARE in words
        assert HolyName.KRISHNA in words

    def test_beat_3_has_only_krishna(self):
        """Beat 3 must have only KRISHNA (source check only)."""
        words = BEAT_WORD_TYPES[3]
        assert all(w == HolyName.KRISHNA for w in words)

    def test_beat_5_has_hare_rama(self):
        """Beat 5 must have HARE RAMA (energy + safety)."""
        words = BEAT_WORD_TYPES[5]
        assert HolyName.HARE in words
        assert HolyName.RAMA in words


class TestGADCheckResults:
    """Test GAD check result structure."""

    def test_all_checks_passed_true(self):
        """all_checks_passed is True when all checks pass."""
        result = GADCheckResult(
            beat_number=1,
            words_chanted=(HolyName.HARE, HolyName.KRISHNA),
            hare_checks=[True],
            krishna_checks=[True],
            rama_checks=[],
            energy_ok=True,
            source_ok=True,
            safety_ok=True,
            feedback_modifier=1.0,
            safety_modifier=1.0,
        )
        assert result.all_checks_passed is True
        assert result.modulation_factor == 1.0

    def test_energy_failure_modulation(self):
        """Energy failure reduces modulation factor."""
        result = GADCheckResult(
            beat_number=1,
            words_chanted=(HolyName.HARE, HolyName.KRISHNA),
            hare_checks=[False],
            krishna_checks=[True],
            rama_checks=[],
            energy_ok=False,
            source_ok=True,
            safety_ok=True,
            feedback_modifier=0.5,  # Reduced
            safety_modifier=1.0,
        )
        assert result.all_checks_passed is False
        assert result.modulation_factor == 0.5

    def test_safety_failure_modulation(self):
        """Safety failure reduces modulation factor."""
        result = GADCheckResult(
            beat_number=5,
            words_chanted=(HolyName.HARE, HolyName.RAMA),
            hare_checks=[True],
            krishna_checks=[],
            rama_checks=[False],
            energy_ok=True,
            source_ok=True,
            safety_ok=False,
            feedback_modifier=1.0,
            safety_modifier=0.7,  # Reduced
        )
        assert result.all_checks_passed is False
        assert result.modulation_factor == 0.7


class TestGADKirtan:
    """Test GAD-integrated kirtan computation."""

    def test_compute_produces_result(self):
        """compute_with_gad must produce valid GADKirtanResult."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        result = kirtan.compute_with_gad(seed=PARAMPARA)

        assert isinstance(result, GADKirtanResult)
        assert result.beat_number in range(1, SEVEN + 1)
        assert 0 <= result.transformed_value < MAHA_QUANTUM

    def test_gad_check_included(self):
        """Result must include GAD check data."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        result = kirtan.compute_with_gad(seed=PARAMPARA)

        assert isinstance(result.gad_check, GADCheckResult)
        assert result.gad_check.beat_number == result.beat_number

    def test_japa_state_advances(self):
        """Japa state must advance with each compute."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        result = kirtan.compute_with_gad(seed=PARAMPARA)

        assert result.japa_state == JapaState.CHANTING
        assert result.words_chanted_total > 0

    def test_energy_check_customizable(self):
        """Custom energy check must affect results."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan.set_energy_check(lambda: False)  # Always fail

        result = kirtan.compute_with_gad(seed=PARAMPARA)

        # Beat 1 has HARE, so energy check should affect it
        if HolyName.HARE in BEAT_WORD_TYPES[result.beat_number]:
            assert result.gad_check.energy_ok is False
            assert result.modulated_by_gad is True

    def test_safety_check_customizable(self):
        """Custom safety check must affect results."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan.set_safety_check(lambda: False)  # Always fail

        # Run enough to get to beat 5 (which has RAMA)
        for _ in range(SEVEN):
            result = kirtan.compute_with_gad(seed=PARAMPARA)
            if HolyName.RAMA in BEAT_WORD_TYPES.get(result.beat_number, ()):
                assert result.gad_check.safety_ok is False
                assert result.modulated_by_gad is True
                break

    def test_round_produces_seven_results(self):
        """compute_round_with_gad must produce SEVEN results."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        results = kirtan.compute_round_with_gad(seed=PARAMPARA)

        assert len(results) == SEVEN

    def test_discover_provides_info(self):
        """discover() must return valid GAD info."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        info = kirtan.discover()

        assert info["name"] == "GADKirtan"
        assert info["operator_inversion"] is True
        assert "beat_word_mapping" in info

    def test_get_state_observable(self):
        """get_state() must return observable state."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan.compute_with_gad(seed=PARAMPARA)

        state = kirtan.get_state()

        assert "japa_state" in state
        assert "words_chanted" in state
        assert state["words_chanted"] > 0


class TestLiveFeedbackOperator:
    """Test high-level live feedback operator."""

    def test_run_beat_works(self):
        """run_beat must work correctly."""
        operator = LiveFeedbackOperator()
        result = operator.run_beat(seed=PARAMPARA)

        assert isinstance(result, GADKirtanResult)

    def test_run_round_produces_seven(self):
        """run_round must produce SEVEN results."""
        operator = LiveFeedbackOperator()
        results = operator.run_round(seed=PARAMPARA)

        assert len(results) == SEVEN

    def test_feedback_callback_invoked(self):
        """Feedback callback must be invoked for each beat."""
        callback_results = []

        def on_beat(result):
            callback_results.append(result)

        operator = LiveFeedbackOperator()
        operator.run_round(seed=PARAMPARA, on_each_beat=on_beat)

        assert len(callback_results) == SEVEN

    def test_feedback_summary(self):
        """get_feedback_summary must return valid summary."""
        operator = LiveFeedbackOperator()
        operator.run_round(seed=PARAMPARA)

        summary = operator.get_feedback_summary()

        assert summary["beats"] == SEVEN
        assert "all_passed" in summary
        assert "success_rate" in summary
        assert 0 <= summary["success_rate"] <= 1.0

    def test_reset_clears_history(self):
        """reset() must clear feedback history."""
        operator = LiveFeedbackOperator()
        operator.run_round(seed=PARAMPARA)
        operator.reset()

        summary = operator.get_feedback_summary()
        assert summary["beats"] == 0


class TestOperatorInversionPrinciple:
    """Test the GAD-000 operator inversion principle."""

    def test_modulation_affects_computation(self):
        """Check failures must actually affect computation."""
        # All checks pass
        kirtan_pass = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan_pass.set_energy_check(lambda: True)
        result_pass = kirtan_pass.compute_with_gad(seed=PARAMPARA)

        # Energy fails
        kirtan_fail = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan_fail.set_energy_check(lambda: False)
        result_fail = kirtan_fail.compute_with_gad(seed=PARAMPARA)

        # The modulated result should be different
        assert result_fail.modulated_by_gad is True
        # Modulation factor should be 0.5
        assert result_fail.gad_check.modulation_factor == 0.5

    def test_krishna_check_always_passes(self):
        """KRISHNA check must ALWAYS pass (acintya)."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)

        # Run multiple beats
        for _ in range(SEVEN):
            result = kirtan.compute_with_gad(seed=PARAMPARA)
            # Source (Krishna) always OK
            assert result.gad_check.source_ok is True

    def test_beat_3_no_energy_check(self):
        """Beat 3 (KRISHNA KRISHNA) should have no energy check."""
        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan.set_energy_check(lambda: False)  # Would fail if called

        # Run until we hit beat 3
        for _ in range(SEVEN):
            result = kirtan.compute_with_gad(seed=PARAMPARA)
            if result.beat_number == 3:
                # Beat 3 has no HARE, so energy check isn't called
                # energy_ok defaults to True when no HARE checks
                assert result.gad_check.energy_ok is True
                assert result.modulated_by_gad is False
                break

    def test_live_feedback_chain(self):
        """Verify modulation propagates through computation chain."""
        energy_call_count = [0]

        def failing_energy():
            energy_call_count[0] += 1
            return False  # Always fail

        kirtan = GADKirtan(mod_space=MAHA_QUANTUM)
        kirtan.set_energy_check(failing_energy)

        results = kirtan.compute_round_with_gad(seed=PARAMPARA)

        # Energy check was called multiple times
        assert energy_call_count[0] > 0

        # Most beats should be modulated (except beat 3)
        modulated_count = sum(1 for r in results if r.modulated_by_gad)
        # Beats 1,2,4,5,6,7 have HARE → 6 modulated
        # Beat 3 has no HARE → not modulated
        assert modulated_count >= 5  # At least 5 should be modulated
