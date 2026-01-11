"""
THE 12 MAHAJANAS - Protocol Owners
==================================

"svayambhur naradah sambhuh kumarah kapilo manuh
prahlado janako bhismo balir vaiyasakir vayam"
- Srimad Bhagavatam 6.3.20

These are the 12 authorities on dharma. They OWN the protocols.
Other protocols INHERIT from or are GUARDED BY a Mahajana.

Architecture:
    protocols/mahajanas/ (Purusha - Spirit)
    +
    tests/mahajanas/ (Prakriti - Matter)
    =
    Living Code / Agent

The Mahajanas are the LINK between Vishnu (Kernel) and Jiva (Implementation).
They GRANT capabilities. We are their heirs.

Hash: 0x25 (37) = 24 Ksetra + 12 Ksetrapala + 1 Ksetrajna
"""

from typing import TYPE_CHECKING

# Lazy imports to avoid circular dependencies
if TYPE_CHECKING:
    from .brahma import BrahmaProtocol
    from .narada import NaradaProtocol
    from .shambhu import ShambhuProtocol
    from .kumaras import KumarasProtocol
    from .kapila import KapilaProtocol
    from .manu import ManuProtocol
    from .prahlada import PrahladaProtocol
    from .janaka import JanakaProtocol
    from .bhishma import BhishmaProtocol
    from .bali import BaliProtocol
    from .shuka import ShukaProtocol
    from .yamaraja import YamarajaProtocol


# The 12 Mahajanas in order (SB 6.3.20)
MAHAJANA_ORDER = [
    "brahma",      # 01 - Creation
    "narada",      # 02 - Devotion
    "shambhu",     # 03 - Destruction
    "kumaras",     # 04 - Purity
    "kapila",      # 05 - Analysis
    "manu",        # 06 - Law
    "prahlada",    # 07 - Resilience
    "janaka",      # 08 - Duty
    "bhishma",     # 09 - Vow
    "bali",        # 10 - Surrender
    "shuka",       # 11 - Vision
    "yamaraja",    # 12 - Judgment
]

# Router exports
from .router import (
    Mahajana,
    MahajanaRoute,
    MahajanaRouter,
    get_router,
    route,
    get_opcodes,
    verify_router,
)

# Protocol exports (Discovered Interface)
from .protocol import (
    MahajanaVerdict,
    MahajanaResult,
    MahajanaProtocol,
    BaseMahajana,
    NullMahajana,
)

# Sabha exports (The Council)
from .sabha import (
    MahajanaStatus,
    SabhaState,
    SabhaProtocol,
    MahajanaSabha,
    get_sabha,
)

# Adoption Pipeline (Mahamantra IS the Filter)
from .adoption import (
    AdoptionStatus,
    AdoptionDecision,
    ProtocolAnalysis,
    AdoptionResult,
    ShudhiReport,
    run_shudhi,
    detect_opcodes_from_source,
    detect_primary_opcode,
    AdoptionPipeline,
    get_pipeline,
    adopt,
    analyze,
)

# OwnedProtocol (Lotus + Vedic Graph Integration)
from .owned_protocol import (
    ProtocolState,
    OwnershipStatus,
    ProtocolMeta,
    OwnedProtocol,
    get_mahajana_position,
    get_mahajana_lineage,
    register_protocol,
    get_protocol,
    get_protocols_by_owner,
    list_orphan_protocols,
    VEDIC_GRAPH,
)

__all__ = [
    "MAHAJANA_ORDER",
    # Router
    "Mahajana",
    "MahajanaRoute",
    "MahajanaRouter",
    "get_router",
    "route",
    "get_opcodes",
    "verify_router",
    # Protocol
    "MahajanaVerdict",
    "MahajanaResult",
    "MahajanaProtocol",
    "BaseMahajana",
    "NullMahajana",
    # Sabha
    "MahajanaStatus",
    "SabhaState",
    "SabhaProtocol",
    "MahajanaSabha",
    "get_sabha",
    # Adoption Pipeline (Mahamantra IS the Filter)
    "AdoptionStatus",
    "AdoptionDecision",
    "ProtocolAnalysis",
    "AdoptionResult",
    "ShudhiReport",
    "run_shudhi",
    "detect_opcodes_from_source",
    "detect_primary_opcode",
    "AdoptionPipeline",
    "get_pipeline",
    "adopt",
    "analyze",
    # OwnedProtocol (Lotus Integration)
    "ProtocolState",
    "OwnershipStatus",
    "ProtocolMeta",
    "OwnedProtocol",
    "get_mahajana_position",
    "get_mahajana_lineage",
    "register_protocol",
    "get_protocol",
    "get_protocols_by_owner",
    "list_orphan_protocols",
    "VEDIC_GRAPH",
]
