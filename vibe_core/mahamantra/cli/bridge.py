"""
CLI BRIDGE - Krishna Routes All Commands
========================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

RESONANZ-BASED ROUTING:
    Intent → MahaCompression → Seed → Category → Position → Execute

KEINE FALLBACKS. KEINE LEGACY BYPASSES.
Wenn mahamantra es nicht kann, FAIL.

ONE IMPORT, KRISHNA ROUTES:
    from vibe_core.mahamantra import cli_bridge
    result = cli_bridge.route("status", ["--verbose"])
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x9f312c63"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Callable, Dict, Final, List, Optional, Set, Tuple, Union

# ONE IMPORT - Krishna IS the router
# FIX: MahamantraLotus hat __call__ UND __getitem__ (Singularity nur __getitem__)
from vibe_core.mahamantra import mahamantra

# SSOT - WORDS derives from Mahamantra counting
from vibe_core.mahamantra.substrate.seed import WORDS

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
    """Result from bridge routing. KEINE FALLBACKS."""

    success: bool
    exit_code: int
    position: Optional[int] = None  # Mahajana position that handled it
    handler: Optional[str] = None  # Handler name
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
        Route and execute a CLI command durch MAHAMANTRA.

        KEINE FALLBACKS. Wenn mahamantra es nicht kann, FAIL.

        "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
        """
        from vibe_core.mahamantra.cli.auto import cli_auto

        # RESONANZ-BASED POSITION
        position = self.get_position(command)

        # EXECUTION - cli_auto mit MahaCompression
        result = cli_auto.execute(command, args)

        return BridgeResult(
            success=result.success,
            exit_code=result.exit_code,
            position=position,
            handler=f"mahamantra[{position}]",
            error=result.error.message if result.error else None,
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
        for position in range(WORDS):  # SSOT: WORDS from seed.py
            pos = mahamantra[position]
            guardian = pos.guardian.value if hasattr(pos.guardian, "value") else str(pos.guardian)
            routes.append((guardian, position, guardian))
        return routes

    def __repr__(self) -> str:
        return f"MahamantraCLIBridge(positions={WORDS}, resonance=True)"  # SSOT: WORDS


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
