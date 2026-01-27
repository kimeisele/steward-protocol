"""
TEST: Mahamantra Pipeline - The 4-Phase Architecture
=====================================================

"catur-vidhā bhajante māṁ janāḥ sukṛtino 'rjuna"
"Four kinds of pious men render devotional service unto Me."
— Bhagavad Gita 7.16

WHAT WE TEST:
1. Phase Structure: 4 phases, correct mappings
2. Genesis Phase: Hash/intent determination works
3. Dharma Phase: Transform/validation works
4. Karma Phase: Routing/action works
5. Moksha Phase: Completion/orchestration works
6. Full Pipeline: End-to-end execution

THE CONTRACT: These tests GUARANTEE the 4-phase architecture works.
"""

import pytest

from vibe_core.mahamantra.adapters.pipeline import (
    MahamantraPipeline,
    PipelineResult,
    GenesisResult,
    DharmaResult,
    KarmaResult,
    MokshaResult,
    PhaseSpec,
    PHASE_SPECS,
    get_pipeline,
)
from vibe_core.mahamantra.substrate.mahajana import Quarter, Sampradaya
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    QUARTERS,
    WORDS,
)


class TestPipelineStructure:
    """Test pipeline structure and metadata."""

    def test_four_phases_exist(self):
        """Pipeline should have exactly 4 phases."""
        assert len(PHASE_SPECS) == QUARTERS
        assert len(PHASE_SPECS) == 4

    def test_phases_are_quarters(self):
        """Each phase should be a Quarter."""
        for quarter in PHASE_SPECS:
            assert isinstance(quarter, Quarter)

    def test_genesis_phase_spec(self):
        """Genesis phase should be correctly specified."""
        spec = PHASE_SPECS[Quarter.GENESIS]
        assert spec.sounds == "Hare Krishna Hare Krishna"
        assert spec.positions == (1, 2, 3, 4)
        assert spec.sampradaya == Sampradaya.BRAHMA
        assert spec.adapter_name == "hash"

    def test_dharma_phase_spec(self):
        """Dharma phase should be correctly specified."""
        spec = PHASE_SPECS[Quarter.DHARMA]
        assert spec.sounds == "Krishna Krishna Hare Hare"
        assert spec.positions == (5, 6, 7, 8)
        assert spec.sampradaya == Sampradaya.KUMARA
        assert spec.adapter_name == "transform"

    def test_karma_phase_spec(self):
        """Karma phase should be correctly specified."""
        spec = PHASE_SPECS[Quarter.KARMA]
        assert spec.sounds == "Hare Rama Hare Rama"
        assert spec.positions == (9, 10, 11, 12)
        assert spec.sampradaya == Sampradaya.SRI
        assert spec.adapter_name == "router"

    def test_moksha_phase_spec(self):
        """Moksha phase should be correctly specified."""
        spec = PHASE_SPECS[Quarter.MOKSHA]
        assert spec.sounds == "Rama Rama Hare Hare"
        assert spec.positions == (13, 14, 15, 16)
        assert spec.sampradaya == Sampradaya.RUDRA
        assert spec.adapter_name == "orchestrator"

    def test_all_positions_covered(self):
        """All 16 positions should be covered by phases."""
        all_positions = []
        for spec in PHASE_SPECS.values():
            all_positions.extend(spec.positions)
        assert sorted(all_positions) == list(range(1, WORDS + 1))


class TestGenesisPhase:
    """Test Genesis phase (hash/intent)."""

    def test_genesis_returns_result(self):
        """Genesis phase should return GenesisResult."""
        pipeline = MahamantraPipeline()
        result = pipeline.genesis("test")
        assert isinstance(result, GenesisResult)

    def test_genesis_hash_in_quantum_space(self):
        """Genesis hash should be in [0, MAHA_QUANTUM)."""
        pipeline = MahamantraPipeline()
        result = pipeline.genesis("test")
        assert 0 <= result.hash_value < MAHA_QUANTUM

    def test_genesis_preserves_input(self):
        """Genesis should preserve input value."""
        pipeline = MahamantraPipeline()
        result = pipeline.genesis("my_input")
        assert result.input_value == "my_input"

    def test_genesis_quarter_is_genesis(self):
        """Genesis result should have GENESIS quarter."""
        pipeline = MahamantraPipeline()
        result = pipeline.genesis("test")
        assert result.quarter == Quarter.GENESIS

    def test_genesis_deterministic(self):
        """Same input should give same hash."""
        pipeline = MahamantraPipeline()
        r1 = pipeline.genesis("consistent")
        r2 = pipeline.genesis("consistent")
        assert r1.hash_value == r2.hash_value


class TestDharmaPhase:
    """Test Dharma phase (transform)."""

    def test_dharma_returns_result(self):
        """Dharma phase should return DharmaResult."""
        pipeline = MahamantraPipeline()
        result = pipeline.dharma(42)
        assert isinstance(result, DharmaResult)

    def test_dharma_output_in_quantum_space(self):
        """Dharma output should be in [0, MAHA_QUANTUM)."""
        pipeline = MahamantraPipeline()
        result = pipeline.dharma(42)
        assert 0 <= result.output_value < MAHA_QUANTUM

    def test_dharma_finds_attractor(self):
        """Dharma should find an attractor."""
        pipeline = MahamantraPipeline()
        result = pipeline.dharma(42)
        assert result.attractor >= 0
        assert result.steps >= 0

    def test_dharma_quarter_is_dharma(self):
        """Dharma result should have DHARMA quarter."""
        pipeline = MahamantraPipeline()
        result = pipeline.dharma(42)
        assert result.quarter == Quarter.DHARMA


