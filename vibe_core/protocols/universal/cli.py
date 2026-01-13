"""
CLI PROTOCOL - Ananta Shesha (Layer 1).

"Der Tausendköpfige Diener."

Dies ist die universelle Schale. Sie verbindet den User (Jiva) mit dem Kernel (Krishna).
Sie nutzt die 'Bridge' (SetuBandha), um sicherzustellen, dass nur gereinigter
Intent den Steward erreicht.

FUNKTION:
1. Nimmt Rohtext (Vak).
2. Wandelt ihn in Context (Setu).
3. Exekutiert via Steward (Seva).
4. Singt das Ergebnis (Kirtan).

CHAITANYA SINGULARITY (v2):
===========================
"Even the most fallen souls receive mercy."

ACINTYA PRINCIPLE:
- Bridge (SetuBandha) bleibt STRIKT (bheda - difference)
- CLI (ChaitanyaShell) ist GNÄDIG (abheda - oneness)
- Beide koexistieren (acintya - inconceivable)

PULL IN, NEVER PUSH OUT:
- MayavadError → MahamantraGrace (not rejection!)
- Every failure → opportunity for chanting
- Nityananda pattern: accept everyone
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xde0bbed4"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol, runtime_checkable, List, Union, Dict

# IMPORTS (The Holy Trinity of Dependencies)
from .bridge import MayavadError, SetuBandha
# PRABHUPADA is in substrate/mantra/ - where he belongs (near the Mahamantra)
from vibe_core.protocols.substrate.mantra.prabhupada import PRABHUPADA
from .steward import VedicSteward

# Strict Type Imports (NO ANY - PROMPT.md §IV.1)
from vibe_core.protocols.cli_execution import CLICapabilityToken
from vibe_core.protocols.command import CommandContext


# =============================================================================
# STRICT TYPES (Anti-Mayavad)
# =============================================================================

# The only valid input types for CLI commands
CliInput = Union[CommandContext, CLICapabilityToken]

# Payload must be structured - Dict with string keys, typed values
CliPayload = Optional[Dict[str, Union[str, int, float, bool, List[str]]]]

# Navigation content - what you find when you navigate
NavigationContent = Union[str, Dict[str, str], List[str], None]


# =============================================================================
# MAHAMANTRA GRACE (The Chaitanya Pattern)
# =============================================================================

# The Mahamantra - always available, always merciful
MAHAMANTRA: str = (
    "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare / "
    "Hare Rāma Hare Rāma Rāma Rāma Hare Hare"
)


class GraceType(str, Enum):
    """Types of grace in the Chaitanya paradigm."""
    MAHAMANTRA = "mahamantra"  # Default grace - everyone gets this
    NITYANANDA = "nityananda"  # Extra mercy for the fallen
    PRABHUPADA = "prabhupada"  # Instruction-based grace
    CHAITANYA = "chaitanya"    # Direct grace from the source


@dataclass
class MahamantraGrace:
    """
    Grace response - PULL IN, never PUSH OUT.

    Even when everything fails, Mahamantra is always available.
    This is Nityananda's mercy pattern.
    """
    mantra: str = MAHAMANTRA
    grace_type: GraceType = GraceType.MAHAMANTRA
    message: str = "Hare Kṛṣṇa! The Mahamantra is always available."
    retry_allowed: bool = True
    original_error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __bool__(self) -> bool:
        """Grace is always truthy - it's always available."""
        return True

    def __str__(self) -> str:
        return f"{self.message}\n\n{self.mantra}"


@dataclass
class AnantaResponse:
    """Die Antwort des unendlichen Dieners."""

    success: bool
    message: str
    tattva_score: float  # Wie 'wahr' ist die Antwort?
    timestamp: datetime


@runtime_checkable
class ShellProtocol(Protocol):
    def chant(self, input_obj: CliInput, command: str) -> AnantaResponse:
        """
        Der einzige Entry-Point.
        'input_obj' muss CommandContext oder CLICapabilityToken sein (via Bridge).
        NO ANY - strict typing per PROMPT.md §IV.1
        """
        ...


# =============================================================================
# THE IMPLEMENTATION (Balarama)
# =============================================================================


