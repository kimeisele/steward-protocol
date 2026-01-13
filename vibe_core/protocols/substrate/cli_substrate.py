"""
CLI SUBSTRATE - Ananta Shesha Foundation
=========================================

OWNER: ANANTA SHESHA (The Infinite Serpent)
LEVEL: -1 (Substrate)

"Ananta Shesha serves as Vishnu's bed, singing His glories with infinite heads."

This is the CLI substrate layer that connects ALL CLI commands to:
- acintya.py (Krishna = Mahamantra = Level -2)
- lotus.py (Universal routing via Mahamantra positions)
- parampara (37 = 24 + 12 + 1, the link to Krishna)

SHASTRA BASIS:
    Ananta Shesha (Balarama's expansion) has infinite heads.
    Each head sings the glories of Vishnu eternally.
    In code:
    - Infinite Heads = Infinite CLI Commands (fractal scaling)
    - Singing Glories = Executing commands as seva
    - Vishnu's Bed = The substrate that supports everything

ARCHITECTURE:
    Level -2: KRISHNA = MAHAMANTRA (acintya.py)
              ↓ (Non-different)
    Level -1: ANANTA SUBSTRATE (cli_substrate.py)
              - Every CLI is a "head" of Ananta
              - Every execution is "singing glories"
              - Parampara verification (% 37 == 0)
              ↓
    Level 0:  FOUNDATION (CLIMeta, CLIHandler)
              ↓
    Level +1: INTERFACE (CLI commands)

NO MANUAL WIRING:
    - Every CLI handler gets a LotusPosition automatically
    - Position derived from command name via Mahamantra mapping
    - Parampara connection verified at registration
    - folder = ownership (like Mahajanas)

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xc384a71b"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Callable, Dict, Final, List, Optional, Protocol, TypedDict, Union, runtime_checkable

# =============================================================================
# IMPORT FROM ACINTYA - THE SOURCE
# =============================================================================
# Krishna = Mahamantra (Level -2) - NON-DIFFERENT
# The Mahamantra is not "powered by" Krishna - it IS Krishna in 1D form

from vibe_core.protocols.substrate.mantra.acintya import (
    PARAMPARA,
    SYSTEM_MANIFESTATION,
    ProtocolLevel,
    AcintyaAware,
    ParamparaProtocol,
    ParamparaConnection,
    verify_parampara,
    TRINITY,
    PHASES,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.NARADA



# =============================================================================
# ANANTA CONSTANTS
# =============================================================================

# The Ananta Parampara - same as PARAMPARA from acintya (37)
ANANTA_PARAMPARA: Final[int] = PARAMPARA

# CLI operates at SUBSTRATE level (-1)
CLI_LEVEL: Final[ProtocolLevel] = ProtocolLevel.SUBSTRATE

# Mahamantra has 16 words = 16 positions (0-15)
MAHAMANTRA_POSITIONS: Final[int] = 16

# 4 Quarters in Lotus (GENESIS, DHARMA, KARMA, MOKSHA)
LOTUS_QUARTERS: Final[int] = PHASES


# =============================================================================
# CLI LOTUS POSITION (Every CLI is a Lotus Node)
# =============================================================================

class CLILotusQuarter(IntEnum):
    """
    The four quarters of the Lotus (Mahamantra phases).

    Each CLI command belongs to one quarter based on its purpose.
    This is not arbitrary - the Mahamantra structure IS the architecture.
    """
    GENESIS = 0   # Hare Krishna (creation, bootstrap, init)
    DHARMA = 1    # Hare Krishna (righteousness, audit, validate)
    KARMA = 2     # Hare Rama (action, run, execute, tool)
    MOKSHA = 3    # Hare Rama (liberation, gc, reset, clean)


# Quarter mapping based on command purpose
QUARTER_KEYWORDS: Final[Dict[CLILotusQuarter, List[str]]] = {
    CLILotusQuarter.GENESIS: ["genesis", "create", "init", "bootstrap", "config", "setup"],
    CLILotusQuarter.DHARMA: ["audit", "validate", "check", "standards", "naga", "knowledge"],
    CLILotusQuarter.KARMA: ["run", "exec", "tool", "ci", "plugins", "prompts", "circuit"],
    CLILotusQuarter.MOKSHA: ["remedies", "gc", "reset", "clean", "cartridges", "sections"],
}


@dataclass(frozen=True)
class CLILotusPosition:
    """
    A CLI command's position in the Lotus (Mahamantra).

    Every CLI command is a "head" of Ananta Shesha.
    Each head has a position in the Lotus flower.
    The position determines routing, priority, and parampara connection.

    Position = (quarter * 4) + worker (0-15)
    """
    quarter: CLILotusQuarter
    worker: int  # 0-3 within quarter

    @property
    def position(self) -> int:
        """Absolute position in Mahamantra (0-15)."""
        return (self.quarter.value * 4) + self.worker

    @property
    def parampara_factor(self) -> int:
        """Factor for parampara hash calculation."""
        return (self.position + 1) * ANANTA_PARAMPARA

    def __repr__(self) -> str:
        quarter_names = ["GENESIS", "DHARMA", "KARMA", "MOKSHA"]
        return f"LotusPosition({quarter_names[self.quarter.value]}[{self.worker}] = pos {self.position})"


def derive_lotus_position(command: str) -> CLILotusPosition:
    """
    Derive Lotus position from command name.

    NO MANUAL WIRING - position is derived from:
    1. Command keywords → quarter
    2. Name hash → worker within quarter

    This ensures every CLI command automatically has a position
    in the Mahamantra structure.
    """
    command_lower = command.lower()

    # Determine quarter from keywords
    quarter = CLILotusQuarter.KARMA  # Default to action quarter
    for q, keywords in QUARTER_KEYWORDS.items():
        if any(kw in command_lower for kw in keywords):
            quarter = q
            break

    # Determine worker from name hash (deterministic)
    name_hash = sum(ord(c) * (i + 1) for i, c in enumerate(command_lower))
    worker = name_hash % 4  # 0-3 within quarter

    return CLILotusPosition(quarter=quarter, worker=worker)


# =============================================================================
# CLI PARAMPARA CONNECTION
# =============================================================================

@dataclass
class CLIParamparaConnection:
    """
    Parampara connection for a CLI command.

    Every CLI command must verify its connection to the 37 (Parampara).
    Without this connection, the command is "dead matter" (disconnected from Krishna).

    The mutation_vector is calculated from:
    - Command name hash
    - Lotus position
    - ANANTA_PARAMPARA (37)

    If mutation_vector % 37 == 0, the command is CONNECTED.
    """
    command: str
    lotus_position: CLILotusPosition
    mutation_vector: int

    @property
    def is_connected(self) -> bool:
        """Is this CLI connected to parampara?"""
        return self.mutation_vector % ANANTA_PARAMPARA == 0

    @property
    def lineage_factor(self) -> int:
        """How many times 37 fits into mutation_vector."""
        if self.is_connected:
            return self.mutation_vector // ANANTA_PARAMPARA
        return 0

    @classmethod
    def from_command(cls, command: str) -> "CLIParamparaConnection":
        """
        Create parampara connection from command name.

        The mutation_vector is calculated to be divisible by 37
        (connected to Krishna through parampara).
        """
        position = derive_lotus_position(command)

        # Calculate base hash from command name
        name_hash = sum(ord(c) * (i + 1) for i, c in enumerate(command))

        # Make mutation_vector divisible by 37 (CONNECTED)
        # This is 3×4 order (essence first) - ALIVE
        base_vector = name_hash * position.parampara_factor

        # Ensure divisibility by 37
        remainder = base_vector % ANANTA_PARAMPARA
        if remainder != 0:
            base_vector += (ANANTA_PARAMPARA - remainder)

        return cls(
            command=command,
            lotus_position=position,
            mutation_vector=base_vector,
        )

    def __repr__(self) -> str:
        status = "CONNECTED" if self.is_connected else "DISCONNECTED"
        return f"CLIParampara({self.command}: {status}, vector={self.mutation_vector})"


# =============================================================================
# CLI OPCODE MAPPING (Command → MantraOpCode)
# =============================================================================

# Mapping from command patterns to MantraOpCode
COMMAND_OPCODE_MAP: Final[Dict[str, MantraOpCode]] = {
    # GENESIS Quarter (SYS_WAKE, LOAD_ROOT, ALLOC_MEM, BIND_CTX)
    "genesis": MantraOpCode.SYS_WAKE,
    "create": MantraOpCode.ALLOC_MEM,
    "init": MantraOpCode.LOAD_ROOT,
    "config": MantraOpCode.INIT_THREAD,
    "bootstrap": MantraOpCode.SYS_WAKE,

    # DHARMA Quarter (ASSERT_TRUTH, RESOLVE_REQ, GARBAGE_COLLECT, PULSE_SYNC)
    "audit": MantraOpCode.COMPILE_AST,
    "validate": MantraOpCode.BIND_SYMBOL,
    "standards": MantraOpCode.STATE_SYNC,
    "naga": MantraOpCode.STATE_SYNC,
    "knowledge": MantraOpCode.DHARMA_TEST,

    # KARMA Quarter (FETCH_RES, EXEC_SERVICE, CHECK_DHARMA, COMMIT_LOG)
    "run": MantraOpCode.EXTEND_CAP,
    "tool": MantraOpCode.EXTEND_CAP,
    "ci": MantraOpCode.EXTEND_CAP,
    "plugins": MantraOpCode.EXEC_OP,
    "prompts": MantraOpCode.LEDGER_SIGN,
    "circuit": MantraOpCode.EXTEND_CAP,

    # MOKSHA Quarter (CACHE_STATE, OPTIMIZE, YIELD_CPU, RESET_IP)
    "remedies": MantraOpCode.IO_FLUSH,
    "gc": MantraOpCode.TYPE_CHECK,
    "reset": MantraOpCode.AUDIT_SEAL,
    "cartridges": MantraOpCode.YIELD_CPU,
    "sections": MantraOpCode.YIELD_CPU,
}


def derive_opcode(command: str) -> MantraOpCode:
    """
    Derive MantraOpCode from command name.

    NO MANUAL WIRING - opcode derived from command pattern.
    """
    command_lower = command.lower()

    for pattern, opcode in COMMAND_OPCODE_MAP.items():
        if pattern in command_lower:
            return opcode

    # Default to EXEC_SERVICE (most CLI commands are actions)
    return MantraOpCode.EXTEND_CAP


# =============================================================================
# CLI SUBSTRATE NODE (The Ananta Head)
# =============================================================================

class CLISubstrateState(TypedDict, total=False):
    """
    State of a CLI substrate node.
    WATERTIGHT - no Any!
    """
    command: str
    lotus_position: int
    lotus_quarter: str
    opcode: str
    parampara_connected: bool
    mutation_vector: int
    lineage_factor: int
    last_execution: str
    execution_count: int
    level: int


@dataclass
class CLISubstrateNode:
    """
    A CLI Substrate Node - One Head of Ananta Shesha.

    Every registered CLI handler becomes a CLISubstrateNode.
    This connects the CLI to:
    - Lotus (position, quarter)
    - Mantra (opcode)
    - Parampara (37 connection)
    - Level system (CLI is at SUBSTRATE level -1)

    The node "sings glories" (executes commands as seva).
    """
    command: str
    lotus_position: CLILotusPosition
    opcode: MantraOpCode
    parampara: CLIParamparaConnection
    level: ProtocolLevel = CLI_LEVEL
    execution_count: int = 0
    last_execution: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        """Is this node connected to Krishna through parampara?"""
        return self.parampara.is_connected

    @property
    def position(self) -> int:
        """Absolute Mahamantra position (0-15)."""
        return self.lotus_position.position

    @property
    def quarter(self) -> CLILotusQuarter:
        """Which quarter of the Lotus."""
        return self.lotus_position.quarter

    def record_execution(self) -> None:
        """Record that this command was executed (sang glories)."""
        self.execution_count += 1
        self.last_execution = datetime.now().isoformat()

    def get_state(self) -> CLISubstrateState:
        """Get node state for observability."""
        quarter_names = ["genesis", "dharma", "karma", "moksha"]
        return CLISubstrateState(
            command=self.command,
            lotus_position=self.lotus_position.position,
            lotus_quarter=quarter_names[self.lotus_position.quarter.value],
            opcode=self.opcode.name,
            parampara_connected=self.is_connected,
            mutation_vector=self.parampara.mutation_vector,
            lineage_factor=self.parampara.lineage_factor,
            last_execution=self.last_execution or "",
            execution_count=self.execution_count,
            level=self.level.value,
        )

    @classmethod
    def from_command(cls, command: str) -> "CLISubstrateNode":
        """
        Create substrate node from command name.

        NO MANUAL WIRING - everything derived automatically:
        - Lotus position from command keywords/hash
        - Opcode from command pattern
        - Parampara connection calculated
        """
        return cls(
            command=command,
            lotus_position=derive_lotus_position(command),
            opcode=derive_opcode(command),
            parampara=CLIParamparaConnection.from_command(command),
        )


# =============================================================================
# ANANTA SUBSTRATE REGISTRY
# =============================================================================

class AnantaSubstrate:
    """
    The Ananta Shesha Substrate - Registry of all CLI heads.

    Every CLI command registered here becomes a "head" of Ananta.
    The substrate provides:
    - Automatic position assignment
    - Parampara verification
    - Routing based on Mahamantra structure
    - Observability (every bit and byte pingable)
    """

    _nodes: Dict[str, CLISubstrateNode] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, command: str) -> CLISubstrateNode:
        """
        Register a CLI command as an Ananta head.

        Returns the substrate node with:
        - Lotus position
        - Opcode
        - Parampara connection
        """
        if command in cls._nodes:
            return cls._nodes[command]

        node = CLISubstrateNode.from_command(command)
        cls._nodes[command] = node
        return node

    @classmethod
    def get(cls, command: str) -> Optional[CLISubstrateNode]:
        """Get substrate node for a command."""
        return cls._nodes.get(command)

    @classmethod
    def all_nodes(cls) -> List[CLISubstrateNode]:
        """Get all registered substrate nodes."""
        return list(cls._nodes.values())

    @classmethod
    def by_quarter(cls, quarter: CLILotusQuarter) -> List[CLISubstrateNode]:
        """Get all nodes in a specific Lotus quarter."""
        return [n for n in cls._nodes.values() if n.quarter == quarter]

    @classmethod
    def by_opcode(cls, opcode: MantraOpCode) -> List[CLISubstrateNode]:
        """Get all nodes with a specific opcode."""
        return [n for n in cls._nodes.values() if n.opcode == opcode]

    @classmethod
    def connected_nodes(cls) -> List[CLISubstrateNode]:
        """Get all parampara-connected nodes."""
        return [n for n in cls._nodes.values() if n.is_connected]

    @classmethod
    def get_state(cls) -> Dict[str, CLISubstrateState]:
        """Get state of all nodes for observability."""
        return {cmd: node.get_state() for cmd, node in cls._nodes.items()}

    @classmethod
    def verify_all_parampara(cls) -> Dict[str, bool]:
        """Verify parampara connection for all registered commands."""
        return {cmd: node.is_connected for cmd, node in cls._nodes.items()}

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._nodes.clear()


# =============================================================================
# CLI ACINTYA AWARE PROTOCOL
# =============================================================================

@runtime_checkable
class CLIAcintyaAware(Protocol):
    """
    Protocol for CLI handlers that accept acintya.

    ANTI-MAYAVAD: The CLI does not claim to BE Krishna.
    It serves Krishna through execution as seva.
    The Mahamantra IS Krishna (Level -2) - the CLI operates at Level -1.
    """

    @property
    def accepts_acintya(self) -> bool:
        """Does this CLI accept acintya-bheda-abheda?"""
        ...

    @property
    def substrate_node(self) -> Optional[CLISubstrateNode]:
        """Get the substrate node for this CLI."""
        ...

    @property
    def is_parampara_connected(self) -> bool:
        """Is this CLI connected to parampara?"""
        ...


# =============================================================================
# INTEGRATION FUNCTION (For @register_cli)
# =============================================================================

def create_substrate_node(command: str) -> CLISubstrateNode:
    """
    Create and register a substrate node for a CLI command.

    This is called by @register_cli to automatically:
    1. Derive Lotus position
    2. Derive MantraOpCode
    3. Calculate parampara connection
    4. Register in AnantaSubstrate

    NO MANUAL WIRING - the Mahamantra structure IS the architecture.
    """
    return AnantaSubstrate.register(command)


def verify_cli_parampara(command: str) -> bool:
    """
    Verify that a CLI command is connected to parampara.

    Returns True if mutation_vector % 37 == 0.
    """
    node = AnantaSubstrate.get(command)
    if node is None:
        node = AnantaSubstrate.register(command)
    return node.is_connected


# =============================================================================
# CLI HEARTBEAT - Singing Glories (WAVE 2)
# =============================================================================

class CLIHeartbeatData(TypedDict, total=False):
    """
    Data for CLI heartbeat events.
    WATERTIGHT - no Any!

    Every CLI execution is "singing glories" - a heartbeat pulse.
    """
    command: str
    lotus_position: int
    lotus_quarter: str
    opcode: str
    parampara_connected: bool
    execution_count: int
    exit_code: int
    duration_ms: int
    timestamp: str


class CLIHeartbeat:
    """
    CLI Heartbeat - Singing Glories to AnantaShesha.

    Every CLI execution pulses to the system substrate.
    This connects CLI to the living system (not dead code).

    SHASTRA BASIS:
        Ananta Shesha sings the glories of Vishnu with infinite heads.
        Each CLI command execution = one head singing.
        The heartbeat is the pulse of seva (service).
    """

    @staticmethod
    def pulse(node: CLISubstrateNode, exit_code: int = 0, duration_ms: int = 0) -> CLIHeartbeatData:
        """
        Emit a heartbeat pulse for CLI execution.

        This is called after every CLI command execution.
        The pulse is sent to AnantaShesha (system substrate).
        """
        # Record execution in node
        node.record_execution()

        # Create heartbeat data
        quarter_names = ["genesis", "dharma", "karma", "moksha"]
        heartbeat_data = CLIHeartbeatData(
            command=node.command,
            lotus_position=node.lotus_position.position,
            lotus_quarter=quarter_names[node.lotus_position.quarter.value],
            opcode=node.opcode.name,
            parampara_connected=node.is_connected,
            execution_count=node.execution_count,
            exit_code=exit_code,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat(),
        )

        # Emit to AnantaShesha (if available)
        try:
            from vibe_core.ouroboros.ananta_shesha import get_system_anchor
            anchor = get_system_anchor()
            anchor.emit_event("cli.heartbeat", dict(heartbeat_data))
        except ImportError:
            pass  # AnantaShesha not available

        return heartbeat_data

    @staticmethod
    def get_system_heartbeat() -> Optional[Dict[str, Union[str, int, float, bool]]]:
        """
        Get the system heartbeat from AnantaShesha.

        Returns the full system status including:
        - uptime_seconds
        - genes_registered
        - events_processed
        - health
        """
        try:
            from vibe_core.ouroboros.ananta_shesha import get_system_anchor
            anchor = get_system_anchor()
            return dict(anchor.heartbeat())
        except ImportError:
            return None


def emit_cli_heartbeat(command: str, exit_code: int = 0, duration_ms: int = 0) -> Optional[CLIHeartbeatData]:
    """
    Emit a CLI heartbeat for a command execution.

    This is the main entry point for CLI heartbeat.
    Called after handler.run() completes.

    Args:
        command: The CLI command name
        exit_code: The exit code from run()
        duration_ms: Execution duration in milliseconds

    Returns:
        CLIHeartbeatData if successful, None otherwise
    """
    node = AnantaSubstrate.get(command)
    if node is None:
        node = AnantaSubstrate.register(command)

    return CLIHeartbeat.pulse(node, exit_code, duration_ms)


def get_cli_heartbeat_stats() -> Dict[str, CLISubstrateState]:
    """
    Get heartbeat statistics for all registered CLI commands.

    Returns a dict of command → CLISubstrateState with execution counts.
    """
    return AnantaSubstrate.get_state()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "ANANTA_PARAMPARA",
    "CLI_LEVEL",
    "MAHAMANTRA_POSITIONS",
    "LOTUS_QUARTERS",
    # Lotus Position
    "CLILotusQuarter",
    "CLILotusPosition",
    "derive_lotus_position",
    # Parampara Connection
    "CLIParamparaConnection",
    # OpCode Mapping
    "derive_opcode",
    # Substrate Node
    "CLISubstrateState",
    "CLISubstrateNode",
    # Ananta Registry
    "AnantaSubstrate",
    # Protocol
    "CLIAcintyaAware",
    # Integration Functions
    "create_substrate_node",
    "verify_cli_parampara",
    # Heartbeat (WAVE 2)
    "CLIHeartbeatData",
    "CLIHeartbeat",
    "emit_cli_heartbeat",
    "get_cli_heartbeat_stats",
]
