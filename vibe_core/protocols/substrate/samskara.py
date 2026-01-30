"""
SAMSKARA PROTOCOL - The 4-Phase Pipeline (Legacy Proxy)
=======================================================

DEPRECATED: Use vibe_core.mahamantra.substrate.samskara

This file is a PROXY to the SSOT in `vibe_core/mahamantra/substrate/samskara.py`.
"""

from vibe_core.mahamantra.substrate.samskara import (
    PARAMPARA,
    PHASES,
    POSITIONS_PER_PHASE,
    Phase,
    PhaseResult,
    PhaseStatus,
    PipelineContext,
    PipelineExecutor,
    SamskaraProtocol,
    NullSamskara,
)

__all__ = [
    "PARAMPARA",
    "PHASES",
    "POSITIONS_PER_PHASE",
    "Phase",
    "PhaseResult",
    "PhaseStatus",
    "PipelineContext",
    "SamskaraProtocol",
    "PipelineExecutor",
    "NullSamskara",
]
