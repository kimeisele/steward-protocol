"""
SAMSKARA — 4-Phase Pipeline Tests
===================================

Tests the universal 4-phase pipeline:
GENESIS → DHARMA → KARMA → MOKSHA

Tests Phase enum, PhaseResult, PipelineContext,
PipelineExecutor, and NullSamskara.
"""

import pytest

from vibe_core.mahamantra.substrate.state.samskara import (
    NullSamskara,
    Phase,
    PhaseResult,
    PhaseStatus,
    PipelineContext,
    PipelineExecutor,
)


# ============================================================================
# Phase Enum
# ============================================================================


class TestPhase:
    """4 phases map to 4 quarters."""

    def test_phase_values(self):
        assert Phase.GENESIS.value == "genesis"
        assert Phase.DHARMA.value == "dharma"
        assert Phase.KARMA.value == "karma"
        assert Phase.MOKSHA.value == "moksha"

    def test_phase_count(self):
        assert len(Phase) == 4

    def test_quarter_index(self):
        assert Phase.GENESIS.quarter_index == 0
        assert Phase.DHARMA.quarter_index == 1
        assert Phase.KARMA.quarter_index == 2
        assert Phase.MOKSHA.quarter_index == 3


# ============================================================================
# PhaseStatus
# ============================================================================


class TestPhaseStatus:
    """6 statuses including Kali Yuga Grace."""

    def test_status_values(self):
        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.RUNNING.value == "running"
        assert PhaseStatus.SUCCESS.value == "success"
        assert PhaseStatus.SKIPPED.value == "skipped"
        assert PhaseStatus.FAILED.value == "failed"
        assert PhaseStatus.GRACEFUL.value == "graceful"

    def test_status_count(self):
        assert len(PhaseStatus) == 6


# ============================================================================
# PhaseResult
# ============================================================================


class TestPhaseResult:
    """PhaseResult tracks outcome of a single phase."""

    def test_success_result(self):
        r = PhaseResult(phase=Phase.GENESIS, status=PhaseStatus.SUCCESS, message="ok")
        assert r.success is True
        assert r.failed is False

    def test_failed_result(self):
        r = PhaseResult(phase=Phase.DHARMA, status=PhaseStatus.FAILED, message="bad")
        assert r.success is False
        assert r.failed is True

    def test_graceful_result(self):
        """Graceful = failed but continued (Kali Yuga Grace)."""
        r = PhaseResult(phase=Phase.KARMA, status=PhaseStatus.GRACEFUL, message="grace")
        assert r.success is True  # graceful counts as success
        assert r.failed is False


# ============================================================================
# PipelineContext
# ============================================================================


class TestPipelineContext:
    """PipelineContext carries payload through all phases."""

    def test_create(self):
        ctx = PipelineContext(payload="test")
        assert ctx.payload == "test"
        assert ctx.is_valid is True
        assert ctx.error is None
        assert len(ctx.phases) == 0

    def test_log_phase(self):
        ctx = PipelineContext(payload="data")
        ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "init ok", 10.5)
        assert len(ctx.phases) == 1
        assert ctx.phases[0].phase == Phase.GENESIS
        assert ctx.phases[0].duration_ms == 10.5

    def test_all_phases_ok(self):
        ctx = PipelineContext(payload="x")
        ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "ok", 0)
        ctx.log_phase(Phase.DHARMA, PhaseStatus.SUCCESS, "ok", 0)
        assert ctx.all_phases_ok is True

        ctx.log_phase(Phase.KARMA, PhaseStatus.FAILED, "bad", 0)
        assert ctx.all_phases_ok is False


# ============================================================================
# NullSamskara + PipelineExecutor
# ============================================================================


class TestNullSamskara:
    """NullSamskara passes everything through unchanged."""

    def test_null_pipeline(self):
        ns = NullSamskara()
        executor = PipelineExecutor(ns)
        ctx, result = executor.run("hello")
        assert result is not None
        assert ctx.is_valid is True

    def test_iterate(self):
        ns = NullSamskara()
        executor = PipelineExecutor(ns)
        phases_seen = []
        for phase, ctx in executor.iterate("data"):
            phases_seen.append(phase)
        # Should see all 4 phases
        assert Phase.GENESIS in phases_seen
        assert Phase.DHARMA in phases_seen
        assert Phase.KARMA in phases_seen
        assert Phase.MOKSHA in phases_seen
