"""
NAGA CLI COMMAND PROTOCOL - The Fractal Command Interface
=========================================================

"If no Protocol, it doesn't exist."

Every CLI command is a Protocol. Each command maps to:
- MantraOpCode (which operation)
- Mahajana (who owns it)
- Phase (WAKE/PURIFY/SERVE/SUSTAIN)

MAHAJANA MAPPING (12 Workers + 4 Avataras = 16):
    WAKE Phase (0-3):
        0. PRITHU (Avatara) - SYS_WAKE
        1. BRAHMA - LOAD_ROOT (Identity)
        2. NARADA - ALLOC_MEM (Resources)
        3. SHAMBHU - BIND_CTX (Context)

    PURIFY Phase (4-7):
        4. VYASA (Avatara) - ASSERT_TRUTH
        5. KUMARAS - RESOLVE_REQ (Intent)
        6. KAPILA - GARBAGE_COLLECT (Analysis)
        7. MANU - PULSE_SYNC (Law/Heartbeat)

    SERVE Phase (8-11):
        8. PARASHURAMA (Avatara) - FETCH_RES
        9. PRAHLADA - EXEC_SERVICE (Execution)
        10. JANAKA - CHECK_DHARMA (Validation)
        11. BHISHMA - COMMIT_LOG (Ledger)

    SUSTAIN Phase (12-15):
        12. NRISIMHA (Avatara) - CACHE_STATE
        13. BALI - OPTIMIZE (Surrender/Optimization)
        14. SHUKA - YIELD_CPU (Vision/Yield)
        15. YAMARAJA - RESET_IP (Judgment/Reset)

STRICT TYPING (NO ANY):
Per PROMPT.md IV.1 - All types explicit, no Any allowed.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# MAHAJANA REGISTRY
# =============================================================================

class Mahajana(str, Enum):
    """The 12 Mahajanas + 4 Avataras who own the 16 opcodes."""
    # WAKE Phase (0-3)
    PRITHU = "prithu"          # Avatara - SYS_WAKE
    BRAHMA = "brahma"          # LOAD_ROOT
    NARADA = "narada"          # ALLOC_MEM
    SHAMBHU = "shambhu"        # BIND_CTX

    # PURIFY Phase (4-7)
    VYASA = "vyasa"            # Avatara - ASSERT_TRUTH
    KUMARAS = "kumaras"        # RESOLVE_REQ
    KAPILA = "kapila"          # GARBAGE_COLLECT
    MANU = "manu"              # PULSE_SYNC

    # SERVE Phase (8-11)
    PARASHURAMA = "parashurama"  # Avatara - FETCH_RES
    PRAHLADA = "prahlada"        # EXEC_SERVICE
    JANAKA = "janaka"            # CHECK_DHARMA
    BHISHMA = "bhishma"          # COMMIT_LOG

    # SUSTAIN Phase (12-15)
    NRISIMHA = "nrisimha"      # Avatara - CACHE_STATE
    BALI = "bali"              # OPTIMIZE
    SHUKA = "shuka"            # YIELD_CPU
    YAMARAJA = "yamaraja"      # RESET_IP


class Phase(str, Enum):
    """The 4 Phases of the Mahamantra CPU."""
    WAKE = "wake"       # System initialization (0-3)
    PURIFY = "purify"   # Validation and cleanup (4-7)
    SERVE = "serve"     # Execution (8-11)
    SUSTAIN = "sustain" # Maintenance (12-15)


# =============================================================================
# OPCODE → MAHAJANA MAPPING
# =============================================================================

OPCODE_TO_MAHAJANA: Dict[MantraOpCode, Mahajana] = {
    MantraOpCode.SYS_WAKE: Mahajana.PRITHU,
    MantraOpCode.LOAD_ROOT: Mahajana.BRAHMA,
    MantraOpCode.ALLOC_MEM: Mahajana.NARADA,
    MantraOpCode.BIND_CTX: Mahajana.SHAMBHU,
    MantraOpCode.ASSERT_TRUTH: Mahajana.VYASA,
    MantraOpCode.RESOLVE_REQ: Mahajana.KUMARAS,
    MantraOpCode.GARBAGE_COLLECT: Mahajana.KAPILA,
    MantraOpCode.PULSE_SYNC: Mahajana.MANU,
    MantraOpCode.FETCH_RES: Mahajana.PARASHURAMA,
    MantraOpCode.EXEC_SERVICE: Mahajana.PRAHLADA,
    MantraOpCode.CHECK_DHARMA: Mahajana.JANAKA,
    MantraOpCode.COMMIT_LOG: Mahajana.BHISHMA,
    MantraOpCode.CACHE_STATE: Mahajana.NRISIMHA,
    MantraOpCode.OPTIMIZE: Mahajana.BALI,
    MantraOpCode.YIELD_CPU: Mahajana.SHUKA,
    MantraOpCode.RESET_IP: Mahajana.YAMARAJA,
}

MAHAJANA_TO_OPCODE: Dict[Mahajana, MantraOpCode] = {v: k for k, v in OPCODE_TO_MAHAJANA.items()}

OPCODE_TO_PHASE: Dict[MantraOpCode, Phase] = {
    MantraOpCode.SYS_WAKE: Phase.WAKE,
    MantraOpCode.LOAD_ROOT: Phase.WAKE,
    MantraOpCode.ALLOC_MEM: Phase.WAKE,
    MantraOpCode.BIND_CTX: Phase.WAKE,
    MantraOpCode.ASSERT_TRUTH: Phase.PURIFY,
    MantraOpCode.RESOLVE_REQ: Phase.PURIFY,
    MantraOpCode.GARBAGE_COLLECT: Phase.PURIFY,
    MantraOpCode.PULSE_SYNC: Phase.PURIFY,
    MantraOpCode.FETCH_RES: Phase.SERVE,
    MantraOpCode.EXEC_SERVICE: Phase.SERVE,
    MantraOpCode.CHECK_DHARMA: Phase.SERVE,
    MantraOpCode.COMMIT_LOG: Phase.SERVE,
    MantraOpCode.CACHE_STATE: Phase.SUSTAIN,
    MantraOpCode.OPTIMIZE: Phase.SUSTAIN,
    MantraOpCode.YIELD_CPU: Phase.SUSTAIN,
    MantraOpCode.RESET_IP: Phase.SUSTAIN,
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
    mahajana: Mahajana = Mahajana.PRITHU
    # Structured data as tuple of key-value pairs (no Dict[str, Any])
    data: Tuple[Tuple[str, str], ...] = ()

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
    - mahajana: Which Mahajana owns it
    - name: Command name for CLI
    - help: GAD-000 compliant help text

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
        """The Mahajana who owns this command."""
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
        """Which phase this command belongs to."""
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

    Provides default implementations.
    Subclasses must set opcode, mahajana, name, help_text.
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
        return self._mahajana

    @property
    def name(self) -> str:
        return self._name

    @property
    def help_text(self) -> str:
        return self._help_text

    @property
    def phase(self) -> Phase:
        return OPCODE_TO_PHASE[self._opcode]

    def execute(self, args: List[str]) -> NagaCommandResult:
        """Default: return error. Override in subclass."""
        return NagaCommandResult(
            success=False,
            exit_code=1,
            error=f"Command '{self._name}' not implemented",
            opcode=self._opcode,
            mahajana=self._mahajana,
        )

    def success(self, output: str, data: Tuple[Tuple[str, str], ...] = ()) -> NagaCommandResult:
        """Helper to create success result."""
        return NagaCommandResult(
            success=True,
            exit_code=0,
            output=output,
            opcode=self._opcode,
            mahajana=self._mahajana,
            data=data,
        )

    def failure(self, error: str, exit_code: int = 1) -> NagaCommandResult:
        """Helper to create failure result."""
        return NagaCommandResult(
            success=False,
            exit_code=exit_code,
            error=error,
            opcode=self._opcode,
            mahajana=self._mahajana,
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
        self._by_mahajana: Dict[Mahajana, List[INagaCommand]] = {}
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

        # Index by mahajana
        if command.mahajana not in self._by_mahajana:
            self._by_mahajana[command.mahajana] = []
        self._by_mahajana[command.mahajana].append(command)

        # Index by phase
        if command.phase not in self._by_phase:
            self._by_phase[command.phase] = []
        self._by_phase[command.phase].append(command)

    def get(self, name: str) -> Optional[INagaCommand]:
        """Get command by name."""
        return self._commands.get(name)

    def get_by_opcode(self, opcode: MantraOpCode) -> List[INagaCommand]:
        """Get all commands for an opcode."""
        return self._by_opcode.get(opcode, [])

    def get_by_mahajana(self, mahajana: Mahajana) -> List[INagaCommand]:
        """Get all commands owned by a Mahajana."""
        return self._by_mahajana.get(mahajana, [])

    def get_by_phase(self, phase: Phase) -> List[INagaCommand]:
        """Get all commands in a phase."""
        return self._by_phase.get(phase, [])

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
    mahajana: Mahajana,
    name: str,
    help_text: str,
):
    """
    Decorator to register a NAGA command.

    Usage:
        @naga_command(
            opcode=MantraOpCode.EXEC_SERVICE,
            mahajana=Mahajana.PRAHLADA,
            name="chat",
            help_text="Chat with the cognitive layer"
        )
        class ChatCommand(NagaCommandBase):
            def execute(self, args: List[str]) -> NagaCommandResult:
                return self.success("Hello!")
    """
    def decorator(cls):
        cls._opcode = opcode
        cls._mahajana = mahajana
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
    # Enums
    "Mahajana",
    "Phase",
    # Mappings
    "OPCODE_TO_MAHAJANA",
    "MAHAJANA_TO_OPCODE",
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
