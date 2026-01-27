"""
Tests for Maha 16-Step Sequencer - The Field/Observer Architecture
===================================================================

"idaṁ śarīraṁ kaunteya kṣetram ity abhidhīyate"
"This body, O son of Kunti, is called the field."
— Bhagavad Gita 13.2

NO HARDCODED VALUES - All derived from seed.py constants.

These tests verify:
1. 16-step field structure is correct
2. 7-beat observer overlay is correct
3. Operations are derived from position sums
4. Polyrhythm alignment (LCM = 112)
5. Structure equations hold
"""

import math

import pytest

from vibe_core.mahamantra.protocols._gad import HolyName
from vibe_core.mahamantra.research.dharma.maha_sequencer import (
    FULL_CYCLE,
    MAHAMANTRA_NAMES,
    MAHAMANTRA_PATTERN,
    OBSERVER_7_BEATS,
    SEQUENCER_16_STEPS,
    WEIGHT_HARE,
    WEIGHT_KRISHNA,
    WEIGHT_RAMA,
    CycleResult,
    Maha16StepSequencer,
    ObserverBeat,
    SequencerStep,
    StepOperation,
    StepResult,
    analyze_step_beat_mapping,
    get_beat_at_number,
    get_step_at_position,
)
from vibe_core.mahamantra.substrate.seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    NAVA,
    PARAMPARA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    SEVEN,
    TEN,
    WORDS,
)


class TestStructureEquations:
    """Test the fundamental structure equations derived from the Mahamantra."""

    def test_words_equals_sixteen(self):
        """WORDS must be 16."""
        assert WORDS == 16

    def test_seven_derivation(self):
        """SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7."""
        assert SEVEN == HARE_COUNT - KSETRAJNA
        assert SEVEN == 7

    def test_structure_equation_seven_plus_nava(self):
        """16 = 7 + 9 = SEVEN + NAVA."""
        assert WORDS == SEVEN + NAVA

    def test_structure_equation_double_seven_plus_halves(self):
        """16 = 7 + 7 + 2 = SEVEN + SEVEN + HALVES."""
        assert WORDS == SEVEN + SEVEN + HALVES

    def test_coprime(self):
        """16 and 7 must be coprime (GCD = 1)."""
        assert math.gcd(WORDS, SEVEN) == 1

    def test_lcm_is_112(self):
        """LCM(16, 7) = 112."""
        assert FULL_CYCLE == 112
        assert FULL_CYCLE == (WORDS * SEVEN) // math.gcd(WORDS, SEVEN)

    def test_words_mod_seven_is_halves(self):
        """16 mod 7 = 2 = HALVES."""
        assert WORDS % SEVEN == HALVES


class TestPositionSumDerivations:
    """Test that position sums correctly encode the operations."""

    def test_hare_position_sum(self):
        """HARE position sum = 70 = 7 × 10."""
        assert WEIGHT_HARE == POSITION_SUM_HARE
        assert WEIGHT_HARE == 70
        assert WEIGHT_HARE == SEVEN * TEN

    def test_krishna_position_sum(self):
        """KRISHNA position sum = 17 = 7 + 10."""
        assert WEIGHT_KRISHNA == POSITION_SUM_KRISHNA
        assert WEIGHT_KRISHNA == 17
        assert WEIGHT_KRISHNA == SEVEN + TEN

    def test_rama_position_sum(self):
        """RAMA position sum = 49 = 7²."""
        assert WEIGHT_RAMA == POSITION_SUM_RAMA
        assert WEIGHT_RAMA == 49
        assert WEIGHT_RAMA == SEVEN * SEVEN


class TestMahamantraPattern:
    """Test the 16-word Mahamantra pattern."""

    def test_pattern_has_16_words(self):
        """Pattern must have exactly WORDS (16) elements."""
        assert len(MAHAMANTRA_PATTERN) == WORDS

    def test_pattern_matches_mahamantra(self):
        """Pattern must match the actual Mahamantra."""
        expected = (
            "H",
            "K",
            "H",
            "K",  # Q1
            "K",
            "K",
            "H",
            "H",  # Q2
            "H",
            "R",
            "H",
            "R",  # Q3
            "R",
            "R",
            "H",
            "H",  # Q4
        )
        assert MAHAMANTRA_PATTERN == expected

    def test_names_enum_mapping(self):
        """MAHAMANTRA_NAMES must correctly map to HolyName enum."""
        assert len(MAHAMANTRA_NAMES) == WORDS
        for i, name in enumerate(MAHAMANTRA_NAMES):
            pattern = MAHAMANTRA_PATTERN[i]
            if pattern == "H":
                assert name == HolyName.HARE
            elif pattern == "K":
                assert name == HolyName.KRISHNA
            else:
                assert name == HolyName.RAMA


