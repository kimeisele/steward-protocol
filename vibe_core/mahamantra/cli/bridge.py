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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x9f312c63"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Callable, Dict, Final, List, Optional, Set, Tuple, Union

# ONE IMPORT - Krishna IS the router
from vibe_core.mahamantra.kernel.singularity import mahamantra

# =============================================================================
# RESONANCE-BASED ROUTING - No Keyword Matching
# =============================================================================
#
# KREBS ENTFERNT: DOMAIN_KEYWORDS und _KEYWORD_TO_POSITION gelöscht.
# Routing geht durch cli_auto._get_position() mit MahaCompression.
#
# "mattaḥ sarvaṁ pravartate" - Resonanz bestimmt Position, nicht Keywords.
#


# =============================================================================
# CLI BRIDGE RESULT
# =============================================================================


@dataclass
class BridgeResult:
    """Result from bridge routing."""

    success: bool
    exit_code: int
    position: Optional[int] = None  # Mahajana position that handled it
    handler: Optional[str] = None  # Handler name
    fallback: bool = False  # True if fell back to CLIRegistry
    error: Optional[str] = None


# =============================================================================
# LEGACY SYSTEM COMMANDS - REMOVED
# =============================================================================
#
# KREBS ENTFERNT: Hardcoded LEGACY_SYSTEM_COMMANDS set gelöscht.
# ALLES geht durch mahamantra. Keine Bypass-Listen mehr.
#


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
        Get mahajana position for a command via RESONANCE.

        KEINE KEYWORD MATCHING. Nutzt cli_auto._get_position() mit:
        - MahaCompression → Seed
        - MahaKirtan → Vibration
        - Category → Position

        "mattaḥ sarvaṁ pravartate" - Resonanz bestimmt alles.
        """
        from vibe_core.mahamantra.cli.auto import cli_auto

        # Ensure discovery happened
        if not cli_auto._discovered:
            cli_auto.discover_all()

        # RESONANZ-BASED ROUTING
        return cli_auto._get_position(command.lower())

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
        1. Get position via Siksastakam (O(1) cached) OR fallback to self.get_position
        2. Execute via cli_auto (has the method matching logic)
        3. Fallback to Legacy if needed

        SIKSASTAKAM: Position routing is cached. Method matching via cli_auto.
        """
        from vibe_core.mahamantra.cli.protocol import CLIErrorCode
        from vibe_core.mahamantra.cli.auto import cli_auto

        # =================================================================
        # POSITION ROUTING - Direct routing (registry DELETED)
        # =================================================================
        position = self.get_position(command)

        # =================================================================
        # EXECUTION - cli_auto (has method matching)
        # =================================================================
        result = cli_auto.execute(command, args)

        # If not implemented in cli_engine, try legacy fallback
        if (
            self._fallback_enabled
            and result.error
            and result.error.code in (CLIErrorCode.NOT_IMPLEMENTED, CLIErrorCode.UNKNOWN_COMMAND)
        ):
            return self._execute_fallback(command, args, position)

        return BridgeResult(
            success=result.success,
            exit_code=result.exit_code,
            position=position,
            handler=f"cli_engine[{position}]",
            fallback=False,
            error=result.error.message if result.error else None,
        )

    def _execute_fallback(self, command: str, args: List[str], position: int) -> BridgeResult:
        """
        Fallback execution: CLIRegistry (Plugins/Cartridges).

        KREBS ENTFERNT: Keine hardcoded LEGACY_SYSTEM_COMMANDS mehr.
        Alles geht durch mahamantra oder CLIRegistry für plugins.
        """
        # CLIRegistry (Plugins/Cartridges) - einziger Fallback
        return self._fallback_to_registry(command, args, position)

    def _fallback_to_registry(self, command: str, args: List[str], position: int) -> BridgeResult:
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
                    fallback=True,
                )
        except ImportError:
            pass
        except Exception as e:
            return BridgeResult(
                success=False, exit_code=1, position=position, error=f"CLIRegistry fallback failed: {e}", fallback=True
            )

        return BridgeResult(
            success=False,
            exit_code=127,  # Command not found
            position=position,
            error=f"Command not found: {command}",
        )

    # =========================================================================
    # REGISTRATION (for gradual migration)
    # =========================================================================

    def register_handler(self, position: int, handler: Callable[[str, List[str]], int]) -> None:
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
            "is_head": pos.is_head,
            # KREBS ENTFERNT: Keine hardcoded keywords mehr
        }

    def list_routes(self) -> List[Tuple[str, int, str]]:
        """List all position → guardian mappings (resonance-based)."""
        routes = []
        for position in range(16):
            pos = mahamantra[position]
            guardian = pos.guardian.value if hasattr(pos.guardian, "value") else str(pos.guardian)
            routes.append((guardian, position, guardian))
        return routes

    def __repr__(self) -> str:
        return f"MahamantraCLIBridge(positions=16, fallback={self._fallback_enabled})"


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
    # KREBS ENTFERNT: DOMAIN_KEYWORDS gelöscht
    "route",
    "get_position",
]
