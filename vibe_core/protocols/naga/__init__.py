"""
NAGA Protocols Package - Fractal Architecture (COMPLETE)

This package is the FRACTAL split of the former god file (2862 lines).
Each protocol now lives in its own module for:
- Independent testing
- Isolated imports
- Self-similar scaling

Backward Compatibility:
    All exports are re-exported here.
    Existing imports work unchanged:
        from vibe_core.protocols.naga import SeshaProtocol

New Fractal Imports (Preferred):
    from vibe_core.protocols.naga.sesha import SeshaProtocol
    from vibe_core.protocols.naga.types import NagaType, NagaStatus

Module Structure (15 modules):
    naga/
    ├── __init__.py     # This file (re-exports for compat)
    ├── types.py        # NagaType, NagaStatus, StatusDetails
    ├── sesha.py        # SeshaProtocol, NullSesha
    ├── vasuki.py       # VasukiProtocol, NullVasuki
    ├── takshaka.py     # TakshakaProtocol, NullTakshaka
    ├── kaliya.py       # KaliyaProtocol, NullKaliya
    ├── narada.py       # NaradaProtocol, NullNarada
    ├── chitragupta.py  # ChitraguptaProtocol, NullChitragupta
    ├── prahlad.py      # PrahladProtocol, NullPrahlad
    ├── federation.py   # NagaFederationProtocol
    ├── cortex.py       # NagaCortexProtocol, NullNagaCortex
    ├── padma.py        # PadmaProtocol, NullPadma (Cache)
    ├── shankha.py      # ShankhaProtocol, NullShankha (Broadcast)
    ├── karkotaka.py    # KarkotakaProtocol, NullKarkotaka (Crypto)
    ├── kulika.py       # KulikaProtocol, NullKulika (Schema Registry)
    └── ananta.py       # AnantaProtocol, NullAnanta (Gene Splicer)
"""

# =============================================================================
# FRACTAL IMPORTS (New modules)
# =============================================================================

# Types
# Ananta (Gene Splicer)
from vibe_core.protocols.naga.ananta import (
    AnantaProtocol,
    FloodProposal,
    NullAnanta,
    ServiceClassification,
    VetoDecision,
)

# Chitragupta
from vibe_core.protocols.naga.chitragupta import (
    AnomalyReport,
    ChitraguptaProtocol,
    NullChitragupta,
)

# Cortex
from vibe_core.protocols.naga.cortex import (
    ContextReasonCode,
    DecisionSummary,
    FeedbackOutcome,
    ManasFeedback,
    NagaContext,
    NagaCortexProtocol,
    NullNagaCortex,
    PeerHealthSummary,
    ThreatSummary,
)

# Federation
from vibe_core.protocols.naga.federation import (
    NagaFederationProtocol,
)

# Kaliya
from vibe_core.protocols.naga.kaliya import (
    KaliyaProtocol,
    NullKaliya,
    QuarantineStatus,
)

# Karkotaka (Crypto)
from vibe_core.protocols.naga.karkotaka import (
    EncryptedPayload,
    KarkotakaProtocol,
    NullKarkotaka,
    SignedContent,
)

# Kulika (Schema Registry)
from vibe_core.protocols.naga.kulika import (
    KulikaProtocol,
    NullKulika,
)

# Narada
from vibe_core.protocols.naga.narada import (
    NaradaProtocol,
    NullNarada,
)

# Padma (Cache)
from vibe_core.protocols.naga.padma import (
    CacheEntry,
    CacheStats,
    CacheValue,
    NullPadma,
    PadmaProtocol,
)

# Prahlad
from vibe_core.protocols.naga.prahlad import (
    DharmaScore,
    NullPrahlad,
    PrahladProtocol,
)

# Sesha
from vibe_core.protocols.naga.sesha import (
    ImportResult,
    LedgerBlock,
    NullSesha,
    SeshaProtocol,
    SyncRequest,
    SyncStatus,
)

# Shankha (Broadcast)
from vibe_core.protocols.naga.shankha import (
    BroadcastMessage,
    NullShankha,
    ShankhaProtocol,
)

# Takshaka
from vibe_core.protocols.naga.takshaka import (
    NullTakshaka,
    TakshakaProtocol,
    ToxicityReport,
    VajraViolation,
    VerifyResult,
    VerifyStatus,
    ViolationDetails,
)
from vibe_core.protocols.naga.types import (
    NagaStatus,
    NagaType,
    StatusDetails,
)

# Vasuki
from vibe_core.protocols.naga.vasuki import (
    NodeAddress,
    NullVasuki,
    SendResult,
    SendStatus,
    SignedEnvelope,
    VasukiProtocol,
)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Types
    "NagaType",
    "NagaStatus",
    "StatusDetails",
    # Sesha
    "SeshaProtocol",
    "SyncStatus",
    "SyncRequest",
    "LedgerBlock",
    "ImportResult",
    "NullSesha",
    # Vasuki
    "VasukiProtocol",
    "SignedEnvelope",
    "SendStatus",
    "SendResult",
    "NodeAddress",
    "NullVasuki",
    # Takshaka
    "TakshakaProtocol",
    "VerifyStatus",
    "VerifyResult",
    "ToxicityReport",
    "VajraViolation",
    "ViolationDetails",
    "NullTakshaka",
    # Kaliya
    "KaliyaProtocol",
    "QuarantineStatus",
    "NullKaliya",
    # Narada
    "NaradaProtocol",
    "NullNarada",
    # Chitragupta
    "ChitraguptaProtocol",
    "AnomalyReport",
    "NullChitragupta",
    # Prahlad
    "PrahladProtocol",
    "DharmaScore",
    "NullPrahlad",
    # Kulika
    "KulikaProtocol",
    "NullKulika",
    # Padma
    "PadmaProtocol",
    "CacheEntry",
    "CacheStats",
    "CacheValue",
    "NullPadma",
    # Shankha
    "ShankhaProtocol",
    "BroadcastMessage",
    "NullShankha",
    # Karkotaka
    "KarkotakaProtocol",
    "SignedContent",
    "EncryptedPayload",
    "NullKarkotaka",
    # Ananta (Gene Splicer)
    "AnantaProtocol",
    "FloodProposal",
    "VetoDecision",
    "ServiceClassification",
    "NullAnanta",
    # Federation
    "NagaFederationProtocol",
    # Cortex (MANAS Integration)
    "NagaCortexProtocol",
    "NagaContext",
    "ManasFeedback",
    "NullNagaCortex",
    # Cortex Typed Fields (GAD-000 Parseability)
    "ContextReasonCode",
    "ThreatSummary",
    "DecisionSummary",
    "PeerHealthSummary",
    "FeedbackOutcome",
]