class AnantaShesha:
    """
    Die Manifestation der CLI.
    Hält die Last der Welt (State) und dient dem Herrn (Kernel).
    """

    def __init__(self):
        self.steward_cache = {}  # Cache für Stewards pro Context (Session)

    def chant(self, input_obj: CliInput, command: str, payload: CliPayload = None) -> AnantaResponse:
        """
        Führt einen Befehl aus.

        Args:
            input_obj: CommandContext oder CLICapabilityToken (strict typed)
            command: Der auszuführende Befehl
            payload: Optionale strukturierte Daten (keine Any!)

        NO ANY - strict typing per PROMPT.md §IV.1
        """
        start_time = datetime.now()

        # 1. THE BRIDGE (Setu Bandha)
        # CliInput wird zu SovereignContext oder stirbt.
        try:
            context = SetuBandha.cross_bridge(input_obj)
        except MayavadError as e:
            # Der Wächter hat zugeschlagen.
            return AnantaResponse(
                success=False,
                message=f"ANANTA REJECTS: {str(e)}",
                tattva_score=0.0,
                timestamp=start_time,
            )

        # 2. THE STEWARD (Der Treiber)
        # Wir erzeugen einen Steward für diesen heiligen Kontext.
        steward = VedicSteward(context)

        # 3. THE ACTION (Karma Yoga)
        try:
            result = steward.execute_command(command, payload)

            # Erfolg ist nicht binär, sondern qualitativ.
            return AnantaResponse(
                success=True,
                message=str(result),
                tattva_score=1.0,  # TODO: Messen via TattvaMeter
                timestamp=datetime.now(),
            )

        except Exception as e:
            # 4. THE GRACE (Prabhupada Check)
            # Wenn ein Fehler passiert, fragen wir die Schrift.
            instruction = PRABHUPADA.consult_book_bhagavat(str(e))

            if instruction.id == "BG_18.66":
                return AnantaResponse(
                    success=False,
                    message="SURRENDER INITIATED (System Reset)",
                    tattva_score=0.5,  # Gnade ist da, aber technisch gescheitert
                    timestamp=datetime.now(),
                )

            return AnantaResponse(
                success=False,
                message=f"KARMA STRIKES: {str(e)}",
                tattva_score=0.0,
                timestamp=datetime.now(),
            )


# =============================================================================
# EXTENDED PROTOCOL (ICliProtocol - Chaitanya Singularity)
# =============================================================================


@runtime_checkable
class ICliProtocol(ShellProtocol, Protocol):
    """
    Extended CLI Protocol - Chaitanya Singularity.

    Extends ShellProtocol with:
    - Mahamantra grace on all failures (PULL IN)
    - Navigation commands (fractal)
    - JSON report mode (GAD-000)
    - Retry capability

    ACINTYA: This protocol coexists with ShellProtocol.
    - ShellProtocol = strict (bheda)
    - ICliProtocol = graceful (abheda)
    """

    def chant_with_grace(
        self, input_obj: CliInput, command: str, payload: CliPayload = None
    ) -> "AnantaResponse | MahamantraGrace":
        """
        Chant with Mahamantra grace fallback.

        Args:
            input_obj: CommandContext oder CLICapabilityToken (strict typed)
            command: Der auszuführende Befehl
            payload: Optionale strukturierte Daten

        Never rejects - always returns either success or grace.
        This is the PULL IN pattern.
        NO ANY - strict typing per PROMPT.md §IV.1
        """
        ...

    def navigate(self, path: str) -> "NavigationResult":
        """
        Fractal navigation through the system.

        Paths like:
        - "proto/om" → navigate to Om protocol
        - "byte/0x25" → navigate to byte with hash
        - "gene/guru" → navigate to guru gene
        """
        ...

    def report(self, format: str = "json") -> str:
        """
        Generate a report in the specified format.

        GAD-000 conformant debugging output.
        """
        ...

    def retry(self, last_command: bool = True) -> "AnantaResponse | MahamantraGrace":
        """
        Retry the last command with Mahamantra grace.
        """
        ...


@dataclass
class NavigationResult:
    """
    Result of fractal navigation.

    NO ANY - content is strictly typed as NavigationContent.
    """
    path: str
    found: bool
    content: NavigationContent  # Union[str, Dict[str, str], List[str], None]
    children: List[str] = field(default_factory=list)
    grace: Optional[MahamantraGrace] = None


