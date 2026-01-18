"""
NAGA CLI COMMAND PROTOCOL - The Fractal Command Interface
=========================================================

"If no Protocol, it doesn't exist."

Every CLI command is a Protocol. Each command maps to:
- MantraOpCode (which operation)
- Owner (derived from opcode via vyuha.py)
- Phase (WAKE/PURIFY/SERVE/SUSTAIN)

WIRING TO EXISTING INFRASTRUCTURE:
==================================
This module USES the REAL infrastructure:
- protocols/avataras/__init__.py (Avatara enum - 4 HEADs)
- protocols/mahajanas/router.py (Mahajana enum - 12 Workers)
- protocols/mahajanas/vyuha.py (get_entity_for_opcode - THE ROUTING!)

The Mahamantra ITSELF determines routing.
No duplicate enums. No manual mappings. "The chant links back."

CHATUR-VYUHA ARCHITECTURE:
==========================
16 = 4 × (1 HEAD + 3 Workers)
- 4 Avataras own HEAD opcodes (positions 0, 4, 8, 12)
- 12 Mahajanas own Worker opcodes (all other positions)
- Owner = Union[Avatara, Mahajana] (derived from opcode!)

STRICT TYPING (NO ANY):
Per PROMPT.md IV.1 - All types explicit, no Any allowed.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xe2a1d086"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Protocol, Tuple, Union, runtime_checkable

# =============================================================================
# IMPORT FROM REAL INFRASTRUCTURE
# =============================================================================
# Avatara from avataras (4 HEADs)
from vibe_core.protocols.avataras import Avatara
from vibe_core.protocols.mahajanas.router import (
    HEAD_OPCODES,
    MahajanaRouter,
    get_router,
)

# Core Mahajana (12 Workers) - for internal use
from vibe_core.protocols.mahajanas.router import (
    Mahajana as CoreMahajana,
)
from vibe_core.protocols.substrate import MantraOpCode

# =============================================================================
# CLI MAHAJANA (16 Positions - Unified for CLI)
# =============================================================================
# For CLI purposes, we treat all 16 positions as "Mahajanas"
# This simplifies command routing while preserving the theological distinction


class Mahajana(str, Enum):
    """
    The 16 Mahajanas (CLI View) - All Protocol Owners.

    For CLI purposes, HEAD positions (Avataras) are also treated as Mahajanas.
    This simplifies command registration and routing.

    Theological distinction (Avatara vs Mahajana) is preserved in:
    - vibe_core.protocols.avataras (4 HEADs)
    - vibe_core.protocols.mahajanas.router (12 Workers)
    """

    # === ALIGNED WITH seed.py ALL_GUARDIANS (SSOT) ===
    # Quarter 1: WAKE (Genesis)
    VYASA = "vyasa"  # 00 - HEAD (Avatara) - SYS_WAKE
    BRAHMA = "brahma"  # 01 - Worker - LOAD_ROOT
    NARADA = "narada"  # 02 - Worker - ALLOC_MEM
    SHAMBHU = "shambhu"  # 03 - Worker - INIT_THREAD
    # Quarter 2: PURIFY (Dharma)
    PRITHU = "prithu"  # 04 - HEAD (Avatara) - COMPILE_AST
    KUMARAS = "kumaras"  # 05 - Worker - BIND_SYMBOL
    KAPILA = "kapila"  # 06 - Worker - TYPE_CHECK
    MANU = "manu"  # 07 - Worker - DHARMA_TEST
    # Quarter 3: SERVE (Karma)
    PARASHURAMA = "parashurama"  # 08 - HEAD (Avatara) - FETCH_RES
    PRAHLADA = "prahlada"  # 09 - Worker - EXEC_SERVICE
    JANAKA = "janaka"  # 10 - Worker - CHECK_DHARMA
    BHISHMA = "bhishma"  # 11 - Worker - COMMIT_LOG
    # Quarter 4: SUSTAIN (Moksha)
    NRISIMHA = "nrisimha"  # 12 - HEAD (Avatara) - CACHE_STATE
    BALI = "bali"  # 13 - Worker - OPTIMIZE
    SHUKA = "shuka"  # 14 - Worker - YIELD_CPU
    YAMARAJA = "yamaraja"  # 15 - Worker - RESET_IP


# Vyuha routing - THE SOURCE OF TRUTH
from vibe_core.protocols.mahajanas.vyuha import (
    CyclePhase,
    get_cycle_for_opcode,
    get_entity_for_opcode,
)

# =============================================================================
# OWNER TYPE (Union of Avatara and Mahajana)
# =============================================================================
# NOT a new enum! Just a type alias for Union[Avatara, Mahajana]

Owner = Union[Avatara, Mahajana]


# =============================================================================
# PHASE ENUM (Maps to CyclePhase for CLI layer)
# =============================================================================


class Phase(str, Enum):
    """The 4 Phases of the Mahamantra CPU."""

    WAKE = "wake"  # Q1: Genesis (SYS_WAKE + 3 workers)
    PURIFY = "purify"  # Q2: Dharma (ASSERT_TRUTH + 3 workers)
    SERVE = "serve"  # Q3: Karma (FETCH_RES + 3 workers)
    SUSTAIN = "sustain"  # Q4: Moksha (CACHE_STATE + 3 workers)


# CyclePhase → Phase mapping
_CYCLE_TO_PHASE: Dict[CyclePhase, Phase] = {
    CyclePhase.GENESIS: Phase.WAKE,
    CyclePhase.DHARMA: Phase.PURIFY,
    CyclePhase.KARMA: Phase.SERVE,
    CyclePhase.MOKSHA: Phase.SUSTAIN,
}


def get_phase_for_opcode(opcode: MantraOpCode) -> Phase:
    """Get CLI Phase for an opcode (derived from vyuha)."""
    cycle = get_cycle_for_opcode(opcode)
    return _CYCLE_TO_PHASE[cycle.phase]


# =============================================================================
# ROUTING (Derived from vyuha.py - "The Mahamantra links back")
# =============================================================================


def route_opcode(opcode: MantraOpCode) -> Owner:
    """
    Route an OpCode to its Owner (Avatara or Mahajana).

    USES vyuha.get_entity_for_opcode - the SINGLE SOURCE OF TRUTH.
    No manual mapping. The Mahamantra determines everything.
    """
    return get_entity_for_opcode(opcode)


# Convenience tables (generated from vyuha)
OPCODE_TO_OWNER: Dict[MantraOpCode, Owner] = {opcode: route_opcode(opcode) for opcode in MantraOpCode}

OPCODE_TO_PHASE: Dict[MantraOpCode, Phase] = {opcode: get_phase_for_opcode(opcode) for opcode in MantraOpCode}

# =============================================================================
# CLI MAHAJANA MAPPINGS (16-fold)
# =============================================================================
# Maps each opcode to its CLI Mahajana (unified 16-member enum)

OPCODE_TO_MAHAJANA: Dict[MantraOpCode, Mahajana] = {
    MantraOpCode.SYS_WAKE: Mahajana.PRITHU,
    MantraOpCode.LOAD_ROOT: Mahajana.BRAHMA,
    MantraOpCode.ALLOC_MEM: Mahajana.NARADA,
    MantraOpCode.INIT_THREAD: Mahajana.SHAMBHU,
    MantraOpCode.COMPILE_AST: Mahajana.VYASA,
    MantraOpCode.BIND_SYMBOL: Mahajana.KUMARAS,
    MantraOpCode.TYPE_CHECK: Mahajana.KAPILA,
    MantraOpCode.DHARMA_TEST: Mahajana.MANU,
    MantraOpCode.EXEC_OP: Mahajana.PARASHURAMA,
    MantraOpCode.EXTEND_CAP: Mahajana.PRAHLADA,
    MantraOpCode.STATE_SYNC: Mahajana.JANAKA,
    MantraOpCode.LEDGER_SIGN: Mahajana.BHISHMA,
    MantraOpCode.YIELD_CPU: Mahajana.NRISIMHA,
    MantraOpCode.IO_FLUSH: Mahajana.BALI,
    MantraOpCode.YIELD_CPU: Mahajana.SHUKA,
    MantraOpCode.AUDIT_SEAL: Mahajana.YAMARAJA,
}

# Reverse mapping
MAHAJANA_TO_OPCODE: Dict[Mahajana, MantraOpCode] = {mahajana: opcode for opcode, mahajana in OPCODE_TO_MAHAJANA.items()}


def get_mahajana_for_opcode(opcode: MantraOpCode) -> Mahajana:
    """Get CLI Mahajana for an opcode."""
    return OPCODE_TO_MAHAJANA[opcode]


# =============================================================================
# COMMAND RESULT (STRICT TYPING)
# =============================================================================


@dataclass(frozen=True)
class NagaCommandResult:
    """
    Immutable result from command execution.

    GAD-000 Compliant:
    - Machine-parseable
    - No Any types
    - Frozen (immutable)
    """

    success: bool
    exit_code: int
    output: str = ""
    error: str = ""
    opcode: MantraOpCode = MantraOpCode.SYS_WAKE
    mahajana: Mahajana = Mahajana.PRITHU
    # Structured data as tuple of key-value pairs (no Dict[str, Any])
    data: Tuple[Tuple[str, str], ...] = ()

    @property
    def owner(self) -> Owner:
        """Owner derived from opcode."""
        return route_opcode(self.opcode)

    @property
    def phase(self) -> Phase:
        """Phase derived from opcode."""
        return get_phase_for_opcode(self.opcode)

    def to_dict(self) -> Dict[str, str]:
        """Convert data to dictionary."""
        return dict(self.data)


# =============================================================================
# NAGA COMMAND PROTOCOL
# =============================================================================


@runtime_checkable
class INagaCommand(Protocol):
    """
    Protocol for NAGA CLI commands.

    Every command declares:
    - opcode: Which MantraOpCode it executes
    - name: Command name for CLI
    - help: GAD-000 compliant help text

    Owner and Phase are DERIVED from opcode via vyuha.py.
    "The Mahamantra links back."

    GAD-000 Compliant:
    - Discoverable: via registry
    - Observable: via execute() result
    - Parseable: NagaCommandResult is machine-readable
    - Composable: Commands can chain
    - Idempotent: Same args = same result (where applicable)
    - Recoverable: Returns error in result, not exception
    """

    @property
    def opcode(self) -> MantraOpCode:
        """The MantraOpCode this command executes."""
        ...

    @property
    def mahajana(self) -> Mahajana:
        """CLI Mahajana for this command."""
        ...

    @property
    def owner(self) -> Owner:
        """Owner derived from opcode (Avatara for HEAD, Mahajana for Worker)."""
        ...

    @property
    def name(self) -> str:
        """Command name (e.g., 'chat', 'scan', 'status')."""
        ...

    @property
    def help_text(self) -> str:
        """GAD-000 compliant help text."""
        ...

    @property
    def phase(self) -> Phase:
        """Phase derived from opcode."""
        ...

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute the command.

        Args:
            args: Command-line arguments

        Returns:
            NagaCommandResult with success/failure and output
        """
        ...


