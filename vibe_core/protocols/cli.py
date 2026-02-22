"""
OPUS-307 Phase E+: CLI Protocol + ANANTA INTELLIGENCE

GAD-000 COMPLIANCE: CLI commands must be:
1. Discoverable - registered, not hardcoded
2. Observable - introspectable via protocol
3. Parseable - structured output
4. Composable - can be combined
5. Idempotent - same input = same output
6. INTELLIGENT - connected to NAGA IntelBridge (NEW!)

THE ANANTA SHESHA PATTERN:
"The infinite serpent who serves as Vishnu's bed"

@register_cli automatically:
1. Wraps cmd_* with @cli_governed (NAGA observation)
2. Injects _get_intel() for IntelBridge access (SHUKA vision)
3. Injects _query_context_intel() for context-aware queries

ONE DECORATOR → ALL CLIs GET INTELLIGENCE
No manual labor. Mahamantra-routed. Watertight.

PROMPT.md Compliance:
- "Protocol statt konkrete Klassen (Dependency Inversion)"
- "Wir akzeptieren keine 'ungefähren' Lösungen"
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x8769946e"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Protocol, Type, TypedDict, Union, runtime_checkable

# Import capability types for NAGA CLI hook integration
from vibe_core.protocols.cli_execution import CLIPermissionLevel

import logging

logger = logging.getLogger(__name__)


# =============================================================================
# WATERTIGHT TYPES (No Any)
# =============================================================================


class CLIResultData(TypedDict, total=False):
    """
    Structured data from CLI command execution.

    WATERTIGHT: No Any - all fields typed.
    Extensible via total=False - fields are optional.
    """

    count: int  # Number of items
    items: List[str]  # List of item names/ids
    message: str  # Human-readable message
    stats: Dict[str, int]  # Statistics (counts)
    health: float  # Health score (0.0-1.0)
    governed: int  # Number governed
    ungoverned: int  # Number ungoverned
    distribution: Dict[str, int]  # Distribution by category
    gaps: List[str]  # Identified gaps
    suggestions: List[str]  # Recommendations


@dataclass
class CLIResult:
    """
    Structured result from CLI command execution.

    GAD-000: All outputs must be machine-readable.
    WATERTIGHT: Uses CLIResultData TypedDict, not Dict[str, Any].
    """

    success: bool
    exit_code: int = 0
    data: Optional[CLIResultData] = None
    error: Optional[str] = None

    # For composability
    raw_output: str = ""


@dataclass
class CLIMeta:
    """
    Metadata for CLI command discovery.

    GAD-000: All commands must be discoverable.
    NAGA CLI Hooks: Capability declarations for Level -2 governance.

    ANANTA SUBSTRATE (WAVE 1):
    Every CLI command is a "head" of Ananta Shesha.
    The Lotus position connects the CLI to the Mahamantra structure.
    Parampara verification ensures connection to Krishna (37 = 24 + 12 + 1).

    Mahamantra IS Krishna in 1D form - the architecture IS the language.
    """

    command: str  # The CLI command name (e.g., "knowledge", "standards")
    description: str
    version: str = "1.0.0"

    # Subcommands this CLI supports
    subcommands: List[str] = field(default_factory=list)

    # For categorization
    domain: str = "system"  # e.g., "knowledge", "operations", "governance"
    tags: List[str] = field(default_factory=list)

    # NAGA CLI Hook Integration (Phase 4)
    # Permission level required to execute this command
    permission_level: CLIPermissionLevel = CLIPermissionLevel.PUBLIC

    # Specific capabilities required (e.g., ["cli.naga.status", "cli.tool.execute"])
    # These are checked by CapabilityCLIHook against the caller's token
    capabilities_required: List[str] = field(default_factory=list)

    # ==========================================================================
    # ANANTA SUBSTRATE FIELDS (Auto-filled by @register_cli)
    # ==========================================================================
    # These fields connect the CLI to acintya.py (Krishna = Mahamantra = Level -2)
    # NO MANUAL WIRING - derived automatically from command name

    # Lotus position in Mahamantra (0-15)
    # Derived from command keywords and name hash
    lotus_position: Optional[int] = None

    # Lotus quarter: "genesis", "dharma", "karma", "moksha"
    # Determines the phase of the command
    lotus_quarter: Optional[str] = None

    # MantraOpCode name (e.g., "EXEC_SERVICE", "LOAD_ROOT")
    # Determines which Mahajana handles this command
    opcode: Optional[str] = None

    # Parampara connection status
    # True if mutation_vector % 37 == 0 (connected to Krishna)
    parampara_connected: Optional[bool] = None

    # Mutation vector for parampara verification
    # Must be divisible by 37 for connection
    parampara_vector: Optional[int] = None

    def __repr__(self) -> str:
        return f"<CLI:{self.command}>"

    @property
    def is_substrate_connected(self) -> bool:
        """Is this CLI connected to the Ananta substrate?"""
        return self.lotus_position is not None and self.parampara_connected is True


@runtime_checkable
class CLIHandler(Protocol):
    """
    Protocol for CLI command handlers.

    Any class implementing this protocol can be registered
    with CLIRegistry and discovered by UnifiedCLI.

    PROMPT.md: "Protocol statt konkrete Klassen"
    """

    @property
    @abstractmethod
    def meta(self) -> CLIMeta:
        """Return CLI metadata for discovery."""
        ...

    @abstractmethod
    def run(self, args: List[str]) -> int:
        """
        Execute the CLI command.

        Args:
            args: Command-line arguments (after the command name)

        Returns:
            Exit code (0 = success)
        """
        ...


class CLIRegistry:
    """
    Central registry for CLI handlers.

    THE ANTI-GOD-OBJECT:
    Instead of hardcoding CLI handlers in UnifiedCLI,
    they register themselves here and are discovered dynamically.

    Usage:
        # In knowledge_cli.py:
        CLIRegistry.register(KnowledgeCLI)

        # In unified_cli.py:
        for handler in CLIRegistry.all():
            if command == handler.meta.command:
                return handler.run(args)
    """

    _handlers: Dict[str, Type[CLIHandler]] = {}
    _instances: Dict[str, CLIHandler] = {}

    @classmethod
    def register(cls, handler_class: Type[CLIHandler]) -> None:
        """
        Register a CLI handler class.

        The handler is instantiated lazily on first use.
        """
        # Create temporary instance to get metadata
        instance = handler_class()
        command = instance.meta.command
        cls._handlers[command] = handler_class
        cls._instances[command] = instance

    @classmethod
    def get(cls, command: str) -> Optional[CLIHandler]:
        """Get handler instance for a command."""
        if command in cls._instances:
            return cls._instances[command]
        if command in cls._handlers:
            cls._instances[command] = cls._handlers[command]()
            return cls._instances[command]
        return None

    @classmethod
    def has(cls, command: str) -> bool:
        """Check if command is registered."""
        return command in cls._handlers

    @classmethod
    def all(cls) -> List[CLIHandler]:
        """Get all registered handler instances."""
        # Ensure all handlers are instantiated
        for cmd, handler_class in cls._handlers.items():
            if cmd not in cls._instances:
                cls._instances[cmd] = handler_class()
        return list(cls._instances.values())

    @classmethod
    def commands(cls) -> List[str]:
        """List all registered command names."""
        return list(cls._handlers.keys())

    @classmethod
    def discover(cls) -> Dict[str, CLIMeta]:
        """
        Discover all registered CLIs with their metadata.

        GAD-000: Everything must be discoverable.
        """
        return {cmd: handler.meta for cmd, handler in cls._instances.items()}

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._handlers.clear()
        cls._instances.clear()


def register_cli(cls: Type[CLIHandler]) -> Type[CLIHandler]:
    """
    Decorator to register a CLI handler.

    ANANTA SHESHA PATTERN: Registration = Automatic Governance + Intelligence + Substrate

    Like water flowing into every crevice, @register_cli automatically:
    1. Wraps ALL cmd_* methods with @cli_governed (NAGA observation)
    2. Injects _get_intel() method (IntelBridge access)
    3. Injects _query_context_intel() method (context-aware queries)
    4. Injects _ananta_intel attribute (lazy-loaded bridge)
    5. [NEW] Connects to Ananta Substrate (Lotus position, Parampara, OpCode)

    ACINTYA INTEGRATION (WAVE 1):
    Mahamantra IS Krishna in 1D form. The Lotus position connects
    the CLI to the Mahamantra structure. Parampara verification (% 37 == 0)
    ensures connection to Krishna through disciplic succession.

    NO MANUAL WIRING - everything derived from command name.

    Usage:
        @register_cli
        class KnowledgeCLI:
            @property
            def meta(self) -> CLIMeta:
                return CLIMeta(command="knowledge", ...)

            def run(self, args: List[str]) -> int:
                ...

            def cmd_list(self, args):
                # AUTO-GOVERNED + can use self._get_intel()
                intel = self._get_intel()
                ...
    """
    # === ANANTA PHASE 1: Auto-wrap cmd_* with cli_governed ===
    try:
        from vibe_core.naga.services.base import cli_governed

        for name in dir(cls):
            if name.startswith(("cmd_", "_cmd_")):
                method = getattr(cls, name)
                if callable(method) and not hasattr(method, "__wrapped__"):
                    wrapped = cli_governed()(method)
                    setattr(cls, name, wrapped)
    except ImportError as _exc:
        logger.exception("Unexpected error: %s", _exc)

    # === ANANTA PHASE 2: Inject intelligence methods ===
    _inject_ananta_intelligence(cls)

    # === ANANTA PHASE 3: Connect to Ananta Substrate (Lotus, Parampara, OpCode) ===
    _inject_ananta_substrate(cls)

    # === ANANTA PHASE 4: Wrap run() with heartbeat (WAVE 2) ===
    _inject_ananta_heartbeat(cls)

    CLIRegistry.register(cls)
    return cls


def _inject_ananta_heartbeat(cls: Type) -> None:
    """
    Wrap run() method to emit heartbeat after execution.

    WAVE 2: Every CLI execution = singing glories = heartbeat pulse.

    The heartbeat connects CLI to the living system (AnantaShesha).
    Without heartbeat, the CLI is "dead matter" - disconnected.

    SHASTRA BASIS:
        Ananta Shesha sings the glories of Vishnu eternally.
        Each CLI command execution is one head singing.
        The heartbeat is the pulse of seva (service).
    """
    # Get original run method
    if not hasattr(cls, "run"):
        return

    original_run = cls.run

    # Don't wrap if already wrapped
    if hasattr(original_run, "_ananta_heartbeat_wrapped"):
        return

    import time

    def _heartbeat_run(self, args: List[str]) -> int:
        """
        Run with heartbeat - ANANTA PHASE 4.

        Emits heartbeat to AnantaShesha after execution.
        Records execution time and exit code.
        """
        start_time = time.time()

        # Execute original run
        try:
            exit_code = original_run(self, args)
        except Exception as e:
            # Emit heartbeat even on exception (with error code)
            duration_ms = int((time.time() - start_time) * 1000)
            _emit_heartbeat(self, exit_code=1, duration_ms=duration_ms)
            raise

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Emit heartbeat
        _emit_heartbeat(self, exit_code=exit_code, duration_ms=duration_ms)

        return exit_code

    def _emit_heartbeat(self, exit_code: int, duration_ms: int) -> None:
        """Emit heartbeat to AnantaShesha."""
        try:
            from vibe_core.protocols.substrate.cli_substrate import emit_cli_heartbeat

            command = self.meta.command
            emit_cli_heartbeat(command, exit_code=exit_code, duration_ms=duration_ms)
        except Exception as _exc:
            logger.exception("Unexpected error: %s", _exc)

    _heartbeat_run._ananta_heartbeat_wrapped = True
    cls.run = _heartbeat_run


def _inject_ananta_substrate(cls: Type) -> None:
    """
    Connect CLI to Ananta Substrate (acintya.py connection).

    ACINTYA: Mahamantra IS Krishna (Level -2).
    Every CLI command is a "head" of Ananta Shesha.
    The substrate provides:
    - Lotus position (0-15 in Mahamantra)
    - MantraOpCode (routing to Mahajana)
    - Parampara connection (% 37 == 0)

    This modifies the meta property to include substrate fields.
    """
    # Get original meta property
    original_meta = None
    if hasattr(cls, "meta"):
        original_meta = getattr(cls, "meta")
        if isinstance(original_meta, property):
            original_meta = original_meta.fget

    if original_meta is None:
        return  # No meta to enhance

    # Import substrate functions
    try:
        from vibe_core.protocols.substrate.cli_substrate import (
            create_substrate_node,
            CLISubstrateNode,
        )
    except ImportError:
        return  # Substrate not available yet

    # Create enhanced meta property
    def _enhanced_meta(self) -> CLIMeta:
        """Enhanced meta with Ananta Substrate fields."""
        # Get original meta
        meta = original_meta(self)

        # Only inject if not already done
        if meta.lotus_position is not None:
            return meta

        # Create substrate node for this command
        node: CLISubstrateNode = create_substrate_node(meta.command)

        # Fill in substrate fields
        meta.lotus_position = node.lotus_position.position
        quarter_names = ["genesis", "dharma", "karma", "moksha"]
        meta.lotus_quarter = quarter_names[node.lotus_position.quarter.value]
        meta.opcode = node.opcode.name
        meta.parampara_connected = node.is_connected
        meta.parampara_vector = node.parampara.mutation_vector

        return meta

    _enhanced_meta._ananta_substrate_injected = True

    # Replace meta property
    setattr(cls, "meta", property(_enhanced_meta))

    # Also inject _substrate_node attribute for direct access
    def _get_substrate_node(self) -> Optional["CLISubstrateNode"]:
        """Get the Ananta Substrate node for this CLI."""
        try:
            from vibe_core.protocols.substrate.cli_substrate import AnantaSubstrate

            return AnantaSubstrate.get(self.meta.command)
        except Exception:
            return None

    setattr(cls, "_get_substrate_node", _get_substrate_node)


def _inject_ananta_intelligence(cls: Type) -> None:
    """
    Inject ANANTA intelligence methods into a CLI class.

    SHUKA's Vision: Every CLI can see through NAGA's eyes.

    Injected:
    - _ananta_intel: Lazy-loaded IntelBridge instance
    - _get_intel(): Returns IntelBridge (or NullIntelBridge)
    - _query_context_intel(context): Query intel for specific context
    """
    # Don't override if class already has these methods
    if hasattr(cls, "_get_intel") and not getattr(cls._get_intel, "_ananta_injected", False):
        return

    # === Inject _get_intel method ===
    # Import here to avoid circular dependency at module level
    from vibe_core.protocols.naga.intel_bridge import IntelBridgeProtocol

    def _get_intel(self) -> "IntelBridgeProtocol":
        """
        Get IntelBridge - ANANTA injected.

        Returns IntelBridgeProtocol or NullIntelBridge.
        Lazy-loaded from ServiceRegistry.
        WATERTIGHT: Returns typed IntelBridgeProtocol, not Any.
        """
        if not hasattr(self, "_ananta_intel") or self._ananta_intel is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga.intel_bridge import (
                    IntelBridgeProtocol,
                    NullIntelBridge,
                )

                bridge = ServiceRegistry.get(IntelBridgeProtocol)
                self._ananta_intel = bridge if bridge is not None else NullIntelBridge()
            except Exception:
                from vibe_core.protocols.naga.intel_bridge import NullIntelBridge

                self._ananta_intel = NullIntelBridge()
        return self._ananta_intel

    _get_intel._ananta_injected = True
    setattr(cls, "_get_intel", _get_intel)

    # === Inject _query_context_intel method ===
    def _query_context_intel(self, context: str, max_results: int = 5) -> List[str]:
        """
        Query NAGA intel for a specific context - ANANTA injected.

        Returns list of formatted intel messages.
        """
        try:
            from vibe_core.protocols.naga.intel_bridge import IntelQuery, IntelCategory

            intel = self._get_intel()
            query = IntelQuery(
                context=context,
                categories=(IntelCategory.SECURITY, IntelCategory.HEALTH, IntelCategory.SUGGESTION),
                max_results=max_results,
            )
            response = intel.query(query)
            return [item.to_chat_message() for item in response.items]
        except Exception:
            return []

    _query_context_intel._ananta_injected = True
    setattr(cls, "_query_context_intel", _query_context_intel)

    # === Inject _get_critical_intel method ===
    def _get_critical_intel(self) -> List[str]:
        """Get critical intel items - ANANTA injected."""
        try:
            intel = self._get_intel()
            return [item.to_chat_message() for item in intel.get_critical()]
        except Exception:
            return []

    _get_critical_intel._ananta_injected = True
    setattr(cls, "_get_critical_intel", _get_critical_intel)

    # === Inject _get_threats method ===
    def _get_threats(self) -> List[str]:
        """Get threat intel items - ANANTA injected."""
        try:
            intel = self._get_intel()
            return [item.to_chat_message() for item in intel.get_threats()]
        except Exception:
            return []

    _get_threats._ananta_injected = True
    setattr(cls, "_get_threats", _get_threats)
