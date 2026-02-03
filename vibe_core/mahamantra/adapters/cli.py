"""
MAHA CLI ADAPTER - Bridge between Resonance and Action
======================================================

"yogaḥ karmasu kauśalam" - Yoga is skill in action.

PURE RESONANCE MATCHING:
    1. mahamantra(input) → position (0-15)
    2. CLIMeta.lotus_position == position → MATCH

NO keyword matching. NO hardcoded imports.
The Mahamantra KNOWS. The CLI declares its position. They meet.

HOLOGRAPHIC PRINCIPLE:
    - Every @register_cli decorated CLI auto-gets lotus_position
    - CLIRegistry.all() discovers ALL CLIs dynamically
    - Position match = resonance alignment
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x4e8a7c21"

import importlib
import pkgutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from vibe_core.protocols.cli import CLIHandler, CLIMeta, CLIRegistry


@dataclass
class AdapterResult:
    """Result from the MahaCLI Adapter."""

    resonance: Dict = field(default_factory=dict)
    executed: bool = False
    cli_command: Optional[str] = None
    cli_result: Optional[int] = None
    matched_position: Optional[int] = None


class MahaCLIAdapter:
    """
    Bridge between Mahamantra Resonance and Domain CLIs.

    PURE RESONANCE MATCHING:
        resonance["position"] == cli.meta.lotus_position

    NO keyword matching. NO string comparison.
    The system is holographic - position IS meaning.
    """

    def __init__(self) -> None:
        self._discovered = False

    def _discover_all_clis(self) -> None:
        """
        Dynamically discover ALL CLIs in vibe_core/cli/.

        NO hardcoded imports. Walk the package and import everything.
        Each @register_cli decorator auto-registers with CLIRegistry.
        """
        if self._discovered:
            return

        try:
            import vibe_core.cli as cli_package

            package_path = Path(cli_package.__file__).parent

            # Import all *_cli.py modules
            for module_info in pkgutil.iter_modules([str(package_path)]):
                if module_info.name.endswith("_cli"):
                    try:
                        importlib.import_module(f"vibe_core.cli.{module_info.name}")
                    except ImportError:
                        pass  # Skip broken modules
        except ImportError:
            pass

        self._discovered = True

    def execute(
        self,
        input_text: str,
        *,
        mode: str = "observe",
    ) -> AdapterResult:
        """
        Execute input through resonance matching.

        Args:
            input_text: Any input
            mode: "observe" (match only) or "execute" (run CLI)

        Returns:
            AdapterResult with resonance and execution data
        """
        # 1. Get resonance from Mahamantra
        from vibe_core.mahamantra import mahamantra

        resonance = mahamantra(input_text)

        # 2. Discover all CLIs (dynamic, no hardcoding)
        self._discover_all_clis()

        # 3. Find CLI by POSITION MATCH (pure resonance)
        position = resonance.get("position")
        cli = self._find_by_position(position)

        result = AdapterResult(
            resonance=resonance,
            matched_position=position,
        )

        if cli:
            result.cli_command = cli.meta.command

            # 4. Execute if requested
            if mode == "execute":
                # Parse subcommand from input if present
                args = self._extract_args(input_text, cli)
                result.cli_result = cli.run(args)
                result.executed = True

        return result

    def _find_by_position(self, position: int) -> Optional[CLIHandler]:
        """
        Find CLI by lotus_position.

        PURE RESONANCE: No keyword matching.
        Position from mahamantra() == lotus_position from CLIMeta.
        """
        for cli in CLIRegistry.all():
            if cli.meta.lotus_position == position:
                return cli
        return None

    def _extract_args(self, input_text: str, cli: CLIHandler) -> List[str]:
        """
        Extract CLI arguments from input.

        Check if any subcommand appears in input.
        """
        words = input_text.lower().split()
        args = []

        # Find subcommand
        for subcmd in cli.meta.subcommands:
            if subcmd.lower() in words:
                args.append(subcmd)
                break

        return args if args else ["--help"]

    def discover(self) -> Dict[str, CLIMeta]:
        """Discover all CLIs."""
        self._discover_all_clis()
        return CLIRegistry.discover()

    def by_position(self, position: int) -> Optional[CLIHandler]:
        """Get CLI for a specific position."""
        self._discover_all_clis()
        return self._find_by_position(position)


# Singleton
_adapter: Optional[MahaCLIAdapter] = None


def get_adapter() -> MahaCLIAdapter:
    """Get the singleton adapter."""
    global _adapter
    if _adapter is None:
        _adapter = MahaCLIAdapter()
    return _adapter