# =============================================================================
# BASE IMPLEMENTATION
# =============================================================================


class NagaCommandBase:
    """
    Base class for NAGA commands.

    Only requires opcode, name, help_text.
    Mahajana, Owner, and Phase are DERIVED from opcode automatically.
    "The Mahamantra links back."
    """

    _opcode: MantraOpCode = MantraOpCode.SYS_WAKE
    _mahajana: Mahajana = Mahajana.PRITHU
    _name: str = "unnamed"
    _help_text: str = "No help available."

    @property
    def opcode(self) -> MantraOpCode:
        return self._opcode

    @property
    def mahajana(self) -> Mahajana:
        """Derived from opcode via CLI mapping."""
        return get_mahajana_for_opcode(self._opcode)

    @property
    def owner(self) -> Owner:
        """Derived from opcode via vyuha."""
        return route_opcode(self._opcode)

    @property
    def name(self) -> str:
        return self._name

    @property
    def help_text(self) -> str:
        return self._help_text

    @property
    def phase(self) -> Phase:
        """Derived from opcode via vyuha."""
        return get_phase_for_opcode(self._opcode)

    def execute(self, args: List[str]) -> NagaCommandResult:
        """Default: return error. Override in subclass."""
        return NagaCommandResult(
            success=False,
            exit_code=1,
            error=f"Command '{self._name}' not implemented",
            opcode=self._opcode,
            mahajana=self.mahajana,
        )

    def success(self, output: str, data: Tuple[Tuple[str, str], ...] = ()) -> NagaCommandResult:
        """Helper to create success result."""
        return NagaCommandResult(
            success=True,
            exit_code=0,
            output=output,
            opcode=self._opcode,
            mahajana=self.mahajana,
            data=data,
        )

    def failure(self, error: str, exit_code: int = 1) -> NagaCommandResult:
        """Helper to create failure result."""
        return NagaCommandResult(
            success=False,
            exit_code=exit_code,
            error=error,
            opcode=self._opcode,
            mahajana=self.mahajana,
        )


