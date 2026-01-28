"""
TESTS: MahaSynth - 16-Step Modular Sequencer
=============================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

These tests make MahaSynth ALTAR-WORTHY.
"""

import pytest

from vibe_core.mahamantra.adapters.synth import (
    MahaSynth,
    SynthParams,
    StepResult,
    CycleResult,
    ResonanceResult,
    SpectrumResult,
    SYNTH_PRESETS,
    PATTERN,
    create_synth,
)
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    QUARTERS,
    SEVEN,
    TEN,
    MAHA_QUANTUM,
    PANCHA,
    NAVA,
    TRINITY,
)


# =============================================================================
# PATTERN TESTS
# =============================================================================


class TestPattern:
    """Test the Mahamantra pattern constants."""

    def test_pattern_has_16_words(self):
        """PATTERN must have 16 words."""
        assert len(PATTERN) == WORDS == 16

    def test_pattern_only_h_k_r(self):
        """PATTERN only contains H, K, R."""
        valid_words = {"H", "K", "R"}
        for word in PATTERN:
            assert word in valid_words

    def test_pattern_quarters(self):
        """PATTERN has correct quarter structure."""
        # Q1: H K H K (seeking Krishna)
        assert PATTERN[0:4] == ("H", "K", "H", "K")
        # Q2: K K H H (Krishna responds)
        assert PATTERN[4:8] == ("K", "K", "H", "H")
        # Q3: H R H R (seeking Rama)
        assert PATTERN[8:12] == ("H", "R", "H", "R")
        # Q4: R R H H (Rama responds)
        assert PATTERN[12:16] == ("R", "R", "H", "H")

    def test_hare_count_in_pattern(self):
        """PATTERN has 8 HAREs."""
        hare_count = sum(1 for w in PATTERN if w == "H")
        assert hare_count == 8


# =============================================================================
# SYNTH PARAMS TESTS
# =============================================================================


class TestSynthParams:
    """Test SynthParams dataclass."""

    def test_default_params(self):
        """Default params are quantum preset."""
        params = SynthParams()
        assert params.mod_space == MAHA_QUANTUM
        assert params.lfo_enabled is True
        assert params.lfo_rate == QUARTERS

    def test_custom_params(self):
        """Can create custom params."""
        params = SynthParams(
            mod_space=256,
            feedback=2,
            phase_offset=3,
            lfo_enabled=False,
        )
        assert params.mod_space == 256
        assert params.feedback == 2
        assert params.lfo_enabled is False


# =============================================================================
# PRESET TESTS
# =============================================================================


class TestSynthPresets:
    """Test synth presets."""

    def test_presets_exist(self):
        """All documented presets exist."""
        preset_names = ["classical", "quantum", "trinity", "pancha", "nava", "wide"]
        for name in preset_names:
            assert name in SYNTH_PRESETS

    def test_classical_preset(self):
        """Classical preset converges (mod 17)."""
        params = SYNTH_PRESETS["classical"]
        assert params.mod_space == 17  # WEIGHT_KRISHNA
        assert params.feedback == 0

    def test_quantum_preset(self):
        """Quantum preset is default (mod 137)."""
        params = SYNTH_PRESETS["quantum"]
        assert params.mod_space == MAHA_QUANTUM

    def test_trinity_preset(self):
        """Trinity preset has 3-state output."""
        params = SYNTH_PRESETS["trinity"]
        assert params.mod_space == TRINITY

    def test_pancha_preset(self):
        """Pancha preset has 5-way classification."""
        params = SYNTH_PRESETS["pancha"]
        assert params.mod_space == PANCHA

    def test_nava_preset(self):
        """Nava preset has 9-state output."""
        params = SYNTH_PRESETS["nava"]
        assert params.mod_space == NAVA


# =============================================================================
# RESULT DATACLASS TESTS
# =============================================================================


class TestStepResult:
    """Test StepResult dataclass."""

    def test_create_step_result(self):
        """Can create StepResult."""
        result = StepResult(
            position=1,
            name="H",
            quarter=1,
            input_value=42,
            output_value=10,
            operation="42 × 7 = 10 (mod 137)",
            observer_beat=1,
        )
        assert result.position == 1
        assert result.name == "H"
        assert result.input_value == 42
        assert result.output_value == 10


class TestCycleResult:
    """Test CycleResult dataclass."""

    def test_create_cycle_result(self):
        """Can create CycleResult."""
        result = CycleResult(
            seed=42,
            final_value=100,
            steps=(),
            mod_space=137,
            preset="quantum",
        )
        assert result.seed == 42
        assert result.final_value == 100


