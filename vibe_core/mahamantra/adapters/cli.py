"""
MAHA CLI ADAPTER - Bridge between Resonance and Action
======================================================

"yogaḥ karmasu kauśalam" - Yoga is skill in action.

BOUNDARY DEFINITION (Ksetra/Ksetrajna - BG 13):
===============================================

    THIS MODULE (our boundary):
        vibe_core/mahamantra/adapters/cli.py  ← YOU ARE HERE
        vibe_core/mahamantra/__main__.py      ← Entry Point

    HOLY (do not modify):
        vibe_core/mahamantra/_mahamantra_lotus.py  ← The Heart
        vibe_core/mahamantra/substrate/*           ← The Algorithm
        vibe_core/mahamantra/protocols/*           ← The Laws
        vibe_core/mahamantra/reactor/*             ← The Reactors

    EXTERNAL (use but don't own):
        vibe_core/cli/*_cli.py                ← Domain CLIs
        vibe_core/protocols/cli.py            ← CLIRegistry

HOLOGRAPHIC ROUTING (Cell-based):
    1. mahamantra(input) → MahaCell (72-byte header + payload)
    2. Cell carries FULL resonance (position, prana, integrity...)
    3. Match by CellFingerprint (multi-dimensional)
    4. Action EMERGES from cell state, not just position lookup

THE CELL KNOWS THE DIFFERENCE:
    "audit" and "create" both resonate at position 14 (Shuka)
    But their cells differ: payload_size 5 vs 6
    Holographic routing uses ALL dimensions for disambiguation.

"Das Routing ist unabhängig von dem Inhalt und der Bedeutung!"
But the CELL knows the difference through its dimensions.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"

__all__ = ["MahaCLIAdapter", "CellFingerprint", "AdapterResult"]

import importlib
import pkgutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vibe_core.protocols.cli import CLIHandler, CLIMeta, CLIRegistry


@dataclass
class CellFingerprint:
    """
    The holographic fingerprint from a MahaCell.

    Multiple dimensions for disambiguation:
    - position: 0-15 (Mahamantra word)
    - payload_size: Length of input
    - prana: Energy level
    - cycle: Computation cycle
    """

    position: int
    payload_size: int
    prana: int
    cycle: int
    seed: int

    def matches(self, other: "CellFingerprint", tolerance: int = 0) -> bool:
        """Check if two fingerprints match within tolerance."""
        if self.position != other.position:
            return False
        if abs(self.payload_size - other.payload_size) > tolerance:
            return False
        return True

    def distance(self, other: "CellFingerprint") -> int:
        """Compute distance between fingerprints."""
        if self.position != other.position:
            return 1000000  # Different position = far apart
        return abs(self.payload_size - other.payload_size) + abs(self.prana - other.prana)


@dataclass
class AdapterResult:
    """Result from the MahaCLI Adapter."""

    resonance: Dict = field(default_factory=dict)
    executed: bool = False
    cli_command: Optional[str] = None
    cli_result: Optional[int] = None
    matched_position: Optional[int] = None
    fingerprint: Optional[CellFingerprint] = None
    candidates: List[str] = field(default_factory=list)


class MahaCLIAdapter:
    """
    Bridge between Mahamantra Resonance and Domain CLIs.

    HOLOGRAPHIC ROUTING:
        1. Input → mahamantra() → Cell with fingerprint
        2. CLI names → mahamantra() → Cell fingerprints (cached)
        3. Match by fingerprint similarity, not just position

    This allows "audit" and "create" to be distinguished even at same position.
    """

    def __init__(self) -> None:
        self._discovered = False
        self._cli_fingerprints: Dict[str, CellFingerprint] = {}

    def _discover_all_clis(self) -> None:
        """
        Dynamically discover ALL CLIs and compute their fingerprints.
        """
        if self._discovered:
            return

        from vibe_core.mahamantra import mahamantra

        try:
            import vibe_core.cli as cli_package

            package_path = Path(cli_package.__file__).parent

            for module_info in pkgutil.iter_modules([str(package_path)]):
                if module_info.name.endswith("_cli"):
                    try:
                        importlib.import_module(f"vibe_core.cli.{module_info.name}")
                    except ImportError as _exc:
                        logger.exception("Unexpected error: %s", _exc)
        except ImportError as _exc:
            logger.exception("Unexpected error: %s", _exc)

        # Compute fingerprint for each registered CLI
        for cli in CLIRegistry.all():
            cmd = cli.meta.command
            resonance = mahamantra(cmd)
            self._cli_fingerprints[cmd] = self._extract_fingerprint(resonance)

        self._discovered = True

    def _extract_fingerprint(self, resonance: Dict) -> CellFingerprint:
        """Extract CellFingerprint from mahamantra() result."""
        cell = resonance.get("cell", {})
        return CellFingerprint(
            position=resonance.get("position", 0),
            payload_size=cell.get("payload_size", 0),
            prana=cell.get("prana", 0),
            cycle=cell.get("cycle", 0),
            seed=resonance.get("vibration", {}).get("seed", 0),
        )

    def execute(
        self,
        input_text: str,
        *,
        mode: str = "observe",
    ) -> AdapterResult:
        """
        Execute input through holographic cell matching.
        """
        from vibe_core.mahamantra import mahamantra

        # 1. Get resonance and fingerprint from input
        resonance = mahamantra(input_text)
        input_fp = self._extract_fingerprint(resonance)

        # 2. Discover all CLIs and their fingerprints
        self._discover_all_clis()

        # 3. Find best matching CLI by fingerprint
        cli, candidates = self._find_by_fingerprint(input_fp, input_text)

        result = AdapterResult(
            resonance=resonance,
            matched_position=input_fp.position,
            fingerprint=input_fp,
            candidates=candidates,
        )

        if cli:
            result.cli_command = cli.meta.command

            if mode == "execute":
                args = self._extract_args(input_text, cli)
                result.cli_result = cli.run(args)
                result.executed = True

        return result

    def _find_by_fingerprint(
        self,
        input_fp: CellFingerprint,
        input_text: str,
    ) -> Tuple[Optional[CLIHandler], List[str]]:
        """
        Find CLI by fingerprint matching.

        Strategy:
        1. Find all CLIs at same position
        2. Sort by fingerprint distance
        3. If exact payload_size match, use that
        4. Otherwise, use name matching as tiebreaker
        """
        candidates = []

        for cli in CLIRegistry.all():
            cmd = cli.meta.command
            cli_fp = self._cli_fingerprints.get(cmd)

            if cli_fp and cli_fp.position == input_fp.position:
                distance = cli_fp.distance(input_fp)
                candidates.append((distance, cmd, cli))

        if not candidates:
            return None, []

        # Sort by distance
        candidates.sort(key=lambda x: x[0])
        candidate_names = [c[1] for c in candidates]

        # If multiple at same distance, use name matching
        if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
            # Check if input contains any CLI name
            input_lower = input_text.lower()
            for _, cmd, cli in candidates:
                if cmd.lower() in input_lower:
                    return cli, candidate_names

        # Return closest match
        return candidates[0][2], candidate_names

    def _extract_args(self, input_text: str, cli: CLIHandler) -> List[str]:
        """Extract CLI arguments from input."""
        words = input_text.lower().split()
        args = []

        for subcmd in cli.meta.subcommands:
            if subcmd.lower() in words:
                args.append(subcmd)
                break

        return args if args else ["--help"]

    def discover(self) -> Dict[str, CLIMeta]:
        """Discover all CLIs."""
        self._discover_all_clis()
        return CLIRegistry.discover()

    def by_position(self, position: int) -> List[CLIHandler]:
        """Get all CLIs at a specific position."""
        self._discover_all_clis()
        return [
            cli
            for cli in CLIRegistry.all()
            if self._cli_fingerprints.get(cli.meta.command, CellFingerprint(0, 0, 0, 0, 0)).position == position
        ]


# Singleton
_adapter: Optional[MahaCLIAdapter] = None


def get_adapter() -> MahaCLIAdapter:
    """Get the singleton adapter."""
    global _adapter
    if _adapter is None:
        _adapter = MahaCLIAdapter()
    return _adapter
