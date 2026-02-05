"""
CLI ENTRY - The Thin Gate
=========================

DEPRECATED: Use vibe_core.mahamantra.__main__ instead.
This file is kept for backwards compatibility only.

The TRUE entry point is now:
    vibe_core/mahamantra/__main__.py

"ekam evādvitīyam" - One without a second.

This is the ONLY entry point. Everything routes through mahamantra.

BEFORE (unified_cli.py):
    1555 LOC
    137 manual wirings
    20+ imports
    if/elif chains

AFTER (this file):
    ~100 LOC
    ZERO manual wiring
    ONE import (mahamantra)
    Protocol introspection

ARCHITECTURE:
    steward <command> <args>
           ↓
    MahamantraCLIEntry.run()
           ↓
    cli_auto.execute()
           ↓
    Protocol method (auto-discovered)
           ↓
    CLIResult

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x8aeeac66"  # GenesisByte: parampara % 37 == 0

import json
import sys
from datetime import datetime
from typing import List, Optional

from vibe_core.gateway import chat as gateway_chat
from vibe_core.mahamantra.cli.auto import cli_auto
from vibe_core.mahamantra.cli.cell_wrapper import MahaCellCLI
from vibe_core.mahamantra.cli.entry_protocol import CLIEntryProtocol
from vibe_core.mahamantra.cli.protocol import (
    CLICapability,
    CLIHealth,
    CLIResult,
    CLIState,
)
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.mahamantra.protocols._seed import MALA, WORDS


class MahamantraCLIEntry(CLIEntryProtocol, PanchaTattvaProtocol):
    """
    THE entry point. Krishna routes everything.

    Implements CLIEntryProtocol.
    ZERO manual wiring - everything via cli_auto.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "CLI Entry Point",
            "nityananda": "CLI State & Health",
            "advaita": "Command Dispatch (Run)",
            "gadadhara": "Args Flow",
            "srivasa": "CLI Governance",
        }

    def __init__(self) -> None:
        # Discover ALL on init - Krishna knows everything
        self._discovered = cli_auto.discover_all()
        self._state = CLIState()
        self._health = CLIHealth()
        # Universal Cell Wrapper (Sankirtan Chamber integration)
        self._cell_wrapper = MahaCellCLI()

    def run(self, args: List[str]) -> int:
        """
        Execute CLI command.

        ONE method. Krishna routes to 108 commands.
        """
        if not args:
            self._print_help()
            return 0

        command = args[0]
        remaining = args[1:]

        # Special commands
        if command in ("-h", "--help", "help"):
            self._print_help()
            return 0

        if command == "capabilities":
            return self._show_capabilities()

        if command == "routes":
            return self._show_routes()

        if command == "chat":
            if not remaining:
                print("Usage: steward chat <message>")
                return 1
            # Combine all remaining args into message
            message = " ".join(remaining)
            response = gateway_chat(message)

            # Print output from GatewayResponse
            print()
            if response.success:
                print(response.output)
            else:
                print(f"Error: {response.error}")
            print()
            return response.exit_code

        # Route via mahamantra
        self._state.busy = True
        self._state.last_command = command

        # === MAHACELL INTEGRATION ===
        # Every interaction must flow through the Sankirtan Chamber
        # P0-FIX: Changed from fail-open to fail-close for security
        # Audit trail is MANDATORY - no ghost operations allowed
        try:
            cell = self._cell_wrapper.wrap(command, remaining)
            # Transform cell through Kirtan (metadata update)
            # This doesn't replace execution yet, but ensures spiritual audit trail
            _ = self._cell_wrapper.execute(cell)
        except Exception as e:
            # P0-SECURITY: Fail-close instead of fail-open
            # If audit fails, execution MUST be blocked
            print(f"ERROR: Sankirtan Chamber audit failed: {e}")
            print("SECURITY: Execution blocked - audit trail is mandatory")
            return 1  # Exit with error code

        result = cli_auto.execute(command, remaining)

        self._state.busy = False
        self._state.last_result = result

        # Output result
        self._print_result(result, command)

        return result.exit_code

    def discover(self) -> List[CLICapability]:
        """GAD-000 Discoverability."""
        return cli_auto.get_capabilities()

    def get_state(self) -> CLIState:
        """GAD-000 Observability."""
        return self._state

    def check_health(self) -> CLIHealth:
        """GAD-000 Recoverability."""
        stats = cli_auto.get_stats()
        self._health.healthy = stats["total_methods"] == MALA
        self._health.last_check = datetime.now().isoformat()
        return self._health

    # =========================================================================
    # OUTPUT
    # =========================================================================

    def _print_result(self, result: CLIResult, command: str) -> None:
        """Print structured result."""
        if result.success:
            # Print output items
            for item in result.output.items:
                print(f"{item.key}: {item.value}")
        else:
            # Print error
            if result.error:
                print(f"ERROR [{result.error.code.name}]: {result.error.message}")
            else:
                print(f"Command failed: {command}")

    def _print_help(self) -> None:
        """Print help - discovered from Protocols."""
        print("STEWARD CLI - Krishna Routes Everything")
        print("=" * 50)
        print()
        print(f"Discovered: {self._discovered} commands from 16 positions (12 mahajanas + 4 avataras)")
        print()
        print("USAGE:")
        print("  steward <command> [args]")
        print("  steward capabilities    # List all 108 commands")
        print("  steward routes          # Show routing table")
        print("  steward help            # This help")
        print()
        print("EXAMPLES:")
        print("  steward analyze system")
        print("  steward judge action")
        print("  steward bootstrap")
        print("  steward fetch resource")
        print()
        print("QUARTERS:")
        print("  GENESIS (0-3):  wake, create, broadcast, destroy")
        print("  DHARMA  (4-7):  assert, purify, analyze, sync")
        print("  KARMA   (8-11): fetch, execute, check, commit")
        print("  MOKSHA (12-15): cache, surrender, view, judge")

    def _show_capabilities(self) -> int:
        """Show all capabilities as JSON."""
        caps = self.discover()
        output = [
            {
                "name": c.name,
                "purpose": c.purpose,
                "position": c.mahajana_position,
            }
            for c in caps
        ]
        print(json.dumps(output, indent=2))
        return 0

    def _show_routes(self) -> int:
        """Show routing table."""
        print("MAHAMANTRA ROUTING TABLE")
        print("=" * 70)
        print()

        from vibe_core.mahamantra import mahamantra

        for pos in range(WORDS):
            position = mahamantra[pos]
            guardian = position.guardian.value.upper()
            opcode = position.opcode.name
            is_head = "HEAD" if position.is_head else "    "
            quarter = position.quarter.name

            methods = cli_auto._methods.get(pos, {})
            method_names = ", ".join(sorted(methods.keys())[:5])
            if len(methods) > 5:
                method_names += f", +{len(methods) - 5} more"

            print(f"[{pos:2d}] {guardian:12s} {is_head} {quarter:8s} {opcode:16s}")
            print(f"     → {method_names}")
            print()

        return 0


# =============================================================================
# SINGLETON
# =============================================================================

_entry: Optional[MahamantraCLIEntry] = None


def get_entry() -> MahamantraCLIEntry:
    """Get or create CLI entry singleton."""
    global _entry
    if _entry is None:
        _entry = MahamantraCLIEntry()
    return _entry


# =============================================================================
# ENTRY POINTS
# =============================================================================


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    if argv is None:
        argv = sys.argv[1:]

    entry = get_entry()
    return entry.run(argv)


def cli_entry() -> None:
    """Console script entry point."""
    sys.exit(main())


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraCLIEntry",
    "get_entry",
    "main",
    "cli_entry",
]