# =============================================================================
# COMMAND REGISTRY (BALARAMA PATTERN)
# =============================================================================


class NagaCommandRegistry:
    """
    Registry for NAGA commands.

    Implements Balarama pattern: auto-discovery and injection.
    Commands register themselves, registry discovers at runtime.
    """

    def __init__(self) -> None:
        self._commands: Dict[str, INagaCommand] = {}
        self._by_opcode: Dict[MantraOpCode, List[INagaCommand]] = {}
        self._by_phase: Dict[Phase, List[INagaCommand]] = {}

    def register(self, command: INagaCommand) -> None:
        """
        Register a command.

        Balarama injects the command into the registry.
        """
        self._commands[command.name] = command

        # Index by opcode
        if command.opcode not in self._by_opcode:
            self._by_opcode[command.opcode] = []
        self._by_opcode[command.opcode].append(command)

        # Index by phase (derived from opcode)
        phase = command.phase
        if phase not in self._by_phase:
            self._by_phase[phase] = []
        self._by_phase[phase].append(command)

    def get(self, name: str) -> Optional[INagaCommand]:
        """Get command by name."""
        return self._commands.get(name)

    def get_by_opcode(self, opcode: MantraOpCode) -> List[INagaCommand]:
        """Get all commands for an opcode."""
        return self._by_opcode.get(opcode, [])

    def get_by_phase(self, phase: Phase) -> List[INagaCommand]:
        """Get all commands in a phase."""
        return self._by_phase.get(phase, [])

    def get_by_owner(self, owner: Owner) -> List[INagaCommand]:
        """Get all commands owned by an Owner (Avatara or Mahajana)."""
        result = []
        for cmd in self._commands.values():
            if cmd.owner == owner:
                result.append(cmd)
        return result

    def get_by_mahajana(self, mahajana: Mahajana) -> List[INagaCommand]:
        """Get all commands by CLI Mahajana."""
        result = []
        for cmd in self._commands.values():
            if cmd.mahajana == mahajana:
                result.append(cmd)
        return result

    def list_all(self) -> List[INagaCommand]:
        """Get all registered commands."""
        return list(self._commands.values())

    def list_names(self) -> List[str]:
        """Get all command names."""
        return list(self._commands.keys())