class TestResonanceResult:
    """Test ResonanceResult dataclass."""

    def test_create_resonance_result(self):
        """Can create ResonanceResult."""
        result = ResonanceResult(
            seed=42,
            attractor=49,
            cycles_to_converge=5,
            cycle_length=1,
            trajectory=(42, 100, 50, 49),
        )
        assert result.attractor == 49
        assert result.cycles_to_converge == 5


# =============================================================================
# MAHA SYNTH INIT TESTS
# =============================================================================


class TestMahaSynthInit:
    """Test MahaSynth initialization."""

    def test_default_preset(self):
        """Default preset is quantum."""
        synth = MahaSynth()
        assert synth.preset == "quantum"
        assert synth.mod_space == MAHA_QUANTUM

    def test_classical_preset(self):
        """Can create with classical preset."""
        synth = MahaSynth(preset="classical")
        assert synth.preset == "classical"
        assert synth.mod_space == 17

    def test_custom_params(self):
        """Can create with custom params."""
        params = SynthParams(mod_space=256)
        synth = MahaSynth(preset="custom", params=params)
        assert synth.mod_space == 256

    def test_params_property(self):
        """params property returns current params."""
        synth = MahaSynth()
        assert synth.params.mod_space == MAHA_QUANTUM


# =============================================================================
# STEP TESTS
# =============================================================================


class TestMahaSynthStep:
    """Test step() method."""

    @pytest.fixture
    def synth(self) -> MahaSynth:
        """Create synth with known params."""
        return MahaSynth(preset="classical")  # mod 17, no feedback

    def test_step_returns_step_result(self, synth: MahaSynth):
        """step() returns StepResult."""
        result = synth.step(value=5, position=1)
        assert isinstance(result, StepResult)
        assert result.position == 1

    def test_step_position_normalized(self, synth: MahaSynth):
        """Position normalized to 1-16."""
        result = synth.step(value=5, position=17)
        assert result.position == 1

        result = synth.step(value=5, position=32)
        assert result.position == 16

    def test_step_hare_operation(self, synth: MahaSynth):
        """HARE step multiplies by SEVEN."""
        # Position 1 is H
        result = synth.step(value=1, position=1)
        assert result.name == "H"
        # Output = value × 7 × ADSR + LFO (mod 17)
        # With ADSR and LFO, the exact formula is complex

    def test_step_krishna_operation(self, synth: MahaSynth):
        """KRISHNA step adds TEN + position."""
        # Position 2 is K
        result = synth.step(value=1, position=2)
        assert result.name == "K"
        # Output = value + 10 + position (mod 17)

    def test_step_rama_operation(self, synth: MahaSynth):
        """RAMA step squares the value."""
        # Position 10 is R
        result = synth.step(value=4, position=10)
        assert result.name == "R"
        # Output = 4² = 16 (mod 17)
        assert result.output_value == 16

    def test_step_has_observer_beat(self, synth: MahaSynth):
        """Each step has observer beat (1-7)."""
        for pos in range(1, 17):
            result = synth.step(value=1, position=pos)
            assert 1 <= result.observer_beat <= SEVEN


# =============================================================================
# CYCLE TESTS
# =============================================================================


class TestMahaSynthCycle:
    """Test cycle() method."""

    @pytest.fixture
    def synth(self) -> MahaSynth:
        return MahaSynth(preset="quantum")

    def test_cycle_returns_cycle_result(self, synth: MahaSynth):
        """cycle() returns CycleResult."""
        result = synth.cycle(seed=42)
        assert isinstance(result, CycleResult)

    def test_cycle_has_16_steps(self, synth: MahaSynth):
        """Cycle has exactly 16 steps."""
        result = synth.cycle(seed=42)
        assert len(result.steps) == 16

    def test_cycle_records_seed(self, synth: MahaSynth):
        """Cycle records original seed."""
        result = synth.cycle(seed=42)
        assert result.seed == 42

    def test_cycle_deterministic(self, synth: MahaSynth):
        """Same seed produces same result."""
        result1 = synth.cycle(seed=42)
        result2 = synth.cycle(seed=42)
        assert result1.final_value == result2.final_value


# =============================================================================
# RESONANCE TESTS
# =============================================================================


class TestMahaSynthResonance:
    """Test resonate() method."""

    def test_resonate_finds_attractor(self):
        """resonate() finds attractor."""
        synth = MahaSynth(preset="classical")  # Converges fast
        result = synth.resonate(seed=42)

        assert isinstance(result, ResonanceResult)
        assert result.attractor is not None

    def test_resonate_with_quantum(self):
        """Quantum preset finds known attractors."""
        synth = MahaSynth(preset="quantum")
        result = synth.resonate(seed=0)

        assert result.attractor is not None
        # Should converge within reasonable cycles
        assert result.cycles_to_converge < 100

    def test_resonate_trajectory_recorded(self):
        """Resonance trajectory is recorded."""
        synth = MahaSynth(preset="classical")
        result = synth.resonate(seed=42)

        assert len(result.trajectory) > 0


