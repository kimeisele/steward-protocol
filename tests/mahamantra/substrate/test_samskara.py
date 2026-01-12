"""
Tests for SamskaraProtocol - The 4-Phase Pipeline Protocol.

Tests verify:
1. Phase enum and constants
2. PhaseResult and PipelineContext
3. NullSamskara implementation
4. PipelineExecutor functionality
5. Protocol compliance
"""

import pytest
from pathlib import Path
from typing import Optional

from vibe_core.protocols.substrate.samskara import (
    PARAMPARA,
    PHASES,
    POSITIONS_PER_PHASE,
    Phase,
    PhaseStatus,
    PhaseResult,
    PipelineContext,
    SamskaraProtocol,
    PipelineExecutor,
    NullSamskara,
)


class TestPhaseEnum:
    """Test Phase enum."""

    def test_phase_count(self):
        """Should have exactly 4 phases."""
        assert len(Phase) == 4

    def test_phase_values(self):
        """Should have correct phase names."""
        assert Phase.GENESIS.value == "genesis"
        assert Phase.DHARMA.value == "dharma"
        assert Phase.KARMA.value == "karma"
        assert Phase.MOKSHA.value == "moksha"

    def test_quarter_index(self):
        """Should return correct quarter indices."""
        assert Phase.GENESIS.quarter_index == 0
        assert Phase.DHARMA.quarter_index == 1
        assert Phase.KARMA.quarter_index == 2
        assert Phase.MOKSHA.quarter_index == 3

    def test_position_range(self):
        """Should return correct position ranges."""
        assert Phase.GENESIS.position_range == (0, 4)
        assert Phase.DHARMA.position_range == (4, 8)
        assert Phase.KARMA.position_range == (8, 12)
        assert Phase.MOKSHA.position_range == (12, 16)

    def test_parampara_vector(self):
        """Should return parampara vectors divisible by 37."""
        for phase in Phase:
            vector = phase.parampara_vector
            assert vector % PARAMPARA == 0, f"{phase.value} vector {vector} not divisible by 37"


class TestConstants:
    """Test module constants."""

    def test_parampara(self):
        """PARAMPARA should be 37."""
        assert PARAMPARA == 37

    def test_phases(self):
        """PHASES should be 4."""
        assert PHASES == 4

    def test_positions_per_phase(self):
        """POSITIONS_PER_PHASE should be 4."""
        assert POSITIONS_PER_PHASE == 4


class TestPhaseStatus:
    """Test PhaseStatus enum."""

    def test_all_statuses_exist(self):
        """Should have all expected statuses."""
        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.RUNNING.value == "running"
        assert PhaseStatus.SUCCESS.value == "success"
        assert PhaseStatus.SKIPPED.value == "skipped"
        assert PhaseStatus.FAILED.value == "failed"
        assert PhaseStatus.GRACEFUL.value == "graceful"


class TestPhaseResult:
    """Test PhaseResult dataclass."""

    def test_create_phase_result(self):
        """Should create a PhaseResult."""
        result = PhaseResult(
            phase=Phase.GENESIS,
            status=PhaseStatus.SUCCESS,
            message="Initialized",
        )
        assert result.phase == Phase.GENESIS
        assert result.status == PhaseStatus.SUCCESS
        assert result.message == "Initialized"
        assert result.success is True
        assert result.failed is False

    def test_success_property(self):
        """Success should be True for SUCCESS, SKIPPED, GRACEFUL."""
        assert PhaseResult(Phase.GENESIS, PhaseStatus.SUCCESS, "ok").success is True
        assert PhaseResult(Phase.GENESIS, PhaseStatus.SKIPPED, "ok").success is True
        assert PhaseResult(Phase.GENESIS, PhaseStatus.GRACEFUL, "ok").success is True
        assert PhaseResult(Phase.GENESIS, PhaseStatus.FAILED, "fail").success is False
        assert PhaseResult(Phase.GENESIS, PhaseStatus.PENDING, "wait").success is False

    def test_failed_property(self):
        """Failed should be True only for FAILED status."""
        assert PhaseResult(Phase.GENESIS, PhaseStatus.FAILED, "fail").failed is True
        assert PhaseResult(Phase.GENESIS, PhaseStatus.SUCCESS, "ok").failed is False
        assert PhaseResult(Phase.GENESIS, PhaseStatus.GRACEFUL, "ok").failed is False


class TestPipelineContext:
    """Test PipelineContext dataclass."""

    def test_create_context(self):
        """Should create a context with payload."""
        ctx = PipelineContext(payload="test_data")
        assert ctx.payload == "test_data"
        assert ctx.is_valid is True
        assert ctx.error is None
        assert len(ctx.phases) == 0

    def test_log_phase(self):
        """Should log phase results."""
        ctx = PipelineContext(payload="data")
        ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "Initialized", 10.5)

        assert len(ctx.phases) == 1
        assert ctx.phases[0].phase == Phase.GENESIS
        assert ctx.phases[0].status == PhaseStatus.SUCCESS
        assert ctx.phases[0].message == "Initialized"
        assert ctx.phases[0].duration_ms == 10.5

    def test_current_phase(self):
        """Should return last executed phase."""
        ctx = PipelineContext(payload="data")
        assert ctx.current_phase is None

        ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "ok")
        assert ctx.current_phase == Phase.GENESIS

        ctx.log_phase(Phase.DHARMA, PhaseStatus.SUCCESS, "ok")
        assert ctx.current_phase == Phase.DHARMA

    def test_all_phases_ok(self):
        """Should return True if all phases succeeded."""
        ctx = PipelineContext(payload="data")
        ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "ok")
        ctx.log_phase(Phase.DHARMA, PhaseStatus.SUCCESS, "ok")
        assert ctx.all_phases_ok is True

        ctx.log_phase(Phase.KARMA, PhaseStatus.FAILED, "fail")
        assert ctx.all_phases_ok is False

    def test_phase_summary(self):
        """Should return readable phase summary."""
        ctx = PipelineContext(payload="data")
        ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "ok")
        ctx.log_phase(Phase.DHARMA, PhaseStatus.GRACEFUL, "skip")

        summary = ctx.phase_summary
        assert "GENESIS" in summary
        assert "DHARMA" in summary


