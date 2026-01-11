"""
COGNITIVE PROTOCOL - MIGRATED TO MAHAJANA OWNERSHIP
====================================================

OWNER: Mahajana.KAPILA (The Analyst - Sankhya Philosophy)
NEW LOCATION: vibe_core.protocols.mahajanas.kapila.cognition

This file re-exports from the canonical location for backwards compatibility.
All new code should import from:
    from vibe_core.protocols.mahajanas.kapila import (
        CognitiveKernelProtocol,
        OperatorCognitiveProtocol,
        CognitiveResult,
        ...
    )

"Lord Kapila - The Founder of Sankhya.
 His analytical philosophy leads to devotion, not dry speculation."
"""

# Re-export from canonical Mahajana location
from vibe_core.protocols.mahajanas.kapila import (
    OWNER,
    LOTUS_POSITION,
    LOTUS_QUARTER,
    # Types (WATERTIGHT)
    IntentType,
    SyscallParams,
    QueryResult,
    MessageRecord,
    TickResult,
    ThoughtResult,
    HeartbeatResult,
    # Dataclasses
    CognitiveResult,
    SignedOperatorInput,
    CognitiveContext,
    # Protocols
    CognitiveKernelProtocol,
    SystemHeartbeatProtocol,
    OperatorCognitiveProtocol,
    # Null implementation
    NullCognitive,
)

# Legacy compatibility: ABC versions redirect to Protocol versions
# The old ABCs are replaced by Protocol (structural subtyping)
# CognitiveKernelProtocol is now a Protocol, not ABC

__all__ = [
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    # Types
    "IntentType",
    "SyscallParams",
    "QueryResult",
    "MessageRecord",
    "TickResult",
    "ThoughtResult",
    "HeartbeatResult",
    # Dataclasses
    "CognitiveResult",
    "SignedOperatorInput",
    "CognitiveContext",
    # Protocols
    "CognitiveKernelProtocol",
    "SystemHeartbeatProtocol",
    "OperatorCognitiveProtocol",
    # Null implementation
    "NullCognitive",
]