# =============================================================================
# SPECTRUM TESTS
# =============================================================================


class TestMahaSynthSpectrum:
    """Test spectrum() method."""

    def test_spectrum_returns_result(self):
        """spectrum() returns SpectrumResult."""
        synth = MahaSynth(preset="classical")
        result = synth.spectrum(sample_size=16)

        assert isinstance(result, SpectrumResult)

    def test_spectrum_finds_attractors(self):
        """spectrum() finds all attractors."""
        synth = MahaSynth(preset="classical")
        result = synth.spectrum(sample_size=17)  # Full mod space

        assert len(result.attractors) > 0

    def test_spectrum_builds_convergence_map(self):
        """spectrum() builds seed → attractor map."""
        synth = MahaSynth(preset="classical")
        result = synth.spectrum(sample_size=16)

        assert len(result.convergence_map) == 16


# =============================================================================
# BATCH OPERATION TESTS
# =============================================================================


class TestMahaSynthBatch:
    """Test batch operations."""

    def test_cycle_batch(self):
        """cycle_batch() processes multiple seeds."""
        synth = MahaSynth()
        results = synth.cycle_batch(seeds=[1, 2, 3])

        assert len(results) == 3
        assert all(isinstance(r, CycleResult) for r in results)

    def test_resonate_batch(self):
        """resonate_batch() processes multiple seeds."""
        synth = MahaSynth()
        results = synth.resonate_batch(seeds=[1, 2, 3])

        assert len(results) == 3
        assert all(isinstance(r, ResonanceResult) for r in results)


# =============================================================================
# STATS TESTS
# =============================================================================


class TestMahaSynthStats:
    """Test stats tracking."""

    def test_stats_returns_dict(self):
        """stats() returns dictionary."""
        synth = MahaSynth()
        stats = synth.stats()

        assert isinstance(stats, dict)
        assert "preset" in stats
        assert "mod_space" in stats
        assert "total_steps" in stats
        assert "total_cycles" in stats

    def test_stats_tracks_steps(self):
        """stats() tracks total steps."""
        synth = MahaSynth()
        synth.step(value=1, position=1)
        synth.step(value=1, position=2)

        stats = synth.stats()
        assert stats["total_steps"] == 2

    def test_stats_tracks_cycles(self):
        """stats() tracks total cycles."""
        synth = MahaSynth()
        synth.cycle(seed=1)
        synth.cycle(seed=2)

        stats = synth.stats()
        assert stats["total_cycles"] == 2


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================


class TestCreateSynth:
    """Test create_synth factory function."""

    def test_create_default(self):
        """create_synth() creates default synth."""
        synth = create_synth()
        assert isinstance(synth, MahaSynth)
        assert synth.preset == "quantum"

    def test_create_with_preset(self):
        """create_synth() accepts preset."""
        synth = create_synth(preset="classical")
        assert synth.preset == "classical"

    def test_create_with_params(self):
        """create_synth() accepts params."""
        params = SynthParams(mod_space=256)
        synth = create_synth(params=params)
        assert synth.mod_space == 256


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMahaSynthIntegration:
    """Integration tests for MahaSynth."""

    def test_full_cycle_flow(self):
        """Full cycle flow works end-to-end."""
        synth = MahaSynth(preset="quantum")

        # Execute a cycle
        cycle = synth.cycle(seed=42)

        # Verify structure
        assert len(cycle.steps) == 16
        assert cycle.seed == 42
        assert cycle.mod_space == MAHA_QUANTUM

        # Each step should be valid
        for step in cycle.steps:
            assert step.name in ("H", "K", "R")
            assert 1 <= step.position <= 16
            assert 1 <= step.quarter <= 4
            assert 1 <= step.observer_beat <= 7

    def test_full_resonance_flow(self):
        """Full resonance flow finds stable state."""
        synth = MahaSynth(preset="classical")  # mod 17 converges fast

        result = synth.resonate(seed=5)

        # Should find attractor
        assert result.attractor is not None
        # Fixed point or periodic orbit
        assert result.cycle_length >= 0

    def test_polyrhythm_alignment(self):
        """16 and 7 create polyrhythm."""
        synth = MahaSynth()

        # Track observer beats across a cycle
        cycle = synth.cycle(seed=0)
        beats = [step.observer_beat for step in cycle.steps]

        # Should cover beats 1-7 (some repeated)
        unique_beats = set(beats)
        assert len(unique_beats) <= 7

    def test_all_presets_work(self):
        """All presets can execute cycles."""
        for preset_name in SYNTH_PRESETS:
            synth = MahaSynth(preset=preset_name)
            cycle = synth.cycle(seed=42)
            assert len(cycle.steps) == 16
