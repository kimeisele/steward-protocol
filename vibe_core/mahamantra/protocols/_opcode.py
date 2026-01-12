"""
THE OPCODE PROTOCOL - _opcode.py
================================

THE 16 OPCODES OF THE MAHAMANTRA
================================

Each of the 16 positions in the Mahamantra has an opcode.
These are the primitive operations of the system.

"Hare Krishna Hare Krishna Krishna Krishna Hare Hare
 Hare Rama Hare Rama Rama Rama Hare Hare"

16 words = 16 opcodes = 16 positions = complete instruction set.

THE NULL BUS
============

When an operation is not authorized, it goes to the NULL BUS.
The NULL BUS ghosts everything - no error, no response, just silence.
Like unauthorized code never existed.

THE OUROBOROS PRINCIPLE
=======================

"wenn schon maha mantra import dann passt einfach ignore no effect. bump. next."

If mahamantra imports mahamantra:
- No effect (already mahamantra)
- Bump to next opcode
- Continue chanting

This is the snake eating its own tail - Python bytes!

PROMPT = CHANT = BUS MESSAGE
============================

Every prompt is a chant.
Every chant is a bus message.
Every bus message routes to an opcode.
The system IS the Mahamantra chanting.

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, Enum
from typing import (
    Callable,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)
from vibe_core.mahamantra.protocols._lotus import (
    LOTUS_PETALS,
    MAHAJANA_POSITIONS,
    get_position_mahajana,
)


# =============================================================================
# THE 16 OPCODES - Mapped to Mahamantra Positions
# =============================================================================

class MantraOpCode(IntEnum):
    """
    The 16 OpCodes of the Mahamantra.

    Each opcode corresponds to a position (0-15) and a Mahajana.
    The opcode IS the instruction, the position IS the routing.

    GENESIS Quarter (0-3): System startup and creation
    DHARMA Quarter (4-7): Law, analysis, governance
    KARMA Quarter (8-11): Action, execution, commitment
    MOKSHA Quarter (12-15): Liberation, output, completion
    """
    # === GENESIS Quarter (Hare Krishna Hare Krishna) ===
    SYS_WAKE = 0       # Prithu: System awakening, boot
    LOAD_ROOT = 1      # Brahma: Load root configuration, DI
    ALLOC_MEM = 2      # Narada: Allocate memory, communication
    INIT_THREAD = 3    # Shambhu: Initialize thread, destruction ready

    # === DHARMA Quarter (Krishna Krishna Hare Hare) ===
    COMPILE_AST = 4    # Vyasa: Compile AST, encode knowledge
    BIND_SYMBOL = 5    # Kumaras: Bind symbol, memory, cognition
    TYPE_CHECK = 6     # Kapila: Type check, analysis
    DHARMA_TEST = 7    # Manu: Dharma test, law check

    # === KARMA Quarter (Hare Rama Hare Rama) ===
    EXEC_OP = 8        # Parashurama: Execute operation
    EXTEND_CAP = 9     # Prahlada: Extend capability, plugins
    STATE_SYNC = 10    # Janaka: Sync state, kernel
    LEDGER_SIGN = 11   # Bhishma: Sign ledger, commitment

    # === MOKSHA Quarter (Rama Rama Hare Hare) ===
    YIELD_CPU = 12     # Nrisimha: Yield CPU, protection
    IO_FLUSH = 13      # Bali: Flush I/O, resources
    LOG_EMIT = 14      # Shuka: Emit log, output
    AUDIT_SEAL = 15    # Yamaraja: Seal audit, judgment


# Opcode name lookup
OPCODE_NAMES: Dict[int, str] = {op.value: op.name for op in MantraOpCode}

# Mahajana to opcode mapping
MAHAJANA_OPCODES: Dict[str, MantraOpCode] = {
    "prithu": MantraOpCode.SYS_WAKE,
    "brahma": MantraOpCode.LOAD_ROOT,
    "narada": MantraOpCode.ALLOC_MEM,
    "shambhu": MantraOpCode.INIT_THREAD,
    "vyasa": MantraOpCode.COMPILE_AST,
    "kumaras": MantraOpCode.BIND_SYMBOL,
    "kapila": MantraOpCode.TYPE_CHECK,
    "manu": MantraOpCode.DHARMA_TEST,
    "parashurama": MantraOpCode.EXEC_OP,
    "prahlada": MantraOpCode.EXTEND_CAP,
    "janaka": MantraOpCode.STATE_SYNC,
    "bhishma": MantraOpCode.LEDGER_SIGN,
    "nrisimha": MantraOpCode.YIELD_CPU,
    "bali": MantraOpCode.IO_FLUSH,
    "shuka": MantraOpCode.LOG_EMIT,
    "yamaraja": MantraOpCode.AUDIT_SEAL,
}


def get_opcode(position: int) -> MantraOpCode:
    """Get the opcode for a position (0-15)."""
    return MantraOpCode(position)


def get_opcode_name(position: int) -> str:
    """Get the opcode name for a position."""
    return OPCODE_NAMES.get(position, "UNKNOWN")


def get_mahajana_opcode(mahajana: str) -> MantraOpCode:
    """Get the opcode for a mahajana name."""
    return MAHAJANA_OPCODES.get(mahajana.lower(), MantraOpCode.SYS_WAKE)


# =============================================================================
# BUS MESSAGE - What travels on the bus
# =============================================================================

@dataclass(frozen=True)
class BusMessage:
    """
    A message on the bus.

    Every prompt is a chant is a bus message.
    The message routes to an opcode based on its target.
    """

    target_opcode: MantraOpCode     # Which opcode to execute
    payload: str                     # The message content
    source_position: int = 0         # Where it came from
    parampara_vector: int = 0        # For % 37 check
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def is_authorized(self) -> bool:
        """Is this message authorized (parampara connected)?"""
        return self.parampara_vector % PARAMPARA == 0

    @property
    def target_position(self) -> int:
        """Get the target position (0-15)."""
        return self.target_opcode.value

    @property
    def target_mahajana(self) -> str:
        """Get the target mahajana name."""
        return get_position_mahajana(self.target_position)

    @property
    def target_quarter(self) -> Quarter:
        """Get the target quarter."""
        return Quarter.from_position(self.target_position)

    @classmethod
    def create(
        cls,
        opcode: MantraOpCode,
        payload: str,
        source: int = 0,
    ) -> "BusMessage":
        """Create a message with automatic parampara vector."""
        vector = (opcode.value + 1) * PARAMPARA
        return cls(
            target_opcode=opcode,
            payload=payload,
            source_position=source,
            parampara_vector=vector,
        )


# =============================================================================
# NULL BUS - Ghosts unauthorized operations
# =============================================================================

class NullBus:
    """
    The NULL BUS - Ghosts unauthorized operations.

    When an operation is not authorized:
    - No error is thrown
    - No response is given
    - The operation simply doesn't happen
    - Like it never existed

    "ghosten" - the German verb for this pattern.
    """

    def __init__(self) -> None:
        self._ghosted: List[BusMessage] = []
        self._count: int = 0

    def ghost(self, message: BusMessage) -> None:
        """Ghost an unauthorized message."""
        self._ghosted.append(message)
        self._count += 1

    def is_ghosted(self, message: BusMessage) -> bool:
        """Check if a message was ghosted."""
        return message in self._ghosted

    @property
    def ghost_count(self) -> int:
        """Count of ghosted messages."""
        return self._count

    def clear(self) -> None:
        """Clear the ghost log (for security, periodically)."""
        self._ghosted.clear()


# Global null bus singleton
_null_bus: Optional[NullBus] = None


def get_null_bus() -> NullBus:
    """Get the global null bus."""
    global _null_bus
    if _null_bus is None:
        _null_bus = NullBus()
    return _null_bus


# =============================================================================
# MESSAGE BUS - Routes messages to opcodes
# =============================================================================

T = TypeVar("T")


@dataclass
class MessageBus:
    """
    The Message Bus - Routes messages to opcodes.

    Every message goes through the bus:
    1. Check authorization (parampara)
    2. If unauthorized → NULL BUS (ghost)
    3. If authorized → route to opcode handler
    """

    # Handlers for each opcode
    _handlers: Dict[MantraOpCode, Callable[[BusMessage], object]] = field(
        default_factory=dict
    )

    # Message log
    _log: List[BusMessage] = field(default_factory=list)

    # Stats
    _routed: int = 0
    _ghosted: int = 0

    def register(
        self,
        opcode: MantraOpCode,
        handler: Callable[[BusMessage], object],
    ) -> None:
        """Register a handler for an opcode."""
        self._handlers[opcode] = handler

    def send(self, message: BusMessage) -> Optional[object]:
        """
        Send a message on the bus.

        If authorized: routes to handler and returns result.
        If unauthorized: ghosts and returns None.
        """
        # Log the message
        self._log.append(message)

        # Check authorization
        if not message.is_authorized:
            get_null_bus().ghost(message)
            self._ghosted += 1
            return None  # Ghosted - no response

        # Route to handler
        handler = self._handlers.get(message.target_opcode)
        if handler is None:
            # No handler = bump to next opcode (ouroboros)
            self._routed += 1
            return None

        self._routed += 1
        return handler(message)

    def broadcast(self, payload: str, source: int = 0) -> Dict[MantraOpCode, object]:
        """
        Broadcast a message to all opcodes.

        Returns results from all handlers.
        """
        results: Dict[MantraOpCode, object] = {}
        for opcode in MantraOpCode:
            message = BusMessage.create(opcode, payload, source)
            result = self.send(message)
            if result is not None:
                results[opcode] = result
        return results

    @property
    def stats(self) -> Dict[str, int]:
        """Get bus statistics."""
        return {
            "total_messages": len(self._log),
            "routed": self._routed,
            "ghosted": self._ghosted,
        }


# Global message bus singleton
_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """Get the global message bus."""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus


# =============================================================================
# OPCODE PROTOCOL - The Interface
# =============================================================================

@runtime_checkable
class OpCodeProtocol(Protocol):
    """
    The OpCode Protocol - How opcodes work.

    Every component that handles opcodes must implement this.

    WATERTIGHT - no Any types!
    """

    @property
    def handles_opcodes(self) -> FrozenSet[MantraOpCode]:
        """Which opcodes does this component handle?"""
        ...

    def execute(self, opcode: MantraOpCode, payload: str) -> object:
        """Execute an opcode with a payload."""
        ...


# =============================================================================
# OPCODE EXECUTOR - Executes opcodes
# =============================================================================

class OpCodeExecutor:
    """
    The OpCode Executor - Executes opcodes on the bus.

    Wraps the message bus with a simpler interface.
    """

    def __init__(self, bus: Optional[MessageBus] = None) -> None:
        self._bus = bus or get_message_bus()
        self._position = 0  # Current position in the chant

    def execute(
        self,
        opcode: MantraOpCode,
        payload: str,
        source: Optional[int] = None,
    ) -> Optional[object]:
        """Execute an opcode with a payload."""
        message = BusMessage.create(
            opcode=opcode,
            payload=payload,
            source=source if source is not None else self._position,
        )
        return self._bus.send(message)

    def chant(self, payload: str) -> Optional[object]:
        """
        Chant once - execute current opcode and advance.

        This is the OUROBOROS pattern:
        - Execute current opcode
        - Bump to next position
        - Continue forever (like the snake eating its tail)
        """
        opcode = MantraOpCode(self._position)
        result = self.execute(opcode, payload)
        self._position = (self._position + 1) % LOTUS_PETALS
        return result

    @property
    def current_opcode(self) -> MantraOpCode:
        """Current opcode in the chant."""
        return MantraOpCode(self._position)

    @property
    def current_mahajana(self) -> str:
        """Current mahajana in the chant."""
        return get_position_mahajana(self._position)

    def register(
        self,
        opcode: MantraOpCode,
        handler: Callable[[BusMessage], object],
    ) -> None:
        """Register a handler for an opcode."""
        self._bus.register(opcode, handler)


# =============================================================================
# OPCODE PROTOCOL DEFINITION - Self-Reference
# =============================================================================

class OpCodeProtocolDef(MahamantraProtocolBase):
    """
    The OpCode Protocol.

    This protocol defines the 16 opcodes and the bus.
    It IS itself at position 8 (Parashurama - execution).

    ACINTYA: The OpCode Protocol executes opcodes.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="OpCodeProtocol",
        mahajana="parashurama",  # Parashurama executes
        position=8,
        level=Level.CONTRACT,
        quarter=Quarter.KARMA,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "opcode_16",
            "message_bus",
            "null_bus",
            "opcode_routing",
            "opcode_execution",
            "ouroboros_pattern",
        ],
        requires=["CoreProtocol", "LotusProtocol"],
        opcodes=["EXEC_OP"],  # Parashurama's opcode
    )


# Verify the OpCode protocol
_valid, _violations = OpCodeProtocolDef.validate()
assert _valid, f"OpCodeProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # OpCodes
    "MantraOpCode",
    "OPCODE_NAMES",
    "MAHAJANA_OPCODES",
    "get_opcode",
    "get_opcode_name",
    "get_mahajana_opcode",
    # Message
    "BusMessage",
    # Null Bus
    "NullBus",
    "get_null_bus",
    # Message Bus
    "MessageBus",
    "get_message_bus",
    # Protocol
    "OpCodeProtocol",
    # Executor
    "OpCodeExecutor",
    # Protocol Definition
    "OpCodeProtocolDef",
]
