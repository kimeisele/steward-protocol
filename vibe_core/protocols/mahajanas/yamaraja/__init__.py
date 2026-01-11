"""
YAMARAJA - The 12th Mahajana (Judgment/Testing)
===============================================

POSITION: 15 (MOKSHA Quarter, RESET_IP OpCode)

The Lord of Death. The Final Judge.
Every soul must face Yamaraja.

DERIVED FROM MAHAMANTRA:
    Position 15 -> guardian=YAMARAJA, opcode=RESET_IP, quarter=MOKSHA
    All properties derived from truth table. No manual wiring.

THE AJAMIL EXCEPTION (SB 6.1-3):
Even Yamaraja bows to the Holy Name.
The Mahamantra OVERRIDES all judgment.

"harer nama harer nama harer namaiva kevalam
kalau nasty eva nasty eva nasty eva gatir anyatha"
"""

from typing import Protocol, runtime_checkable, List, Union, ClassVar
from dataclasses import dataclass
from enum import Enum

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode


# =============================================================================
# YAMARAJA PROTOCOL BASE - Derives from MantraPosition 15
# =============================================================================

class YamarajaProtocolBase(WorkerProtocol):
    """
    Yamaraja protocol ownership - DERIVED from Mahamantra position 15.

    NO MANUAL WIRING:
        _position_index = 15 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.YAMARAJA
        opcode()    -> MantraOpCode.RESET_IP
        quarter()   -> Quarter.MOKSHA
        is_head()   -> False (Worker position)
        parampara_vector() -> 592 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 15  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[15]


# =============================================================================
# JUDGMENT TYPES
# =============================================================================

class Verdict(str, Enum):
    """The five possible verdicts."""
    ALLOW = "allow"       # Vaikuntha - Passage granted
    DENY = "deny"         # Naraka - Passage denied
    ATONE = "atone"       # Prayascitta - Must purify first
    ELEVATED = "elevated" # Grace - Beyond judgment
    MERCY = "mercy"       # AJAMIL EXCEPTION - Holy Name overrides!


@dataclass(frozen=True)
class Judgeable:
    """
    Anything that can be judged by Yamaraja.
    Replaces 'Any' with explicit judgeable structure.

    Note: Yamaraja CAN judge anything (acintya),
    but we provide structure for type safety.
    """
    subject_type: str  # "code", "action", "entity", "soul"
    subject_id: str
    karma_history: List[str] = None  # type: ignore

    def __post_init__(self) -> None:
        if self.karma_history is None:
            object.__setattr__(self, 'karma_history', [])


@dataclass(frozen=True)
class JudgmentRecord:
    """The record of Yamaraja's judgment."""
    subject: Judgeable
    verdict: Verdict
    reason: str
    karma_delta: float  # Change to karma balance


# =============================================================================
# PROTOCOL DEFINITION
# =============================================================================

@runtime_checkable
class YamarajaProtocol(Protocol):
    """
    The Judgment Protocol.
    Any system that makes final decisions must implement this.

    ANTI-MAYAVAD: This is not abstract "testing".
    YAMARAJA (the Person) judges. He is the Lord of Death.

    THE AJAMIL EXCEPTION:
    Even if subject fails all tests, check_holy_name() can override!
    The Holy Name is supreme - even Yamaraja bows to it.
    """

    def judge(self, subject: Union[Judgeable, object]) -> Verdict:
        """
        Judge a subject.
        Returns the final verdict.

        Note: Accepts 'object' for flexibility, but Judgeable preferred.
        Yamaraja can judge ANYTHING (acintya principle).

        IMPORTANT: Always check check_holy_name() before returning DENY!
        """
        ...

    def check_holy_name(self, subject: Union[Judgeable, object]) -> bool:
        """
        THE AJAMIL EXCEPTION - Check if subject chanted the Holy Name.

        If True: Return Verdict.MERCY (overrides all other judgments)
        If False: Proceed with normal judgment

        Even accidental chanting counts (Ajamil called his son "Narayana").
        In Kali Yuga, this is the ONLY way.
        """
        ...

    def assert_truth(self, condition: bool, reason: str) -> None:
        """
        Assert truth. Raises if false.
        This is the OpCode.
        """
        ...

    def get_karma_balance(self) -> float:
        """
        Get the subject's karma balance.
        Positive = good karma. Negative = bad karma.
        """
        ...