# =============================================================================
# GLOBAL REGISTRY
# =============================================================================

# Singleton registry - commands register here
NAGA_COMMAND_REGISTRY = NagaCommandRegistry()


def naga_command(
    opcode: MantraOpCode,
    name: str,
    help_text: str,
):
    """
    Decorator to register a NAGA command.

    SIMPLE: Just specify opcode, name, help_text.
    Owner and Phase are DERIVED from opcode via vyuha.py.
    "The Mahamantra links back."

    Usage:
        @naga_command(
            opcode=MantraOpCode.EXTEND_CAP,
            name="chat",
            help_text="Chat with the cognitive layer"
        )
        class ChatCommand(NagaCommandBase):
            def execute(self, args: List[str]) -> NagaCommandResult:
                return self.success("Hello!")
    """

    def decorator(cls):
        cls._opcode = opcode
        cls._name = name
        cls._help_text = help_text
        # Auto-register
        NAGA_COMMAND_REGISTRY.register(cls())
        return cls

    return decorator


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types (from real infrastructure)
    "Avatara",  # From protocols/avataras (4 HEADs)
    "Mahajana",  # CLI Mahajana (16-member unified enum)
    "Owner",  # Union[Avatara, CoreMahajana]
    "Phase",  # 4 CLI Phases
    # Router bridge
    "MahajanaRouter",
    "get_router",
    "HEAD_OPCODES",
    # Routing (via vyuha)
    "route_opcode",
    "get_phase_for_opcode",
    "get_mahajana_for_opcode",
    "OPCODE_TO_OWNER",
    "OPCODE_TO_PHASE",
    "OPCODE_TO_MAHAJANA",
    "MAHAJANA_TO_OPCODE",
    # Result
    "NagaCommandResult",
    # Protocol
    "INagaCommand",
    # Base
    "NagaCommandBase",
    # Registry
    "NagaCommandRegistry",
    "NAGA_COMMAND_REGISTRY",
    # Decorator
    "naga_command",
]
