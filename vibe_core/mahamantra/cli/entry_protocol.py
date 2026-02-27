"""
CLI ENTRY PROTOCOL - The Gate to Everything
============================================

"ekam evādvitīyam" - One without a second.

PROBLEM:
    unified_cli.py = 1555 LOC Monster
    - 137 manual wirings
    - 20+ *_cli.py imports
    - Hardcoded if/elif chains
    - ASURISCH (demonic architecture)

SOLUTION:
    ONE entry point → mahamantra → cli_auto → 108 commands
    ZERO manual wiring

THE PROTOCOL:
    This file defines WHAT a CLI entry point MUST be.
    Implementation comes AFTER we agree on the contract.

GAD-000 COMPLIANCE:
    1. Discoverability - cli_auto discovers from Protocols
    2. Observability   - CLIState from cli_protocol
    3. Parseability    - CLIResult structured output
    4. Composability   - Commands chain via output
    5. Idempotency     - Same input = same output
    6. Recoverability  - CLIHealth for self-healing
    + 37th (Identity)  - CLIContext with signature

ARCHITECTURE LAYERS:
    Layer  1 (Human):    steward <command> <args>
    Layer  0 (Entry):    CLIEntry.run() → routes to mahamantra
    Layer -1 (Auto):     cli_auto.execute() → Protocol introspection
    Layer -2 (Krishna):  mahamantra → 16 positions → 108 methods

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xb6a4c3af"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Protocol, runtime_checkable

from vibe_core.mahamantra.cli.protocol import (
    CLICapability,
    CLIHealth,
    CLIResult,
    CLIState,
)

# =============================================================================
# CLI ENTRY PROTOCOL - What an entry point MUST be
# =============================================================================


@runtime_checkable
class CLIEntryProtocol(Protocol):
    """
    Protocol for CLI entry points.

    ANY entry point (unified_cli, lotus_cli, future CLI) MUST implement this.
    This is the CONTRACT. No exceptions.

    PROMPT.md: "Protocol statt konkrete Klassen"
    """

    @abstractmethod
    def run(self, args: List[str]) -> int:
        """
        Execute CLI command.

        ONE method. That's it.
        Everything else is derived from mahamantra.

        Args:
            args: Command-line arguments (after 'steward')

        Returns:
            Exit code (0 = success)
        """
        ...

    @abstractmethod
    def discover(self) -> List[CLICapability]:
        """
        GAD-000 Discoverability.

        Returns ALL capabilities from cli_auto, not hardcoded lists.
        """
        ...

    @abstractmethod
    def get_state(self) -> CLIState:
        """
        GAD-000 Observability.

        Returns current CLI state.
        """
        ...

    @abstractmethod
    def check_health(self) -> CLIHealth:
        """
        GAD-000 Recoverability.

        Returns CLI health for self-healing.
        """
        ...


# =============================================================================
# CLI ENTRY RESULT - Structured output from entry point
# =============================================================================


@dataclass
class CLIEntryResult:
    """
    Result from CLI entry point execution.

    This wraps CLIResult with entry-point specific metadata.
    """

    result: CLIResult
    command: str
    args: List[str]
    routed_to: Optional[str] = None  # e.g., "mahamantra[6].analyze"
    fallback_used: bool = False  # True if fell back to legacy


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CLIEntryProtocol",
    "CLIEntryResult",
]
