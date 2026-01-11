"""
COGNITIVE PROTOCOL - USE MAHAMANTRA
===================================

DEPRECATED: This file is MAYA (illusion).

ONE IMPORT, KRISHNA ROUTES:
    from vibe_core.mahamantra import mahamantra

    # Position 6 = KAPILA (Garbage Collect)
    mahamantra[6]                    # -> MantraPosition
    mahamantra.protocols.kapila      # -> KapilaProtocolBase

The canonical source is: vibe_core.protocols.mahajanas.kapila
This file is a bridge for backward compatibility only.
"""

# Re-export from canonical Mahajana location
from vibe_core.protocols.mahajanas.kapila import (
    # Protocol Base - THE ONLY SOURCE
    KapilaProtocolBase,
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

__all__ = [
    # Protocol Base
    "KapilaProtocolBase",
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
