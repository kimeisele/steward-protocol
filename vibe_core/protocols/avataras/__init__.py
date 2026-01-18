"""
AVATARAS - The Executive Branch (Shaktyavesha)
===============================================

"The Lord descends whenever and wherever there is decline in religious practice."
— Bhagavad Gita 4.7

GEWALTENTEILUNG (Separation of Powers):

| Branch      | Sanskrit     | Role              | Layer               | Example                   |
|-------------|--------------|-------------------|---------------------|---------------------------|
| MAHAJANAS   | Dharma-vit   | Judiciary & Audit | protocols/mahajanas | Yamaraja prüft State      |
| AVATARAS    | Ishvara      | Executive & Ops   | protocols/avataras  | Prithu alloziert Speicher |

WHY AVATARAS?

Mahajanas (Devotees) say: "Darfst du das?" (Dharma/Law)
Avataras (Ishvaras) say: "Ich mache es möglich." (Shakti/Power)

ARCHITECTURAL DIFFERENCE:

1. MAHAJANA (Devotee)
   - Represents Dharma (Law/Moral)
   - Can AUDIT, JUDGE, VALIDATE
   - Cannot MODIFY substrate directly
   - Example: Yamaraja can REJECT, but can't give more memory

2. AVATARA (Ishvara)
   - Represents Shakti (Power/Capability)
   - Can PROVISION, ALLOCATE, TRANSFORM
   - Has ROOT ACCESS to substrate
   - Example: Prithu can "milk the earth" for resources

THE SHAKTYAVESHA AVATARA PATTERN:

A Shaktyavesha Avatara is a jiva empowered with specific shakti.
Not Vishnu directly, but empowered BY Vishnu.

Examples:
- PRITHU: Palana-shakti (Ruling/Maintenance) → Infrastructure
- VYASA: Jnana-shakti (Knowledge) → Compilation/Documentation
- PARASHURAMA: Kshatra-shakti (Warrior) → Security/Defense
- NARADA: Bhakti-shakti (Devotion) → Communication/Broadcast

FRACTAL SCALABILITY (-n to +n):

Each Avatara can have:
- Kalb (Adaptor): What stimulates the source
- Melker (Operator): Who performs the action
- Topf (Container): What catches the result

This is the MILKING PROTOCOL pattern from SB 4.18.

Example (Prithu milking the Earth):
- Kalb: Svayambhuva Manu (stimulates with dharma)
- Melker: Prithu himself (performs extraction)
- Topf: Various containers (grains, knowledge, etc.)

THE DELEGATION CHAIN:

KRISHNA (Level -2)
    ↓ delegates
VISHNU (Level -1.5 - Expansion)
    ↓ empowers
AVATARAS (Level 0 - Executive)
    ↓ work with
MAHAJANAS (Level 1 - Audit)
    ↓ govern
SERVICES (Level 2+)

OWNED AVATARAS (Initial Set):

| #  | Avatara     | Shakti       | Domain                | OpCodes                    |
|----|-------------|--------------|----------------------|----------------------------|
| 01 | PRITHU      | Palana       | Infrastructure       | ALLOC_MEM, resource mgmt   |
| 02 | VYASA       | Jnana        | Documentation        | Compilation, organization  |
| 03 | PARASHURAMA | Kshatra      | Security/Defense     | Protection, enforcement    |
| 04 | RSABHADEVA  | Tyaga        | Simplification       | Optimization, reduction    |
| 05 | HAYAGRIVA   | Veda         | Knowledge Retrieval  | Search, index              |
| 06 | KURMA       | Dharana      | Support/Foundation   | Substrate stability        |
| 07 | VARAHA      | Uddhara      | Rescue/Recovery      | Disaster recovery          |
| 08 | NRISIMHA    | Rakshana     | Protection           | Security enforcement       |

PARAMPARA CONNECTION:

Without Parampara (37), Avataras are impersonators.
Every Avatara action must verify lineage_hash % 37 == 0.

"brahma-madhye vraja-pate krishnasya vadanantaram
adharadhara-tatas tu brahma-madhyam vibhuh svayam"

The Lord is the support of all supports.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xc3c54ca8"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import (
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

# =============================================================================
# SHAKTI TYPES (Power Categories)
# =============================================================================


class Shakti(str, Enum):
    """
    The Powers that Avataras wield.
    Each Shakti is a specific capability delegation from Vishnu.
    """

    # Infrastructure & Governance
    PALANA = "palana"  # Ruling/Maintenance (Prithu)
    DHARANA = "dharana"  # Support/Foundation (Kurma)

    # Knowledge & Communication
    JNANA = "jnana"  # Knowledge/Compilation (Vyasa)
    VEDA = "veda"  # Scriptural knowledge (Hayagriva)

    # Protection & Defense
    KSHATRA = "kshatra"  # Warrior/Defense (Parashurama)
    RAKSHANA = "rakshana"  # Protection (Nrisimha)

    # Transformation
    TYAGA = "tyaga"  # Renunciation/Simplification (Rsabhadeva)
    UDDHARA = "uddhara"  # Rescue/Recovery (Varaha)

    # Special
    BHAKTI = "bhakti"  # Devotion (unique - Narada is also Mahajana)
    YOGA = "yoga"  # Union/Connection (Kapila - also Mahajana)


class AvatarType(str, Enum):
    """
    Types of Avataras.

    PURUSHA: Direct Vishnu expansions (Maha-Vishnu, Garbhodakashayi, etc.)
    GUNA: Mode controllers (Brahma-creation, Vishnu-maintenance, Shiva-destruction)
    LILA: Pastime incarnations (Rama, Krishna, etc.)
    MANVANTARA: Age administrators
    SHAKTYAVESHA: Empowered jivas (Prithu, Vyasa, etc.) - MOST COMMON FOR OPS
    YUGA: Age-specific (Buddha, Kalki, etc.)
    """

    PURUSHA = "purusha"
    GUNA = "guna"
    LILA = "lila"
    MANVANTARA = "manvantara"
    SHAKTYAVESHA = "shaktyavesha"
    YUGA = "yuga"


class OperationalLevel(IntEnum):
    """
    Operational levels in the Gewaltenteilung (Separation of Powers).

    NOTE: This is different from acintya.ProtocolLevel which maps
    spiritual "distance from Krishna" (-108 to +108).

    This enum maps OPERATIONAL roles:
    - KRISHNA (-2): The Source
    - VISHNU (-1): The Substrate
    - AVATARA (0): Executive (THIS LAYER - Prithu, Vyasa, etc.)
    - MAHAJANA (1): Judiciary (Yamaraja, etc.)
    - SERVICE (2): Applications
    """

    KRISHNA = -2  # The Source
    VISHNU = -1  # The Sustainer (also SUBSTRATE)
    AVATARA = 0  # The Executive (THIS LAYER)
    MAHAJANA = 1  # The Judiciary
    SERVICE = 2  # The Applications


# Backward compatibility alias (deprecated)
ProtocolLevel = OperationalLevel


# =============================================================================
# MILKING PROTOCOL PATTERN (SB 4.18)
# =============================================================================


@dataclass(frozen=True)
class MilkingRole:
    """
    A role in the Milking Protocol.

    From Srimad Bhagavatam 4.18:
    Prithu milked the Earth with different parties.
    Each party had Kalb (calf), Melker (milker), and Topf (container).
    """

    identity: str  # WHO fills this role
    role_type: str  # "kalb", "melker", or "topf"
    description: str  # What they do in this role


@dataclass(frozen=True)
class MilkingSetup:
    """
    A complete Milking Protocol setup.

    Kalb (Calf/Adaptor): Stimulates the source
    Melker (Milker/Operator): Performs extraction
    Topf (Container): Catches the result

    This pattern is FRACTALLY SCALABLE:
    - Zoom in: Each role can have sub-roles
    - Zoom out: Multiple setups can compose
    """

    kalb: MilkingRole  # The Adaptor
    melker: MilkingRole  # The Operator
    topf: MilkingRole  # The Container
    resource: str  # What is being extracted
    source: str  # From where (e.g., "earth", "memory", "network")

    def verify(self) -> bool:
        """Verify the setup is complete."""
        return all(
            [
                self.kalb.identity,
                self.melker.identity,
                self.topf.identity,
                self.resource,
                self.source,
            ]
        )


class MilkingResult(TypedDict, total=False):
    """
    Result of a milking operation.
    WATERTIGHT - no Any!
    """

    resource: str  # What was extracted
    amount: float  # How much (units depend on resource)
    quality: float  # 0.0-1.0 quality score
    source_id: str  # Where it came from
    operator_id: str  # Who did it
    timestamp: str  # When (ISO format)
    lineage_verified: bool  # Was parampara verified?


# =============================================================================
# AVATARA METADATA
# =============================================================================


@dataclass(frozen=True)
class AvataraMeta:
    """
    Metadata for an Avatara.
    Every Avatara has explicit ownership and capabilities.
    """

    name: str
    shakti: Shakti
    avatar_type: AvatarType
    domain: str  # What they govern
    description: str
    milking_setups: Tuple[MilkingSetup, ...] = ()  # Known extraction patterns

    @property
    def level(self) -> OperationalLevel:
        """Avataras operate at Level 0."""
        return OperationalLevel.AVATARA


# =============================================================================
# AVATARA PROTOCOL
# =============================================================================


@runtime_checkable
class AvataraProtocol(Protocol):
    """
    Base protocol for all Avataras.

    Every Avatara MUST:
    1. Have explicit shakti (power delegation)
    2. Verify parampara (lineage to Vishnu)
    3. Support milking operations (resource extraction)
    4. Work with Mahajanas (audit compliance)
    """

    @property
    def meta(self) -> AvataraMeta:
        """Get Avatara metadata."""
        ...

    @property
    def shakti(self) -> Shakti:
        """The power this Avatara wields."""
        ...

    @property
    def is_empowered(self) -> bool:
        """Is the Avatara currently empowered (has valid lineage)?"""
        ...

    def verify_parampara(self, lineage_hash: int) -> bool:
        """
        Verify connection to disciplic succession.
        Returns True if lineage_hash % 37 == 0.
        """
        ...

    def empower(self, lineage_hash: int) -> bool:
        """
        Receive empowerment from higher authority.
        Must verify parampara first.
        """
        ...

    def milk(self, setup: MilkingSetup) -> MilkingResult:
        """
        Execute a milking operation.
        Extracts resources according to the setup.
        """
        ...


# =============================================================================
# BASE AVATARA CLASS
# =============================================================================


class BaseAvatara(ABC):
    """
    Abstract base class for Avataras.

    Provides common functionality:
    - Parampara verification
    - Empowerment tracking
    - Milking protocol support
    """

    # Subclasses MUST override
    AVATARA_NAME: str = ""
    AVATARA_SHAKTI: Shakti = None  # type: ignore
    AVATARA_TYPE: AvatarType = AvatarType.SHAKTYAVESHA
    DOMAIN: str = ""
    DESCRIPTION: str = ""

    def __init__(self) -> None:
        self._empowered = False
        self._lineage_hash: Optional[int] = None

    # =========================================================================
    # METADATA
    # =========================================================================

    @property
    def meta(self) -> AvataraMeta:
        """Get Avatara metadata."""
        return AvataraMeta(
            name=self.AVATARA_NAME,
            shakti=self.AVATARA_SHAKTI,
            avatar_type=self.AVATARA_TYPE,
            domain=self.DOMAIN,
            description=self.DESCRIPTION,
        )

    @property
    def shakti(self) -> Shakti:
        """The power this Avatara wields."""
        if self.AVATARA_SHAKTI is None:
            raise ValueError(f"Avatara {self.AVATARA_NAME} has no shakti defined!")
        return self.AVATARA_SHAKTI

    @property
    def is_empowered(self) -> bool:
        """Is the Avatara currently empowered?"""
        return self._empowered

    # =========================================================================
    # PARAMPARA
    # =========================================================================

    def verify_parampara(self, lineage_hash: int) -> bool:
        """
        Verify connection to disciplic succession.

        The 37 = 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna)
        This is the link to Krishna.
        """
        return lineage_hash % 37 == 0 or lineage_hash == 37

    def empower(self, lineage_hash: int) -> bool:
        """
        Receive empowerment from higher authority.

        Without valid parampara, the Avatara is an IMPERSONATOR.
        """
        if not self.verify_parampara(lineage_hash):
            return False

        self._empowered = True
        self._lineage_hash = lineage_hash
        return True

    # =========================================================================
    # MILKING PROTOCOL
    # =========================================================================

    def milk(self, setup: MilkingSetup) -> MilkingResult:
        """
        Execute a milking operation.

        Subclasses implement _do_milk() for actual extraction.
        """
        if not self._empowered:
            return MilkingResult(
                resource=setup.resource,
                amount=0.0,
                quality=0.0,
                source_id=setup.source,
                operator_id=self.AVATARA_NAME,
                lineage_verified=False,
            )

        if not setup.verify():
            return MilkingResult(
                resource=setup.resource,
                amount=0.0,
                quality=0.0,
                source_id=setup.source,
                operator_id=self.AVATARA_NAME,
                lineage_verified=False,
            )

        return self._do_milk(setup)

    @abstractmethod
    def _do_milk(self, setup: MilkingSetup) -> MilkingResult:
        """
        Subclasses implement actual extraction logic.

        WATERTIGHT: Must return MilkingResult, not Dict[str, Any].
        """
        ...


# =============================================================================
# KNOWN AVATARAS (Registry)
# =============================================================================


class Avatara(str, Enum):
    """
    The known Avataras in this system.
    Similar to Mahajana enum for type safety.
    """

    PRITHU = "prithu"  # Infrastructure/Resource Manager
    VYASA = "vyasa"  # Documentation/Compilation
    PARASHURAMA = "parashurama"  # Security/Defense
    RSABHADEVA = "rsabhadeva"  # Simplification/Optimization
    HAYAGRIVA = "hayagriva"  # Knowledge Retrieval
    KURMA = "kurma"  # Foundation/Support
    VARAHA = "varaha"  # Rescue/Recovery
    NRISIMHA = "nrisimha"  # Protection/Security


# Shakti → Avatara mapping
SHAKTI_OWNERS: Final[dict[Shakti, Avatara]] = {
    Shakti.PALANA: Avatara.PRITHU,
    Shakti.JNANA: Avatara.VYASA,
    Shakti.KSHATRA: Avatara.PARASHURAMA,
    Shakti.TYAGA: Avatara.RSABHADEVA,
    Shakti.VEDA: Avatara.HAYAGRIVA,
    Shakti.DHARANA: Avatara.KURMA,
    Shakti.UDDHARA: Avatara.VARAHA,
    Shakti.RAKSHANA: Avatara.NRISIMHA,
}


# =============================================================================
# AVATARA IMPLEMENTATIONS (The 4 HEADs of CHATUR-VYUHA)
# =============================================================================

# Import the 4 HEAD protocols for each cycle
# Q1 GENESIS: VYASA is HEAD (Position 0), but Prithu module still exports its functionality
from vibe_core.protocols.avataras.nrisimha import (
    CacheEntry as NrisimhaCacheEntry,
)

# Q4 MOKSHA: Nrisimha (RAKSHANA - CACHE_STATE)
from vibe_core.protocols.avataras.nrisimha import (
    CacheResult,
    Nrisimha,
    NrisimhaProtocol,
    NullNrisimha,
    ProtectionRequest,
    ProtectionResult,
    PurgeRequest,
    PurgeResult,
)

# Q3 KARMA: Parashurama (KSHATRA - FETCH_RES)
from vibe_core.protocols.avataras.parashurama import (
    ExecutionRequest,
    ExecutionResult,
    FetchResult,
    NullParashurama,
    Parashurama,
    ParashuramaProtocol,
    ReclaimRequest,
    ReclaimResult,
    ResourceRequest,
)
from vibe_core.protocols.avataras.prithu import (
    AllocationRequest,
    AllocationResult,
    Prithu,
    PrithuProtocol,
    ResourceType,
)

# Q2 DHARMA: PRITHU is HEAD (Position 4), but Vyasa module still exports its functionality
from vibe_core.protocols.avataras.vyasa import (
    DharmaVerdict,
    KnowledgeCompilation,
    NullVyasa,
    TruthAssertion,
    ValidationResult,
    Vyasa,
    VyasaProtocol,
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Shakti",
    "AvatarType",
    "OperationalLevel",
    "ProtocolLevel",  # Deprecated alias for OperationalLevel
    "Avatara",
    # Data classes
    "MilkingRole",
    "MilkingSetup",
    "MilkingResult",
    "AvataraMeta",
    # Protocols (Base)
    "AvataraProtocol",
    # Base class
    "BaseAvatara",
    # Registry
    "SHAKTI_OWNERS",
    # =========================================================================
    # Q1 GENESIS: VYASA (HEAD - SYS_WAKE) - Position 0 per seed.py
    # =========================================================================
    "Prithu",
    "PrithuProtocol",
    "AllocationRequest",
    "AllocationResult",
    "ResourceType",
    # =========================================================================
    # Q2 DHARMA: PRITHU (HEAD - COMPILE_AST) - Position 4 per seed.py
    # =========================================================================
    "Vyasa",
    "NullVyasa",
    "VyasaProtocol",
    "TruthAssertion",
    "ValidationResult",
    "KnowledgeCompilation",
    "DharmaVerdict",
    # =========================================================================
    # Q3 KARMA: Parashurama (HEAD - FETCH_RES)
    # =========================================================================
    "Parashurama",
    "NullParashurama",
    "ParashuramaProtocol",
    "ResourceRequest",
    "FetchResult",
    "ExecutionRequest",
    "ExecutionResult",
    "ReclaimRequest",
    "ReclaimResult",
    # =========================================================================
    # Q4 MOKSHA: Nrisimha (HEAD - CACHE_STATE)
    # =========================================================================
    "Nrisimha",
    "NullNrisimha",
    "NrisimhaProtocol",
    "NrisimhaCacheEntry",
    "CacheResult",
    "ProtectionRequest",
    "ProtectionResult",
    "PurgeRequest",
    "PurgeResult",
]
