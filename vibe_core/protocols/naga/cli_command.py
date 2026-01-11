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

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Protocol, Tuple, Union, runtime_checkable

from vibe_core.protocols.substrate import MantraOpCode

# =============================================================================
# IMPORT FROM REAL INFRASTRUCTURE - NO DUPLICATES!
# =============================================================================
# Avatara from avataras (4 HEADs)
from vibe_core.protocols.avataras import Avatara

# Mahajana from router (12 Workers)
from vibe_core.protocols.mahajanas.router import (
    Mahajana,
    MahajanaRouter,
    get_router,
    HEAD_OPCODES,
)

# Vyuha routing - THE SOURCE OF TRUTH
from vibe_core.protocols.mahajanas.vyuha import (
    get_entity_for_opcode,
    get_cycle_for_opcode,
    CyclePhase,
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
    WAKE = "wake"       # Q1: Genesis (SYS_WAKE + 3 workers)
    PURIFY = "purify"   # Q2: Dharma (ASSERT_TRUTH + 3 workers)
    SERVE = "serve"     # Q3: Karma (FETCH_RES + 3 workers)
    SUSTAIN = "sustain" # Q4: Moksha (CACHE_STATE + 3 workers)


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
OPCODE_TO_OWNER: Dict[MantraOpCode, Owner] = {
    opcode: route_opcode(opcode) for opcode in MantraOpCode
}

OPCODE_TO_PHASE: Dict[MantraOpCode, Phase] = {
    opcode: get_phase_for_opcode(opcode) for opcode in MantraOpCode
}


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
    Owner and Phase are DERIVED from opcode automatically.
    "The Mahamantra links back."
    """

    _opcode: MantraOpCode = MantraOpCode.SYS_WAKE
    _name: str = "unnamed"
    _help_text: str = "No help available."

    @property
    def opcode(self) -> MantraOpCode:
        return self._opcode

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
        )

    def success(self, output: str, data: Tuple[Tuple[str, str], ...] = ()) -> NagaCommandResult:
        """Helper to create success result."""
        return NagaCommandResult(
            success=True,
            exit_code=0,
            output=output,
            opcode=self._opcode,
            data=data,
        )

    def failure(self, error: str, exit_code: int = 1) -> NagaCommandResult:
        """Helper to create failure result."""
        return NagaCommandResult(
            success=False,
            exit_code=exit_code,
            error=error,
            opcode=self._opcode,
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
            opcode=MantraOpCode.EXEC_SERVICE,
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
    "Avatara",       # From protocols/avataras (4 HEADs)
    "Mahajana",      # From protocols/mahajanas/router (12 Workers)
    "Owner",         # Union[Avatara, Mahajana]
    "Phase",         # 4 CLI Phases
    # Router bridge
    "MahajanaRouter",
    "get_router",
    "HEAD_OPCODES",
    # Routing (via vyuha)
    "route_opcode",
    "get_phase_for_opcode",
    "OPCODE_TO_OWNER",
    "OPCODE_TO_PHASE",
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
