"""
MAHAJANA PROTOCOL - The Discovered Interface
=============================================

"We don't BUILD, we DISCOVER."

This protocol is not designed - it is DISCOVERED from:
- The existing implementations (narada.py, yamaraja.py, prahlad.py)
- The OpCode definitions (mantra.py)
- The Mahajana principles (SB 6.3.20)

The Mahajana Protocol defines what it MEANS to be a Mahajana.
Each Mahajana:
1. OWNS certain OpCodes (verified via router)
2. HANDLES requests in their domain
3. VALIDATES according to their principle

GAD-000 Compliant:
- Discoverable: Each Mahajana declares its OpCodes
- Observable: Handle returns traceable results
- Parseable: Strict typed inputs/outputs
- Composable: Mahajanas can delegate to each other
- Idempotent: Same input = same judgment
- Recoverable: Failures are explicit, not silent
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x340d6bca"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable, Any, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.mahajanas.router import Mahajana, route


# =============================================================================
# RESULT TYPES - What a Mahajana returns
# =============================================================================

class MahajanaVerdict(str, Enum):
    """The outcome of a Mahajana's judgment."""
    ACCEPT = "accept"       # Request is valid, proceed
    REJECT = "reject"       # Request is invalid, stop
    DELEGATE = "delegate"   # Another Mahajana should handle
    TRANSFORM = "transform" # Request needs modification first


@dataclass
class MahajanaResult:
    """
    The result of a Mahajana handling a request.

    GAD-000: Observable, Parseable, Recoverable
    """
    verdict: MahajanaVerdict
    mahajana: Mahajana          # Who made this judgment
    opcode: MantraOpCode        # Which OpCode triggered
    payload: Optional[Any]      # Transformed/returned data
    reason: str                 # Human-readable explanation
    delegate_to: Optional[Mahajana] = None  # If verdict is DELEGATE

    def is_success(self) -> bool:
        return self.verdict == MahajanaVerdict.ACCEPT

    def should_delegate(self) -> bool:
        return self.verdict == MahajanaVerdict.DELEGATE and self.delegate_to is not None


# =============================================================================
# THE PROTOCOL - Discovered from existing implementations
# =============================================================================

ContextT = TypeVar("ContextT")
PayloadT = TypeVar("PayloadT")


@runtime_checkable
class MahajanaProtocol(Protocol):
    """
    The interface that every Mahajana implementation must satisfy.

    Discovered from:
    - YamarajaGate.judge_action()
    - NaradaProtocol.spy()
    - PrahladProtocol.remember()

    Each Mahajana:
    1. Declares which OpCodes it owns
    2. Validates if it can handle a request
    3. Handles the request and returns a result
    """

    @property
    def identity(self) -> Mahajana:
        """Which Mahajana am I?"""
        ...

    def get_opcodes(self) -> List[MantraOpCode]:
        """
        Declare which OpCodes this Mahajana owns.

        GAD-000: Discoverable
        """
        ...

    def can_handle(self, opcode: MantraOpCode) -> bool:
        """
        Check if this Mahajana can handle the given OpCode.

        Default: opcode in self.get_opcodes()
        But may be overridden for delegation patterns.
        """
        ...

    def handle(
        self,
        opcode: MantraOpCode,
        context: Any,
        payload: Any
    ) -> MahajanaResult:
        """
        Handle a request for the given OpCode.

        Returns MahajanaResult with verdict and transformed payload.

        GAD-000: Observable (result is traceable)
                 Idempotent (same input = same result)
                 Recoverable (failures are explicit)
        """
        ...


# =============================================================================
# BASE IMPLEMENTATION - The Discovered Pattern
# =============================================================================

class BaseMahajana:
    """
    Base implementation of MahajanaProtocol.

    Provides:
    - Automatic OpCode discovery via router
    - Default can_handle() implementation
    - Stub handle() that must be overridden

    Subclasses only need to:
    1. Set self._identity
    2. Override handle() for their domain
    """

    def __init__(self, identity: Mahajana) -> None:
        self._identity = identity
        self._opcodes: Optional[List[MantraOpCode]] = None

    @property
    def identity(self) -> Mahajana:
        return self._identity

    def get_opcodes(self) -> List[MantraOpCode]:
        """Discover OpCodes from router (lazy cached)."""
        if self._opcodes is None:
            from vibe_core.protocols.mahajanas.router import get_opcodes
            self._opcodes = get_opcodes(self._identity)
        return self._opcodes

    def can_handle(self, opcode: MantraOpCode) -> bool:
        """Default: Check if opcode is in our list."""
        return opcode in self.get_opcodes()

    def handle(
        self,
        opcode: MantraOpCode,
        context: Any,
        payload: Any
    ) -> MahajanaResult:
        """
        Override this in subclass.

        Default: Reject with "not implemented".
        """
        return MahajanaResult(
            verdict=MahajanaVerdict.REJECT,
            mahajana=self._identity,
            opcode=opcode,
            payload=None,
            reason=f"{self._identity.value} has not discovered how to handle {opcode.name}"
        )

    def _accept(
        self,
        opcode: MantraOpCode,
        payload: Any,
        reason: str
    ) -> MahajanaResult:
        """Helper: Create an ACCEPT result."""
        return MahajanaResult(
            verdict=MahajanaVerdict.ACCEPT,
            mahajana=self._identity,
            opcode=opcode,
            payload=payload,
            reason=reason
        )

    def _reject(
        self,
        opcode: MantraOpCode,
        reason: str
    ) -> MahajanaResult:
        """Helper: Create a REJECT result."""
        return MahajanaResult(
            verdict=MahajanaVerdict.REJECT,
            mahajana=self._identity,
            opcode=opcode,
            payload=None,
            reason=reason
        )

    def _delegate(
        self,
        opcode: MantraOpCode,
        to: Mahajana,
        reason: str
    ) -> MahajanaResult:
        """Helper: Create a DELEGATE result."""
        return MahajanaResult(
            verdict=MahajanaVerdict.DELEGATE,
            mahajana=self._identity,
            opcode=opcode,
            payload=None,
            reason=reason,
            delegate_to=to
        )


# =============================================================================
# NULL IMPLEMENTATION - The Silent Mahajana
# =============================================================================

class NullMahajana(BaseMahajana):
    """
    A Mahajana that accepts everything silently.

    Used in tests where Mahajana logic is not the focus.
    """

    def __init__(self, identity: Mahajana = Mahajana.BRAHMA) -> None:
        super().__init__(identity)

    def handle(
        self,
        opcode: MantraOpCode,
        context: Any,
        payload: Any
    ) -> MahajanaResult:
        return self._accept(opcode, payload, "NullMahajana accepts all")


__all__ = [
    "MahajanaVerdict",
    "MahajanaResult",
    "MahajanaProtocol",
    "BaseMahajana",
    "NullMahajana",
]