class TestNullSamskara:
    """Test NullSamskara implementation."""

    def test_implements_protocol(self):
        """Should implement SamskaraProtocol."""
        samskara = NullSamskara()
        assert isinstance(samskara, SamskaraProtocol)

    def test_genesis(self):
        """Genesis should create context with string payload."""
        samskara = NullSamskara()
        ctx = samskara.genesis("test_input")
        assert ctx.payload == "test_input"
        assert ctx.is_valid is True

    def test_dharma(self):
        """Dharma should always return True."""
        samskara = NullSamskara()
        ctx = PipelineContext(payload="data")
        assert samskara.dharma(ctx) is True

    def test_karma(self):
        """Karma should return payload unchanged."""
        samskara = NullSamskara()
        ctx = PipelineContext(payload="original_data")
        result = samskara.karma(ctx)
        assert result == "original_data"

    def test_moksha(self):
        """Moksha should not raise."""
        samskara = NullSamskara()
        ctx = PipelineContext(payload="data")
        samskara.moksha(ctx, "result")  # Should not raise


class TestPipelineExecutor:
    """Test PipelineExecutor."""

    def test_create_executor(self):
        """Should create executor with samskara."""
        samskara = NullSamskara()
        executor = PipelineExecutor(samskara)
        assert executor._samskara is samskara

    def test_run_complete_pipeline(self):
        """Should run all 4 phases."""
        samskara = NullSamskara()
        executor = PipelineExecutor(samskara)

        ctx, result = executor.run("input_data")

        assert result == "input_data"
        assert len(ctx.phases) == 4
        assert ctx.phases[0].phase == Phase.GENESIS
        assert ctx.phases[1].phase == Phase.DHARMA
        assert ctx.phases[2].phase == Phase.KARMA
        assert ctx.phases[3].phase == Phase.MOKSHA
        assert ctx.all_phases_ok is True

    def test_iterate_yields_all_phases(self):
        """Should yield each phase during execution."""
        samskara = NullSamskara()
        executor = PipelineExecutor(samskara)

        phases_seen = []
        for phase, ctx in executor.iterate("data"):
            phases_seen.append(phase)

        assert phases_seen == [Phase.GENESIS, Phase.DHARMA, Phase.KARMA, Phase.MOKSHA]


class TestCustomSamskara:
    """Test custom SamskaraProtocol implementation."""

    def test_custom_implementation(self):
        """Should be able to create custom samskara."""

        class DoublingSamskara:
            """Doubles the input number."""

            def genesis(self, input_data: object) -> PipelineContext[int]:
                return PipelineContext(payload=int(input_data))

            def dharma(self, ctx: PipelineContext[int]) -> bool:
                return ctx.payload >= 0  # Only positive numbers

            def karma(self, ctx: PipelineContext[int]) -> int:
                return ctx.payload * 2

            def moksha(self, ctx: PipelineContext[int], result: Optional[int]) -> None:
                pass

        samskara = DoublingSamskara()
        executor = PipelineExecutor(samskara)

        ctx, result = executor.run(5)
        assert result == 10

    def test_dharma_skip_skips_karma(self):
        """When dharma returns False, karma should be skipped."""

        class RejectingSamskara:
            """Always rejects in dharma."""

            def genesis(self, input_data: object) -> PipelineContext[str]:
                return PipelineContext(payload=str(input_data))

            def dharma(self, ctx: PipelineContext[str]) -> bool:
                return False  # Always reject

            def karma(self, ctx: PipelineContext[str]) -> str:
                return "SHOULD_NOT_SEE_THIS"

            def moksha(self, ctx: PipelineContext[str], result: Optional[str]) -> None:
                pass

        samskara = RejectingSamskara()
        executor = PipelineExecutor(samskara)

        ctx, result = executor.run("input")

        # Result should be None since karma was skipped
        assert result is None
        # KARMA phase should be SKIPPED
        karma_phase = [p for p in ctx.phases if p.phase == Phase.KARMA][0]
        assert karma_phase.status == PhaseStatus.SKIPPED


class TestKaliYugaGrace:
    """Test graceful failure handling (Kali Yuga Grace)."""

    def test_dharma_error_is_graceful(self):
        """Errors in dharma should be graceful, not hard failures."""

        class ExplodingDharmaSamskara:
            def genesis(self, input_data: object) -> PipelineContext[str]:
                return PipelineContext(payload=str(input_data))

            def dharma(self, ctx: PipelineContext[str]) -> bool:
                raise ValueError("Dharma explosion!")

            def karma(self, ctx: PipelineContext[str]) -> str:
                return ctx.payload

            def moksha(self, ctx: PipelineContext[str], result: Optional[str]) -> None:
                pass

        samskara = ExplodingDharmaSamskara()
        executor = PipelineExecutor(samskara)

        # Should NOT raise, should handle gracefully
        ctx, result = executor.run("input")

        # Check dharma phase is GRACEFUL (not FAILED)
        dharma_phase = [p for p in ctx.phases if p.phase == Phase.DHARMA][0]
        assert dharma_phase.status == PhaseStatus.GRACEFUL

        # Moksha should still have run
        assert len(ctx.phases) == 4
        assert ctx.phases[-1].phase == Phase.MOKSHA