class TestSequencer16Steps:
    """Test the 16 sequencer steps."""

    def test_has_16_steps(self):
        """Must have exactly 16 steps."""
        assert len(SEQUENCER_16_STEPS) == WORDS

    def test_step_positions(self):
        """Steps must have positions 1-16."""
        positions = [s.position for s in SEQUENCER_16_STEPS]
        assert positions == list(range(1, WORDS + 1))

    def test_step_quarters(self):
        """Steps must have correct quarter assignments."""
        for i, step in enumerate(SEQUENCER_16_STEPS):
            expected_quarter = (i // 4) + 1
            assert step.quarter == expected_quarter

    def test_step_operations_match_names(self):
        """Operations must match the name at each position."""
        for step in SEQUENCER_16_STEPS:
            if step.name == HolyName.HARE:
                assert step.operation == StepOperation.MULTIPLY_SEVEN
            elif step.name == HolyName.KRISHNA:
                assert step.operation == StepOperation.ADD_TEN
            else:
                assert step.operation == StepOperation.SQUARE


class TestObserver7Beats:
    """Test the 7 observer beats."""

    def test_has_7_beats(self):
        """Must have exactly 7 beats."""
        assert len(OBSERVER_7_BEATS) == SEVEN

    def test_beat_numbers(self):
        """Beats must be numbered 1-7."""
        beat_numbers = [b.beat_number for b in OBSERVER_7_BEATS]
        assert beat_numbers == list(range(1, SEVEN + 1))

    def test_all_steps_observed(self):
        """All 16 steps must be observed by some beat."""
        all_observed = set()
        for beat in OBSERVER_7_BEATS:
            all_observed.update(beat.step_positions)
        assert all_observed == set(range(1, WORDS + 1))

    def test_no_overlapping_observations(self):
        """No step should be observed by multiple beats."""
        seen = set()
        for beat in OBSERVER_7_BEATS:
            for pos in beat.step_positions:
                assert pos not in seen, f"Step {pos} observed by multiple beats"
                seen.add(pos)

    def test_names_observed_match_pattern(self):
        """Names observed must match the Mahamantra pattern."""
        for beat in OBSERVER_7_BEATS:
            for i, pos in enumerate(beat.step_positions):
                expected_name = MAHAMANTRA_NAMES[pos - 1]
                assert beat.names_observed[i] == expected_name


class TestMaha16StepSequencer:
    """Test the main sequencer class."""

    def test_create_sequencer(self):
        """Sequencer should be creatable."""
        seq = Maha16StepSequencer()
        assert seq.mod_space == MAHA_QUANTUM
        assert seq.STEPS == WORDS
        assert seq.BEATS == SEVEN

    def test_execute_cycle_produces_result(self):
        """execute_cycle must produce a CycleResult."""
        seq = Maha16StepSequencer()
        result = seq.execute_cycle(seed=PARAMPARA)

        assert isinstance(result, CycleResult)
        assert result.seed == PARAMPARA
        assert 0 <= result.final_value < MAHA_QUANTUM

    def test_cycle_has_16_steps(self):
        """Cycle must contain exactly 16 step results."""
        seq = Maha16StepSequencer()
        result = seq.execute_cycle(seed=PARAMPARA)

        assert len(result.steps) == WORDS

    def test_step_chain_is_correct(self):
        """Output of each step must be input of next."""
        seq = Maha16StepSequencer()
        result = seq.execute_cycle(seed=PARAMPARA)

        # First step input is seed
        assert result.steps[0].input_value == PARAMPARA % MAHA_QUANTUM

        # Each subsequent step takes previous output
        for i in range(1, len(result.steps)):
            assert result.steps[i].input_value == result.steps[i - 1].output_value

        # Final value matches last step output
        assert result.final_value == result.steps[-1].output_value

    def test_operations_are_correct(self):
        """Operations must match position sums."""
        seq = Maha16StepSequencer(mod_space=MAHA_QUANTUM)

        # Test HARE operation: value × 7
        value = 10
        step = get_step_at_position(1)  # First step is HARE
        result = seq.execute_step(value, step)
        assert result.output_value == (value * SEVEN) % MAHA_QUANTUM

        # Test KRISHNA operation: value + 10
        step = get_step_at_position(2)  # Second step is KRISHNA
        result = seq.execute_step(value, step)
        assert result.output_value == (value + TEN) % MAHA_QUANTUM

        # Test RAMA operation: value²
        step = get_step_at_position(10)  # Position 10 is RAMA
        result = seq.execute_step(value, step)
        assert result.output_value == (value * value) % MAHA_QUANTUM

    def test_deterministic(self):
        """Same seed must produce same result."""
        seq1 = Maha16StepSequencer()
        seq2 = Maha16StepSequencer()

        result1 = seq1.execute_cycle(seed=PARAMPARA)
        result2 = seq2.execute_cycle(seed=PARAMPARA)

        assert result1.final_value == result2.final_value


class TestPolyrhythm:
    """Test the 16:7 polyrhythm alignment."""

    def test_full_polyrhythm_has_7_cycles(self):
        """Full polyrhythm must execute 7 cycles (112 steps)."""
        seq = Maha16StepSequencer()
        results = seq.execute_full_polyrhythm(seed=PARAMPARA)

        assert len(results) == FULL_CYCLE // WORDS  # 7 cycles

    def test_full_polyrhythm_step_count(self):
        """Full polyrhythm must traverse 112 steps."""
        seq = Maha16StepSequencer()
        seq.execute_full_polyrhythm(seed=PARAMPARA)

        assert seq._total_steps == FULL_CYCLE

    def test_observer_beat_coverage(self):
        """Each cycle must traverse all 7 beats."""
        seq = Maha16StepSequencer()
        result = seq.execute_cycle(seed=PARAMPARA, track_observer=True)

        assert result.beats_traversed == SEVEN


class TestGADCompliance:
    """Test GAD protocol compliance."""

    def test_discover(self):
        """discover() must return valid info."""
        seq = Maha16StepSequencer()
        info = seq.discover()

        assert info["name"] == "Maha16StepSequencer"
        assert info["architecture"]["field_steps"] == WORDS
        assert info["architecture"]["observer_beats"] == SEVEN
        assert info["architecture"]["full_cycle"] == FULL_CYCLE

    def test_get_state(self):
        """get_state() must return observable state."""
        seq = Maha16StepSequencer()
        seq.execute_cycle(seed=PARAMPARA)

        state = seq.get_state()

        assert state["total_steps"] == WORDS
        assert state["total_cycles"] == 1
        assert state["mod_space"] == MAHA_QUANTUM

    def test_reset(self):
        """reset() must clear state."""
        seq = Maha16StepSequencer()
        seq.execute_cycle(seed=PARAMPARA)
        seq.reset()

        state = seq.get_state()
        assert state["total_steps"] == 0
        assert state["total_cycles"] == 0


class TestHelperFunctions:
    """Test convenience functions."""

    def test_get_step_at_position(self):
        """get_step_at_position must return correct step."""
        step = get_step_at_position(1)
        assert step.position == 1
        assert step.name == HolyName.HARE

        step = get_step_at_position(16)
        assert step.position == 16

    def test_get_step_at_position_bounds(self):
        """get_step_at_position must reject invalid positions."""
        with pytest.raises(ValueError):
            get_step_at_position(0)
        with pytest.raises(ValueError):
            get_step_at_position(17)

    def test_get_beat_at_number(self):
        """get_beat_at_number must return correct beat."""
        beat = get_beat_at_number(1)
        assert beat.beat_number == 1

        beat = get_beat_at_number(7)
        assert beat.beat_number == 7

    def test_get_beat_at_number_bounds(self):
        """get_beat_at_number must reject invalid numbers."""
        with pytest.raises(ValueError):
            get_beat_at_number(0)
        with pytest.raises(ValueError):
            get_beat_at_number(8)

    def test_analyze_step_beat_mapping(self):
        """analyze_step_beat_mapping must return complete mapping."""
        mapping = analyze_step_beat_mapping()

        assert len(mapping) == SEVEN

        # All 16 steps must be covered
        all_steps = []
        for steps in mapping.values():
            all_steps.extend(steps)
        assert set(all_steps) == set(range(1, WORDS + 1))
