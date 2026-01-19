"""
OBSERVE - See the Mahamantra State
==================================

Read-only observation of what exists and what's connected.
NO CHANGES. NO INJECTION. Just SEE.

Usage:
    python -m vibe_core.mahamantra.cli.observe

    Or via steward:
    steward observe
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x507b609d"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

# Import Protocol Interface
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict

# Local imports only - no circular deps
from vibe_core.mahamantra.kernel.singularity import (
    MAHAMANTRA_POSITIONS,
    Quarter,
    mahamantra,
    get_quarter_positions,
)
from vibe_core.mahamantra.substrate.sankirtan import (
    FOLDER_MAHAJANA_MAP,
    SCAN_DIRECTORIES,
    get_mahajana_for_path,
)


class MahamantraObserver(PanchaTattvaProtocol):
    """
    The Observer (Narada).
    Sees the state of the Mahamantra.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "Observation Service",
            "nityananda": "Filesystem Scanner",
            "advaita": "Status Aggregation",
            "gadadhara": "Report Flow",
            "srivasa": "Observability Governance",
        }


# Singleton instance
observer = MahamantraObserver()

# =============================================================================
# OBSERVATION TYPES
# =============================================================================


class FolderMapping(TypedDict):
    """Folder → Mahajana mapping status."""

    folder: str
    mahajana: str
    position: int
    exists: bool
    in_map: bool  # Explicitly in FOLDER_MAHAJANA_MAP?


class ProtocolStatus(TypedDict):
    """Protocol existence and connection status."""

    name: str
    exists: bool
    connected: bool
    location: str


class ObserveResult(TypedDict):
    """Complete observation result."""

    mahamantra_type: str
    can_chant: bool
    can_tick: bool
    positions: int
    quarters: List[str]
    folder_mappings: List[FolderMapping]
    missing_mappings: List[str]
    protocols: List[ProtocolStatus]


# =============================================================================
# OBSERVATION FUNCTIONS
# =============================================================================


def observe_mahamantra() -> Dict:
    """Observe mahamantra singleton state."""
    return {
        "type": str(type(mahamantra)),
        "can_chant": hasattr(mahamantra, "chant") and callable(getattr(mahamantra, "chant", None)),
        "can_tick": hasattr(mahamantra, "tick") and callable(getattr(mahamantra, "tick", None)),
        "positions": len(MAHAMANTRA_POSITIONS),
        "quarters": [q.value for q in Quarter],
    }


def observe_folder_mappings() -> tuple[List[FolderMapping], List[str]]:
    """Observe folder → mahajana mappings."""
    mappings: List[FolderMapping] = []
    missing: List[str] = []

    base = Path("vibe_core")

    for folder in SCAN_DIRECTORIES:
        folder_path = base / folder
        exists = folder_path.exists()

        # Check if explicitly in map
        in_map = folder in FOLDER_MAHAJANA_MAP

        # Get mapping (explicit or hash-based)
        result = get_mahajana_for_path(folder_path / "dummy.py")
        if result:
            mahajana, position = result
        else:
            mahajana, position = "unknown", -1

        mappings.append(
            FolderMapping(
                folder=folder,
                mahajana=mahajana,
                position=position,
                exists=exists,
                in_map=in_map,
            )
        )

        if exists and not in_map:
            missing.append(folder)

    return mappings, missing


def observe_protocols() -> List[ProtocolStatus]:
    """Observe key protocol status."""
    protocols = []

    # Check key protocols
    checks = [
        ("KalaProtocol", "vibe_core.protocols.substrate", False),
        ("EventBusProtocol", "vibe_core.protocols.mahajanas.narada.events", False),
        ("BroadcastProtocol", "vibe_core.protocols.mahajanas.narada.broadcast", False),
        ("CognitiveKernelProtocol", "vibe_core.protocols.mahajanas.kapila.cognition", False),
        ("SamskaraProtocol", "vibe_core.protocols.substrate.samskara", False),
    ]

    for name, module, connected in checks:
        try:
            mod = __import__(module, fromlist=[name])
            exists = hasattr(mod, name)
        except ImportError:
            exists = False

        protocols.append(
            ProtocolStatus(
                name=name,
                exists=exists,
                connected=connected,  # TODO: Check actual connection
                location=module,
            )
        )

    return protocols


def observe() -> ObserveResult:
    """Complete observation of mahamantra state."""
    mahamantra_state = observe_mahamantra()
    folder_mappings, missing = observe_folder_mappings()
    protocols = observe_protocols()

    return ObserveResult(
        mahamantra_type=mahamantra_state["type"],
        can_chant=mahamantra_state["can_chant"],
        can_tick=mahamantra_state["can_tick"],
        positions=mahamantra_state["positions"],
        quarters=mahamantra_state["quarters"],
        folder_mappings=folder_mappings,
        missing_mappings=missing,
        protocols=protocols,
    )


def print_observation() -> None:
    """Print observation in human-readable format."""
    result = observe()

    print("=" * 60)
    print("  MAHAMANTRA OBSERVATION")
    print("=" * 60)
    print()

    # Mahamantra state
    print("=== MAHAMANTRA ===")
    print(f"  Type: {result['mahamantra_type']}")
    print(f"  Positions: {result['positions']}")
    print(f"  Quarters: {', '.join(result['quarters'])}")
    print(f"  Can chant(): {'YES' if result['can_chant'] else 'NO'}")
    print(f"  Can tick():  {'YES' if result['can_tick'] else 'NO - MISSING!'}")
    print()

    # Folder mappings
    print("=== FOLDER_IS_WIRING ===")
    for m in result["folder_mappings"]:
        status = "✓" if m["in_map"] else "△"  # △ = hash-based
        exists = "exists" if m["exists"] else "MISSING"
        print(f"  {status} {m['folder']:20} → {m['mahajana']:12} ({m['position']:2}) [{exists}]")
    print()

    if result["missing_mappings"]:
        print("  ⚠ Folders using hash-based mapping (not explicit):")
        for folder in result["missing_mappings"]:
            print(f"    - {folder}")
        print()

    # Protocols
    print("=== PROTOCOLS ===")
    for p in result["protocols"]:
        exists = "✓" if p["exists"] else "✗"
        connected = "CONNECTED" if p["connected"] else "not connected"
        print(f"  {exists} {p['name']:30} [{connected}]")
    print()

    print("=" * 60)


# =============================================================================
# CLI ENTRY
# =============================================================================


def cli_observe(args: List[str] = None) -> Dict:
    """
    CLI entry point for observe command.

    Returns machine-readable result.
    """
    result = observe()

    # Also print human-readable if not piped
    import sys

    if sys.stdout.isatty():
        print_observation()

    return dict(result)


if __name__ == "__main__":
    print_observation()
