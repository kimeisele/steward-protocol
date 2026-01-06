"""
PRAHLAD - Resilience & Hardening Agent.

Modular split for maintainability:
- service.py: Main PrahladService class
- types.py: TypedDicts, Protocols, dataclasses
- chaos.py: ChaosProbingMixin
- coverage.py: CoverageIntelligenceMixin
- hiranyakashipu.py: HiranyakashipuMixin

Backward Compatibility:
    from vibe_core.naga.services.prahlad import PrahladService
"""

from vibe_core.naga.services.prahlad.service import PrahladService
from vibe_core.naga.services.prahlad.types import (
    ChaosProbeResult,
    ChaosScenario,
    ChaosTarget,
    CoverageIntelligence,
    DharmaScore,
    ErrorContextData,
    ErrorEvent,
    KernelLike,
    LedgerLike,
    NagaCoverageData,
    PhoenixResult,
    PhoenixStateData,
    ProbeFailure,
    ProbeResult,
    RegistryLike,
    ReproductionContextData,
    ShuddhiHealResult,
    TestCase,
)

__all__ = [
    # Main service
    "PrahladService",
    # Types
    "ChaosProbeResult",
    "ChaosScenario",
    "ChaosTarget",
    "CoverageIntelligence",
    "DharmaScore",
    "ErrorContextData",
    "ErrorEvent",
    "KernelLike",
    "LedgerLike",
    "NagaCoverageData",
    "PhoenixResult",
    "PhoenixStateData",
    "ProbeFailure",
    "ProbeResult",
    "RegistryLike",
    "ReproductionContextData",
    "ShuddhiHealResult",
    "TestCase",
]
