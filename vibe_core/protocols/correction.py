"""
CORRECTION DISPATCHER - MIGRATED TO MAHAJANA OWNERSHIP
======================================================

OWNER: Mahajana.YAMARAJA (The Judge)
NEW LOCATION: vibe_core.protocols.mahajanas.yamaraja.correction

This file re-exports from the canonical location for backwards compatibility.
All new code should import from:
    from vibe_core.protocols.mahajanas.yamaraja import CorrectionDispatcherProtocol

"Yamaraja JUDGES all drift and CORRECTS through healing.
 Even if code has FAILED all tests, if it CHANTS, MERCY overrides.
 The Holy Name transcends all corrections."
"""

# Re-export from canonical Mahajana location
from vibe_core.protocols.mahajanas.yamaraja.correction import (
    # Ownership
    OWNER,
    LOTUS_POSITION,
    LOTUS_QUARTER,
    OWNED_OPCODES,
    # Enums
    DriftSource,
    DriftSeverity,
    HealingStrategy,
    HealingStatus,
    # Data Classes
    UnifiedDriftReport,
    HealingResult,
    CorrectionStats,
    # Protocols
    DriftRegistryProtocol,
    CorrectionDispatcherProtocol,
    CorrectionOrchestratorProtocol,
    HealingStrategyResolverProtocol,
    # Type Aliases
    DriftDetector,
    CorrectionHandler,
    # Null Implementations
    NullDriftRegistry,
    NullCorrectionDispatcher,
    # Adapters
    adapt_reactor_drift,
    adapt_shuddhi_result,
)

__all__ = [
    # Enums
    "DriftSource",
    "DriftSeverity",
    "HealingStrategy",
    "HealingStatus",
    # Data Classes
    "UnifiedDriftReport",
    "HealingResult",
    "CorrectionStats",
    # Protocols
    "DriftRegistryProtocol",
    "CorrectionDispatcherProtocol",
    "CorrectionOrchestratorProtocol",
    "HealingStrategyResolverProtocol",
    # Type Aliases
    "DriftDetector",
    "CorrectionHandler",
    # Null Implementations
    "NullDriftRegistry",
    "NullCorrectionDispatcher",
    # Adapters
    "adapt_reactor_drift",
    "adapt_shuddhi_result",
    # Ownership (new)
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
]