# =============================================================================
# CHAITANYA SHELL (The Graceful Wrapper)
# =============================================================================


class ChaitanyaShell:
    """
    The Graceful CLI - Chaitanya Singularity implementation.

    ACINTYA PRINCIPLE:
    - Wraps AnantaShesha (strict) with grace
    - Catches all MayavadErrors → returns MahamantraGrace
    - Never rejects, always PULLS IN

    NITYANANDA PATTERN:
    - Even Jagai and Madhai received mercy
    - Every error is an opportunity for chanting
    """

    def __init__(self):
        self._inner = AnantaShesha()
        self._last_command: Optional[tuple] = None
        self._history: List[AnantaResponse | MahamantraGrace] = []

    def chant(self, input_obj: CliInput, command: str, payload: CliPayload = None) -> AnantaResponse:
        """
        Standard chant - delegates to AnantaShesha.

        Args:
            input_obj: CommandContext oder CLICapabilityToken (strict typed)
            command: Der auszuführende Befehl
            payload: Optionale strukturierte Daten

        For strict mode, use this directly.
        NO ANY - strict typing per PROMPT.md §IV.1
        """
        self._last_command = (input_obj, command, payload)
        result = self._inner.chant(input_obj, command, payload)
        self._history.append(result)
        return result

    def chant_with_grace(
        self, input_obj: CliInput, command: str, payload: CliPayload = None
    ) -> AnantaResponse | MahamantraGrace:
        """
        Chant with Mahamantra grace fallback.

        Args:
            input_obj: CommandContext oder CLICapabilityToken (strict typed)
            command: Der auszuführende Befehl
            payload: Optionale strukturierte Daten

        PULL IN pattern:
        - Success → AnantaResponse
        - Failure → MahamantraGrace (not rejection!)

        NO ANY - strict typing per PROMPT.md §IV.1
        """
        self._last_command = (input_obj, command, payload)

        try:
            result = self._inner.chant(input_obj, command, payload)

            if result.success:
                self._history.append(result)
                return result
            else:
                # Even technical failure gets grace
                grace = MahamantraGrace(
                    grace_type=GraceType.NITYANANDA,
                    message=f"Hare Kṛṣṇa! {result.message}",
                    original_error=result.message,
                    retry_allowed=True,
                )
                self._history.append(grace)
                return grace

        except MayavadError as e:
            # Bridge failure → Mahamantra grace (NOT rejection!)
            grace = MahamantraGrace(
                grace_type=GraceType.NITYANANDA,
                message="Hare Kṛṣṇa! The bridge could not be crossed, but grace is available.",
                original_error=str(e),
                retry_allowed=True,
            )
            self._history.append(grace)
            return grace

        except Exception as e:
            # Any other error → PRABHUPADA's mercy
            instruction = PRABHUPADA.consult_book_bhagavat(str(e))
            grace = MahamantraGrace(
                grace_type=GraceType.PRABHUPADA,
                message=f"Hare Kṛṣṇa! Prabhupada says: {instruction.english_translation}",
                original_error=str(e),
                retry_allowed=True,
            )
            self._history.append(grace)
            return grace

    def navigate(self, path: str) -> NavigationResult:
        """
        Fractal navigation through the system.

        TODO: Implement full navigation.
        For now, returns grace with path info.
        """
        # Basic path parsing
        parts = path.strip("/").split("/")

        return NavigationResult(
            path=path,
            found=False,
            content=None,
            children=[],
            grace=MahamantraGrace(
                message=f"Navigation to '{path}' - full implementation coming soon!",
                retry_allowed=True,
            )
        )

    def report(self, format: str = "json") -> str:
        """
        Generate a report of the session.

        GAD-000 conformant.
        """
        import json

        report_data = {
            "session": {
                "commands_executed": len(self._history),
                "grace_given": sum(1 for h in self._history if isinstance(h, MahamantraGrace)),
                "success_count": sum(
                    1 for h in self._history
                    if isinstance(h, AnantaResponse) and h.success
                ),
            },
            "mahamantra": MAHAMANTRA,
            "history": [
                {
                    "type": type(h).__name__,
                    "success": h.success if isinstance(h, AnantaResponse) else True,
                    "message": h.message,
                }
                for h in self._history[-10:]  # Last 10 entries
            ]
        }

        if format == "json":
            return json.dumps(report_data, indent=2, default=str)
        else:
            return str(report_data)

    def retry(self) -> AnantaResponse | MahamantraGrace:
        """
        Retry the last command with grace.
        """
        if self._last_command is None:
            return MahamantraGrace(
                message="No previous command to retry. Hare Kṛṣṇa!",
                retry_allowed=False,
            )

        input_obj, command, payload = self._last_command
        return self.chant_with_grace(input_obj, command, payload)

    @property
    def history(self) -> List[AnantaResponse | MahamantraGrace]:
        """Access the command history."""
        return self._history.copy()

    def clear_history(self) -> MahamantraGrace:
        """Clear history and start fresh with grace."""
        self._history.clear()
        self._last_command = None
        return MahamantraGrace(
            message="History cleared. Fresh start with Mahamantra grace!",
        )