class NullYamaraja(YamarajaProtocolBase):
    """
    The Merciful Judge.
    All pass (for testing without judgment).

    Inherits from YamarajaProtocolBase -> position 15 -> YAMARAJA.
    """

    def judge(self, subject: Union[Judgeable, object]) -> Verdict:
        # Always check Holy Name first (Ajamil exception)
        if self.check_holy_name(subject):
            return Verdict.MERCY
        return Verdict.ALLOW

    def check_holy_name(self, subject: Union[Judgeable, object]) -> bool:
        """NullYamaraja always grants mercy."""
        return True  # Maximum mercy in Kali Yuga

    def assert_truth(self, condition: bool, reason: str) -> None:
        pass  # No assertion

    def get_karma_balance(self) -> float:
        return 0.0  # Neutral


# Import security submodule
from .security import (
    SecurityProtocol,
    NullSecurityProtocol,
    SecurityLevel,
    SecurityCapability,
    SecurityViolation,
    SecurityAuditRecord,
    SecurityStateSnapshot,
    SecuredSubject,
)

# Import samskara submodule (Migration/Transformation)
from .samskara import (
    SamskaraType,
    MigrationStatus,
    WildProtocol,
    MigrationVerdict,
    SamskaraState,
    MigrationManifest,
    SamskaraProtocol,
    SamskaraOwnedProtocol,
    NullSamskara,
)

# Import Correction (Drift Detection & Healing) - Yamaraja's judicial function
from .correction import (
    DriftSource,
    DriftSeverity,
    HealingStrategy,
    HealingStatus,
    UnifiedDriftReport,
    HealingResult,
    CorrectionStats,
    DriftRegistryProtocol,
    CorrectionDispatcherProtocol,
    CorrectionOrchestratorProtocol,
    HealingStrategyResolverProtocol,
    DriftDetector,
    CorrectionHandler,
    NullDriftRegistry,
    NullCorrectionDispatcher,
    adapt_reactor_drift,
    adapt_shuddhi_result,
    LOTUS_POSITION as CORRECTION_POSITION,
)

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "YamarajaProtocolBase",
    # Yamaraja Protocol
    "YamarajaProtocol",
    "NullYamaraja",
    # Yamaraja Types
    "Verdict",
    "Judgeable",
    "JudgmentRecord",
    # Security Protocol (Owned by Yamaraja)
    "SecurityProtocol",
    "NullSecurityProtocol",
    "SecurityLevel",
    # Security Types
    "SecurityCapability",
    "SecurityViolation",
    "SecurityAuditRecord",
    "SecurityStateSnapshot",
    "SecuredSubject",
    # Samskara Protocol (Migration/Transformation)
    "SamskaraType",
    "MigrationStatus",
    "WildProtocol",
    "MigrationVerdict",
    "SamskaraState",
    "MigrationManifest",
    "SamskaraProtocol",
    "SamskaraOwnedProtocol",
    "NullSamskara",
    # Correction Protocol (Drift Detection & Healing)
    "DriftSource",
    "DriftSeverity",
    "HealingStrategy",
    "HealingStatus",
    "UnifiedDriftReport",
    "HealingResult",
    "CorrectionStats",
    "DriftRegistryProtocol",
    "CorrectionDispatcherProtocol",
    "CorrectionOrchestratorProtocol",
    "HealingStrategyResolverProtocol",
    "DriftDetector",
    "CorrectionHandler",
    "NullDriftRegistry",
    "NullCorrectionDispatcher",
    "adapt_reactor_drift",
    "adapt_shuddhi_result",
]
