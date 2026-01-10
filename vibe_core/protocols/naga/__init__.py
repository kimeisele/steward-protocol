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
from vibe_core.protocols.naga.types import (
    EventRecord,
    NagaServiceProtocol,
    NagaStatus,
    NagaType,
    StatusDetails,
)

# Kaliya
from vibe_core.protocols.naga.kaliya import (
    KaliyaProtocol,
    NullKaliya,
    QuarantineStatus,
)

# Narada
from vibe_core.protocols.naga.narada import (
    NaradaProtocol,
    NullNarada,
)

# Prahlad
from vibe_core.protocols.naga.prahlad import (
    PrahladMemory,
    PrahladProtocol,
    NullPrahlad,
)

# Kulika
from vibe_core.protocols.naga.kulika import (
    KulikaProtocol,
    NullKulika,
)

# Padma
from vibe_core.protocols.naga.padma import (
    CacheEntry,
    CacheStats,
    CacheValue,
    NullPadma,
    PadmaProtocol,
)

# Shankha
from vibe_core.protocols.naga.shankha import (
    BroadcastMessage,
    NullShankha,
    ShankhaProtocol,
)

# Karkotaka
from vibe_core.protocols.naga.karkotaka import (
    EncryptedPayload,
    KarkotakaProtocol,
    NullKarkotaka,
    SignedContent,
)

# TÜV
from vibe_core.protocols.naga.tuv import (
    ChurnEntry,
    FindableProtocol,
    FindingRegistry,
    Leak,
    LeakDict,
    LeakPattern,
    LeakSeverity,
    LeakStatus,
    NullTÜV,
    ProtocolAudit,
    ProtocolCoverageReport,
    ProtocolGap,
    ProtocolGapDict,
    ProtocolGapSeverity,
    ProtocolGapStatus,
    TÜVProtocol,
    TÜVRegistry,
    TÜVReport,
)

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

# Flood (NARADA - The Messenger)
from vibe_core.protocols.naga.flood import (
    FloodProtocol,
    FloodConsumerProtocol,
    NullFlood,
    FloodLayer,
    FloodStatus,
    FloodStats,
    FloodConfig,
    FloodSignal,
    FloodObservation,
)

# Intel Bridge (SHUKA - The Visionary)
from vibe_core.protocols.naga.intel_bridge import (
    IntelBridgeProtocol,
    NullIntelBridge,
    IntelCategory,
    IntelPriority,
    IntelItem,
    IntelQuery,
    IntelResponse,
)

# Federation
from vibe_core.protocols.naga.federation import (
    NagaFederationProtocol,
)

# Garuda (The Carrier)
from vibe_core.protocols.naga.garuda import Garuda, GarudaProtocol

# Sesha (The Bed)
from vibe_core.protocols.naga.sesha import (
    ImportResult,
    LedgerBlock,
    NullSesha,
    Sesha,
    SeshaProtocol,
    SyncRequest,
    SyncStatus,
)

# Takshaka (The Architect)
from vibe_core.protocols.naga.takshaka import (
    NullTakshaka,
    Takshaka,
    TakshakaProtocol,
    ToxicityReport,
    VajraViolation,
    VerifyResult,
    VerifyStatus,
    ViolationDetails,
)

# Vasuki (The Rope)
from vibe_core.protocols.naga.vasuki import (
    NodeAddress,
    NullVasuki,
    SendResult,
    SendStatus,
    SignedEnvelope,
    Vasuki,
    VasukiProtocol,
)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Types
    "NagaType",
    "NagaStatus",
    "NagaServiceProtocol",  # Common DNA - discovered from 14+ protocols
    "StatusDetails",
    "EventRecord",  # YAMARAJA: Typed event for Sesha.record_event()
    # Sesha
    "Sesha",
    "SeshaProtocol",
    "SyncStatus",
    "SyncRequest",
    "LedgerBlock",
    "ImportResult",
    "NullSesha",
    # Vasuki
    "Vasuki",
    "SignedEnvelope",
    "SendStatus",
    "SendResult",
    "SendResult",
    "NodeAddress",
    "VasukiProtocol",
    "NullVasuki",
    # Takshaka
    "Takshaka",
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
    "PrahladMemory",
    "PrahladProtocol",
    "NullPrahlad",
    # NOTE: DharmaScore now in vibe_core.naga.services.prahlad.types
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
    # Garuda
    "Garuda",
    "GarudaProtocol",
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
    # TÜV (Type Audit Intelligence)
    "TÜVProtocol",
    "NullTÜV",
    "TÜVReport",
    "ProtocolAudit",
    "ChurnEntry",
    # Findings (Protocol-First - reusable by any auditor)
    "FindableProtocol",
    "FindingRegistry",
    # Leak types
    "Leak",
    "LeakDict",
    "LeakPattern",
    "LeakSeverity",
    "LeakStatus",
    # Protocol Gap types
    "ProtocolGap",
    "ProtocolGapDict",
    "ProtocolGapSeverity",
    "ProtocolGapStatus",
    "ProtocolCoverageReport",
    # Backward compat
    "TÜVRegistry",
    # Flood (NARADA - The Messenger)
    "FloodProtocol",
    "FloodConsumerProtocol",
    "NullFlood",
    "FloodLayer",
    "FloodStatus",
    "FloodStats",
    "FloodConfig",
    "FloodSignal",
    "FloodObservation",
    # Intel Bridge (SHUKA - The Visionary)
    "IntelBridgeProtocol",
    "NullIntelBridge",
    "IntelCategory",
    "IntelPriority",
    "IntelItem",
    "IntelQuery",
    "IntelResponse",
]