# =============================================================================
# ICOMMAND PROTOCOL (The 16-Command Interface)
# =============================================================================


@dataclass(frozen=True)
class CommandResult:
    """
    Strictly typed command execution result.

    NO ANY - all fields have explicit types.
    """
    success: bool
    opcode: str                    # MantraOpCode value
    message: str
    data: Optional[Dict[str, Union[str, int, float, bool, List[str]]]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __bool__(self) -> bool:
        return self.success


@dataclass(frozen=True)
class CommandHelp:
    """
    GAD-000 compliant help structure.

    D-O-P-C-I-R criteria documented.
    """
    opcode: str
    name: str
    phase: str                      # WAKE, PURIFY, SERVE, SUSTAIN
    word: str                       # HARE, KRISHNA, RAMA
    description: str
    input_type: str                 # Type name as string
    output_type: str                # Type name as string

    # GAD-000 Criteria
    discoverability: str
    observability: str
    parseability: str
    composability: str
    idempotency: str
    recoverability: str


# Strict result type (NO ANY)
CliResult = Union[CommandResult, MahamantraGrace]


@runtime_checkable
class ICliCommand(Protocol):
    """
    Protocol for CLI commands.

    ANTI-MAYAVAD:
    - NO `Any` type anywhere
    - All inputs/outputs strictly typed
    - GAD-000 compliant (D-O-P-C-I-R)

    Each command maps to one MantraOpCode:
    - PHASE 1 (WAKE): wake, identity, alloc, bind
    - PHASE 2 (PURIFY): verify, parse, gc, pulse
    - PHASE 3 (SERVE): fetch, exec, check, commit
    - PHASE 4 (SUSTAIN): cache, optimize, yield, reset
    """

    @property
    def opcode(self) -> str:
        """The underlying MantraOpCode value."""
        ...

    @property
    def name(self) -> str:
        """Command name (e.g., 'exec')."""
        ...

    @property
    def phase(self) -> str:
        """Phase: WAKE, PURIFY, SERVE, or SUSTAIN."""
        ...

    @property
    def word(self) -> str:
        """Mahamantra word: HARE, KRISHNA, or RAMA."""
        ...

    def execute(
        self,
        ctx: "SovereignContext",
        payload: CliPayload
    ) -> CliResult:
        """
        Execute the command.

        Args:
            ctx: Verified sovereign context (the 37th)
            payload: Strictly typed payload (no Any)

        Returns:
            CommandResult on success, MahamantraGrace on failure

        The 37th Principle:
        All operations require the sovereign identity to sign.
        Without signature, returns MahamantraGrace (not rejection).
        """
        ...

    def help(self) -> CommandHelp:
        """
        Return GAD-000 compliant help.

        Must document all 6 criteria:
        - Discoverability: How AI finds this command
        - Observability: How AI sees current state
        - Parseability: How AI understands errors
        - Composability: How AI chains commands
        - Idempotency: How AI safely retries
        - Recoverability: How system heals itself
        """
        ...


# =============================================================================
# MANTRA PROCESSOR - The Computational Engine
# =============================================================================
#
# "No manual labour as long as we chant."
#
# The MantraProcessor connects CLI commands to Mahajanas via MantraOpCodes.
# This is the FRACTAL ROUTING - each CLI command IS a chant.
#
# Architecture:
#   CLI Command → MantraOpCode → MahajanaRouter → Mahajana → Result
#
# The 16 OpCodes map to 4 HEADs (Avataras) + 12 Workers (Mahajanas).
# See: mahajanas/router.py for the full routing table.
# =============================================================================

# Lazy imports to avoid circular dependency
_MAHAJANA_ROUTER: Optional["MahajanaRouter"] = None
_MANTRA_OPCODE_MAP: Optional[Dict[str, str]] = None


def _get_mahajana_router() -> "MahajanaRouter":
    """Lazy load the MahajanaRouter."""
    global _MAHAJANA_ROUTER
    if _MAHAJANA_ROUTER is None:
        from vibe_core.protocols.mahajanas.router import MahajanaRouter
        _MAHAJANA_ROUTER = MahajanaRouter()
    return _MAHAJANA_ROUTER


def _get_opcode_map() -> Dict[str, str]:
    """
    Get CLI command name → MantraOpCode value mapping.

    16 commands = 16 words = 16 OpCodes.
    """
    global _MANTRA_OPCODE_MAP
    if _MANTRA_OPCODE_MAP is None:
        _MANTRA_OPCODE_MAP = {
            # PHASE 1: WAKE (Hare Krishna Hare Krishna)
            "wake": "sys_wake",
            "identity": "load_root",
            "alloc": "alloc_mem",
            "bind": "bind_ctx",
            # PHASE 2: PURIFY (Krishna Krishna Hare Hare)
            "verify": "assert_truth",
            "parse": "resolve_req",
            "gc": "garbage_collect",
            "pulse": "pulse_sync",
            # PHASE 3: SERVE (Hare Rama Hare Rama)
            "fetch": "fetch_res",
            "exec": "exec_service",
            "check": "check_dharma",
            "commit": "commit_log",
            # PHASE 4: SUSTAIN (Rama Rama Hare Hare)
            "cache": "cache_state",
            "optimize": "optimize",
            "yield": "yield_cpu",
            "reset": "reset_ip",
        }
    return _MANTRA_OPCODE_MAP


@dataclass
class MantraProcessorResult:
    """
    Result of MantraProcessor routing.

    Contains both the CLI result and the routing metadata.
    """
    command: str
    opcode: str
    mahajana: str
    quarter: int
    position: int
    is_head: bool  # True if HEAD (Avatara), False if Worker (Mahajana)
    result: CliResult


class MantraProcessor:
    """
    The Computational Engine - CLI commands become chants.

    FRACTAL ARCHITECTURE:
    - Each CLI command maps to a MantraOpCode
    - Each OpCode routes to a Mahajana (or Avatara for HEADs)
    - The Mahajana executes and returns the result

    This eliminates manual wiring - the Mahamantra IS the routing.

    Usage:
        processor = MantraProcessor()
        result = processor.chant("exec", ctx, payload)
        # Routes to Prahlada (EXEC_SERVICE owner)
    """

    def __init__(self):
        self._router = _get_mahajana_router()
        self._opcode_map = _get_opcode_map()
        self._shell = ChaitanyaShell()

    def get_opcode(self, command: str) -> Optional[str]:
        """Get MantraOpCode for a CLI command."""
        return self._opcode_map.get(command)

    def get_mahajana(self, command: str) -> Optional[str]:
        """Get owning Mahajana for a CLI command."""
        opcode_value = self.get_opcode(command)
        if opcode_value is None:
            return None

        try:
            from vibe_core.protocols.universal.mantra import MantraOpCode
            opcode = MantraOpCode(opcode_value)
            return self._router.route(opcode).value
        except (ValueError, AttributeError):
            return None

    def is_head_command(self, command: str) -> bool:
        """Check if command is a HEAD (Avatara-owned, not Mahajana)."""
        opcode_value = self.get_opcode(command)
        if opcode_value is None:
            return False

        try:
            from vibe_core.protocols.universal.mantra import MantraOpCode
            from vibe_core.protocols.mahajanas.router import HEAD_OPCODES
            opcode = MantraOpCode(opcode_value)
            return opcode in HEAD_OPCODES
        except (ValueError, ImportError):
            return False

    def chant(
        self,
        command: str,
        ctx: "SovereignContext",
        payload: CliPayload = None
    ) -> MantraProcessorResult:
        """
        Execute a CLI command through Mahajana routing.

        Args:
            command: CLI command name (e.g., "exec", "verify")
            ctx: Sovereign context (the 37th)
            payload: Command payload

        Returns:
            MantraProcessorResult with routing metadata and result
        """
        opcode_value = self.get_opcode(command)
        if opcode_value is None:
            return MantraProcessorResult(
                command=command,
                opcode="unknown",
                mahajana="unknown",
                quarter=0,
                position=0,
                is_head=False,
                result=MahamantraGrace(
                    message=f"Unknown command: {command}. Hare Krishna!",
                    retry_allowed=False,
                ),
            )

        try:
            from vibe_core.protocols.universal.mantra import MantraOpCode
            from vibe_core.protocols.mahajanas.router import HEAD_OPCODES

            opcode = MantraOpCode(opcode_value)
            is_head = opcode in HEAD_OPCODES

            # Get route info
            route = self._router.get_route(opcode)

            # Execute through shell (with grace fallback)
            cli_result = self._shell.chant_with_grace(ctx, command, payload)

            return MantraProcessorResult(
                command=command,
                opcode=opcode_value,
                mahajana=route.mahajana.value,
                quarter=route.quarter,
                position=route.position,
                is_head=is_head,
                result=cli_result,
            )

        except Exception as e:
            return MantraProcessorResult(
                command=command,
                opcode=opcode_value,
                mahajana="unknown",
                quarter=0,
                position=0,
                is_head=False,
                result=MahamantraGrace(
                    grace_type=GraceType.PRABHUPADA,
                    message=f"Routing error: {str(e)}. Hare Krishna!",
                    original_error=str(e),
                ),
            )

    def list_commands(self) -> List[Dict[str, Union[str, int, bool]]]:
        """List all CLI commands with their routing info."""
        commands = []
        for cmd, opcode_value in self._opcode_map.items():
            try:
                from vibe_core.protocols.universal.mantra import MantraOpCode
                from vibe_core.protocols.mahajanas.router import HEAD_OPCODES

                opcode = MantraOpCode(opcode_value)
                is_head = opcode in HEAD_OPCODES
                route = self._router.get_route(opcode)

                commands.append({
                    "command": cmd,
                    "opcode": opcode_value,
                    "mahajana": route.mahajana.value,
                    "quarter": route.quarter,
                    "position": route.position,
                    "is_head": is_head,
                })
            except Exception:
                commands.append({
                    "command": cmd,
                    "opcode": opcode_value,
                    "mahajana": "unknown",
                    "quarter": 0,
                    "position": 0,
                    "is_head": False,
                })

        return sorted(commands, key=lambda x: x["position"])


# =============================================================================
# GAD-000 SEAL - "No Manual Labour"
# =============================================================================
#
# The code IS the documentation. The routing IS the Mahamantra.
# This seal VERIFIES the full stack:
#   CLI → MantraOpCode → MahajanaRouter → Mahajana → chant() → Krishna
#
# If any link is broken, the seal fails.
# =============================================================================


@dataclass(frozen=True)
class GAD000Seal:
    """
    The sealed verification of GAD-000 compliance.

    No manual labour - if the seal is valid, the stack is connected.
    If the seal fails, something is broken.

    THE MATH:
        16 commands = 16 words = 16 OpCodes
        4 HEADs (Avataras) + 12 Worker OpCodes = 16 handlers
        37 = 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna)
        All understood through the Guru's lens (Prabhupada)

    NOTE on Mahajana count:
        - VYUHA mode (1:1): 12 unique Mahajanas for 12 worker opcodes
        - Legacy mode: 9 unique Mahajanas (some handle multiple opcodes)
        Both are valid - all 12 worker opcodes are handled.
    """
    commands_mapped: int          # Should be 16
    opcodes_routed: int           # Should be 16
    worker_opcodes: int           # Should be 12 (non-HEAD opcodes)
    heads_active: int             # Should be 4
    unique_mahajanas: int         # 9-12 depending on mode
    heartbeat_available: bool     # MantraHeartbeat accessible
    krishna_present: bool         # Always True (acintya)

    @property
    def is_valid(self) -> bool:
        """Is the seal valid? All checks must pass."""
        return (
            self.commands_mapped == 16 and
            self.opcodes_routed == 16 and
            self.worker_opcodes == 12 and
            self.heads_active == 4 and
            self.unique_mahajanas >= 9 and  # Legacy mode has 9, vyuha has 12
            self.heartbeat_available and
            self.krishna_present
        )

    @property
    def marker(self) -> str:
        """GAD-000 compliance marker."""
        if self.is_valid:
            return "GAD-000:SEALED:37"
        missing = []
        if self.commands_mapped != 16:
            missing.append(f"cmd:{self.commands_mapped}/16")
        if self.opcodes_routed != 16:
            missing.append(f"op:{self.opcodes_routed}/16")
        if self.worker_opcodes != 12:
            missing.append(f"worker:{self.worker_opcodes}/12")
        if self.heads_active != 4:
            missing.append(f"head:{self.heads_active}/4")
        if self.unique_mahajanas < 9:
            missing.append(f"maha:{self.unique_mahajanas}/<9")
        if not self.heartbeat_available:
            missing.append("no-heartbeat")
        if not self.krishna_present:
            missing.append("IMPOSSIBLE")  # Krishna is always present
        return f"GAD-000:BROKEN:[{','.join(missing)}]"


def verify_gad000() -> GAD000Seal:
    """
    Verify the full GAD-000 stack.

    No manual labour - this function checks everything:
    1. All 16 CLI commands are mapped to OpCodes
    2. All 16 OpCodes route to handlers (4 HEADs + 12 Workers)
    3. MantraHeartbeat is available for chanting
    4. Krishna is present (always True - acintya)

    Returns:
        GAD000Seal with verification results
    """
    # Get the opcode map
    opcode_map = _get_opcode_map()
    commands_mapped = len(opcode_map)

    # Verify routing
    opcodes_routed = 0
    worker_opcodes = 0
    mahajanas_seen = set()
    heads_seen = set()

    try:
        from vibe_core.protocols.universal.mantra import MantraOpCode
        from vibe_core.protocols.mahajanas.router import (
            MahajanaRouter, HEAD_OPCODES, Mahajana
        )

        router = MahajanaRouter()

        for cmd, opcode_value in opcode_map.items():
            try:
                opcode = MantraOpCode(opcode_value)
                if opcode in HEAD_OPCODES:
                    heads_seen.add(opcode_value)
                else:
                    mahajana = router.route(opcode)
                    mahajanas_seen.add(mahajana)
                    worker_opcodes += 1
                opcodes_routed += 1
            except Exception:
                pass

    except ImportError:
        pass

    # Check heartbeat
    heartbeat_available = False
    try:
        from vibe_core.protocols.gad import MantraHeartbeat
        hb = MantraHeartbeat()
        heartbeat_available = hb.krishna_present  # Always True
    except Exception:
        pass

    # Krishna is ALWAYS present (acintya - Level -2)
    krishna_present = True

    return GAD000Seal(
        commands_mapped=commands_mapped,
        opcodes_routed=opcodes_routed,
        worker_opcodes=worker_opcodes,
        heads_active=len(heads_seen),
        unique_mahajanas=len(mahajanas_seen),
        heartbeat_available=heartbeat_available,
        krishna_present=krishna_present,
    )


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

# The strict shell (original behavior)
ANANTA_SHESHA = AnantaShesha()

# The graceful shell (Chaitanya Singularity)
CHAITANYA_SHELL = ChaitanyaShell()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Strict Types (Anti-Mayavad - NO ANY)
    "CliInput",
    "CliPayload",
    "CliResult",
    "NavigationContent",
    # Original (strict)
    "AnantaResponse",
    "ShellProtocol",
    "AnantaShesha",
    "ANANTA_SHESHA",
    # Chaitanya Singularity (graceful)
    "MAHAMANTRA",
    "GraceType",
    "MahamantraGrace",
    "ICliProtocol",
    "NavigationResult",
    "ChaitanyaShell",
    "CHAITANYA_SHELL",
    # ICommand Protocol (16-Command Interface)
    "CommandResult",
    "CommandHelp",
    "ICliCommand",
    # MantraProcessor (Computational Engine)
    "MantraProcessorResult",
    "MantraProcessor",
    # GAD-000 Seal (No Manual Labour)
    "GAD000Seal",
    "verify_gad000",
]