class TestKarmaPhase:
    """Test Karma phase (routing)."""

    def test_karma_returns_result(self):
        """Karma phase should return KarmaResult."""
        pipeline = MahamantraPipeline()
        result = pipeline.karma(42)
        assert isinstance(result, KarmaResult)

    def test_karma_with_payload(self):
        """Karma should store payload."""
        pipeline = MahamantraPipeline()
        result = pipeline.karma(42, payload="my_data")
        assert result.routed == True
        assert result.value == "my_data"

    def test_karma_quarter_is_karma(self):
        """Karma result should have KARMA quarter."""
        pipeline = MahamantraPipeline()
        result = pipeline.karma(42)
        assert result.quarter == Quarter.KARMA


class TestMokshaPhase:
    """Test Moksha phase (orchestration)."""

    def test_moksha_returns_result(self):
        """Moksha phase should return MokshaResult."""
        pipeline = MahamantraPipeline()
        pipeline.reset()  # Clean state
        result = pipeline.moksha(42)
        assert isinstance(result, MokshaResult)

    def test_moksha_has_beat(self):
        """Moksha should report beat."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.moksha(42)
        assert 1 <= result.beat <= 7

    def test_moksha_has_resonance(self):
        """Moksha should report resonance."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.moksha(42)
        assert 0 <= result.resonance <= 1

    def test_moksha_quarter_is_moksha(self):
        """Moksha result should have MOKSHA quarter."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.moksha(42)
        assert result.quarter == Quarter.MOKSHA


class TestFullPipeline:
    """Test complete pipeline execution."""

    def test_execute_returns_result(self):
        """Execute should return PipelineResult."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.execute("test input")
        assert isinstance(result, PipelineResult)

    def test_execute_has_all_phases(self):
        """Execute result should have all phase results."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.execute("test")
        assert isinstance(result.genesis, GenesisResult)
        assert isinstance(result.dharma, DharmaResult)
        assert isinstance(result.karma, KarmaResult)
        assert isinstance(result.moksha, MokshaResult)

    def test_execute_phases_chain(self):
        """Phases should chain correctly."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.execute("chain test")

        # Genesis hash feeds Dharma
        assert result.dharma.input_value == result.genesis.hash_value

        # Dharma attractor feeds Karma
        assert result.karma.key == result.dharma.attractor % 65536  # 16-bit key space

    def test_execute_final_value_is_attractor(self):
        """Final value should be the attractor."""
        pipeline = MahamantraPipeline()
        pipeline.reset()
        result = pipeline.execute("attractor test")
        assert result.final_value == result.dharma.attractor

    def test_execute_different_inputs_different_results(self):
        """Different inputs should give different results."""
        pipeline = MahamantraPipeline()
        r1 = pipeline.execute("input_one")
        r2 = pipeline.execute("input_two")
        assert r1.genesis.hash_value != r2.genesis.hash_value


class TestPipelineReset:
    """Test pipeline reset functionality."""

    def test_reset_clears_orchestrator(self):
        """Reset should clear orchestrator state."""
        pipeline = MahamantraPipeline()
        pipeline.moksha(42)  # Advance state
        pipeline.reset()
        result = pipeline.moksha(42)
        assert result.beat == 1  # Back to start


class TestPipelineSingleton:
    """Test pipeline singleton access."""

    def test_get_pipeline_returns_instance(self):
        """get_pipeline should return a MahamantraPipeline."""
        pipeline = get_pipeline()
        assert isinstance(pipeline, MahamantraPipeline)

    def test_get_pipeline_is_singleton(self):
        """get_pipeline should return same instance."""
        p1 = get_pipeline()
        p2 = get_pipeline()
        assert p1 is p2


class TestPipelineDescribe:
    """Test pipeline description."""

    def test_describe_returns_dict(self):
        """describe() should return dict."""
        pipeline = MahamantraPipeline()
        desc = pipeline.describe()
        assert isinstance(desc, dict)

    def test_describe_has_phases(self):
        """describe() should include phase count."""
        pipeline = MahamantraPipeline()
        desc = pipeline.describe()
        assert desc["phases"] == QUARTERS

    def test_describe_has_phase_details(self):
        """describe() should include phase details."""
        pipeline = MahamantraPipeline()
        desc = pipeline.describe()
        assert "genesis" in desc["phase_details"]
        assert "dharma" in desc["phase_details"]
        assert "karma" in desc["phase_details"]
        assert "moksha" in desc["phase_details"]


class TestMahamantraSingletonPipeline:
    """Test pipeline access through mahamantra singleton."""

    def test_pipeline_accessible(self):
        """mahamantra.pipeline should be accessible."""
        from vibe_core.mahamantra import mahamantra
        assert hasattr(mahamantra, 'pipeline')
        assert mahamantra.pipeline is not None

    def test_pipeline_execute_works(self):
        """mahamantra.pipeline.execute() should work."""
        from vibe_core.mahamantra import mahamantra
        mahamantra.pipeline.reset()
        result = mahamantra.pipeline.execute("singleton test")
        assert isinstance(result, PipelineResult)

    def test_pipeline_phases_work(self):
        """Individual phases should work through singleton."""
        from vibe_core.mahamantra import mahamantra

        genesis = mahamantra.pipeline.genesis("test")
        assert isinstance(genesis, GenesisResult)

        dharma = mahamantra.pipeline.dharma(genesis.hash_value)
        assert isinstance(dharma, DharmaResult)
