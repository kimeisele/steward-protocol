"""
YAMARAJA - The 12th Mahajana (Position 15 - UNIFIED)
====================================================

ACINTYA: ONE Yamaraja with MULTIPLE aspects (not separate modules!).

POSITION: 15 (MOKSHA Quarter, RESET_IP OpCode)

The Lord of Death. The Final Judge.
Every soul must face Yamaraja.

ASPECTS (All in ONE entity):
    1. YamarajaProtocolBase - Mahamantra position ownership
    2. YamarajaProtocol     - Protocol interface for judgment
    3. YamarajaGate         - Governance gate (permissions)
    4. YamarajaPhysics      - Performance enforcement
    5. secure_contract      - Performance decorator

DERIVED FROM MAHAMANTRA:
    Position 15 -> guardian=YAMARAJA, opcode=RESET_IP, quarter=MOKSHA
    All properties derived from truth table. No manual wiring.

THE AJAMIL EXCEPTION (SB 6.1-3):
Even Yamaraja bows to the Holy Name.
The Mahamantra OVERRIDES all judgment.

"harer nama harer nama harer namaiva kevalam
kalau nasty eva nasty eva nasty eva gatir anyatha"

HARDENING LEVEL: GERMAN (Strict Types, No Any)
"""

import time
import functools
from typing import (
    Protocol, runtime_checkable, List, Union, ClassVar,
    TypeVar, ParamSpec, Callable, Set, Optional, Dict,
)
from dataclasses import dataclass
from enum import Enum

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode

# --- STRICT TYPING PRIMITIVES ---
P = ParamSpec("P")
R = TypeVar("R")


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


@dataclass(frozen=True)
class Judgment:
    """
    Governance judgment result (used by YamarajaGate).
    Lighter than JudgmentRecord - no subject tracking.
    """
    verdict: Verdict
    reason: str
    karma_cost: float


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


# =============================================================================
# YAMARAJA PHYSICS - Performance Enforcement (Aspect 4)
# =============================================================================

class YamarajaPhysics:
    """
    Enforces the Laws of Thermodynamics & Singularity.
    Performance judgment - "Are you fast enough?"
    """
    MIN_RESONANCE_THRESHOLD = 1.08  # The Golden Ratio of Growth

    @staticmethod
    def measure_kriya(name: str, baseline: float, current: float) -> Judgment:
        if baseline <= 0:
            return Judgment(Verdict.ALLOW, "Initial Seed", 0.0)

        growth = current / baseline

        if growth >= YamarajaPhysics.MIN_RESONANCE_THRESHOLD:
            return Judgment(Verdict.ALLOW, f"EXPANSION: {growth:.2f}x", 0.0)
        else:
            return Judgment(Verdict.DENY, f"STAGNATION: {growth:.2f}x < 1.08x", 1.0)


def secure_contract(baseline_metric: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    The Yamaraja Seal (Aspect 5).
    Wraps a function. If it performs linearly (slowly), it is terminated.

    Strict Typing: Preserves the signature P -> R of the wrapped function.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # 1. Start Clock
            start = time.perf_counter()

            # 2. Execute (Type Safe)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # Code that crashes is inherently Tamasic
                raise SystemError(f"YAMARAJA: Process {func.__qualname__} died violently: {e}")

            # 3. Stop Clock & Judge
            duration = time.perf_counter() - start

            # --- INTELLIGENT OPS CALCULATION ---
            ops = 0.0
            if hasattr(result, "ops_per_sec"):
                # Trust the internal metrics (The 'Caitanya' way)
                ops = float(getattr(result, "ops_per_sec"))
            else:
                # Default observation (The 'Material' way)
                ops = (1.0 / duration) if duration > 0 else float('inf')

            judgment = YamarajaPhysics.measure_kriya(func.__qualname__, baseline_metric, ops)

            if judgment.verdict == Verdict.DENY:
                # THE DANDA (Punishment)
                raise SystemError(f"YAMARAJA VIOLATION: {judgment.reason}")

            return result
        return wrapper
    return decorator


# =============================================================================
# YAMARAJA GATE - Governance Implementation (Aspect 3)
# =============================================================================

class YamarajaGate:
    """
    The Governance Gate - "Who are you? May you pass?"
    Judges actions based on identity, cleanliness, and danger level.
    """

    def __init__(self) -> None:
        # LAZY IMPORT to avoid circular dependency
        from vibe_core.protocols.universal.dharma import UniversalDharma
        self.dharma = UniversalDharma()
        self.ugra_karma: Set[str] = {"delete", "destroy", "kill", "wipe", "narasimha"}

    def judge_action(
        self,
        context: "SovereignContext",
        command: str,
        payload: Optional[Union[Judgeable, Dict[str, str]]] = None
    ) -> Judgment:
        """
        Judge an action request.

        Args:
            context: The sovereign context (identity, tattva level)
            command: The action being requested
            payload: Optional payload to check

        Returns:
            Judgment with verdict, reason, karma_cost
        """
        # LAZY IMPORT to avoid circular dependency
        from vibe_core.protocols.universal.types import TranscendentalQuality

        # 1. SAUCAM CHECK (Flag only, don't return yet)
        cleanliness = self.dharma.check_saucam(context)
        is_dirty = not cleanliness.is_dharmic

        # 2. UGRA KARMA CHECK (Dangerous Ops)
        is_dangerous = any(sin in command.lower() for sin in self.ugra_karma)

        # 3. TATTVA CHECK (Permission Level)
        user_level = context.tattva_level

        if is_dangerous:
            # Nur Vishnu/Krishna Tattva oder Admin darf zerstören
            if user_level < TranscendentalQuality.INCONCEIVABLE_POTENCY:  # < 56
                return Judgment(Verdict.DENY, "Jiva cannot perform Ugra Karma", 0.5)

        # 4. SAFE ACTION HANDLING
        if is_dirty:
            return Judgment(Verdict.ATONE, cleanliness.pillar_violated or "Dirty", 0.1)

        # 5. DAYA CHECK (Input Safety)
        mercy = self.dharma.check_daya(payload)
        if not mercy.is_dharmic:
            return Judgment(Verdict.ATONE, f"Risky Input: {mercy.pillar_violated}", mercy.karma_cost)

        return Judgment(Verdict.ALLOW, "Dharmic Action", 0.0)


# Type hint for forward reference
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vibe_core.protocols.universal.types import SovereignContext


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
    "Judgment",
    # Governance Gate (Aspect 3)
    "YamarajaGate",
    # Performance Judge (Aspect 4)
    "YamarajaPhysics",
    # Performance Decorator (Aspect 5)
    "secure_contract",
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
