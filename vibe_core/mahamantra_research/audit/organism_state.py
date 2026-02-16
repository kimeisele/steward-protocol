"""
ORGANISM STATE — Where are we? What exists? What's missing?

This is not a report. This is a machine-readable snapshot of the system's
current state, to be consumed by future analysis and migration tooling.

Run: python -m vibe_core.mahamantra.research.audit.organism_state
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class OrganState:
    name: str
    path: str
    file_count: int = 0
    sloc: int = 0
    imports_mahamantra: int = 0  # files that import from mahamantra
    imported_by_mahamantra: int = 0  # files in mahamantra that import from this
    has_protocol: bool = False  # has a Protocol class
    has_heartbeat: bool = False  # connected to tick/heartbeat
    world: str = ""  # "new" (mahamantra), "bridge" (imports both), "legacy"


@dataclass
class OrganismSnapshot:
    total_files: int = 0
    total_sloc: int = 0
    new_world_files: int = 0
    legacy_files: int = 0
    bridge_files: int = 0
    organs: List[OrganState] = field(default_factory=list)


def count_sloc(filepath: Path) -> int:
    try:
        lines = filepath.read_text(errors="replace").split("\n")
    except Exception:
        return 0
    count = 0
    in_doc = False
    for line in lines:
        s = line.strip()
        if s.startswith('"""') or s.startswith("'''"):
            if s.count('"""') >= 2 or s.count("'''") >= 2:
                continue
            in_doc = not in_doc
            continue
        if in_doc or not s or s.startswith("#"):
            continue
        count += 1
    return count


def scan_organ(base: Path, dirname: str, maha_modules: Set[str]) -> OrganState:
    dirpath = base / dirname
    if not dirpath.exists():
        return OrganState(name=dirname, path=str(dirpath))

    py_files = [
        f for f in dirpath.rglob("*.py")
        if "__pycache__" not in str(f) and "test" not in f.name.lower()
    ]

    organ = OrganState(name=dirname, path=str(dirpath), file_count=len(py_files))

    for f in py_files:
        try:
            content = f.read_text(errors="replace")
        except Exception:
            continue

        organ.sloc += count_sloc(f)

        if "from vibe_core.mahamantra" in content or "import vibe_core.mahamantra" in content:
            organ.imports_mahamantra += 1

        if "class " in content and "Protocol" in content and "runtime_checkable" in content:
            organ.has_protocol = True

        if "tick(" in content or "heartbeat" in content.lower() or "BeatSubscriber" in content:
            organ.has_heartbeat = True

    # Check if mahamantra imports from this organ
    for mmod in maha_modules:
        if f"from vibe_core.{dirname}" in mmod or f"import vibe_core.{dirname}" in mmod:
            organ.imported_by_mahamantra += 1

    # Classify world
    if dirname == "mahamantra":
        organ.world = "new"
    elif organ.imports_mahamantra > 0 and organ.imported_by_mahamantra > 0:
        organ.world = "bridge"
    elif organ.imports_mahamantra > 0:
        organ.world = "consumer"
    elif organ.imported_by_mahamantra > 0:
        organ.world = "dependency"
    else:
        organ.world = "legacy"

    return organ


def get_mahamantra_imports(base: Path) -> Set[str]:
    """Collect all import lines from mahamantra/ to find what it depends on."""
    imports = set()
    maha = base / "mahamantra"
    if not maha.exists():
        return imports
    for f in maha.rglob("*.py"):
        if "__pycache__" in str(f):
            continue
        try:
            for line in f.read_text(errors="replace").split("\n"):
                s = line.strip()
                if s.startswith("from vibe_core.") or s.startswith("import vibe_core."):
                    imports.add(s)
        except Exception:
            pass
    return imports


def find_root() -> Path:
    p = Path(__file__).resolve()
    while p.name != "steward-protocol" and p != p.parent:
        p = p.parent
    return p


def main():
    root = find_root()
    base = root / "vibe_core"

    maha_imports = get_mahamantra_imports(base)

    all_dirs = sorted([
        d.name for d in base.iterdir()
        if d.is_dir() and d.name != "__pycache__"
    ])

    snapshot = OrganismSnapshot()
    for dirname in all_dirs:
        organ = scan_organ(base, dirname, maha_imports)
        if organ.file_count == 0:
            continue
        snapshot.organs.append(organ)
        snapshot.total_files += organ.file_count
        snapshot.total_sloc += organ.sloc
        if organ.world == "new":
            snapshot.new_world_files += organ.file_count
        elif organ.world in ("bridge", "consumer", "dependency"):
            snapshot.bridge_files += organ.file_count
        else:
            snapshot.legacy_files += organ.file_count

    # Print
    print("=" * 95)
    print("ORGANISM STATE — System Topology")
    print("=" * 95)
    print(f"{'Organ':20s} | {'Files':>5s} | {'SLOC':>6s} | {'→Maha':>5s} | {'Maha→':>5s} | {'Proto':>5s} | {'Beat':>4s} | World")
    print("-" * 95)
    for o in sorted(snapshot.organs, key=lambda x: x.file_count, reverse=True):
        print(
            f"{o.name:20s} | {o.file_count:5d} | {o.sloc:6d} | "
            f"{o.imports_mahamantra:5d} | {o.imported_by_mahamantra:5d} | "
            f"{'Y' if o.has_protocol else '-':>5s} | {'Y' if o.has_heartbeat else '-':>4s} | {o.world}"
        )
    print("-" * 95)
    print(
        f"{'TOTAL':20s} | {snapshot.total_files:5d} | {snapshot.total_sloc:6d} | "
        f"{'':>5s} | {'':>5s} | {'':>5s} | {'':>4s} |"
    )
    print(f"\nNew world (mahamantra):  {snapshot.new_world_files}")
    print(f"Bridge/connected:       {snapshot.bridge_files}")
    print(f"Legacy (isolated):      {snapshot.legacy_files}")

    # Save
    out = Path(__file__).parent / "organism_state_report.json"
    out.write_text(json.dumps(asdict(snapshot), indent=2))
    print(f"\nJSON: {out}")


if __name__ == "__main__":
    main()
