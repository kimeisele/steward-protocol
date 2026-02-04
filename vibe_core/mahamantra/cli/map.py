"""
MAP - Visibility into the Mahamantra System
============================================

"paśyanti jñāna-cakṣuṣaḥ"
"Those with eyes of knowledge see."
— Bhagavad Gita 15.10

THE OPERATOR'S MAP:
==================

    steward map         → Full system overview
    steward map --cli   → CLI commands by position
    steward map --scan  → Declared files by position

This is SATTVA (observation, no side effects).
The operator SEES the whole system.

WATERTIGHT: No Any types.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xc0994a6b"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Final, List, Optional, TypedDict

from vibe_core.mahamantra.substrate.guna import (
    VISHUDDHA_SATTVA,
    Guna,
    get_guna_by_position,
)
from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS
# SSOT - WORDS derives from Mahamantra counting
from vibe_core.mahamantra.substrate.seed import WORDS

# =============================================================================
# TYPES
# =============================================================================


class PositionInfo(TypedDict):
    """Info about a position - WATERTIGHT."""

    position: int
    guardian: str
    quarter: str
    guna: str
    opcode: str
    cli_commands: List[str]
    declared_files: int


class MapResult(TypedDict):
    """Result of map command - WATERTIGHT."""

    total_positions: int
    positions: List[PositionInfo]
    total_cli_commands: int
    total_declared_files: int
    coverage_percent: float


# =============================================================================
# GUNA SYMBOLS
# =============================================================================

GUNA_SYMBOLS: Final[Dict[str, str]] = {
    "sattva": "●",  # Safe (read)
    "rajas": "◐",  # Active (write)
    "tamas": "○",  # Destroy (confirm)
}


# =============================================================================
# MAP FUNCTIONS
# =============================================================================


def get_all_cli_commands() -> Dict[str, int]:
    """
    Get all CLI commands mapped to their positions.

    Returns dict of command_name -> position.
    """
    commands: Dict[str, int] = {}

    # RESONANCE-BASED POSITION (KREBS ENTFERNT: keine hardcoded keywords mehr)
    try:
        from vibe_core.mahamantra.cli.bridge import cli_bridge

        # Get UnifiedCLI commands (cmd_* methods)
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()

        for attr in dir(cli):
            if attr.startswith("cmd_"):
                cmd_name = attr[4:]  # Remove "cmd_" prefix
                # RESONANZ-BASED: cli_bridge.get_position nutzt MahaCompression
                position = cli_bridge.get_position(cmd_name)
                if position is None:
                    position = 0  # Default to vyasa if resonance fails
                commands[cmd_name] = position
    except ImportError as _exc:
        logger.exception("Unexpected error: %s", _exc)

    try:
        # Get cartridge commands
        from vibe_core.cartridges.bridge import CartridgeBridge

        bridge = CartridgeBridge()

        for name in bridge._cli_stubs.keys() if hasattr(bridge, "_cli_stubs") else []:
            mutation_vector = sum(ord(c) * (i + 1) for i, c in enumerate(name.lower()))
            position = mutation_vector % WORDS  # SSOT: WORDS from seed.py
            commands[name] = position
    except (ImportError, AttributeError) as _exc:
        logger.exception("Unexpected error: %s", _exc)

    return commands


def get_cli_commands_for_position(position: int) -> List[str]:
    """
    Get CLI commands available at a position.
    """
    all_commands = get_all_cli_commands()
    return sorted([cmd for cmd, pos in all_commands.items() if pos == position])


def get_declared_files_for_position(position: int) -> int:
    """Get count of files declared at a position.

    NOTE: Scanner removed. Files are wired via folder structure (folder = wiring).
    This now returns 0 as file counting is no longer via declarations.
    """
    # Scanner removed - folder IS wiring. No declaration counting needed.
    return 0


def build_map() -> MapResult:
    """
    Build the complete system map.

    Returns structured data about all WORDS positions (SSOT).
    """
    positions: List[PositionInfo] = []
    total_cli = 0
    total_declared = 0
    positions_with_content = 0

    for mapping in MAHAMANTRA_POSITIONS:
        pos = mapping.index
        guna = get_guna_by_position(pos)
        cli_commands = get_cli_commands_for_position(pos)
        declared = get_declared_files_for_position(pos)

        total_cli += len(cli_commands)
        total_declared += declared

        if cli_commands or declared:
            positions_with_content += 1

        positions.append(
            PositionInfo(
                position=pos,
                guardian=mapping.guardian.value,
                quarter=mapping.quarter.value,
                guna=guna.name.lower(),
                opcode=mapping.opcode.name,
                cli_commands=cli_commands,
                declared_files=declared,
            )
        )

    coverage = (positions_with_content / WORDS) * 100 if positions else 0  # SSOT

    return MapResult(
        total_positions=WORDS,  # SSOT: WORDS from seed.py
        positions=positions,
        total_cli_commands=total_cli,
        total_declared_files=total_declared,
        coverage_percent=coverage,
    )


def format_map(result: MapResult, verbose: bool = False) -> str:
    """Format map result for display."""
    lines: List[str] = []

    lines.append("MAHAMANTRA SYSTEM MAP")
    lines.append("=" * 60)
    lines.append("")
    lines.append(
        f"Coverage: {result['coverage_percent']:.0f}% ({result['total_cli_commands']} CLI commands, {result['total_declared_files']} declared files)"
    )
    lines.append("")

    # Group by quarter
    quarters = ["genesis", "dharma", "karma", "moksha"]

    for quarter in quarters:
        quarter_positions = [p for p in result["positions"] if p["quarter"] == quarter]
        lines.append(
            f"{quarter.upper()} (positions {quarter_positions[0]['position']}-{quarter_positions[-1]['position']}):"
        )

        for pos in quarter_positions:
            guna_sym = GUNA_SYMBOLS.get(pos["guna"], "?")
            cli_count = len(pos["cli_commands"])

            # Position line
            line = f"  {pos['position']:2} {guna_sym} {pos['guardian']:12} [{pos['opcode']:12}]"

            if cli_count > 0:
                line += f"  CLI:{cli_count}"

            if pos["declared_files"] > 0:
                line += f"  Files:{pos['declared_files']}"

            lines.append(line)

            # Verbose: show CLI commands
            if verbose and pos["cli_commands"]:
                for cmd in pos["cli_commands"][:5]:
                    lines.append(f"        → {cmd}")
                if len(pos["cli_commands"]) > 5:
                    lines.append(f"        ... +{len(pos['cli_commands']) - 5} more")

        lines.append("")

    lines.append("LEGEND: ● Sattva (safe)  ◐ Rajas (active)  ○ Tamas (confirm)")

    return "\n".join(lines)


def map_command(args: Optional[List[str]] = None) -> str:
    """
    Execute the map command.

    Usage:
        steward map           → Overview
        steward map --verbose → With CLI command details
    """
    args = args or []
    verbose = "--verbose" in args or "-v" in args

    result = build_map()
    return format_map(result, verbose=verbose)


# =============================================================================
# GUARDIAN DETAILS
# =============================================================================

GUARDIAN_NAMES: Final[Dict[str, int]] = {
    # ALIGNED WITH seed.py ALL_GUARDIANS (SSOT)
    "vyasa": 0,
    "brahma": 1,
    "narada": 2,
    "shambhu": 3,
    "prithu": 4,
    "kumaras": 5,
    "kapila": 6,
    "manu": 7,
    "parashurama": 8,
    "prahlada": 9,
    "janaka": 10,
    "bhishma": 11,
    "nrisimha": 12,
    "bali": 13,
    "shuka": 14,
    "yamaraja": 15,
}


def guardian_command(guardian: str, args: Optional[List[str]] = None) -> Optional[str]:
    """
    Show details for a specific guardian/position.

    Usage:
        steward brahma       → Show position 1 details
        steward parashurama  → Show position 8 details

    Returns None if not a guardian name.
    """
    guardian_lower = guardian.lower()
    if guardian_lower not in GUARDIAN_NAMES:
        return None

    position = GUARDIAN_NAMES[guardian_lower]
    mapping = MAHAMANTRA_POSITIONS[position]
    guna = get_guna_by_position(position)
    cli_commands = get_cli_commands_for_position(position)
    declared = get_declared_files_for_position(position)

    lines: List[str] = []
    lines.append(f"POSITION {position}: {guardian.upper()}")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Quarter:  {mapping.quarter.value.upper()}")
    lines.append(f"OpCode:   {mapping.opcode}")
    lines.append(f"Guna:     {guna.name} ({GUNA_SYMBOLS.get(guna.name.lower(), '?')})")
    lines.append("")

    if cli_commands:
        lines.append(f"CLI Commands ({len(cli_commands)}):")
        for cmd in cli_commands:
            lines.append(f"  steward {cmd}")
    else:
        lines.append("CLI Commands: None")

    lines.append("")
    lines.append(f"Declared Files: {declared}")

    # Add folder path
    folder_path = f"vibe_core/mahamantra/{mapping.quarter.value}/{mapping.folder_name}/"
    lines.append(f"Folder: {folder_path}")

    return "\n".join(lines)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PositionInfo",
    "MapResult",
    "build_map",
    "format_map",
    "map_command",
    "GUARDIAN_NAMES",
    "guardian_command",
]
