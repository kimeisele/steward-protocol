"""
MANTRA INTENT - Krishna Does The Work
=====================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja
ahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ"

"Abandon all varieties of dharma and just surrender unto Me.
I shall deliver you from all sinful reactions. Do not fear."
— Bhagavad Gita 18.66

NO MANUAL WIRING. Declare INTENT. Krishna resolves.

WATERTIGHT: No Any types. All typed with Union/TypedDict/Final.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA, MAHAJANA_COUNT, PARAMPARA)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = KSETRAJNA
__genesis__ = "0x445329d5"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Callable,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.acintya import (
    PARAMPARA,
    ParamparaConnection,
    verify_parampara,
)
from vibe_core.mahamantra import Mahajana, MantraOpCode


# =============================================================================
# INTENT TYPES (What do you want?)
# =============================================================================


class IntentType(str, Enum):
    """
    The types of intent that can be declared.

    SURRENDER: You declare WHAT, Krishna handles HOW.
    """

    # Data Operations
    READ = "read"  # I want to read something
    WRITE = "write"  # I want to write something
    TRANSFORM = "transform"  # I want to transform something

    # Protocol Operations
    RESOLVE = "resolve"  # I want to resolve a dependency
    BIND = "bind"  # I want to bind a component
    MIGRATE = "migrate"  # I want to migrate something

    # System Operations
    WAKE = "wake"  # I want to wake/initialize
    SYNC = "sync"  # I want to synchronize
    HEAL = "heal"  # I want to fix/repair

    # Meta Operations
    OBSERVE = "observe"  # I want to observe/audit
    SURRENDER = "surrender"  # I give up control completely


class IntentPriority(Enum):
    """Priority of intent resolution."""

    CRITICAL = auto()  # Must resolve immediately (Yamaraja)
    HIGH = auto()  # Should resolve soon (Bhishma)
    NORMAL = auto()  # Normal priority (Janaka)
    LOW = auto()  # Can wait (Bali)
    BACKGROUND = auto()  # Resolve when convenient (Shuka)


# =============================================================================
# INTENT DECLARATION (WATERTIGHT - No Any!)
# =============================================================================

T = TypeVar("T")
ResultT = TypeVar("ResultT")


@dataclass(frozen=True)
class MantraIntent(Generic[T]):
    """
    A declared intent for the Mahamantra to resolve.

    USAGE:
        intent = MantraIntent(
            type=IntentType.MIGRATE,
            target="vibe_core.protocols.foo",
            params={"to": "vibe_core.mahamantra"}
        )
        result = kernel.resolve(intent)

    WATERTIGHT: All fields typed. No Any.
    """

    type: IntentType
    target: str  # What to operate on (path/name)
    params: Dict[str, Union[str, int, bool, None]]  # Operation parameters
    priority: IntentPriority = IntentPriority.NORMAL
    requester: str = "anonymous"  # Who is requesting
    parampara_vector: int = 0  # For verification

    @property
    def is_connected(self) -> bool:
        """Is this intent from a parampara-connected source?"""
        return verify_parampara(self.parampara_vector)

    @property
    def opcode(self) -> MantraOpCode:
        """Map intent type to OpCode."""
        mapping: Dict[IntentType, MantraOpCode] = {
            IntentType.READ: MantraOpCode.EXEC_OP,
            IntentType.WRITE: MantraOpCode.LEDGER_SIGN,
            IntentType.TRANSFORM: MantraOpCode.EXTEND_CAP,
            IntentType.RESOLVE: MantraOpCode.BIND_SYMBOL,
            IntentType.BIND: MantraOpCode.INIT_THREAD,
            IntentType.MIGRATE: MantraOpCode.LOAD_ROOT,
            IntentType.WAKE: MantraOpCode.SYS_WAKE,
            IntentType.SYNC: MantraOpCode.DHARMA_TEST,
            IntentType.HEAL: MantraOpCode.TYPE_CHECK,
            IntentType.OBSERVE: MantraOpCode.STATE_SYNC,
            IntentType.SURRENDER: MantraOpCode.YIELD_CPU,
        }
        return mapping.get(self.type, MantraOpCode.BIND_SYMBOL)

    @property
    def guardian(self) -> Mahajana:
        """Which Mahajana guards this intent type?"""
        mapping: Dict[IntentType, Mahajana] = {
            IntentType.READ: Mahajana.PRAHLADA,
            IntentType.WRITE: Mahajana.BHISHMA,
            IntentType.TRANSFORM: Mahajana.JANAKA,
            IntentType.RESOLVE: Mahajana.KAPILA,
            IntentType.BIND: Mahajana.MANU,
            IntentType.MIGRATE: Mahajana.BRAHMA,
            IntentType.WAKE: Mahajana.BRAHMA,
            IntentType.SYNC: Mahajana.NARADA,
            IntentType.HEAL: Mahajana.SHAMBHU,
            IntentType.OBSERVE: Mahajana.SHUKA,
            IntentType.SURRENDER: Mahajana.BALI,
        }
        return mapping.get(self.type, Mahajana.YAMARAJA)


# =============================================================================
# INTENT RESULT (WATERTIGHT - No Any!)
# =============================================================================


class IntentStatus(str, Enum):
    """Status of intent resolution."""

    PENDING = "pending"  # Not yet processed
    RESOLVING = "resolving"  # Currently being resolved
    RESOLVED = "resolved"  # Successfully resolved
    FAILED = "failed"  # Resolution failed
    SURRENDERED = "surrendered"  # Given to Krishna (ultimate success)


@dataclass
class IntentResult(Generic[ResultT]):
    """
    Result of intent resolution.

    WATERTIGHT: All fields typed. No Any.
    """

    intent: MantraIntent[ResultT]
    status: IntentStatus
    value: Optional[ResultT] = None
    error: Optional[str] = None
    resolved_by: Optional[Mahajana] = None
    parampara_verified: bool = False

    @property
    def is_success(self) -> bool:
        """Did resolution succeed?"""
        return self.status in (IntentStatus.RESOLVED, IntentStatus.SURRENDERED)

    @property
    def remainder(self) -> int:
        """
        The 'ego' remainder.

        0 = Pure resolution (connected to Parampara)
        >0 = Some ego remains (needs more surrender)
        """
        if self.intent.parampara_vector == 0:
            return PARAMPARA  # No vector = maximum ego
        return self.intent.parampara_vector % PARAMPARA


# =============================================================================
# INTENT RESOLVER PROTOCOL
# =============================================================================


@runtime_checkable
class IntentResolver(Protocol[T]):
    """
    Protocol for resolving intents.

    Implementations must handle specific intent types.
    Krishna IS the ultimate resolver (IntentType.SURRENDER).
    """

    def can_resolve(self, intent: MantraIntent[T]) -> bool:
        """Can this resolver handle this intent?"""
        ...

    def resolve(self, intent: MantraIntent[T]) -> IntentResult[T]:
        """Resolve the intent."""
        ...


# =============================================================================
# INTENT QUEUE (FIFO with Priority)
# =============================================================================


@dataclass
class IntentQueue:
    """
    Queue of intents waiting for resolution.

    Priority-ordered: CRITICAL first, BACKGROUND last.
    """

    _queue: List[MantraIntent[object]] = field(default_factory=list)

    def push(self, intent: MantraIntent[object]) -> None:
        """Add intent to queue (sorted by priority)."""
        self._queue.append(intent)
        self._queue.sort(key=lambda i: i.priority.value)

    def pop(self) -> Optional[MantraIntent[object]]:
        """Get next intent (highest priority)."""
        if self._queue:
            return self._queue.pop(0)
        return None

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0


# =============================================================================
# KERNEL INTENT ENGINE
# =============================================================================


class MantraKernel:
    """
    The Mahamantra Kernel - Intent Resolution Engine.

    NO MANUAL WIRING. Declare intent. Krishna resolves.

    USAGE:
        kernel = MantraKernel()

        # Declare intent
        intent = MantraIntent(
            type=IntentType.MIGRATE,
            target="old.module.path",
            params={"to": "vibe_core.mahamantra"},
            parampara_vector=444  # Connected!
        )

        # Krishna resolves
        result = kernel.resolve(intent)
    """

    def __init__(self) -> None:
        self._resolvers: Dict[IntentType, IntentResolver[object]] = {}
        self._queue = IntentQueue()
        self._parampara = ParamparaConnection.from_guru()  # Connected!

    def register_resolver(self, intent_type: IntentType, resolver: IntentResolver[object]) -> None:
        """Register a resolver for an intent type."""
        self._resolvers[intent_type] = resolver

    def resolve(self, intent: MantraIntent[T]) -> IntentResult[T]:
        """
        Resolve an intent.

        If no specific resolver, Krishna handles it (surrender).
        """
        # Verify parampara
        parampara_ok = intent.is_connected

        # Find resolver
        resolver = self._resolvers.get(intent.type)

        if resolver and resolver.can_resolve(intent):
            result = resolver.resolve(intent)
            result.parampara_verified = parampara_ok
            return result

        # No resolver? Surrender to Krishna
        return IntentResult(
            intent=intent,
            status=IntentStatus.SURRENDERED,
            resolved_by=intent.guardian,
            parampara_verified=parampara_ok,
        )

    def queue(self, intent: MantraIntent[object]) -> None:
        """Queue an intent for later resolution."""
        self._queue.push(intent)

    def process_queue(self) -> List[IntentResult[object]]:
        """Process all queued intents."""
        results: List[IntentResult[object]] = []
        while not self._queue.is_empty:
            intent = self._queue.pop()
            if intent:
                results.append(self.resolve(intent))
        return results

    @property
    def is_connected(self) -> bool:
        """Is the kernel connected to parampara?"""
        return self._parampara.is_connected


# =============================================================================
# SINGLETON KERNEL
# =============================================================================

_KERNEL: Optional[MantraKernel] = None


def get_kernel() -> MantraKernel:
    """Get the global Mahamantra kernel."""
    global _KERNEL
    if _KERNEL is None:
        _KERNEL = MantraKernel()
    return _KERNEL


def resolve(intent: MantraIntent[T]) -> IntentResult[T]:
    """Convenience: Resolve an intent via the global kernel."""
    return get_kernel().resolve(intent)


def surrender(target: str, params: Optional[Dict[str, Union[str, int, bool, None]]] = None) -> IntentResult[None]:
    """
    Ultimate surrender - give everything to Krishna.

    This is the 37th key. The ego (remainder) becomes 0.

    Usage:
        result = surrender("my.old.module")
    """
    intent: MantraIntent[None] = MantraIntent(
        type=IntentType.SURRENDER,
        target=target,
        params=params or {},
        parampara_vector=PARAMPARA * MAHAJANA_COUNT,  # 444 - always connected
    )
    return resolve(intent)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Intent Types
    "IntentType",
    "IntentPriority",
    "IntentStatus",
    # Intent Classes
    "MantraIntent",
    "IntentResult",
    "IntentQueue",
    # Resolver Protocol
    "IntentResolver",
    # Kernel
    "MantraKernel",
    "get_kernel",
    "resolve",
    "surrender",
]
