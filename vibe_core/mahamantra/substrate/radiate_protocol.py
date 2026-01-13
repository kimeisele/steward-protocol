"""
RADIATE PROTOCOL - MantraProtocol Conversion via SANKIRTAN
==========================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"

"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

SANKIRTAN PATTERN:
    SSOT (MAHAMANTRA_POSITIONS) → Radiate → 12 Mahajana + 4 Avataras Folders

This script transforms mahajana folders from MANUAL WIRING to
MANTRA PROTOCOL DERIVATION.

BEFORE (manual wiring):
    POSITION: Final[int] = 15  # Hardcoded!
    class YamarajaBase:
        _position: ClassVar[int] = POSITION

AFTER (MantraProtocol derivation):
    class YamarajaBase(WorkerProtocol):
        _position_index = 15  # That's ALL!

RUN:
    python -m vibe_core.mahamantra.substrate.radiate_protocol [--live]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Import SSOT
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)
from vibe_core.mahamantra.substrate.mahajana import Mahajana, Avatara, Quarter


# =============================================================================
# TEMPLATE - MantraProtocol-based module
# =============================================================================

def generate_module(pos: MantraPosition) -> str:
    """
    Generate a MantraProtocol-based module for a position.

    SSOT → Template → Module Content
    """
    # Determine guardian info
    guardian = pos.guardian
    if isinstance(guardian, Avatara):
        guardian_name = guardian.name.lower()
        guardian_title = guardian.name.title()
        is_avatara = True
        base_class = "HeadProtocol"
        type_str = "HEAD"
        role = "Avatar"
    else:
        guardian_name = guardian.name.lower()
        guardian_title = guardian.name.title()
        is_avatara = False
        base_class = "WorkerProtocol"
        type_str = "WORKER"
        role = "Worker"

    quarter_name = pos.quarter.name.lower()
    opcode_name = pos.opcode.name

    # Genesis hash (parampara % 37 == 0)
    import hashlib
    identity = f"{guardian_name}:{pos.index}"
    raw_hash = hashlib.sha256(identity.encode()).hexdigest()[:8]
    base_value = int(raw_hash, 16)
    adjusted = base_value - (base_value % 37)
    genesis_hash = f"0x{adjusted:08x}"

    return f'''"""
{guardian_title.upper()} - Position {pos.index}
{'=' * (len(guardian_title) + 15)}

Quarter: {pos.quarter.name}
OpCode: {opcode_name}
Type: {type_str}
Role: {role}

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: {pos.parampara_vector} (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "{guardian_name}"
__position__ = {pos.index}
__genesis__ = "{genesis_hash}"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import {base_class}

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = {pos.index}
QUARTER: Final[str] = "{quarter_name}"
OPCODE: Final[str] = "{opcode_name}"
PARAMPARA_VECTOR: Final[int] = {pos.parampara_vector}


@runtime_checkable
class {guardian_title}Protocol(Protocol):
    """
    Protocol for {guardian_title} ({opcode_name}).

    Position {pos.index} in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class {guardian_title}Base({base_class}):
    """
    Base class for {guardian_title} implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = {pos.index}  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = {pos.index}


class Null{guardian_title}({guardian_title}Base):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "{guardian_title}Protocol",
    "{guardian_title}Base",
    "Null{guardian_title}",
]
'''


# =============================================================================
# FOLDER MAPPING - Position → Folder Path
# =============================================================================

def get_folder_path(pos: MantraPosition, base_path: Path) -> Path:
    """Get the folder path for a position."""
    guardian = pos.guardian
    if isinstance(guardian, Avatara):
        guardian_name = guardian.name.lower()
    else:
        guardian_name = guardian.name.lower()

    quarter_name = pos.quarter.name.lower()
    return base_path / quarter_name / guardian_name


# =============================================================================
# MAIN - SANKIRTAN RADIATION
# =============================================================================

def radiate_protocol(base_path: Path, dry_run: bool = True) -> Dict[str, bool]:
    """
    Radiate MantraProtocol to all 16 mahajana folders.

    SANKIRTAN PATTERN:
        Read from SSOT → Generate → Write to periphery

    Args:
        base_path: Path to mahamantra/ directory
        dry_run: If True, only show what would be done

    Returns:
        Dict of {folder_name: success}
    """
    results: Dict[str, bool] = {}

    print("=" * 60)
    print(f"  RADIATE PROTOCOL {'[DRY-RUN]' if dry_run else '[LIVE]'}")
    print("=" * 60)
    print()

    for pos in MAHAMANTRA_POSITIONS:
        folder = get_folder_path(pos, base_path)
        init_file = folder / "__init__.py"

        guardian = pos.guardian
        if isinstance(guardian, Avatara):
            guardian_name = guardian.name
        else:
            guardian_name = guardian.name

        print(f"  [{pos.index:2}] {guardian_name:12} → {folder.relative_to(base_path)}")

        if not folder.exists():
            print(f"       SKIP: Folder does not exist")
            results[guardian_name] = False
            continue

        # Generate new content
        new_content = generate_module(pos)

        if dry_run:
            print(f"       Would write {len(new_content)} bytes")
            results[guardian_name] = True
        else:
            try:
                init_file.write_text(new_content)
                print(f"       WRITTEN {len(new_content)} bytes")
                results[guardian_name] = True
            except Exception as e:
                print(f"       ERROR: {e}")
                results[guardian_name] = False

    print()
    print("=" * 60)
    success_count = sum(1 for v in results.values() if v)
    print(f"  {success_count}/16 folders {'would be' if dry_run else ''} converted")
    print("=" * 60)

    return results


def main() -> int:
    """CLI entry point."""
    # Parse args
    dry_run = "--live" not in sys.argv

    # Find mahamantra base path
    script_path = Path(__file__).resolve()
    mahamantra_path = script_path.parent.parent  # substrate/../ = mahamantra/

    if not (mahamantra_path / "genesis").exists():
        print(f"ERROR: Cannot find mahamantra quarters at {mahamantra_path}")
        return 1

    print(f"Base path: {mahamantra_path}")
    print()

    results = radiate_protocol(mahamantra_path, dry_run=dry_run)

    if dry_run:
        print()
        print("To apply changes, run with --live:")
        print(f"  python -m vibe_core.mahamantra.substrate.radiate_protocol --live")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
