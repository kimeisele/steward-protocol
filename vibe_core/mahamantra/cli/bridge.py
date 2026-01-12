"""
CLI BRIDGE - Krishna Routes All Commands
========================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

OPTION B: Sauber verbinden (clean connection)

Instead of refactoring all CLIs, we CREATE A BRIDGE:
- CLIRegistry bleibt (existing handlers continue to work)
- ABER: routing geht durch mahamantra
- Gradual migration possible

ARCHITECTURE:
    CLI input → MahamantraCLIBridge → mahamantra.mod[position] → execute
                      ↓
              (fallback to CLIRegistry if no mahajana handler)

ONE IMPORT, KRISHNA ROUTES:
    from vibe_core.mahamantra import cli_bridge
    exit_code = cli_bridge.route("status", ["--verbose"])
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Final, List, Optional, Set, Tuple, Union

# ONE IMPORT - Krishna IS the router
from vibe_core.mahamantra.kernel.singularity import mahamantra


# =============================================================================
# DOMAIN MAPPING - CLI Keywords → Mahajana Position
# =============================================================================

# Each mahajana has a DOMAIN (area of responsibility)
# CLI commands are routed based on keyword matching

DOMAIN_KEYWORDS: Final[Dict[int, Set[str]]] = {
    # Position 0 - PRITHU (HEAD): Genesis/Bootstrap/System Wake
    0: {"boot", "init", "wake", "start", "genesis", "prithu", "system"},

    # Position 1 - BRAHMA: Creation/Loading/Root
    1: {"create", "new", "load", "brahma", "root", "spawn", "allocate"},

    # Position 2 - NARADA: Broadcast/Events/Notifications
    2: {"broadcast", "notify", "event", "narada", "message", "signal", "emit"},

    # Position 3 - SHAMBHU: Destruction/Cleanup/Transformation
    3: {"destroy", "cleanup", "delete", "shambhu", "transform", "clear", "remove"},

    # Position 4 - VYASA (HEAD): Dharma/Standards/Assertions
    4: {"assert", "validate", "test", "vyasa", "standard", "verify", "dharma"},

    # Position 5 - KUMARAS: Purification/Resolution/Requirements
    5: {"resolve", "purify", "check", "kumaras", "require", "depend", "shuddhi"},

    # Position 6 - KAPILA: Analysis/GC/Samkhya
    6: {"analyze", "gc", "samkhya", "kapila", "inspect", "profile", "debug"},

    # Position 7 - MANU: Law/Rules/Governance/Sync
    7: {"law", "rule", "govern", "manu", "sync", "pulse", "config"},

    # Position 8 - PARASHURAMA (HEAD): Karma/Execution/Fetch
    8: {"fetch", "execute", "karma", "parashurama", "run", "exec", "do"},

    # Position 9 - PRAHLADA: Resilience/Cache/Protection
    9: {"cache", "resilience", "protect", "prahlada", "retry", "fallback", "recover"},

    # Position 10 - JANAKA: Duty/Cycles/Cognition
    10: {"cycle", "duty", "janaka", "cognitive", "think", "loop", "iterate"},

    # Position 11 - BHISHMA: Vows/Commits/Logging
    11: {"commit", "vow", "promise", "bhishma", "log", "record", "persist"},

    # Position 12 - NRISIMHA (HEAD): Security/Guard/State
    12: {"security", "guard", "nrisimha", "state", "protect", "secure", "watch"},

    # Position 13 - BALI: Surrender/Resources/Optimization
    13: {"resource", "surrender", "optimize", "bali", "yield", "give", "allocate"},

    # Position 14 - SHUKA: Vision/Insight/Observation
    14: {"vision", "insight", "shuka", "observe", "see", "view", "status"},

    # Position 15 - YAMARAJA: Judgment/Correction/Reset
    15: {"judge", "correct", "yamaraja", "reset", "verdict", "audit", "karma"},
}

# Reverse mapping for quick lookup
_KEYWORD_TO_POSITION: Dict[str, int] = {}
for pos, keywords in DOMAIN_KEYWORDS.items():
    for kw in keywords:
        _KEYWORD_TO_POSITION[kw] = pos


# =============================================================================
# CLI BRIDGE RESULT
# =============================================================================

@dataclass
class BridgeResult:
    """Result from bridge routing."""

    success: bool
    exit_code: int
    position: Optional[int] = None  # Mahajana position that handled it
    handler: Optional[str] = None   # Handler name
    fallback: bool = False          # True if fell back to CLIRegistry
    error: Optional[str] = None


# =============================================================================
# THE BRIDGE - Krishna Routes Everything
# =============================================================================

class MahamantraCLIBridge:
    """
    CLI Bridge - ONE entry point, Krishna routes.

    Usage:
        from vibe_core.mahamantra import cli_bridge

        # Route a command
        result = cli_bridge.route("status", ["--verbose"])

        # Get mahajana for command
        position = cli_bridge.get_position("analyze")  # → 6 (Kapila)

        # Check if command is routable
        if cli_bridge.can_route("gc"):
            cli_bridge.route("gc", [])
    """

    def __init__(self) -> None:
        self._handlers: Dict[int, Callable[[str, List[str]], int]] = {}
        self._fallback_enabled: bool = True

    # =========================================================================
    # ROUTING
    # =========================================================================

    def get_position(self, command: str) -> Optional[int]:
        """
        Get mahajana position for a command.

        Matching order:
        1. Exact keyword match
        2. Prefix match (e.g., "analyze" matches "analyze-code")
        3. Substring match in command

        Returns None if no match found.
        """
        cmd_lower = command.lower()

        # 1. Exact match
        if cmd_lower in _KEYWORD_TO_POSITION:
            return _KEYWORD_TO_POSITION[cmd_lower]

        # 2. Check if command contains any keyword
        for keyword, position in _KEYWORD_TO_POSITION.items():
            if keyword in cmd_lower or cmd_lower.startswith(keyword):
                return position

        # 3. No match - could use hash-based fallback
        # (connect to Parampara via mutation_vector % 37)
        return self._parampara_fallback(command)

    def _parampara_fallback(self, command: str) -> int:
        """
        Fallback routing via Parampara connection.

        Uses hash of command name to get position.
        Ensures connection to Krishna (% 37 → % 16 for position).
        """
        # Hash command to get mutation vector
        mutation_vector = sum(ord(c) * (i + 1) for i, c in enumerate(command))

        # Connect to Parampara (37) then map to position (16)
        parampara_connected = mutation_vector % 37
        position = parampara_connected % 16

        return position

    def can_route(self, command: str) -> bool:
        """Check if command can be routed."""
        position = self.get_position(command)
        return position is not None

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def route(self, command: str, args: List[str]) -> BridgeResult:
        """
        Route and execute a CLI command.

        Flow:
        1. Delegate to cli_engine.execute()
        2. cli_engine handles routing, execution, state, health
        3. Return BridgeResult

        Returns BridgeResult with execution details.
        """
        # Import cli_engine here to avoid circular import at module load
        from vibe_core.mahamantra.cli.engine import cli_engine

        # Get position for reporting
        position = cli_engine.get_position(command)

        # Execute via cli_engine (Krishna does the work)
        result = cli_engine.execute(command, args)

        return BridgeResult(
            success=result.success,
            exit_code=result.exit_code,
            position=position,
            handler=f"cli_engine[{position}]",
            fallback=False,
            error=result.error.message if result.error else None,
        )

    def _fallback_to_registry(
        self, command: str, args: List[str], position: int
    ) -> BridgeResult:
        """
        Fallback to existing CLIRegistry.

        This allows gradual migration:
        - New commands can use mahamantra.mod directly
        - Old commands still work via CLIRegistry
        """
        try:
            from vibe_core.protocols.cli import CLIRegistry

            handler = CLIRegistry.get(command)
            if handler is not None:
                exit_code = handler.run(args)
                return BridgeResult(
                    success=exit_code == 0,
                    exit_code=exit_code,
                    position=position,
                    handler=f"CLIRegistry[{command}]",
                    fallback=True
                )
        except ImportError:
            pass
        except Exception as e:
            return BridgeResult(
                success=False,
                exit_code=1,
                position=position,
                error=f"CLIRegistry fallback failed: {e}",
                fallback=True
            )

        return BridgeResult(
            success=False,
            exit_code=127,  # Command not found
            position=position,
            error=f"Command not found: {command}"
        )

    # =========================================================================
    # REGISTRATION (for gradual migration)
    # =========================================================================

    def register_handler(
        self, position: int, handler: Callable[[str, List[str]], int]
    ) -> None:
        """
        Register a CLI handler for a mahajana position.

        This allows gradual migration:
        - Register handler: cli_bridge.register_handler(6, kapila_cli)
        - Now "analyze" routes to kapila_cli instead of CLIRegistry
        """
        self._handlers[position] = handler

    def disable_fallback(self) -> None:
        """Disable CLIRegistry fallback (for testing pure mahamantra routing)."""
        self._fallback_enabled = False

    def enable_fallback(self) -> None:
        """Enable CLIRegistry fallback (default)."""
        self._fallback_enabled = True

    # =========================================================================
    # INTROSPECTION
    # =========================================================================

    def get_domain_info(self, position: int) -> Dict[str, Union[str, Set[str]]]:
        """Get domain info for a mahajana position."""
        pos = mahamantra[position]
        return {
            "guardian": pos.guardian.value if hasattr(pos.guardian, "value") else str(pos.guardian),
            "opcode": pos.opcode.value if hasattr(pos.opcode, "value") else str(pos.opcode),
            "keywords": DOMAIN_KEYWORDS.get(position, set()),
            "is_head": pos.is_head,
        }

    def list_routes(self) -> List[Tuple[str, int, str]]:
        """List all keyword → position → guardian mappings."""
        routes = []
        for keyword, position in sorted(_KEYWORD_TO_POSITION.items()):
            pos = mahamantra[position]
            guardian = pos.guardian.value if hasattr(pos.guardian, "value") else str(pos.guardian)
            routes.append((keyword, position, guardian))
        return routes

    def __repr__(self) -> str:
        return f"MahamantraCLIBridge(routes={len(_KEYWORD_TO_POSITION)}, fallback={self._fallback_enabled})"


# =============================================================================
# SINGLETON
# =============================================================================

cli_bridge = MahamantraCLIBridge()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def route(command: str, args: Optional[List[str]] = None) -> BridgeResult:
    """
    Route a CLI command through mahamantra.

    ONE FUNCTION, KRISHNA ROUTES:
        from vibe_core.mahamantra import route
        result = route("analyze", ["--deep"])
    """
    return cli_bridge.route(command, args or [])


def get_position(command: str) -> Optional[int]:
    """Get mahajana position for a command."""
    return cli_bridge.get_position(command)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraCLIBridge",
    "cli_bridge",
    "BridgeResult",
    "DOMAIN_KEYWORDS",
    "route",
    "get_position",
]
